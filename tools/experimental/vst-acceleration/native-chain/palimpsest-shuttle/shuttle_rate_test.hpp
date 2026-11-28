#pragma once
#include "shuttle.hpp"
#include "shuttle_stagger_test.hpp"
#include <cstdlib>
#include <iostream>
#include <limits>
#include <memory>
#include <vector>
namespace mhac::accel {
inline unsigned long long qualifyShuttleRates() {
    unsigned long long checks=0;
    const auto check=[&](bool ok){++checks;if(!ok){std::cerr<<"RATE FAIL "<<checks<<'\n';std::abort();}};
    auto e=std::make_unique<DesktopShuttle>();
    auto f=std::make_unique<DesktopShuttle>();
    const auto equal=[](ShuttleFrame a,ShuttleFrame b){return a.l==b.l&&a.r==b.r;};
    for(double rate:{1000.,1234.568,8000.,12345.678,44100.,48000.,96000.,123456.780,192000.,384000.,1234567.800,2000000.}) {
        check(e->prepareRate(rate));check(f->prepareRate(rate));
        const unsigned g=e->grainSamples();
        check(g==2u*static_cast<unsigned>(std::floor(rate*.04+.5)));
        check(std::abs(double(g)/rate-.08)<=1./rate+1e-12);
        for(unsigned mode:{0u,1000u}) {
            check(e->configure({1000,uint16_t(mode),0,0,false}));e->reset();
            check(f->configure(e->patch()));f->reset();
            std::vector<ShuttleFrame> x(3*g);
            for(unsigned n=0;n<x.size();++n)x[n]={float(int(n%97)-48)/128.f,float(int(n%71)-35)/128.f};
            auto at=[&](int n){return n<0?ShuttleFrame{}:x[unsigned(n)];};
            for(unsigned n=0;n<x.size();++n){
                auto y=e->process(x[n]);
                if(!mode){auto a=at(int(n)-int(g));check(std::abs(y.l-a.l)<2e-7f&&std::abs(y.r-a.r)<2e-7f);}
                else{
                    const unsigned p=n%g,q=(p+g/2)%g;
                    const double w=2.*std::min(p,g-p)/g;
                    const auto a=at(int(n)-int(2*p+1)),b=at(int(n)-int(2*q+1));
                    check(std::abs(y.l-(w*a.l+(1-w)*b.l))<3e-7&&std::abs(y.r-(w*a.r+(1-w)*b.r))<3e-7);
                }
                if(n==g){for(double bad:{0.,999.,2000000.1,std::numeric_limits<double>::infinity(),std::numeric_limits<double>::quiet_NaN()})check(!e->prepareRate(bad));check(e->grainSamples()==g);}
                check(equal(y,f->process(x[n])));
            }
        }
    }
    auto old=std::make_unique<PalimpsestShuttle<>>();
    for(unsigned rate:{8000u,44100u,48000u,96000u,192000u}){
        check(old->prepare(rate));check(e->prepareRate(rate));check(old->grainSamples()==e->grainSamples());
        check(old->configure({350,750,250,500,false}));check(e->configure(old->patch()));old->reset();e->reset();
        for(unsigned n=0;n<4*e->grainSamples();++n){if(n==100){check(old->configure({900,100,1000,800,false}));check(e->configure(old->patch()));}ShuttleFrame x{float(n%31)/64.f,-float(n%19)/64.f};check(equal(old->process(x),e->process(x)));}
    }
    check(!old->prepare(7999));check(!old->prepare(192001));check(!old->prepareRate(384000.));
    qualifyShuttleStagger();
    std::cout<<"RATE PASS "<<checks<<" checks; desktop bytes "<<sizeof(DesktopShuttle)<<'\n';return checks;
}
}
