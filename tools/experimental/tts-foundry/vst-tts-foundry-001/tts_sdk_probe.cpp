#include "public.sdk/source/vst/hosting/module.h"
#include "public.sdk/source/vst/hosting/hostclasses.h"
#include "public.sdk/source/vst/hosting/parameterchanges.h"
#include "public.sdk/source/vst/hosting/eventlist.h"
#include "public.sdk/source/common/memorystream.h"
#include "pluginterfaces/vst/ivstaudioprocessor.h"
#include "pluginterfaces/vst/ivstcomponent.h"
#include "pluginterfaces/vst/vstspeaker.h"
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <vector>
using namespace Steinberg;
using namespace Steinberg::Vst;
namespace {
void require(bool b,const char* where){if(!b)throw std::runtime_error(where);}void ok(tresult r,const char* where){if(r!=kResultOk)throw std::runtime_error(std::string(where)+" result="+std::to_string(r));}
std::vector<std::uint8_t> save(IComponent* c){MemoryStream s;ok(c->getState(&s),"getState");require(s.getSize()>0&&s.getSize()<65536,"state size");auto* p=reinterpret_cast<const std::uint8_t*>(s.getData());return {p,p+s.getSize()};}
void restore(IComponent* c,const std::vector<std::uint8_t>& b){MemoryStream s(const_cast<std::uint8_t*>(b.data()),TSize(b.size()));ok(c->setState(&s),"setState");}
}
int main(int argc,char** argv){
    try{
        require(argc==3,"usage: mhac_tts_sdk_probe bundle first-param-id");const ParamID first=ParamID(std::stoul(argv[2]));auto host=owned(new HostApplication);std::string err;
        auto module=VST3::Hosting::Module::create(argv[1],err);if(!module)throw std::runtime_error(err);const auto& factory=module->getFactory();factory.setHostContext(host.get());
        for(const auto& info:factory.classInfos())if(info.category()==kVstAudioEffectClass){
            auto c=factory.createInstance<IComponent>(info.ID());require(bool(c),"component");FUnknownPtr<IAudioProcessor> proc(c.get());require(proc.getInterface()!=nullptr,"processor");ok(c->initialize(host.get()),"initialize");
            require(c->getBusCount(kAudio,kInput)==0,"unexpected audio input");require(c->getBusCount(kAudio,kOutput)==1,"output count");require(c->getBusCount(kEvent,kInput)==1,"event input");
            SpeakerArrangement out=SpeakerArr::kStereo;ok(proc->setBusArrangements(nullptr,0,&out,1),"arrangement");ok(c->activateBus(kAudio,kOutput,0,true),"activate audio");ok(c->activateBus(kEvent,kInput,0,true),"activate events");
            ProcessSetup setup{kRealtime,kSample32,128,48000.};ok(proc->setupProcessing(setup),"setup");ok(c->setActive(true),"active");ok(proc->setProcessing(true),"processing");
            const auto original=save(c.get());ParameterChanges changes(1);int32 qi=0,pi=0;auto* q=changes.addParameterData(first,qi);require(q,"param queue");ok(q->addPoint(0,.731,pi),"param point");ProcessData flush{};flush.processMode=kRealtime;flush.symbolicSampleSize=kSample32;flush.inputParameterChanges=&changes;ok(proc->process(flush),"flush");const auto changed=save(c.get());require(changed!=original,"state did not change");restore(c.get(),original);require(save(c.get())==original,"restore roundtrip");
            std::vector<float> l(128),r(128);float* ptr[]{l.data(),r.data()};AudioBusBuffers bus{};bus.numChannels=2;bus.channelBuffers32=ptr;EventList events;events.setMaxSize(8);Event e{};e.type=Event::kNoteOnEvent;e.sampleOffset=0;e.busIndex=0;e.noteOn.channel=0;e.noteOn.pitch=60;e.noteOn.velocity=.8f;e.noteOn.noteId=1;require(events.addEvent(e)==kResultOk,"note event");
            ProcessData d{};d.processMode=kRealtime;d.symbolicSampleSize=kSample32;d.numSamples=128;d.numInputs=0;d.numOutputs=1;d.outputs=&bus;d.inputEvents=&events;double energy=0;unsigned nonzero=0;
            for(unsigned block=0;block<256;++block){bus.silenceFlags=0;ok(proc->process(d),"audio process");for(unsigned i=0;i<128;++i){require(std::isfinite(l[i])&&std::isfinite(r[i]),"nonfinite audio");require(std::abs(l[i])<=1.01f&&std::abs(r[i])<=1.01f,"unbounded audio");energy+=double(l[i])*l[i]+double(r[i])*r[i];if(l[i]!=0||r[i]!=0)++nonzero;}events.clear();}
            require(energy>1e-5&&nonzero>128,"silent host render");Event off{};off.type=Event::kNoteOffEvent;off.sampleOffset=0;off.busIndex=0;off.noteOff.channel=0;off.noteOff.pitch=60;off.noteOff.velocity=0;off.noteOff.noteId=1;require(events.addEvent(off)==kResultOk,"off event");ok(proc->process(d),"note off process");events.clear();
            ok(proc->setProcessing(false),"stop");ok(c->setActive(false),"deactivate");ok(c->terminate(),"terminate");std::cout<<"VST_TTS_HOST_PASS name="<<info.name()<<" energy="<<energy<<" nonzero="<<nonzero<<" state_bytes="<<original.size()<<"\n";return 0;
        }
        throw std::runtime_error("no audio component");
    }catch(const std::exception& e){std::cerr<<"VST_TTS_HOST_FAIL "<<e.what()<<"\n";return 1;}
}
