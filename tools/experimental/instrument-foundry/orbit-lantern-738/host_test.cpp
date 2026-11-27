#include "host.hpp"
#include <cstdlib>
#include <iostream>
#include <limits>
#include <thread>
using namespace mhac::orbit;
using namespace mhac::orbit::host;
static unsigned checks=0;
static void check(bool ok){++checks;if(!ok){std::cerr<<"FAIL "<<checks<<'\n';std::exit(1);}}
static bool same(Patch a,Patch b){return pack(a)==pack(b);}
static void rateTests(){
    Live e;check(e.prepare(48000));check(e.on(1,0,69,0,1));
    for(double rate:{0.,999.,2000001.,std::numeric_limits<double>::infinity(),std::numeric_limits<double>::quiet_NaN()}){
        check(!validSampleRate(rate));check(!e.prepare(rate));check(e.active()==1);
    }
    for(double rate:{1000.,1234.568,8000.,384000.,1234567.8,2000000.}){
        check(validSampleRate(rate));check(e.prepare(rate));check(e.active()==0);
        for(unsigned blend:{0u,500u,1000u}){
            check(e.setPatch({blend,10,0}));check(e.on(1,0,69,0,1));
            if(rate<2000.)check(!e.on(2,0,127,0,1));
            double l=0,r=0;double peak=0;
            for(unsigned i=0;i<unsigned(std::ceil(.006*rate));++i){e.tick(l,r);check(std::isfinite(l)&&std::isfinite(r)&&std::abs(l)<=.52&&std::abs(r)<=.52);peak=std::max({peak,std::abs(l),std::abs(r)});}
            check(peak>0);check(e.off(1,0,69));
            for(unsigned i=0;i<unsigned(std::ceil(.01*rate));++i)e.tick(l,r);
            check(e.active()==0&&l==0&&r==0);
        }
    }
}
static void retriggerTests(){
    // Fallback note IDs must behave like distinct explicit IDs for a legal
    // sequence of nonoverlapping key holds with overlapping release tails.
    for(double rate:{8000.,44100.,48000.,96000.})for(unsigned mode:{0u,1u,2u}){
        Live a,b;check(a.prepare(rate)&&b.prepare(rate));
        const Patch p{1000,800,0,mode,1000};check(a.setPatch(p)&&b.setPatch(p));
        double l=0,r=0,x=0,y=0;unsigned n=unsigned(rate/100.);
        const auto advance=[&](unsigned frames){for(unsigned j=0;j<frames;++j){a.tick(l,r);b.tick(x,y);check(l==x&&r==y&&std::isfinite(l)&&std::isfinite(r));}};
        for(int i=0;i<8;++i){
            check(a.on(-1,2,69,0,.8)&&b.on(i,2,69,0,.8));
            check(!a.on(-1,2,69,0,.8));advance(n);
            if(i%2==0)check(a.on(-1,2,69,0,0)&&b.off(i,2,69));
            else check(a.offSpectral(-1,2,69,.5)&&b.offSpectral(i,2,69,.5));
            check(a.active()==unsigned(i+1)&&a.active()==b.active());advance(n);
        }
        check(!a.on(-1,2,69,0,.8)&&!b.on(8,2,69,0,.8));
        advance(unsigned(rate));check(a.active()==0&&b.active()==0&&l==0&&r==0);
        check(a.on(-1,2,69,0,.8)&&a.on(-1,3,69,0,.8));
        check(a.off(-1,2,69)&&a.off(-1,2,69));
        check(a.on(-1,2,69,0,.8)&&a.off(-1,2,69));
        for(unsigned i=0;i<unsigned(rate);++i)a.tick(l,r);
        check(a.active()==1);check(a.off(-1,3,69));
        for(unsigned i=0;i<unsigned(rate);++i)a.tick(l,r);
        check(a.active()==0&&l==0&&r==0);
        check(a.on(9,2,69,0,.8)&&a.off(9,2,69)&&!a.on(9,2,69,0,.8));
        a.reset();check(a.on(-1,2,69,0,.8));a.reset();check(a.active()==0);
    }
}
int main(){
    retriggerTests();
    rateTests();
    Live e;Bridge state;check(e.prepare(48000));
    for(unsigned b=0;b<=1000;++b){Patch p{b,10+b%991,int(b%201)-100};
        check(state.request(p)&&same(state.save(),p));auto t=state.begin(e);check(same(e.patch(),p));
        for(unsigned i=0;i<count;++i)check(e.parameter(i,normalized(p,i)));
        state.end(t,e);check(same(state.save(),p));}
    check(!state.request({1001,160,0}));check(!e.parameter(5,.5));check(!e.parameter(0,std::numeric_limits<double>::quiet_NaN()));
    auto t=state.begin(e);check(e.parameter(0,.25));check(state.request({750,10,0}));state.end(t,e);check(state.save().blend==750);
    t=state.begin(e);check(e.patch().blend==750);state.end(t,e);
    check(e.on(-1,0,60,0,1)&&e.on(-1,1,60,0,1)&&e.on(0,0,60,0,1));
    check(!e.on(-1,0,60,0,1)&&!e.on(0,1,61,0,1));
    check(!e.on(-2,0,60,0,1)&&!e.on(1,16,60,0,1)&&!e.on(1,0,60,1300,1));
    double l=0,r=0;for(int i=0;i<500;++i)e.tick(l,r);
    check(e.off(-1,0,60)&&e.on(-1,1,60,0,0)&&e.off(0,0,60));
    for(int i=0;i<480;++i)e.tick(l,r);
    check(e.active()==0&&l==0&&r==0);check(e.on(-1,0,60,0,1));e.reset();check(e.active()==0);
    // Native oracle: host mapping must preserve exact stereo samples with tuning.
    Engine ref;check(ref.prepare(48000));check(ref.setPatch({750,10,0}));
    check(e.on(2147483647,0,60,25,0.8)&&ref.noteOn(0,60,.8,25));
    for(int i=0;i<2000;++i){double x=0,y=0;if(i==1000)check(e.off(2147483647,0,60)&&ref.noteOff(0));e.tick(l,r);ref.tick(x,y);check(l==x&&r==y);}
    check(e.active()==0);for(int i=0;i<8;++i)check(e.on(i,0,60+i,0,1));check(!e.on(8,0,72,0,1));e.reset();
    // Concurrent state producer; every observed patch must be one coherent request.
    const Patch a{0,10,-100,1,1000},b{1000,1000,100,2,17};check(state.request(a));t=state.begin(e);state.end(t,e);
    std::atomic<bool> go{false};std::thread producer([&]{while(!go.load()){}for(int i=0;i<30000;++i)state.request(i%2?a:b);});
    go.store(true);for(int i=0;i<30000;++i){auto token=state.begin(e);auto p=e.patch();check(same(p,a)||same(p,b));state.end(token,e);p=state.save();check(same(p,a)||same(p,b));}
    producer.join();t=state.begin(e);state.end(t,e);check(same(state.save(),a));
    std::cout<<"PASS host checks="<<checks<<'\n';
}
