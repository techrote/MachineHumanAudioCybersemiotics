#pragma once
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
namespace mhac::orbit {
// A time-expanded, ping-pong reading of escape energy; not an escape solver.
// All configuration happens at note admission; tick is constant work.
class SustainPath {
    std::array<double,61> knots_{};
    unsigned length_=0, half_=0, position_=0;
    double depth_=0.;
public:
    bool configure(const std::array<double,61>& knots,unsigned length,double depth,
                   double rate,double cycleMs) noexcept {
        if(!length||length>60||!std::isfinite(depth)||depth<0.||depth>1.||
           !std::isfinite(rate)||rate<1000.||rate>2000000.||
           !std::isfinite(cycleMs)||cycleMs<200.||cycleMs>8000.||
           knots[0]!=1.||knots[length]!=0.)return false;
        for(unsigned i=0;i<=length;++i)
            if(!std::isfinite(knots[i])||knots[i]<0.||knots[i]>1.)return false;
        knots_=knots;length_=length;depth_=depth;
        half_=unsigned(std::ceil(rate*cycleMs/2000.));position_=0;return true;
    }
    bool configured() const noexcept {return length_!=0;}
    double tick() noexcept {
        if(!configured()||depth_==0.)return 0.;
        const unsigned distance=position_<=half_?position_:2*half_-position_;
        const double t=double(distance)*length_/half_;
        const unsigned i=std::min(length_-1,unsigned(t));
        const double energy=knots_[i]+(t-i)*(knots_[i+1]-knots_[i]);
        if(++position_==2*half_)position_=0;
        return depth_*(1.-energy);
    }
};
} // namespace mhac::orbit
