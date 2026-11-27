#include "shuttle_control.hpp"
#include "../trace-bell/trace_bell_mailbox.hpp"
#include "public.sdk/source/vst/vstaudioeffect.h"
#include "public.sdk/source/vst/vsteditcontroller.h"
#include "public.sdk/source/main/pluginfactory.h"
#include "pluginterfaces/base/ibstream.h"
#include "pluginterfaces/vst/ivstparameterchanges.h"

using namespace Steinberg;
using namespace Steinberg::Vst;
using namespace mhac::accel;
namespace {
const FUID processorID(0x58F3C28A,0xBA5142D1,0xAF75DF83,0x173B962E);
const FUID controllerID(0x7D191A63,0x804C4BF0,0xA02BFE68,0x9B7D1C24);
constexpr unsigned count=5;
bool readState(IBStream* stream,ShuttlePatch& patch) {
    if(!stream)return false;
    ShuttleState bytes{};
    int32 offset=0;
    while(offset<int32(bytes.size())){
        int32 n=0;
        const auto rc=stream->read(bytes.data()+offset,int32(bytes.size())-offset,&n);
        if(rc!=kResultOk||n<=0||n>int32(bytes.size())-offset)return false;
        offset+=n;
    }
    return decode(bytes,patch);
}
bool writeState(IBStream* stream,const ShuttlePatch& patch) {
    auto bytes=encode(patch);
    if(!stream||!valid(patch))return false;
    int32 offset=0;
    while(offset<int32(bytes.size())){
        int32 n=0;
        if(stream->write(bytes.data()+offset,int32(bytes.size())-offset,&n)!=kResultOk||
           n<=0||n>int32(bytes.size())-offset)return false;
        offset+=n;
    }
    return true;
}
// Fixed cursor per parameter. No allocation, no event truncation. Host queues
// are immutable for the duration of process. Preflight all recognized queues.
struct Cursor {
    IParamValueQueue* q=nullptr;
    int32 index=0,size=0,offset=0;
    ParamValue value=0;
    bool pending=false;
    void advance(){
        pending=index<size;
        if(pending)q->getPoint(index++,offset,value);
    }
    bool init(IParamValueQueue* queue,int32 frames){
        if(q)return false;
        q=queue;size=q->getPointCount();
        if(size<0||size>std::max(int32(1),frames))return false;
        int32 last=-1;
        for(int32 i=0;i<size;++i){
            int32 at=0;ParamValue v=0;
            if(q->getPoint(i,at,v)!=kResultTrue||at<0||at>=std::max(int32(1),frames)||
               at<last||!std::isfinite(v)||v<0||v>1)return false;
            last=at;
        }
        advance();return true;
    }
};
class Processor final : public AudioEffect {
    DesktopShuttle engine;
    TraceStateBridge<ShuttlePatch> state;
    uint32 tail=1440000;
    void applyPending() noexcept {
        ShuttlePatch p{};if(state.take(p))engine.configure(p);
    }
    void publishState() noexcept {state.publish(engine.patch());}
public:
    Processor(){setControllerClass(controllerID);}
    static FUnknown* create(void*){return static_cast<IAudioProcessor*>(new Processor);}
    tresult PLUGIN_API initialize(FUnknown* ctx) override {
        const auto rc=AudioEffect::initialize(ctx);if(rc!=kResultOk)return rc;
        addAudioInput(STR16("Stereo Input"),SpeakerArr::kStereo);
        addAudioOutput(STR16("Stereo Output"),SpeakerArr::kStereo);
        return kResultOk;
    }
    tresult PLUGIN_API setBusArrangements(SpeakerArrangement* in,int32 ni,SpeakerArrangement* out,int32 no) override {
        if(ni!=1||no!=1||!in||!out||in[0]!=SpeakerArr::kStereo||out[0]!=SpeakerArr::kStereo)return kResultFalse;
        return AudioEffect::setBusArrangements(in,ni,out,no);
    }
    tresult PLUGIN_API canProcessSampleSize(int32 size) override {
        return size==kSample32?kResultTrue:kResultFalse;
    }
    tresult PLUGIN_API setupProcessing(ProcessSetup& setup) override {
        if(setup.symbolicSampleSize!=kSample32||!DesktopShuttle::grainForRate(setup.sampleRate))return kResultFalse;
        const auto rc=AudioEffect::setupProcessing(setup);if(rc!=kResultOk)return rc;
        if(!engine.prepareRate(setup.sampleRate))return kResultFalse;
        applyPending();engine.reset();publishState();
        tail=uint32(std::ceil(30.*setup.sampleRate));return kResultOk;
    }
    tresult PLUGIN_API setActive(TBool active) override {
        const auto rc=AudioEffect::setActive(active);
        if(rc==kResultOk&&active){applyPending();engine.reset();publishState();}return rc;
    }
    // Activation owns initialization/reset. Start/stop are notifications only;
    // preserve tails and pending state across transport pauses, with no RT work.
    tresult PLUGIN_API setProcessing(TBool /*state*/) override {return kResultOk;}
    uint32 PLUGIN_API getLatencySamples() override {return 0;}
    uint32 PLUGIN_API getTailSamples() override {return tail;}
    // State I/O is control-side only; the engine has a single audio owner.
    tresult PLUGIN_API setState(IBStream* stream) override {
        ShuttlePatch p{};if(!readState(stream,p))return kResultFalse;
        state.request(p);return kResultOk;
    }
    tresult PLUGIN_API getState(IBStream* stream) override {
        return writeState(stream,state.snapshot())?kResultOk:kResultFalse;
    }
    tresult PLUGIN_API process(ProcessData& d) override {
        if(d.numSamples<0||d.numInputs<0||d.numInputs>1||d.numOutputs<0||d.numOutputs>1)return kResultFalse;
        std::array<Cursor,count> cursors{};
        if(d.inputParameterChanges){
            const auto n=d.inputParameterChanges->getParameterCount();
            if(n<0)return kResultFalse;
            for(int32 i=0;i<n;++i){
                auto* q=d.inputParameterChanges->getParameterData(i);
                if(!q)return kResultFalse;
                const auto id=q->getParameterId();
                if(id<count&&!cursors[id].init(q,d.numSamples))return kResultFalse;
            }
        }
        const auto apply=[&](int32 sample){
            ShuttlePatch patch=engine.patch();bool changed=false;
            for(unsigned id=0;id<count;++id){
                auto& c=cursors[id];
                while(c.pending&&c.offset==sample){
                    applyShuttleNormalized(patch,id,c.value);changed=true;c.advance();
                }
            }
            if(changed)engine.configure(patch);
        };
        if(!d.numSamples){applyPending();apply(0);publishState();return kResultOk;}
        if(d.symbolicSampleSize!=kSample32)return kResultFalse;
        Sample32** in=nullptr;Sample32** out=nullptr;uint64 silentIn=3,silentOut=3;
        if(d.numInputs){
            if(!d.inputs||d.inputs[0].numChannels!=2)return kResultFalse;
            in=d.inputs[0].channelBuffers32;silentIn=d.inputs[0].silenceFlags;
            if(!in||(!in[0]&&!(silentIn&1))||(!in[1]&&!(silentIn&2)))return kResultFalse;
        }
        if(d.numOutputs){
            if(!d.outputs||d.outputs[0].numChannels!=2)return kResultFalse;
            out=d.outputs[0].channelBuffers32;
            if(!out||!out[0]||!out[1])return kResultFalse;
        }
        applyPending();
        for(int32 i=0;i<d.numSamples;++i){
            apply(i);
            const float l=(!in||(silentIn&1))?0.f:in[0][i];
            const float r=(!in||(silentIn&2))?0.f:in[1][i];
            const auto y=engine.process({l,r});
            if(out){out[0][i]=y.l;out[1][i]=y.r;if(y.l!=0) silentOut&=~uint64(1);if(y.r!=0)silentOut&=~uint64(2);}
        }
        if(out)d.outputs[0].silenceFlags=silentOut;
        publishState();
        return kResultOk;
    }
};
class Controller final : public EditController {
public:
    static FUnknown* create(void*){return static_cast<IEditController*>(new Controller);}
    tresult PLUGIN_API initialize(FUnknown* ctx) override {
        const auto rc=EditController::initialize(ctx);if(rc!=kResultOk)return rc;
        ShuttlePatch p{};
        const auto add=[&](const TChar* name,unsigned id,int32 steps=0,int32 flags=ParameterInfo::kCanAutomate){
            parameters.addParameter(name,nullptr,steps,shuttleNormalized(p,id),flags,id);
        };
        add(STR16("Wet mix"),0,1000);
        add(STR16("Reverse"),1,1000);
        add(STR16("Feedback (max 65%)"),2,1000);
        add(STR16("Stereo cross"),3,1000);
        add(STR16("Bypass"),4,1,ParameterInfo::kCanAutomate|ParameterInfo::kIsBypass);
        return kResultOk;
    }
    tresult PLUGIN_API setComponentState(IBStream* stream) override {
        ShuttlePatch p{};if(!readState(stream,p))return kResultFalse;
        for(unsigned id=0;id<count;++id)setParamNormalized(id,shuttleNormalized(p,id));
        return kResultOk;
    }
};
}
BEGIN_FACTORY_DEF("MHAC", "https://github.com/techrote/MachineHumanAudioCybersemiotics", "")
DEF_CLASS2(INLINE_UID_FROM_FUID(processorID), PClassInfo::kManyInstances, kVstAudioEffectClass,
           "MHAC Palimpsest Shuttle", Vst::kDistributable, "Fx", "0.1.0", kVstVersionString, Processor::create)
DEF_CLASS2(INLINE_UID_FROM_FUID(controllerID), PClassInfo::kManyInstances, kVstComponentControllerClass,
           "MHAC Palimpsest Shuttle Controller", 0, "", "0.1.0", kVstVersionString, Controller::create)
END_FACTORY
