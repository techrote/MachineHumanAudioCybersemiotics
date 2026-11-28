#pragma once
#include <array>
#include <algorithm>
#include <cmath>
namespace mhac::afterimage {
// Gain-weighted, independently anchored partial bank. Configure at note onset;
// copy preserves phase for a stolen voice's fade. No allocation or I/O.
class AdditiveMemory {
    static constexpr double tau=6.2831853071795864769;
    struct Partial { double phase=0, step=0, gain=0, x=0, y=0, c=1, s=0; };
    std::array<Partial,4> partials{};
    unsigned ticks=0;
public:
    // Inputs are the already-tapered, normalized coefficients of the voice.
    void configure(const std::array<double,4>& steps,const std::array<double,4>& gains) noexcept {
        ticks=0;
        for(unsigned i=0;i<4;++i){
            auto& p=partials[i];
            p={0,steps[i],gains[i],gains[i],0,1,0};
            if(p.gain>0){p.c=std::cos(tau*p.step);p.s=std::sin(tau*p.step);}
        }
    }
    double tick() noexcept {
        double out=0;
        for(unsigned i=0;i<4;++i){
            auto& p=partials[i];if(p.gain<=0)continue;
            // Stagger anchors over the four partials; initial coordinates are exact.
            if(ticks==64u*i){p.x=p.gain*std::cos(tau*p.phase);p.y=p.gain*std::sin(tau*p.phase);}
            out+=p.y;
            const double x=p.x*p.c-p.y*p.s;
            p.y=p.y*p.c+p.x*p.s;p.x=x;
            p.phase+=p.step;if(p.phase>=1)p.phase-=1;
        }
        ticks=(ticks+1u)&255u;
        return out;
    }
};
}
