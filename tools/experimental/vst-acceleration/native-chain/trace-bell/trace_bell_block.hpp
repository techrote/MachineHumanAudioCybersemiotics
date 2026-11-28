#pragma once
#include "trace_bell_state.hpp"

namespace mhac::accel {
struct TraceEvent { uint32_t offset,id; double normalized; };
// Host-independent stereo block bridge. Sorted sample-offset events; duplicates
// at one offset are legal (last wins). All same-offset changes commit together.
// For zero-frame parameter flush only, offset 0 is valid and buffers may be null.
// Normal planar or matching in-place buffers; cross-channel overlap unsupported.
// Caller owns buffers and event memory; no allocation, locks or I/O here.
inline bool processTraceBlock(TraceBellPerformance& engine,
    const float* left,const float* right,float* outL,float* outR,
    uint32_t frames,const TraceEvent* events,size_t count) noexcept {
    if((frames&&(!left||!right||!outL||!outR))||(!events&&count)||
       uint64_t(count)>6ull*std::max(1u,frames))return false;
    // Preflight prevents a malformed event from partially processing a block.
    TracePatch probe=engine.patch();
    for(size_t i=0;i<count;++i){
        const auto& e=events[i];
        if(e.offset>=std::max(1u,frames)||(i&&e.offset<events[i-1].offset)||
           !applyTraceNormalized(probe,e.id,e.normalized))return false;
    }
    size_t cursor=0;
    const auto apply=[&](uint32_t offset){
        if(cursor==count||events[cursor].offset!=offset)return;
        TracePatch p=engine.patch();
        do{const auto& e=events[cursor++];applyTraceNormalized(p,e.id,e.normalized);}
        while(cursor<count&&events[cursor].offset==offset);
        engine.configure(p);
    };
    if(!frames){apply(0);return true;}
    for(uint32_t i=0;i<frames;++i){
        apply(i);const auto y=engine.process({left[i],right[i]});outL[i]=y.l;outR[i]=y.r;
    }
    return true;
}
} // namespace mhac::accel
