#pragma once
#include "trace_bell.hpp"
#include <cstdint>
#include <cstring>
#include <limits>

namespace mhac::accel {
// Stable candidate parameter IDs; no VST class IDs assigned yet.
enum class TraceParam : uint32_t { Pitch=0, Decay=1, Contrast=2, Mix=3, Spread=4, Bypass=5 };
using TraceState = std::array<uint8_t,32>;
static_assert(sizeof(float)==4 && std::numeric_limits<float>::is_iec559,"binary32 required");
inline bool validTracePatch(const TracePatch& p) noexcept {
    const auto in=[](float x,float lo,float hi){return std::isfinite(x)&&x>=lo&&x<=hi;};
    return in(p.pitch,80,500)&&in(p.decay,.03f,1.2f)&&in(p.contrast,0,1)&&in(p.mix,0,1)&&in(p.spread,0,1);
}
inline bool encodeTraceState(const TracePatch& p,TraceState& out) noexcept {
    if(!validTracePatch(p)) return false;
    TraceState s{{'T','B','0','1',1,0,0,0}};
    const float values[]={p.pitch,p.decay,p.contrast,p.mix,p.spread};
    for(unsigned i=0;i<5;++i){uint32_t u;std::memcpy(&u,&values[i],4);for(unsigned j=0;j<4;++j)s[8+4*i+j]=uint8_t(u>>(8*j));}
    s[28]=p.bypass?1:0;out=s;return true;
}
inline bool decodeTraceState(const uint8_t* s,size_t n,TracePatch& out) noexcept {
    if(!s||n!=32||s[0]!='T'||s[1]!='B'||s[2]!='0'||s[3]!='1'||s[4]!=1||s[5]||s[6]||s[7]||s[28]>1||s[29]||s[30]||s[31])return false;
    float v[5];for(unsigned i=0;i<5;++i){uint32_t u=0;for(unsigned j=0;j<4;++j)u|=uint32_t(s[8+4*i+j])<<(8*j);std::memcpy(&v[i],&u,4);}
    TracePatch p{v[0],v[1],v[2],v[3],v[4],s[28]!=0};if(!validTracePatch(p))return false;out=p;return true;
}
inline bool applyTraceNormalized(TracePatch& patch,uint32_t id,double value) noexcept {
        if(!std::isfinite(value)||value<0||value>1)return false;
        TracePatch p=patch;const float v=float(value);
        switch(static_cast<TraceParam>(id)){
        case TraceParam::Pitch:p.pitch=80.f+420.f*v;break;
        case TraceParam::Decay:p.decay=v==1.f?1.2f:.03f+(1.2f-.03f)*v;break;
        case TraceParam::Contrast:p.contrast=v;break;
        case TraceParam::Mix:p.mix=v;break;
        case TraceParam::Spread:p.spread=v;break;
        case TraceParam::Bypass:p.bypass=value>=.5;break;
        default:return false;
        }patch=p;return true;
    }
// Single audio owner; adapter dispatches events at exact sample boundaries.
// State is parameter-only; no resonator history is serialized.
class TraceBellPerformance {
    TraceBell core_{};TracePatch patch_{};
    unsigned fadeSamples_=480,remaining_=0;
    float dry_=0,step_=0,target_=0;
    static float clean(float x) noexcept {return std::isfinite(x)?std::clamp(x,-1.f,1.f):0.f;}
    void targetBypass(bool bypass) noexcept {
        const float next=bypass?1.f:0.f;if(next==target_)return;
        target_=next;remaining_=fadeSamples_;step_=(target_-dry_)/float(remaining_);
    }
public:
    TraceBellPerformance() noexcept {core_.setTuningSmoothing(true);}
    const TracePatch& patch()const noexcept{return patch_;}
    bool prepare(float rate) noexcept {if(!core_.prepare(rate))return false;fadeSamples_=std::max(1u,unsigned(std::ceil(rate*.01f)));reset();return true;}
    void reset() noexcept {core_.reset();dry_=target_=patch_.bypass?1.f:0.f;step_=0;remaining_=0;}
    bool configure(TracePatch p) noexcept {
        if(!validTracePatch(p))return false;
        TracePatch wet=p;wet.bypass=false;
        if(p.pitch!=patch_.pitch||p.decay!=patch_.decay||p.contrast!=patch_.contrast||p.mix!=patch_.mix||p.spread!=patch_.spread){if(!core_.configure(wet))return false;}
        patch_=p;targetBypass(p.bypass);return true;
    }
    bool setNormalized(uint32_t id,double value) noexcept {
        TracePatch p=patch_;return applyTraceNormalized(p,id,value)&&configure(p);
    }
    bool save(TraceState& out)const noexcept{return encodeTraceState(patch_,out);}
    bool restore(const uint8_t* s,size_t n)noexcept{TracePatch p;return decodeTraceState(s,n,p)&&configure(p);}
    TraceFrame process(TraceFrame in)noexcept{
        in={clean(in.l),clean(in.r)};const auto wet=core_.process(in);
        if(remaining_){if(--remaining_==0)dry_=target_;else dry_=std::clamp(dry_+step_,0.f,1.f);}
        if(dry_==1.f)return in;
        if(dry_==0.f)return wet;
        return {clean(wet.l+dry_*(in.l-wet.l)),clean(wet.r+dry_*(in.r-wet.r))};
    }
};
} // namespace mhac::accel
