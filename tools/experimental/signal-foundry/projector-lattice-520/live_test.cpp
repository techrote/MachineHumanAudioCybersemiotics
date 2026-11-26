#include "live.hpp"
#include <chrono>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
using namespace mhac::lattice;
static unsigned checks=0;
static void ck(bool b){++checks;if(!b)throw std::runtime_error("live check "+std::to_string(checks));}
static Frame signal(unsigned n){return {.03*std::sin(n*.031),.04*std::cos(n*.017)};}
static void change(Live& e){e.set(Axis1,0);e.set(Axis2,1);e.set(Delay1,1);e.set(Inverse,1);}
int main(){
    Params p{};auto s=encode(defaults);ck(decode(s,p)&&p==defaults);auto bad=s;bad[4]=4;ck(!decode(bad,p)&&p==defaults);bad=s;bad[2]=2;ck(!decode(bad,p));
    for(double sr:{8000.,44100.,48000.,96000.,192000.,384000.}){
        Live e,ref,old;e.set(Mix,1);old.set(Mix,1);ref.set(Mix,1);change(ref);e.reset(sr);old.reset(sr);ref.reset(sr);
        const unsigned warm=1024+127+256+511, fade=unsigned(std::lround(sr*.005));
        for(unsigned n=0;n<12000;++n){if(n==300)change(e);auto x=signal(n);auto a=e.process(x.l,x.r),b=ref.process(x.l,x.r),c=old.process(x.l,x.r);
            if(n<300+warm)ck(a==c);else if(n>=300+warm+fade)ck(a==b&&!e.transitioning());else {double t=double(n-(300+warm)+1)/fade;for(unsigned j=0;j<2;++j)ck(std::abs(a[j]-(c[j]+(b[j]-c[j])*t))<1e-15);}}
        e.set(Bypass,1);for(unsigned n=0;n<fade+2;++n)e.process(.01,-.01);ck(e.process(.01,-.01)==(std::array<double,2>{.01,-.01}));
        e.set(Mix,std::numeric_limits<double>::quiet_NaN());ck(e.params()[Mix]==1);
        for(unsigned n=0;n<4096;++n)e.process(0.,0.);ck(e.process(0.,0.)==(std::array<double,2>{}));
    }
    Live a,b;for(unsigned n=0;n<10000;++n){if(n%11==0){a.set(Delay1,(n%1024)/1023.);b.set(Delay1,(n%1024)/1023.);}auto x=signal(n);ck(a.process(float(x.l),float(x.r))==b.process(float(x.l),float(x.r)));}
    for(unsigned n=0;n<15000;++n){auto y=a.process(0.f,0.f);if(n>=4096)ck(y==(std::array<float,2>{}));}ck(!a.transitioning());
    auto start=std::chrono::steady_clock::now();double sum=0;for(unsigned n=0;n<2000000;++n){if(n%4096==0)b.set(Inverse,(n/4096)%2);auto y=b.process(.02,-.01);sum+=y[0];}auto sec=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
    std::cout<<checks<<" live assertions; benchmark seconds="<<sec<<" checksum="<<sum<<"\n";
}
