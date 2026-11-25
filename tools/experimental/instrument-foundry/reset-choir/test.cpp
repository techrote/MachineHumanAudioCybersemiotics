#include "engine.hpp"
#include <iostream>
#include <fstream>
#include <stdexcept>
#include <string>
using namespace mhac::choir;
unsigned checks=0;
void check(bool b){++checks;if(!b)throw std::runtime_error("check "+std::to_string(checks));}
void le(std::ostream& o,unsigned v,unsigned n){for(unsigned i=0;i<n;++i)o.put(char(v>>(8*i)));}
void render(const char* path,unsigned mask,double seed){Engine e;e.reset(48000);e.set(Score,mask/255.);e.set(Seed,seed);e.set(Rate,.25);e.set(Colour,.8);e.noteOn(0,48,1,.8);constexpr unsigned n=144000;std::ofstream o(path,std::ios::binary);o.write("RIFF",4);le(o,36+n*2,4);o.write("WAVEfmt ",8);le(o,16,4);le(o,1,2);le(o,1,2);le(o,48000,4);le(o,96000,4);le(o,2,2);le(o,16,2);o.write("data",4);le(o,n*2,4);for(unsigned i=0;i<n;++i){if(i==132000)e.noteOff(0,48,1);le(o,unsigned(int(std::lround(e.next()*32767))),2);}check(bool(o));}
int main(int argc,char**){
    for(unsigned mask=0;mask<256;++mask){auto w=compile(mask);int net=0;for(unsigned i=0;i<w.size;++i){check(w.symbols[i]==1||w.symbols[i]==-1);net+=w.symbols[i];}check(net==0);unsigned ones=0,cost=8;for(unsigned i=0;i<8;++i){ones+=(mask>>i)&1u;if(i&&((mask>>i)^(mask>>(i-1)))&1u)cost+=i;}cost+=(mask&128)?ones:8-ones;check(w.size==cost&&w.size<=40);int target=0;for(unsigned m=1;m<=8;++m){target+=(mask>>(m-1))&1u;for(unsigned start=0;start<=m;++start){int x=start;for(unsigned i=0;i<w.size;++i)x=std::clamp(x+w.symbols[i],0,int(m));check(x==target);}}}
    Engine e;check(!e.reset(0));check(!e.reset(NAN));check(!e.reset(INFINITY));check(!e.reset(2000001));
    Params p{.2,.4,.6,.8,1},q{};auto st=encode(p);check(decode(st,q));for(unsigned i=0;i<Count;++i)check(std::abs(p[i]-q[i])<1e-7);st[0]=0;check(!decode(st,q));
    for(double r:{1000.,1234.568,8000.,44100.,48000.,96000.,192000.,1234567.8,2000000.}){check(e.reset(r));check(e.next()==0);check(!e.noteOn(0,-1,1,1));check(!e.noteOn(0,60,1,NAN));for(int i=0;i<16;++i)check(e.noteOn(0,36+i,i,1));check(!e.noteOn(0,60,17,1));for(unsigned i=0;i<unsigned(.03*r);++i){auto y=e.next();check(std::isfinite(y)&&std::abs(y)<=.5);}for(int i=0;i<16;++i)e.noteOff(0,36+i,i);for(unsigned i=0;i<unsigned(.021*r)+2;++i)check(std::abs(e.next())<=.5);check(e.active()==0&&e.next()==0);}
    Engine a,b;a.reset(48000);b.reset(48000);a.set(Seed,0);b.set(Seed,1);a.set(Rate,0);b.set(Rate,0);a.noteOn(0,48,1,1);b.noteOn(0,48,1,1);bool different=false;for(unsigned i=0;i<48000;++i){auto x=a.next(),y=b.next();if(i<10000)different|=x!=y;if(i>30000)check(x==y);}check(different);
    if(argc>1){render("alternating-empty.wav",85,0);render("alternating-full.wav",85,1);render("ascending.wav",255,.5);}
    std::cout<<checks<<" checks passed\n";
}
