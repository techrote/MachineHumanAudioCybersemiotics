#pragma once
#include <algorithm>
#include <array>
#include <cmath>

namespace mhac::accel {
struct TraceFrame { float l, r; };
struct TracePatch {
    float pitch = 220.f, decay = .35f, contrast = .8f, mix = .3f, spread = .5f;
    bool bypass = false;
};
// Creative exaptation: transient contrast opens a bank of pitched memories.
// All control calls and process() belong to one audio owner. No shared state.
class TraceBell {
    struct Mode { float u=0, v=0, a=0, b=0; };
    struct Lane { float fast=0, slow=0; std::array<Mode,4> modes{}; };
    std::array<Lane,2> lanes_{};
    TracePatch patch_{};
    float rate_=48000, fast_=0, slow_=0, smooth_=0, inject_=0;
    float wet_=.3f, contrast_=.8f;
    static float clean(float x) noexcept {
        return std::isfinite(x) ? std::clamp(x,-1.f,1.f) : 0.f;
    }
    static float tiny(float x) noexcept { return std::abs(x)<1.e-20f ? 0.f : x; }
    static bool in(float x,float lo,float hi) noexcept {
        return std::isfinite(x) && x>=lo && x<=hi;
    }
    float lane(Lane& s,float x) noexcept {
        const float level=std::abs(x);
        s.fast=tiny(s.fast+fast_*(level-s.fast));
        s.slow=tiny(s.slow+slow_*(level-s.slow));
        const float novelty=std::clamp((s.fast-s.slow)/(s.fast+s.slow+.001f),0.f,1.f);
        const float drive=inject_*x*((1.f-contrast_)+contrast_*novelty);
        float sum=0;
        for(auto& m:s.modes) {
            float u=m.a*m.u-m.b*m.v+drive, v=m.b*m.u+m.a*m.v;
            // Bounded nonlinear radial compression; preserve quadrature phase.
            const float peak=std::max(std::abs(u),std::abs(v));
            if(peak>.5f) { const float scale=.5f/peak; u*=scale; v*=scale; }
            m.u=tiny(u); m.v=tiny(v); sum+=m.u;
        }
        return sum*.5f;
    }
public:
    TraceBell() noexcept { prepare(48000.f); }
    bool prepare(float rate) noexcept {
        if(!in(rate,8000.f,192000.f)) return false;
        rate_=rate;
        fast_=1.f-std::exp(-1.f/(.004f*rate));
        slow_=1.f-std::exp(-1.f/(.15f*rate));
        smooth_=1.f-std::exp(-1.f/(.01f*rate));
        inject_=1200.f/rate;
        configure(patch_); reset(); return true;
    }
    // Transactional validation; coefficient changes preserve existing memory.
    // Call on the owning thread at a control/event boundary, not per sample.
    bool configure(TracePatch p) noexcept {
        if(!in(p.pitch,80,500)||!in(p.decay,.03f,1.2f)||!in(p.contrast,0,1)
           ||!in(p.mix,0,1)||!in(p.spread,0,1)) return false;
        patch_=p;
        constexpr float ratios[]={1.f,1.5f,2.125f,3.25f};
        const float radius=std::exp(-1.f/(p.decay*rate_));
        for(unsigned c=0;c<2;++c) for(unsigned i=0;i<4;++i) {
            const float angle=6.283185307179586f*p.pitch*ratios[i]*(1.f+(c?1.f:-1.f)*.012f*p.spread)/rate_;
            lanes_[c].modes[i].a=radius*std::cos(angle);
            lanes_[c].modes[i].b=radius*std::sin(angle);
        }
        return true;
    }
    void reset() noexcept {
        for(auto& s:lanes_) { s.fast=s.slow=0; for(auto& m:s.modes) m.u=m.v=0; }
        wet_=patch_.mix; contrast_=patch_.contrast;
    }
    TraceFrame process(TraceFrame x) noexcept {
        x={clean(x.l),clean(x.r)};
        wet_+=smooth_*(patch_.mix-wet_);
        contrast_+=smooth_*(patch_.contrast-contrast_);
        const float l=lane(lanes_[0],x.l), r=lane(lanes_[1],x.r);
        if(patch_.bypass) return x; // Exact bounded dry; memory keeps evolving.
        return {clean(x.l+wet_*(l-x.l)),clean(x.r+wet_*(r-x.r))};
    }
};
} // namespace mhac::accel
