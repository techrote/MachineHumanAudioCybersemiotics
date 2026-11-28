#include "host.hpp"
#include "public.sdk/source/vst/vstaudioeffect.h"
#include "public.sdk/source/vst/vsteditcontroller.h"
#include "public.sdk/source/vst/vstparameters.h"
#include "public.sdk/source/main/pluginfactory.h"
#include "pluginterfaces/base/ibstream.h"
#include "pluginterfaces/vst/ivstparameterchanges.h"
using namespace Steinberg;
using namespace Steinberg::Vst;
namespace cr=mhac::counterfactual;
namespace h=cr::host;
namespace {
const FUID processorID(0xFBC2EF81,0xCA534C7A,0x8B3BC61D,0x9929C901);
const FUID controllerID(0xA1C27808,0x16014C3A,0x8AC0E00B,0x6D775BD5);
bool readState(IBStream* s,cr::State& p){
    if(!s)return false;
    auto readTo=[&](int32& pos,int32 size){while(pos<size){int32 n=0;if(s->read(p.bytes.data()+pos,size-pos,&n)!=kResultOk||n<=0||n>size-pos)return false;pos+=n;}return true;};
    int32 pos=0;if(!readTo(pos,4))return false;
    if(p.bytes[3]=='1')p.size=12;else if(p.bytes[3]=='2')p.size=14;else return false;
    if(!readTo(pos,static_cast<int32>(p.size)))return false;
    cr::Controls c;return cr::decodeState(p,c);
}
struct Cursor {
    IParamValueQueue* q=nullptr;int32 index=0,count=0,offset=0;ParamValue value=0;bool pending=false;
    void next(){pending=false;while(index<count){if(q->getPoint(index++,offset,value)==kResultTrue){pending=true;break;}}}
    void init(IParamValueQueue* v){q=v;count=q->getPointCount();next();}
    void apply(h::Host& host,unsigned id,int32 sample,bool flush){while(pending&&(flush||offset<=sample)){host.parameter(id,value);next();}}
};
using Cursors=std::array<Cursor,h::Count>;
class Processor final : public AudioEffect {
    h::Host host;
    void controls(Cursors& c,int32 i,bool flush=false){for(unsigned k=0;k<h::Count;++k)c[k].apply(host,k,i,flush);}
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
        Cursors c{};if(d.inputParameterChanges)for(int32 i=0;i<d.inputParameterChanges->getParameterCount();++i){auto* q=d.inputParameterChanges->getParameterData(i);if(!q)continue;const auto id=q->getParameterId();if(id>=h::firstID&&id<h::firstID+h::Count&&!c[id-h::firstID].q)c[id-h::firstID].init(q);}
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
    uint32 PLUGIN_API getTailSamples() override {return kInfiniteTail;}
    tresult PLUGIN_API setState(IBStream* s) override {cr::State p;return readState(s,p)&&host.request(p)?kResultOk:kResultFalse;}
    tresult PLUGIN_API getState(IBStream* s) override {if(!s)return kResultFalse;auto b=host.save();int32 n=0;return s->write(b.bytes.data(),int32(b.size),&n)==kResultOk&&n==int32(b.size)?kResultOk:kResultFalse;}
    tresult PLUGIN_API process(ProcessData& d) override {host.begin();auto r=block(d);host.end();return r;}
};
class Controller final : public EditController {
public:
    static FUnknown* create(void*){return static_cast<IEditController*>(new Controller);}
    tresult PLUGIN_API initialize(FUnknown* c) override {
        auto r=EditController::initialize(c);if(r!=kResultOk)return r;
        auto add=[&](const TChar* name,unsigned id,int32 steps=0,int32 flags=ParameterInfo::kCanAutomate){parameters.addParameter(name,nullptr,steps,h::normalized(cr::Controls{},id),flags,h::firstID+id);};
        add(STR16("Frequency (40-6000 Hz)"),h::Frequency,5960);add(STR16("Wet mix"),h::Wet,1000);add(STR16("Wet gain"),h::Gain,1000);
        add(STR16("Monitor (reference/persistent/residual)"),h::Monitor,2);add(STR16("Erase"),h::Erase,1);
        add(STR16("Bypass"),h::Bypass,1,ParameterInfo::kCanAutomate|ParameterInfo::kIsBypass);add(STR16("Intervention pulse"),h::Pulse,1);add(STR16("Peak excitation mix"),h::PeakMix,1000);return kResultOk;
    }
    tresult PLUGIN_API setComponentState(IBStream* s) override {cr::State p;cr::Controls c;if(!readState(s,p)||!cr::decodeState(p,c))return kResultFalse;for(unsigned i=0;i<h::Count;++i)setParamNormalized(h::firstID+i,h::normalized(c,i));return kResultOk;}
};
}
BEGIN_FACTORY_DEF("MHAC", "https://github.com/techrote/MachineHumanAudioCybersemiotics", "")
DEF_CLASS2(INLINE_UID_FROM_FUID(processorID),PClassInfo::kManyInstances,kVstAudioEffectClass,"MHAC Counterfactual Resonator",Vst::kDistributable,"Fx|Filter","0.2.0",kVstVersionString,Processor::create)
DEF_CLASS2(INLINE_UID_FROM_FUID(controllerID),PClassInfo::kManyInstances,kVstComponentControllerClass,"MHAC Counterfactual Resonator Controller",0,"","0.2.0",kVstVersionString,Controller::create)
END_FACTORY
