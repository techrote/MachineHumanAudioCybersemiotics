// ACCEL-010: original diagnostic host using the official VST 3.8.0 hosting API.
// No plug-in source is built or modified. Only the pinned packaged module is loaded.
#include "public.sdk/source/vst/hosting/module.h"
#include "public.sdk/source/vst/hosting/hostclasses.h"
#include "public.sdk/source/vst/hosting/eventlist.h"
#include "public.sdk/source/vst/hosting/parameterchanges.h"
#include "pluginterfaces/vst/ivstaudioprocessor.h"
#include "pluginterfaces/vst/ivstcomponent.h"
#include "pluginterfaces/vst/vstspeaker.h"
#include <algorithm>
#include <array>
#include <cmath>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
using namespace Steinberg;
using namespace Steinberg::Vst;
namespace {
void check(bool ok,const char* stage){if(!ok)throw std::runtime_error(stage);}
void result(tresult v,const char* stage){std::cout<<stage<<"="<<v<<std::endl;check(v==kResultOk,stage);}
struct Observation {std::vector<float> left,right;double peak=0,stemError=0;int rejected=0;};
struct Lifecycle {
    IComponent* c; IAudioProcessor* p; bool initialized=false,active=false,running=false;
    ~Lifecycle(){if(running)p->setProcessing(false);if(active)c->setActive(false);if(initialized)c->terminate();}
};
Observation run(const VST3::Hosting::PluginFactory& factory,const VST3::Hosting::ClassInfo& info,
                HostApplication* host,int rate,int block,bool aux,bool malformed,bool inactiveMemory=false){
    std::cout<<"case rate="<<rate<<" block="<<block<<" aux="<<aux<<" malformed="<<malformed<<" inactive_memory="<<inactiveMemory<<std::endl;
    auto c=factory.createInstance<IComponent>(info.ID());
    check(bool(c),"component create");
    FUnknownPtr<IAudioProcessor> p(c.get());check(p.getInterface()!=nullptr,"processor interface");
    Lifecycle guard{c.get(),p.getInterface()};
    result(c->initialize(host),"initialize");guard.initialized=true;
    check(c->getBusCount(kAudio,kInput)==0&&c->getBusCount(kAudio,kOutput)==4&&
          c->getBusCount(kEvent,kInput)==1,"bus inventory");
    std::array<SpeakerArrangement,4> arrangements{SpeakerArr::kStereo,SpeakerArr::kMono,SpeakerArr::kMono,SpeakerArr::kMono};
    result(p->setBusArrangements(nullptr,0,arrangements.data(),4),"setBusArrangements");
    for(int i=0;i<4;++i){
        BusInfo b{};result(c->getBusInfo(kAudio,kOutput,i,b),"getBusInfo");
        check(b.channelCount==(i==0?2:1),"channel count");
        result(c->activateBus(kAudio,kOutput,i,i==0||aux),"activate audio");
    }
    result(c->activateBus(kEvent,kInput,0,true),"activate event");
    result(p->canProcessSampleSize(kSample32),"sample format");
    ProcessSetup setup{kRealtime,kSample32,block,double(rate)};
    result(p->setupProcessing(setup),"setupProcessing");
    result(c->setActive(true),"setActive");guard.active=true;
    result(p->setProcessing(true),"setProcessing");guard.running=true;
    ParameterChanges params(19); EventList events(4);
    std::array<std::array<float*,2>,4> pointers{};
    std::array<std::vector<float>,5> samples;
    for(auto& s:samples)s.resize(block);
    pointers[0]={samples[0].data(),samples[1].data()};
    for(int i=1;i<4;++i)pointers[i][0]=(aux||inactiveMemory)?samples[i+1].data():nullptr;
    std::array<AudioBusBuffers,4> buses{};
    for(int i=0;i<4;++i){buses[i].numChannels=i==0?2:(malformed?0:1);buses[i].channelBuffers32=pointers[i].data();}
    ProcessData data{};data.processMode=kRealtime;data.symbolicSampleSize=kSample32;
    data.numOutputs=4;data.outputs=buses.data();data.inputEvents=&events;data.inputParameterChanges=&params;
    Observation obs;
    // The foundry gain smoother settles in 5 ms. Allow silent pre-roll so
    // lane isolation is not falsely rejected by the legitimate default-gain ramp.
    const int total=rate*2/5,on=rate/50+17,off=rate/5+13;
    obs.left.reserve(total);obs.right.reserve(total);
    for(int pos=0;pos<total;pos+=block){
        int n=std::min(block,total-pos);data.numSamples=n;events.clear();params.clearQueue();
        for(auto& s:samples)std::fill(s.begin(),s.end(),-0.75f);
        for(auto& bus:buses)bus.silenceFlags=0;
        if(pos==0){
            // All pitch slots unison, manual clocks; only latch gain active.
            for(ParamID id=1000;id<1019;++id){
                int32 qi=0,pi=0;auto* q=params.addParameterData(id,qi);check(q!=nullptr,"parameter queue");
                result(q->addPoint(0,id==1008?1.0:0.0,pi),"parameter point");
            }
        }
        if(on>=pos&&on<pos+n){
            Event e{};e.busIndex=0;e.sampleOffset=on-pos;e.type=Event::kNoteOnEvent;
            e.noteOn.channel=0;e.noteOn.pitch=69;e.noteOn.velocity=100.f/127;e.noteOn.noteId=-1;
            result(events.addEvent(e),"note on");
        }
        if(off>=pos&&off<pos+n){
            Event e{};e.busIndex=0;e.sampleOffset=off-pos;e.type=Event::kNoteOffEvent;
            e.noteOff.channel=0;e.noteOff.pitch=69;e.noteOff.noteId=-1;
            result(events.addEvent(e),"note off");
        }
        auto rc=p->process(data);
        if(rc!=kResultOk){++obs.rejected;std::cout<<"process rejected pos="<<pos<<" rc="<<rc<<std::endl;}
        if(malformed)continue;
        check(rc==kResultOk,"process valid buffers");
        if(!aux){
            for(int k=1;k<4;++k){
                check((buses[k].silenceFlags&1u)!=0,"inactive stem silence flag");
                if(inactiveMemory)for(int j=0;j<n;++j)
                    check(samples[k+1][j]==0.f,"inactive stem poison not cleared");
            }
        }
        for(int j=0;j<n;++j){
            float l=samples[0][j],r=samples[1][j];check(std::isfinite(l)&&std::isfinite(r),"nonfinite output");
            check(std::abs(l)<=1.f&&std::abs(r)<=1.f,"output bound");
            obs.left.push_back(l);obs.right.push_back(r);obs.peak=std::max(obs.peak,double(std::abs(l)));
            if(aux){
                for(int k=2;k<5;++k)check(std::isfinite(samples[k][j]),"nonfinite stem");
                obs.stemError=std::max(obs.stemError,std::abs(double(l)-samples[2][j]-.5*samples[3][j]));
                obs.stemError=std::max(obs.stemError,std::abs(double(r)-samples[4][j]-.5*samples[3][j]));
            }
        }
    }
    if(!malformed){
        check(obs.peak>1e-4,"silent note");
        for(int i=0;i<on;++i)check(std::abs(obs.left[i])<1e-7,"pre-note signal");
        for(float v:obs.right)check(std::abs(v)<1e-6,"inactive lane audible");
        for(int i=rate*3/10;i<total;++i)check(std::abs(obs.left[i])<1e-6,"release");
        double re=0,im=0;const double tau=6.283185307179586;
        for(int i=rate/10;i<rate/5;++i){double t=tau*440*i/rate;re+=obs.left[i]*std::cos(t);im+=obs.left[i]*std::sin(t);}
        double a=2*std::hypot(re,im)/(rate/5-rate/10);
        check(a>1e-4&&a<=obs.peak*1.01,"440 Hz witness");
        check(obs.stemError<2e-6,"stem reconstruction");
        std::cout<<"positive peak="<<obs.peak<<" fundamental="<<a<<" stem_error="<<obs.stemError<<std::endl;
    }else{
        // Deliberately nonconformant: this is a diagnostic negative, not a host acceptance case.
        check(obs.rejected>0,"expected rejection of zero-channel inactive auxiliaries");
        std::cout<<"negative rejected_blocks="<<obs.rejected<<std::endl;
    }
    return obs;
}
}
int main(int argc,char** argv){
    try{
        check(argc==2,"usage: winters_sdk_probe <VST3 bundle>");
        auto host=owned(new HostApplication);std::string error;
        auto module=VST3::Hosting::Module::create(argv[1],error);
        if(!module)throw std::runtime_error(error);
        const auto& factory=module->getFactory();factory.setHostContext(host.get());
        for(const auto& info:factory.classInfos()){
            if(info.category()!=kVstAudioEffectClass)continue;
            check(info.name()=="MHAC Three Winters"&&info.version()=="0.2.0","module identity");
            int positive=0;
            for(int rate:{44100,48000,96000}){
                Observation reference;
                for(int block:{257,1024}){
                    auto off=run(factory,info,host.get(),rate,block,false,false);
                    auto on=run(factory,info,host.get(),rate,block,true,false);
                    auto supplied=run(factory,info,host.get(),rate,block,false,false,true);
                    check(off.left==supplied.left&&off.right==supplied.right,"inactive stem memory changed main waveform");
                    check(off.left==on.left&&off.right==on.right,"aux activation changed main waveform");
                    if(block==257)reference=off;
                    else check(reference.left==off.left&&reference.right==off.right,"block partition mismatch");
                    positive+=3;
                }
            }
            auto negative=run(factory,info,host.get(),44100,257,false,true);
            std::cout<<"SDK_PROBE_PASS positives="<<positive<<" negative_rejected="<<negative.rejected<<std::endl;
            return 0;
        }
        throw std::runtime_error("no audio processor class");
    }catch(const std::exception& e){std::cerr<<"SDK_PROBE_FAIL "<<e.what()<<std::endl;return 1;}
}
