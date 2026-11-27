// ACCEL-040: direct SDK host of the actual packaged module, not a DSP-only test.
#include "public.sdk/source/vst/hosting/module.h"
#include "public.sdk/source/vst/hosting/hostclasses.h"
#include "public.sdk/source/vst/hosting/parameterchanges.h"
#include "public.sdk/source/common/memorystream.h"
#include "pluginterfaces/vst/ivstaudioprocessor.h"
#include "pluginterfaces/vst/ivstcomponent.h"
#include "pluginterfaces/vst/vstspeaker.h"
#include "shuttle_control.hpp"
#include <cstring>
#include <iterator>
#include <atomic>
#include <iostream>
#include <stdexcept>
#include <thread>
#include <vector>
using namespace Steinberg;
using namespace Steinberg::Vst;
using namespace mhac::accel;
namespace {
void require(bool ok,const char* stage){if(!ok)throw std::runtime_error(stage);}
void ok(tresult rc,const char* stage){
    if(rc!=kResultOk)throw std::runtime_error(std::string(stage)+" result="+std::to_string(static_cast<int>(rc)));
}
void restore(IComponent* c,ShuttleState b){MemoryStream s(b.data(),TSize(b.size()));ok(c->setState(&s),"setState");}
ShuttleState save(IComponent* c){
    MemoryStream s;ok(c->getState(&s),"getState");require(s.getSize()==13,"state length");
    ShuttleState b{};std::memcpy(b.data(),s.getData(),b.size());ShuttlePatch p{};
    require(decode(b,p),"state decode");return b;
}
struct Life {
    IComponent* c; IAudioProcessor* p; bool initialized=false,active=false,running=false;
    ~Life(){if(running)p->setProcessing(false);if(active)c->setActive(false);if(initialized)c->terminate();}
};
struct ShuttleEvent {unsigned offset,id;double normalized;};
constexpr ShuttleEvent score[]={{0,0,.25},{0,3,.7},{17,2,.1},{129,1,.8},{129,2,.65},
    {4097,4,1.},{8195,4,0.},{12001,0,.8},{12001,3,.2},{16003,1,.15}};
std::vector<float> run(const VST3::Hosting::PluginFactory& factory,const VST3::Hosting::ClassInfo& info,
    HostApplication* host,int rate,int block,bool stress){
    auto c=factory.createInstance<IComponent>(info.ID());require(bool(c),"create");
    FUnknownPtr<IAudioProcessor> proc(c.get());require(proc.getInterface()!=nullptr,"processor");
    Life life{c.get(),proc.getInterface()};
    ok(c->initialize(host),"initialize");life.initialized=true;
    SpeakerArrangement arrangement=SpeakerArr::kStereo;
    ok(proc->setBusArrangements(&arrangement,1,&arrangement,1),"arrangement");
    ok(c->activateBus(kAudio,kInput,0,true),"input");
    ok(c->activateBus(kAudio,kOutput,0,true),"output");
    const ShuttlePatch initial{650,150,180,600,false};
    const auto initialBytes=encode(initial);
    restore(c.get(),initialBytes);require(save(c.get())==initialBytes,"cold pending restore");
    ProcessSetup setup{kRealtime,kSample32,block,double(rate)};
    ok(proc->setupProcessing(setup),"setup");
    ok(c->setActive(true),"activate");life.active=true;
    ok(proc->setProcessing(true),"start");life.running=true;
    require(save(c.get())==initialBytes,"cold setup restore");
    std::vector<float> left(block),right(block),outL(block),outR(block),result;
    float* in[]{left.data(),right.data()},*out[]{outL.data(),outR.data()};
    AudioBusBuffers input{},output{};input.numChannels=output.numChannels=2;
    input.channelBuffers32=in;output.channelBuffers32=out;
    ParameterChanges params(5);
    ProcessData d{};d.processMode=kRealtime;d.symbolicSampleSize=kSample32;
    d.numInputs=d.numOutputs=1;d.inputs=&input;d.outputs=&output;d.inputParameterChanges=&params;
    PalimpsestShuttle<> oracle;require(oracle.prepare(unsigned(rate))&&oracle.configure(initial),"oracle setup");oracle.reset();
    constexpr int total=20000;
    if(!stress){
        result.reserve(2*total);
        double maxError=0;unsigned cursor=0;
        for(int pos=0;pos<total;pos+=block){
            const int n=std::min(block,total-pos);d.numSamples=n;params.clearQueue();
            for(const auto& e:score)if(e.offset>=unsigned(pos)&&e.offset<unsigned(pos+n)){
                int32 qi=0,pi=0;auto* q=params.addParameterData(e.id,qi);require(q!=nullptr,"queue");
                ok(q->addPoint(int32(e.offset)-pos,e.normalized,pi),"point");
            }
            for(int j=0;j<n;++j){
                const auto i=pos+j;left[j]=float((i*17)%251-125)*.0008f;right[j]=float((i*31)%127-63)*.001f;
            }
            input.silenceFlags=0;output.silenceFlags=0;
            ok(proc->process(d),"process");
            for(int j=0;j<n;++j){
                const unsigned i=unsigned(pos+j);
                if(cursor<std::size(score)&&score[cursor].offset==i){
                    auto p=oracle.patch();
                    do{require(applyShuttleNormalized(p,score[cursor].id,score[cursor].normalized),"oracle event");++cursor;}
                    while(cursor<std::size(score)&&score[cursor].offset==i);
                    require(oracle.configure(p),"oracle configure");
                }
                const auto y=oracle.process({left[j],right[j]});
                require(std::isfinite(outL[j])&&std::isfinite(outR[j])&&std::abs(outL[j])<=1.f&&std::abs(outR[j])<=1.f,"output bound");
                maxError=std::max({maxError,std::abs(double(y.l)-outL[j]),std::abs(double(y.r)-outR[j])});
                result.push_back(outL[j]);result.push_back(outR[j]);
            }
        }
        require(maxError<2e-5,"sample offset oracle mismatch");
        require(save(c.get())==encode(oracle.patch()),"automation state mismatch");
        // Zero-frame flush must apply a pending restore before offset-zero automation.
        restore(c.get(),initialBytes);params.clearQueue();int32 qi=0,pi=0;ParamID mix=3;
        auto* q=params.addParameterData(mix,qi);require(q!=nullptr,"flush queue");
        ok(q->addPoint(0,.9,pi),"flush point");
        d.numSamples=0;d.numInputs=d.numOutputs=0;d.inputs=d.outputs=nullptr;
        ok(proc->process(d),"flush");
        auto expected=initial;require(applyShuttleNormalized(expected,3,.9),"flush oracle");
        require(save(c.get())==encode(expected),"restore ordering");
        std::cout<<"SDK_AUTOMATION rate="<<rate<<" block="<<block<<" frames="<<total<<" max_error="<<maxError<<std::endl;
    }else{
        // Actual SDK calls from distinct threads. No concurrent lifecycle calls;
        // no automation during stress, so every snapshot must be a whole bank entry.
        const auto a=encode({100,650,700,950,false});
        const auto b=encode({900,180,650,850,true});
        std::atomic<bool> go{false},failed{false},done{false};
        std::atomic<unsigned> reads{0},writes{0};
        std::thread writer([&]{
            while(!go.load(std::memory_order_acquire))std::this_thread::yield();
            try{for(unsigned i=0;i<20000;++i){restore(c.get(),i&1?a:b);++writes;}restore(c.get(),b);}
            catch(...){failed=true;}done.store(true,std::memory_order_release);
        });
        std::thread reader([&]{
            while(!go.load(std::memory_order_acquire))std::this_thread::yield();
            try{do{const auto v=save(c.get());require(v==a||v==b||v==initialBytes,"torn state");++reads;}
                while(!done.load(std::memory_order_acquire));}catch(...){failed=true;}
        });
        go.store(true,std::memory_order_release);unsigned blocks=0;
        d.numSamples=block;params.clearQueue();
        std::fill(left.begin(),left.end(),.03f);std::fill(right.begin(),right.end(),-.02f);
        do{
            input.silenceFlags=0;output.silenceFlags=0;
            if(proc->process(d)!=kResultOk){failed=true;break;}
            for(int j=0;j<block;++j)if(!std::isfinite(outL[j])||!std::isfinite(outR[j])||std::abs(outL[j])>1.f||std::abs(outR[j])>1.f)failed=true;
            ++blocks;
        }while(!done.load(std::memory_order_acquire)||blocks<256);
        writer.join();reader.join();
        require(!failed&&writes==20000&&reads>0,"concurrent SDK state");
        ok(proc->process(d),"final block");require(save(c.get())==b,"final restore");
        std::cout<<"SDK_STATE_PASS writes="<<writes<<" reads="<<reads<<" blocks="<<blocks<<std::endl;
    }
    ok(proc->setProcessing(false),"stop");life.running=false;
    ok(c->setActive(false),"deactivate");life.active=false;
    ok(c->terminate(),"terminate");life.initialized=false;
    return result;
}
}
int main(int argc,char** argv){
    try{
        require(argc==2,"usage: shuttle_sdk_probe <bundle>");
        auto host=owned(new HostApplication);std::string error;
        auto module=VST3::Hosting::Module::create(argv[1],error);if(!module)throw std::runtime_error(error);
        const auto& factory=module->getFactory();factory.setHostContext(host.get());
        for(const auto& info:factory.classInfos()){
            if(info.category()!=kVstAudioEffectClass)continue;
            require(info.name()=="MHAC Palimpsest Shuttle"&&info.version()=="0.1.0","identity");
            for(int rate:{44100,48000,96000}){
                auto a=run(factory,info,host.get(),rate,127,false);
                auto b=run(factory,info,host.get(),rate,1024,false);
                require(a==b,"partition mismatch");
            }
            run(factory,info,host.get(),48000,128,true);
            std::cout<<"SDK_PROBE_PASS automation_cases=6 stereo_frames=120000"<<std::endl;return 0;
        }
        throw std::runtime_error("no effect");
    }catch(const std::exception& e){std::cerr<<"SDK_PROBE_FAIL "<<e.what()<<std::endl;return 1;}
}
