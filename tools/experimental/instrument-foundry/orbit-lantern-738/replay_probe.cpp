// INST-011R: shared native reference and actual module replay (SDK build only).
#include "host.hpp"
#include <iostream>
#include <iterator>
#include <stdexcept>
#include <vector>
#include <type_traits>
using namespace mhac::orbit;
using namespace mhac::orbit::host;
namespace replay {
void require(bool yes,const char* stage){if(!yes)throw std::runtime_error(stage);}
constexpr Patch initial{750,800,0,2,1000};
struct Control {int offset; unsigned index; double value;};
constexpr Control controls[]={{17,0,1.},{1041,4,.5},{3089,2,.625},{3089,5,.85},{3089,6,0.},{4113,4,1.},{6161,0,.25},{6161,6,.2},{9233,3,.5},{9233,5,0.},{12305,3,1.},{12305,5,1.},{15377,1,.2},{18449,0,.75}};
struct Note {int offset,id,channel,pitch; bool on;};
std::vector<Note> score(int identity){
    std::vector<Note> out;
    for(int i=0;i<8;++i){const int id=identity==0?i:identity==1?7:-1;const int start=17+i*3072;
        out.push_back({start,id,2,69,true});out.push_back({start+1024,id,2,69,false});}
    return out;
}
int frames(double rate){return 17+8*3072+int(std::ceil(rate))+2048;}
struct Ref {
    Live live; std::vector<Note> notes; std::size_t ni=0,ci=0; int admits=0; bool sustain=false;
    Ref(double rate,int identity,bool enabled):notes(score(identity)),sustain(enabled){require(live.prepare(rate)&&live.setPatch(initial),"native prepare");}
    void sample(int i,double& l,double& r){
        while(ci<std::size(controls)&&controls[ci].offset==i){const auto c=controls[ci++];if(sustain||c.index<5)require(live.parameter(c.index,c.value),"native control");}
        while(ni<notes.size()&&notes[ni].offset==i){const auto n=notes[ni++];
            require(n.on?live.on(n.id,n.channel,n.pitch,25.,.75):live.off(n.id,n.channel,n.pitch),"native note admission");if(n.on)++admits;}
        live.tick(l,r);require(std::isfinite(l)&&std::isfinite(r)&&std::abs(l)<=.52&&std::abs(r)<=.52,"native bound");
    }
};
template<class T> std::vector<T> native(double rate,int channels,int identity,bool sustain){
    Ref ref(rate,identity,sustain);std::vector<T> output;double peak=0.;
    for(int i=0;i<frames(rate);++i){double l=0,r=0;ref.sample(i,l,r);peak=std::max({peak,std::abs(l),std::abs(r)});
        if(i<17||i>=frames(rate)-1024)require(l==0.&&r==0.,"native silence boundary");
        output.push_back(T(channels==1?(l+r)*.5:l));if(channels==2)output.push_back(T(r));}
    require(ref.admits==8&&ref.live.active()==0&&peak>.001,"native render witness");return output;
}
void nativeTests(){
    unsigned cases=0;
    for(bool sustain:{false,true})for(double rate:{44100.,48000.,96000.})for(int channels:{1,2}){
        const auto a=native<double>(rate,channels,0,sustain);const auto b=native<float>(rate,channels,0,sustain);
        for(std::size_t i=0;i<a.size();++i)require(float(a[i])==b[i],"native format conversion");
        for(int identity:{1,2}){require(native<double>(rate,channels,identity,sustain)==a,"native identity double");require(native<float>(rate,channels,identity,sustain)==b,"native identity float");}
        cases+=6;
    }
    std::cout<<"NATIVE_REPLAY_PASS cases="<<cases<<" notes_per_case=8\n";
}
}
#ifdef MHAC_ORBIT_SDK_REPLAY
#include "public.sdk/source/vst/hosting/module.h"
#include "public.sdk/source/vst/hosting/hostclasses.h"
#include "public.sdk/source/vst/hosting/parameterchanges.h"
#include "public.sdk/source/vst/hosting/eventlist.h"
#include "public.sdk/source/common/memorystream.h"
#include "pluginterfaces/vst/ivstaudioprocessor.h"
#include "pluginterfaces/vst/ivstcomponent.h"
#include "pluginterfaces/vst/ivsteditcontroller.h"
#include "pluginterfaces/vst/vstspeaker.h"
#include <cstring>
using namespace Steinberg;
using namespace Steinberg::Vst;
namespace replay {
void ok(tresult code,const char* stage){require(code==kResultOk,stage);}
void restore(IComponent* c,Patch p){auto bytes=encodeFull(p);MemoryStream s(bytes.data(),TSize(stateSize(p)));ok(c->setState(&s),"restore");}
void saved(IComponent* c,Patch p){MemoryStream s;ok(c->getState(&s),"save");const auto b=encodeFull(p);require(s.getSize()==stateSize(p)&&std::memcmp(s.getData(),b.data(),stateSize(p))==0,"saved bytes");}
struct Life {
    IComponent* c; IAudioProcessor* p; bool initialized=false,active=false,running=false;
    ~Life(){if(running)p->setProcessing(false);if(active)c->setActive(false);if(initialized)c->terminate();}
};
template<class T> void sdkRun(const VST3::Hosting::PluginFactory& factory,const VST3::Hosting::ClassInfo& info,HostApplication* host,double rate,int channels,int identity,int block,bool sustain){
    auto c=factory.createInstance<IComponent>(info.ID());require(bool(c),"component");
    FUnknownPtr<IAudioProcessor> proc(c.get());require(proc.getInterface()!=nullptr,"audio processor");Life life{c.get(),proc.getInterface()};
    ok(c->initialize(host),"initialize");life.initialized=true;
    require(c->getBusCount(kAudio,kInput)==0&&c->getBusCount(kAudio,kOutput)==1&&c->getBusCount(kEvent,kInput)==1,"bus counts");
    SpeakerArrangement arrangement=channels==1?SpeakerArr::kMono:SpeakerArr::kStereo;
    ok(proc->setBusArrangements(nullptr,0,&arrangement,1),"arrangement");ok(c->activateBus(kAudio,kOutput,0,true),"audio bus");ok(c->activateBus(kEvent,kInput,0,true),"event bus");
    restore(c.get(),initial);saved(c.get(),initial);
    const int32 format=std::is_same_v<T,float>?kSample32:kSample64;
    ProcessSetup setup{kRealtime,format,block,rate};ok(proc->setupProcessing(setup),"setup");ok(c->setActive(true),"activate");life.active=true;
    ok(proc->setProcessing(true),"start");life.running=true;saved(c.get(),initial);
    require(proc->getLatencySamples()==0&&proc->getTailSamples()==uint32(std::ceil(rate)),"latency/tail");
    Ref ref(rate,identity,sustain);ParameterChanges params(count);EventList events(32);
    std::vector<T> left(block),right(block);T* ptr[]={left.data(),right.data()};AudioBusBuffers bus{};bus.numChannels=channels;
    if constexpr(std::is_same_v<T,float>)bus.channelBuffers32=ptr;else bus.channelBuffers64=ptr;
    ProcessData d{};d.processMode=kRealtime;d.symbolicSampleSize=format;d.numOutputs=1;d.outputs=&bus;d.inputEvents=&events;d.inputParameterChanges=&params;
    double error=0.,peak=0.;
    for(int pos=0;pos<frames(rate);pos+=block){const int n=std::min(block,frames(rate)-pos);d.numSamples=n;params.clearQueue();events.clear();
        for(const auto& a:controls)if((sustain||a.index<5)&&a.offset>=pos&&a.offset<pos+n){int32 qi=0,pi=0;auto* q=params.addParameterData(firstID+a.index,qi);require(q!=nullptr,"queue");ok(q->addPoint(a.offset-pos,a.value,pi),"point");}
        for(const auto& a:ref.notes)if(a.offset>=pos&&a.offset<pos+n){Steinberg::Vst::Event e{};e.busIndex=0;e.sampleOffset=a.offset-pos;
            if(a.on){e.type=Steinberg::Vst::Event::kNoteOnEvent;e.noteOn.channel=int16(a.channel);e.noteOn.pitch=int16(a.pitch);e.noteOn.noteId=a.id;e.noteOn.velocity=.75f;e.noteOn.tuning=25.f;}
            else{e.type=Steinberg::Vst::Event::kNoteOffEvent;e.noteOff.channel=int16(a.channel);e.noteOff.pitch=int16(a.pitch);e.noteOff.noteId=a.id;}
            ok(events.addEvent(e),"event");}
        std::fill(left.begin(),left.end(),T(9));std::fill(right.begin(),right.end(),T(9));bus.silenceFlags=0;
        ok(proc->process(d),"process");uint64 mask=(uint64(1)<<channels)-1;
        for(int j=0;j<n;++j){double l=0,r=0;ref.sample(pos+j,l,r);const T expected[]={T(channels==1?(l+r)*.5:l),T(r)};
            for(int k=0;k<channels;++k){const double v=ptr[k][j];require(std::isfinite(v)&&std::abs(v)<=.521,"module bound");error=std::max(error,std::abs(v-double(expected[k])));peak=std::max(peak,std::abs(v));if(v!=0.)mask&=~(uint64(1)<<k);if(pos+j<17||pos+j>=frames(rate)-1024)require(v==0.,"module silence boundary");}}
        require(bus.silenceFlags==mask,"silence flags");
    }
    require(ref.admits==8&&ref.live.active()==0&&peak>.001&&error< (std::is_same_v<T,float>?2e-6:1e-10),"render oracle");saved(c.get(),ref.live.patch());
    // Restore all historical state encodings; flush automation on the same boundary.
    events.clear();params.clearQueue();d.numSamples=0;d.numOutputs=0;d.outputs=nullptr;
    for(Patch p: {Patch{250,80,-25,0,0},Patch{500,160,0,1,0},initial,Patch{250,800,0,2,1000,850,900}}){restore(c.get(),p);saved(c.get(),p);ok(proc->process(d),"restore flush");saved(c.get(),p);}
    int32 qi=0,pi=0;auto* q=params.addParameterData(firstID+4,qi);require(q!=nullptr,"flush queue");ok(q->addPoint(0,.25,pi),"flush point");restore(c.get(),initial);
    ok(proc->process(d),"parameter flush");auto expected=initial;expected.spectralDepth=250;saved(c.get(),expected);
    params.clearQueue();q=params.addParameterData(firstID+5,qi);require(q!=nullptr,"sustain flush queue");ok(q->addPoint(0,.75,pi),"sustain flush point");
    q=params.addParameterData(firstID+6,qi);require(q!=nullptr,"period flush queue");ok(q->addPoint(0,1.,pi),"period flush point");ok(proc->process(d),"sustain flush");expected.sustainDepth=750;expected.sustainMs=8000;saved(c.get(),expected);
    auto bad=encodeFull(expected);MemoryStream broken(bad.data(),TSize(16));require(c->setState(&broken)!=kResultOk,"truncated state admitted");saved(c.get(),expected);
    ok(proc->setProcessing(false),"stop");life.running=false;ok(c->setActive(false),"deactivate");life.active=false;ok(c->terminate(),"terminate");life.initialized=false;
    std::cout<<"SDK_REPLAY rate="<<rate<<" sustain="<<sustain<<" channels="<<channels<<" identity="<<identity<<" format="<<format<<" block="<<block<<" frames="<<frames(rate)<<" max_error="<<error<<'\n';
}
void controllerTest(const VST3::Hosting::PluginFactory& factory,HostApplication* host){
    unsigned found=0;
    for(const auto& info:factory.classInfos())if(info.category()==kVstComponentControllerClass){
        auto c=factory.createInstance<IEditController>(info.ID());require(bool(c),"controller");ok(c->initialize(host),"controller initialize");
        struct End {IEditController* c;~End(){c->terminate();}} end{c.get()};
        require(c->getParameterCount()==int32(count),"controller parameter count");
        for(unsigned i=0;i<count;++i){ParameterInfo pi{};ok(c->getParameterInfo(int32(i),pi),"parameter info");require(pi.id==firstID+i,"parameter identity");}
        for(Patch p:{Patch{250,80,-25,0,0},Patch{500,160,0,1,0},initial,Patch{250,800,0,2,1000,850,900}}){
            auto b=encodeFull(p);MemoryStream s(b.data(),TSize(stateSize(p)));ok(c->setComponentState(&s),"controller restore");
            for(unsigned i=0;i<count;++i)require(std::abs(c->getParamNormalized(firstID+i)-normalized(p,i))<1e-12,"controller normalized restore");}
        ++found;
    }
    require(found==1,"controller count");std::cout<<"SDK_CONTROLLER_PASS encodings=4 parameters=7\n";
}
void sdkTests(const char* path){
    auto host=owned(new HostApplication);std::string error;auto module=VST3::Hosting::Module::create(path,error);if(!module)throw std::runtime_error(error);
    const auto& factory=module->getFactory();factory.setHostContext(host.get());controllerTest(factory,host.get());unsigned cases=0;
    for(const auto& info:factory.classInfos())if(info.category()==kVstAudioEffectClass){require(info.name()=="MHAC Orbit Lantern"&&info.version()=="0.4.0","module identity");
        for(bool sustain:{false,true})for(double rate:{44100.,48000.,96000.})for(int channels:{1,2})for(int identity:{0,1,2})for(int block:{127,1024}){sdkRun<float>(factory,info,host.get(),rate,channels,identity,block,sustain);sdkRun<double>(factory,info,host.get(),rate,channels,identity,block,sustain);cases+=2;}}
    require(cases==144,"module count");std::cout<<"SDK_REPLAY_PASS cases="<<cases<<'\n';
}
}
#endif
int main(int argc,char** argv){try{
    replay::nativeTests();
#ifdef MHAC_ORBIT_SDK_REPLAY
    replay::require(argc==2,"usage: orbit_sdk_replay <bundle>");replay::sdkTests(argv[1]);
#else
    (void)argc;(void)argv;
#endif
    return 0;
}catch(const std::exception& e){std::cerr<<"REPLAY_FAIL "<<e.what()<<'\n';return 1;}}
