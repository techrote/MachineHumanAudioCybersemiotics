#include "trace_bell_state.hpp"
#include "public.sdk/source/vst/vstaudioeffect.h"
#include "public.sdk/source/vst/vsteditcontroller.h"
#include "public.sdk/source/main/pluginfactory.h"
#include "pluginterfaces/base/ibstream.h"
#include "pluginterfaces/vst/ivstparameterchanges.h"

using namespace Steinberg;
using namespace Steinberg::Vst;
using namespace mhac::accel;
namespace {
const FUID processorID(0xA6740DA9,0xEA17442B,0x9B283CF2,0x584E908C);
const FUID controllerID(0x6CC1A2E8,0x9D724BD3,0xA4AE670C,0xC88F11B5);
constexpr unsigned count=6;
double normalized(const TracePatch& p,unsigned id) {
    switch(id) {
    case 0:return std::clamp((double(p.pitch)-80.)/420.,0.,1.);
    case 1:return std::clamp((double(p.decay)-double(.03f))/(double(1.2f)-double(.03f)),0.,1.);
    case 2:return p.contrast;
    case 3:return p.mix;
    case 4:return p.spread;
    default:return p.bypass?1.:0.;
    }
}
bool readState(IBStream* stream,TracePatch& patch) {
    if(!stream)return false;
    TraceState bytes{};
    int32 offset=0;
    while(offset<int32(bytes.size())){
        int32 n=0;
        const auto rc=stream->read(bytes.data()+offset,int32(bytes.size())-offset,&n);
        if(rc!=kResultOk||n<=0||n>int32(bytes.size())-offset)return false;
        offset+=n;
    }
    return decodeTraceState(bytes.data(),bytes.size(),patch);
}
bool writeState(IBStream* stream,const TracePatch& patch) {
    TraceState bytes{};
    if(!stream||!encodeTraceState(patch,bytes))return false;
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
    TraceBellPerformance engine;
    uint32 tail=2880000;
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
        if(setup.symbolicSampleSize!=kSample32||!traceRateSupported(setup.sampleRate))return kResultFalse;
        const auto rc=AudioEffect::setupProcessing(setup);if(rc!=kResultOk)return rc;
        if(!engine.prepare(float(setup.sampleRate)))return kResultFalse;
        tail=uint32(std::ceil(60.*setup.sampleRate));return kResultOk;
    }
    tresult PLUGIN_API setActive(TBool active) override {
        const auto rc=AudioEffect::setActive(active);
        if(rc==kResultOk&&active)engine.reset();return rc;
    }
    uint32 PLUGIN_API getLatencySamples() override {return 0;}
    uint32 PLUGIN_API getTailSamples() override {return tail;}
    // First adapter candidate: lifecycle/state calls require serialized access
    // with processing. Concurrent host state save/load is not qualified.
    tresult PLUGIN_API setState(IBStream* stream) override {
        TracePatch p{};return readState(stream,p)&&engine.configure(p)?kResultOk:kResultFalse;
    }
    tresult PLUGIN_API getState(IBStream* stream) override {
        return writeState(stream,engine.patch())?kResultOk:kResultFalse;
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
            TracePatch patch=engine.patch();bool changed=false;
            for(unsigned id=0;id<count;++id){
                auto& c=cursors[id];
                while(c.pending&&c.offset==sample){
                    applyTraceNormalized(patch,id,c.value);changed=true;c.advance();
                }
            }
            if(changed)engine.configure(patch);
        };
        if(!d.numSamples){apply(0);return kResultOk;}
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
        for(int32 i=0;i<d.numSamples;++i){
            apply(i);
            const float l=(!in||(silentIn&1))?0.f:in[0][i];
            const float r=(!in||(silentIn&2))?0.f:in[1][i];
            const auto y=engine.process({l,r});
            if(out){out[0][i]=y.l;out[1][i]=y.r;if(y.l!=0) silentOut&=~uint64(1);if(y.r!=0)silentOut&=~uint64(2);}
        }
        if(out)d.outputs[0].silenceFlags=silentOut;
        return kResultOk;
    }
};
class Controller final : public EditController {
public:
    static FUnknown* create(void*){return static_cast<IEditController*>(new Controller);}
    tresult PLUGIN_API initialize(FUnknown* ctx) override {
        const auto rc=EditController::initialize(ctx);if(rc!=kResultOk)return rc;
        TracePatch p{};
        const auto add=[&](const TChar* name,unsigned id,int32 steps=0,int32 flags=ParameterInfo::kCanAutomate){
            parameters.addParameter(name,nullptr,steps,normalized(p,id),flags,id);
        };
        add(STR16("Pitch (80-500 Hz)"),0);
        add(STR16("Decay (0.03-1.2 s)"),1);
        add(STR16("Transient contrast"),2);
        add(STR16("Wet mix"),3);
        add(STR16("Stereo spread"),4);
        add(STR16("Bypass"),5,1,ParameterInfo::kCanAutomate|ParameterInfo::kIsBypass);
        return kResultOk;
    }
    tresult PLUGIN_API setComponentState(IBStream* stream) override {
        TracePatch p{};if(!readState(stream,p))return kResultFalse;
        for(unsigned id=0;id<count;++id)setParamNormalized(id,normalized(p,id));
        return kResultOk;
    }
};
}
BEGIN_FACTORY_DEF("MHAC", "https://github.com/techrote/MachineHumanAudioCybersemiotics", "")
DEF_CLASS2(INLINE_UID_FROM_FUID(processorID), PClassInfo::kManyInstances, kVstAudioEffectClass,
           "MHAC Trace Bell", Vst::kDistributable, "Fx", "0.1.0", kVstVersionString, Processor::create)
DEF_CLASS2(INLINE_UID_FROM_FUID(controllerID), PClassInfo::kManyInstances, kVstComponentControllerClass,
           "MHAC Trace Bell Controller", 0, "", "0.1.0", kVstVersionString, Controller::create)
END_FACTORY
