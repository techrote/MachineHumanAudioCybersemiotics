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
constexpr double expected[3][6]={{0,.25,.25,.25,.25,.5},{0,.25,.25,.875,.875,.875},{0,.25,.25,.25,.75,.5}};
double witness(const std::vector<float>& x,int rate,int end,double target){
    constexpr double tau=6.283185307179586;
    const int n=rate/10,start=end-n;
    std::array<double,2> re{},im{};
    for(int i=start;i<end;++i)for(int k=0;k<2;++k){
        double t=tau*440*(k+1)*i/rate;
        re[k]+=x[i]*std::cos(t);im[k]+=x[i]*std::sin(t);
    }
    double a=2*std::hypot(re[0],im[0])/n,b=2*std::hypot(re[1],im[1])/n;
    check(a+b>1e-4,"silent timbre witness");
    check(std::abs(b/(a+b)-target)<.003,"timbre mixture");
    double err=0;
    for(int i=start;i<end;++i){
        double v=x[i];
        for(int k=0;k<2;++k){
            double t=tau*440*(k+1)*i/rate;
            v-=2*(re[k]*std::cos(t)+im[k]*std::sin(t))/n;
        }
        err+=v*v;
    }
    check(std::sqrt(err/n)<2e-4,"timbre residual");
    return b/(a+b);
}
// Derived host profiles: a disabled bus is not an absent arrangement.
constexpr bool activeAux(int bus,int mask){return bus==0||(mask&(1<<(bus-1)))!=0;}
constexpr int hostChannels(int bus,int mask,bool zeroDisabled){return bus==0?2:(zeroDisabled&&!activeAux(bus,mask)?0:1);}
static_assert(hostChannels(1,0,false)==1&&hostChannels(1,0,true)==0&&hostChannels(1,1,true)==1);
struct Observation {std::vector<float> left,right;double peak=0,stemError=0;int rejected=0;};
struct Lifecycle {
    IComponent* c; IAudioProcessor* p; bool initialized=false,active=false,running=false;
    ~Lifecycle(){if(running)p->setProcessing(false);if(active)c->setActive(false);if(initialized)c->terminate();}
};
Observation run(const VST3::Hosting::PluginFactory& factory,const VST3::Hosting::ClassInfo& info,
                HostApplication* host,int rate,int block,bool aux,bool malformed,bool inactiveMemory=false,int lane=-1,int activeMask=-1,bool juceShape=false,bool offline=false){
    const int mask=activeMask<0?(aux?7:0):activeMask;
    check(mask>=0&&mask<=7&&(!juceShape||malformed),"host profile");
    const auto mode=offline||juceShape?kOffline:kRealtime;
    std::cout<<"case rate="<<rate<<" block="<<block<<" aux="<<aux<<" malformed="<<malformed<<" inactive_memory="<<inactiveMemory<<" timbre_lane="<<lane<<" mask="<<mask<<" juce_shape="<<juceShape<<" mode="<<mode<<std::endl;
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
        result(c->activateBus(kAudio,kOutput,i,activeAux(i,mask)),"activate audio");
    }
    result(c->activateBus(kEvent,kInput,0,true),"activate event");
    result(p->canProcessSampleSize(kSample32),"sample format");
    ProcessSetup setup{mode,kSample32,block,double(rate)};
    result(p->setupProcessing(setup),"setupProcessing");
    result(c->setActive(true),"setActive");guard.active=true;
    result(p->setProcessing(true),"setProcessing");guard.running=true;
    ParameterChanges params(19); EventList events(4);
    std::array<std::array<float*,2>,4> pointers{};
    std::array<std::vector<float>,5> samples;
    for(auto& s:samples)s.resize(block);
    pointers[0]={samples[0].data(),samples[1].data()};
    for(int i=1;i<4;++i)pointers[i][0]=(activeAux(i,mask)||inactiveMemory)?samples[i+1].data():nullptr;
    std::array<AudioBusBuffers,4> buses{};
    for(int i=0;i<4;++i){buses[i].numChannels=hostChannels(i,mask,malformed);buses[i].channelBuffers32=juceShape&&buses[i].numChannels==0?nullptr:pointers[i].data();}
    ProcessData data{};data.processMode=mode;data.symbolicSampleSize=kSample32;
    data.numOutputs=4;data.outputs=buses.data();data.inputEvents=&events;data.inputParameterChanges=&params;
    Observation obs;
    // The foundry gain smoother settles in 5 ms. Allow silent pre-roll so
    // lane isolation is not falsely rejected by the legitimate default-gain ramp.
    const int section=rate/5,total=lane<0?rate*2/5:7*section,on=rate/50+17,off=lane<0?rate/5+13:6*section+17;
    obs.left.reserve(total);obs.right.reserve(total);
    for(int pos=0;pos<total;pos+=block){
        int n=std::min(block,total-pos);data.numSamples=n;events.clear();params.clearQueue();
        for(auto& s:samples)std::fill(s.begin(),s.end(),juceShape?0.f:-0.75f);
        for(auto& bus:buses)bus.silenceFlags=0;
        auto point=[&](int sample,ParamID id,double value){
            if(sample<pos||sample>=pos+n)return;
            int32 qi=0,pi=0;auto* q=params.addParameterData(id,qi);check(q!=nullptr,"parameter queue");
            result(q->addPoint(sample-pos,value,pi),"parameter point");
        };
        if(pos==0){
            // All pitch slots unison; independent timbre lane for the extended score.
            std::array<double,19> v{};
            v[8+(lane<0?0:lane)]=1.;
            if(lane>=0){v[7]=.25;v[12]=.25;v[13]=.75;v[14]=1.;v[18]=.25;}
            for(ParamID id=1000;id<1019;++id)point(0,id,v[id-1000]);
        }
        if(lane>=0){
            // Non-block-aligned events exercise actual sample-offset queues.
            point(section+17,1016,1.);
            point(2*section+17,1015,1.);point(2*section+17,1016,0.);
            point(3*section+17,1012,.875);point(3*section+17,1013,.5);
            point(4*section+17,1016,1.);
            point(5*section+17,1015,0.);point(5*section+17,1016,0.);
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
        if(malformed){
            if(juceShape){
                check(rc!=kResultOk,"JUCE-shaped block unexpectedly accepted by pinned strict module");
                for(int k=0;k<2;++k)for(int j=0;j<n;++j)check(samples[k][j]==0.f,"rejected cleared main buffer changed");
            }
            continue;
        }
        check(rc==kResultOk,"process valid buffers");
        {
            for(int k=1;k<4;++k){
                if(activeAux(k,mask))continue;
                check((buses[k].silenceFlags&1u)!=0,"inactive stem silence flag");
                if(inactiveMemory)for(int j=0;j<n;++j)
                    check(samples[k+1][j]==0.f,"inactive stem poison not cleared");
            }
        }
        for(int j=0;j<n;++j){
            float l=samples[0][j],r=samples[1][j];check(std::isfinite(l)&&std::isfinite(r),"nonfinite output");
            check(std::abs(l)<=1.f&&std::abs(r)<=1.f,"output bound");
            obs.left.push_back(l);obs.right.push_back(r);obs.peak=std::max(obs.peak,double(std::abs(l)));
            if(lane<0){
                if(activeAux(1,mask))check(std::abs(samples[2][j]-l)<2e-6,"latch stem mismatch");
                if(activeAux(2,mask))check(std::abs(samples[3][j])<2e-6,"pause stem leak");
                if(activeAux(3,mask))check(std::abs(samples[4][j])<2e-6,"snapshot stem leak");
            }
            if(mask==7){
                for(int k=2;k<5;++k)check(std::isfinite(samples[k][j]),"nonfinite stem");
                obs.stemError=std::max(obs.stemError,std::abs(double(l)-samples[2][j]-.5*samples[3][j]));
                obs.stemError=std::max(obs.stemError,std::abs(double(r)-samples[4][j]-.5*samples[3][j]));
            }
        }
    }
    if(lane>=0){
        for(int i=0;i<total;++i){
            if(i<on||i>=total-rate/10)
                check(std::abs(obs.left[i])<1e-6&&std::abs(obs.right[i])<1e-6,"timbre pre-note/release");
            if(lane==1)check(std::abs(obs.left[i]-obs.right[i])<2e-6,"pause stereo");
            else check(std::abs(lane==0?obs.right[i]:obs.left[i])<2e-6,"inactive timbre lane");
        }
        for(int k=0;k<6;++k){
            double measured=witness(lane==2?obs.right:obs.left,rate,(k+1)*section,expected[lane][k]);
            std::cout<<"TIMBRE_WITNESS rate="<<rate<<" block="<<block<<" lane="<<lane<<" section="<<k<<" ratio="<<measured<<std::endl;
        }
    }else if(!malformed){
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
        if(juceShape)check(obs.rejected==(total+block-1)/block,"JUCE-shaped rejection count");
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
            // Source-derived JUCE host shape, not an intercepted Pedalboard call.
            // Disabled layouts are mapped to zero channels and a null channel array,
            // even though the last enabled (mono) arrangements remain negotiated.
            // The pinned strict processor should reject this, leaving the precleared
            // output silent. The conformant offline twin must actually sound.
            int shaped=0,mixed=0,rejected=0;
            for(int rate:{44100,48000,96000})for(int block:{257,1024}){
                auto baseline=run(factory,info,host.get(),rate,block,false,false,false,-1,0,false,true);
                for(int mask=1;mask<7;++mask){
                    auto m=run(factory,info,host.get(),rate,block,false,false,true,-1,mask,false,true);
                    check(m.left==baseline.left&&m.right==baseline.right,"mixed activation changed main waveform");
                    ++mixed;
                }
                auto j=run(factory,info,host.get(),rate,block,false,true,false,-1,0,true);
                rejected+=j.rejected;++shaped;
            }
            std::cout<<"HOST_SHAPE_PROBE_PASS cases="<<shaped<<" rejected_blocks="<<rejected<<" mixed_activation_cases="<<mixed<<std::endl;
            int timbreCases=0;
            for(int rate:{44100,48000,96000})for(int lane=0;lane<3;++lane){
                auto a=run(factory,info,host.get(),rate,257,false,false,false,lane);
                auto b=run(factory,info,host.get(),rate,1024,false,false,false,lane);
                check(a.left==b.left&&a.right==b.right,"timbre block partition mismatch");
                timbreCases+=2;
            }
            std::cout<<"TIMBRE_PROBE_PASS cases="<<timbreCases<<" windows="<<timbreCases*6<<std::endl;
            return 0;
        }
        throw std::runtime_error("no audio processor class");
    }catch(const std::exception& e){std::cerr<<"SDK_PROBE_FAIL "<<e.what()<<std::endl;return 1;}
}
