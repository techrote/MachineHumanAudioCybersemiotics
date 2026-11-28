#pragma once
#include "resonator.hpp"

namespace mhac::counterfactual {
// Unity-centre-gain, Q=4 topology-preserving state-variable bandpass.
// Coefficient changes are control-thread/audio-owner operations, not per sample.
class BandInput {
    struct State { double s1=0,s2=0; };
    std::array<State,2> states_{};
    double a1_=1,a2_=0,a3_=0;
    static constexpr double k_=0.25;
    static double clean(double x) noexcept {
        return std::isfinite(x)&&std::abs(x)>=1e-20?std::clamp(x,-1.0,1.0):0;
    }
    static double zap(double x) noexcept {return std::abs(x)<1e-20?0:x;}
    double one(double x,State& s) noexcept {
        const double v3=clean(x)-s.s2;
        const double v1=a1_*s.s1+a2_*v3;
        const double v2=s.s2+a2_*s.s1+a3_*v3;
        s.s1=zap(2*v1-s.s1);s.s2=zap(2*v2-s.s2);
        if(!std::isfinite(s.s1)||!std::isfinite(s.s2)){s={};return 0;}
        return std::clamp(k_*v1,-1.0,1.0);
    }
public:
    bool tune(double rate,unsigned hz) noexcept {
        if(!validSampleRate(rate)||hz<40||hz>6000)return false;
        const double g=std::tan(3.14159265358979323846*std::min(double(hz),rate/16)/rate);
        a1_=1/(1+g*(g+k_));a2_=g*a1_;a3_=g*a2_;return true;
    }
    void reset() noexcept {states_={};}
    Stereo process(double l,double r) noexcept {return {one(l,states_[0]),one(r,states_[1])};}
};
} // namespace mhac::counterfactual
