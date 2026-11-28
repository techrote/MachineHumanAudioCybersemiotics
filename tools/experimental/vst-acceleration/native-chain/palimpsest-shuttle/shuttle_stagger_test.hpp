#pragma once
#include "shuttle.hpp"
#include <cstdlib>
#include <iostream>
#include <limits>
#include <memory>
#include <vector>
namespace mhac::accel {
inline unsigned long long qualifyShuttleStagger() {
    unsigned long long checks=0;
    const auto check=[&](bool ok){++checks;if(!ok){std::cerr<<"STAGGER FAIL "<<checks<<'\n';std::abort();}};
    auto a=std::make_unique<DesktopShuttle>(), b=std::make_unique<DesktopShuttle>();
    for(double rate:{1000.,1234.568,44100.,48000.,96000.,192000.,384000.,2000000.}) {
        check(a->prepareRate(rate)&&b->prepareRate(rate));
        const unsigned g=a->grainSamples();
        std::vector<float> x(3*g);
        for(unsigned n=0;n<x.size();++n)x[n]=float(int(n*17u%251u)-125)/256.f;
        const auto at=[&](int n){return n<0?0.f:x[unsigned(n)];};
        const auto reverseAt=[&](unsigned n,unsigned p){
            const unsigned q=(p+g/2)%g;
            const double w=2.*std::min(p,g-p)/g;
            return w*at(int(n)-int(2*p+1))+(1.-w)*at(int(n)-int(2*q+1));
        };
        for(unsigned amount:{0u,250u,1000u}) {
            check(a->configure({1000,1000,0,0,false})&&a->configureStagger(amount));
            a->reset(); check(a->stagger()==amount&&!a->configureStagger(1001)&&a->stagger()==amount);
            double separation=0.;
            for(unsigned n=0;n<x.size();++n){
                const unsigned p=n%g,s=(p+g/4)%g;
                const double l=reverseAt(n,p), r=l+(reverseAt(n,s)-l)*amount/1000.;
                const auto y=a->process({x[n],x[n]});
                check(std::abs(y.l-l)<5e-7&&std::abs(y.r-r)<5e-7);
                separation+=std::abs(y.l-y.r);
            }
            check(amount?separation>0.:separation==0.);
        }
        for(bool bypass:{false,true}) {
            const ShuttlePatch p{1000,0,1000,1000,bypass};
            check(a->configure(p)&&b->configure(p)&&a->configureStagger(1000)&&b->configureStagger(0));a->reset();b->reset();
            for(float v:x){const auto y=a->process({v,-v}),z=b->process({v,-v});check(y.l==z.l&&y.r==z.r);}
        }
        const ShuttlePatch p{850,1000,1000,750,false};
        check(a->configure(p)&&b->configure(p)&&a->configureStagger(0)&&b->configureStagger(0));a->reset();b->reset();
        std::vector<ShuttleFrame> reference(x.size());
        const auto step=[&](DesktopShuttle& e,unsigned n){
            if(n==g)check(e.configureStagger(1000));
            if(n==2*g)check(e.configureStagger(0));
            return e.process({x[n],-x[n]});
        };
        for(unsigned n=0;n<x.size();++n){const auto y=step(*a,n);reference[n]=y;check(std::isfinite(y.l)&&std::isfinite(y.r)&&std::abs(y.l)<=1.f&&std::abs(y.r)<=1.f);}
        for(unsigned pos=0;pos<x.size();){const unsigned end=std::min(unsigned(x.size()),pos+1+pos%127);for(;pos<end;++pos){const auto y=step(*b,pos);check(y.l==reference[pos].l&&y.r==reference[pos].r);}}
        auto y=a->process({std::numeric_limits<float>::infinity(),std::numeric_limits<float>::quiet_NaN()});check(std::isfinite(y.l)&&std::isfinite(y.r));
    }
    std::cout<<"STAGGER PASS "<<checks<<" checks\n";return checks;
}
}
