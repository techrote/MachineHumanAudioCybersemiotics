#include "host.hpp"
#include <type_traits>
#include "public.sdk/source/vst/vstaudioeffect.h"
#include "public.sdk/source/vst/vsteditcontroller.h"
#include "public.sdk/source/vst/vstparameters.h"
#include "public.sdk/source/main/pluginfactory.h"
#include "pluginterfaces/base/ibstream.h"
#include "pluginterfaces/vst/ivstevents.h"
#include "pluginterfaces/vst/ivstparameterchanges.h"
using namespace Steinberg;
using namespace Steinberg::Vst;
namespace {
using namespace mhac::orbit;
using namespace mhac::orbit::host;
const FUID processorID(0x24C15B79,0x3B8C4F4B,0x98275F23,0x3EE969C4);
const FUID controllerID(0xA501C96D,0xF0EC48C8,0x8BA63D11,0xB860D74F);
bool readPatch(IBStream* s,Patch& p){Bytes b{};int32 n=0;if(!s||s->read(b.data(),int32(b.size()),&n)!=kResultOk||n!=int32(b.size()))return false;
    if(b[3]=='1')return decode(b,p);
    if(b[3]!='2')return false;
    StateBytes extended{};std::copy(b.begin(),b.end(),extended.begin());
    return s->read(extended.data()+10,1,&n)==kResultOk&&n==1&&decodeState(extended,p);}
struct Cursor {
    IParamValueQueue* q=nullptr;int32 index=0,size=0,offset=0;ParamValue value=0;bool pendingPoint=false;
    void next(){pendingPoint=false;while(index<size){if(q->getPoint(index++,offset,value)==kResultTrue){pendingPoint=true;break;}}}
    void init(IParamValueQueue* queue){q=queue;size=q->getPointCount();next();}
    void apply(Live& e,unsigned id,int32 sample){while(pendingPoint&&offset<=sample){if(offset>=0)e.parameter(id,value);next();}}
};
struct Events {
    IEventList* list;int32 index=0,size=0;Steinberg::Vst::Event event{};bool pendingEvent=false;
    explicit Events(IEventList* l):list(l),size(l?l->getEventCount():0){next();}
    void next(){pendingEvent=false;while(index<size){if(list->getEvent(index++,event)==kResultOk){pendingEvent=true;break;}}}
    void apply(Live& e,int32 sample){while(pendingEvent&&event.sampleOffset<=sample){
        if(event.sampleOffset>=0&&event.busIndex==0){
            if(event.type==Steinberg::Vst::Event::kNoteOnEvent){const auto& n=event.noteOn;e.on(n.noteId,n.channel,n.pitch,n.tuning,n.velocity);}
            else if(event.type==Steinberg::Vst::Event::kNoteOffEvent){const auto& n=event.noteOff;e.off(n.noteId,n.channel,n.pitch);}
        }next();
    }}
};
class Processor final: public AudioEffect {
    Live engine;Bridge state;double sr=48000.;using Cursors=std::array<Cursor,count>;
    template<class T> tresult audio(ProcessData& d,Cursors& c,Events& ev){
        std::array<T*,2> ptr{};unsigned channels=0;uint64 silence=0;
        if(d.numOutputs==1){auto& bus=d.outputs[0];auto* info=getAudioOutput(0);
            if(!info||bus.numChannels<1||bus.numChannels>2||bus.numChannels!=SpeakerArr::getChannelCount(info->getArrangement()))return kResultFalse;
            channels=unsigned(bus.numChannels);silence=(uint64(1)<<channels)-1;
            T** p=nullptr;if constexpr(std::is_same_v<T,Sample32>)p=bus.channelBuffers32;else p=bus.channelBuffers64;
            for(unsigned j=0;j<channels;++j){if(info->isActive()&&(!p||!p[j]))return kResultFalse;if(p)ptr[j]=p[j];}
            if(!info->isActive()){for(auto* ch:ptr)if(ch)std::fill_n(ch,d.numSamples,T(0));ptr={};}
        }
        for(int32 i=0;i<d.numSamples;++i){for(unsigned k=0;k<count;++k)c[k].apply(engine,k,i);ev.apply(engine,i);
            double l=0,r=0;engine.tick(l,r);const std::array<T,2> y{T(channels==1?(l+r)*.5:l),T(r)};
            for(unsigned j=0;j<channels;++j)if(ptr[j]){ptr[j][i]=y[j];if(y[j]!=T(0))silence&=~(uint64(1)<<j);}}
        if(d.numOutputs==1)d.outputs[0].silenceFlags=silence;
        return kResultOk;
    }
public:
    Processor(){setControllerClass(controllerID);}
    static FUnknown* create(void*){return static_cast<IAudioProcessor*>(new Processor);}
    tresult PLUGIN_API initialize(FUnknown* ctx) override {const auto r=AudioEffect::initialize(ctx);if(r!=kResultOk)return r;addAudioOutput(STR16("Output"),SpeakerArr::kStereo);addEventInput(STR16("Notes"),16);return kResultOk;}
    tresult PLUGIN_API setBusArrangements(SpeakerArrangement* in,int32 ni,SpeakerArrangement* out,int32 no) override {if(ni!=0||no!=1||!out||(out[0]!=SpeakerArr::kMono&&out[0]!=SpeakerArr::kStereo))return kResultFalse;return AudioEffect::setBusArrangements(in,ni,out,no);}
    tresult PLUGIN_API canProcessSampleSize(int32 n) override{return n==kSample32||n==kSample64?kResultTrue:kResultFalse;}
    tresult PLUGIN_API setupProcessing(ProcessSetup& setup) override {if(!validSampleRate(setup.sampleRate))return kResultFalse;const auto r=AudioEffect::setupProcessing(setup);if(r==kResultOk){sr=setup.sampleRate;if(!engine.prepare(sr))return kResultFalse;}return r;}
    tresult PLUGIN_API setActive(TBool active) override {const auto r=AudioEffect::setActive(active);if(r==kResultOk)engine.reset();return r;}
    tresult PLUGIN_API setProcessing(TBool active) override {if(!active)engine.reset();return kResultOk;}
    uint32 PLUGIN_API getLatencySamples() override{return 0;}
    uint32 PLUGIN_API getTailSamples() override{return uint32(std::ceil(sr));}
    tresult PLUGIN_API setState(IBStream* s) override {Patch p{};return readPatch(s,p)&&state.request(p)?kResultOk:kResultFalse;}
    tresult PLUGIN_API getState(IBStream* s) override {if(!s)return kResultFalse;const auto p=state.save();auto bytes=encodeState(p);int32 size=11,n=0;
        if(p.releaseMode==0){bytes[3]='1';size=10;}
        return s->write(bytes.data(),size,&n)==kResultOk&&n==size?kResultOk:kResultFalse;}
    tresult PLUGIN_API process(ProcessData& d) override {
        if(d.numSamples<0||d.numInputs!=0||d.numOutputs<0||d.numOutputs>1||(d.numOutputs&&!d.outputs))return kResultFalse;
        if(d.inputEvents&&(d.inputEvents->getEventCount()<0||d.inputEvents->getEventCount()>4096))return kResultFalse;
        Cursors c{};if(d.inputParameterChanges){const auto n=d.inputParameterChanges->getParameterCount();if(n<0||n>4096)return kResultFalse;
            for(int32 i=0;i<n;++i){auto* q=d.inputParameterChanges->getParameterData(i);if(q){auto id=q->getParameterId();if(id>=firstID&&id<firstID+count&&!c[id-firstID].q){if(q->getPointCount()<0||q->getPointCount()>4096)return kResultFalse;c[id-firstID].init(q);}}}}
        const auto token=state.begin(engine);
        struct Publish {Bridge& s;Live& e;std::uint32_t token;~Publish(){s.end(token,e);}} publish{state,engine,token};
        if(d.numSamples==0){for(unsigned k=0;k<count;++k)c[k].apply(engine,k,0);return kResultOk;}
        Events ev(d.inputEvents);if(d.symbolicSampleSize==kSample32)return audio<Sample32>(d,c,ev);if(d.symbolicSampleSize==kSample64)return audio<Sample64>(d,c,ev);return kResultFalse;
    }
};
class Controller final: public EditController {
public:
    static FUnknown* create(void*){return static_cast<IEditController*>(new Controller);}
    tresult PLUGIN_API initialize(FUnknown* ctx) override {const auto r=EditController::initialize(ctx);if(r!=kResultOk)return r;
        parameters.addParameter(STR16("Orbit blend"),nullptr,1000,normalized(Patch{},0),ParameterInfo::kCanAutomate,firstID);
        parameters.addParameter(STR16("Release (10..1000 ms)"),nullptr,990,normalized(Patch{},1),ParameterInfo::kCanAutomate,firstID+1);
        parameters.addParameter(STR16("Tuning (-100..100 cents)"),nullptr,200,normalized(Patch{},2),ParameterInfo::kCanAutomate,firstID+2);
        parameters.addParameter(STR16("Release mode (0 Linear, 1 Fixed, 2 Phase)"),nullptr,2,0.,ParameterInfo::kCanAutomate,firstID+3);return kResultOk;}
    tresult PLUGIN_API setComponentState(IBStream* s) override {Patch p{};if(!readPatch(s,p))return kResultFalse;for(unsigned i=0;i<count;++i)setParamNormalized(firstID+i,normalized(p,i));return kResultOk;}
};
}
BEGIN_FACTORY_DEF("MHAC","https://github.com/techrote/MachineHumanAudioCybersemiotics","")
DEF_CLASS2(INLINE_UID_FROM_FUID(processorID),PClassInfo::kManyInstances,kVstAudioEffectClass,"MHAC Orbit Lantern",Vst::kDistributable,"Instrument|Synth","0.2.0",kVstVersionString,Processor::create)
DEF_CLASS2(INLINE_UID_FROM_FUID(controllerID),PClassInfo::kManyInstances,kVstComponentControllerClass,"MHAC Orbit Lantern Controller",0,"","0.2.0",kVstVersionString,Controller::create)
END_FACTORY
