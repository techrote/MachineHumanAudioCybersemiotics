#pragma once
#include "../loom.hpp"
namespace loom {
// Same two anonymous carriers; receipt bits request a swap at successive full-period meetings.
struct CyclePatch { double spread=.35, period=.5, width=1; std::uint16_t swaps=0xffff; };
struct CycleVoice {
    bool active=false, released=false, swapped=false; unsigned receiptIndex=0;
    std::uint64_t position=0, period=1, age=0, attack=1, release=1, remaining=0;
    double phase=0, increment=0, excursion=0, width=1, velocity=0, releaseStart=0;
    std::uint16_t mask=0;
    bool start(double sr,int note,double cents,double vel,CyclePatch p) noexcept {
        if(!std::isfinite(sr)||sr<1000||sr>2000000)return false;
        *this=CycleVoice{}; active=true;
        period=std::uint64_t(std::llround(bound(p.period,.025,2)*sr));
        attack=std::uint64_t(std::llround(.005*sr)); release=std::uint64_t(std::llround(.04*sr));
        const double center=std::min(440*std::exp2((std::clamp(note,0,127)-69+bound(cents,-1200,1200)/100)/12),.25*sr);
        constexpr double pi=3.14159265358979323846;
        increment=center/sr; excursion=center*bound(p.spread,0,.8)*double(period)/sr/pi;
        width=bound(p.width,0,1); velocity=bound(vel,0,1); mask=p.swaps; return true;
    }
    double envelope() const noexcept {return released?releaseStart*double(remaining)/double(release):std::min(1.,double(age)/double(attack));}
    void off() noexcept {if(active&&!released){releaseStart=envelope();remaining=release;released=true;}}
    Pair tick() noexcept {
        if(!active)return {};
        constexpr double pi=3.14159265358979323846;
        const double s=std::sin(pi*double(position)/double(period));
        const double delta=excursion*s*s;
        const double a=std::sin(2*pi*std::remainder(phase-delta,1.)),b=std::sin(2*pi*std::remainder(phase+delta,1.));
        const double gain=.05*velocity*envelope(), m=(a+b)*.5, side=(a-b)*.5*width*(swapped?-1.:1.);
        phase=std::remainder(phase+increment,1.);
        if(++position==period){position=0;swapped^=bool((mask>>receiptIndex)&1u);receiptIndex=(receiptIndex+1)%16;}
        if(age<attack)++age;
        if(released&&--remaining==0)active=false;
        return {gain*(m+side),gain*(m-side)};
    }
};
}
