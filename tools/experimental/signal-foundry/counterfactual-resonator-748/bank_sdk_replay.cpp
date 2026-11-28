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
    int channels,block,format,keyChannels;
    bool initialized=false,active=false,running=false,paused=false;
    unsigned rendered=0;
    ParameterChanges params{int32(bh::ParamCount)};
    ModuleEngine(IComponent* c,IAudioProcessor* p,HostApplication* host,int nc,int bs,int fmt,int nk=0,bool keyed=false)
        :component(c),processor(p),channels(nc),block(bs),format(fmt),keyChannels(nk){
        ok(component->initialize(host));initialized=true;
        check(component->getBusCount(kAudio,kInput)==2&&component->getBusCount(kAudio,kOutput)==1);
        BusInfo keyInfo{};ok(component->getBusInfo(kAudio,kInput,1,keyInfo));check(keyInfo.busType==kAux&&!(keyInfo.flags&BusInfo::kDefaultActive));
        SpeakerArrangement arrangement=channels==1?SpeakerArr::kMono:SpeakerArr::kStereo;
        SpeakerArrangement inputs[]={arrangement,nk==1?SpeakerArr::kMono:SpeakerArr::kStereo};
        ok(processor->setBusArrangements(inputs,nk?2:1,&arrangement,1));
        ok(component->activateBus(kAudio,kInput,1,keyed));
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
    template<class T> bool processOptional(const T* l,const T* r,T* ol,T* oright,unsigned n,const bh::Event* ev,unsigned count,const T* kl=nullptr,const T* kr=nullptr){
        check(n<=unsigned(block));params.clearQueue();
        // Pause during excitation, without deactivation, and require the same
        // subsequent samples as uninterrupted native DSP (memory retained).
        if(!paused&&rendered>=6000){pauseResume();paused=true;}
        rendered+=n;
        for(unsigned i=0;i<count;++i){int32 qi=0,pi=0;auto* q=params.addParameterData(ev[i].id,qi);
            check(q!=nullptr);ok(q->addPoint(int32(ev[i].offset),ev[i].value,pi));}
        // Input buffers are read-only by contract; VST3 declares mutable pointers.
        T* in[]={const_cast<T*>(l),const_cast<T*>(r)},*out[]={ol,oright};
        T* key[]={const_cast<T*>(kl),const_cast<T*>(kr)};
        AudioBusBuffers ib[2]{},ob{};ib[0].numChannels=channels;ob.numChannels=channels;ib[1].numChannels=keyChannels;
        if constexpr(std::is_same_v<T,float>){ib[0].channelBuffers32=in;ib[1].channelBuffers32=key;ob.channelBuffers32=out;}
        else {ib[0].channelBuffers64=in;ib[1].channelBuffers64=key;ob.channelBuffers64=out;}
        for(int k=0;k<keyChannels;++k)if(!key[k]||std::all_of(key[k],key[k]+n,[](T x){return x==T(0);}))ib[1].silenceFlags|=uint64(1)<<k;
        for(int k=0;k<channels;++k){
            if(std::all_of(in[k],in[k]+n,[](T x){return x==T(0);}))ib[0].silenceFlags|=uint64(1)<<k;
            std::fill(out[k],out[k]+n,T(9));
        }
        ProcessData d{};d.processMode=kRealtime;d.symbolicSampleSize=format;d.numSamples=int32(n);
        d.numInputs=keyChannels?2:1;d.inputs=ib;d.numOutputs=1;d.outputs=&ob;d.inputParameterChanges=&params;
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
        std::array<uint8,bh::State{}.size()+1> extra{};std::copy(b.begin(),b.end(),extra.begin());
        MemoryStream appended(extra.data(),TSize(extra.size()));check(component->setState(&appended)!=kResultOk);check(save()==b);
        auto legacy=b;legacy[3]='1';MemoryStream old(legacy.data(),TSize(bh::LegacyStateSize));
        ok(component->setState(&old));check(save()==b);
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
template<class T> void runBudget(const VST3::Hosting::PluginFactory& factory,const VST3::Hosting::ClassInfo& info,HostApplication* host,double rate,unsigned block,bool energy,bool mono){
    auto c=factory.createInstance<IComponent>(info.ID());check(bool(c));
    FUnknownPtr<IAudioProcessor> proc(c.get());check(proc.getInterface()!=nullptr);
    ModuleEngine engine(c.get(),proc.getInterface(),host,mono?1:2,int(block),std::is_same_v<T,float>?kSample32:kSample64);
    budgetReplay<T>(engine,rate,block,energy,mono);engine.finish();
    std::cout<<"SDK_BANK_BUDGET_CASE rate="<<rate<<" block="<<block<<" energy="<<energy<<" mono="<<mono<<" format="<<engine.format<<'\n';
}
// Compare actual sidechain buffers with the native keyed Host. The old
// one-bus cases remain unchanged apart from the newly advertised aux bus.
template<class T> void runKey(const VST3::Hosting::PluginFactory& factory,const VST3::Hosting::ClassInfo& info,HostApplication* host,unsigned rate,int channels,int nk,bool keyed,unsigned budget){
    auto comp=factory.createInstance<IComponent>(info.ID());check(bool(comp));
    FUnknownPtr<IAudioProcessor> proc(comp.get());check(proc.getInterface()!=nullptr);
    ModuleEngine engine(comp.get(),proc.getInterface(),host,channels,257,std::is_same_v<T,float>?kSample32:kSample64,nk,keyed);
    bh::Host native;MemoryConfig cfg{};cfg.wet=1000;cfg.budget=budget;cfg.energyFirst=true;
    for(unsigned k=0;k<4;++k){auto& b=cfg.bands[k];b.peakMix=1000;b.gain=800;b.selectivity=static_cast<std::uint16_t>((177+k*271)%1001);}
    check(engine.request(cfg)&&native.request(cfg)&&engine.prepare(rate)&&native.prepare(rate));
    std::array<T,257> l{},r{},kl{},kr{},a{},b{},x{},y{};
    std::array<bh::Event,32> ev{};
    for(unsigned start=0;start<rate*3;){
        const unsigned n=std::min(257u,rate*3-start);unsigned numEvents=0;
        for(unsigned i=0;i<n;++i){const unsigned t=start+i;
            const auto pcm=[](double value){return std::round(value*32768)/32768;};
            l[i]=t<rate/4?T(pcm(.85*std::sin(6.283185307179586*117*t/rate))):T(0);
            r[i]=channels==2&&t<rate/4?T(pcm(-.55*std::sin(6.283185307179586*168*t/rate))):T(0);
            bool hit=false;for(unsigned onset:{rate/2,rate/2+rate*3/100,rate,rate*3/2})if(t>=onset&&t<onset+rate/100)hit=true;
            kl[i]=hit&&nk==1?T(-26214.0/32768):T(0);kr[i]=hit&&nk==2?T(-26214.0/32768):T(0);
            if(t==rate/4)for(unsigned k=0;k<4;++k)ev[numEvents++]={i,bh::FirstBand+k*bh::Stride+bh::Excite,0};
            if(t==rate/2||t==rate/2+1)ev[numEvents++]={i,bh::AdmitBudget,t==rate/2?1.:0.};
        }
        check(engine.processOptional(l.data(),r.data(),a.data(),b.data(),n,ev.data(),numEvents,kl.data(),kr.data()));
        check(native.processOptional(l.data(),channels==2?r.data():nullptr,x.data(),channels==2?y.data():nullptr,n,ev.data(),numEvents,keyed,kl.data(),nk==2?kr.data():nullptr));
        for(unsigned i=0;i<n;++i){check(a[i]==x[i]);if(channels==2)check(b[i]==y[i]);}
        start+=n;
    }
    check(engine.save()==native.save());engine.finish();
    std::cout<<"SDK_BANK_KEY_CASE rate="<<rate<<" channels="<<channels<<" key="<<nk<<" active="<<keyed<<" budget="<<budget<<" format="<<engine.format<<'\n';
}
void controller(const VST3::Hosting::PluginFactory& factory,HostApplication* host){
    unsigned found=0;
    for(const auto& info:factory.classInfos())if(info.category()==kVstComponentControllerClass){
        auto c=factory.createInstance<IEditController>(info.ID());check(bool(c));ok(c->initialize(host));
        check(c->getParameterCount()==int32(bh::ParamCount));
        for(unsigned i=0;i<bh::ParamCount;++i){ParameterInfo pi{};ok(c->getParameterInfo(int32(i),pi));check(pi.id==bh::paramID(i));}
        MemoryConfig config{};config.wet=321;config.bypass=true;config.bands[3].hz=723;config.bands[3].gain=456;config.bands[3].excite=false;config.budget=9;config.energyFirst=true;
        auto b=bh::encode(config);MemoryStream s(b.data(),TSize(b.size()));ok(c->setComponentState(&s));
        for(unsigned i=0;i<bh::ParamCount;++i){const auto id=bh::paramID(i);check(std::abs(c->getParamNormalized(id)-bh::normalized(config,id))<1e-12);}
        MemoryStream bad(b.data(),TSize(b.size()-1));check(c->setComponentState(&bad)!=kResultOk);
        auto legacy=b;legacy[3]='1';MemoryStream old(legacy.data(),TSize(bh::LegacyStateSize));ok(c->setComponentState(&old));
        check(c->getParamNormalized(bh::Budget)==0&&c->getParamNormalized(bh::Objective)==0&&c->getParamNormalized(bh::AdmitBudget)==0);
        ok(c->terminate());++found;
    }
    check(found==1);std::cout<<"SDK_BANK_CONTROLLER_PASS parameters=45\n";
}
}
int main(int argc,char** argv){
    check(argc==2);nativeTests(0,nullptr);
    auto host=owned(new HostApplication);std::string error;auto module=VST3::Hosting::Module::create(argv[1],error);
    if(!module){std::cerr<<error<<'\n';return 1;}
    const auto& factory=module->getFactory();factory.setHostContext(host.get());controller(factory,host.get());
    unsigned cases=0,budgetCases=0,keyCases=0;
    for(const auto& info:factory.classInfos())if(info.category()==kVstAudioEffectClass){
        check(info.name()=="MHAC Harmonic Memory Bank"&&info.version()=="0.4.0");
        for(unsigned band=0;band<4;++band)for(bool reverse:{false,true})for(bool manual:{false,true})
            for(unsigned block:{127u,257u})for(bool mono:{false,true}){
                run<float>(factory,info,host.get(),48000,band,block,reverse,manual,mono);
                run<double>(factory,info,host.get(),96000,band,block,reverse,manual,mono);cases+=2;
            }
        for(bool energy:{false,true})for(unsigned block:{127u,257u})for(bool mono:{false,true}){
            runBudget<float>(factory,info,host.get(),48000,block,energy,mono);
            runBudget<double>(factory,info,host.get(),96000,block,energy,mono);budgetCases+=2;
        }
        for(int channels:{1,2})for(int nk:{1,2})for(bool keyed:{false,true})for(unsigned budget:{4u,16u}){
            runKey<float>(factory,info,host.get(),48000,channels,nk,keyed,budget);
            runKey<double>(factory,info,host.get(),96000,channels,nk,keyed,budget);keyCases+=2;
        }
    }
    check(keyCases==32);std::cout<<"SDK_BANK_KEY_PASS cases="<<keyCases<<'\n';
    check(budgetCases==16);std::cout<<"SDK_BANK_BUDGET_PASS cases="<<budgetCases<<'\n';
    check(cases==128);std::cout<<"SDK_BANK_REPLAY_PASS cases="<<cases<<" checks="<<checks<<'\n';
}
