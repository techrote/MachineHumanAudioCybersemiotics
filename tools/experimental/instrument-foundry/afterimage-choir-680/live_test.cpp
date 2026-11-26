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
    Live e;Bridge s;std::atomic<bool> stop{false};std::atomic<unsigned> bad{0},blocks{0};
    std::thread audio([&]{while(!stop.load()){s.begin(e);for(unsigned j=0;j<64;++j)e.tick();s.end(e);++blocks;}});
    while(!blocks.load())std::this_thread::yield();
    for(unsigned i=0;i<30000;++i){auto w=pack(i%28,i%4,i%2001,i%1001);check(s.request(w));if(s.save()!=w)++bad;}
    stop=true;audio.join();check(!bad&&blocks>0);std::printf("%u checks; 30000 state transactions; %u audio blocks\n",checks,blocks.load());
}
