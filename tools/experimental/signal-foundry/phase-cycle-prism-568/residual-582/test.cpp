#include "residual.hpp"
#include <cstdlib>
#include <iostream>
#include <random>
using namespace prism;
void check(bool b,const char* s){if(!b){std::cerr<<s<<'\n';std::exit(1);}}
C tone(std::size_t t,std::size_t n,unsigned k,double amp){return std::polar(amp,tau*k*double(t%n)/double(n));}
void config(ResidualPrism& p,double drive,double cancel,double retention,unsigned grid=0){
    p.set(Drive,drive);p.set(Cancel,cancel);p.set(Wet,1);p.set(Gain,1);p.set(Grid,grid*.5);p.set(Bypass,0);p.set(Count,retention);p.reset();
}
int main(){
    ResidualPrism p;check(!p.prepare(0)&&p.step(1,1)==C{},"unprepared");
    double maxLegacy=0,maxFalse=0,maxOff=0;std::size_t neutral=0,cases=0;
    for(double sr:{1000.,1234.5678,8000.,44100.,48000.,96000.,192000.,384000.,1234567.8,2000000.}){
        check(p.prepare(sr),"prepare");const auto n=p.latency();
        config(p,.5,1,1);std::mt19937 rng(582);std::vector<C> input(3*n);
        for(std::size_t t=0;t<input.size();++t){input[t]={double(int(rng()%2001)-1000)/2000.,double(int(rng()%2001)-1000)/2000.};p.set(Grid,double((t/31)%3)*.5);check(p.step(input[t].real(),input[t].imag())==(t<n?C{}:input[t-n]),"exact neutral under grid changes");++neutral;}
        for(unsigned g=0;g<3;++g)for(double cancel:{0.,.5,1.}){
            config(p,1,cancel,1,g);const unsigned f=1u<<g;C phantom{},off{};
            for(std::size_t t=0;t<4*n;++t){C x=tone(t,n,3,.11);for(unsigned j=1;j<4;++j)x+=tone(t,n,unsigned(bins[j])*f,.18);auto y=p.step(x.real(),x.imag());if(t>=3*n){phantom+=y*std::conj(tone(t,n,5*f,1));off+=y*std::conj(tone(t,n,3,1));}}
            phantom/=double(n);off/=double(n);const double e=std::abs(phantom-C(.011664*(1-cancel)));const double o=std::abs(off-C(.11));maxFalse=std::max(maxFalse,e);maxOff=std::max(maxOff,o);check(e<2e-13&&o<2e-13,"coherent witness and unmodeled carrier");++cases;
            for(std::size_t t=0;t<3*n;++t){p.step(0,0);}check(p.step(0,0)==C{},"tail");
        }
    }
    check(p.prepare(48000),"prepare legacy");LivePrism old;check(old.prepare(48000),"old prepare");config(p,1,.5,0);old.restore({1,.5,1,1,0,0});old.reset();
    for(std::size_t t=0;t<12000;++t){if(t%731==0){double v=double((t/731)%3)*.5;p.set(Grid,v);old.set(Grid,v);}auto x=tone(t,600,6,.18)+tone(t,600,9,.18)+tone(t,600,3,.11);auto a=p.step(x.real(),x.imag()),b=old.step(x.real(),x.imag());maxLegacy=std::max(maxLegacy,std::abs(a-b));}check(maxLegacy<2e-13,"legacy equivalence");
    config(p,1,0,1);p.set(Bypass,1);p.reset();for(std::size_t t=0;t<1200;++t)check(p.step(t==0?.5:0,0)==C(t==600?.5:0,0),"bypass impulse");
    config(p,1,0,1);for(unsigned t=0;t<5000;++t){p.set(Count,double(t%3)*.5);p.set(Bypass,double(t%2));auto y=p.step(t%2?1e300:std::numeric_limits<double>::quiet_NaN(),-1e300);check(std::isfinite(y.real())&&std::isfinite(y.imag())&&std::abs(y.real())<=1&&std::abs(y.imag())<=1,"finite output");}
    std::cout<<"neutral exact frames="<<neutral<<" coherent cases="<<cases<<" max phantom error="<<maxFalse<<" max off-grid error="<<maxOff<<" max legacy difference="<<maxLegacy<<'\n';
}
