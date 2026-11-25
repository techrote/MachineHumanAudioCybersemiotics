#include "integrated.hpp"
#include <type_traits>
#include "public.sdk/source/vst/vstaudioeffect.h"
#include "public.sdk/source/vst/vsteditcontroller.h"
#include "public.sdk/source/vst/vstparameters.h"
#include "public.sdk/source/main/pluginfactory.h"
#include "pluginterfaces/base/ibstream.h"
#include "pluginterfaces/vst/ivstevents.h"
#include "pluginterfaces/vst/ivstparameterchanges.h"
using namespace Steinberg;
using namespace Steinberg::Vst;
namespace {
const FUID processorID(0xD1195E6E,0x292C442C,0xB550AE83,0x4977E4CD);
const FUID controllerID(0x992821A7,0xB1114FB3,0x8B69B059,0xEC25C81C);
constexpr ParamID firstID=1000;
bool readParams(IBStream* s,winters::integrated::Params& p){
    winters::integrated::State bytes{};int32 n=0;
    if(!s||s->read(bytes.data(),4,&n)!=kResultOk||n!=4)return false;
    const int32 size=bytes[3]=='1'?int32(winters::live::State{}.size()):bytes[3]=='2'?int32(bytes.size()):0;
    return size>4&&s->read(bytes.data()+4,size-4,&n)==kResultOk&&n==size-4&&winters::integrated::decode(bytes.data(),size,p);
}
struct Cursor {
    IParamValueQueue* queue=nullptr;int32 index=0,count=0,offset=0;ParamValue value=0;bool pending=false;
    void next(){pending=false;while(index<count){if(queue->getPoint(index++,offset,value)==kResultTrue){pending=true;break;}}}
    void init(IParamValueQueue* q){queue=q;count=q->getPointCount();next();}
    void apply(winters::integrated::Engine& e,unsigned id,int32 sample,bool flush=false){while(pending&&(flush||offset<=sample)){e.parameter(id,value);next();}}
};
int key(int id,int channel,int pitch){return id>=0?id:-1-128*std::clamp(channel,0,15)-std::clamp(pitch,0,127);}
struct Events {
    IEventList* list=nullptr;int32 index=0,count=0;Event event{};bool pending=false;
    explicit Events(IEventList* l):list(l),count(l?l->getEventCount():0){next();}
    void next(){pending=false;while(index<count){if(list->getEvent(index++,event)==kResultOk){pending=true;break;}}}
    void apply(winters::integrated::Engine& e,int32 sample){
        while(pending&&event.sampleOffset<=sample){
            if(event.busIndex==0){
                if(event.type==Event::kNoteOnEvent){const auto& n=event.noteOn;const int k=key(n.noteId,n.channel,n.pitch);if(n.velocity>0)e.on(k,n.pitch,n.tuning,n.velocity);else e.off(k);}
                if(event.type==Event::kNoteOffEvent){const auto& n=event.noteOff;e.off(key(n.noteId,n.channel,n.pitch));}
            }
            next();
        }
    }
};
class Processor final: public AudioEffect {
    winters::integrated::Engine engine;double sr=48000.;
    using Cursors=std::array<Cursor,winters::integrated::Count>;
    winters::live::Frame step(Cursors& c,Events& ev,int32 i){for(unsigned k=0;k<winters::integrated::Count;++k)c[k].apply(engine,k,i);ev.apply(engine,i);return engine.tick();}
    template<class T> tresult audio(ProcessData& d,Cursors& c,Events& ev){
        std::array<std::array<T*,2>,4> buffers{};
        std::array<unsigned,4> channels{};
        std::array<uint64,4> silence{};
        for(int32 bus=0;bus<d.numOutputs;++bus){
            auto& out=d.outputs[bus];auto* info=getAudioOutput(bus);
            if(!info||out.numChannels<0||out.numChannels>(bus==0?2:1))return kResultFalse;
            const auto expected=SpeakerArr::getChannelCount(info->getArrangement());
            if(out.numChannels!=expected)return kResultFalse;
            channels[bus]=unsigned(out.numChannels);silence[bus]=(uint64(1)<<channels[bus])-1;
            T** ptr=nullptr;
            if constexpr(std::is_same_v<T,Sample32>)ptr=out.channelBuffers32;
            else ptr=out.channelBuffers64;
            for(unsigned ch=0;ch<channels[bus];++ch){
                if(info->isActive()&&(!ptr||!ptr[ch]))return kResultFalse;
                // Inactive buses may have null sample pointers. If the host supplies valid
                // memory, write silence there rather than leaving stale samples.
                if(info->isActive())buffers[bus][ch]=ptr[ch];
                else if(ptr&&ptr[ch])std::fill_n(ptr[ch],d.numSamples,T(0));
            }
        }
        for(int32 i=0;i<d.numSamples;++i){
            const auto f=step(c,ev,i);
            winters::live::write(f,buffers[0].data(),channels[0],buffers[1][0],buffers[2][0],buffers[3][0],unsigned(i));
            for(int32 bus=0;bus<d.numOutputs;++bus)for(unsigned ch=0;ch<channels[bus];++ch)
                if(buffers[bus][ch]&&buffers[bus][ch][i]!=T(0))silence[bus]&=~(uint64(1)<<ch);
        }
        for(int32 bus=0;bus<d.numOutputs;++bus)d.outputs[bus].silenceFlags=silence[bus];
        return kResultOk;
    }
public:
    Processor(){setControllerClass(controllerID);}
    static FUnknown* create(void*){return static_cast<IAudioProcessor*>(new Processor);}
    tresult PLUGIN_API initialize(FUnknown* ctx) override {
        const auto r=AudioEffect::initialize(ctx);if(r!=kResultOk)return r;
        addAudioOutput(STR16("Output"),SpeakerArr::kStereo);
        addAudioOutput(STR16("Latch stem"),SpeakerArr::kMono,kAux,0);
        addAudioOutput(STR16("Pause stem"),SpeakerArr::kMono,kAux,0);
        addAudioOutput(STR16("Snapshot stem"),SpeakerArr::kMono,kAux,0);
        addEventInput(STR16("Notes"),16);return kResultOk;
    }
    tresult PLUGIN_API setBusArrangements(SpeakerArrangement* in,int32 ni,SpeakerArrangement* out,int32 no) override {
        if(ni!=0||no<1||no>4||!out||(out[0]!=SpeakerArr::kMono&&out[0]!=SpeakerArr::kStereo))return kResultFalse;
        for(int32 i=1;i<no;++i)if(out[i]!=SpeakerArr::kMono)return kResultFalse;
        return AudioEffect::setBusArrangements(in,ni,out,no);
    }
    tresult PLUGIN_API canProcessSampleSize(int32 size) override{return size==kSample32||size==kSample64?kResultTrue:kResultFalse;}
    tresult PLUGIN_API setupProcessing(ProcessSetup& setup) override {
        if(!std::isfinite(setup.sampleRate)||setup.sampleRate<1000||setup.sampleRate>2000000)return kResultFalse;
        const auto r=AudioEffect::setupProcessing(setup);if(r==kResultOk){sr=setup.sampleRate;engine.prepare(sr);}return r;
    }
    tresult PLUGIN_API setActive(TBool active) override {const auto r=AudioEffect::setActive(active);if(r==kResultOk)engine.reset();return r;}
    tresult PLUGIN_API setProcessing(TBool active) override {if(!active)engine.reset();return kResultOk;}
    uint32 PLUGIN_API getLatencySamples() override{return 0;}
    uint32 PLUGIN_API getTailSamples() override{return uint32(std::ceil(sr*.041));}
    tresult PLUGIN_API setState(IBStream* s) override {winters::integrated::Params p{};if(!readParams(s,p))return kResultFalse;engine.restore(p);return kResultOk;}
    tresult PLUGIN_API getState(IBStream* s) override {if(!s)return kResultFalse;auto bytes=winters::integrated::encode(engine.parameters());int32 n=0;return s->write(bytes.data(),int32(bytes.size()),&n)==kResultOk&&n==int32(bytes.size())?kResultOk:kResultFalse;}
    tresult PLUGIN_API process(ProcessData& d) override {
        if(d.numSamples<0||d.numInputs!=0||d.numOutputs<0||d.numOutputs>4)return kResultFalse;
        Cursors c{};
        if(d.inputParameterChanges)for(int32 i=0;i<d.inputParameterChanges->getParameterCount();++i){
            auto* q=d.inputParameterChanges->getParameterData(i);if(!q)continue;
            auto id=q->getParameterId();if(id>=firstID&&id<firstID+winters::integrated::Count&&!c[id-firstID].queue)c[id-firstID].init(q);
        }
        if(d.numSamples==0){for(unsigned k=0;k<winters::integrated::Count;++k)c[k].apply(engine,k,0,true);return kResultOk;}
        Events ev(d.inputEvents);
        if(d.numOutputs==0){for(int32 i=0;i<d.numSamples;++i)step(c,ev,i);return kResultOk;}
        if(!d.outputs)return kResultFalse;
        if(d.symbolicSampleSize==kSample32)return audio<Sample32>(d,c,ev);
        if(d.symbolicSampleSize==kSample64)return audio<Sample64>(d,c,ev);
        return kResultFalse;
    }
};
class Controller final: public EditController {
public:
    static FUnknown* create(void*){return static_cast<IEditController*>(new Controller);}
    tresult PLUGIN_API initialize(FUnknown* ctx) override {
        const auto r=EditController::initialize(ctx);if(r!=kResultOk)return r;
        auto add=[&](const TChar* n,unsigned i,int32 steps=0){parameters.addParameter(n,nullptr,steps,winters::integrated::defaults[i],ParameterInfo::kCanAutomate,firstID+i);};
        add(STR16("Bank slot 1"),0,3);add(STR16("Bank slot 2"),1,3);add(STR16("Bank slot 3"),2,3);add(STR16("Bank slot 4"),3,3);
        add(STR16("Hold"),4,1);add(STR16("Tick (rising edge)"),5,1);add(STR16("Internal clock"),6,1);add(STR16("Clock (0.5-8 Hz)"),7);
        add(STR16("Latch gain"),8);add(STR16("Pause gain"),9);add(STR16("Snapshot gain"),10);
        add(STR16("Timbre slot 1"),11);add(STR16("Timbre slot 2"),12);add(STR16("Timbre slot 3"),13);add(STR16("Timbre slot 4"),14);
        add(STR16("Timbre hold"),15,1);add(STR16("Timbre tick (edge)"),16,1);add(STR16("Timbre clock"),17,1);add(STR16("Timbre speed (0.5-8 Hz)"),18);
        return kResultOk;
    }
    tresult PLUGIN_API setComponentState(IBStream* s) override {winters::integrated::Params p{};if(!readParams(s,p))return kResultFalse;for(unsigned i=0;i<winters::integrated::Count;++i)setParamNormalized(firstID+i,p[i]);return kResultOk;}
};
}
BEGIN_FACTORY_DEF("MHAC","https://github.com/techrote/MachineHumanAudioCybersemiotics","")
DEF_CLASS2(INLINE_UID_FROM_FUID(processorID),PClassInfo::kManyInstances,kVstAudioEffectClass,
"MHAC Three Winters",Vst::kDistributable,"Instrument|Synth","0.2.0",kVstVersionString,Processor::create)
DEF_CLASS2(INLINE_UID_FROM_FUID(controllerID),PClassInfo::kManyInstances,kVstComponentControllerClass,
"MHAC Three Winters Controller",0,"","0.2.0",kVstVersionString,Controller::create)
END_FACTORY
