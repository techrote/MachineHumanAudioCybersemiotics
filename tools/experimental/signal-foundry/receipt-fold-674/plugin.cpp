#include "balanced_host.hpp"
#include "public.sdk/source/vst/vstaudioeffect.h"
#include "public.sdk/source/vst/vsteditcontroller.h"
#include "public.sdk/source/vst/vstparameters.h"
#include "public.sdk/source/main/pluginfactory.h"
#include "pluginterfaces/base/ibstream.h"
#include "pluginterfaces/vst/ivstparameterchanges.h"
using namespace Steinberg;
using namespace Steinberg::Vst;
namespace rf=mhac::receipt::balanced_host;
namespace {
const FUID processorID(0x302FA817,0x7F104E13,0xBFC8A3EF,0x4356888E);
const FUID controllerID(0x1C3243AF,0x755B41C0,0x9A150E33,0x7150A434);
bool readPatch(IBStream* s,rf::Patch& p){
    std::array<std::uint8_t,20> b{};if(!s)return false;
    auto read=[&](std::uint8_t* dst,int32 left){while(left){int32 n=0;if(s->read(dst,left,&n)!=kResultOk||n<=0||n>left)return false;dst+=n;left-=n;}return true;};
    if(!read(b.data(),4))return false;
    const int32 size=(b[3]=='2'||b[3]=='4')?20:16;
    return read(b.data()+4,size-4)&&rf::load(b.data(),static_cast<std::size_t>(size),p);
}
struct Cursor {
    IParamValueQueue* q=nullptr;int32 index=0,count=0,offset=0;ParamValue value=0;bool pending=false;
    void next(){pending=false;while(index<count){if(q->getPoint(index++,offset,value)==kResultTrue){pending=true;break;}}}
    void init(IParamValueQueue* v){q=v;count=q->getPointCount();next();}
    bool apply(rf::Patch& p,unsigned id,int32 sample,bool flush){bool changed=false;while(pending&&(flush||offset<=sample)){changed=rf::control(p,id,value)||changed;next();}return changed;}
};
using Cursors=std::array<Cursor,rf::count>;
class Processor final : public AudioEffect {
    rf::Host host;
    void controls(Cursors& c,int32 i,bool flush=false){auto p=host.patch();bool changed=false;for(unsigned k=0;k<rf::count;++k)changed=c[k].apply(p,k,i,flush)||changed;if(changed)host.apply(p);}
    template<class T> tresult audio(ProcessData& d,T** in,T** out,Cursors& c){
        const auto channels=d.outputs[0].numChannels;
        if(!out||(channels!=1&&channels!=2)||(d.numInputs&&d.inputs[0].numChannels!=channels)||!out[0]||(channels==2&&!out[1]))return kResultFalse;
        const uint64 inputSilence=in?d.inputs[0].silenceFlags:~uint64(0);uint64 silent=(uint64(1)<<channels)-1;
        for(int32 i=0;i<d.numSamples;++i){controls(c,i);
            T l=(!in||!in[0]||(inputSilence&1))?T(0):in[0][i];T r=(channels==1||!in||!in[1]||(inputSilence&2))?T(0):in[1][i];
            host.frame(l,r);out[0][i]=l;if(channels==2)out[1][i]=r;
            if(l!=T(0))silent&=~uint64(1);if(channels==2&&r!=T(0))silent&=~uint64(2);
        }
        d.outputs[0].silenceFlags=silent;return kResultOk;
    }
    tresult block(ProcessData& d){
        if(d.numSamples<0||d.numInputs<0||d.numOutputs<0||d.numInputs>1||d.numOutputs>1)return kResultFalse;
        Cursors c{};if(d.inputParameterChanges)for(int32 i=0;i<d.inputParameterChanges->getParameterCount();++i){auto* q=d.inputParameterChanges->getParameterData(i);if(!q)continue;const auto id=q->getParameterId();if(id>=rf::firstID&&id<rf::firstID+rf::count&&!c[id-rf::firstID].q)c[id-rf::firstID].init(q);}
        if(d.numSamples==0){controls(c,0,true);return kResultOk;}
        if(d.numOutputs==0){for(int32 i=0;i<d.numSamples;++i){controls(c,i);double l=0,r=0;host.frame(l,r);}return kResultOk;}
        if(!d.outputs||(d.numInputs&&!d.inputs))return kResultFalse;
        if(d.symbolicSampleSize==kSample32)return audio(d,d.numInputs?d.inputs[0].channelBuffers32:nullptr,d.outputs[0].channelBuffers32,c);
        if(d.symbolicSampleSize==kSample64)return audio(d,d.numInputs?d.inputs[0].channelBuffers64:nullptr,d.outputs[0].channelBuffers64,c);
        return kResultFalse;
    }
public:
    Processor(){setControllerClass(controllerID);}
    static FUnknown* create(void*){return static_cast<IAudioProcessor*>(new Processor);}
    tresult PLUGIN_API initialize(FUnknown* c) override {auto r=AudioEffect::initialize(c);if(r!=kResultOk)return r;addAudioInput(STR16("Input"),SpeakerArr::kStereo);addAudioOutput(STR16("Output"),SpeakerArr::kStereo);return kResultOk;}
    tresult PLUGIN_API setBusArrangements(SpeakerArrangement* in,int32 ni,SpeakerArrangement* out,int32 no) override {if(ni!=1||no!=1||!in||!out||in[0]!=out[0]||(in[0]!=SpeakerArr::kStereo&&in[0]!=SpeakerArr::kMono))return kResultFalse;return AudioEffect::setBusArrangements(in,ni,out,no);}
    tresult PLUGIN_API canProcessSampleSize(int32 size) override {return size==kSample32||size==kSample64?kResultTrue:kResultFalse;}
    tresult PLUGIN_API setupProcessing(ProcessSetup& s) override {if(!host.prepare(s.sampleRate))return kResultFalse;return AudioEffect::setupProcessing(s);}
    tresult PLUGIN_API setActive(TBool active) override {auto r=AudioEffect::setActive(active);if(r==kResultOk&&active)host.reset();return r;}
    uint32 PLUGIN_API getLatencySamples() override {return 0;}
    uint32 PLUGIN_API getTailSamples() override {return 0;}
    tresult PLUGIN_API setState(IBStream* s) override {rf::Patch p;return readPatch(s,p)&&host.request(p)?kResultOk:kResultFalse;}
    tresult PLUGIN_API getState(IBStream* s) override {rf::Patch p;if(!s||!host.snapshot(p))return kResultFalse;auto b=rf::save(p);int32 n=0;return s->write(b.data(),int32(b.size()),&n)==kResultOk&&n==int32(b.size())?kResultOk:kResultFalse;}
    tresult PLUGIN_API process(ProcessData& d) override {host.begin();auto r=block(d);host.end();return r;}
};
class Controller final : public EditController {
public:
    static FUnknown* create(void*){return static_cast<IEditController*>(new Controller);}
    tresult PLUGIN_API initialize(FUnknown* c) override {
        auto r=EditController::initialize(c);if(r!=kResultOk)return r;
        auto add=[&](const TChar* name,unsigned id,int32 steps=0,int32 flags=ParameterInfo::kCanAutomate){parameters.addParameter(name,nullptr,steps,rf::normalized(rf::Patch{},id),flags,rf::firstID+id);};
        add(STR16("Collapse pair (0-27)"),rf::Action,27);add(STR16("Receipt (absent/fixed/preview/full)"),rf::Contract,3);add(STR16("Wet mix"),rf::Wet);add(STR16("Bypass"),rf::Bypass,1,ParameterInfo::kCanAutomate|ParameterInfo::kIsBypass);
        add(STR16("Resolution (3-8 bits)"),rf::Resolution,5);add(STR16("Fixed receipt budget (0-8)"),rf::Budget,8);
        add(STR16("Fine endpoint A (0-255)"),rf::FineA,255);add(STR16("Fine endpoint B (0-255)"),rf::FineB,255);
        add(STR16("Use fine endpoints"),rf::FineSource,1);
        add(STR16("Balanced receipt mode"),rf::Balanced,1);add(STR16("Receipt epoch (5-1000 ms)"),rf::Epoch,995);
        add(STR16("Receipt seed (0-65535)"),rf::Seed,65535);return kResultOk;
    }
    tresult PLUGIN_API setComponentState(IBStream* s) override {rf::Patch p;if(!readPatch(s,p))return kResultFalse;for(unsigned i=0;i<rf::count;++i)setParamNormalized(rf::firstID+i,rf::normalized(p,i));return kResultOk;}
};
}
BEGIN_FACTORY_DEF("MHAC", "https://github.com/techrote/MachineHumanAudioCybersemiotics", "")
DEF_CLASS2(INLINE_UID_FROM_FUID(processorID),PClassInfo::kManyInstances,kVstAudioEffectClass,"MHAC Receipt Fold",Vst::kDistributable,"Fx|Distortion","0.3.0",kVstVersionString,Processor::create)
DEF_CLASS2(INLINE_UID_FROM_FUID(controllerID),PClassInfo::kManyInstances,kVstComponentControllerClass,"MHAC Receipt Fold Controller",0,"","0.3.0",kVstVersionString,Controller::create)
END_FACTORY
