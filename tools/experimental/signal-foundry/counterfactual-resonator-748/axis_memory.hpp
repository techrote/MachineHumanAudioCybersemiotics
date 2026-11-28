#pragma once
#include "resonator.hpp"

namespace mhac::counterfactual {
// Independent mid/side memories. The wet decoder reserves 6 dB for summation.
// Native experimental component; no changes to the existing CR state contract.
class AxisMemory {
    Processor mid_, side_;
    double wet_=1, target_=1, slew_=1.0/240;
    static double clean(double x) noexcept {
        return std::isfinite(x)&&std::abs(x)>=1e-20?std::clamp(x,-1.0,1.0):0;
    }
public:
    bool prepare(double rate) noexcept {
        if(!validSampleRate(rate))return false;
        mid_.prepare(rate); side_.prepare(rate);
        slew_=1.0/std::ceil(rate*0.005); wet_=target_; return true;
    }
    void reset() noexcept {mid_.reset();side_.reset();wet_=target_;}
    bool configure(Controls mid,Controls side,unsigned wet) noexcept {
        if(!valid(mid)||!valid(side)||wet>1000)return false;
        // Axis wet and bypass are controlled by the outer mix, not the cores.
        mid.wet=side.wet=1000;mid.bypass=side.bypass=false;
        mid_.set(mid);side_.set(side);target_=wet/1000.0;return true;
    }
    bool eraseMid() noexcept {return mid_.beginOptimalEscape();}
    bool eraseSide() noexcept {return side_.beginOptimalEscape();}
    IntegerState midState() const noexcept {return mid_.lattice(0);}
    IntegerState sideState() const noexcept {return side_.lattice(0);}
    std::uint64_t midInterventions() const noexcept {return mid_.interventions();}
    std::uint64_t sideInterventions() const noexcept {return side_.interventions();}
    Stereo process(double left,double right) noexcept {
        left=clean(left);right=clean(right);
        const double m=(left+right)*0.5,s=(left-right)*0.5;
        const double a=mid_.process(m,m).left,b=side_.process(s,s).left;
        wet_+=std::clamp(target_-wet_,-slew_,slew_);
        return {(1-wet_)*left+wet_*0.5*(a+b),(1-wet_)*right+wet_*0.5*(a-b)};
    }
    template<class T> void processBlock(const T* l,const T* r,T* ol,T* oright,unsigned n) noexcept {
        for(unsigned i=0;i<n;++i){const auto v=process(l[i],r[i]);ol[i]=static_cast<T>(v.left);oright[i]=static_cast<T>(v.right);}
    }
};
}
