#include "afterimage.hpp"
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <string>
using namespace mhac::afterimage;
static unsigned checks=0;
static void require(bool ok){++checks;if(!ok){std::fprintf(stderr,"archive check %u failed\n",checks);std::exit(1);}}
static void configure(Engine& e,unsigned depth){Patch p;p.mode=Mode::full;p.minimumMs=0;p.memory=1;require(e.configure(p)&&e.setHistoryDepth(depth));}
static void commit(Engine& e,int pitch){require(e.on(7,pitch,1));require(e.off(7));require(e.tick()==0);}
static void prime(Engine& e,unsigned depth,int oldest,int middle){configure(e,depth);commit(e,oldest);commit(e,middle);commit(e,62);}
static void test(double sr){
    Engine a,b,c,d;require(a.prepare(sr)&&b.prepare(sr)&&c.prepare(sr)&&d.prepare(sr));
    prime(a,1,57,59);prime(b,1,60,61);prime(c,3,57,59);prime(d,3,60,61);
    require(c.rememberedCount()==3&&c.rememberedAt(0)==6&&c.rememberedAt(1)==3&&c.rememberedAt(2)==1);
    require(!c.setHistoryDepth(0)&&!c.setHistoryDepth(4));
    for(auto* e:{&a,&b,&c,&d})require(e->on(0,36,1));
    bool differs=false;
    for(unsigned i=0;i<4096;++i){double x=a.tick(),y=b.tick(),z=c.tick(),w=d.tick();require(x==y);require(std::isfinite(z)&&std::abs(z)<=.52);differs|=z!=w;}
    require(differs);
    // Existing voices retain their spectral capture even after another commit.
    Engine f,g;require(f.prepare(sr)&&g.prepare(sr));prime(f,3,57,59);prime(g,3,57,59);
    require(f.on(0,36,1)&&g.on(0,36,1));
    require(f.on(7,64,1)&&f.off(7));
    require(f.rememberedAt(0)==0&&f.rememberedAt(1)==6&&f.rememberedAt(2)==3);
    for(unsigned i=0;i<1024;++i)require(f.tick()==g.tick());
    require(f.on(7,65,1)&&f.off(7,false));require(f.rememberedAt(0)==0&&f.rememberedAt(2)==3);
    Patch p;p.mode=Mode::full;p.minimumMs=100;require(f.configure(p));
    require(f.on(7,66,1)&&f.off(7));require(f.rememberedAt(0)==0&&f.rememberedAt(2)==3);
    f.reset();require(f.rememberedCount()==0&&f.rememberedAt(2)==0&&f.tick()==0);
    require(c.off(0));for(unsigned i=0;i<static_cast<unsigned>(std::ceil(sr*.032))+2;++i)c.tick();require(c.active()==0&&c.tick()==0);
}
static void put16(std::ostream& o,unsigned n){o.put(static_cast<char>(n&255));o.put(static_cast<char>((n>>8)&255));}
static void put32(std::ostream& o,unsigned n){put16(o,n);put16(o,n>>16);}
static void demo(const std::string& path,unsigned depth){
    constexpr unsigned frames=192000;std::ofstream o(path,std::ios::binary);
    o.write("RIFF",4);put32(o,36+frames*2);o.write("WAVEfmt ",8);put32(o,16);put16(o,1);put16(o,1);put32(o,48000);put32(o,96000);put16(o,2);put16(o,16);o.write("data",4);put32(o,frames*2);
    Engine e;configure(e,depth);
    const int notes[]{57,59,62,48,60,61,62,48};
    for(unsigned i=0;i<frames;++i){
        unsigned step=i/24000,offset=i%24000;
        if(offset==0)require(e.on(0,notes[step],.85));
        if(offset==18000)require(e.off(0,step%4!=3));
        put16(o,static_cast<unsigned>(static_cast<int>(std::lround(e.tick()*32767))));
    }
    require(bool(o));
}
int main(int argc,char** argv){
    for(double sr:{1000.,1234.568,8000.,44100.,48000.,96000.,192000.,384000.,1234567.8,2000000.})test(sr);
    if(argc==3&&std::string(argv[1])=="--render"){demo(std::string(argv[2])+"/latest.wav",1);demo(std::string(argv[2])+"/archive.wav",3);}
    std::printf("PASS %u archive checks\n",checks);
}
