#include "live.hpp"
#include <cstdio>
#include <cstdlib>
#include <thread>
#include <limits>
using namespace mhac::afterimage::live;
static unsigned checks=0;
static void check(bool b){++checks;if(!b){std::fprintf(stderr,"failed %u\n",checks);std::exit(1);}}
int main(){
    check(pairAt(16).low==2&&pairAt(16).high==6);
    for(unsigned p=0;p<28;++p)for(unsigned m=0;m<4;++m)for(unsigned ms:{0u,80u,2000u})for(unsigned a:{0u,800u,1000u}){
        Word w=pack(p,m,ms,a),out=0;auto s=encode(w);check(decode(s.data(),8,out)&&out==w);Live e;for(unsigned i=0;i<4;++i)check(e.parameter(i,normalized(w,i)));check(e.parameters()==w);
        s[7]|=128;check(!decode(s.data(),8,out)&&out==w);
    }
    for(double sr:{8000.,44100.,48000.,96000.,192000.}){
        Live e;check(e.prepare(sr));check(e.parameter(2,0));check(e.on(-1,62,0,1));check(e.parameter(4,1));check(e.off(-1));check(e.remembered()==0);check(e.parameter(4,0));check(e.on(-1,62,0,1));check(e.off(-1));check(e.remembered()==2);
        check(!e.parameter(3,std::numeric_limits<double>::quiet_NaN()));
        Live a,b;check(a.prepare(sr)&&b.prepare(sr));check(a.on(0,57,12,1)&&b.on(0,57,12,1));Bridge s;check(s.request(pack(16,3,0,1000)));s.begin(a);s.end(a);check(s.save()==pack(16,3,0,1000));
        for(unsigned i=0;i<2048;++i){float x=float(a.tick()),y=float(b.tick());check(x==y&&std::abs(x)<=.52f);}
        check(a.off(0)&&b.off(0));for(unsigned i=0;i<unsigned(sr*.032)+2;++i)check(a.tick()==b.tick());check(a.active()==0&&a.tick()==0);
    }
    // Every rate exercised by the pinned SDK validator, plus range boundaries.
    for(double sr:{1000.,1234.568,8000.,12345.678,22050.,32000.,44100.,48000.,88200.,96000.,123456.78,192000.,384000.,1234567.8,2000000.}){
        Live a,b;check(a.prepare(sr)&&b.prepare(sr));
        check(a.applyPatch(pack(16,2,1,1000))&&b.applyPatch(pack(16,2,1,1000)));
        const auto held=static_cast<unsigned>(std::ceil(sr/1000.));
        check(a.on(1,38,0,1)&&b.on(1,38,0,1));
        for(unsigned i=0;i<held;++i){const double x=a.tick(),y=b.tick();check(std::isfinite(x)&&std::abs(x)<=.52&&x==y);}
        check(a.off(1)&&b.off(1)&&a.remembered()==6&&b.remembered()==6);
        check(a.on(2,127,1200,1)&&b.on(2,127,1200,1));
        for(unsigned i=0;i<held;++i){const double x=a.tick(),y=b.tick();check(std::isfinite(x)&&std::abs(x)<=.52&&x==y);}
        check(a.off(2)&&b.off(2));
        for(unsigned i=0;i<static_cast<unsigned>(std::ceil(sr*.032))+2;++i){const double x=a.tick(),y=b.tick();check(std::isfinite(x)&&std::abs(x)<=.52&&x==y);}
        check(a.active()==0&&a.tick()==0&&b.active()==0&&b.tick()==0);
        // Invalid setup cannot erase a live note or change its rate.
        check(a.on(3,38,0,1)&&b.on(3,38,0,1));
        for(double bad:{0.,999.,2000001.,std::numeric_limits<double>::infinity(),std::numeric_limits<double>::quiet_NaN()})check(!a.prepare(bad));
        for(unsigned i=0;i<257;++i)check(a.tick()==b.tick());
        check(a.prepare(48000.)&&a.active()==0&&a.remembered()==0&&a.tick()==0);
    }
    Live e;Bridge s;std::atomic<bool> stop{false};std::atomic<unsigned> bad{0},blocks{0};
    std::thread audio([&]{while(!stop.load()){s.begin(e);for(unsigned j=0;j<64;++j)e.tick();s.end(e);++blocks;}});
    while(!blocks.load())std::this_thread::yield();
    for(unsigned i=0;i<30000;++i){auto w=pack(i%28,i%4,i%2001,i%1001,1+i%3);check(s.request(w));if(s.save()!=w)++bad;}
    stop=true;audio.join();check(!bad&&blocks>0);std::printf("%u checks; 30000 state transactions; %u audio blocks\n",checks,blocks.load());
}
