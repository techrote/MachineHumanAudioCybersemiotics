#include "socket.hpp"
#include <cstdlib>
#include <iostream>
#include <limits>
#define CHECK(x) do {if(!(x)){std::cerr<<__LINE__<<": "<<#x<<'\n';std::exit(1);}}while(false)
using namespace winters;
int main(){
    for(unsigned n=0;n<256;++n){timbre::Socket s;Score ref;for(unsigned i=0;i<4;++i){int v=int((n>>(2*i))&3);s.edit(i,v/3.);ref.edit(int(i),v);}auto check=[&]{auto a=s.values();for(int i=0;i<3;++i)CHECK(a[i]==ref.token(i)/3.);};check();s.hold();ref.hold();s.edit(1,.3333333333333333);ref.edit(1,1);s.hold();ref.hold();s.tick();ref.tick();check();s.release();ref.release();check();s.tick();ref.tick();check();}
    for(double sr:{1000.,8000.,44100.,48000.,96000.,192000.,2000000.}){
        timbre::Engine e;live::Engine ref;CHECK(e.prepare(sr)&&ref.prepare(sr));
        for(int n=0;n<4;++n){CHECK(e.pitch.on(n,48+n*7,0,.7));CHECK(ref.on(n,48+n*7,0,.7));}
        for(int i=0;i<4096;++i){if(i%257==0){e.pitch.parameter(5,0);ref.parameter(5,0);e.pitch.parameter(5,1);ref.parameter(5,1);}auto a=e.sample(),b=ref.tick();CHECK(a.l==b.l&&a.r==b.r&&a.primary==b.primary&&a.middle==b.middle&&a.deep==b.deep);}
        e.socket.edit(0,1);e.socket.edit(1,.25);e.socket.hold();e.socket.edit(1,.75);e.socket.tick();
        CHECK((e.socket.values()==std::array<double,3>{1,1,.25}));
        double last=0;for(int i=0;i<int(sr*.006)+2;++i){auto f=e.sample();CHECK(std::isfinite(f.l)&&std::abs(f.l)<=.3000001&&std::abs(f.r)<=.3000001);CHECK(std::abs(e.amounts()[0]-last)<=1/std::max(1.,sr*.005)+1e-12);last=e.amounts()[0];}CHECK(std::abs(last-1)<1e-12);
        e.socket.edit(0,std::numeric_limits<double>::quiet_NaN());CHECK(e.socket.slot(0)==1);
        for(int n=0;n<4;++n)e.pitch.off(n);
        for(int i=0;i<int(sr*.041)+2;++i){e.sample();}auto f=e.sample();CHECK(f.l==0&&f.r==0&&f.primary==0&&f.middle==0&&f.deep==0);
    }
    CHECK(timbre::harmonic(.123,.23,1)==timbre::harmonic(.123,.23,0));
    double f1=0,f2=0;for(int i=0;i<1024;++i){double p=i/1024.;double x=timbre::harmonic(p,.01,.75);f1+=x*std::sin(2*Engine::pi*p)*2/1024;f2+=x*std::sin(4*Engine::pi*p)*2/1024;}CHECK(std::abs(f1-.25)<1e-12&&std::abs(f2-.75)<1e-12);
    std::cout<<"256 banks; 28672 exact neutral frames; seven rates; harmonic coefficients "<<f1<<", "<<f2<<"; PASS\n";
}
