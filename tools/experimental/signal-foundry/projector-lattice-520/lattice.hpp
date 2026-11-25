#pragma once
#include <array>
#include <algorithm>
#include <cmath>
#include <cstddef>
namespace mhac::lattice {
struct Frame { double l=0,r=0; };
enum class Axis { Left, Right, Sum, Difference };
struct Spec { Axis axis=Axis::Sum; unsigned delay=1; };
using Program=std::array<Spec,4>;
inline double guard(double x) noexcept {
    return std::isfinite(x)&&std::abs(x)>=1e-30?std::clamp(x,-1.0,1.0):0.;
}
class Stage {
    std::array<Frame,1024> memory{};
    unsigned pos=0;
    Spec spec{};
    friend class Lattice;
    void reset(Spec s) noexcept { spec=s; pos=0; memory.fill({}); }
    Frame step(Frame x) noexcept {
        Frame p{};
        switch(spec.axis) {
        case Axis::Left: p={x.l,0}; break;
        case Axis::Right: p={0,x.r}; break;
        case Axis::Sum: p.l=p.r=(x.l+x.r)*.5; break;
        case Axis::Difference: p.l=(x.l-x.r)*.5; p.r=-p.l; break;
        }
        const auto d=memory[pos]; memory[pos]=p;
        if(++pos==spec.delay) pos=0;
        return {x.l-p.l+d.l,x.r-p.r+d.r};
    }
};
class Lattice {
    std::array<Stage,4> stages{};
    unsigned tail_=4;
    static Axis complement(Axis a) noexcept {
        switch(a) {case Axis::Left:return Axis::Right;case Axis::Right:return Axis::Left;
        case Axis::Sum:return Axis::Difference;default:return Axis::Sum;}
    }
public:
    // Configure only off the audio thread; clears all history. Invalid input is transactional.
    bool configure(const Program& p,bool inverse=false) noexcept {
        unsigned total=0;
        for(auto s:p) {
            if(s.delay<1||s.delay>1024||static_cast<unsigned>(s.axis)>3) return false;
            total+=s.delay;
        }
        for(unsigned i=0;i<4;++i) {
            auto s=p[inverse?3-i:i]; if(inverse)s.axis=complement(s.axis);
            stages[i].reset(s);
        }
        tail_=total; return true;
    }
    Lattice() noexcept { configure(Program{}); }
    unsigned tail() const noexcept { return tail_; }
    Frame step(Frame x) noexcept {
        x={guard(x.l),guard(x.r)};
        for(auto& s:stages)x=s.step(x);
        return {guard(x.l),guard(x.r)};
    }
};
}
