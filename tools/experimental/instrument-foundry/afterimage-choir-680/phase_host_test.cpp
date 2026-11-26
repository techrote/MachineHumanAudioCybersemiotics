#include "live.hpp"
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <limits>
#include <string>
#include <vector>
using namespace mhac::afterimage;
using namespace mhac::afterimage::live;
static unsigned checks=0;
static void check(bool ok){++checks;if(!ok){std::fprintf(stderr,"phase host check %u failed\n",checks);std::exit(1);}}
static void put16(std::ostream& o,unsigned n){o.put(static_cast<char>(n&255));o.put(static_cast<char>((n>>8)&255));}
static void put32(std::ostream& o,unsigned n){put16(o,n);put16(o,n>>16);}
static void prime(Live& e){for(int p:{57,59,62})check(e.on(p,p,0,1)&&e.off(p)&&e.tick()==0);}
static void score(unsigned level,const std::string& path){
    constexpr unsigned frames=192000;
    std::ofstream o;if(!path.empty()){o.open(path,std::ios::binary);o.write("RIFF",4);put32(o,36+frames*2);o.write("WAVEfmt ",8);put32(o,16);put16(o,1);put16(o,1);put32(o,48000);put32(o,96000);put16(o,2);put16(o,16);o.write("data",4);put32(o,frames*2);}
    Live a;Bridge bridge;Engine b;
    const Word w=pack(16,3,0,1000,3,level);
    check(a.prepare(48000)&&bridge.request(w)&&b.prepare(48000)&&b.configure(patch(w))&&b.setHistoryDepth(3)&&b.setPhaseMix(normalized(w,6)));
    bridge.begin(a);bridge.end(a);check(bridge.save()==w);
    const int notes[]{57,59,62,48,60,61,62,48};
    for(unsigned i=0;i<frames;++i){const auto step=i/24000,offset=i%24000;
        if(offset==0)check(a.on(0,notes[step],0,.85)&&b.on(0,notes[step],.85));
        if(offset==18000){check(a.parameter(4,step%4==3?1:0)&&a.off(0)&&b.off(0,step%4!=3));}
        const double y=a.tick();check(y==b.tick()&&std::isfinite(y)&&std::abs(y)<=.52);if(i>=frames-2400)check(y==0);
        if(o.is_open())put16(o,static_cast<unsigned>(static_cast<int>(std::lround(y*32767))));
    }
    if(o.is_open())check(bool(o));
}
static void benchmark(){
    // All voices sustained, then every ~6 ms replace eight at once. This
    // creates up to sixteen oscillator banks during each forced fade.
    using Clock=std::chrono::steady_clock;
    for(unsigned sr:{44100u,48000u,96000u})for(unsigned block:{32u,64u,257u,1024u}){
        Live e;check(e.prepare(sr)&&e.applyPatch(pack(16,3,0,1000,3,2)));prime(e);
        for(int i=0;i<8;++i)check(e.on(i,36+i,0,1));
        for(unsigned i=0;i<sr/100;++i)e.tick();
        unsigned next=8,epoch=0;std::vector<double> times;times.reserve((sr*2+block-1)/block);
        double sum=0,peak=0;const unsigned interval=sr*6/1000;
        for(unsigned start=0;start<sr*2;start+=block){const unsigned count=std::min(block,sr*2-start);const auto t=Clock::now();
            for(unsigned i=0;i<count;++i){if((start+i)%interval==0){for(unsigned k=0;k<8;++k){check(e.on(static_cast<int>(next++),36+static_cast<int>((k+epoch)%12),0,1));}++epoch;}
                const double y=e.tick();peak=std::max(peak,std::abs(y));sum+=y;
            }
            times.push_back(std::chrono::duration<double,std::micro>(Clock::now()-t).count()/count*sr/1e6*100);
        }
        std::sort(times.begin(),times.end());check(std::isfinite(sum)&&peak<=.52);
        std::printf("BENCH %u Hz %u frames: %zu blocks, p50 %.3f%% p99 %.3f%% max %.3f%% deadline, peak %.6f FS\n",sr,block,times.size(),times[times.size()/2],times[(times.size()-1)*99/100],times.back(),peak);
    }
}
int main(int argc,char** argv){
    for(unsigned p=0;p<28;++p)for(unsigned m=0;m<4;++m)for(unsigned ms:{0u,80u,2000u})for(unsigned a:{0u,800u,1000u})for(unsigned d=1;d<=3;++d)for(unsigned phase=0;phase<4;++phase){
        const Word w=pack(p,m,ms,a,d,phase);Word out=0;const auto bytes=encode(w);
        check(bytes[3]==(phase?'3':d==1?'1':'2'));check(decode(bytes.data(),8,out)&&out==w);
        Live e;for(unsigned i:{0u,1u,2u,3u,5u,6u})check(e.parameter(i,normalized(w,i)));check(e.parameters()==w);
        for(unsigned char version:{'1','2','3','4'})if(version!=bytes[3]){auto bad=bytes;bad[3]=version;check(!decode(bad.data(),8,out)&&out==w);}
        auto bad=bytes;bad[7]|=48;check(!decode(bad.data(),8,out)&&out==w);
    }
    for(double sr:{8000.,44100.,48000.,96000.,192000.}){
        Live a,b;check(a.prepare(sr)&&b.prepare(sr));const Word w=pack(16,3,0,1000,3,3);
        check(a.applyPatch(w)&&b.applyPatch(w));prime(a);prime(b);
        check(a.on(0,48,0,1)&&b.on(0,48,0,1));
        for(unsigned i=0;i<257;++i)check(a.tick()==b.tick());
        Bridge bridge;check(bridge.request(pack(16,3,0,1000,3)));bridge.begin(a);bridge.end(a);check(phaseOf(bridge.save())==0);
        for(unsigned i=0;i<1024;++i)check(a.tick()==b.tick()); // active voice unchanged
        check(a.off(0)&&b.off(0));for(unsigned i=0;i<unsigned(sr*.032)+2;++i)check(a.tick()==b.tick());
        check(a.on(0,48,0,1)&&b.on(0,48,0,1));bool differs=false;
        for(unsigned i=0;i<2048;++i){const double x=a.tick(),y=b.tick();check(std::isfinite(x)&&std::isfinite(y)&&std::abs(x)<=.52&&std::abs(y)<=.52);differs|=x!=y;}check(differs);
        a.reset();b.reset();check(a.tick()==0&&b.tick()==0&&phaseOf(b.parameters())==3);
        for(double x:{-.01,1.01,std::numeric_limits<double>::quiet_NaN(),std::numeric_limits<double>::infinity()})check(!b.parameter(6,x)&&b.parameters()==w);
        for(double x:{0.,.16,.17,.49,.5,.83,.84,1.}){check(b.parameter(6,x)&&phaseOf(b.parameters())==static_cast<unsigned>(std::lround(x*3)));}
    }
    for(unsigned p=0;p<4;++p){const std::string path=argc==3&&std::string(argv[1])=="--render"?std::string(argv[2])+"/phase-"+std::to_string(p)+".wav":"";score(p,path);}
    std::printf("PASS %u phase host checks\n",checks);
    if(argc==2&&std::string(argv[1])=="--bench")benchmark();
}
