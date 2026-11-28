#include "live.hpp"
#include <cstdlib>
#include <iostream>
#include <fstream>
#include <chrono>
using namespace winters::live;
#define CHECK(x) do{if(!(x)){std::cerr<<"FAIL "<<__LINE__<<" "<<#x<<'\n';std::exit(1);}}while(false)
void word(std::ofstream& o,unsigned v,int n){for(int i=0;i<n;++i)o.put(char((v>>(8*i))&255));}
void controls(Engine& e,unsigned i){if(i==0){CHECK(e.on(1,48,0,.9));CHECK(e.on(2,55,7,.75));e.parameter(6,1);}if(i==48000)e.parameter(4,1);if(i==72000)e.parameter(1,1);if(i==96000)e.parameter(2,0);if(i==144000)e.parameter(4,0);if(i==192000){e.off(1);e.off(2);}}
void demo(const char* name,bool stems){Engine e;CHECK(e.prepare(48000));std::ofstream o(name,std::ios::binary);unsigned ch=stems?3:2,n=288000*ch*2;o.write("RIFF",4);word(o,36+n,4);o.write("WAVEfmt ",8);word(o,16,4);word(o,1,2);word(o,ch,2);word(o,48000,4);word(o,48000*ch*2,4);word(o,ch*2,2);word(o,16,2);o.write("data",4);word(o,n,4);for(unsigned i=0;i<288000;++i){controls(e,i);auto f=e.tick();if(stems){for(double x:{f.primary,f.middle,f.deep})word(o,unsigned(std::lround(x*32767)),2);}else for(double x:{f.l,f.r})word(o,unsigned(std::lround(x*32767)),2);}CHECK(bool(o));}
int main(int argc,char**){
    auto p=defaults;p[1]=1;p[4]=p[5]=1;p[6]=1;p[7]=.7;p[9]=.4;auto s=encode(p);Params q{};CHECK(decode(s.data(),s.size(),q)&&encode(q)==s&&q[4]==0&&q[5]==0&&q[1]==1);auto old=q;CHECK(!decode(s.data(),s.size()-1,q)&&q==old);s[32]=0;s[33]=0;s[34]=192;s[35]=127;CHECK(!decode(s.data(),s.size(),q)&&q==old);
    Engine c;CHECK(c.prepare(48000));c.parameter(4,1);c.parameter(1,1);c.parameter(5,1);c.parameter(5,1);CHECK(c.score().token(0)==0&&c.score().token(1)==0&&c.score().token(2)==1);c.parameter(4,0);CHECK(c.score().token(0)==3&&c.score().token(1)==0&&c.score().token(2)==3);c.parameter(5,0);c.parameter(5,1);CHECK(c.score().token(0)==2&&c.score().token(1)==3);c.restore(old);CHECK(c.score().moving==0&&!c.score().held&&c.score().bank[1]==3);
    for(double rate:{1000.,1234.5678,8000.,44100.,48000.,96000.,192000.,384000.,1234567.8,2000000.}){
        Engine a;CHECK(a.prepare(rate));a.parameter(6,1);a.parameter(7,1);unsigned n=unsigned(std::ceil(rate/8));for(unsigned i=0;i<n;++i){a.tick();CHECK(a.score().moving==0);}a.tick();CHECK(a.score().moving==1);a.parameter(4,1);for(unsigned i=0;i<n;++i)a.tick();CHECK(a.score().moving==2&&a.score().paused==1);a.reset();CHECK(a.score().moving==0&&!a.score().held);for(int k=0;k<4;++k)CHECK(a.on(k,127-k,1200,1));CHECK(!a.on(9,60,0,1));CHECK(!a.on(0,60,0,1));for(unsigned i=0;i<1000;++i){auto f=a.tick();CHECK(std::isfinite(f.l)&&std::abs(f.l)<=.300001&&std::abs(f.r)<=.300001);}for(int k=0;k<4;++k)a.off(k);for(unsigned i=0;i<unsigned(rate*.041)+2;++i)a.tick();CHECK(a.tick().l==0&&a.tick().r==0);
    }
    Engine a,b;CHECK(a.prepare(48000)&&b.prepare(48000));std::array<double,257> l{},r{},x{},y{},z{};std::array<float,257> m{};double* stereo[]={l.data(),r.data()};float* mono[]={m.data()};unsigned time=0;for(unsigned block=0;block<900;++block){for(unsigned i=0;i<257;++i,++time){controls(a,time);controls(b,time);auto f=a.tick(),g=b.tick();CHECK(f.l==g.l&&f.r==g.r);write(f,stereo,2,x.data(),y.data(),z.data(),i);write<float>(g,mono,1,nullptr,nullptr,nullptr,i);CHECK(m[i]==float((f.l+f.r)*.5)&&x[i]==f.primary&&y[i]==f.middle&&z[i]==f.deep);}}
    Engine tune;CHECK(tune.prepare(48000)&&tune.on(1,69,1200,1));unsigned crossings=0;double prev=0;for(int i=0;i<48000;++i){auto f=tune.tick();if(prev<=0&&f.primary>0)++crossings;prev=f.primary;}CHECK(crossings>=879&&crossings<=881);
    Engine bench;CHECK(bench.prepare(48000));for(int i=0;i<4;++i)CHECK(bench.on(i,48+i*3,0,1));bench.parameter(6,1);auto t=std::chrono::steady_clock::now();double sum=0;for(int i=0;i<480000;++i)sum+=std::abs(bench.tick().l);CHECK(sum>1&&std::isfinite(sum));std::cout<<"PASS state, manual contract, auto clock, 10 rates, routing, tuning; 10s benchmark "<<std::chrono::duration<double>(std::chrono::steady_clock::now()-t).count()<<" s\n";
    if(argc>1){demo("winters-clock.wav",false);demo("winters-stems.wav",true);}
}
