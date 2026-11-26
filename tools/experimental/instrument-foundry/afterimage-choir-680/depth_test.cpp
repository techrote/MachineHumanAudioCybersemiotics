#include "live.hpp"
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <string>
using namespace mhac::afterimage;
using namespace mhac::afterimage::live;
static unsigned checks=0;
static void check(bool ok){++checks;if(!ok){std::fprintf(stderr,"depth check %u failed\n",checks);std::exit(1);}}
static void commit(Live& e,int pitch){check(e.on(pitch,pitch,0,1)&&e.off(pitch)&&e.tick()==0);}
static void prime(Live& e,unsigned depth,int oldest,int middle){
    check(e.applyPatch(pack(16,3,0,1000,depth)));commit(e,oldest);commit(e,middle);commit(e,62);
}
static void same(Live& a,Live& b,unsigned frames){for(unsigned i=0;i<frames;++i){const auto x=a.tick(),y=b.tick();check(x==y&&std::isfinite(x)&&std::abs(x)<=.52);}}
static void different(Live& a,Live& b){bool differs=false;for(unsigned i=0;i<2048;++i){const auto x=a.tick(),y=b.tick();check(std::isfinite(x)&&std::isfinite(y)&&std::abs(x)<=.52&&std::abs(y)<=.52);differs|=x!=y;}check(differs);}
static void put16(std::ostream& o,unsigned n){o.put(static_cast<char>(n&255));o.put(static_cast<char>((n>>8)&255));}
static void put32(std::ostream& o,unsigned n){put16(o,n);put16(o,n>>16);}
static void demo(const std::string& path,unsigned depth){
    constexpr unsigned frames=192000;std::ofstream o(path,std::ios::binary);
    o.write("RIFF",4);put32(o,36+frames*2);o.write("WAVEfmt ",8);put32(o,16);put16(o,1);put16(o,1);put32(o,48000);put32(o,96000);put16(o,2);put16(o,16);o.write("data",4);put32(o,frames*2);
    Live e;Bridge bridge;check(e.prepare(48000)&&bridge.request(pack(16,3,0,1000,depth)));bridge.begin(e);bridge.end(e);
    const int notes[]{57,59,62,48,60,61,62,48};
    for(unsigned i=0;i<frames;++i){
        const unsigned step=i/24000,offset=i%24000;
        if(offset==0)check(e.on(0,notes[step],0,.85));
        if(offset==18000){check(e.parameter(4,step%4==3?1:0));check(e.off(0));}
        put16(o,static_cast<unsigned>(static_cast<int>(std::lround(e.tick()*32767))));
    }
    check(bool(o));
}
int main(int argc,char** argv){
    for(unsigned p=0;p<28;++p)for(unsigned m=0;m<4;++m)for(unsigned ms:{0u,80u,2000u})for(unsigned a:{0u,800u,1000u})for(unsigned d=1;d<=3;++d){
        const Word w=pack(p,m,ms,a,d);Word out=0;auto bytes=encode(w);check(bytes[3]==(d==1?'1':'2'));check(decode(bytes.data(),8,out)&&out==w);
        Live e;for(unsigned i:{0u,1u,2u,3u,5u})check(e.parameter(i,normalized(w,i)));check(e.parameters()==w);
        auto bad=bytes;bad[3]=static_cast<unsigned char>(d==1?'2':'1');check(!decode(bad.data(),8,out)&&out==w);
        bad=bytes;bad[7]|=64;check(!decode(bad.data(),8,out)&&out==w);
        bad=bytes;bad[7]|=48;check(!decode(bad.data(),8,out)&&out==w);
    }
    for(double sr:{8000.,44100.,48000.,96000.,192000.}){
        Live a,b,c,d;for(auto* e:{&a,&b,&c,&d})check(e->prepare(sr));
        prime(a,2,57,59);prime(b,2,60,59);prime(c,2,57,61);prime(d,3,60,59);
        for(auto* e:{&a,&b,&c,&d})check(e->on(0,36,0,1));
        same(a,b,2048); // depth 2 ignores oldest state
        // Restart identical probe onset to isolate previous vs oldest effects.
        a.reset();prime(a,2,57,59);check(a.on(0,36,0,1));different(a,c);
        a.reset();prime(a,3,57,59);check(a.on(0,36,0,1));different(a,d);
        Live f,g;check(f.prepare(sr)&&g.prepare(sr));
        // Warm-up: zero and one entry fall back to latest for all depths.
        check(f.applyPatch(pack(16,3,0,1000,1))&&g.applyPatch(pack(16,3,0,1000,3)));
        for(int step=0;step<2;++step){check(f.on(0,36,0,1)&&g.on(0,36,0,1));same(f,g,1024);check(f.off(0)&&g.off(0));same(f,g,static_cast<unsigned>(std::ceil(sr*.032))+2);}
        // At two distinct entries, depth 2 and 3 agree only when the
        // missing oldest entry falls back to latest. Depth 1 differs.
        f.reset();g.reset();Live h;check(h.prepare(sr));
        check(f.parameter(5,.5)&&g.parameter(5,1)&&h.applyPatch(pack(16,3,0,1000,1)));
        for(auto* e:{&f,&g,&h}){commit(*e,59);commit(*e,62);check(e->on(0,36,0,1));}
        same(f,g,2048);
        f.reset();commit(f,59);commit(f,62);check(f.on(0,36,0,1));different(f,h);
        // Active patch restore and automation affect only future onsets; archive retained.
        f.reset();g.reset();prime(f,1,57,59);prime(g,1,57,59);
        check(f.on(0,36,0,1)&&g.on(0,36,0,1));same(f,g,17);
        Bridge bridge;check(bridge.request(pack(16,3,0,1000,3)));bridge.begin(f);bridge.end(f);check(bridge.save()==f.parameters()&&depthOf(f.parameters())==3);
        same(f,g,1024);check(f.parameter(4,1)&&g.parameter(4,1));check(f.off(0)&&g.off(0));same(f,g,static_cast<unsigned>(std::ceil(sr*.032))+2);
        check(f.on(0,36,0,1)&&g.on(0,36,0,1));different(f,g);
        f.reset();g.reset();check(depthOf(f.parameters())==3&&depthOf(g.parameters())==1);check(f.on(0,36,0,1)&&g.on(0,36,0,1));same(f,g,1024);
    }
    if(argc==3&&std::string(argv[1])=="--render"){
        demo(std::string(argv[2])+"/latest.wav",1);demo(std::string(argv[2])+"/dual.wav",2);demo(std::string(argv[2])+"/archive.wav",3);
    }
    std::printf("PASS %u archive host checks\n",checks);
}
