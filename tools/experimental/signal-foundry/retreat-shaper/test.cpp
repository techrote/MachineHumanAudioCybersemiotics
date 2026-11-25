#include "retreat.hpp"
#include <iostream>
#include <cstdlib>
#include <fstream>
#include <string>
using namespace mhac::retreat;
unsigned long long checks=0;
void check(bool b){++checks;if(!b){std::cerr<<"failure at check "<<checks<<'\n';std::exit(1);}}
int main(int argc,char** argv){
    for(unsigned a=0;a<=16;++a)for(unsigned b=0;b<=16;++b)for(unsigned c=0;c<=16;++c)for(unsigned d=0;d<=16;++d){
        Relays r;bool v[2][8]{};
        for(unsigned x:{a,b,c,d}){r.step(x);for(unsigned k=0;k<2;++k)for(unsigned i=0;i<8;++i){const unsigned lo=k?8-i:(i==7?8:7-i);if(x>=9+i)v[k][i]=true;else if(x<lo)v[k][i]=false;}
            for(unsigned k=0;k<2;++k){unsigned n=0;for(bool y:v[k])n+=y;check(r.mass(double(k))==n/8.);}}
    }
    Relays r;for(unsigned x=0;x<=16;++x){r.step(x);check(r.mass(0)==r.mass(1));}for(int x=16;x>=0;--x){r.step(unsigned(x));check(r.mass(0)==r.mass(1));}
    constexpr unsigned path[]{0,15,1,14,2,13,3,12,4,11,5,10,6,9,7};
    r={};for(auto x:path)r.step(x);check(r.mass(0)==.875);check(r.mass(1)==0);check(r.mass(.5)==.4375);
    for(double sr:{1000.,1234.568,44100.,48000.,96000.,192000.,1234567.8,2000000.}){
        Engine e;e.reset(sr);e.set(Depth,1);e.set(Coupling,0);for(auto x:path)e.process(0,x/16.);check(e.mass(0)==.875);check(e.mass(1)==0);
        for(unsigned i=0;i<4000;++i){double x=std::sin(i*.039);double y=e.process(0,x);check(std::isfinite(y)&&std::abs(y)<=std::abs(x));float z=e.process(1,float(x));check(std::isfinite(z)&&std::abs(z)<=std::abs(float(x)));}
        e.set(Bypass,1);for(unsigned i=0;i<unsigned(sr*.006)+2;++i)e.process(0,.25);check(e.process(0,.25)==.25);
        check(e.process(0,std::numeric_limits<double>::infinity())==0);check(e.process(0,std::numeric_limits<float>::quiet_NaN())==0);check(e.process(0,std::numeric_limits<double>::denorm_min())==0);
        e.reset(sr);check(e.mass(0)==0&&e.mass(1)==0);
    }
    Engine a,b;for(unsigned i=0;i<10000;++i){const double x=std::sin(i*.051);if(i%113==0){a.set(Coupling,double(i%100)/100);b.set(Coupling,double(i%100)/100);}check(a.process(0,x)==b.process(0,x));b.process(1,1.);}
    auto p=defaults;p[Drive]=.123456;p[Coupling]=.25;auto s=encode(p);Params q{};check(decode(s,q)&&q==p);s[4]=3;check(!decode(s,q)&&q==p);s=encode(p);s[8]=255;s[9]=255;s[10]=255;check(!decode(s,q)&&q==p);
    if(argc==2){for(unsigned k=0;k<3;++k){std::ofstream f(std::string(argv[1])+"/retreat-"+std::to_string(k)+".pcm",std::ios::binary);check(bool(f));Engine e;e.set(Coupling,double(k==1));e.set(Depth,1);e.set(Mix,k==2?0.:1.);for(unsigned level:path)for(unsigned i=0;i<4800;++i){double x=level/16.*(i%96<48?1.:-1.);auto y=e.process(0,x);auto v=std::uint16_t(std::int16_t(std::lround(y*16000.)));f.put(char(v&255));f.put(char(v>>8));}check(bool(f));}}
    std::cout<<checks<<" assertions passed\n";
}
