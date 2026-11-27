#include "bank_adapter.hpp"
#include "public.sdk/source/vst/vstaudioeffect.h"
#include "public.sdk/source/vst/vsteditcontroller.h"
#include "public.sdk/source/vst/vstparameters.h"
#include "public.sdk/source/main/pluginfactory.h"
#include "pluginterfaces/base/ibstream.h"
#include "pluginterfaces/vst/ivstparameterchanges.h"
#include <mutex>
using namespace Steinberg;
using namespace Steinberg::Vst;
namespace cr=mhac::counterfactual;
namespace bh=cr::bankhost;
namespace {
const FUID processorID(0xAE00577B,0xADF94D9C,0x8F2FB9D0,0x4991475C);
const FUID controllerID(0xB82C6F98,0xA6D847E9,0xB6084DF9,0x834F4B45);
bool readState(IBStream* s,bh::State& bytes){
    if(!s)return false;
    int32 pos=0;const auto size=static_cast<int32>(bytes.size());
    while(pos<size){int32 n=0;if(s->read(bytes.data()+pos,size-pos,&n)!=kResultOk||n<=0||n>size-pos)return false;pos+=n;}
    // State is a bounded component stream; reject appended data.
    uint8 extra=0;int32 n=0;s->read(&extra,1,&n);
    cr::MemoryConfig c{};return n==0&&bh::decode(bytes,c);
}
bool writeState(IBStream* s,bh::State bytes){
    if(!s)return false;
    int32 pos=0;const auto size=static_cast<int32>(bytes.size());
    while(pos<size){int32 n=0;if(s->write(bytes.data()+pos,size-pos,&n)!=kResultOk||n<=0||n>size-pos)return false;pos+=n;}return true;
}
class Processor final : public AudioEffect {
    bh::Host host;
    bh::EventBatch batch;
    std::mutex stateMutex; // only non-audio state callers
    bool collect(ProcessData& d){
        batch.clear(static_cast<unsigned>(d.numSamples));
        if(auto* changes=d.inputParameterChanges){
            const auto count=changes->getParameterCount();if(count<0||count>static_cast<int32>(bh::ParamCount))return false;
            for(int32 q=0;q<count;++q){auto* queue=changes->getParameterData(q);if(!queue||!batch.queue(queue->getParameterId()))return false;
                const auto points=queue->getPointCount();if(points<0||points>static_cast<int32>(bh::MaxEvents-batch.size()))return false;
                for(int32 p=0;p<points;++p){int32 offset=0;ParamValue value=0;if(queue->getPoint(p,offset,value)!=kResultTrue||offset<0||!batch.point(static_cast<unsigned>(offset),value))return false;}
            }
        }
        return batch.finish();
    }
    template<class T> tresult audio(ProcessData& d,T** in,T** out){
        const auto ni=d.numInputs?d.inputs[0].numChannels:0;
        const auto no=d.numOutputs?d.outputs[0].numChannels:0;
        if((d.numInputs&&ni!=1&&ni!=2)||(d.numOutputs&&no!=1&&no!=2)||(ni&&no&&ni!=no))return kResultFalse;
        if(d.numSamples&&no&&(!out||!out[0]||(no==2&&!out[1])))return kResultFalse;
        const uint64 mask=d.numInputs?d.inputs[0].silenceFlags:~uint64(0);
        const T* l=in&&ni&&!(mask&1)?in[0]:nullptr;
        const T* r=in&&ni==2&&!(mask&2)?in[1]:nullptr;
        T* ol=out&&no?out[0]:nullptr;T* oright=out&&no==2?out[1]:nullptr;
        if(!host.processOptional(l,r,ol,oright,static_cast<unsigned>(d.numSamples),batch.data(),batch.size()))return kResultFalse;
        if(d.numOutputs){uint64 silent=(uint64(1)<<no)-1;
            for(int32 i=0;i<d.numSamples;++i){if(ol[i]!=T(0))silent&=~uint64(1);if(no==2&&oright[i]!=T(0))silent&=~uint64(2);}
            d.outputs[0].silenceFlags=silent;
        }
        return kResultOk;
    }
public:
    Processor(){setControllerClass(controllerID);}
    static FUnknown* create(void*){return static_cast<IAudioProcessor*>(new Processor);}
    tresult PLUGIN_API initialize(FUnknown* c) override {auto r=AudioEffect::initialize(c);if(r!=kResultOk)return r;addAudioInput(STR16("Input"),SpeakerArr::kStereo);addAudioOutput(STR16("Output"),SpeakerArr::kStereo);return kResultOk;}
    tresult PLUGIN_API setBusArrangements(SpeakerArrangement* in,int32 ni,SpeakerArrangement* out,int32 no) override {if(ni!=1||no!=1||!in||!out||in[0]!=out[0]||(in[0]!=SpeakerArr::kStereo&&in[0]!=SpeakerArr::kMono))return kResultFalse;return AudioEffect::setBusArrangements(in,ni,out,no);}
    tresult PLUGIN_API canProcessSampleSize(int32 s) override {return s==kSample32||s==kSample64?kResultTrue:kResultFalse;}
    tresult PLUGIN_API setupProcessing(ProcessSetup& s) override {if(!host.prepare(s.sampleRate))return kResultFalse;return AudioEffect::setupProcessing(s);}
    tresult PLUGIN_API setActive(TBool active) override {auto r=AudioEffect::setActive(active);if(r==kResultOk&&active)host.reset();return r;}
    uint32 PLUGIN_API getLatencySamples() override {return 0;}
    uint32 PLUGIN_API getTailSamples() override {return kInfiniteTail;}
    tresult PLUGIN_API setState(IBStream* s) override {bh::State p{};if(!readState(s,p))return kResultFalse;std::lock_guard<std::mutex> lock(stateMutex);return host.request(p)?kResultOk:kResultFalse;}
    tresult PLUGIN_API getState(IBStream* s) override {bh::State p{};{std::lock_guard<std::mutex> lock(stateMutex);p=host.save();}return writeState(s,p)?kResultOk:kResultFalse;}
    tresult PLUGIN_API process(ProcessData& d) override {
        if(d.numSamples<0||d.numInputs<0||d.numOutputs<0||d.numInputs>1||d.numOutputs>1||(d.numInputs&&!d.inputs)||(d.numOutputs&&!d.outputs)||!collect(d))return kResultFalse;
        if(d.numSamples==0)return host.processOptional<double>(nullptr,nullptr,nullptr,nullptr,0,batch.data(),batch.size())?kResultOk:kResultFalse;
        if(d.symbolicSampleSize==kSample32)return audio(d,d.numInputs?d.inputs[0].channelBuffers32:nullptr,d.numOutputs?d.outputs[0].channelBuffers32:nullptr);
        if(d.symbolicSampleSize==kSample64)return audio(d,d.numInputs?d.inputs[0].channelBuffers64:nullptr,d.numOutputs?d.outputs[0].channelBuffers64:nullptr);
        return kResultFalse;
    }
};
class Controller final : public EditController {
public:
    static FUnknown* create(void*){return static_cast<IEditController*>(new Controller);}
    tresult PLUGIN_API initialize(FUnknown* c) override {
        auto r=EditController::initialize(c);if(r!=kResultOk)return r;
        auto add=[&](const TChar* name,unsigned id,int32 steps,int32 flags=ParameterInfo::kCanAutomate){parameters.addParameter(name,nullptr,steps,bh::normalized(cr::MemoryConfig{},id),flags,id);};
        add(STR16("Wet mix"),bh::Wet,1000);add(STR16("Bypass"),bh::Bypass,1,ParameterInfo::kCanAutomate|ParameterInfo::kIsBypass);
        const TChar* names[4][9]={
            {STR16("B1 Frequency (Hz)"),STR16("B1 Gain"),STR16("B1 Peak mix"),STR16("B1 Selectivity"),STR16("B1 Capture"),STR16("B1 Erase"),STR16("B1 Discard on close"),STR16("B1 Intervention pulse"),STR16("B1 Discard pending")},
            {STR16("B2 Frequency (Hz)"),STR16("B2 Gain"),STR16("B2 Peak mix"),STR16("B2 Selectivity"),STR16("B2 Capture"),STR16("B2 Erase"),STR16("B2 Discard on close"),STR16("B2 Intervention pulse"),STR16("B2 Discard pending")},
            {STR16("B3 Frequency (Hz)"),STR16("B3 Gain"),STR16("B3 Peak mix"),STR16("B3 Selectivity"),STR16("B3 Capture"),STR16("B3 Erase"),STR16("B3 Discard on close"),STR16("B3 Intervention pulse"),STR16("B3 Discard pending")},
            {STR16("B4 Frequency (Hz)"),STR16("B4 Gain"),STR16("B4 Peak mix"),STR16("B4 Selectivity"),STR16("B4 Capture"),STR16("B4 Erase"),STR16("B4 Discard on close"),STR16("B4 Intervention pulse"),STR16("B4 Discard pending")}};
        for(unsigned b=0;b<4;++b)for(unsigned f=0;f<9;++f)add(names[b][f],bh::FirstBand+b*bh::Stride+f,f==bh::Frequency?5960:f<bh::Excite?1000:1);
        const TChar* optimalNames[4]={STR16("B1 Optimal erase"),STR16("B2 Optimal erase"),STR16("B3 Optimal erase"),STR16("B4 Optimal erase")};
        for(unsigned b=0;b<4;++b)add(optimalNames[b],bh::FirstOptimal+b,1);
        return kResultOk;
    }
    tresult PLUGIN_API setComponentState(IBStream* s) override {bh::State p{};cr::MemoryConfig c{};if(!readState(s,p)||!bh::decode(p,c))return kResultFalse;for(unsigned i=0;i<bh::ParamCount;++i){const auto id=bh::paramID(i);setParamNormalized(id,bh::normalized(c,id));}return kResultOk;}
};
}
BEGIN_FACTORY_DEF("MHAC", "https://github.com/techrote/MachineHumanAudioCybersemiotics", "")
DEF_CLASS2(INLINE_UID_FROM_FUID(processorID),PClassInfo::kManyInstances,kVstAudioEffectClass,"MHAC Harmonic Memory Bank",Vst::kDistributable,"Fx|Filter","0.2.0",kVstVersionString,Processor::create)
DEF_CLASS2(INLINE_UID_FROM_FUID(controllerID),PClassInfo::kManyInstances,kVstComponentControllerClass,"MHAC Harmonic Memory Bank Controller",0,"","0.2.0",kVstVersionString,Controller::create)
END_FACTORY
