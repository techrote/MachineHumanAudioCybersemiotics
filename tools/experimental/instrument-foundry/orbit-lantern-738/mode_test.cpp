#include "host.hpp"
#include <cstdlib>
#include <iostream>
#include <limits>
using namespace mhac::orbit;
using namespace mhac::orbit::host;
static unsigned checks=0;
static void check(bool x){++checks;if(!x){std::cerr<<"FAIL "<<checks<<'\n';std::exit(1);}}
int main(){
    for(unsigned mode=0;mode<3;++mode)for(unsigned b=0;b<=1000;++b){
        Patch p{b,10+b%991,int(b%201)-100,mode},q{};
        auto bytes=encodeState(p);check(decodeState(bytes,q)&&pack(p)==pack(q));
        check(pack(unpack(pack(p)))==pack(p));
        bytes[10]=3;check(!decodeState(bytes,q)&&pack(p)==pack(q));
        if(mode==0){check(decode(encode(p),q)&&q.releaseMode==0);}
    }
    for(unsigned depth=0;depth<=1000;++depth)for(unsigned mode=0;mode<3;++mode){
        Patch p{1000,10,0,mode,depth},q{};const auto bytes=encodeFull(p);
        check(decodeFull(bytes,stateSize(p),q)&&pack(p)==pack(q));
        check(pack(unpack(pack(p)))==pack(p));
        if(depth){auto bad=bytes;bad[12]=255;check(!decodeFull(bad,13,q)&&pack(p)==pack(q));check(!decodeFull(bytes,11,q));}
    }
    Live live; Bridge mailbox;check(live.prepare(48000));
    for(unsigned mode=0;mode<3;++mode){
        Patch p{1000,800,0,mode};check(mailbox.request(p));auto token=mailbox.begin(live);check(pack(live.patch())==pack(p));
        check(live.parameter(3,normalized(p,3)));mailbox.end(token,live);check(pack(mailbox.save())==pack(p));
    }
    check(!live.parameter(3,std::numeric_limits<double>::quiet_NaN()));
    for(double rate:{1000.,1234.568,48000.,96000.,1234567.8,2000000.})for(unsigned mode=0;mode<3;++mode){
        check(live.prepare(rate));Patch p{1000,10,0,0};check(live.setPatch(p));
        escape::Instrument ref;check(ref.prepare(rate)&&ref.setPatch(p));
        check(live.on(7,0,60,0,.8)&&ref.on(7,60,.8));
        double l=0,r=0,x=0,y=0;const auto sustain=unsigned(std::ceil(rate*.007));
        for(unsigned i=0;i<sustain;++i){live.tick(l,r);ref.tick(x,y);check(l==x&&r==y);}
        check(live.parameter(3,mode/2.));check(live.off(7,0,60));
        check(mode==2?ref.offPhase(7):ref.off(7,mode==1));
        for(unsigned i=0;i<unsigned(std::ceil(rate*.01));++i){
            if(i==1){check(live.parameter(3,(2-mode)/2.));check(live.off(7,0,60));}
            live.tick(l,r);ref.tick(x,y);check(std::abs(l-x)<1e-12&&std::abs(r-y)<1e-12&&std::abs(l)<=.52&&std::abs(r)<=.52);
        }
        check(live.active()==0&&l==0&&r==0);
    }
    // Parameter admission at note-off matches the native experimental oracle.
    for(unsigned mode=0;mode<3;++mode){
        Live a,b;check(a.prepare(48000)&&b.prepare(48000));
        check(a.setPatch({1000,100,0,mode})&&b.setPatch({1000,100,0,mode}));
        check(a.on(1,0,48,0.,.8)&&b.on(1,0,48,0.,.8));
        double l=0,r=0,x=0,y=0;bool difference=false;
        for(int i=0;i<500;++i){a.tick(l,r);b.tick(x,y);check(l==x&&r==y);}
        check(a.parameter(4,1.)&&a.off(1,0,48));
        check(mode==2?b.offSpectral(1,0,48,1.):b.off(1,0,48));
        check(a.parameter(4,0.)&&a.off(1,0,48));
        for(int i=0;i<4800;++i){a.tick(l,r);b.tick(x,y);difference|=l!=x||r!=y;check(std::isfinite(l)&&std::isfinite(r)&&std::abs(l)<=.52&&std::abs(r)<=.52);if(mode!=1)check(l==x&&r==y);}
        check(difference==(mode==1));check(a.active()==0&&b.active()==0&&l==0&&r==0);
    }
    check(!live.parameter(4,std::numeric_limits<double>::quiet_NaN()));
    // A concurrent state request must survive a stale audio publication.
    auto t=mailbox.begin(live);check(live.parameter(3,1.));check(mailbox.request({0,10,-100,1}));mailbox.end(t,live);
    check(mailbox.save().releaseMode==1);t=mailbox.begin(live);check(live.patch().releaseMode==1);mailbox.end(t,live);
    std::cout<<"PASS mode checks="<<checks<<'\n';
}
