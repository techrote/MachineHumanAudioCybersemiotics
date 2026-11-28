#include "clock_state_bridge.hpp"
#include "public.sdk/source/vst/vstaudioeffect.h"
#include "public.sdk/source/vst/vsteditcontroller.h"
#include "public.sdk/source/vst/vstparameters.h"
#include "public.sdk/source/main/pluginfactory.h"
#include "pluginterfaces/base/ibstream.h"
#include "pluginterfaces/vst/ivstparameterchanges.h"
using namespace Steinberg;
using namespace Steinberg::Vst;
namespace cf=mhac::clock_fold;
namespace {
const FUID processorID(0x9C421577,0xDB974730,0x93EA688E,0xA71D090A);
const FUID controllerID(0x13D9F7E3,0xDAD34F94,0xB72F25D5,0xD2BD4564);
constexpr ParamID firstID=cf::firstID;
bool readExact(IBStream* stream,std::uint8_t* bytes,int32 size){
    if(!stream)return false;
    while(size>0){int32 n=0;if(stream->read(bytes,size,&n)!=kResultOk||n<=0||n>size)return false;bytes+=n;size-=n;}
    return true;
}
bool readParams(IBStream* stream,cf::Normalized& p){
    cf::State bytes{};
    if(!readExact(stream,bytes.data(),4)||bytes[0]!='C'||bytes[1]!='F'||bytes[2]!='0')return false;
    const int32 size=bytes[3]=='1'?52:bytes[3]=='2'?int32(bytes.size()):0;
    return size>4&&readExact(stream,bytes.data()+4,size-4)&&cf::decode(bytes.data(),std::size_t(size),p);
}
struct Cursor {
    IParamValueQueue* queue=nullptr;int32 index=0,count=0,offset=0;ParamValue value=0;bool pending=false;
    void next(){pending=false;while(index<count){if(queue->getPoint(index++,offset,value)==kResultTrue){pending=true;break;}}}
    void init(IParamValueQueue* q){queue=q;count=q->getPointCount();next();}
    void apply(cf::Live& e,unsigned id,int32 sample,bool flush=false){while(pending&&(flush||offset<=sample)){e.set(id,value);next();}}
};
class Processor final : public AudioEffect {
    cf::Live engine;
    cf::StateBridge state;
    
