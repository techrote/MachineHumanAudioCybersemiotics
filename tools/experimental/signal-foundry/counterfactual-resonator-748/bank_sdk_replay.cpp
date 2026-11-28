// FX-011P: reuse the native oracle with a loaded VST3 processor.
#define MHAC_BANK_SDK_REPLAY
#include "bank_optimal_test.cpp"
#include "public.sdk/source/vst/hosting/module.h"
#include "public.sdk/source/vst/hosting/hostclasses.h"
#include "public.sdk/source/vst/hosting/parameterchanges.h"
#include "public.sdk/source/common/memorystream.h"
#include "pluginterfaces/vst/ivstaudioprocessor.h"
#include "pluginterfaces/vst/ivstcomponent.h"
#include "pluginterfaces/vst/ivsteditcontroller.h"
#include "pluginterfaces/vst/vstspeaker.h"
#include <cstring>
#include <type_traits>
using namespace Steinberg;
using namespace Steinberg::Vst;
namespace {
void ok(tresult result,const char* stage="SDK call"){
    if(result!=kResultOk)std::cerr<<stage<<" returned "<<result<<'\n';
    check(result==kResultOk);
}
struct ModuleEngine {
    IComponent* component;
    IAudioProcessor* processor;
    int channels,block,format;
    bool initialized=false,active=false,running=false,paused=false;
    unsigned rendered=0;
    ParameterChanges params{int32(bh::ParamCount)};
    ModuleEngine(IComponent* c,IAudioProcessor* p,HostApplication* host,int nc,int bs,int fmt)
        :component(c),processor(p),channels(nc),block(bs),format(fmt){
        ok(component->initialize(host));initialized=true;
        check(component->getBusCount(kAudio,kInput)==1&&component->getBusCount(kAudio,kOutput)==1);
        SpeakerArrangement arrangement=channels==1?SpeakerArr::kMono:SpeakerArr::kStereo;
        ok(processor->setBusArrangements(&arrangement,1,&arrangement,1));
        ok(component->activateBus(kAudio,kInput,0,true));ok(component->activateBus(kAudio,kOutput,0,true));
        check(processor->canProcessSampleSize(format)==kResultTrue);
    }
    ~ModuleEngine(){
        if(running)processor->setProcessing(false);
        if(active)component->setActive(false);
        if(initialized)component->terminate();
    }
    bool request(const MemoryConfig& config){
        auto b=bh::encode(config);MemoryStream s(b.data(),TSize(b.size()));ok(component->setState(&s));
        check(save()==b);return true;
    }
    bh::State save(){
        MemoryStream s;ok(component->getState(&s));bh::State b{};
        check(s.getSize()==TSize(b.size()));std::memcpy(b.data(),s.getData(),b.size());return b;
    }
    bool prepare(double rate){
        ProcessSetup setup{kRealtime,format,block,rate};ok(processor->setupProcessing(setup),"setupProcessing");
        ok(component->setActive(true),"setActive(true)");active=true;
        ok(processor->setProcessing(true),"setProcessing(true)");running=true;
        // A legal start/stop pair with no intervening audio must also succeed.
        pauseResume();
        check(processor->getLatencySamples()==0&&processor->getTailSamples()==kInfiniteTail);return true;
    }
    void pauseResume(){
        ok(processor->setProcessing(false),"pause setProcessing(false)");running=false;
        ok(processor->setProcessing(true),"resume setProcessing(true)");running=true;
    }
    void finish(){
        check(paused);ok(processor->setProcessing(false),"stop");running=false;
        ok(component->setActive(false),"deactivate");active=false;
        ok(component->terminate(),"terminate");initialized=false;
    }
    template<class T> bool processOptional(const T* l,const T* r,T* ol,T* oright,unsigned n,const bh::Event* ev,unsigned count){
        check(n<=unsigned(block));params.clearQueue();
        // Pause during excitation, without deactivation, and require the same
        // subsequent samples as uninterrupted native DSP (memory retained).
        if(!paused&&rendered>=6000){pauseResume();paused=true;}
        rendered+=n;
        for(unsigned i=0;i<count;++i){int32 qi=0,pi=0;auto* q=params.addParameterData(ev[i].id,qi);
            check(q!=nullptr);ok(q->addPoint(int32(ev[i].offset),ev[i].value,pi));}
        // Input buffers are read-only by contract; VST3 declares mutable pointers.
        T* in[]={const_cast<T*>(l),const_cast<T*>(r)},*out[]={ol,oright};
        AudioBusBuffers ib{},ob{};ib.numChannels=channels;ob.numChannels=channels;
        if constexpr(std::is_same_v<T,float>){ib.channelBuffers32=in;ob.channelBuffers32=out;}
        else {ib.channelBuffers64=in;ob.channelBuffers64=out;}
        for(int k=0;k<channels;++k){
            if(std::all_of(in[k],in[k]+n,[](T x){return x==T(0);}))ib.silenceFlags|=uint64(1)<<k;
            std::fill(out[k],out[k]+n,T(9));
        }
        ProcessData d{};d.processMode=kRealtime;d.symbolicSampleSize=format;d.numSamples=int32(n);
        d.numInputs=1;d.inputs=&ib;d.numOutputs=1;d.outputs=&ob;d.inputParameterChanges=&params;
        ok(processor->process(d),"audio process");uint64 mask=(uint64(1)<<channels)-1;
        for(int k=0;k<channels;++k)for(unsigned i=0;i<n;++i){
            const T x=out[k][i];check(std::isfinite(x)&&std::abs(x)<=T(1));
            if(x!=T(0))mask&=~(uint64(1)<<k);
        }
        check(ob.silenceFlags==mask);return true;
    }
    void stateChecks(){
        MemoryConfig c{};c.wet=321;c.bands[2].hz=777;c.bands[2].excite=false;request(c);
        ProcessData d{};d.processMode=kRealtime;d.symbolicSampleSize=format;d.inputParameterChanges=&params;
        params.clearQueue();ok(processor->process(d));check(save()==bh::encode(c));
        int32 qi=0,pi=0;auto* q=params.addParameterData(bh::Wet,qi);check(q!=nullptr);ok(q->addPoint(0,.625,pi));
        ok(processor->process(d));c.wet=625;check(save()==bh::encode(c));
        auto b=bh::encode(c);MemoryStream bad(b.data(),TSize(b.size()-1));
        check(component->setState(&bad)!=kResultOk);check(save()==b);
        std::array<uint8,44> extra{};std::copy(b.begin(),b.end(),extra.begin());
        MemoryStream appended(extra.data(),TSize(extra.size()));check(component->setState(&appended)!=kResultOk);check(save()==b);
    }
};
template<class T> void run(const VST3::Hosting::PluginFactory& factory,const VST3::Hosting::ClassInfo& info,HostApplication* host,double rate,unsigned band,unsigned block,bool reverse,bool manual,bool mono){
    auto c=factory.createInstance<IComponent>(info.ID());check(bool(c));
    FUnknownPtr<IAudioProcessor> proc(c.get());check(proc.getInterface()!=nullptr);
    ModuleEngine engine(c.get(),proc.getInterface(),host,mono?1:2,int(block),std::is_same_v<T,float>?kSample32:kSample64);
    std::cout<<"SDK_BANK_BEGIN rate="<<rate<<" band="<<band<<" block="<<block<<" reverse="<<reverse<<" manual="<<manual<<" mono="<<mono<<" format="<<engine.format<<std::endl;
    replay<T>(engine,rate,band,block,reverse,manual,mono);engine.stateChecks();engine.finish();
    std::cout<<"SDK_BANK_CASE rate="<<rate<<" band="<<band<<" block="<<block<<" reverse="<<reverse<<" manual="<<manual<<" mono="<<mono<<" format="<<engine.format<<'\n';
}
void controller(const VST3::Hosting::PluginFactory& factory,HostApplication* host){
    unsigned found=0;
    for(const auto& info:factory.classInfos())if(info.category()==kVstComponentControllerClass){
        auto c=factory.createInstance<IEditController>(info.ID());check(bool(c));ok(c->initialize(host));
        check(c->getParameterCount()==int32(bh::ParamCount));
        for(unsigned i=0;i<bh::ParamCount;++i){ParameterInfo pi{};ok(c->getParameterInfo(int32(i),pi));check(pi.id==bh::paramID(i));}
        MemoryConfig config{};config.wet=321;config.bypass=true;config.bands[3].hz=723;config.bands[3].gain=456;config.bands[3].excite=false;
        auto b=bh::encode(config);MemoryStream s(b.data(),TSize(b.size()));ok(c->setComponentState(&s));
        for(unsigned i=0;i<bh::ParamCount;++i){const auto id=bh::paramID(i);check(std::abs(c->getParamNormalized(id)-bh::normalized(config,id))<1e-12);}
        MemoryStream bad(b.data(),TSize(b.size()-1));check(c->setComponentState(&bad)!=kResultOk);
        ok(c->terminate());++found;
    }
    check(found==1);std::cout<<"SDK_BANK_CONTROLLER_PASS parameters=42\n";
}
}
int main(int argc,char** argv){
    check(argc==2);nativeTests(0,nullptr);
    auto host=owned(new HostApplication);std::string error;auto module=VST3::Hosting::Module::create(argv[1],error);
    if(!module){std::cerr<<error<<'\n';return 1;}
    const auto& factory=module->getFactory();factory.setHostContext(host.get());controller(factory,host.get());
    unsigned cases=0;
    for(const auto& info:factory.classInfos())if(info.category()==kVstAudioEffectClass){
        check(info.name()=="MHAC Harmonic Memory Bank"&&info.version()=="0.2.0");
        for(unsigned band=0;band<4;++band)for(bool reverse:{false,true})for(bool manual:{false,true})
            for(unsigned block:{127u,257u})for(bool mono:{false,true}){
                run<float>(factory,info,host.get(),48000,band,block,reverse,manual,mono);
                run<double>(factory,info,host.get(),96000,band,block,reverse,manual,mono);cases+=2;
            }
    }
    check(cases==128);std::cout<<"SDK_BANK_REPLAY_PASS cases="<<cases<<" checks="<<checks<<'\n';
}
