// Offline diagnostic: paired spectral-depth residual, not a real-time FFT.
#include "host.hpp"
#include <complex>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <vector>
using namespace mhac::orbit;
using mhac::orbit::host::Live;
static void require(bool ok){if(!ok){std::cerr<<"FAIL sideband probe\n";std::exit(1);}}
using Complex=std::complex<double>;
static void fft(std::vector<Complex>& x){
    const auto n=x.size();require(n>1&&(n&(n-1))==0);
    for(std::size_t i=1,j=0;i<n;++i){
        std::size_t bit=n>>1;
        for(;j&bit;bit>>=1)j^=bit;
        j^=bit;if(i<j)std::swap(x[i],x[j]);
    }
    for(std::size_t len=2;len<=n;len*=2){
        const Complex wstep=std::polar(1.,-tau/double(len));
        for(std::size_t i=0;i<n;i+=len){Complex w(1.,0.);
            for(std::size_t j=0;j<len/2;++j){
                const auto a=x[i+j],b=x[i+j+len/2]*w;
                x[i+j]=a+b;x[i+j+len/2]=a-b;w*=wstep;
            }
        }
        if(len==n)break;
    }
}
struct Energy {double total=0.,above=0.;};
static Energy measure(const std::vector<double>& s,unsigned rate,double threshold){
    std::size_t n=2;while(n<s.size())n*=2;
    std::vector<Complex> x(n);double time=0.;
    for(std::size_t i=0;i<s.size();++i){x[i]=s[i];time+=s[i]*s[i];}
    fft(x);Energy e;
    for(std::size_t i=0;i<n;++i){const double p=std::norm(x[i])/double(n);
        e.total+=p;if(double(std::min(i,n-i))*rate/double(n)>threshold)e.above+=p;
    }
    require(std::abs(time-e.total)<=1e-8*std::max(1.,time));return e;
}
static void oracle(){
    std::vector<double> s(1024);
    for(std::size_t i=0;i<s.size();++i)s[i]=std::sin(tau*16.*double(i)/1024.)+.5*std::cos(tau*256.*double(i)/1024.);
    auto e=measure(s,1024,128.);
    require(std::abs(e.total-640.)<1e-8&&std::abs(e.above-128.)<1e-8);
    std::fill(s.begin(),s.end(),0.);e=measure(s,1024,128.);require(e.total==0.&&e.above==0.);
}
static Energy probe(unsigned rate,int note,unsigned ms,unsigned mode,unsigned offset){
    Live a,b;require(a.prepare(rate)&&b.prepare(rate));
    require(a.setPatch({1000,ms,0,mode,0})&&b.setPatch({1000,ms,0,mode,1000}));
    require(a.on(1,0,note,0.,.8)&&b.on(1,0,note,0.,.8));
    double l=0,r=0,x=0,y=0;
    for(unsigned i=0;i<rate/10+offset*(rate/48000);++i){a.tick(l,r);b.tick(x,y);require(l==x&&r==y);}
    require(a.off(1,0,note)&&b.off(1,0,note));
    const unsigned samples=rate*ms/1000+8;
    std::vector<double> dl(samples),dr(samples);
    for(unsigned i=0;i<samples;++i){a.tick(l,r);b.tick(x,y);
        require(std::isfinite(l)&&std::isfinite(r)&&std::isfinite(x)&&std::isfinite(y));
        require(std::abs(l)<=.52&&std::abs(r)<=.52&&std::abs(x)<=.52&&std::abs(y)<=.52);
        dl[i]=x-l;dr[i]=y-r;
    }
    require(a.active()==0&&b.active()==0&&l==0.&&r==0.&&x==0.&&y==0.);
    auto e=measure(dl,rate,24000.);auto f=measure(dr,rate,24000.);
    return { (e.total+f.total)/(2.*samples), (e.above+f.above)/(2.*samples) };
}
int main(){
    oracle();Spectrum spectrum;require(spectrum.build<68>({-16,4},8,4,9));
    std::cout<<"rate,note,release_ms,mode,offset,cutoff_matched,cutoff,dominant,residual_rms,above_24k_fraction\n"<<std::setprecision(12);
    for(int note:{69,93,105,117,125})for(unsigned ms:{10u,80u,800u})for(unsigned mode:{0u,1u,2u})for(unsigned offset:{17u,53u}){
        const double freq=440.*std::exp2((note-69)/12.);
        const auto cut=[&](unsigned rate){return std::min(spectrum.harmonics,int(std::floor(.45*rate*spectrum.dominant/freq)));};
        for(unsigned rate:{48000u,192000u}){
            const auto e=probe(rate,note,ms,mode,offset);
            if(mode==0||cut(rate)<2*spectrum.dominant)require(e.total==0.);
            else require(e.total>0.);
            std::cout<<rate<<','<<note<<','<<ms<<','<<mode<<','<<offset<<','<<(cut(48000)==cut(192000))<<','<<cut(rate)<<','<<spectrum.dominant<<','<<std::sqrt(e.total)<<','<<(e.total?e.above/e.total:0.)<<'\n';
        }
    }
}
