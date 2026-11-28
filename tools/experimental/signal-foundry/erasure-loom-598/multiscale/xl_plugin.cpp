#include "../../../vst-mainline/state_bridge.hpp"
#include "xl.hpp"
#include "public.sdk/source/vst/vstaudioeffect.h"
#include "public.sdk/source/vst/vsteditcontroller.h"
#include "public.sdk/source/vst/vstparameters.h"
#include "public.sdk/source/main/pluginfactory.h"
#include "pluginterfaces/base/ibstream.h"
#include "pluginterfaces/vst/ivstparameterchanges.h"
using namespace Steinberg;
using namespace Steinberg::Vst;
namespace {
const FUID processorID(0xB74B3910,0xA48B4F39,0x85C32649,0x18E4C6F1);
const FUID controllerID(0xE852D6D2,0xC8D641D5,0x9AD99778,0x47B32C16);
constexpr ParamID firstID=1300;
bool readExact(IBStream* stream,std::uint8_t* bytes,int32 size){
    if(!stream)return false;
    while(size>0){int32 n=0;if(stream->read(bytes,size,&n)!=kResultOk||n<=0||n>size)return false;bytes+=n;size-=n;}
    return true;
}
bool readParams(IBStream* stream,loomxl::Normalized& p){
    loomxl::State bytes{};
    return readExact(stream,bytes.data(),int32(bytes.size()))&&loomxl::decode(bytes.data(),bytes.size(),p);
}
struct Cursor {
    IParamValueQueue* queue=nullptr;int32 index=0,count=0,offset=0;ParamValue value=0;bool pending=false;
    void next(){pending=false;while(index<count){if(queue->getPoint(index++,offset,value)==kResultTrue){pending=true;break;}}}
    void init(IParamValueQueue* q){queue=q;count=q->getPointCount();next();}
    void apply(loomxl::Live& e,unsigned id,int32 sample,bool flush=false){while(pending&&(flush||offset<=sample)){e.set(id,value);next();}}
};
class Processor final : public AudioEffect {
    loomxl::Live engine;
    
