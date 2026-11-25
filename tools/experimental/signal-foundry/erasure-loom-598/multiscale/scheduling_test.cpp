#include "scales.hpp"
#include <chrono>
#include <cstdlib>
#include <iostream>
#include <memory>
#include <limits>
#include <cstdint>
static void check(bool b,const char* s){if(!b){std::cerr<<s<<'\n';std::exit(1);}}
static std::uint32_t next(std::uint32_t& s){s^=s<<13;s^=s>>17;s^=s<<5;return s;}
static double unitRandom(std::uint32_t& s){return double(next(s)%1025)/1024.;}
template<class Engine> void bench(const char* name){
    using clock=std::chrono::steady_clock;
    auto e=std::make_unique<Engine>();e->prepare(48000);
    loom::ProbeParams p{};p.base.separation=1;p.base.rotation=8;p.base.wet=1;p.base.budget=16;p.probe=.6;p.edge=.4;e->set(p,2);e->reset();
    constexpr unsigned block=32,count=9216*48/block;
    double sum=0,peak=0,total=0;
    for(unsigned j=0;j<count;++j){auto start=clock::now();for(unsigned i=0;i<block;++i)sum+=e->step(.04,.03)[0];double us=std::chrono::duration<double,std::micro>(clock::now()-start).count();peak=std::max(peak,us);total+=us;}
    std::cout<<name<<" block32 max_us="<<peak<<" mean_us="<<total/count<<" checksum="<<sum<<'\n';
}
int main(){
    using namespace loom;auto a=std::make_unique<loomscale::Engine>();auto b=std::make_unique<loomscale::BurstReference>();
    std::uint32_t seed=0x598007f;unsigned long long pairs=0;
    for(double rate:{8000.,44100.,48000.,96000.,192000.}){
        check(a->prepare(rate)&&b->prepare(rate),"prepare");
        for(unsigned i=0;i<loomscale::latency*18;++i){
            if(i%97==0){ProbeParams p{};p.base.separation=1+next(seed)%4;p.base.rotation=next(seed)%9;p.base.budget=1+15*unitRandom(seed);p.base.repair=unitRandom(seed);p.base.wet=unitRandom(seed);p.base.gain=unitRandom(seed);p.base.bypass=next(seed)%7==0;p.probe=next(seed)%3?unitRandom(seed):0;p.edge=next(seed)%3?unitRandom(seed):0;auto k=next(seed)%3;a->set(p,k);b->set(p,k);}
            if(i==loomscale::latency*6+113){a->reset();b->reset();}
            double l=2*unitRandom(seed)-1,r=2*unitRandom(seed)-1;if(i%311==0)l=std::numeric_limits<double>::infinity();
            const auto x=a->step(l,r),y=b->step(l,r);check(x==y,"incremental versus burst");check(std::isfinite(x[0])&&std::isfinite(x[1])&&std::abs(x[0])<=1&&std::abs(x[1])<=1,"bounds");++pairs;
        }
    }
    std::cout<<"exact scheduling pairs="<<pairs<<'\n';
    bench<loomscale::BurstReference>("burst");bench<loomscale::Engine>("incremental");
}
