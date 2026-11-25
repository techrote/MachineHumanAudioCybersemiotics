#include "core.hpp"
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
const FUID processorID(0x7F9C7A06,0x438E429D,0x8110F294,0xA64B4D5A);
const FUID controllerID(0xB53EF43B,0xB92C45AF,0xA797271E,0x39D339C4);
constexpr ParamID firstID=800;
bool readParams(IBStream* s,offcut::Params& p){
    offcut::State bytes{};int32 n=0;
    return s&&s->read(bytes.data(),int32(bytes.size()),&n)==kResultOk&&n==int32(bytes.size())&&offcut::decode(bytes,p);
}
struct Cursor {
    IParamValueQueue* queue=nullptr;int32 index=0,count=0,offset=0;ParamValue value=0;bool pending=false;
    void next(){pending=false;while(index<count){if(queue->getPoint(index++,offset,value)==kResultTrue){pending=true;break;}}}
    void init(IParamValueQueue* q){queue=q;count=q->getPointCount();next();}
    void apply(offcut::Params& p,unsigned id,int32 sample,bool flush=false){while(pending&&(flush||offset<=sample)){offcut::set(p,id,value);next();}}
};
int key(int id,int channel,int pitch){return id>=0?id:-1-128*std::clamp(channel,0,15)-std::clamp(pitch,0,127);}
struct Events {
    IEventList* list=nullptr;int32 index=0,count=0;Event event{};bool pending=false;
    explicit Events(IEventList* l):list(l),count(l?l->getEventCount():0){next();}
    void next(){pending=false;while(index<count){if(list->getEvent(index++,event)==kResultOk){pending=true;break;}}}
    void apply(offcut::Engine& e,const offcut::Params& p,int32 sample){
        while(pending&&event.sampleOffset<=sample){
            if(event.busIndex==0){
                if(event.type==Event::kNoteOnEvent){const auto& n=event.noteOn;const int k=key(n.noteId,n.channel,n.pitch);if(n.velocity>0)e.on(k,n.pitch,n.tuning,n.velocity,p);else e.off(k);}
                if(event.type==Event::kNoteOffEvent){const auto& n=event.noteOff;e.off(key(n.noteId,n.channel,n.pitch));}
            }
            next();
        }
    }
};
class Processor final: public AudioEffect {
    offcut::Engine engine;offcut::Params params=offcut::defaults;double sr=48000.;
    using Cursors=std::array<Cursor,offcut::Count>;
    offcut::Pair step(Cursors& c,Events& ev,int32 i){for(unsigned k=0;k<offcut::Count;++k)c[k].apply(params,k,i);ev.apply(engine,params,i);return engine.tick();}
    template<class T> tresult audio(ProcessData& d,T** out,Cursors& c,Events& ev){
        const int32 channels=d.outputs[0].numChannels;
        if(!out||channels<1||channels>2)return kResultFalse;
        for(int32 ch=0;ch<channels;++ch)if(!out[ch])return kResultFalse;
        uint64 silence=(uint64(1)<<channels)-1;
        for(int32 i=0;i<d.numSamples;++i){
            const auto p=step(c,ev,i);
            if(channels==1){out[0][i]=T((p.l+p.r)*.5);if(out[0][i]!=T(0))silence&=~uint64(1);}
            else {out[0][i]=T(p.l);out[1][i]=T(p.r);if(out[0][i]!=T(0))silence&=~uint64(1);if(out[1][i]!=T(0))silence&=~uint64(2);}
        }
        d.outputs[0].silenceFlags=silence;
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
        if(!offcut::supported(setup.sampleRate))return kResultFalse;
        const auto r=AudioEffect::setupProcessing(setup);if(r==kResultOk){sr=setup.sampleRate;engine.prepare(sr);}return r;
    }
    tresult PLUGIN_API setActive(TBool active) override {const auto r=AudioEffect::setActive(active);if(r==kResultOk)engine.reset();return r;}
    tresult PLUGIN_API setProcessing(TBool active) override {if(!active)engine.reset();return kResultOk;}
    uint32 PLUGIN_API getLatencySamples() override{return 0;}
    uint32 PLUGIN_API getTailSamples() override{return uint32(std::ceil(sr*.041));}
    tresult PLUGIN_API setState(IBStream* s) override {offcut::Params p{};if(!readParams(s,p))return kResultFalse;params=p;return kResultOk;}
    tresult PLUGIN_API getState(IBStream* s) override {if(!s)return kResultFalse;auto bytes=offcut::encode(params);int32 n=0;return s->write(bytes.data(),int32(bytes.size()),&n)==kResultOk&&n==int32(bytes.size())?kResultOk:kResultFalse;}
    tresult PLUGIN_API process(ProcessData& d) override {
        if(d.numSamples<0||d.numInputs!=0||d.numOutputs<0||d.numOutputs>1)return kResultFalse;
        Cursors c{};
        if(d.inputParameterChanges)for(int32 i=0;i<d.inputParameterChanges->getParameterCount();++i){
            auto* q=d.inputParameterChanges->getParameterData(i);if(!q)continue;
            auto id=q->getParameterId();if(id>=firstID&&id<firstID+offcut::Count&&!c[id-firstID].queue)c[id-firstID].init(q);
        }
        if(d.numSamples==0){for(unsigned k=0;k<offcut::Count;++k)c[k].apply(params,k,0,true);return kResultOk;}
        Events ev(d.inputEvents);
        if(d.numOutputs==0){for(int32 i=0;i<d.numSamples;++i)step(c,ev,i);return kResultOk;}
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
        auto add=[&](const TChar* n,unsigned i,int32 steps=0){parameters.addParameter(n,nullptr,steps,offcut::defaults[i],ParameterInfo::kCanAutomate,firstID+i);};
        add(STR16("Threshold (20-80%)"),0);add(STR16("Residual amount"),1);add(STR16("Colour ratio (1-8)"),2,7);add(STR16("Routing (Split/Reconstruct)"),3,1);
        return kResultOk;
    }
    tresult PLUGIN_API setComponentState(IBStream* s) override {offcut::Params p{};if(!readParams(s,p))return kResultFalse;for(unsigned i=0;i<offcut::Count;++i)setParamNormalized(firstID+i,p[i]);return kResultOk;}
};
}
BEGIN_FACTORY_DEF("MHAC","https://github.com/techrote/MachineHumanAudioCybersemiotics","")
DEF_CLASS2(INLINE_UID_FROM_FUID(processorID),PClassInfo::kManyInstances,kVstAudioEffectClass,
"MHAC Offcut Loom",Vst::kDistributable,"Instrument|Synth","0.1.0",kVstVersionString,Processor::create)
DEF_CLASS2(INLINE_UID_FROM_FUID(controllerID),PClassInfo::kManyInstances,kVstComponentControllerClass,
"MHAC Offcut Loom Controller",0,"","0.1.0",kVstVersionString,Controller::create)
END_FACTORY
