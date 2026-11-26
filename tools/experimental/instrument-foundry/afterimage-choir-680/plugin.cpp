#include "live.hpp"
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
const FUID processorID(0xBD0B8CB3,0xB82E43EB,0x9613F0C9,0xA37FBA83);
const FUID controllerID(0xB9A28D3E,0x533D43A5,0xB7203754,0x3F6420E1);
using mhac::afterimage::live::Live;
constexpr auto firstID=mhac::afterimage::live::FirstID;
constexpr auto count=mhac::afterimage::live::Count;
using namespace mhac::afterimage::live;
bool readParams(IBStream* s,Word& w){State bytes{};int32 n=0;return s&&s->read(bytes.data(),8,&n)==kResultOk&&n==8&&decode(bytes.data(),8,w);}
struct Cursor {
    IParamValueQueue* q=nullptr;int32 index=0,size=0,offset=0;ParamValue value=0;bool pending=false;
    void next(){pending=false;while(index<size){if(q->getPoint(index++,offset,value)==kResultTrue){pending=true;break;}}}
    void init(IParamValueQueue* queue){q=queue;size=q->getPointCount();next();}
    void apply(Live& e,unsigned id,int32 sample,bool flush=false){while(pending&&(flush||offset<=sample)){if(offset>=0)e.parameter(id,value);next();}}
};
int key(int id,int channel,int pitch){return id>=0?id:-1-128*std::clamp(channel,0,15)-std::clamp(pitch,0,127);}
struct Events {
    IEventList* list;int32 index=0,size=0;Event event{};bool pending=false;
    explicit Events(IEventList* l):list(l),size(l?l->getEventCount():0){next();}
    void next(){pending=false;while(index<size){if(list->getEvent(index++,event)==kResultOk){pending=true;break;}}}
    void apply(Live& e,int32 sample){while(pending&&event.sampleOffset<=sample){
        if(event.sampleOffset>=0&&event.busIndex==0){
            if(event.type==Event::kNoteOnEvent){const auto& n=event.noteOn;e.on(key(n.noteId,n.channel,n.pitch),n.pitch,n.tuning,n.velocity);}
            else if(event.type==Event::kNoteOffEvent){const auto& n=event.noteOff;e.off(key(n.noteId,n.channel,n.pitch));}
        }next();
    }}
};
class Processor final: public AudioEffect {
    Live engine;mhac::afterimage::live::Bridge state;double sr=48000.;using Cursors=std::array<Cursor,count>;
    template<class T> tresult audio(ProcessData& d,Cursors& c,Events& ev){
        std::array<T*,2> ptr{};unsigned channels=0;uint64 silence=0;
        if(d.numOutputs==1){auto& bus=d.outputs[0];auto* info=getAudioOutput(0);
            if(!info||bus.numChannels<1||bus.numChannels>2||bus.numChannels!=SpeakerArr::getChannelCount(info->getArrangement()))return kResultFalse;
            channels=unsigned(bus.numChannels);silence=(uint64(1)<<channels)-1;
            T** p=nullptr;if constexpr(std::is_same_v<T,Sample32>)p=bus.channelBuffers32;else p=bus.channelBuffers64;
            for(unsigned j=0;j<channels;++j){if(info->isActive()&&(!p||!p[j]))return kResultFalse;if(p)ptr[j]=p[j];}
            if(!info->isActive()){for(auto* ch:ptr)if(ch)std::fill_n(ch,d.numSamples,T(0));ptr={};}
        }
        for(int32 i=0;i<d.numSamples;++i){for(unsigned k=0;k<count;++k)c[k].apply(engine,k,i);ev.apply(engine,i);const T y=T(engine.tick());
            for(unsigned j=0;j<channels;++j)if(ptr[j]){ptr[j][i]=y;if(y!=T(0))silence&=~(uint64(1)<<j);}}
        if(d.numOutputs==1)d.outputs[0].silenceFlags=silence;
        return kResultOk;
    }
public:
    Processor(){setControllerClass(controllerID);}
    static FUnknown* create(void*){return static_cast<IAudioProcessor*>(new Processor);}
    tresult PLUGIN_API initialize(FUnknown* ctx) override {const auto r=AudioEffect::initialize(ctx);if(r!=kResultOk)return r;addAudioOutput(STR16("Output"),SpeakerArr::kStereo);addEventInput(STR16("Notes"),16);return kResultOk;}
    tresult PLUGIN_API setBusArrangements(SpeakerArrangement* in,int32 ni,SpeakerArrangement* out,int32 no) override {if(ni!=0||no!=1||!out||(out[0]!=SpeakerArr::kMono&&out[0]!=SpeakerArr::kStereo))return kResultFalse;return AudioEffect::setBusArrangements(in,ni,out,no);}
    tresult PLUGIN_API canProcessSampleSize(int32 n) override{return n==kSample32||n==kSample64?kResultTrue:kResultFalse;}
    tresult PLUGIN_API setupProcessing(ProcessSetup& setup) override {if(!mhac::afterimage::supportsRate(setup.sampleRate))return kResultFalse;const auto r=AudioEffect::setupProcessing(setup);if(r==kResultOk){sr=setup.sampleRate;engine.prepare(sr);}return r;}
    tresult PLUGIN_API setActive(TBool active) override {const auto r=AudioEffect::setActive(active);if(r==kResultOk)engine.reset();return r;}
    tresult PLUGIN_API setProcessing(TBool active) override {if(!active)engine.reset();return kResultOk;}
    uint32 PLUGIN_API getLatencySamples() override{return 0;}
    uint32 PLUGIN_API getTailSamples() override{return uint32(std::ceil(sr*.032));}
    tresult PLUGIN_API setState(IBStream* s) override {Word p{};return readParams(s,p)&&state.request(p)?kResultOk:kResultFalse;}
    tresult PLUGIN_API getState(IBStream* s) override {if(!s)return kResultFalse;Word p{};p=state.save();auto bytes=mhac::afterimage::live::encode(p);int32 n=0;return s->write(bytes.data(),int32(bytes.size()),&n)==kResultOk&&n==int32(bytes.size())?kResultOk:kResultFalse;}
    tresult PLUGIN_API process(ProcessData& d) override {
        if(d.numSamples<0||d.numInputs!=0||d.numOutputs<0||d.numOutputs>1)return kResultFalse;
        if(d.numOutputs&&!d.outputs)return kResultFalse;
        state.begin(engine);
        struct Publish {mhac::afterimage::live::Bridge& s;Live& e;~Publish(){s.end(e);}} publish{state,engine};
        Cursors c{};if(d.inputParameterChanges)for(int32 i=0;i<d.inputParameterChanges->getParameterCount();++i){auto* q=d.inputParameterChanges->getParameterData(i);if(q){auto id=q->getParameterId();if(id>=firstID&&id<firstID+count&&!c[id-firstID].q)c[id-firstID].init(q);}}
        if(d.numSamples==0){for(unsigned k=0;k<count;++k)c[k].apply(engine,k,0,true);return kResultOk;}
        Events ev(d.inputEvents);if(d.symbolicSampleSize==kSample32)return audio<Sample32>(d,c,ev);if(d.symbolicSampleSize==kSample64)return audio<Sample64>(d,c,ev);return kResultFalse;
    }
};
class Controller final: public EditController {
public:
    static FUnknown* create(void*){return static_cast<IEditController*>(new Controller);}
    tresult PLUGIN_API initialize(FUnknown* ctx) override {const auto r=EditController::initialize(ctx);if(r!=kResultOk)return r;
        parameters.addParameter(STR16("Collapse pair (lexicographic rank)"),nullptr,27,normalized(Default,0),ParameterInfo::kCanAutomate,firstID);
        parameters.addParameter(STR16("Receipt (absent/fixed/preview/full)"),nullptr,3,normalized(Default,1),ParameterInfo::kCanAutomate,firstID+1);
        parameters.addParameter(STR16("Minimum duration (0..2000 ms)"),nullptr,2000,normalized(Default,2),ParameterInfo::kCanAutomate,firstID+2);
        parameters.addParameter(STR16("Memory influence"),nullptr,1000,normalized(Default,3),ParameterInfo::kCanAutomate,firstID+3);
        parameters.addParameter(STR16("Cancel releases (gate)"),nullptr,1,0,ParameterInfo::kCanAutomate,firstID+4);
        parameters.addParameter(STR16("Memory depth (latest/dual/archive)"),nullptr,2,normalized(Default,5),ParameterInfo::kCanAutomate,firstID+5);
        parameters.addParameter(STR16("Phase memory mix (0/33/67/100%)"),nullptr,3,normalized(Default,6),ParameterInfo::kCanAutomate,firstID+6);return kResultOk;
    }
    tresult PLUGIN_API setComponentState(IBStream* s) override {Word w{};if(!readParams(s,w))return kResultFalse;for(unsigned i=0;i<4;++i)setParamNormalized(firstID+i,normalized(w,i));setParamNormalized(firstID+4,0);setParamNormalized(firstID+5,normalized(w,5));setParamNormalized(firstID+6,normalized(w,6));return kResultOk;}
};
}
BEGIN_FACTORY_DEF("MHAC","https://github.com/techrote/MachineHumanAudioCybersemiotics","")
DEF_CLASS2(INLINE_UID_FROM_FUID(processorID),PClassInfo::kManyInstances,kVstAudioEffectClass,"MHAC Afterimage Choir",Vst::kDistributable,"Instrument|Synth","0.3.0",kVstVersionString,Processor::create)
DEF_CLASS2(INLINE_UID_FROM_FUID(controllerID),PClassInfo::kManyInstances,kVstComponentControllerClass,"MHAC Afterimage Choir Controller",0,"","0.3.0",kVstVersionString,Controller::create)
END_FACTORY
