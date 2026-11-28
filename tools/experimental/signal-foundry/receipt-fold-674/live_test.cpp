#include "receipt_live.hpp"
#include <cstdlib>
#include <iostream>
#include <fstream>
#include <string>
using namespace mhac::receipt;
static void check(bool ok){if(!ok)std::abort();}
static void put(std::ofstream& f,unsigned v,unsigned n){for(unsigned j=0;j<n;++j)f.put(static_cast<char>((v>>(8*j))&255));}
static void render(bool smooth,const char* name){
    constexpr unsigned n=48000*2;std::ofstream f(name,std::ios::binary);
    f.write("RIFF",4);put(f,36+4*n,4);f.write("WAVEfmt ",8);put(f,16,4);put(f,1,2);put(f,2,2);put(f,48000,4);put(f,192000,4);put(f,4,2);put(f,16,2);f.write("data",4);put(f,4*n,4);
    Live a;Engine b;a.prepare(48000);b.prepare(48000);Patch p{{0,7},Mode::preview,false,1};a.apply(p);b.setAction(0,7);b.setWet(1);
    for(unsigned i=0;i<n;++i){if(i%6000==0){p.mode=(i/6000)%2?Mode::absent:Mode::preview;a.apply(p);b.setMode(p.mode);}
        const double t=i/48000.,env=std::max(0.,std::min({1.,t*20,(1.9-t)*20}));
        double l=env*.9*std::sin(6.283185307179586*110*t),r=env*.9*std::sin(6.283185307179586*165*t);
        if(smooth)a.frame(l,r);else b.frame(l,r);
        put(f,static_cast<unsigned>(static_cast<int>(l*32767)),2);put(f,static_cast<unsigned>(static_cast<int>(r*32767)),2);}
    check(bool(f));
}
template<class T> static void test(double rate){
    const auto n=static_cast<unsigned>(std::ceil(rate*.005));Live a,b;check(a.prepare(rate)&&b.prepare(rate));
    Patch p{{0,7},Mode::preview,false,1};check(a.apply(p)&&b.apply(p));
    for(unsigned i=0;i<n+1;++i){T l=T(.9),r=T(.9);a.frame(l,r);b.frame(l,r);}
    p.mode=Mode::absent;check(a.apply(p)&&b.apply(p));double previous=.4375;
    for(unsigned i=0;i<n;++i){T l=T(.9),r=T(.9),ll=l,rr=r;check(b.apply(p));a.frame(l,r);b.frame(ll,rr);
        check(l==r&&l==ll&&r==rr&&std::abs(double(l)-previous)<=.875/n+1e-7);previous=l;}
    check(previous==-.4375);
    // Retarget every three samples, including bypass and malformed audio.
    for(unsigned i=0;i<4096;++i){if(i%3==0){p.mode=static_cast<Mode>((i/3)%4);p.action=pair(i%8,(i/8)%8);p.bypass=i%7==0;check(a.apply(p)&&b.apply(p));}
        T l=static_cast<T>(std::sin(i*.19)),r=static_cast<T>(std::cos(i*.31)),ll=l,rr=r;a.frame(l,r);b.frame(ll,rr);check(l==ll&&r==rr&&std::abs(l)<=1&&std::abs(r)<=1);}
    T l=std::numeric_limits<T>::infinity(),r=std::numeric_limits<T>::quiet_NaN();a.frame(l,r);check(l==0&&r==0);
    p.bypass=true;check(a.apply(p));for(unsigned i=0;i<n+2;++i){l=T(.625);r=T(-.75);a.frame(l,r);}check(l==T(.625)&&r==T(-.75));
    a.reset();l=0;r=0;a.frame(l,r);check(l==0&&r==0);
}
int main(int argc,char** argv){
    for(double rate:{8000.,44100.,48000.,96000.,192000.,384000.}){test<float>(rate);test<double>(rate);}
    for(unsigned lo=0;lo<8;++lo)for(unsigned hi=lo+1;hi<8;++hi)for(unsigned m=0;m<4;++m){Patch p{{lo,hi},static_cast<Mode>(m),true,.123456789};auto s=save(p);Patch q{};check(load(s.data(),s.size(),q)&&save(q)==s);s[7]=2;check(!load(s.data(),s.size(),q)&&q.wet==p.wet);}
    Live a;check(!a.prepare(0));Patch p=a.patch();p.wet=std::numeric_limits<double>::quiet_NaN();check(!a.apply(p));check(a.patch().wet==0);
    std::cout<<"six rates x two formats; 49152 rapid-control paired frames; 112 state roundtrips; transition and bypass bounds PASS\n";
    if(argc==2&&std::string(argv[1])=="--render"){render(false,"action-hard.wav");render(true,"action-smoothed.wav");}
}
