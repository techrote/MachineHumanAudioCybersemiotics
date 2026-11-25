#pragma once
#include <array>
#include <algorithm>
#include <cmath>
#include <cstdint>
namespace mhac {
enum Param : unsigned { S0,S1,S2,S3,Rate,Wet,Hold,Mode,Bypass,Count };
using Params=std::array<double,Count>;
constexpr Params defaults{0.15,0.85,0.4,1.0,0.35,0.65,0,0,0};
inline double unit(double x) noexcept {return std::isfinite(x)?std::clamp(x,0.0,1.0):0.0;}
// Four live gain slots, a free-running phase, and three precise hold contracts.
class Freeze {
    Params p=defaults;
    std::array<double,4> saved{};
    double sampleRate=48000, fraction=0, captured=1, gain=1, mix=0, alpha=0;
    unsigned slot=0, activeMode=0;
    bool held=false;
public:
    void prepare(double sr) noexcept {
        sampleRate=std::isfinite(sr)?std::clamp(sr,8000.0,384000.0):48000;
        alpha=1-std::exp(-1/(0.005*sampleRate)); reset();
    }
    void reset() noexcept {
        fraction=0;slot=0;held=false;activeMode=0;captured=1;saved={};gain=1;mix=0;
    }
    void set(unsigned id,double value) noexcept { if(id<Count)p[id]=unit(value); }
    const Params& parameters() const noexcept {return p;}
    unsigned phase() const noexcept {return slot;}
    double target() const noexcept {
        return held&&activeMode==0?captured:held&&activeMode==2?saved[slot]:p[slot];
    }
    // Call once per audio frame, after applying all parameter changes at its offset.
    double step() noexcept {
        bool want=p[Hold]>=0.5;
        if(want&&!held){activeMode=unsigned(std::lround(2*p[Mode]));captured=p[slot];for(unsigned i=0;i<4;++i)saved[i]=p[i];}
        held=want;
        gain+=alpha*(target()-gain);mix+=alpha*((p[Bypass]>=0.5?0:p[Wet])-mix);
        if(std::abs(gain)<1e-20)gain=0;
        if(std::abs(mix)<1e-20)mix=0;
        double out=1-mix+mix*gain;
        if(!(held&&activeMode==1)){
            // 0.25 to 16 slot advances per second, logarithmic.
            fraction+=0.25*std::exp2(6*p[Rate])/sampleRate;
            if(fraction>=1){fraction-=1;slot=(slot+1)%4;}
        }
        return std::clamp(out,0.0,1.0);
    }
    template<class T> static T apply(T x,double g) noexcept {
        if(!std::isfinite(x))return T(0);
        // No amplification; preserve ordinary over-unity host audio rather than clip it.
        T y=T(double(x)*g);return std::abs(y)<T(1e-20)?T(0):y;
    }
};
}
