#include "live.hpp"
#include "public.sdk/source/vst/vstaudioeffect.h"
#include "public.sdk/source/vst/vsteditcontroller.h"
#include "public.sdk/source/vst/vstparameters.h"
#include "public.sdk/source/main/pluginfactory.h"
#include "pluginterfaces/base/ibstream.h"
#include "pluginterfaces/vst/ivstparameterchanges.h"

using namespace Steinberg;
using namespace Steinberg::Vst;
namespace fx = mhac::lattice;
namespace {
const FUID processorID(0x752F649A,0xC7E24E77,0xB90CFDB8,0x28B23E10);
const FUID controllerID(0x22467EC7,0x346A4895,0x8DCA660A,0x0DA4F528);
constexpr ParamID firstID=100;
bool readParams(IBStream* stream,fx::Params& p){
    fx::State bytes{};int32 n=0;
    return stream&&stream->read(bytes.data(),int32(bytes.size()),&n)==kResultOk&&n==int32(bytes.size())&&fx::decode(bytes,p);
}
struct Cursor {
    IParamValueQueue* queue=nullptr;int32 index=0,count=0,offset=0;ParamValue value=0;bool pending=false;
    void next(){
        pending=false;
        while(index<count){if(queue->getPoint(index++,offset,value)==kResultTrue){pending=true;break;}}
    }
    void init(IParamValueQueue* q){queue=q;count=q->getPointCount();next();}
    void apply(fx::Live& e,unsigned id,int32 sample,bool flush=false){
        while(pending&&(flush||offset<=sample)){e.set(id,value);next();}
    }
};
class Processor final : public AudioEffect {
    fx::Live engine;
    double sampleRate=48000.;
    using Cursors=std::array<Cursor,fx::Count>;
    template<class T> tresult audio(ProcessData& d,T** in,T** out,Cursors& cursors){
        if(!out||d.outputs[0].numChannels!=2||(in&&d.inputs[0].numChannels!=2)||!out[0]||!out[1])return kResultFalse;
        const uint64 inputSilence=in?d.inputs[0].silenceFlags:~uint64(0);
        uint64 silent=3;
        for(int32 i=0;i<d.numSamples;++i){
            for(unsigned k=0;k<fx::Count;++k)cursors[k].apply(engine,k,i);
            const T l=(!in||!in[0]||(inputSilence&1))?T(0):in[0][i];
            const T r=(!in||!in[1]||(inputSilence&2))?T(0):in[1][i];
            const auto y=engine.process(l,r);
            for(unsigned c=0;c<2;++c){out[c][i]=y[c];if(y[c]!=T(0))silent&=~(uint64(1)<<c);}
        }
        d.outputs[0].silenceFlags=silent;
        return kResultOk;
    }
public:
    Processor(){setControllerClass(controllerID);}
    static FUnknown* create(void*){return static_cast<IAudioProcessor*>(new Processor);}
    tresult PLUGIN_API initialize(FUnknown* context) override {
        auto r=AudioEffect::initialize(context);if(r!=kResultOk)return r;
        addAudioInput(STR16("Input"),SpeakerArr::kStereo);
        addAudioOutput(STR16("Output"),SpeakerArr::kStereo);return kResultOk;
    }
    tresult PLUGIN_API setBusArrangements(SpeakerArrangement* in,int32 ni,SpeakerArrangement* out,int32 no) override {
        if(ni!=1||no!=1||!in||!out||in[0]!=out[0]||in[0]!=SpeakerArr::kStereo)return kResultFalse;
        return AudioEffect::setBusArrangements(in,ni,out,no);
    }
    tresult PLUGIN_API canProcessSampleSize(int32 size) override {return size==kSample32||size==kSample64?kResultTrue:kResultFalse;}
    tresult PLUGIN_API setupProcessing(ProcessSetup& setup) override {
        if(!fx::validSampleRate(setup.sampleRate))return kResultFalse;
        auto r=AudioEffect::setupProcessing(setup);if(r==kResultOk){sampleRate=setup.sampleRate;engine.reset(sampleRate);}return r;
    }
    tresult PLUGIN_API setActive(TBool active) override {auto r=AudioEffect::setActive(active);if(r==kResultOk&&active)engine.reset(sampleRate);return r;}
    uint32 PLUGIN_API getLatencySamples() override {return 0;}
    uint32 PLUGIN_API getTailSamples() override {return 4096;}
    tresult PLUGIN_API setState(IBStream* stream) override {fx::Params p{};if(!readParams(stream,p))return kResultFalse;engine.restore(p);return kResultOk;}
    tresult PLUGIN_API getState(IBStream* stream) override {
        if(!stream)return kResultFalse;auto bytes=fx::encode(engine.params());int32 n=0;
        return stream->write(bytes.data(),int32(bytes.size()),&n)==kResultOk&&n==int32(bytes.size())?kResultOk:kResultFalse;
    }
    tresult PLUGIN_API process(ProcessData& d) override {
        Cursors cursors{};
        if(d.inputParameterChanges)for(int32 i=0;i<d.inputParameterChanges->getParameterCount();++i){
            auto* q=d.inputParameterChanges->getParameterData(i);if(!q)continue;
            auto id=q->getParameterId();if(id>=firstID&&id<firstID+fx::Count&&!cursors[id-firstID].queue)cursors[id-firstID].init(q);
        }
        if(d.numSamples<0)return kResultFalse;
        if(d.numSamples==0){for(unsigned k=0;k<fx::Count;++k)cursors[k].apply(engine,k,0,true);return kResultOk;}
        if(d.numOutputs==0){for(int32 i=0;i<d.numSamples;++i){for(unsigned k=0;k<fx::Count;++k)cursors[k].apply(engine,k,i);engine.process(0.,0.);}return kResultOk;}
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
        constexpr int32 autoFlag=ParameterInfo::kCanAutomate;
        auto add=[&](const TChar* name,unsigned id,int32 steps=0,int32 flags=ParameterInfo::kCanAutomate){parameters.addParameter(name,nullptr,steps,fx::defaults[id],flags,firstID+id);};
        add(STR16("Stage 1 axis (L/R/S/D)"),fx::Axis1,3);
        add(STR16("Stage 2 axis (L/R/S/D)"),fx::Axis2,3);
        add(STR16("Stage 3 axis (L/R/S/D)"),fx::Axis3,3);
        add(STR16("Stage 4 axis (L/R/S/D)"),fx::Axis4,3);
        add(STR16("Stage 1 delay (1-1024)"),fx::Delay1,1023);
        add(STR16("Stage 2 delay (1-1024)"),fx::Delay2,1023);
        add(STR16("Stage 3 delay (1-1024)"),fx::Delay3,1023);
        add(STR16("Stage 4 delay (1-1024)"),fx::Delay4,1023);
        add(STR16("Causal inverse"),fx::Inverse,1);
        add(STR16("Wet mix"),fx::Mix);
        add(STR16("Bypass"),fx::Bypass,1,autoFlag|ParameterInfo::kIsBypass);
        return kResultOk;
    }
    tresult PLUGIN_API setComponentState(IBStream* stream) override {
        fx::Params p{};if(!readParams(stream,p))return kResultFalse;
        for(unsigned i=0;i<fx::Count;++i)setParamNormalized(firstID+i,p[i]);return kResultOk;
    }
};
}
BEGIN_FACTORY_DEF("MHAC", "https://github.com/techrote/MachineHumanAudioCybersemiotics", "")
DEF_CLASS2(INLINE_UID_FROM_FUID(processorID), PClassInfo::kManyInstances, kVstAudioEffectClass,
           "MHAC Projector Lattice", Vst::kDistributable, "Fx|Spatial", "0.1.1", kVstVersionString, Processor::create)
DEF_CLASS2(INLINE_UID_FROM_FUID(controllerID), PClassInfo::kManyInstances, kVstComponentControllerClass,
           "MHAC Projector Lattice Controller", 0, "", "0.1.1", kVstVersionString, Controller::create)
END_FACTORY
