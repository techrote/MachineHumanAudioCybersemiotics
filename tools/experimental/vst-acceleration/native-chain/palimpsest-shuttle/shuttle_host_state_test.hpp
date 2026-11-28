#pragma once
#include "shuttle_host_state.hpp"
#include <cstdlib>
#include <iostream>
#include <limits>
#include <memory>
namespace mhac::accel {
inline unsigned qualifyShuttleHostState(){
    unsigned checks=0;
    const auto check=[&](bool ok){++checks;if(!ok){std::cerr<<"HOST STATE FAIL "<<checks<<'\n';std::abort();}};
    for(unsigned id=0;id<6;++id)for(unsigned n=0;n<=1000;++n){
        ShuttleHostPatch p{{650,150,180,600,false},500},q{};
        check(applyHostNormalized(p,id,n/1000.));
        check(hostNormalized(p,id)==(id==4?double(n>=500):n/1000.));
        const auto s=encodeHost(p);check(decodeHost(s,hostStateSize(s),q)&&encodeHost(q)==s);
    }
    auto a=std::make_unique<DesktopShuttle>(),b=std::make_unique<DesktopShuttle>();
    ShuttleHostPatch p{{850,1000,400,0,false},1000},q{};
    check(a->prepareRate(48000)&&b->prepareRate(48000));
    check(configureHost(*a,p));a->reset();
    const auto s=encodeHost(p);check(hostStateSize(s)==15&&s[3]=='2');
    for(unsigned n=0;n<15;++n){q=p;check(!decodeHost(s,n,q)&&encodeHost(q)==s);}
    auto bad=s;bad[13]=255;bad[14]=255;check(!decodeHost(bad,15,q));
    for(double v:{-1.,1.1,std::numeric_limits<double>::infinity(),std::numeric_limits<double>::quiet_NaN()})
        check(!applyHostNormalized(p,5,v)&&encodeHost(p)==s);
    check(!applyHostNormalized(p,6,.5));
    check(!configureHost(*a,{{850,1000,400,0,false},1001})&&encodeHost(snapshotHost(*a))==s);
    check(decodeHost(s,15,q)&&configureHost(*b,q));b->reset();
    double side=0;
    for(unsigned n=0;n<20000;++n){
        if(n==1234||n==9001){check(applyHostNormalized(p,5,n==1234?.5:1.));check(configureHost(*a,p)&&configureHost(*b,p));}
        const float v=float(int(n%251)-125)/1024.f;
        const auto x=a->process({v,v}),y=b->process({v,v});
        check(x.l==y.l&&x.r==y.r&&std::isfinite(x.l)&&std::isfinite(x.r));side+=std::abs(x.l-x.r);
    }
    check(side>0);
    const ShuttleHostPatch legacy{{850,1000,400,0,false},0};
    const auto l=encodeHost(legacy);const auto old=encode(legacy.base);
    check(hostStateSize(l)==13&&std::equal(old.begin(),old.end(),l.begin()));
    check(decodeHost(l,13,q)&&q.stagger==0&&configureHost(*a,q));a->reset();
    check(b->configure(legacy.base)&&b->configureStagger(0));b->reset();
    for(unsigned n=0;n<10000;++n){const float v=float(int(n%97)-48)/128.f;const auto x=a->process({v,v}),y=b->process({v,v});check(x.l==y.l&&x.r==y.r);}
    std::cout<<"HOST STATE PASS "<<checks<<" checks\n";return checks;
}
}
