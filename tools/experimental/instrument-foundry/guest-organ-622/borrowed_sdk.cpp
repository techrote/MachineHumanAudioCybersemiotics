// Refs #622: actual SDK event/automation and optional stem replay of Borrowed Rooms.
#include "borrowed_score.hpp"
#include "public.sdk/source/vst/hosting/module.h"
#include "public.sdk/source/vst/hosting/hostclasses.h"
#include "public.sdk/source/vst/hosting/parameterchanges.h"
#include "public.sdk/source/vst/hosting/eventlist.h"
#include "public.sdk/source/common/memorystream.h"
#include "pluginterfaces/vst/ivstaudioprocessor.h"
#include "pluginterfaces/vst/ivstcomponent.h"
#include "pluginterfaces/vst/vstspeaker.h"
#include <cstring>
#include <iomanip>
#include <iostream>
#include <type_traits>
using namespace Steinberg;
using namespace Steinberg::Vst;
namespace {
void ok(tresult r,const char* stage){if(r!=kResultOk)throw std::runtime_error(std::string(stage)+" code="+std::to_string(r));}
struct Life {
    IComponent* c; IAudioProcessor* p; bool initialized=false,active=false,running=false;
    ~Life(){if(running)p->setProcessing(false);if(active)c->setActive(false);if(initialized)c->terminate();}
    void finish(){ok(p->setProcessing(false),"stop");running=false;ok(c->setActive(false),"deactivate");active=false;ok(c->terminate(),"terminate");initialized=false;}
};
void point(ParameterChanges& params,ParamID id,int offset,double value){
    int32 qi=0,pi=0;auto* q=params.addParameterData(id,qi);
    borrowed::check(q!=nullptr,"parameter queue");ok(q->addPoint(offset,value,pi),"parameter point");
}
void note(EventList& list,const borrowed::Event& v,int pos){
    const auto& n=borrowed::score[v.note]; Steinberg::Vst::Event e{};
    e.busIndex=0;e.sampleOffset=v.at-pos;
    if(v.type==1){e.type=Steinberg::Vst::Event::kNoteOnEvent;e.noteOn.channel=0;e.noteOn.pitch=int16(n.pitch);e.noteOn.noteId=int32(v.note)+1;e.noteOn.velocity=float(n.velocity/127.);}
    else{e.type=Steinberg::Vst::Event::kNoteOffEvent;e.noteOff.channel=0;e.noteOff.pitch=int16(n.pitch);e.noteOff.noteId=int32(v.note)+1;}
    ok(list.addEvent(e),"note event");
}
using Sample=std::array<double,4>;
using Audio=std::vector<Sample>;
template<class T> Audio replay(const VST3::Hosting::Module::Ptr& module,HostApplication* host,int rate,int block,bool stereo,bool baseline,const std::vector<guest::Frame>& ref){
    using borrowed::check;
    const auto& factory=module->getFactory();factory.setHostContext(host);
    for(const auto& info:factory.classInfos()){
        if(info.category()!=kVstAudioEffectClass)continue;
        check(info.name()=="MHAC Guest Organ"&&info.version()=="0.3.1","factory identity");
        auto c=factory.createInstance<IComponent>(info.ID());check(bool(c),"component");
        FUnknownPtr<IAudioProcessor> proc(c.get());check(proc.getInterface()!=nullptr,"processor");
        Life life{c.get(),proc.getInterface()};
        ok(c->initialize(host),"initialize");life.initialized=true;
        check(c->getBusCount(kAudio,kInput)==0&&c->getBusCount(kAudio,kOutput)==3&&c->getBusCount(kEvent,kInput)==1,"bus count");
        for(int i=1;i<3;++i){BusInfo bi{};ok(c->getBusInfo(kAudio,kOutput,i,bi),"stem info");check(bi.busType==kAux&&!(bi.flags&BusInfo::kDefaultActive),"stem contract");}
        SpeakerArrangement arr[]={stereo?SpeakerArr::kStereo:SpeakerArr::kMono,SpeakerArr::kMono,SpeakerArr::kMono};
        ok(proc->setBusArrangements(nullptr,0,arr,3),"arrangements");
        ok(c->activateBus(kEvent,kInput,0,true),"events active");
        for(int i=0;i<3;++i)ok(c->activateBus(kAudio,kOutput,i,i==0||stereo),"output activation");
        constexpr int fmt=std::is_same_v<T,float>?kSample32:kSample64;
        check(proc->canProcessSampleSize(fmt)==kResultTrue,"sample format");
        ProcessSetup setup{kRealtime,fmt,block,double(rate)};
        ok(proc->setupProcessing(setup),"setup");ok(c->setActive(true),"activate");life.active=true;
        ok(proc->setProcessing(true),"start");life.running=true;
        check(proc->getLatencySamples()==0,"latency");
        const int total=borrowed::sample(borrowed::duration,rate);
        check(ref.size()==size_t(total),"reference length");
        Audio result(static_cast<size_t>(total));
        std::array<std::vector<T>,4> buffers;for(auto& v:buffers)v.resize(size_t(block));
        T* main[]={buffers[0].data(),buffers[1].data()};T* base[]={stereo?buffers[2].data():nullptr};T* counter[]={stereo?buffers[3].data():nullptr};
        AudioBusBuffers outs[3]{};outs[0].numChannels=stereo?2:1;outs[1].numChannels=outs[2].numChannels=1;
        if constexpr(std::is_same_v<T,float>){outs[0].channelBuffers32=main;outs[1].channelBuffers32=base;outs[2].channelBuffers32=counter;}
        else{outs[0].channelBuffers64=main;outs[1].channelBuffers64=base;outs[2].channelBuffers64=counter;}
        ParameterChanges params(11);EventList events(16);
        ProcessData d{};d.processMode=kRealtime;d.symbolicSampleSize=fmt;d.numOutputs=3;d.outputs=outs;d.inputEvents=&events;d.inputParameterChanges=&params;
        const auto scoreEvents=borrowed::events(rate);size_t next=0;unsigned points=0,notes=0;
        double err=0;
        for(int pos=0;pos<total;pos+=block){
            const int n=std::min(block,total-pos);d.numSamples=n;params.clearQueue();events.clear();
            while(next<scoreEvents.size()&&scoreEvents[next].at<pos+n){
                const auto v=scoreEvents[next++];check(v.at>=pos,"event offset");
                if(v.type==0){const auto patch=borrowed::params(borrowed::score[v.note],baseline);for(unsigned k=0;k<patch.size();++k){point(params,1200+k,v.at-pos,patch[k]);++points;}}
                else{note(events,v,pos);++notes;}
            }
            for(auto& v:buffers)std::fill_n(v.data(),n,T(9));
            for(auto& out:outs)out.silenceFlags=0;
            ok(proc->process(d),"process");
            std::array<uint64,3> flags{stereo?3u:1u,1u,1u};
            for(int j=0;j<n;++j){
                const auto f=ref[size_t(pos+j)];
                const Sample expected=stereo?Sample{f.left,f.right,f.base,f.counter}:Sample{(f.left+f.right)*.5,0,0,0};
                Sample actual{double(buffers[0][j]),0,0,0};
                if(stereo){actual[1]=double(buffers[1][j]);actual[2]=double(buffers[2][j]);actual[3]=double(buffers[3][j]);}
                for(unsigned k=0;k<4;++k){check(std::isfinite(actual[k])&&std::abs(actual[k])<=.52,"finite/bound");err=std::max(err,std::abs(actual[k]-double(T(expected[k]))));}
                if(actual[0]!=0)flags[0]&=~uint64(1);
                if(actual[1]!=0)flags[0]&=~uint64(2);
                if(actual[2]!=0)flags[1]=0;
                if(actual[3]!=0)flags[2]=0;
                if(pos+j>=total-rate/20)check(actual==Sample{},"tail silence");
                result[size_t(pos+j)]=actual;
            }
            for(unsigned i=0;i<3;++i)check(outs[i].silenceFlags==flags[i],"silence flags");
        }
        check(points==66&&notes==12&&next==scoreEvents.size(),"complete score admission");
        // SDK note velocities are float, native reference uses double; allow only sub-PCM error.
        check(err<2e-7,"native reference disagreement");
        MemoryStream state;ok(c->getState(&state),"get state");
        const auto expectedState=guest::control::encode(borrowed::params(borrowed::score.back(),baseline));
        check(state.getSize()==TSize(expectedState.size())&&std::memcmp(state.getData(),expectedState.data(),expectedState.size())==0,"GO03 last patch");
        life.finish();return result;
    }
    throw std::runtime_error("no audio factory");
}
template<class T> void matrix(const VST3::Hosting::Module::Ptr& module,HostApplication* host,int rate,unsigned& cases){
    for(bool stereo:{false,true})for(bool baseline:{false,true}){
        const auto ref=borrowed::render(rate,257,baseline);
        auto a=replay<T>(module,host,rate,257,stereo,baseline,ref);
        auto b=replay<T>(module,host,rate,1024,stereo,baseline,ref);
        borrowed::check(a==b,"partition comparison");
        std::cout<<"BORROWED_SDK_CASE rate="<<rate<<" bits="<<sizeof(T)*8<<" stereo="<<stereo<<" baseline="<<baseline<<" frames="<<a.size()<<std::endl;
        ++cases;
    }
}
}
int main(int argc,char** argv){
    try{
        borrowed::check(argc==2,"usage: guest_borrowed_sdk <bundle>");
        std::string error;auto module=VST3::Hosting::Module::create(argv[1],error);if(!module)throw std::runtime_error(error);
        auto host=owned(new HostApplication);unsigned cases=0;
        for(int rate:{44100,48000,96000}){matrix<float>(module,host.get(),rate,cases);matrix<double>(module,host.get(),rate,cases);}
        borrowed::check(cases==24,"case count");
        std::cout<<"BORROWED_SDK_PASS cases=24 renders=48"<<std::endl;return 0;
    }catch(const std::exception& e){std::cerr<<"BORROWED_SDK_FAIL "<<e.what()<<std::endl;return 1;}
}
