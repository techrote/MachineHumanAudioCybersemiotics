#pragma once
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>

namespace mhac::accel {
struct ShuttleFrame { float l=0, r=0; };
struct ShuttlePatch {
    uint16_t mix=350, reverse=750, feedback=250, cross=500;
    bool bypass=false;
};
using ShuttleState=std::array<uint8_t,13>;
inline bool valid(ShuttlePatch p) noexcept {
    return p.mix<=1000 && p.reverse<=1000 && p.feedback<=1000 && p.cross<=1000;
}
inline ShuttleState encode(ShuttlePatch p) noexcept {
    ShuttleState s={'P','S','0','1'};
    const uint16_t values[]={p.mix,p.reverse,p.feedback,p.cross};
    for(unsigned i=0;i<4;++i) { s[4+2*i]=uint8_t(values[i]); s[5+2*i]=uint8_t(values[i]>>8); }
    s[12]=uint8_t(p.bypass); return s;
}
inline bool decode(const ShuttleState& s,ShuttlePatch& out) noexcept {
    if(s[0]!='P'||s[1]!='S'||s[2]!='0'||s[3]!='1'||s[12]>1) return false;
    auto word=[&](unsigned i){return uint16_t(unsigned(s[i])|(unsigned(s[i+1])<<8));};
    const ShuttlePatch p{word(4),word(6),word(8),word(10),s[12]!=0};
    if(!valid(p)) return false;
    out=p; return true;
}
// Two overlapping reverse grains, forward reference, convex stereo feedback.
// Owner-thread only. prepare/reset are not real-time calls. No process allocation.
// MaxGrain=2048 supports 24 kHz; the default supports 192 kHz.
template<unsigned MaxGrain=15360> class PalimpsestShuttle {
    static_assert(MaxGrain>=2 && MaxGrain<=15360);
    std::array<ShuttleFrame,2*MaxGrain> ring_{};
    unsigned grain_=0, pos_=0, phase_=0;
    ShuttlePatch patch_{};
    float alpha_=1, inv_=0, mix_=0, reverse_=0, feedback_=0, cross_=0;
    static float clean(float x) noexcept {
        return std::isfinite(x)&&std::abs(x)>=1.e-20f?std::clamp(x,-1.f,1.f):0.f;
    }
    static float blend(float a,float b,float w) noexcept { return a+(b-a)*w; }
    static ShuttleFrame blend(ShuttleFrame a,ShuttleFrame b,float w) noexcept {
        return {blend(a.l,b.l,w),blend(a.r,b.r,w)};
    }
    void smooth(float& x,float target) noexcept {
        x=std::abs(x-target)<1.e-7f?target:x+alpha_*(target-x);
    }
    ShuttleFrame read(unsigned delay) const noexcept {
        return ring_[pos_>=delay?pos_-delay:pos_+2*grain_-delay];
    }
public:
    bool prepare(unsigned rate) noexcept {
        if(rate<8000||rate>192000) return false;
        const unsigned g=(rate*80u/1000u+1u)&~1u;
        if(g>MaxGrain) return false;
        grain_=g; inv_=2.f/float(g); alpha_=1.f-std::exp(-1.f/(.01f*float(rate)));
        reset(); return true;
    }
    unsigned grainSamples() const noexcept { return grain_; }
    bool configure(ShuttlePatch p) noexcept {
        if(!valid(p)) return false;
        patch_=p; return true;
    }
    ShuttlePatch patch() const noexcept { return patch_; }
    void reset() noexcept {
        std::fill_n(ring_.begin(),2*grain_,ShuttleFrame{}); pos_=phase_=0;
        mix_=patch_.mix*.001f; reverse_=patch_.reverse*.001f;
        feedback_=patch_.feedback*.00065f; cross_=patch_.cross*.001f;
    }
    ShuttleFrame process(ShuttleFrame in) noexcept {
        in={clean(in.l),clean(in.r)};
        if(!grain_) return in;
        smooth(mix_,patch_.mix*.001f); smooth(reverse_,patch_.reverse*.001f);
        smooth(feedback_,patch_.feedback*.00065f); smooth(cross_,patch_.cross*.001f);
        const unsigned h=grain_/2, p=phase_, q=p<h?p+h:p-h;
        const float w=float(std::min(p,grain_-p))*inv_;
        const auto rev=blend(read(2*q+1),read(2*p+1),w);
        const auto wet=blend(read(grain_),rev,reverse_);
        const auto loop=blend(wet,ShuttleFrame{wet.r,wet.l},cross_);
        ring_[pos_]={clean(blend(in.l,loop.l,feedback_)),clean(blend(in.r,loop.r,feedback_))};
        if(++pos_==2*grain_) pos_=0;
        if(++phase_==grain_) phase_=0;
        if(patch_.bypass) return in;
        return {clean(blend(in.l,wet.l,mix_)),clean(blend(in.r,wet.r,mix_))};
    }
};
} // namespace mhac::accel
