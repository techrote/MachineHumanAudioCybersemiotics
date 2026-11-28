#include "live.hpp"
#include <cstdlib>
#include <iostream>
#include <fstream>
#include <chrono>
using namespace offcut::live;
void check(bool b){if(!b){std::cerr<<"FAIL\n";std::exit(1);}}
void word(std::ofstream& o,unsigned v,int n){for(int i=0;i<n;++i)o.put(char((v>>(8*i))&255));}
void demo(const char* name,unsigned route){
    Engine e;check(e.prepare(48000));auto p=defaults;p[0]=.25;p[1]=1;p[2]=0;p[4]=1;p[5]=.12;p[7]=7./15.;
    std::ofstream o(name,std::ios::binary);constexpr unsigned frames=192000,n=frames*4;
    o.write("RIFF",4);word(o,36+n,4);o.write("WAVEfmt ",8);word(o,16,4);word(o,1,2);word(o,2,2);word(o,48000,4);word(o,192000,4);word(o,4,2);word(o,16,2);o.write("data",4);word(o,n,4);
    const int notes[]={48,55,60,64,67,62,55};
    for(unsigned i=0;i<frames;++i){if(i%24000==0&&i<168000)check(e.on(int(i),notes[i/24000],0,.9,p));if(i>=18000&&(i-18000)%24000==0)e.off(int(i-18000));auto f=e.tick();double l=route==0?f.l:route==1?f.primary:f.deep,r=route==0?f.r:route==1?f.middle:f.deep;word(o,unsigned(std::lround(l*32767)),2);word(o,unsigned(std::lround(r*32767)),2);}check(bool(o));
}
int main(int argc,char**){
    auto p=defaults;set(p,7,.48);set(p,4,1);set(p,5,.12);set(p,6,.7);auto s=encode(p);Params q{};check(decode(s.data(),s.size(),q));check(encode(q)==s);
    auto old=offcut::defaults;old[3]=1;auto os=offcut::encode(old);check(decode(os.data(),os.size(),q)&&q[4]==0&&q[3]==1);auto before=q;s[20]=0;s[21]=0;s[22]=0xc0;s[23]=0x7f;check(!decode(s.data(),s.size(),q)&&q==before);check(!decode(os.data(),os.size()-1,q)&&q==before);
    std::uint64_t frames=0;
    for(double rate:{1000.,1234.568,8000.,44100.,48000.,96000.,192000.,384000.,1234567.8,2000000.}){
        Engine e;offcut::Engine legacy;offcut::nested::Engine nested;check(e.prepare(rate)&&legacy.prepare(rate)&&nested.prepare(rate));auto a=defaults;auto b=p;b[3]=0;offcut::Params ap{};std::copy_n(a.begin(),4,ap.begin());offcut::nested::Patch bp;std::copy_n(b.begin(),4,bp.original.begin());bp.cut=b[5];bp.depth=b[6];bp.ratio=1+std::round(15*b[7]);
        check(e.on(1,48,0,.9,a)&&legacy.on(1,48,0,.9,ap));check(e.on(2,67,0,.8,b)&&nested.on(2,67,0,.8,bp));check(!e.on(2,62,0,.8,b));
        auto hold=std::uint64_t(rate*.08),end=hold+std::uint64_t(rate*.05)+2;
        for(std::uint64_t i=0;i<end;++i){if(i==hold){e.off(1);e.off(2);legacy.off(1);nested.off(2);}auto f=e.tick();auto l=legacy.tick();auto n=nested.tick();check(f.l==l.l+(n.primary+n.middle)&&f.r==l.r+n.deep);check(f.primary==n.primary&&f.middle==n.middle&&f.deep==n.deep);++frames;}
        auto f=e.tick();check(f.l==0&&f.r==0&&f.primary==0&&f.middle==0&&f.deep==0);
    }
    Engine a,b;check(a.prepare(48000)&&b.prepare(48000));p[3]=1;for(int i=0;i<8;++i)check(a.on(i,48+i,0,1,p)&&b.on(i,48+i,0,1,p));check(!a.on(8,60,0,1,p));
    std::array<double,1024> l{},r{},x{},y{},z{};std::array<float,1024> mono{};double* stereo[]={l.data(),r.data()};float* m[]={mono.data()};
    for(unsigned i=0;i<1024;++i){auto f=a.tick(),g=b.tick();check(f.l==g.l&&f.r==g.r&&f.l==f.r&&std::abs(f.l)<=.400000000000001);check(std::abs(f.l-(f.primary+f.middle+f.deep))<1e-15);write(f,stereo,2,x.data(),y.data(),z.data(),i);write<float>(g,m,1,nullptr,nullptr,nullptr,i);check(mono[i]==float(l[i])&&x[i]==f.primary&&y[i]==f.middle&&z[i]==f.deep);}
    a.reset();check(a.tick().l==0);auto t=std::chrono::steady_clock::now();double total=0;for(int i=0;i<480000;++i)total+=std::abs(b.tick().l);check(total>1&&std::isfinite(total));std::cout<<"mixed paired frames="<<frames<<"; 8-voice 10s benchmark="<<std::chrono::duration<double>(std::chrono::steady_clock::now()-t).count()<<" s\n";
    if(argc>1){demo("main.wav",0);demo("primary-middle.wav",1);demo("deep.wav",2);}
}
