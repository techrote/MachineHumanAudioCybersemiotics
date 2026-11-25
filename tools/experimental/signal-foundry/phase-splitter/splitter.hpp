#pragma once
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <limits>
namespace mhac::splitter {
enum Param : unsigned { Delay, Direction, Mix, Gain, Bypass, Count };
using Params=std::array<double,Count>;
inline constexpr Params defaults{15./63.,0.,1.,.5,0.};
inline bool validSampleRate(double r) noexcept {return std::isfinite(r)&&r>=1000.&&r<=2000000.;}
inline double unit(double x) noexcept {return std::isfinite(x)?std::clamp(x,0.,1.):0.;}
using State=std::array<std::uint8_t,8+4*Count>;
inline void put(State& a,unsigned off,std::uint32_t x) noexcept {for(unsigned j=0;j<4;++j)a[off+j]=std::uint8_t(x>>(8*j));}
inline std::uint32_t get(const State& a,unsigned off) noexcept {std::uint32_t x=0;for(unsigned j=0;j<4;++j)x|=std::uint32_t(a[off+j])<<(8*j);return x;}
inline State encode(const Params& p) noexcept {State a{'M','H','S','P'};put(a,4,1);for(unsigned i=0;i<Count;++i)put(a,8+4*i,std::uint32_t(std::lround(unit(p[i])*1000000.)));return a;}
inline bool decode(const State& a,Params& p) noexcept {if(a[0]!='M'||a[1]!='H'||a[2]!='S'||a[3]!='P'||get(a,4)!=1)return false;Params t{};for(unsigned i=0;i<Count;++i){auto x=get(a,8+4*i);if(x>1000000)return false;t[i]=x/1000000.;}p=t;return true;}
// Delay the mid projection (forward) or its orthogonal complement (return).
// With fixed settings, full wet, unity gain and no limiting: return*forward=z^d I.
class Engine {
    Params p_=defaults;
    std::array<double,65> mid_{},side_{};
    unsigned pos_=0;
    double sr_=48000.,delay_=16.,direction_=0.,mix_=1.,gain_=.5,step_=200./48000.;
    double targetDelay() const noexcept {return 1.+std::round(63.*p_[Delay]);}
    static double approach(double v,double t,double s) noexcept {return v+std::clamp(t-v,-s,s);}
    double tap(const std::array<double,65>& a) const noexcept {
        const unsigned n=unsigned(delay_);const double f=delay_-n;
        const double x=a[(pos_+65-n)%65];
        return f==0.?x:x+f*(a[(pos_+64-n)%65]-x);
    }
    static double clean(double x) noexcept {return std::isfinite(x)&&std::abs(x)>=1e-20?std::clamp(x,-1.,1.):0.;}
public:
    void reset(double sr) noexcept {sr_=validSampleRate(sr)?sr:48000.;step_=std::min(1.,200./sr_);mid_={};side_={};pos_=0;delay_=targetDelay();direction_=p_[Direction]>=.5?1.:0.;mix_=p_[Bypass]>=.5?0.:p_[Mix];gain_=p_[Bypass]>=.5?1.:p_[Gain];}
    const Params& params() const noexcept {return p_;}
    void set(unsigned id,double value) noexcept {if(id<Count&&std::isfinite(value))p_[id]=unit(value);}
    void restore(const Params& p) noexcept {for(unsigned i=0;i<Count;++i)set(i,p[i]);reset(sr_);}
    template<class T> std::array<T,2> process(T left,T right) noexcept {
        const double l=clean(double(left)),r=clean(double(right));
        const double m=.5*(l+r),s=.5*(l-r);
        mid_[pos_]=m;side_[pos_]=s;
        delay_=approach(delay_,targetDelay(),63.*step_);
        direction_=approach(direction_,p_[Direction]>=.5?1.:0.,step_);
        mix_=approach(mix_,p_[Bypass]>=.5?0.:p_[Mix],step_);
        gain_=approach(gain_,p_[Bypass]>=.5?1.:p_[Gain],step_);
        const double dm=tap(mid_),ds=tap(side_);
        pos_=(pos_+1)%65;
        const double om=dm+direction_*(m-dm),os=s+direction_*(ds-s);
        return {T(clean(gain_*(l+mix_*(om+os-l)))),T(clean(gain_*(r+mix_*(om-os-r))))};
    }
};
}
