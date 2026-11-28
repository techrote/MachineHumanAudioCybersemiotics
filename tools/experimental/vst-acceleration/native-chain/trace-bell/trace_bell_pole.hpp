#pragma once
#include <cmath>

namespace mhac::accel {
// Internal pole transition: interpolate phase and log radius, not Cartesian
// coefficients (a chord through the unit disk would erase resonant memory).
// Inputs are finite nonzero strictly stable poles from TraceBell::retune.
struct TracePoleRamp {
    float a=0, b=0, targetA=0, targetB=0;
    double real=0, imag=0, mulA=1, mulB=0;
    unsigned remaining=0;
    void snap() noexcept {
        a=targetA; b=targetB; real=a; imag=b; remaining=0;
    }
    void set(float nextA,float nextB,unsigned samples) noexcept {
        if(nextA==targetA&&nextB==targetB&&samples) return;
        targetA=nextA; targetB=nextB;
        if(!samples||(real==0&&imag==0)){snap();return;}
        const double radius=std::hypot(real,imag);
        const double nextRadius=std::hypot(double(nextA),double(nextB));
        const double angle=std::atan2(double(nextB)*real-double(nextA)*imag,
                                     double(nextA)*real+double(nextB)*imag)/samples;
        const double gain=std::exp(std::log(nextRadius/radius)/samples);
        mulA=gain*std::cos(angle); mulB=gain*std::sin(angle);
        remaining=samples;
    }
    void advance() noexcept {
        if(!remaining)return;
        if(--remaining==0){snap();return;}
        const double nextReal=real*mulA-imag*mulB;
        imag=imag*mulA+real*mulB; real=nextReal;
        a=float(real); b=float(imag);
    }
};
} // namespace mhac::accel
