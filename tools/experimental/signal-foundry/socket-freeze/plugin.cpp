// Experimental VST3 adapter. Independent code; SDK API references in README.
#include "freeze.hpp"
#include "state.hpp"
#include "public.sdk/source/vst/vstaudioeffect.h"
#include "public.sdk/source/vst/vsteditcontroller.h"
#include "public.sdk/source/main/pluginfactory.h"
#include "pluginterfaces/base/ibstream.h"
#include "pluginterfaces/vst/ivstparameterchanges.h"
using namespace Steinberg;
using namespace Steinberg::Vst;
namespace {
const FUID processorId(0x8299B3A1,0x6A6548BF,0xBB2E741C,0x45C7A436);
const FUID controllerId(0x5FB36D21,0xF4AA4D0C,0xA9C1EE63,0xD34B8436);
bool readState(IBStream* s,mhac::Params& p){
    if(!s)return false;mhac::State b{};
    int32 offset=0;
    while(offset<int32(b.size())){int32 n=0;if(s->read(b.data()+offset,int32(b.size())-offset,&n)!=kResultOk||n<=0||n>int32(b.size())-offset)return false;offset+=n;}
    return mhac::decode(b,p);
}
bool writeState(IBStream* s,const mhac::Params& p){
    if(!s)return false;auto b=mhac::encode(p);int32 offset=0;
    while(offset<int32(b.size())){int32 n=0;if(s->write(b.data()+offset,int32(b.size())-offset,&n)!=kResultOk||n<=0||n>int32(b.size())-offset)return false;offset+=n;}
    return true;
}
// One cursor per stable parameter ID. Continuous points interpolate; switches step.
struct Cursor {
    IParamValueQueue* q=nullptr;int32 index=0,count=0,nextOffset=0,prevOffset=-1;
    double next=0,prev=0;bool valid=false;
    void advance(){
        valid=false;
        while(q&&index<count){int32 o=0;ParamValue v=0;if(q->getPoint(index++,o,v)==kResultTrue){nextOffset=std::max(0,o);next=mhac::unit(v);valid=true;break;}}
    }
    void init(IParamValueQueue* queue,double value){q=queue;count=q?q->getPointCount():0;prev=value;advance();}
    double at(int32 sample,bool continuous){
        while(valid&&nextOffset<=sample){prev=next;prevOffset=nextOffset;advance();}
        if(continuous&&valid&&nextOffset>prevOffset){double t=double(sample-prevOffset)/double(nextOffset-prevOffset);return prev+(next-prev)*std::clamp(t,0.0,1.0);}
        return prev;
    }
    double flush(){while(valid){prev=next;advance();}return prev;}
};
class Processor final:public AudioEffect {
    mhac::Freeze dsp;
    mhac::AtomicBank pending,published;
    std::atomic<uint64_t> applied{0};
    void restore(){
        mhac::Params p{};uint64_t v=0;
        if(pending.tryRead(p,v)&&v!=applied.load()){
            for(unsigned i=0;i<mhac::Count;++i)dsp.set(i,p[i]);
            dsp.reset();published.write(p);applied.store(v);
        }
    }
    template<class T> void render(ProcessData& d,std::array<Cursor,mhac::Count>& c,T** in,T** out,int32 n,uint64 inSilent){
        uint64 silence=(uint64(1)<<n)-1;
        for(int32 i=0;i<d.numSamples;++i){
            for(unsigned k=0;k<mhac::Count;++k)if(c[k].q)dsp.set(k,c[k].at(i,k<=mhac::Wet));
            const double g=dsp.step();
            for(int32 ch=0;ch<n;++ch){
                if(!out||!out[ch])continue;
                const T x=in&&in[ch]&&!(inSilent&(uint64(1)<<ch))?in[ch][i]:T(0);
                const T y=mhac::Freeze::apply(x,g);out[ch][i]=y;
                if(y!=0)silence&=~(uint64(1)<<ch);
            }
        }
        if(d.numOutputs>0)d.outputs[0].silenceFlags=silence;
    }
public:
    Processor(){setControllerClass(controllerId);}
    static FUnknown* createInstance(void*){return static_cast<IAudioProcessor*>(new Processor);}
    tresult PLUGIN_API initialize(FUnknown* context) override {
        auto r=AudioEffect::initialize(context);if(r!=kResultOk)return r;
        addAudioInput(STR16("Input"),SpeakerArr::kStereo);addAudioOutput(STR16("Output"),SpeakerArr::kStereo);return kResultOk;
    }
    tresult PLUGIN_API setBusArrangements(SpeakerArrangement* in,int32 ni,SpeakerArrangement* out,int32 no) override {
        if(ni!=1||no!=1||!in||!out||in[0]!=out[0]||(in[0]!=SpeakerArr::kMono&&in[0]!=SpeakerArr::kStereo))return kResultFalse;
        return AudioEffect::setBusArrangements(in,ni,out,no);
    }
    tresult PLUGIN_API canProcessSampleSize(int32 s) override {return s==kSample32||s==kSample64?kResultTrue:kResultFalse;}
    tresult PLUGIN_API setupProcessing(ProcessSetup& s) override {
        if(!std::isfinite(s.sampleRate)||s.sampleRate<8000||s.sampleRate>384000)return kResultFalse;
        auto r=AudioEffect::setupProcessing(s);if(r==kResultOk)dsp.prepare(s.sampleRate);return r;
    }
    tresult PLUGIN_API setActive(TBool state) override {if(state)dsp.reset();return AudioEffect::setActive(state);}
    tresult PLUGIN_API setState(IBStream* s) override {mhac::Params p{};if(!readState(s,p))return kResultFalse;pending.write(p);return kResultOk;}
    tresult PLUGIN_API getState(IBStream* s) override {
        for(int attempt=0;attempt<8;++attempt){mhac::Params p{};uint64_t v=0;if(!pending.tryRead(p,v))continue;if(v!=applied.load())return writeState(s,p)?kResultOk:kResultFalse;if(published.tryRead(p,v))return writeState(s,p)?kResultOk:kResultFalse;}
        return kResultFalse;
    }
    tresult PLUGIN_API process(ProcessData& d) override {
        if(d.numSamples<0||d.numInputs<0||d.numInputs>1||d.numOutputs<0||d.numOutputs>1)return kResultFalse;
        if(d.symbolicSampleSize!=kSample32&&d.symbolicSampleSize!=kSample64)return kResultFalse;
        if((d.numInputs&&!d.inputs)||(d.numOutputs&&!d.outputs))return kResultFalse;
        int32 ni=d.numInputs?d.inputs[0].numChannels:0,no=d.numOutputs?d.outputs[0].numChannels:0;
        if(ni<0||no<0||ni>2||no>2||(ni&&no&&ni!=no))return kResultFalse;
        restore();
        std::array<Cursor,mhac::Count> c{};
        if(auto* changes=d.inputParameterChanges)for(int32 j=0;j<changes->getParameterCount();++j){auto* q=changes->getParameterData(j);if(q&&q->getParameterId()<mhac::Count){auto k=q->getParameterId();c[k].init(q,dsp.parameters()[k]);}}
        if(d.numSamples==0){for(unsigned k=0;k<mhac::Count;++k)if(c[k].q)dsp.set(k,c[k].flush());}
        else {
            const auto silent=d.numInputs?d.inputs[0].silenceFlags:uint64(0);
            if(d.symbolicSampleSize==kSample32)render(d,c,ni?d.inputs[0].channelBuffers32:nullptr,no?d.outputs[0].channelBuffers32:nullptr,no,silent);
            else render(d,c,ni?d.inputs[0].channelBuffers64:nullptr,no?d.outputs[0].channelBuffers64:nullptr,no,silent);
        }
        published.write(dsp.parameters());return kResultOk;
    }
};
class Controller final:public EditController {
public:
    static FUnknown* createInstance(void*){return static_cast<IEditController*>(new Controller);}
    tresult PLUGIN_API initialize(FUnknown* context) override {
        auto r=EditController::initialize(context);if(r!=kResultOk)return r;
        const TChar* labels[]={STR16("Slot 1"),STR16("Slot 2"),STR16("Slot 3"),STR16("Slot 4"),STR16("Clock rate (log)"),STR16("Wet"),STR16("Hold")};
        for(unsigned i=0;i<=mhac::Hold;++i)parameters.addParameter(labels[i],nullptr,i==mhac::Hold?1:0,mhac::defaults[i],ParameterInfo::kCanAutomate,i);
        auto* mode=new StringListParameter(STR16("Freeze contract"),mhac::Mode);
        mode->appendString(STR16("Output latch"));mode->appendString(STR16("Transport pause"));mode->appendString(STR16("Bank snapshot"));parameters.addParameter(mode);
        parameters.addParameter(STR16("Bypass"),nullptr,1,0,ParameterInfo::kCanAutomate|ParameterInfo::kIsBypass,mhac::Bypass);
        return kResultOk;
    }
    tresult PLUGIN_API setComponentState(IBStream* s) override {
        mhac::Params p{};if(!readState(s,p))return kResultFalse;
        for(unsigned i=0;i<mhac::Count;++i)setParamNormalized(i,p[i]);return kResultOk;
    }
};
}
BEGIN_FACTORY_DEF("MHAC Experimental Audio","https://github.com/techrote/MachineHumanAudioCybersemiotics","")
DEF_CLASS2(INLINE_UID_FROM_FUID(processorId),PClassInfo::kManyInstances,kVstAudioEffectClass,"Socket Freeze",0,"Fx|Modulation","0.1.0",kVstVersionString,Processor::createInstance)
DEF_CLASS2(INLINE_UID_FROM_FUID(controllerId),PClassInfo::kManyInstances,kVstComponentControllerClass,"Socket Freeze Controller",0,"","0.1.0",kVstVersionString,Controller::createInstance)
END_FACTORY
