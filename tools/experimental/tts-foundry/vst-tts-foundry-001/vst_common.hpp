#pragma once
#include "state.hpp"
#include "../../vst-mainline/state_bridge.hpp"
#include "public.sdk/source/vst/vstaudioeffect.h"
#include "public.sdk/source/vst/vsteditcontroller.h"
#include "public.sdk/source/vst/vstparameters.h"
#include "pluginterfaces/base/ibstream.h"
#include "pluginterfaces/vst/ivstevents.h"
#include "pluginterfaces/vst/ivstparameterchanges.h"
#include <array>
#include <type_traits>

namespace mhac::tts::vst {
using namespace Steinberg;
using namespace Steinberg::Vst;

template<std::size_t Bytes>
inline bool read_state(IBStream* s,std::array<std::uint8_t,Bytes>& b){int32 n=0;return s&&s->read(b.data(),int32(b.size()),&n)==kResultOk&&n==int32(b.size());}
template<std::size_t Bytes>
inline tresult write_state(IBStream* s,const std::array<std::uint8_t,Bytes>& b){if(!s)return kResultFalse;int32 n=0;return s->write(b.data(),int32(b.size()),&n)==kResultOk&&n==int32(b.size())?kResultOk:kResultFalse;}

struct ParamCursor {
    IParamValueQueue* q=nullptr;int32 index=0,count=0,offset=0;ParamValue value=0;bool pending=false;
    void next(){pending=false;while(index<count){if(q->getPoint(index++,offset,value)==kResultTrue){pending=true;break;}}}
    void init(IParamValueQueue* queue){q=queue;count=q->getPointCount();next();}
};

struct EventCursor {
    IEventList* list=nullptr;int32 index=0,count=0;Event event{};bool pending=false;
    explicit EventCursor(IEventList* l):list(l),count(l?l->getEventCount():0){next();}
    void next(){pending=false;while(index<count){if(list->getEvent(index++,event)==kResultOk){pending=true;break;}}}
};

template<class Engine,class ParamApply>
inline void apply_events(EventCursor& e,Engine& engine,int32 sample,ParamApply){
    while(e.pending&&e.event.sampleOffset<=sample){
        if(e.event.sampleOffset>=0&&e.event.busIndex==0){
            if(e.event.type==Event::kNoteOnEvent){const auto& n=e.event.noteOn;if(n.velocity>0)engine.note_on(double(n.pitch)+double(n.tuning)/100.0,n.velocity);else engine.note_off();}
            else if(e.event.type==Event::kNoteOffEvent)engine.note_off();
        }
        e.next();
    }
}

template<class T,class Engine>
inline tresult render_mono_to_host(ProcessData& d,Engine& engine,T** out){
    if(!out||d.outputs[0].numChannels<1||d.outputs[0].numChannels>2)return kResultFalse;const int32 channels=d.outputs[0].numChannels;
    for(int32 c=0;c<channels;++c)if(!out[c])return kResultFalse;bool silent=true;
    for(int32 i=0;i<d.numSamples;++i){const T y=T(engine.tick());silent&=y==T(0);for(int32 c=0;c<channels;++c)out[c][i]=y;}
    d.outputs[0].silenceFlags=silent?((uint64(1)<<channels)-1):0;return kResultOk;
}

} // namespace mhac::tts::vst
