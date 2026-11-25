#pragma once
#include "../prism.hpp"
#include <cstdint>
#include <cstring>
#include <limits>
#include <vector>
namespace prism {
enum Id : unsigned { Drive, Cancel, Wet, Gain, Grid, Bypass, Count };
using LiveParams=std::array<double,Count>;
inline constexpr LiveParams defaults{.75,1.,.5,.5,0.,0.};
using State=std::array<std::uint8_t,4+4*Count>;
inline State encode(const LiveParams& p) noexcept {
    static_assert(sizeof(float)==4 && std::numeric_limits<float>::is_iec559);
    State s{'P','C','0','1'};
    for(unsigned i=0;i<Count;++i){float f=static_cast<float>(p[i]);std::uint32_t u;std::memcpy(&u,&f,4);for(unsigned b=0;b<4;++b)s[4+4*i+b]=std::uint8_t(u>>(8*b));}
    return s;
}
inline bool decode(const std::uint8_t* s,std::size_t size,LiveParams& out) noexcept {
    if(!s||size!=State{}.size()||s[0]!='P'||s[1]!='C'||s[2]!='0'||s[3]!='1')return false;
    LiveParams p{};
    for(unsigned i=0;i<Count;++i){std::uint32_t u=0;for(unsigned b=0;b<4;++b)u|=std::uint32_t(s[4+4*i+b])<<(8*b);float f;std::memcpy(&f,&u,4);if(!std::isfinite(f)||f<0||f>1)return false;p[i]=f;}
    out=p;return true;
}
inline bool validRate(double sr) noexcept {return std::isfinite(sr)&&sr>=1000&&sr<=2000000;}
inline std::size_t frameLength(double sr) noexcept {return validRate(sr)?std::max<std::size_t>(96,static_cast<std::size_t>(std::round(sr/80.))):0;}
inline unsigned factor(double normalized) noexcept {return 1u<<unsigned(std::round(2*bound(normalized,0,1)));}
class LivePrism {
    struct Frame {Coeff c{};unsigned grid=1;};
    std::vector<C> basis,delay;
    Frame from{},to{};Coeff sum{};
    LiveParams target=defaults;std::size_t n=0,pos=0;unsigned captureGrid=1;
    double wet=.5,gain=.5,slew=.01;
    C carrier(unsigned j,unsigned grid) const noexcept {return basis[(pos*unsigned(bins[j])*grid)%n];}
    C synth(const Frame& f) const noexcept {C y{};for(unsigned j=0;j<4;++j)y+=f.c[j]*carrier(j,f.grid);return y;}
public:
    bool prepare(double sr) {
        const auto len=frameLength(sr);if(!len)return false;
        try {std::vector<C> b(len),d(len);for(std::size_t i=0;i<len;++i)b[i]=std::polar(1.,tau*double(i)/double(len));basis.swap(b);delay.swap(d);}catch(...){return false;}
        n=len;slew=std::min(1.,200./sr);reset();return true;
    }
    void set(unsigned id,double v) noexcept {if(id<Count&&std::isfinite(v))target[id]=std::clamp(v,0.,1.);}
    void restore(const LiveParams& p) noexcept {for(unsigned i=0;i<Count;++i)set(i,p[i]);}
    const LiveParams& params() const noexcept {return target;}
    void reset() noexcept {pos=0;sum={};captureGrid=factor(target[Grid]);from=to=Frame{{},captureGrid};std::fill(delay.begin(),delay.end(),C{});wet=target[Bypass]>=.5?0:target[Wet];gain=target[Gain];}
    std::size_t latency() const noexcept {return n;}
    std::size_t tailBound() const noexcept {return 3*n;}
    C step(double l,double r) noexcept {
        if(!n)return {};
        if(pos==0)captureGrid=factor(target[Grid]);
        const C x{bound(l,-1,1),bound(r,-1,1)},dry=delay[pos];delay[pos]=x;
        for(unsigned j=0;j<4;++j)sum[j]+=x*std::conj(carrier(j,captureGrid));
        const double a=double(pos+1)/double(n);
        const C y0=synth(from),y1=synth(to);
        wet+=std::clamp((target[Bypass]>=.5?0.:target[Wet])-wet,-slew,slew);
        gain+=std::clamp(target[Gain]-gain,-slew,slew);
        const C y=(1-wet)*dry+wet*gain*(y0+a*(y1-y0));
        if(++pos==n){pos=0;for(auto& c:sum)c/=double(n);const double drive=2*target[Drive]-1;auto raw=cubic(sum,drive),clean=cycle(sum,drive);from=to;to.grid=captureGrid;for(unsigned j=0;j<4;++j)to.c[j]=raw[j]+target[Cancel]*(clean[j]-raw[j]);sum={};}
        return {bound(y.real(),-1,1),bound(y.imag(),-1,1)};
    }
};
}
