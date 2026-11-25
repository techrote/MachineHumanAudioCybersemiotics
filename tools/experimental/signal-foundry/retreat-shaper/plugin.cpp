#include "retreat.hpp"
#include "public.sdk/source/vst/vstaudioeffect.h"
#include "public.sdk/source/vst/vsteditcontroller.h"
#include "public.sdk/source/vst/vstparameters.h"
#include "public.sdk/source/main/pluginfactory.h"
#include "pluginterfaces/base/ibstream.h"
#include "pluginterfaces/vst/ivstparameterchanges.h"

using namespace Steinberg;
using namespace Steinberg::Vst;
namespace fx = mhac::retreat;
namespace {
const FUID processorID(0xE54A3D7C,0xB2F64201,0xAF5E8993,0x1CC7B816);
const FUID controllerID(0x67FB91AE,0x15E34C72,0xBBD98E24,0x7CA53F10);
constexpr ParamID firstID=100;
bool readParams(IBStream* stream,fx::Params& p){
    fx::State bytes{};int32 n=0;
    if(!stream||stream->read(bytes.data(),8,&n)!=kResultOk||n!=8)return false;
    const auto version=fx::get(bytes,4);
    const int32 size=version==1?int32(fx::legacySize):version==2?int32(bytes.size()):0;
    if(!size)return false;
    return stream->read(bytes.data()+8,size-8,&n)==kResultOk&&n==size-8&&fx::decode(bytes,p,unsigned(size));
}
struct Cursor {
    IParamValueQueue* queue=nullptr;int32 index=0,count=0,offset=0;ParamValue value=0;bool pending=false;
    void next(){
        pending=false;
        while(index<count){if(queue->getPoint(index++,offset,value)==kResultTrue){pending=true;break;}}
    }
    void init(IParamValueQueue* q){queue=q;count=q->getPointCount();next();}
    void apply(fx::Engine& e,unsigned id,int32 sample,bool flush=false){
        while(pending&&(flush||offset<=sample)){e.set(id,value);next();}
    }
};
class Processor final : public AudioEffect {
    fx::Engine engine;
    double sampleRate=48000.;
    using Cursors=std::array<Cursor,fx::Count>;
    template<class T> tresult audio(ProcessData& d,T** in,T** out,Cursors& cursors){
        const int32 channels=d.outputs[0].numChannels;
        if(!out||channels<1||channels>2||(in&&d.inputs[0].numChannels!=channels))return kResultFalse;
        for(int32 c=0;c<channels;++c)if(!out[c])return kResultFalse;
        const uint64 inputSilence=in?d.inputs[0].silenceFlags:~uint64(0);
        uint64 silent=(uint64(1)<<channels)-1;
        for(int32 i=0;i<d.numSamples;++i){
            for(unsigned k=0;k<fx::Count;++k)cursors[k].apply(engine,k,i);
            for(int32 c=0;c<channels;++c){
                const uint64 bit=uint64(1)<<c;
                const T x=(!in||!in[c]||(inputSilence&bit))?T(0):in[c][i];
                const T y=engine.process(unsigned(c),x);
                out[c][i]=y;if(y!=T(0))silent&=~bit;
            }
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
        if(ni!=1||no!=1||!in||!out||in[0]!=out[0]||(in[0]!=SpeakerArr::kMono&&in[0]!=SpeakerArr::kStereo))return kResultFalse;
        return AudioEffect::setBusArrangements(in,ni,out,no);
    }
    tresult PLUGIN_API canProcessSampleSize(int32 size) override {return size==kSample32||size==kSample64?kResultTrue:kResultFalse;}
    tresult PLUGIN_API setupProcessing(ProcessSetup& setup) override {
        if(!fx::validSampleRate(setup.sampleRate))return kResultFalse;
        auto r=AudioEffect::setupProcessing(setup);if(r==kResultOk){sampleRate=setup.sampleRate;engine.reset(sampleRate);}return r;
    }
    tresult PLUGIN_API setActive(TBool active) override {auto r=AudioEffect::setActive(active);if(r==kResultOk&&active)engine.reset(sampleRate);return r;}
    uint32 PLUGIN_API getLatencySamples() override {return 0;}
    uint32 PLUGIN_API getTailSamples() override {return kNoTail;}
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
        if(d.numOutputs==0){for(int32 i=0;i<d.numSamples;++i){for(unsigned k=0;k<fx::Count;++k)cursors[k].apply(engine,k,i);engine.process(0,0.);engine.process(1,0.);}return kResultOk;}
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
        add(STR16("Drive (1-16x)"),fx::Drive);
        add(STR16("Coupling A-B"),fx::Coupling);
        add(STR16("Depth"),fx::Depth);
        add(STR16("Mix"),fx::Mix);
        add(STR16("Bypass"),fx::Bypass,1,autoFlag|ParameterInfo::kIsBypass);
        add(STR16("Attack (0-100 ms)"),fx::Attack);
        add(STR16("Release (0-500 ms)"),fx::Release);
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
           "MHAC Retreat Shaper", Vst::kDistributable, "Fx|Dynamics", "0.2.0", kVstVersionString, Processor::create)
DEF_CLASS2(INLINE_UID_FROM_FUID(controllerID), PClassInfo::kManyInstances, kVstComponentControllerClass,
           "MHAC Retreat Shaper Controller", 0, "", "0.2.0", kVstVersionString, Controller::create)
END_FACTORY
