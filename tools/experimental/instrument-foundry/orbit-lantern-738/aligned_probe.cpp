// Offline spectral residual reference; no SDK or real-time filtering.
#include "host.hpp"
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <vector>
using namespace mhac::orbit;
using mhac::orbit::host::Live;
static void check(bool b){if(!b){std::cerr<<"aligned reference failure\n";std::exit(1);}}
struct Pair {double l=0.,r=0.;};
// Symmetric Blackman-windowed sinc: exactly aligned sample centres, zero extension.
class Decimator {
    unsigned factor_; int radius_; std::vector<double> h_;
public:
    explicit Decimator(unsigned factor):factor_(factor),radius_(int(64*factor)),h_(std::size_t(2*radius_+1)) {
        const double fc=.45/double(factor_);double sum=0.;
        for(int k=-radius_;k<=radius_;++k){const double x=double(k), a=tau*x/double(2*radius_);
            const double sinc=k?std::sin(tau*fc*x)/(tau*.5*x):2.*fc;
            const double w=.42+.5*std::cos(a)+.08*std::cos(2.*a);
            h_[std::size_t(k+radius_)]=sinc*w;sum+=sinc*w;}
        for(auto& v:h_)v/=sum;
    }
    Pair at(const std::vector<Pair>& s,std::size_t i) const {
        Pair y;const auto centre=std::int64_t(i)*factor_;
        for(int k=-radius_;k<=radius_;++k){const auto j=centre+k;
            if(j>=0&&std::uint64_t(j)<s.size()){const auto x=s[std::size_t(j)];const auto h=h_[std::size_t(k+radius_)];y.l+=h*x.l;y.r+=h*x.r;}}
        return y;
    }
};
static double square(Pair p){return .5*(p.l*p.l+p.r*p.r);}
static Pair diff(Pair a,Pair b){return {a.l-b.l,a.r-b.r};}
static void oracle(unsigned factor){
    Decimator d(factor);std::vector<Pair> s(4096*factor);
    for(std::size_t i=0;i<s.size();++i)s[i]={std::sin(tau*3000.*double(i)/(48000.*factor)),std::sin(tau*30000.*double(i)/(48000.*factor))};
    double pass=0.,stop=0.;for(unsigned i=128;i<3968;++i){auto y=d.at(s,i);const double e=y.l-std::sin(tau*3000.*i/48000.);pass+=e*e;stop+=y.r*y.r;}
    check(std::sqrt(pass/3840.)<1e-5&&std::sqrt(stop/3840.)<1e-5);
    std::fill(s.begin(),s.end(),Pair{});s[1024*factor]={1.,1.};check(d.at(s,1024).l>d.at(s,1023).l);check(std::abs(d.at(s,1023).l-d.at(s,1025).l)<1e-14);
    std::fill(s.begin(),s.end(),Pair{1.,1.});check(std::abs(d.at(s,1024).l-1.)<1e-12);
}
static std::vector<Pair> residual(unsigned factor,int note,unsigned ms,unsigned mode){
    const unsigned rate=48000*factor;Live a,b;check(a.prepare(rate)&&b.prepare(rate));
    check(a.setPatch({1000,ms,0,mode,0})&&b.setPatch({1000,ms,0,mode,1000}));
    check(a.on(1,0,note,0.,.8)&&b.on(1,0,note,0.,.8));
    const unsigned off=4817*factor,n=(4817+48*ms+128)*factor;std::vector<Pair> s(n);
    for(unsigned i=0;i<n;++i){if(i==off)check(a.off(1,0,note)&&b.off(1,0,note));Pair x,y;a.tick(x.l,x.r);b.tick(y.l,y.r);s[i]=diff(y,x);
        check(std::isfinite(s[i].l)&&std::isfinite(s[i].r));if(i<off)check(square(s[i])==0.);}
    check(a.active()==0&&b.active()==0&&square(s.back())==0.);return s;
}
int main(){
    oracle(4);oracle(8);Decimator d4(4),d8(8);Spectrum sp;check(sp.build<68>({-16,4},8,4,9));
    std::cout<<"note,release_ms,mode,cut48,cut192,cut384,matched,residual48_rms,raw4_vs_filtered4_rms,low_vs_filtered4_rms,filtered4_vs_filtered8_rms\n"<<std::setprecision(12);
    for(int note:{69,93,105,117,125})for(unsigned ms:{10u,80u,800u})for(unsigned mode:{1u,2u}){
        const double f=440.*std::exp2((note-69)/12.);const auto cut=[&](unsigned rate){return std::min(sp.harmonics,int(std::floor(.45*rate*sp.dominant/f)));};
        const auto a=residual(1,note,ms,mode),b=residual(4,note,ms,mode),c=residual(8,note,ms,mode);double e=0.,raw=0.,low=0.,conv=0.;
        for(std::size_t i=0;i<a.size();++i){auto y=d4.at(b,i),z=d8.at(c,i);e+=square(a[i]);raw+=square(diff(b[4*i],y));low+=square(diff(a[i],y));conv+=square(diff(y,z));}
        const double n=double(a.size());std::cout<<note<<','<<ms<<','<<mode<<','<<cut(48000)<<','<<cut(192000)<<','<<cut(384000)<<','<<(cut(48000)==cut(384000))<<','<<std::sqrt(e/n)<<','<<std::sqrt(raw/n)<<','<<std::sqrt(low/n)<<','<<std::sqrt(conv/n)<<'\n';
    }
}
