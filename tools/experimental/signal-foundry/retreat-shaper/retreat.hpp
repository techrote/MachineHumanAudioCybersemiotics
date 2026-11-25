#pragma once
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <limits>
namespace mhac::retreat {
enum Param : unsigned { Drive, Coupling, Depth, Mix, Bypass, Attack, Release, Count };
using Params=std::array<double,Count>;
inline constexpr Params defaults{0.,0.,.8,1.,0.,0.,0.};
inline bool validSampleRate(double r) noexcept { return std::isfinite(r)&&r>=1000.&&r<=2000000.; }
inline double unit(double v) noexcept { return std::isfinite(v)?std::clamp(v,0.,1.):0.; }
// Equal upper/lower marginals, different pairings (PR #365, Result B, m=8).
struct Relays {
    std::uint8_t a=0,b=0;
    void step(unsigned level) noexcept {
        for(unsigned i=1;i<=8;++i){
            const unsigned bit=1u<<(i-1),loA=i==8?8:8-i,loB=9-i;
            if(level>=8+i){a|=bit;b|=bit;}
            else {if(level<loA)a&=~bit;if(level<loB)b&=~bit;}
        }
    }
    static unsigned count(unsigned x) noexcept { unsigned n=0;for(unsigned i=0;i<8;++i)n+=(x>>i)&1u;return n; }
    double mass(double coupling) const noexcept {return ((1.-coupling)*count(a)+coupling*count(b))/8.;}
};
inline constexpr unsigned legacyCount=5, legacySize=8+4*legacyCount;
using State=std::array<std::uint8_t,8+4*Count>;
inline void put(State& a,unsigned off,std::uint32_t x) noexcept {for(unsigned j=0;j<4;++j)a[off+j]=std::uint8_t(x>>(8*j));}
inline std::uint32_t get(const State& a,unsigned off) noexcept {std::uint32_t x=0;for(unsigned j=0;j<4;++j)x|=std::uint32_t(a[off+j])<<(8*j);return x;}
inline State encode(const Params& p) noexcept {State a{'M','H','R','S'};put(a,4,2);for(unsigned i=0;i<Count;++i)put(a,8+4*i,std::uint32_t(std::lround(unit(p[i])*1000000.)));return a;}
inline bool decode(const State& a,Params& p,unsigned size=sizeof(State)) noexcept {
    if(a[0]!='M'||a[1]!='H'||a[2]!='R'||a[3]!='S')return false;
    const auto version=get(a,4);
    const unsigned n=version==1&&size==legacySize?legacyCount:version==2&&size==sizeof(State)?unsigned(Count):0u;
    if(!n)return false;
    Params t=defaults;for(unsigned i=0;i<n;++i){auto x=get(a,8+4*i);if(x>1000000)return false;t[i]=x/1000000.;}p=t;return true;
}
// One-pole magnitude detector; time constants are 1/e settling times.
struct Detector {
    double value=0.;
    static double coefficient(double sr,double seconds) noexcept {return seconds>0.?-std::expm1(-1./(sr*seconds)):1.;}
    double step(double x,double attack,double release) noexcept {
        const double k=x>=value?attack:release;
        value=k==1.?x:std::clamp(value+k*(x-value),0.,1.);
        if(value<1e-20)value=0.;
        return value;
    }
};
class Engine {
    Params p_=defaults;std::array<Relays,2> relays_{};std::array<double,2> gain_{1.,1.};
    double sr_=48000.,slew_=200./48000.,drive_=1.,attack_=1.,release_=1.;
    std::array<Detector,2> detector_{};
    void updateDetector() noexcept {attack_=Detector::coefficient(sr_,.1*p_[Attack]);release_=Detector::coefficient(sr_,.5*p_[Release]);}
public:
    void reset(double sr) noexcept {sr_=validSampleRate(sr)?sr:48000.;slew_=std::min(1.,200./sr_);relays_={};gain_={1.,1.};detector_={};updateDetector();}
    const Params& params() const noexcept{return p_;}
    void set(unsigned id,double value) noexcept {if(id>=Count||!std::isfinite(value))return;const double v=unit(value);if(p_[id]==v)return;p_[id]=v;if(id==Drive)drive_=std::exp2(4.*p_[Drive]);if(id==Attack||id==Release)updateDetector();}
    void restore(const Params& p) noexcept {for(unsigned i=0;i<Count;++i)set(i,p[i]);reset(sr_);}
    double mass(unsigned c) const noexcept {return c<2?relays_[c].mass(p_[Coupling]):0.;}
    template<class T> T process(unsigned c,T input) noexcept {
        if(c>=2)return T(0);
        if(!std::isfinite(input)||std::abs(input)<std::numeric_limits<T>::min())input=T(0);
        const double x=std::min(1.,std::min(1.,std::abs(double(input)))*drive_);
        const unsigned level=unsigned(16.*detector_[c].step(x,attack_,release_));
        relays_[c].step(level);
        const double target=p_[Bypass]>=.5?1.:1.-p_[Depth]*p_[Mix]*(1.-mass(c));
        gain_[c]=std::clamp(gain_[c]+std::clamp(target-gain_[c],-slew_,slew_),0.,1.);
        const T out=T(input*gain_[c]);return std::abs(out)<std::numeric_limits<T>::min()?T(0):out;
    }
};
}