    mhac::mainline::StateBridge<loomxl::Normalized> state{engine.params()};
    void applyPending() noexcept { loomxl::Normalized p{};if(state.take(p)) { (void)(engine.restore(p)); } }
    void publishState() noexcept { state.publish(engine.params()); }
    using Cursors=std::array<Cursor,loomxl::Count>;
    template<class T> tresult audio(ProcessData& d,T** in,T** out,Cursors& cursors){
        if(!out||d.outputs[0].numChannels!=2||(d.numInputs&&d.inputs[0].numChannels!=2)||!out[0]||!out[1])return kResultFalse;
        const uint64 inputSilence=in?d.inputs[0].silenceFlags:~uint64(0);uint64 silent=3;
        for(int32 i=0;i<d.numSamples;++i){
            for(unsigned k=0;k<loomxl::Count;++k)cursors[k].apply(engine,k,i);
            const T l=(!in||!in[0]||(inputSilence&1))?T(0):in[0][i];
            const T r=(!in||!in[1]||(inputSilence&2))?T(0):in[1][i];
            const auto y=engine.step(l,r);out[0][i]=T(y[0]);out[1][i]=T(y[1]);
            for(unsigned c=0;c<2;++c)if(out[c][i]!=T(0))silent&=~(uint64(1)<<c);
        }
        d.outputs[0].silenceFlags=silent;return kResultOk;
    }
public:
    Processor(){setControllerClass(controllerID);}
    static FUnknown* create(void*){return static_cast<IAudioProcessor*>(new Processor);}
    tresult PLUGIN_API initialize(FUnknown* context) override {
        auto r=AudioEffect::initialize(context);if(r!=kResultOk)return r;
        addAudioInput(STR16("Stereo Input"),SpeakerArr::kStereo);
        addAudioOutput(STR16("Stereo Output"),SpeakerArr::kStereo);return kResultOk;
    }
    tresult PLUGIN_API setBusArrangements(SpeakerArrangement* in,int32 ni,SpeakerArrangement* out,int32 no) override {
        if(ni!=1||no!=1||!in||!out||in[0]!=out[0]||in[0]!=SpeakerArr::kStereo)return kResultFalse;
        return AudioEffect::setBusArrangements(in,ni,out,no);
    }
    tresult PLUGIN_API canProcessSampleSize(int32 size) override {return size==kSample32||size==kSample64?kResultTrue:kResultFalse;}
    tresult PLUGIN_API setupProcessing(ProcessSetup& setup) override {
        applyPending();if(!engine.prepare(setup.sampleRate))return kResultFalse;
        publishState();return AudioEffect::setupProcessing(setup);
    }
    tresult PLUGIN_API setActive(TBool active) override {auto r=AudioEffect::setActive(active);if(r==kResultOk&&active){applyPending();engine.reset();publishState();}return r;}
    uint32 PLUGIN_API getLatencySamples() override {return loomxl::latency;}
    uint32 PLUGIN_API getTailSamples() override {return loomxl::tail;}
    tresult PLUGIN_API setState(IBStream* stream) override {loomxl::Normalized p{};if(!readParams(stream,p))return kResultFalse;state.request(p);return kResultOk;}
    tresult PLUGIN_API getState(IBStream* stream) override {
        if(!stream)return kResultFalse;auto bytes=loomxl::encode(state.snapshot());int32 n=0;
        return stream->write(bytes.data(),int32(bytes.size()),&n)==kResultOk&&n==int32(bytes.size())?kResultOk:kResultFalse;
    }
    tresult PLUGIN_API process(ProcessData& d) override {
        if(d.numSamples<0)return kResultFalse;
        applyPending();
        struct Publish { Processor& owner; ~Publish(){owner.publishState();} } publish{*this};
        if(d.numSamples<0||d.numInputs<0||d.numOutputs<0)return kResultFalse;
        Cursors cursors{};
        if(d.inputParameterChanges)for(int32 i=0;i<d.inputParameterChanges->getParameterCount();++i){
            auto* q=d.inputParameterChanges->getParameterData(i);if(!q)continue;
            auto id=q->getParameterId();if(id>=firstID&&id<firstID+loomxl::Count&&!cursors[id-firstID].queue)cursors[id-firstID].init(q);
        }
        if(d.numSamples==0){for(unsigned k=0;k<loomxl::Count;++k)cursors[k].apply(engine,k,0,true);return kResultOk;}
        if(d.numOutputs==0){for(int32 i=0;i<d.numSamples;++i){for(unsigned k=0;k<loomxl::Count;++k)cursors[k].apply(engine,k,i);engine.step(0.,0.);}return kResultOk;}
        if(!d.outputs||d.numOutputs!=1||d.numInputs>1||(d.numInputs&&!d.inputs))return kResultFalse;
        if(d.symbolicSampleSize==kSample32)return audio(d,d.numInputs?d.inputs[0].channelBuffers32:nullptr,d.outputs[0].channelBuffers32,cursors);
        if(d.symbolicSampleSize==kSample64)return audio(d,d.numInputs?d.inputs[0].channelBuffers64:nullptr,d.outputs[0].channelBuffers64,cursors);
        return kResultFalse;
    }
};
class Controller final : public EditController {
public:
    static FUnknown* create(void*){return static_cast<IEditController*>(new Controller);}
    tresult PLUGIN_API initialize(FUnknown* ctx) override {
        auto r=EditController::initialize(ctx);if(r!=kResultOk)return r;
        auto add=[&](const TChar* name,unsigned id,int32 steps=0,int32 flags=ParameterInfo::kCanAutomate){parameters.addParameter(name,nullptr,steps,loomxl::defaults[id],flags,firstID+id);};
        add(STR16("Separation (1-4 chunks)"),loomxl::Separation,3);
        add(STR16("Rotation (0-8)"),loomxl::Rotation,8);
        add(STR16("Amplification budget (1-16x)"),loomxl::Budget);
        add(STR16("Repair"),loomxl::Repair);
        add(STR16("Wet mix"),loomxl::Wet);
        add(STR16("Wet gain"),loomxl::Gain);
        add(STR16("Bypass"),loomxl::Bypass,1,ParameterInfo::kCanAutomate|ParameterInfo::kIsBypass);
        add(STR16("Probe restoration"),loomxl::Probe);
        add(STR16("Soft erasure edges"),loomxl::Edge);
        add(STR16("Scale (Fine / Medium / Coarse)"),loomxl::Scale,2);
        return kResultOk;
    }
    tresult PLUGIN_API setComponentState(IBStream* stream) override {
        loomxl::Normalized p{};if(!readParams(stream,p))return kResultFalse;
        for(unsigned i=0;i<loomxl::Count;++i)setParamNormalized(firstID+i,p[i]);return kResultOk;
    }
};
}
BEGIN_FACTORY_DEF("MHAC", "https://github.com/techrote/MachineHumanAudioCybersemiotics", "")
DEF_CLASS2(INLINE_UID_FROM_FUID(processorID), PClassInfo::kManyInstances, kVstAudioEffectClass,
           "MHAC Erasure Loom XL", Vst::kDistributable, "Fx|Filter", "0.1.0", kVstVersionString, Processor::create)
DEF_CLASS2(INLINE_UID_FROM_FUID(controllerID), PClassInfo::kManyInstances, kVstComponentControllerClass,
           "MHAC Erasure Loom XL Controller", 0, "", "0.1.0", kVstVersionString, Controller::create)
END_FACTORY