    using Cursors=std::array<Cursor,cf::Count>;
    template<class T> tresult audio(ProcessData& d,T** in,T** out,Cursors& cursors){
        const int32 channels=d.outputs[0].numChannels;
        if(!out||(channels!=1&&channels!=2)||(d.numInputs&&d.inputs[0].numChannels!=channels)||!out[0]||(channels==2&&!out[1]))return kResultFalse;
        const uint64 inputSilence=in?d.inputs[0].silenceFlags:~uint64(0);uint64 silent=(uint64(1)<<channels)-1;
        for(int32 i=0;i<d.numSamples;++i){
            for(unsigned k=0;k<cf::Count;++k)cursors[k].apply(engine,k,i);
            const T l=(!in||!in[0]||(inputSilence&1))?T(0):in[0][i];
            const T r=(channels==1||!in||!in[1]||(inputSilence&2))?T(0):in[1][i];
            const auto y=engine.step(l,r);out[0][i]=T(y[0]);if(channels==2)out[1][i]=T(y[1]);
            for(int32 c=0;c<channels;++c)if(out[c][i]!=T(0))silent&=~(uint64(1)<<c);
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
        if(ni!=1||no!=1||!in||!out||in[0]!=out[0]||(in[0]!=SpeakerArr::kStereo&&in[0]!=SpeakerArr::kMono))return kResultFalse;
        return AudioEffect::setBusArrangements(in,ni,out,no);
    }
    tresult PLUGIN_API canProcessSampleSize(int32 size) override {return size==kSample32||size==kSample64?kResultTrue:kResultFalse;}
    tresult PLUGIN_API setupProcessing(ProcessSetup& setup) override {
        if(!engine.prepare(setup.sampleRate))return kResultFalse;
        return AudioEffect::setupProcessing(setup);
    }
    tresult PLUGIN_API setActive(TBool active) override {auto r=AudioEffect::setActive(active);if(r==kResultOk&&active)engine.reset();return r;}
    uint32 PLUGIN_API getLatencySamples() override {return cf::Engine::latency;}
    uint32 PLUGIN_API getTailSamples() override {return cf::Engine::tail;}
    tresult PLUGIN_API setState(IBStream* stream) override {cf::Normalized p{};if(!readParams(stream,p))return kResultFalse;return state.request(p)?kResultOk:kResultFalse;}
    tresult PLUGIN_API getState(IBStream* stream) override {
        cf::Normalized p{};if(!stream||!state.save(p))return kResultFalse;auto bytes=cf::encode(p);int32 n=0;
        return stream->write(bytes.data(),int32(bytes.size()),&n)==kResultOk&&n==int32(bytes.size())?kResultOk:kResultFalse;
    }
    tresult PLUGIN_API process(ProcessData& d) override {
        // Lifecycle activation clears history; patch changes during processing do not.
        state.begin(engine,true);
        const auto result=processBlock(d);
        state.end(engine);
        return result;
    }
private:
    tresult processBlock(ProcessData& d) {
        if(d.numSamples<0||d.numInputs<0||d.numOutputs<0)return kResultFalse;
        Cursors cursors{};
        if(d.inputParameterChanges)for(int32 i=0;i<d.inputParameterChanges->getParameterCount();++i){
            auto* q=d.inputParameterChanges->getParameterData(i);if(!q)continue;
            auto id=q->getParameterId();if(id>=firstID&&id<firstID+cf::Count&&!cursors[id-firstID].queue)cursors[id-firstID].init(q);
        }
        if(d.numSamples==0){for(unsigned k=0;k<cf::Count;++k)cursors[k].apply(engine,k,0,true);return kResultOk;}
        if(d.numOutputs==0){for(int32 i=0;i<d.numSamples;++i){for(unsigned k=0;k<cf::Count;++k)cursors[k].apply(engine,k,i);engine.step(0.,0.);}return kResultOk;}
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
        auto add=[&](const TChar* name,unsigned id,int32 steps=0,int32 flags=ParameterInfo::kCanAutomate){parameters.addParameter(name,nullptr,steps,cf::defaults[id],flags,firstID+id);};
        add(STR16("Log drift (-0.5 to 0.5)"),cf::Drift);
        add(STR16("Curvature (-0.5 to 0.5)"),cf::Curvature);
        add(STR16("Known drift compensation"),cf::Compensation);
        add(STR16("Wet mix"),cf::Wet);
        add(STR16("Seam width (0-25%)"),cf::Edge);
        add(STR16("Bypass"),cf::Bypass,1,ParameterInfo::kCanAutomate|ParameterInfo::kIsBypass);
        add(STR16("Reconstruction (linear / filtered)"),cf::Quality,1);
        return kResultOk;
    }
    tresult PLUGIN_API setComponentState(IBStream* stream) override {
        cf::Normalized p{};if(!readParams(stream,p))return kResultFalse;
        for(unsigned i=0;i<cf::Count;++i)setParamNormalized(firstID+i,p[i]);return kResultOk;
    }
};
}
BEGIN_FACTORY_DEF("MHAC", "https://github.com/techrote/MachineHumanAudioCybersemiotics", "")
DEF_CLASS2(INLINE_UID_FROM_FUID(processorID), PClassInfo::kManyInstances, kVstAudioEffectClass,
           "MHAC Clock Fold", Vst::kDistributable, "Fx|Delay", "0.2.2", kVstVersionString, Processor::create)
DEF_CLASS2(INLINE_UID_FROM_FUID(controllerID), PClassInfo::kManyInstances, kVstComponentControllerClass,
           "MHAC Clock Fold Controller", 0, "", "0.2.2", kVstVersionString, Controller::create)
END_FACTORY
