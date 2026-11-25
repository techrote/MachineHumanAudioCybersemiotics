#include "retreat.hpp"
#include <cstdlib>
#include <iostream>
using namespace mhac::retreat;
static unsigned long long checks=0;
static void check(bool ok){++checks;if(!ok){std::cerr<<"failed "<<checks<<'\n';std::exit(1);}}
int main(){
    for(double sr:{1000.,1234.568,44100.,48000.,96000.,192000.,1234567.8,2000000.}){
        Detector d;const double k=Detector::coefficient(sr,.01);const unsigned n=unsigned(sr*.01);
        for(unsigned i=0;i<n;++i)d.step(1.,k,k);
        check(std::abs(d.value-(-std::expm1(-double(n)/(sr*.01))))<1e-10);
        const double start=d.value;for(unsigned i=0;i<n;++i)d.step(0.,k,k);
        check(std::abs(d.value-start*std::exp(-double(n)/(sr*.01)))<1e-10);
        Engine dry,env;dry.reset(sr);env.reset(sr);env.set(Release,.2);
        dry.process(0,1.);env.process(0,1.);dry.process(0,0.);env.process(0,0.);
        check(dry.mass(0)==0.&&env.mass(0)>=.875&&env.mass(1)==0.);
        for(unsigned i=0;i<unsigned(sr*.6)+1;++i){check(env.process(0,0.)==0.);}
        check(env.mass(0)==0.);
        env.reset(sr);check(env.mass(0)==0.&&env.mass(1)==0.);
        for(unsigned i=0;i<4096;++i){double x=std::sin(i*.07);if(i%101==0)env.set(Attack,(i%100)/100.);auto y=env.process(0,x);check(std::isfinite(y)&&std::abs(y)<=std::abs(x));auto z=env.process(1,float(x));check(std::isfinite(z)&&std::abs(z)<=std::abs(float(x)));}
    }
    auto p=defaults;p[Drive]=.5;p[Attack]=.25;p[Release]=.2;auto s=encode(p);Params q{};
    check(decode(s,q)&&q==p);check(!decode(s,q,legacySize)&&q==p);
    put(s,4,1);check(decode(s,q,legacySize)&&q[Drive]==.5&&q[Attack]==0.&&q[Release]==0.);
    check(!decode(s,q));put(s,4,3);check(!decode(s,q,legacySize));
    Engine a,b;b.set(Release,.2);unsigned ca=0,cb=0;
    double ea=0.,eb=0.;for(unsigned i=0;i<48000;++i){double x=.95*std::sin(6.283185307179586*100*i/48000.);auto y=a.process(0,x),z=b.process(0,x);if(i>=24000){ca+=a.mass(0)>0.;cb+=b.mass(0)>0.;ea+=y*y;eb+=z*z;}}
    check(cb==24000&&ca<cb);std::cout<<"checks="<<checks<<" active="<<ca<<","<<cb<<" rms="<<std::sqrt(ea/24000)<<","<<std::sqrt(eb/24000)<<'\n';
}
