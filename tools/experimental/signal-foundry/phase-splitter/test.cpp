#include "splitter.hpp"
#include <iostream>
#include <cstdlib>
#include <fstream>
#include <vector>
using namespace mhac::splitter;
static unsigned long long checks=0;
static void check(bool b){++checks;if(!b){std::cerr<<"failure "<<checks<<'\n';std::exit(1);}}
int main(int argc,char** argv){
    for(double sr:{1000.,1234.568,44100.,48000.,96000.,192000.,1234567.8,2000000.})for(unsigned d=1;d<=64;++d){
        Engine a,b;a.set(Delay,(d-1)/63.);b.set(Delay,(d-1)/63.);a.set(Gain,1.);b.set(Gain,1.);b.set(Direction,1.);a.reset(sr);b.reset(sr);
        std::array<double,512> l{},r{};double ei=0.,eo=0.;
        for(unsigned i=0;i<384;++i){l[i]=.23*std::sin(.17*i);r[i]=.21*std::cos(.091*i);}
        for(unsigned i=0;i<512;++i){auto y=a.process(l[i],r[i]);auto z=b.process(y[0],y[1]);ei+=l[i]*l[i]+r[i]*r[i];eo+=y[0]*y[0]+y[1]*y[1];check(std::abs(z[0]-(i>=d?l[i-d]:0.))<1e-14);check(std::abs(z[1]-(i>=d?r[i-d]:0.))<1e-14);}
        check(std::abs(ei-eo)<1e-10);
    }
    Engine a;a.set(Gain,1.);a.reset(48000.);auto impulse=a.process(1.,0.);check(impulse[0]==.5&&impulse[1]==-.5);for(unsigned i=1;i<=64;++i){auto y=a.process(0.,0.);check(y[0]==(i==16?.5:0.)&&y[1]==(i==16?.5:0.));}
    Engine b;for(unsigned i=0;i<20000;++i){if(i%17==0){b.set(Delay,(i%101)/100.);b.set(Direction,i%2);b.set(Mix,(i%97)/96.);b.set(Gain,(i%89)/88.);b.set(Bypass,(i%3)==0);}auto y=b.process(float(i%2?10:-10),std::numeric_limits<float>::infinity());check(std::isfinite(y[0])&&std::isfinite(y[1])&&std::abs(y[0])<=1.f&&std::abs(y[1])<=1.f);}
    b.set(Bypass,1.);for(unsigned i=0;i<300;++i)b.process(0.,0.);auto y=b.process(.25,-.5);check(y[0]==.25&&y[1]==-.5);
    auto p=defaults;p[Delay]=.25;p[Mix]=.75;auto bytes=encode(p);Params q{};check(decode(bytes,q)&&q==p);bytes[4]=2;check(!decode(bytes,q)&&q==p);
    for(unsigned period:{64u,81u}){Engine e;e.set(Gain,1.);e.reset(48000.);double el=0.,er=0.;for(unsigned i=0;i<period*1025;++i){const double x=.4*std::sin(6.283185307179586*(i%period)/period);auto z=e.process(x,0.);if(i>=period){el+=z[0]*z[0];er+=z[1]*z[1];}}const double f=el/(el+er);check(std::abs(f-std::pow(std::cos(3.141592653589793*16/period),2))<1e-12);std::cout<<"q="<<period<<" left fraction="<<f<<'\n';}
    if(argc==2)for(unsigned mode=0;mode<3;++mode){std::ofstream f(std::string(argv[1])+"/split-"+std::to_string(mode)+".pcm",std::ios::binary);check(bool(f));Engine e;e.set(Gain,1.);e.set(Mix,mode?1.:0.);e.set(Direction,mode==2?1.:0.);e.reset(48000.);for(unsigned i=0;i<144000;++i){double t=i/48000.;double phase=6.283185307179586*(100*t+600*t*t);double x=.35*std::sin(phase)*std::min({1.,t*100.,(3.-t)*100.});auto y=e.process(x,0.);for(double v:y){auto n=std::uint16_t(std::int16_t(std::lround(v*30000.)));f.put(char(n&255));f.put(char(n>>8));}}check(bool(f));}
    std::cout<<checks<<" checks PASS\n";
}
