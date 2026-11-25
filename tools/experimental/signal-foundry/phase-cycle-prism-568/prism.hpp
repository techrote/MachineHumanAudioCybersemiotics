#pragma once
#include <algorithm>
#include <array>
#include <cmath>
#include <complex>
#include <cstddef>
namespace prism {
using C=std::complex<double>;
using Coeff=std::array<C,4>;
inline constexpr std::array<int,4> bins{5,6,9,10};
inline constexpr double tau=6.283185307179586476925286766559;
inline double bound(double x,double lo,double hi) noexcept {return std::isfinite(x)&&std::abs(x)>=1e-30?std::clamp(x,lo,hi):0.;}
inline Coeff cubic(const Coeff& a,double gamma) noexcept {
    Coeff y=a;
    for(int l=0;l<4;++l) for(int i=0;i<4;++i) for(int j=0;j<4;++j) for(int k=0;k<4;++k)
        if(bins[i]+bins[j]==bins[k]+bins[l]) y[l]+=gamma*a[i]*a[j]*std::conj(a[k]);
    return y;
}
inline Coeff cycle(const Coeff& a,double gamma) noexcept {
    Coeff b=a; b[3]=-b[3]; auto y=cubic(a,gamma),z=cubic(b,gamma); z[3]=-z[3];
    for(int j=0;j<4;++j) y[j]=(y[j]+z[j])*.5;
    return y;
}
struct Params {double drive=.5,cancel=1.,wet=.5,gain=.5;};
class Prism {
    static constexpr std::size_t cap=4096;
    std::array<std::array<C,cap>,4> basis{};
    std::array<C,cap> delay{};
    Coeff sum{},from{},to{};
    std::size_t n=0,pos=0;
    Params target{}; double wet=.5,gain=.5,slew=.01;
public:
    bool prepare(double sr) noexcept {
        if(!std::isfinite(sr)||sr<8000||sr>192000) return false;
        n=static_cast<std::size_t>(std::round(sr/80.)); slew=std::min(1.,200./sr);
        for(int j=0;j<4;++j) for(std::size_t p=0;p<n;++p)
            basis[j][p]=std::polar(1.,tau*bins[j]*double(p)/double(n));
        reset(); return true;
    }
    void set(Params p) noexcept {
        target={bound(p.drive,-1,1),bound(p.cancel,0,1),bound(p.wet,0,1),bound(p.gain,0,1)};
    }
    void reset() noexcept {pos=0;sum={};from={};to={};delay.fill({});wet=target.wet;gain=target.gain;}
    std::size_t latency() const noexcept {return n;}
    std::size_t tailBound() const noexcept {return 3*n;}
    C step(double l,double r) noexcept {
        if(!n) return {};
        const C x{bound(l,-1,1),bound(r,-1,1)},dry=delay[pos]; delay[pos]=x;
        C y{}; const double alpha=double(pos+1)/double(n);
        for(int j=0;j<4;++j){
            sum[j]+=x*std::conj(basis[j][pos]);
            y+=(from[j]+alpha*(to[j]-from[j]))*basis[j][pos];
        }
        wet+=std::clamp(target.wet-wet,-slew,slew); gain+=std::clamp(target.gain-gain,-slew,slew);
        y=(1-wet)*dry+wet*gain*y;
        if(++pos==n){
            pos=0;for(auto& a:sum)a/=double(n);
            auto raw=cubic(sum,target.drive),clean=cycle(sum,target.drive);from=to;
            for(int j=0;j<4;++j) to[j]=raw[j]+target.cancel*(clean[j]-raw[j]);
            sum={};
        }
        return {bound(y.real(),-1,1),bound(y.imag(),-1,1)};
    }
};
}
