#include "live.hpp"
#include <cstdlib>
#include <cstdio>
#include <fstream>
#include <limits>
#include <string>
using namespace mhac::afterimage;
using mhac::afterimage::live::Live;
static unsigned checks=0;
static void require(bool ok){++checks;if(!ok){std::fprintf(stderr,"admission check %u failed\n",checks);std::exit(1);}}
static void test(double sr){
    Engine a,b;require(a.prepare(sr)&&b.prepare(sr));Patch p;p.minimumMs=0;p.mode=Mode::full;
    require(a.configure(p)&&b.configure(p));
    for(int i=0;i<8;++i)require(a.on(i,36+i,1)&&b.on(i,36+i,1));
    const auto fade=static_cast<unsigned>(std::ceil(sr*.005));
    for(unsigned i=0;i<fade+2;++i)require(a.tick()==b.tick());
    int victim=-1;require(a.on(8,52,1,0,&victim)&&victim==0);
    require(std::abs(a.tick()-b.tick())<=.13/(sr*.005)+1e-12);
    require(!a.off(0)&&a.remembered()==0);
    for(int i=1;i<8;++i)require(a.on(8+i,52+i,1,0,&victim)&&victim==i);
    require(!a.on(16,62,1,0,&victim)&&victim==-1);
    require(!a.on(17,62,std::numeric_limits<double>::quiet_NaN(),0,&victim));
    for(unsigned i=0;i<fade+2;++i){double x=a.tick();require(std::isfinite(x)&&std::abs(x)<=.52);}
    require(a.on(16,62,1,0,&victim)&&victim==8);
    require(!a.off(8)&&a.remembered()==0);
    a.reset();require(a.active()==0&&a.tick()==0);
    // Host tokens: a younger released voice wins over oldest held voice.
    Live l;require(l.prepare(sr)&&l.parameter(1,1)&&l.parameter(2,0));
    for(int i=0;i<8;++i)require(l.on(100+i,40+i,0,1));
    for(unsigned i=0;i<fade+2;++i)l.tick();
    require(l.off(105)&&l.remembered()==5);
    require(l.on(200,60,0,1)&&l.remembered()==5);
    require(l.off(100)&&l.remembered()==0); // oldest was not stolen
    require(!l.off(105));
    l.reset();require(l.active()==0&&l.tick()==0);
    for(int i=0;i<8;++i)require(l.on(100+i,40+i,0,1));
    for(unsigned i=0;i<fade+2;++i)l.tick();
    for(int i=0;i<8;++i)require(l.on(200+i,56+i,0,1));
    require(!l.on(300,60,0,1));
    for(int i=0;i<8;++i)require(!l.off(100+i));
    require(l.remembered()==0);
    for(unsigned i=0;i<fade+2;++i){const float x=static_cast<float>(l.tick());require(std::isfinite(x)&&std::abs(x)<=.52f);}
    require(l.on(300,62,0,1));require(!l.off(200));
    for(int i=1;i<8;++i)require(l.off(200+i));
    require(l.off(300)&&l.remembered()==6);
    for(unsigned i=0;i<static_cast<unsigned>(std::ceil(sr*.032))+2;++i)l.tick();
    require(l.active()==0&&l.tick()==0);
}
static void put16(std::ostream& o,unsigned n){o.put(static_cast<char>(n&255));o.put(static_cast<char>((n>>8)&255));}
static void put32(std::ostream& o,unsigned n){put16(o,n);put16(o,n>>16);}
static void demo(const std::string& path,bool replace){
    std::ofstream o(path,std::ios::binary);constexpr unsigned frames=96000;
    o.write("RIFF",4);put32(o,36+frames*2);o.write("WAVEfmt ",8);put32(o,16);put16(o,1);put16(o,1);put32(o,48000);put32(o,96000);put16(o,2);put16(o,16);o.write("data",4);put32(o,frames*2);
    Engine e;Patch p;p.mode=Mode::full;p.minimumMs=0;require(e.configure(p));
    const int chord[]{48,55,60,64,67,71,74,79};
    for(int i=0;i<8;++i)require(e.on(i,chord[i],.65));
    for(unsigned i=0;i<frames;++i){
        if(i>=19200&&i<38400&&(i-19200)%4800==0){int v=-1;const int j=static_cast<int>((i-19200)/4800);require(e.on(8+j,72+j*2,.8,0,replace?&v:nullptr)==replace);}
        if(i==57600)for(int j=0;j<12;++j)e.off(j);
        put16(o,static_cast<unsigned>(static_cast<int>(std::lround(e.tick()*32767))));
    }
    require(bool(o));
}
int main(int argc,char** argv){
    for(double sr:{1000.,1234.568,8000.,44100.,48000.,96000.,192000.,384000.,1234567.8,2000000.})test(sr);
    if(argc==3&&std::string(argv[1])=="--render"){demo(std::string(argv[2])+"/reject.wav",false);demo(std::string(argv[2])+"/replace.wav",true);}
    std::printf("PASS %u admission checks\n",checks);
}
