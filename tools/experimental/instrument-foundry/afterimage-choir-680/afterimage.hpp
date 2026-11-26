#pragma once
#include <array>
#include <algorithm>
#include <cmath>
#include <cstdint>
namespace mhac::afterimage {
// Shared native/host rate contract. No rate-sized buffers are allocated.
inline bool supportsRate(double sr) noexcept {
    return std::isfinite(sr)&&sr>=1000.0&&sr<=2000000.0;
}
enum class Mode { absent, fixed, preview, full };
struct Pair { unsigned low=2, high=6; bool valid() const { return low<high && high<8; } };
inline unsigned mask(Mode m, Pair p) {
    if(m==Mode::full) return 7;
    if(m==Mode::fixed) return 1;
    if(m==Mode::preview) { unsigned x=p.low^p.high; return x&(~x+1u); }
    return 0;
}
struct Result { unsigned state; bool ambiguous; };
inline Result decode(unsigned observed, unsigned tag, unsigned m, Pair p) {
    if(observed!=p.low) return {observed,false};
    const bool l=(p.low&m)==tag, h=(p.high&m)==tag;
    return {l?p.low:p.high,l&&h}; // trusted, internally generated tag only
}
struct Patch { Pair pair; Mode mode=Mode::fixed; double minimumMs=80; double memory=0.8; };
class Engine {
    struct Voice {
        bool used=false, held=false; int id=0; unsigned original=0, tag=0, mask=0, captured=0;
        Pair pair; Mode mode=Mode::fixed; std::uint64_t age=0, minimum=0;
        double velocity=0, gain=0; std::array<double,4> phase{},step{},weight{};
    };
    std::array<Voice,8> voices{};
    Patch patch{}; double rate=48000, attack=1.0/240, release=1.0/1440;
    unsigned history=0; bool ambiguous=false;
public:
    bool prepare(double sr) {
        if(!supportsRate(sr)) return false;
        rate=sr; attack=1/(.005*sr); release=1/(.030*sr); reset(); return true;
    }
    void reset() { voices={}; history=0; ambiguous=false; }
    bool configure(Patch p) {
        if(!p.pair.valid()||static_cast<unsigned>(p.mode)>3||!std::isfinite(p.minimumMs)||p.minimumMs<0||p.minimumMs>2000||!std::isfinite(p.memory)||p.memory<0||p.memory>1) return false;
        patch=p; return true;
    }
    unsigned remembered() const { return history; }
    bool lastAmbiguous() const { return ambiguous; }
    unsigned active() const { unsigned n=0; for(const auto& v:voices) n+=v.used; return n; }
    bool off(int id, bool commit=true) {
        for(auto& v:voices) if(v.used&&v.held&&v.id==id) {
            v.held=false;
            if(commit&&v.age>=v.minimum) {
                const Pair p=v.mode==Mode::preview?v.pair:patch.pair;
                const auto r=decode(v.original==p.high?p.low:v.original,v.tag,v.mask,p);
                history=r.state; ambiguous=r.ambiguous;
            }
            return true;
        }
        return false;
    }
    bool on(int id, int pitch, double velocity, double cents=0) {
        if(id<0||pitch<0||pitch>127||!std::isfinite(velocity)||velocity<0||velocity>1||!std::isfinite(cents)||std::abs(cents)>1200) return false;
        if(velocity==0) return off(id);
        for(const auto& v:voices) if(v.used&&v.held&&v.id==id) return false;
        for(auto& v:voices) if(!v.used) {
            v={}; v.used=v.held=true; v.id=id; v.velocity=velocity; v.original=static_cast<unsigned>(pitch)%8;
            v.mode=patch.mode; v.pair=patch.pair; v.mask=mask(v.mode,v.pair); v.tag=v.original&v.mask;
            v.captured=history; v.minimum=static_cast<std::uint64_t>(std::ceil(rate*patch.minimumMs/1000));
            const double f=440*std::exp2((pitch-69+cents/100)/12);
            const std::array<double,4> ratios{1,2.0+history*.25,3.0+history*.5,5.0+history*.75};
            const std::array<double,4> w{1,.5*patch.memory,.3*patch.memory,.2*patch.memory};
            double sum=0;
            for(unsigned k=0;k<4;++k) { const double hz=f*ratios[k]; v.step[k]=hz/rate; v.weight[k]=w[k]*std::clamp((.45-hz/rate)/.05,0.0,1.0); sum+=v.weight[k]; }
            for(auto& a:v.weight) a/=std::max(1.0,sum);
            return true;
        }
        return false; // bounded admission, no stealing
    }
    double tick() {
        double out=0;
        for(auto& v:voices) if(v.used) {
            if(v.held) { v.gain=std::min(1.0,v.gain+attack); if(v.age<v.minimum) ++v.age; }
            else { v.gain=std::max(0.0,v.gain-release); if(v.gain<=1e-12) { v={}; continue; } }
            double y=0;
            for(unsigned k=0;k<4;++k) if(v.weight[k]>0) { y+=v.weight[k]*std::sin(6.2831853071795864769*v.phase[k]); v.phase[k]+=v.step[k]; if(v.phase[k]>=1) v.phase[k]-=1; }
            out+=.065*v.velocity*v.gain*y;
        }
        return std::clamp(out,-.52,.52);
    }
    template<class T> void render(T* left,T* right,unsigned frames) {
        for(unsigned i=0;i<frames;++i) { const T s=static_cast<T>(tick()); if(left) left[i]=s; if(right) right[i]=s; }
    }
};
}
