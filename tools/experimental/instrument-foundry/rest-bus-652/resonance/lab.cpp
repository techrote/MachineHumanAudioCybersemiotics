#include "bank.hpp"
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <limits>
#include <string>
#include <vector>
using namespace restbus;
using namespace restbus::resonance;
static unsigned checks=0;
static void check(bool b){++checks;if(!b){std::cerr<<"failed at check "<<checks<<'\n';std::exit(1);}}
static void le(std::ostream& f,unsigned n,unsigned bytes){for(unsigned i=0;i<bytes;++i)f.put(char((n>>(8*i))&255));}
static void wav(const std::string& path,const std::vector<double>& x){std::ofstream f(path,std::ios::binary);f.write("RIFF",4);le(f,36+unsigned(x.size()*2),4);f.write("WAVEfmt ",8);le(f,16,4);le(f,1,2);le(f,1,2);le(f,48000,4);le(f,96000,4);le(f,2,2);le(f,16,2);f.write("data",4);le(f,unsigned(x.size()*2),4);for(double v:x)le(f,unsigned(int(std::lround(v*32767))),2);if(!f)std::exit(2);}
int main(int argc,char** argv){
    for(double sr:{1000.,8000.,44100.,48000.,96000.,192000.,2000000.}){
        for(unsigned p=0;p<5;++p){Bank b;check(b.strike(sr,220,1,p));for(unsigned i=0;i<4096;++i){double x=b.tick();check(std::isfinite(x)&&std::abs(x)<=.06);}b.release();for(unsigned i=0;i<unsigned(sr*.032)+2;++i)b.tick();check(!b.active()&&b.tick()==0);}
        Instrument a,b;check(a.prepare(sr,.01)&&b.prepare(sr,.01));a.domain(Domain::manual);b.domain(Domain::manual);
        for(unsigned i=0;i<8;++i){check(a.on(int(i),60,1)&&b.on(int(i),60,1));}check(!a.on(8,60,1));
        a.step();for(unsigned i=0;i<4096;++i){double x=a.tick();check(x==b.tick()&&std::abs(x)<=.480000000001);}
        for(int i=0;i<8;++i){a.off(i);b.off(i);}for(unsigned i=0;i<unsigned(sr*.032)+2;++i){check(a.tick()==b.tick());}check(a.tick()==0&&b.tick()==0);
        check(a.on(8,60,1)&&b.on(8,60,1));double diff=0;for(unsigned i=0;i<4096;++i)diff+=std::abs(a.tick()-b.tick());check(diff>0);
        a.reset();check(a.index()==0&&a.tick()==0);check(!a.on(0,60,std::numeric_limits<double>::quiet_NaN()));
    }
    Instrument a,b;check(a.prepare(48000,.01)&&b.prepare(48000,.01));for(int i=0;i<480;++i){a.tick();b.tick();}check(a.index()==1&&b.index()==1);check(a.on(1,57,1)&&b.on(1,57,1));
    std::array<double,257> l{},r{};for(unsigned n:{1u,64u,257u,13u}){a.process(l.data(),r.data(),n);for(unsigned i=0;i<n;++i)check(l[i]==r[i]&&l[i]==b.tick());}a.reset();b.reset();check(a.on(2,57,1)&&b.on(2,57,1));std::array<float,257> f{};a.process(f.data(),f.data(),257);for(float x:f)check(x==float(b.tick()));
    Bank invalid;check(!invalid.strike(0,220,1,0)&&!invalid.strike(48000,0,1,0)&&!invalid.strike(48000,220,1,5));
    if(argc==2){for(unsigned p=0;p<5;++p){Instrument e;check(e.prepare(48000,.1));e.domain(Domain::manual);for(unsigned i=0;i<p;++i)e.step();check(e.on(1,57,.8));std::vector<double> x(96000);for(unsigned i=0;i<x.size();++i){if(i==72000)e.off(1);x[i]=e.tick();}wav(std::string(argv[1])+"/modal-"+std::to_string(p)+".wav",x);}}
    std::cout<<checks<<" checks passed\n";
}
