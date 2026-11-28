// SDK-host witness of actual repaired Windows modules, not a DSP-core substitute.
#include "public.sdk/source/vst/hosting/module.h"
#include "public.sdk/source/vst/hosting/hostclasses.h"
#include "public.sdk/source/vst/hosting/parameterchanges.h"
#include "public.sdk/source/common/memorystream.h"
#include "pluginterfaces/vst/ivstaudioprocessor.h"
#include "pluginterfaces/vst/ivstcomponent.h"
#include "pluginterfaces/vst/vstspeaker.h"
#include <algorithm>
#include <atomic>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <thread>
#include <vector>
using namespace Steinberg;
using namespace Steinberg::Vst;
namespace {
using Bytes=std::vector<std::uint8_t>;
void require(bool b,const char* where){if(!b)throw std::runtime_error(where);}
void ok(tresult r,const char* where){require(r==kResultOk,where);}
Bytes save(IComponent* c){
    MemoryStream s;ok(c->getState(&s),"getState");
    require(s.getSize()>0&&s.getSize()<=65536,"state size");
    auto* p=reinterpret_cast<const std::uint8_t*>(s.getData());return Bytes(p,p+s.getSize());
}
void restore(IComponent* c,Bytes b){MemoryStream s(b.data(),TSize(b.size()));ok(c->setState(&s),"setState");}
struct Life {
    IComponent* c; IAudioProcessor* p; bool initialized=false,active=false,running=false;
    ~Life(){if(running)p->setProcessing(false);if(active)c->setActive(false);if(initialized)c->terminate();}
};
void run(const VST3::Hosting::PluginFactory& factory,const VST3::Hosting::ClassInfo& info,HostApplication* host,ParamID id){
    auto c=factory.createInstance<IComponent>(info.ID());require(bool(c),"component");
    FUnknownPtr<IAudioProcessor> proc(c.get());require(proc.getInterface()!=nullptr,"processor");
    Life life{c.get(),proc.getInterface()};
    ok(c->initialize(host),"initialize");life.initialized=true;
    const int ni=c->getBusCount(kAudio,kInput),no=c->getBusCount(kAudio,kOutput);
    require(ni>=0&&ni<=1&&no>=1&&no<=4,"bus count");
    std::vector<SpeakerArrangement> ins(ni),outs(no);
    for(int i=0;i<ni;++i)ok(proc->getBusArrangement(kInput,i,ins[i]),"input arrangement");
    for(int i=0;i<no;++i)ok(proc->getBusArrangement(kOutput,i,outs[i]),"output arrangement");
    if(ni)ins[0]=SpeakerArr::kStereo;outs[0]=SpeakerArr::kStereo;
    ok(proc->setBusArrangements(ins.empty()?nullptr:ins.data(),ni,outs.data(),no),"negotiate");
    if(ni)ok(c->activateBus(kAudio,kInput,0,true),"activate input");
    for(int i=0;i<no;++i)ok(c->activateBus(kAudio,kOutput,i,i==0),"activate output");
    constexpr int block=128;
    ProcessSetup setup{kRealtime,kSample32,block,48000.};
    ok(proc->setupProcessing(setup),"setup");ok(c->setActive(true),"activate");life.active=true;
    ok(proc->setProcessing(true),"start");life.running=true;
    const auto a=save(c.get());
    // Obtain a second valid state through the real adapter, not a guessed wire format.
    ParameterChanges changes(1);int32 qi=0,pi=0;
    auto* queue=changes.addParameterData(id,qi);require(queue!=nullptr,"parameter queue");
    ok(queue->addPoint(0,.371,pi),"parameter point");
    ProcessData flush{};flush.processMode=kRealtime;flush.symbolicSampleSize=kSample32;flush.inputParameterChanges=&changes;
    ok(proc->process(flush),"zero-frame automation");
    const auto b=save(c.get());require(a!=b,"second state identical");
    restore(c.get(),a);require(save(c.get())==a,"pending restore");
    std::vector<float> left(block,.03f),right(block,-.02f),outL(block),outR(block);
    float* in[]{left.data(),right.data()},*out[]{outL.data(),outR.data()};
    AudioBusBuffers input{},output{};input.numChannels=output.numChannels=2;
    input.channelBuffers32=in;output.channelBuffers32=out;
    ProcessData d{};d.processMode=kRealtime;d.symbolicSampleSize=kSample32;d.numSamples=block;
    d.numInputs=ni;d.numOutputs=1;d.inputs=ni?&input:nullptr;d.outputs=&output;
    std::atomic<bool> done{false},failed{false};std::atomic<unsigned> blocks{0};
    std::thread audio([&]{
        do{
            input.silenceFlags=0;output.silenceFlags=0;
            if(proc->process(d)!=kResultOk){failed=true;break;}
            for(int i=0;i<block;++i)if(!std::isfinite(outL[i])||!std::isfinite(outR[i])||std::abs(outL[i])>8.f||std::abs(outR[i])>8.f)failed=true;
            ++blocks;
        }while((!done.load(std::memory_order_acquire)||blocks.load()<256)&&blocks.load()<1000000&&!failed.load());
    });
    unsigned writes=0,reads=0;
    try{
        while(blocks.load()==0&&!failed.load())std::this_thread::yield();
        for(unsigned i=0;i<20000;++i){
            const auto& requested=i&1?a:b;restore(c.get(),requested);++writes;
            require(save(c.get())==requested,"torn or stale patch");++reads;
            require(!failed.load(),"audio failure");
        }
        restore(c.get(),b);
    }catch(...){done.store(true,std::memory_order_release);audio.join();throw;}
    done.store(true,std::memory_order_release);audio.join();
    require(!failed&&writes==20000&&reads==20000&&blocks.load()>=256,"concurrent stress");
    ok(proc->process(d),"final block");require(save(c.get())==b,"final restore");
    ok(proc->setProcessing(false),"stop");life.running=false;
    ok(c->setActive(false),"deactivate");life.active=false;
    ok(c->terminate(),"terminate");life.initialized=false;
    std::cout<<"SDK_CONCURRENT_STATE_PASS name="<<info.name()<<" writes="<<writes<<" reads="<<reads<<" blocks="<<blocks.load()<<std::endl;
}
}
int main(int argc,char** argv){
    try{
        require(argc==3,"usage: mhac_state_probe bundle first-parameter-id");
        auto host=owned(new HostApplication);std::string err;
        auto module=VST3::Hosting::Module::create(argv[1],err);if(!module)throw std::runtime_error(err);
        const auto& factory=module->getFactory();factory.setHostContext(host.get());
        for(const auto& info:factory.classInfos())if(info.category()==kVstAudioEffectClass){run(factory,info,host.get(),ParamID(std::stoul(argv[2])));return 0;}
        throw std::runtime_error("no component");
    }catch(const std::exception& e){std::cerr<<"SDK_CONCURRENT_STATE_FAIL "<<e.what()<<std::endl;return 1;}
}
