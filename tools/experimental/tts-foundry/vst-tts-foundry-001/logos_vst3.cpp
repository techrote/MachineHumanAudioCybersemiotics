#include "vst_common.hpp"
#include "public.sdk/source/main/pluginfactory.h"
#include <algorithm>
#include <array>
#include <cmath>

using namespace Steinberg;
using namespace Steinberg::Vst;
namespace {
using namespace mhac::tts;
using namespace mhac::tts::vst;
const FUID processorID(0xE3B14C6F,0x32DA44F1,0xA221D983,0x6F4AC587);
const FUID controllerID(0x8D4750C2,0xB91E4F36,0xA3F7C012,0x5EDE2B9A);
constexpr ParamID firstID=2100;
constexpr unsigned count=7;

class Processor final: public AudioEffect {
    Logos engine_{};
    LogosPatch patch_=logosDefaults;
    mhac::mainline::StateBridge<LogosPatch> state_{logosDefaults};
    std::array<PhrasePlan,8> programs_{};
    double sr_=48000.0;

    void apply_patch(const LogosPatch& p) noexcept {
        patch_=p;engine_.set_parameters(logos_parameters(patch_));engine_.set_plan(programs_[phrase_index(patch_[5])]);
    }
    void apply_parameter(unsigned i,ParamValue v) noexcept {
        if(i>=count)return;patch_[i]=unit(float(v));
        if(i==5)engine_.set_plan(programs_[phrase_index(patch_[5])]);else engine_.set_parameters(logos_parameters(patch_));
    }
    void apply_pending() noexcept {LogosPatch p{};if(state_.take(p))apply_patch(p);}
    void publish() noexcept {state_.publish(patch_);}
    using Cursors=std::array<ParamCursor,count>;
    void parameters(Cursors& c,int32 sample,bool flush=false) noexcept {
        for(unsigned i=0;i<count;++i)while(c[i].pending&&(flush||c[i].offset<=sample)){apply_parameter(i,c[i].value);c[i].next();}
    }
    void events(EventCursor& e,int32 sample) noexcept {
        while(e.pending&&e.event.sampleOffset<=sample){
            if(e.event.sampleOffset>=0&&e.event.busIndex==0){
                if(e.event.type==Event::kNoteOnEvent){const auto& n=e.event.noteOn;if(n.velocity>0)engine_.note_on(double(n.pitch)+double(n.tuning)/100.0,n.velocity);else engine_.note_off();}
                else if(e.event.type==Event::kNoteOffEvent)engine_.note_off();
            }e.next();
        }
    }
    template<class T> tresult audio(ProcessData& d,Cursors& c,EventCursor& ev){
        auto& bus=d.outputs[0];auto* info=getAudioOutput(0);if(!info)return kResultFalse;
        const int32 channels=bus.numChannels;if(channels<0||channels>2)return kResultFalse;
        T** out=nullptr;if constexpr(std::is_same_v<T,Sample32>)out=bus.channelBuffers32;else out=bus.channelBuffers64;
        std::array<T*,2> ptr{};uint64 silence=channels?((uint64(1)<<channels)-1):0;
        for(int32 ch=0;ch<channels;++ch){if(info->isActive()&&(!out||!out[ch]))return kResultFalse;if(out)ptr[ch]=out[ch];if(!info->isActive()&&ptr[ch])std::fill_n(ptr[ch],d.numSamples,T(0));}
        engine_.begin_block();
        for(int32 i=0;i<d.numSamples;++i){parameters(c,i);events(ev,i);const T y=T(engine_.tick());for(int32 ch=0;ch<channels;++ch)if(info->isActive()&&ptr[ch]){ptr[ch][i]=y;if(y!=T(0))silence&=~(uint64(1)<<ch);}}
        bus.silenceFlags=silence;return kResultOk;
    }
public:
    Processor(){setControllerClass(controllerID);for(unsigned i=0;i<programs_.size();++i)programs_[i]=phrase_program(i);apply_patch(patch_);}
    static FUnknown* create(void*){return static_cast<IAudioProcessor*>(new Processor);}
    tresult PLUGIN_API initialize(FUnknown* ctx) override {const auto r=AudioEffect::initialize(ctx);if(r!=kResultOk)return r;addAudioOutput(STR16("Output"),SpeakerArr::kStereo);addEventInput(STR16("Notes"),16);return kResultOk;}
    tresult PLUGIN_API setBusArrangements(SpeakerArrangement* in,int32 ni,SpeakerArrangement* out,int32 no) override {if(ni!=0||no!=1||!out||(out[0]!=SpeakerArr::kMono&&out[0]!=SpeakerArr::kStereo))return kResultFalse;return AudioEffect::setBusArrangements(in,ni,out,no);}
    tresult PLUGIN_API canProcessSampleSize(int32 size) override{return size==kSample32||size==kSample64?kResultTrue:kResultFalse;}
    tresult PLUGIN_API setupProcessing(ProcessSetup& setup) override {if(!valid_rate(setup.sampleRate))return kResultFalse;const auto r=AudioEffect::setupProcessing(setup);if(r==kResultOk){sr_=setup.sampleRate;apply_pending();if(!engine_.prepare(sr_))return kResultFalse;apply_patch(patch_);publish();}return r;}
    tresult PLUGIN_API setActive(TBool active) override {const auto r=AudioEffect::setActive(active);if(r==kResultOk){apply_pending();engine_.reset();apply_patch(patch_);publish();}return r;}
    tresult PLUGIN_API setProcessing(TBool active) override {if(!active)engine_.reset();return kResultOk;}
    uint32 PLUGIN_API getLatencySamples() override{return 0;}
    uint32 PLUGIN_API getTailSamples() override{return 0;}
    tresult PLUGIN_API setState(IBStream* s) override {StateBytes<7> b{};LogosPatch p{};if(!read_state(s,b)||!decode_logos(b,p))return kResultFalse;state_.request(p);return kResultOk;}
    tresult PLUGIN_API getState(IBStream* s) override {return write_state(s,encode_logos(state_.snapshot()));}
    tresult PLUGIN_API process(ProcessData& d) override {
        if(d.numSamples<0||d.numInputs!=0||d.numOutputs<0||d.numOutputs>1||(d.numOutputs&&!d.outputs))return kResultFalse;
        if(d.inputEvents&&(d.inputEvents->getEventCount()<0||d.inputEvents->getEventCount()>4096))return kResultFalse;
        apply_pending();struct Publish{Processor& p;~Publish(){p.publish();}} publishGuard{*this};
        Cursors c{};if(d.inputParameterChanges){const auto n=d.inputParameterChanges->getParameterCount();if(n<0||n>4096)return kResultFalse;for(int32 i=0;i<n;++i){auto* q=d.inputParameterChanges->getParameterData(i);if(!q)continue;const auto id=q->getParameterId();if(id>=firstID&&id<firstID+count&&!c[id-firstID].q){if(q->getPointCount()<0||q->getPointCount()>4096)return kResultFalse;c[id-firstID].init(q);}}}
        if(d.numSamples==0){parameters(c,0,true);return kResultOk;}EventCursor ev(d.inputEvents);
        if(d.numOutputs==0){engine_.begin_block();for(int32 i=0;i<d.numSamples;++i){parameters(c,i);events(ev,i);(void)engine_.tick();}return kResultOk;}
        if(d.symbolicSampleSize==kSample32)return audio<Sample32>(d,c,ev);if(d.symbolicSampleSize==kSample64)return audio<Sample64>(d,c,ev);return kResultFalse;
    }
};

class Controller final: public EditController {
public:
    static FUnknown* create(void*){return static_cast<IEditController*>(new Controller);}
    tresult PLUGIN_API initialize(FUnknown* ctx) override {const auto r=EditController::initialize(ctx);if(r!=kResultOk)return r;
        parameters.addParameter(STR16("Pitch (-24..24 st)"),nullptr,0,logosDefaults[0],ParameterInfo::kCanAutomate,firstID+0);
        parameters.addParameter(STR16("Speech rate"),nullptr,0,logosDefaults[1],ParameterInfo::kCanAutomate,firstID+1);
        parameters.addParameter(STR16("Whisper"),nullptr,0,logosDefaults[2],ParameterInfo::kCanAutomate,firstID+2);
        parameters.addParameter(STR16("Formant shift"),nullptr,0,logosDefaults[3],ParameterInfo::kCanAutomate,firstID+3);
        parameters.addParameter(STR16("Articulation"),nullptr,0,logosDefaults[4],ParameterInfo::kCanAutomate,firstID+4);
        auto* phrase=new StringListParameter(STR16("Phrase program"),firstID+5);phrase->appendString(STR16("Machine voice"));phrase->appendString(STR16("Hello world"));phrase->appendString(STR16("Word grows mouth"));phrase->appendString(STR16("Signal becomes song"));phrase->appendString(STR16("Artificial articulation"));phrase->appendString(STR16("Uncertain source"));phrase->appendString(STR16("Sound poetry"));phrase->appendString(STR16("Speak in circuits"));parameters.addParameter(phrase);
        parameters.addParameter(STR16("Gain"),nullptr,0,logosDefaults[6],ParameterInfo::kCanAutomate,firstID+6);return kResultOk;}
    tresult PLUGIN_API setComponentState(IBStream* s) override {StateBytes<7> b{};LogosPatch p{};if(!read_state(s,b)||!decode_logos(b,p))return kResultFalse;for(unsigned i=0;i<count;++i)setParamNormalized(firstID+i,p[i]);return kResultOk;}
};
}
BEGIN_FACTORY_DEF("MHAC","https://github.com/techrote/MachineHumanAudioCybersemiotics","")
DEF_CLASS2(INLINE_UID_FROM_FUID(processorID),PClassInfo::kManyInstances,kVstAudioEffectClass,"MHAC LOGOS",Vst::kDistributable,"Instrument|Synth","0.1.0",kVstVersionString,Processor::create)
DEF_CLASS2(INLINE_UID_FROM_FUID(controllerID),PClassInfo::kManyInstances,kVstComponentControllerClass,"MHAC LOGOS Controller",0,"","0.1.0",kVstVersionString,Controller::create)
END_FACTORY
