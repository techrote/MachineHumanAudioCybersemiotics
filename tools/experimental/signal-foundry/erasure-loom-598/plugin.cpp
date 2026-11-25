#include "live2.hpp"
#include "public.sdk/source/vst/vstaudioeffect.h"
#include "public.sdk/source/vst/vsteditcontroller.h"
#include "public.sdk/source/vst/vstparameters.h"
#include "public.sdk/source/main/pluginfactory.h"
#include "pluginterfaces/base/ibstream.h"
#include "pluginterfaces/vst/ivstparameterchanges.h"
using namespace Steinberg;
using namespace Steinberg::Vst;
namespace {
const FUID processorID(0xDC4F4B71,0x8CA24A61,0xA3B728C4,0xC77342EE);
const FUID controllerID(0x180FD226,0x37C64D5B,0x9BEA1378,0x6F8D22A1);
constexpr ParamID firstID=1100;
bool readExact(IBStream* stream,std::uint8_t* bytes,int32 size){
    if(!stream)return false;
    while(size>0){int32 n=0;if(stream->read(bytes,size,&n)!=kResultOk||n<=0||n>size)return false;bytes+=n;size-=n;}
    return true;
}
bool readParams(IBStream* stream,loom2::Normalized& p){
    loom2::State bytes{};
    if(!readExact(stream,bytes.data(),4)||bytes[0]!='E'||bytes[1]!='L'||bytes[2]!='0')return false;
    const int32 size=bytes[3]=='1'?60:bytes[3]=='2'?int32(bytes.size()):0;
    return size&&readExact(stream,bytes.data()+4,size-4)&&loom2::decode(bytes.data(),size,p);
}
struct Cursor {
    IParamValueQueue* queue=nullptr;int32 index=0,count=0,offset=0;ParamValue value=0;bool pending=false;
    void next(){pending=false;while(index<count){if(queue->getPoint(index++,offset,value)==kResultTrue){pending=true;break;}}}
    void init(IParamValueQueue* q){queue=q;count=q->getPointCount();next();}
    void apply(loom2::Live& e,unsigned id,int32 sample,bool flush=false){while(pending&&(flush||offset<=sample)){e.set(id,value);next();}}
};
class Processor final : public AudioEffect {
    loom2::Live engine;
    
    using Cursors=std::array<Cursor,loom2::Count>;
    template<class T> tresult audio(ProcessData& d,T** in,T** out,Cursors& cursors){
        if(!out||d.outputs[0].numChannels!=2||(d.numInputs&&d.inputs[0].numChannels!=2)||!out[0]||!out[1])return kResultFalse;
        const uint64 inputSilence=in?d.inputs[0].silenceFlags:~uint64(0);uint64 silent=3;
        for(int32 i=0;i<d.numSamples;++i){
            for(unsigned k=0;k<loom2::Count;++k)cursors[k].apply(engine,k,i);
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
        if(!engine.prepare(setup.sampleRate))return kResultFalse;
        return AudioEffect::setupProcessing(setup);
    }
    tresult PLUGIN_API setActive(TBool active) override {auto r=AudioEffect::setActive(active);if(r==kResultOk&&active)engine.reset();return r;}
    uint32 PLUGIN_API getLatencySamples() override {return loom2::ProbeEngine::latency;}
    uint32 PLUGIN_API getTailSamples() override {return loom2::ProbeEngine::tail;}
    tresult PLUGIN_API setState(IBStream* stream) override {loom2::Normalized p{};if(!readParams(stream,p))return kResultFalse;return engine.restore(p)?kResultOk:kResultFalse;}
    tresult PLUGIN_API getState(IBStream* stream) override {
        if(!stream)return kResultFalse;auto bytes=loom2::encode(engine.params());int32 n=0;
        return stream->write(bytes.data(),int32(bytes.size()),&n)==kResultOk&&n==int32(bytes.size())?kResultOk:kResultFalse;
    }
    tresult PLUGIN_API process(ProcessData& d) override {
        if(d.numSamples<0||d.numInputs<0||d.numOutputs<0)return kResultFalse;
        Cursors cursors{};
        if(d.inputParameterChanges)for(int32 i=0;i<d.inputParameterChanges->getParameterCount();++i){
            auto* q=d.inputParameterChanges->getParameterData(i);if(!q)continue;
            auto id=q->getParameterId();if(id>=firstID&&id<firstID+loom2::Count&&!cursors[id-firstID].queue)cursors[id-firstID].init(q);
        }
        if(d.numSamples==0){for(unsigned k=0;k<loom2::Count;++k)cursors[k].apply(engine,k,0,true);return kResultOk;}
        if(d.numOutputs==0){for(int32 i=0;i<d.numSamples;++i){for(unsigned k=0;k<loom2::Count;++k)cursors[k].apply(engine,k,i);engine.step(0.,0.);}return kResultOk;}
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
        auto add=[&](const TChar* name,unsigned id,int32 steps=0,int32 flags=ParameterInfo::kCanAutomate){parameters.addParameter(name,nullptr,steps,loom2::defaults[id],flags,firstID+id);};
        add(STR16("Separation (1-4 chunks)"),loom2::Separation,3);
        add(STR16("Rotation (0-8)"),loom2::Rotation,8);
        add(STR16("Amplification budget (1-16x)"),loom2::Budget);
        add(STR16("Repair"),loom2::Repair);
        add(STR16("Wet mix"),loom2::Wet);
        add(STR16("Wet gain"),loom2::Gain);
        add(STR16("Bypass"),loom2::Bypass,1,ParameterInfo::kCanAutomate|ParameterInfo::kIsBypass);
        add(STR16("Probe restoration"),loom2::Probe);
        add(STR16("Soft erasure edges"),loom2::Edge);
        return kResultOk;
    }
    tresult PLUGIN_API setComponentState(IBStream* stream) override {
        loom2::Normalized p{};if(!readParams(stream,p))return kResultFalse;
        for(unsigned i=0;i<loom2::Count;++i)setParamNormalized(firstID+i,p[i]);return kResultOk;
    }
};
}
BEGIN_FACTORY_DEF("MHAC", "https://github.com/techrote/MachineHumanAudioCybersemiotics", "")
DEF_CLASS2(INLINE_UID_FROM_FUID(processorID), PClassInfo::kManyInstances, kVstAudioEffectClass,
           "MHAC Erasure Loom", Vst::kDistributable, "Fx|Filter", "0.2.0", kVstVersionString, Processor::create)
DEF_CLASS2(INLINE_UID_FROM_FUID(controllerID), PClassInfo::kManyInstances, kVstComponentControllerClass,
           "MHAC Erasure Loom Controller", 0, "", "0.2.0", kVstVersionString, Controller::create)
END_FACTORY
