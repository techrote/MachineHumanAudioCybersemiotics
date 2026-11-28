#include "control.hpp"
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <string>
using namespace restbus;
using namespace restbus::control;
unsigned checks=0;
void ck(bool b){++checks;if(!b){std::cerr<<"failure "<<checks<<'\n';std::exit(1);}}
void advance(Live& e,unsigned state){ck(e.parameter(0,1));for(unsigned i=0;i<state;++i){ck(e.parameter(2,0));ck(e.parameter(2,1));}}
void le(std::ostream& f,unsigned n,unsigned bytes){for(unsigned i=0;i<bytes;++i)f.put(char(n>>(8*i)));}
int main(int argc,char** argv){
    for(double sr:{1000.,8000.,44100.,48000.,96000.,192000.,2000000.})for(unsigned state=0;state<5;++state)for(double dest:{.5,1.}){
        Live a;ck(a.prepare(sr));advance(a,state);ck(a.parameter(3,dest));
        resonance::Bank ref;double hz=440*std::exp2((57+(dest==1?Engine::offsets[state]:0)-69+.25)/12);
        ck(ref.strike(sr,hz,.8,state)&&a.on(1,57,25,.8));
        for(unsigned i=0;i<2048;++i){if(i==500){ck(a.parameter(3,0));ck(a.parameter(2,0)&&a.parameter(2,1));}ck(a.tick()==ref.tick());}
        a.off(1);ref.release();for(unsigned i=0;i<unsigned(sr*.032)+2;++i)ck(a.tick()==ref.tick());
        ck(a.tick()==0);ck(a.on(2,57,0,.8));Engine sine;ck(sine.prepare(sr));sine.domain(Domain::manual);for(unsigned i=0;i<a.index();++i)sine.step();ck(sine.on(2,57,0,.8));for(unsigned i=0;i<128;++i)ck(a.tick()==sine.tick());
    }
    Live a,b;ck(a.prepare(48000)&&b.prepare(48000));advance(a,2);advance(b,2);
    for(int i=0;i<8;++i){double d=(i%3)*.5;ck(a.parameter(3,d)&&b.parameter(3,d));ck(a.on(i,120+i,1200,1)&&b.on(i,120+i,1200,1));}
    ck(!a.on(9,60,0,1));for(unsigned i=0;i<8192;++i){double x=a.tick();ck(x==b.tick()&&std::isfinite(x)&&std::abs(x)<=.480000000001);}
    for(int i=0;i<8;++i){a.off(i);b.off(i);}for(unsigned i=0;i<1600;++i)ck(a.tick()==b.tick());ck(a.tick()==0);
    Params p{1,.25,1},q{};auto s=encode(p);ck(decode(s.data(),s.size(),q)&&q==p);s[3]='1';ck(decode(s.data(),20,q)&&q==Params{1,.25,0});
    ck(!decode(s.data(),s.size(),q));s[3]='2';ck(!decode(s.data(),20,q));ck(!decode(s.data(),3,q));
    ck(a.restore(p)&&a.index()==0&&a.tick()==0);ck(!a.restore({0,0,-1})&&a.parameters()==p);ck(a.restore(q)&&a.parameters()==q);
    if(argc==2)for(unsigned d=0;d<3;++d){Live e;ck(e.prepare(48000));ck(e.parameter(3,d*.5));std::ofstream f(std::string(argv[1])+"/destination-"+std::to_string(d)+".wav",std::ios::binary);constexpr unsigned n=240000;f.write("RIFF",4);le(f,36+n*2,4);f.write("WAVEfmt ",8);le(f,16,4);le(f,1,2);le(f,1,2);le(f,48000,4);le(f,96000,4);le(f,2,2);le(f,16,2);f.write("data",4);le(f,n*2,4);
        for(unsigned i=0;i<n;++i){if(i%48000==14400&&i<192000)ck(e.on(1,57,0,.8));if(i%48000==38400)e.off(1);le(f,unsigned(int(std::lround(e.tick()*32767))),2);}ck(bool(f));}
    std::cout<<"PASS "<<checks<<" assertions\n";
}
