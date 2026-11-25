#include "engine.hpp"
#include "public.sdk/source/vst/vstaudioeffect.h"
#include "public.sdk/source/vst/vsteditcontroller.h"
#include "public.sdk/source/vst/vstparameters.h"
#include "public.sdk/source/main/pluginfactory.h"
#include "pluginterfaces/base/ibstream.h"
#include "pluginterfaces/vst/ivstevents.h"
#include "pluginterfaces/vst/ivstparameterchanges.h"
using namespace Steinberg;
using namespace Steinberg::Vst;
namespace g=mhac::organ;
namespace {
const FUID processorID(0x54C90E31,0xCA6745FA,0x8EBB91F1,0x12FAD637);
const FUID controllerID(0xD047B8C2,0x5EE84FD9,0xAD8939C6,0xB70FE102);
constexpr ParamID firstID=400;
bool readParams(IBStream* s,g::Params& p){g::State bytes{};int32 n=0;return s&&s->read(bytes.data(),int32(bytes.size()),&n)==kResultOk&&n==int32(bytes.size())&&g::decode(bytes,p);}
struct Cursor {
    IParamValueQueue* queue=nullptr;int32 index=0,count=0,offset=0;ParamValue value=0;bool pending=false;
    void next(){pending=false;while(index<count){if(queue->getPoint(index++,offset,value)==kResultTrue){pending=true;break;}}}
    void init(IParamValueQueue* q){queue=q;count=q->getPointCount();next();}
    void apply(g::Engine& e,unsigned id,int32 sample,bool flush=false){while(pending&&(flush||offset<=sample)){e.set(id,value);next();}}
};
struct Events {
    IEventList* list=nullptr;int32 index=0,count=0;Event event{};bool pending=false;
    explicit Events(IEventList* l):list(l),count(l?l->getEventCount():0){next();}
    void next(){pending=false;while(index<count){if(list->getEvent(index++,event)==kResultOk){pending=true;break;}}}
    void apply(g::Engine& e,int32 sample){
        while(pending&&event.sampleOffset<=sample){
            if(event.busIndex==0){
                if(event.type==Event::kNoteOnEvent){const auto& n=event.noteOn;if(n.velocity>0)e.noteOn(n.channel,n.pitch,n.noteId,n.velocity,n.tuning);else e.noteOff(n.channel,n.pitch,n.noteId);}
                if(event.type==Event::kNoteOffEvent){const auto& n=event.noteOff;e.noteOff(n.channel,n.pitch,n.noteId);}
            }
            next();
        }
    }
};
class Processor final: public AudioEffect {
    g::Engine engine;double sr=48000.;
    using Cursors=std::array<Cursor,g::Count>;
    template<class T> tresult audio(ProcessData& d,T** out,Cursors& c,Events& ev){
        const int32 channels=d.outputs[0].numChannels;
        if(!out||channels<1||channels>2)return kResultFalse;
        for(int32 ch=0;ch<channels;++ch)if(!out[ch])return kResultFalse;
        bool silent=true;
        for(int32 i=0;i<d.numSamples;++i){
            for(unsigned k=0;k<g::Count;++k)c[k].apply(engine,k,i);
            ev.apply(engine,i);
            const T y=static_cast<T>(engine.next());silent&=y==T(0);
            for(int32 ch=0;ch<channels;++ch)out[ch][i]=y;
        }
        d.outputs[0].silenceFlags=silent?((uint64(1)<<channels)-1):0;
        return kResultOk;
    }
public:
    Processor(){setControllerClass(controllerID);}
    static FUnknown* create(void*){return static_cast<IAudioProcessor*>(new Processor);}
    tresult PLUGIN_API initialize(FUnknown* ctx) override {
        const auto r=AudioEffect::initialize(ctx);if(r!=kResultOk)return r;
        addAudioOutput(STR16("Output"),SpeakerArr::kStereo);addEventInput(STR16("Notes"),16);return kResultOk;
    }
    tresult PLUGIN_API setBusArrangements(SpeakerArrangement* in,int32 ni,SpeakerArrangement* out,int32 no) override {
        if(ni!=0||no!=1||!out||(out[0]!=SpeakerArr::kMono&&out[0]!=SpeakerArr::kStereo))return kResultFalse;
        return AudioEffect::setBusArrangements(in,ni,out,no);
    }
    tresult PLUGIN_API canProcessSampleSize(int32 size) override{return size==kSample32||size==kSample64?kResultTrue:kResultFalse;}
    tresult PLUGIN_API setupProcessing(ProcessSetup& setup) override {
        if(!g::validRate(setup.sampleRate))return kResultFalse;
        const auto r=AudioEffect::setupProcessing(setup);if(r==kResultOk){sr=setup.sampleRate;engine.reset(sr);}return r;
    }
    tresult PLUGIN_API setActive(TBool active) override {const auto r=AudioEffect::setActive(active);if(r==kResultOk)engine.reset(sr);return r;}
    tresult PLUGIN_API setProcessing(TBool active) override {if(!active)engine.reset(sr);return kResultOk;}
    uint32 PLUGIN_API getLatencySamples() override{return 0;}
    uint32 PLUGIN_API getTailSamples() override{return uint32(std::ceil(sr*.021));}
    tresult PLUGIN_API setState(IBStream* s) override {g::Params p{};if(!readParams(s,p))return kResultFalse;engine.restore(p);return kResultOk;}
    tresult PLUGIN_API getState(IBStream* s) override {if(!s)return kResultFalse;auto bytes=g::encode(engine.params());int32 n=0;return s->write(bytes.data(),int32(bytes.size()),&n)==kResultOk&&n==int32(bytes.size())?kResultOk:kResultFalse;}
    tresult PLUGIN_API process(ProcessData& d) override {
        if(d.numSamples<0||d.numInputs!=0||d.numOutputs<0||d.numOutputs>1)return kResultFalse;
        Cursors c{};
        if(d.inputParameterChanges)for(int32 i=0;i<d.inputParameterChanges->getParameterCount();++i){
            auto* q=d.inputParameterChanges->getParameterData(i);if(!q)continue;
            auto id=q->getParameterId();if(id>=firstID&&id<firstID+g::Count&&!c[id-firstID].queue)c[id-firstID].init(q);
        }
        if(d.numSamples==0){for(unsigned k=0;k<g::Count;++k)c[k].apply(engine,k,0,true);return kResultOk;}
        Events ev(d.inputEvents);
        if(d.numOutputs==0){for(int32 i=0;i<d.numSamples;++i){for(unsigned k=0;k<g::Count;++k)c[k].apply(engine,k,i);ev.apply(engine,i);engine.next();}return kResultOk;}
        if(!d.outputs)return kResultFalse;
        if(d.symbolicSampleSize==kSample32)return audio(d,d.outputs[0].channelBuffers32,c,ev);
        if(d.symbolicSampleSize==kSample64)return audio(d,d.outputs[0].channelBuffers64,c,ev);
        return kResultFalse;
    }
};
class Controller final: public EditController {
public:
    static FUnknown* create(void*){return static_cast<IEditController*>(new Controller);}
    tresult PLUGIN_API initialize(FUnknown* ctx) override {
        const auto r=EditController::initialize(ctx);if(r!=kResultOk)return r;
        auto add=[&](const TChar* n,unsigned i,int32 steps=0){parameters.addParameter(n,nullptr,steps,g::defaults[i],ParameterInfo::kCanAutomate,firstID+i);};
        add(STR16("Path (Manual/Major/Nested)"),g::Mode,2);add(STR16("Manual dial (0-16)"),g::Dial,16);
        add(STR16("Relay bank blend A/B"),g::Blend);add(STR16("Step interval (25-200 ms)"),g::Rate);add(STR16("Gain"),g::Gain);return kResultOk;
    }
    tresult PLUGIN_API setComponentState(IBStream* s) override {g::Params p{};if(!readParams(s,p))return kResultFalse;for(unsigned i=0;i<g::Count;++i)setParamNormalized(firstID+i,p[i]);return kResultOk;}
};
}
BEGIN_FACTORY_DEF("MHAC","https://github.com/techrote/MachineHumanAudioCybersemiotics","")
DEF_CLASS2(INLINE_UID_FROM_FUID(processorID),PClassInfo::kManyInstances,kVstAudioEffectClass,
"MHAC Retreat Organ",Vst::kDistributable,"Instrument|Synth","0.1.0",kVstVersionString,Processor::create)
DEF_CLASS2(INLINE_UID_FROM_FUID(controllerID),PClassInfo::kManyInstances,kVstComponentControllerClass,
"MHAC Retreat Organ Controller",0,"","0.1.0",kVstVersionString,Controller::create)
END_FACTORY
