// Refs #632. Direct SDK host of the exact delivered 0.5/0.4/0.2 modules.
// Stages run serially with the previous stage's actual audio as input.
#include "public.sdk/source/vst/hosting/module.h"
#include "public.sdk/source/vst/hosting/hostclasses.h"
#include "public.sdk/source/vst/hosting/parameterchanges.h"
#include "public.sdk/source/vst/hosting/eventlist.h"
#include "public.sdk/source/common/memorystream.h"
#include "pluginterfaces/vst/ivstaudioprocessor.h"
#include "pluginterfaces/vst/ivstcomponent.h"
#include "pluginterfaces/vst/vstspeaker.h"
#include <algorithm>
#include <array>
#include <cmath>
#include <cstring>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
using namespace Steinberg;
using namespace Steinberg::Vst;
namespace {
void require(bool b,const char* stage){if(!b)throw std::runtime_error(stage);}
void ok(tresult r,const char* stage){if(r!=kResultOk)throw std::runtime_error(std::string(stage)+" code="+std::to_string(r));}
struct Frame {float l=0,r=0;};
using Audio=std::vector<Frame>;
using Bytes=std::vector<unsigned char>;
void word(Bytes& b,unsigned v){b.push_back(static_cast<unsigned char>(v&255));b.push_back(static_cast<unsigned char>(v>>8));}
Bytes orbitState(){Bytes b{'O','L','0','4'};for(unsigned v:{180u,650u,88u})word(b,v);b.push_back(2);for(unsigned v:{700u,900u,1400u})word(b,v);return b;}
Bytes bankState(unsigned budget,bool capture){Bytes b{'H','M','0','2'};word(b,1000);b.push_back(0);for(unsigned hz:{110u,165u,220u,330u}){for(unsigned v:{hz,800u,1000u,0u})word(b,v);b.push_back(capture?1:0);}b.push_back(static_cast<unsigned char>(budget));b.push_back(1);return b;}
Bytes shuttleState(){Bytes b{'P','S','0','2'};for(unsigned v:{650u,850u,200u,400u})word(b,v);b.push_back(0);word(b,1000);return b;}
void saved(IComponent* c,const Bytes& b){MemoryStream s;ok(c->getState(&s),"getState");require(s.getSize()==TSize(b.size())&&std::memcmp(s.getData(),b.data(),b.size())==0,"component state mismatch");}
void restore(IComponent* c,Bytes b){MemoryStream s(b.data(),TSize(b.size()));ok(c->setState(&s),"setState");saved(c,b);}
struct Life {
    IComponent* c; IAudioProcessor* p; bool initialized=false,active=false,running=false;
    ~Life(){if(running)p->setProcessing(false);if(active)c->setActive(false);if(initialized)c->terminate();}
    void finish(){ok(p->setProcessing(false),"stop");running=false;ok(c->setActive(false),"deactivate");active=false;ok(c->terminate(),"terminate");initialized=false;}
};
struct Mode {const char* name;bool pressure,key;unsigned budget;};
constexpr Mode modes[]={{"baseline",false,false,4},{"pressure",true,false,4},{"keyed",true,true,4},{"full",true,true,16}};
struct Note {int t,id,pitch,kind;float value;};
std::vector<Note> score(int rate,bool pressure){
    std::vector<Note> n;
    for(int k=0;k<4;++k)n.push_back({0,k,45+7*k,0,.8f});
    if(pressure){n.push_back({rate/4,0,45,2,1.f});n.push_back({rate/2,2,59,2,.8f});}
    for(int k=0;k<4;++k)n.push_back({rate*3/4,k,45+7*k,1,0.f});
    n.push_back({rate*3,4,69,0,.7f});
    if(pressure)n.push_back({rate*13/4,4,69,2,1.f});
    n.push_back({rate*7/2,4,69,1,0.f});return n;
}
bool pulse(int t,int rate){for(int a:{rate*3/2,rate*153/100,rate*2,rate*5/2})if(t>=a&&t<a+rate/100)return true;return false;}
void point(ParameterChanges& params,ParamID id,int offset,double value){int32 qi=0,pi=0;auto* q=params.addParameterData(id,qi);require(q!=nullptr,"parameter queue");ok(q->addPoint(offset,value,pi),"parameter point");}
void addNote(EventList& events,const Note& a,int pos){
    Event e{};e.busIndex=0;e.sampleOffset=a.t-pos;
    if(a.kind==2){e.type=Event::kPolyPressureEvent;e.polyPressure.channel=0;e.polyPressure.pitch=int16(a.pitch);e.polyPressure.noteId=a.id;e.polyPressure.pressure=a.value;}
    else if(a.kind==0){e.type=Event::kNoteOnEvent;e.noteOn.channel=0;e.noteOn.pitch=int16(a.pitch);e.noteOn.noteId=a.id;e.noteOn.velocity=a.value;}
    else{e.type=Event::kNoteOffEvent;e.noteOff.channel=0;e.noteOff.pitch=int16(a.pitch);e.noteOff.noteId=a.id;}
    ok(events.addEvent(e),"note event");
}
uint64 silence(float* const* p,int n){uint64 mask=0;for(int k=0;k<2;++k)if(std::all_of(p[k],p[k]+n,[](float x){return x==0.f;}))mask|=uint64(1)<<k;return mask;}
Audio stage(const char* path,HostApplication* host,int which,int rate,int block,Mode mode,bool manual,const Audio& upstream){
    const bool instrument=which==0,bank=which==1,key=bank&&mode.key&&!manual;
    const char* names[]={"MHAC Orbit Lantern","MHAC Harmonic Memory Bank","MHAC Palimpsest Shuttle"};
    const char* versions[]={"0.5.0","0.4.0","0.2.0"};
    std::string error;auto module=VST3::Hosting::Module::create(path,error);if(!module)throw std::runtime_error(error);
    const auto& factory=module->getFactory();factory.setHostContext(host);
    for(const auto& info:factory.classInfos()){
        if(info.category()!=kVstAudioEffectClass)continue;
        require(info.name()==names[which]&&info.version()==versions[which],"factory identity");
        auto c=factory.createInstance<IComponent>(info.ID());require(bool(c),"component");
        FUnknownPtr<IAudioProcessor> proc(c.get());require(proc.getInterface()!=nullptr,"audio processor");
        Life life{c.get(),proc.getInterface()};
        ok(c->initialize(host),"initialize");life.initialized=true;
        require(c->getBusCount(kAudio,kInput)==(instrument?0:bank?2:1)&&c->getBusCount(kAudio,kOutput)==1,"audio bus count");
        if(bank){BusInfo i{};ok(c->getBusInfo(kAudio,kInput,1,i),"key bus info");require(i.busType==kAux&&!(i.flags&BusInfo::kDefaultActive),"aux contract");}
        SpeakerArrangement arr[]={SpeakerArr::kStereo,SpeakerArr::kStereo};
        ok(proc->setBusArrangements(instrument?nullptr:arr,instrument?0:key?2:1,arr,1),"arrangement");
        if(bank)ok(c->activateBus(kAudio,kInput,1,key),"key activation");
        if(!instrument)ok(c->activateBus(kAudio,kInput,0,true),"main input activation");
        if(instrument){require(c->getBusCount(kEvent,kInput)==1,"event bus count");ok(c->activateBus(kEvent,kInput,0,true),"event bus activation");}
        ok(c->activateBus(kAudio,kOutput,0,true),"output activation");
        const Bytes initial=instrument?orbitState():bank?bankState(mode.budget,true):shuttleState();
        restore(c.get(),initial);
        require(proc->canProcessSampleSize(kSample32)==kResultTrue,"float32");
        ProcessSetup setup{kRealtime,kSample32,block,double(rate)};
        ok(proc->setupProcessing(setup),"setup");ok(c->setActive(true),"active");life.active=true;
        ok(proc->setProcessing(true),"start");life.running=true;saved(c.get(),initial);
        const int total=rate*5;
        require(instrument||upstream.size()==size_t(total),"upstream extent");
        Audio result(static_cast<size_t>(total));
        std::vector<float> l(block),r(block),kl(block),kr(block),ol(block),orr(block);
        float* input[]={l.data(),r.data()},*aux[]={kl.data(),kr.data()},*output[]={ol.data(),orr.data()};
        AudioBusBuffers in[2]{},out{};in[0].numChannels=2;in[0].channelBuffers32=input;in[1].numChannels=2;in[1].channelBuffers32=aux;out.numChannels=2;out.channelBuffers32=output;
        ParameterChanges params(45);EventList events(32);
        ProcessData d{};d.processMode=kRealtime;d.symbolicSampleSize=kSample32;d.numInputs=instrument?0:key?2:1;d.inputs=instrument?nullptr:in;d.numOutputs=1;d.outputs=&out;d.inputEvents=instrument?&events:nullptr;d.inputParameterChanges=&params;
        const auto notes=score(rate,mode.pressure);
        unsigned noteCount=0;
        for(int pos=0;pos<total;pos+=block){
            const int n=std::min(block,total-pos);d.numSamples=n;params.clearQueue();events.clear();
            if(instrument){for(const auto& note:notes)if(note.t>=pos&&note.t<pos+n){addNote(events,note,pos);++noteCount;}}
            if(bank){
                if(rate>=pos&&rate<pos+n)for(unsigned k=0;k<4;++k)point(params,2010+9*k+4,rate-pos,0.);
                if(manual&&mode.key)for(int a:{rate*3/2,rate*2,rate*5/2}){
                    if(a>=pos&&a<pos+n)point(params,2056,a-pos,1.);
                    if(a+1>=pos&&a+1<pos+n)point(params,2056,a+1-pos,0.);
                }
            }
            for(int j=0;j<n;++j){
                const int t=pos+j;
                if(!instrument){const auto x=upstream[size_t(t)];l[j]=bank?std::clamp(x.l*8.f,-.9f,.9f):x.l;r[j]=bank?std::clamp(x.r*8.f,-.9f,.9f):x.r;}
                kl[j]=0.f;kr[j]=key&&pulse(t,rate)?-.8f:0.f;ol[j]=orr[j]=9.f;
            }
            in[0].silenceFlags=silence(input,n);in[1].silenceFlags=silence(aux,n);out.silenceFlags=0;
            ok(proc->process(d),"audio process");
            for(int j=0;j<n;++j){
                require(std::isfinite(ol[j])&&std::isfinite(orr[j])&&std::abs(ol[j])<=1.f&&std::abs(orr[j])<=1.f,"output bounds");
                result[size_t(pos+j)]={ol[j],orr[j]};
            }
        }
        if(instrument)require(noteCount==notes.size(),"score event count");
        saved(c.get(),bank?bankState(mode.budget,false):initial);life.finish();return result;
    }
    throw std::runtime_error("no audio factory");
}
struct Result{Audio dry,bank,mix;};
Result render(char** paths,HostApplication* host,int rate,int block,Mode m,bool manual){
    Result x;x.dry=stage(paths[0],host,0,rate,block,m,manual,{});
    x.bank=stage(paths[1],host,1,rate,block,m,manual,x.dry);
    auto wet=stage(paths[2],host,2,rate,block,m,manual,x.bank);x.mix.resize(wet.size());
    for(size_t i=0;i<wet.size();++i)x.mix[i]={.4f*x.dry[i].l+.35f*wet[i].l,.4f*x.dry[i].r+.35f*wet[i].r};
    return x;
}
double diff(const Audio& a,const Audio& b){require(a.size()==b.size(),"comparison extent");double e=0;for(size_t i=0;i<a.size();++i)e=std::max({e,std::abs(double(a[i].l)-b[i].l),std::abs(double(a[i].r)-b[i].r)});return e;}
double compare(const Result& a,const Result& b){return std::max({diff(a.dry,b.dry),diff(a.bank,b.bank),diff(a.mix,b.mix)});}
double rms(const Audio& x,int start,int end){double v=0;for(int i=start;i<end;++i){auto a=x[size_t(i)];v+=double(a.l)*a.l+double(a.r)*a.r;}return std::sqrt(v/(2*(end-start)));}
void wav(const std::string& path,const Audio& x,int rate){
    std::ofstream f(path,std::ios::binary);require(bool(f),"wav open");
    auto put=[&](unsigned v,unsigned n){while(n--){f.put(char(v&255));v>>=8;}};
    const unsigned bytes=unsigned(x.size()*4);f.write("RIFF",4);put(36+bytes,4);f.write("WAVEfmt ",8);put(16,4);put(1,2);put(2,2);put(unsigned(rate),4);put(unsigned(rate)*4,4);put(4,2);put(16,2);f.write("data",4);put(bytes,4);
    for(size_t i=0;i<x.size();++i){double fade=std::min({1.,double(i)/(rate*.01),double(x.size()-1-i)/(rate*.05)});for(float v:{x[i].l,x[i].r})put(unsigned(int(std::lround(v*fade*32767))),2);}
    f.close();require(bool(f),"wav write");
}
}
int main(int argc,char** argv){
    try{
        require(argc==5,"usage: pressure_key_sdk <Orbit bundle> <Bank bundle> <Shuttle bundle> <output dir>");
        auto host=owned(new HostApplication);unsigned renders=0,cases=0,manualCases=0;
        for(int rate:{44100,48000,96000}){
            std::array<Result,4> results;
            for(unsigned i=0;i<4;++i){
                auto m=modes[i];auto a=render(argv+1,host.get(),rate,257,m,false);auto b=render(argv+1,host.get(),rate,1024,m,false);renders+=2;
                const double partition=compare(a,b);require(partition<1e-5,"partition comparison");
                double manualError=0;
                if(m.key){auto manual=render(argv+1,host.get(),rate,1024,m,true);++renders;++manualCases;manualError=compare(a,manual);require(manualError<1e-5,"automatic/manual comparison");}
                require(rms(a.dry,rate/4,rate*3/4)>1e-5&&rms(a.dry,rate*49/10,rate*5)==0.,"voice activity/release");
                if(m.budget==16)require(rms(a.bank,rate*11/4,rate*3)==0.,"full erasure tail");
                std::cout<<std::setprecision(17)<<"PRESSURE_KEY_SDK_CASE rate="<<rate<<" mode="<<m.name<<" partition_error="<<partition<<" manual_error="<<manualError<<" dry_rms="<<rms(a.dry,rate/4,rate*3/4)<<" bank_rms="<<rms(a.bank,rate*11/4,rate*3)<<std::endl;
                if(rate==48000)wav(std::string(argv[4])+"/"+m.name+".wav",a.mix,rate);
                results[i]=std::move(a);++cases;
            }
            require(diff(results[0].dry,results[1].dry)>1e-5,"pressure contrast");
            require(diff(results[1].dry,results[2].dry)<1e-6&&diff(results[2].dry,results[3].dry)<1e-6,"key changed dry instrument");
            require(rms(results[1].bank,rate*11/4,rate*3)>1e-5&&diff(results[1].bank,results[2].bank)>1e-5,"key contrast");
        }
        require(cases==12&&renders==30&&manualCases==6,"case matrix");
        std::cout<<"PRESSURE_KEY_SDK_PASS cases=12 renders=30 manual=6"<<std::endl;return 0;
    }catch(const std::exception& e){std::cerr<<"PRESSURE_KEY_SDK_FAIL "<<e.what()<<std::endl;return 1;}
}
