#include "live.hpp"
#include <cstdlib>
#include <iostream>
#include <chrono>
using namespace prism;
void check(bool b,const char* why){if(!b){std::cerr<<why<<'\n';std::exit(1);}}
C tone(std::size_t t,std::size_t n,unsigned g){C x{};for(unsigned j=1;j<4;++j)x+=std::polar(.18,tau*bins[j]*g*double(t%n)/double(n));return x;}
int main(){
    LivePrism p;check(!p.prepare(0),"invalid rate");check(p.step(1,1)==C{},"unprepared");double maxResidual=0,maxError=0;std::size_t cases=0;
    for(double sr:{1000.,1234.5678,8000.,44100.,48000.,96000.,192000.,384000.,1234567.8,2000000.}){
        check(p.prepare(sr),"prepare");auto n=p.latency();check(n>=96&&n<=25000&&p.tailBound()==3*n,"bounds");
        for(unsigned grid=0;grid<3;++grid)for(double cancel:{0.,.5,1.}){
            p.restore({1,cancel,1,1,grid*.5,0});p.reset();C c{};const unsigned g=1u<<grid;
            for(std::size_t t=0;t<4*n;++t){auto x=tone(t,n,g),y=p.step(x.real(),x.imag());if(t>=3*n)c+=y*std::polar(1.,-tau*bins[0]*g*double(t%n)/double(n));}
            c/=double(n);double err=std::abs(c-C(.011664*(1-cancel)));check(err<2e-13,"coefficient oracle");maxError=std::max(maxError,err);if(cancel==1)maxResidual=std::max(maxResidual,std::abs(c));++cases;
            for(std::size_t t=0;t<3*n;++t)p.step(0,0);
            check(p.step(0,0)==C{},"tail");
        }
        p.restore({1,1,1,1,1,1});p.reset();for(std::size_t t=0;t<2*n;++t){p.set(Grid,double(t%3)*.5);check(p.step(t==0?.25:0,0)==C(t==n?.25:0,0),"bypass impulse");}
    }
    check(p.prepare(48000),"rate reset");Prism old;check(old.prepare(48000),"legacy prepare");p.restore({.75,.5,.5,.5,0,0});p.reset();old.set({.5,.5,.5,.5});old.reset();double legacy=0;
    for(std::size_t t=0;t<12000;++t){auto x=tone(t,p.latency(),1),a=p.step(x.real(),x.imag()),b=old.step(x.real(),x.imag());legacy=std::max(legacy,std::abs(a-b));}check(legacy<2e-13,"legacy reference");
    LivePrism a,b;check(a.prepare(48000)&&b.prepare(48000),"partition prepare");a.restore({1,0,1,.7,0,0});b.restore(a.params());a.reset();b.reset();
    auto render=[](LivePrism& e,std::size_t t){if(t%173==0)e.set(Grid,double((t/173)%3)*.5);if(t%503==0)e.set(Bypass,double((t/503)%2));auto x=tone(t,e.latency(),1)+tone(t,e.latency(),2)*.25;return e.step(x.real(),x.imag());};
    std::vector<C> reference;for(std::size_t t=0;t<16384;++t)reference.push_back(render(a,t));std::size_t t=0;for(unsigned block=1;t<reference.size();block=block%257+17)for(unsigned j=0;j<block&&t<reference.size();++j,++t)check(render(b,t)==reference[t],"partition invariance");
    const auto state=encode({1,.5,.25,.75,1,0});LiveParams q{};check(decode(state.data(),state.size(),q)&&q==LiveParams{1,.5,.25,.75,1,0},"state roundtrip");auto bad=state;bad[4]=0;bad[5]=0;bad[6]=128;bad[7]=127;check(!decode(bad.data(),bad.size(),q)&&!decode(state.data(),state.size()-1,q),"corrupt state");
    p.set(Bypass,0);p.set(Wet,1);p.set(Gain,1);p.reset();for(unsigned i=0;i<4000;++i){auto y=p.step(i%2?1e300:std::numeric_limits<double>::quiet_NaN(),-1e300);check(std::isfinite(y.real())&&std::isfinite(y.imag())&&std::abs(y.real())<=1&&std::abs(y.imag())<=1,"finite output");}
    const auto start=std::chrono::steady_clock::now();double sink=0;for(unsigned i=0;i<480000;++i)sink+=p.step(.1,.2).real();const auto elapsed=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
    std::cout<<"grid/rate/cancel cases="<<cases<<" max residual="<<maxResidual<<" max error="<<maxError<<" legacy difference="<<legacy<<" 10s render time="<<elapsed<<" sink="<<sink<<'\n';
}
