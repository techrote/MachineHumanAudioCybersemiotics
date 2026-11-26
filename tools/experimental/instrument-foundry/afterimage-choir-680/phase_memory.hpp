#pragma once
#include <array>
#include <algorithm>
#include <cmath>
namespace mhac::afterimage {
// Truncated phase-modulation series, with explicit signed sideband frequencies.
// Fixed cost: 13 oscillators, coefficient work only at note onset.
class PhaseMemory {
    static constexpr double tau=6.2831853071795864769;
    // Gain-weighted complex rotation; the wrapped reference phase anchors
    // both coordinates every 256 ticks, bounding accumulated rotation error.
    struct Side { double phase=0, step=0, gain=0, x=0, y=0, c=1, s=0; };
    std::array<Side,13> sides{};
    double scale=1;
    unsigned ticks=0;
    static double bessel(unsigned k,double beta) noexcept {
        double t=1;
        for(unsigned i=1;i<=k;++i)t*=beta/(2*i);
        double sum=t;
        for(unsigned j=1;j<=10;++j){t*=-beta*beta/(4*j*(j+k));sum+=t;}
        return sum;
    }
public:
    // Captured parameters; do not change a sounding oscillator's configuration.
    bool configure(double sr,double carrier,double ratio,double beta) noexcept {
        if(!std::isfinite(sr)||sr<1000||sr>2000000||!std::isfinite(carrier)||carrier<=0||carrier>100000||
           !std::isfinite(ratio)||ratio<1||ratio>3||!std::isfinite(beta)||beta<0||beta>1.5)return false;
        double sum=0;
        for(int k=-6;k<=6;++k){
            const double hz=carrier*(1+k*ratio), step=hz/sr;
            const auto order=static_cast<unsigned>(std::abs(k));
            const double sign=k<0&&order%2? -1:1;
            const double taper=std::clamp((.45-std::abs(step))/.05,0.,1.);
            auto& side=sides[static_cast<unsigned>(k+6)];
            side={0,step,sign*bessel(order,beta)*taper};sum+=std::abs(side.gain);
        }
        scale=1/std::max(1.,sum);
        for(auto& side:sides){
            side.gain*=scale;
            side.x=side.gain;
            if(side.gain!=0){side.c=std::cos(tau*side.step);side.s=std::sin(tau*side.step);}
        }
        ticks=0;
        return true;
    }
    double normalization()const noexcept{return scale;}
    double tick() noexcept {
        double y=0;
        for(auto& side:sides)if(side.gain!=0){
            if(ticks==0){
                side.x=side.gain*std::cos(tau*side.phase);
                side.y=side.gain*std::sin(tau*side.phase);
            }
            y+=side.y;
            const double x=side.x*side.c-side.y*side.s;
            side.y=side.y*side.c+side.x*side.s;
            side.x=x;
            side.phase+=side.step;
            if(side.phase>=1)side.phase-=1;
            else if(side.phase<0)side.phase+=1;
        }
        ticks=(ticks+1u)&255u;
        return std::clamp(y,-1.,1.);
    }
};
}
