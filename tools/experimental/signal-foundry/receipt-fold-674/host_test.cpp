#include "host.hpp"
#include <cstdlib>
#include <thread>
#include <iostream>
using namespace mhac::receipt;
static void check(bool b){if(!b)std::abort();}
static Patch pattern(unsigned i){return {unrank(i%28),static_cast<Mode>(i%4),i%3==0,double(i%1009)/1009};}
static void stress(){
    Host h;check(h.prepare(48000));std::atomic<bool> stop{false};std::atomic<unsigned> blocks{0};
    std::thread audio([&]{while(!stop.load()){h.begin();double l=.9,r=-.8;for(int i=0;i<32;++i){h.frame(l,r);check(std::abs(l)<=1&&std::abs(r)<=1);}h.end();++blocks;}});
    unsigned busy=0;
    for(unsigned i=0;i<30000;++i){auto p=pattern(i);check(h.request(p));Patch q;if(h.snapshot(q))check(save(p)==save(q));else ++busy;}
    stop=true;audio.join();check(blocks>0);h.begin();h.end();Patch q;check(h.snapshot(q)&&save(q)==save(pattern(29999)));
    std::cout<<"state stress: 30000 requests, "<<busy<<" busy saves, "<<blocks<<" audio blocks\n";
}
template<class T> static void stream(double rate){
    Host a,b;check(a.prepare(rate)&&b.prepare(rate));Live ref;check(ref.prepare(rate));
    for(unsigned i=0;i<8192;++i){
        if(i%127==0)a.begin();
        if(i%31==0)b.begin();
        if(i%13==0){const unsigned id=(i/13)%count;const double v=(i%101)/100.;check(a.set(id,v)&&b.set(id,v));auto p=ref.patch();check(control(p,id,v)&&ref.apply(p));}
        T l=static_cast<T>(std::sin(i*.13)),r=static_cast<T>(std::cos(i*.19)),ll=l,rr=r,rl=l,rr2=r;
        a.frame(l,r);b.frame(ll,rr);ref.frame(rl,rr2);check(l==ll&&r==rr&&l==rl&&r==rr2);
        if(i%127==126)a.end();
        if(i%31==30)b.end();
    }
    a.end();Patch p;check(a.snapshot(p)&&save(p)==save(ref.patch()));
    auto next=pattern(7);check(a.request(next));check(a.snapshot(p)&&save(p)==save(next));a.begin();check(save(a.patch())==save(next));a.end();
    check(!a.set(Wet,std::numeric_limits<double>::quiet_NaN()));
}
int main(){
    for(unsigned i=0;i<28;++i){Patch p;check(rank(unrank(i))==i);check(control(p,Action,i/27.)&&rank(p.action)==i);check(normalized(p,Action)==i/27.);}
    for(double r:{8000.,44100.,48000.,96000.,192000.,384000.}){stream<float>(r);stream<double>(r);}
    stress();std::cout<<"98304 paired frames, 28 action ranks, PASS\n";
}
