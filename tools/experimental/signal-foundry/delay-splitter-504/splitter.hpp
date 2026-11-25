#pragma once
#include <array>
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstring>
namespace mhac::splitter {
enum Param : unsigned { Delay, Inverse, Mix, Bypass, Count };
using Params=std::array<double,Count>;
inline constexpr Params defaults{0.,0.,0.5,0.};
inline constexpr std::array<unsigned,4> delays{16,64,256,1024};
inline bool validSampleRate(double r) noexcept {return std::isfinite(r)&&r>=1000&&r<=2000000;}
inline double clean(double x) noexcept {return std::isfinite(x)&&std::abs(x)>=1e-30?std::clamp(x,-1.,1.):0.;}
inline unsigned tap(double x) noexcept {return unsigned(std::lround(3*x));}
using State=std::array<std::uint8_t,40>;
inline State encode(const Params& p) noexcept {
    State b{};b[0]='M';b[1]='S';b[2]='P';b[3]='L';b[4]=1;
    for(unsigned i=0;i<Count;++i){std::uint64_t u=0;std::memcpy(&u,&p[i],8);for(unsigned j=0;j<8;++j)b[8+8*i+j]=std::uint8_t(u>>(8*j));}return b;
}
inline bool decode(const State& b,Params& out) noexcept {
    if(b[0]!='M'||b[1]!='S'||b[2]!='P'||b[3]!='L'||b[4]!=1||b[5]||b[6]||b[7])return false;
    Params p{};for(unsigned i=0;i<Count;++i){std::uint64_t u=0;for(unsigned j=0;j<8;++j)u|=std::uint64_t(b[8+8*i+j])<<(8*j);std::memcpy(&p[i],&u,8);if(!std::isfinite(p[i])||p[i]<0||p[i]>1)return false;}out=p;return true;
}
class Engine {
    Params p=defaults;
    std::array<std::array<double,1024>,2> ring{};
    std::array<double,4> weights{1,0,0,0};
    unsigned pos=0;double coeff=1,inv=0,wet=.5;
    double glide(double x,double target) const noexcept {return std::abs(x-target)<1e-10?target:x+coeff*(target-x);}
public:
    const Params& params() const noexcept{return p;}
    void set(unsigned i,double v) noexcept {if(i<Count&&std::isfinite(v))p[i]=std::clamp(v,0.,1.);}
    void restore(const Params& v) noexcept {for(unsigned i=0;i<Count;++i)set(i,v[i]);}
    bool reset(double rate) noexcept {
        if(!validSampleRate(rate))return false;
        for(auto& c:ring)c.fill(0);pos=0;weights.fill(0);weights[tap(p[Delay])]=1;
        inv=p[Inverse]>=.5?1:0;wet=p[Bypass]>=.5?0:p[Mix];coeff=-std::expm1(-1./(.005*rate));return true;
    }
    template<class T> std::array<T,2> process(T left,T right) noexcept {
        const double l=clean(left),r=clean(right);double dl=0,dr=0;
        const auto k=tap(p[Delay]);
        for(unsigned i=0;i<4;++i){weights[i]=glide(weights[i],i==k?1.:0.);const auto j=(pos+1024-delays[i])%1024;dl+=weights[i]*ring[0][j];dr+=weights[i]*ring[1][j];}
        ring[0][pos]=l;ring[1][pos]=r;pos=(pos+1)%1024;
        inv=glide(inv,p[Inverse]>=.5?1.:0.);wet=glide(wet,p[Bypass]>=.5?0.:p[Mix]);
        const double sign=1-2*inv;
        const double a=.5*(l+dl+sign*(dr-r)),b=.5*(r+dr+sign*(dl-l));
        return {T(clean(l+wet*(a-l))),T(clean(r+wet*(b-r)))};
    }
};
static_assert(sizeof(double)==8,"Requires binary64 storage");
}
