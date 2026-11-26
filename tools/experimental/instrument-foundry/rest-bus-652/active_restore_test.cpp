#include "state_bridge.hpp"
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <string>
using namespace restbus::control;
static unsigned long long checks=0;
static void ck(bool b){++checks;if(!b){std::cerr<<"failure "<<checks<<'\n';std::exit(1);}}
static void le(std::ostream& f,unsigned n,unsigned bytes){for(unsigned i=0;i<bytes;++i)f.put(char(n>>(8*i)));}
int main(int argc,char** argv){
    // Restore is equivalent to applying persistent automation, not a voice reset.
    for(double sr:{1000.,8000.,44100.,48000.,96000.,192000.})for(double dest:{0.,.5,1.}){
        Live a,b;StateBridge bridge;ck(a.prepare(sr)&&b.prepare(sr));
        ck(a.parameter(0,1)&&b.parameter(0,1));ck(a.parameter(3,dest)&&b.parameter(3,dest));
        ck(a.parameter(2,1)&&b.parameter(2,1));
        for(int id=0;id<8;++id)ck(a.on(id,57+id,0,.8)&&b.on(id,57+id,0,.8));
        for(unsigned i=0;i<1024;++i)ck(a.tick()==b.tick());
        auto patch=a.parameters();ck(bridge.request(patch)&&bridge.begin(a));bridge.end(a);
        ck(a.parameter(2,1)&&b.parameter(2,1)&&a.index()==1&&b.index()==1);
        for(unsigned i=0;i<1024;++i)ck(a.tick()==b.tick());
        // Change all persistent controls while held; old notes remain identical.
        patch={2./3.,0.,1.-dest};ck(bridge.request(patch)&&bridge.begin(a));
        ck(b.parameter(0,patch[0])&&b.parameter(1,patch[1])&&b.parameter(3,patch[2]));
        bridge.end(a);Params saved{};ck(bridge.save(saved)&&saved==patch);
        for(unsigned i=0;i<2048;++i)ck(a.tick()==b.tick()&&a.index()==b.index());
        for(int id=0;id<8;++id){a.off(id);b.off(id);}
        // Restore during release must preserve the tail as well.
        ck(bridge.request(patch)&&bridge.begin(a));bridge.end(a);
        for(unsigned i=0;i<unsigned(sr*.032)+2;++i)ck(a.tick()==b.tick());
        ck(a.tick()==0&&b.tick()==0);ck(a.on(9,69,0,.8)&&b.on(9,69,0,.8));
        for(unsigned i=0;i<1024;++i)ck(a.tick()==b.tick());
        auto bad=patch;bad[1]=std::numeric_limits<double>::infinity();ck(!a.applyPatch(bad)&&a.parameters()==patch);
        a.reset();ck(a.index()==0&&a.partial()==0&&a.tick()==0);
    }
    // An identical restore must not postpone a pending idle-clock tick.
    Live a;StateBridge bridge;ck(a.prepare(48000));ck(a.parameter(1,0));
    for(unsigned i=0;i<479;++i){ck(a.tick()==0);}
    ck(a.partial()==479);
    ck(bridge.request(a.parameters())&&bridge.begin(a));ck(a.partial()==479);ck(a.tick()==0&&a.index()==1);
    if(argc==2)for(unsigned hard=0;hard<2;++hard){
        Live e;StateBridge h;ck(e.prepare(48000));ck(e.on(1,57,0,.8));
        std::ofstream f(std::string(argv[1])+(hard?"/restore-hard.wav":"/restore-preserved.wav"),std::ios::binary);
        constexpr unsigned n=144000;f.write("RIFF",4);le(f,36+n*2,4);f.write("WAVEfmt ",8);le(f,16,4);le(f,1,2);le(f,1,2);le(f,48000,4);le(f,96000,4);le(f,2,2);le(f,16,2);f.write("data",4);le(f,n*2,4);
        for(unsigned i=0;i<n;++i){if(i==48000){if(hard)ck(e.restore(e.parameters()));else ck(h.request(e.parameters())&&h.begin(e));}if(i==96000)e.off(1);le(f,unsigned(int(std::lround(e.tick()*32767))),2);}ck(bool(f));
    }
    std::cout<<"PASS "<<checks<<" assertions\n";
}
