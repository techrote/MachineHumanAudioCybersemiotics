#include "nested.hpp"
#include <cstdlib>
#include <iostream>
#include <fstream>
#include <string>
#include <limits>
#include <chrono>
using namespace offcut::nested;
void check(bool b){if(!b){std::cerr<<"FAIL\n";std::exit(1);}}
void word(std::ofstream& o,unsigned v,int n){for(int i=0;i<n;++i)o.put(char((v>>(8*i))&255));}
void demo(const std::string& name,double ratio,bool mix){
    Engine e;check(e.prepare(48000));Patch p;p.original={.25,1,0,0};p.cut=.12;p.ratio=ratio;
    std::ofstream o(name,std::ios::binary);constexpr unsigned frames=192000,n=frames*4;
    o.write("RIFF",4);word(o,36+n,4);o.write("WAVEfmt ",8);word(o,16,4);word(o,1,2);word(o,2,2);word(o,48000,4);word(o,192000,4);word(o,4,2);word(o,16,2);o.write("data",4);word(o,n,4);
    const int notes[]={48,55,60,64,67,62,55};
    for(unsigned i=0;i<frames;++i){if(i%24000==0&&i<168000)check(e.on(int(i),notes[i/24000],0,.9,p));if(i>=18000&&(i-18000)%24000==0)e.off(int(i-18000));const auto s=e.tick();word(o,unsigned(std::lround((mix?s.sum():s.primary+s.middle)*32767)),2);word(o,unsigned(std::lround((mix?s.sum():s.deep)*32767)),2);}check(bool(o));
}
int main(int argc,char** argv){
    std::uint64_t cases=0,frames=0;double diff=0,err=0;
    for(int x=-100;x<=100;++x)for(int a=0;a<=10;++a)for(int b=0;b<=10;++b)for(int g=0;g<=10;++g){
        const double t=a/10.,u=b/10.;const auto q=offcut::split(x/100.,t,1);
        const auto s=partition({q.primary,q.residual},u,g/10.);
        check(s.primary==q.primary&&std::clamp(s.middle+s.deep,-u,u)==s.middle);
        check(std::clamp(s.sum(),-t,t)==s.primary);
        check(std::abs(s.primary)+std::abs(s.middle)+std::abs(s.deep)<=1.000000000000001);
        if(g==10){err=std::max(err,std::abs(s.sum()-x/100.));check(err<3e-16);}++cases;
    }
    for(double rate:{1000.,1234.568,8000.,44100.,48000.,96000.,192000.,384000.,1234567.8,2000000.}){
        Engine a,b;offcut::Engine original;check(a.prepare(rate)&&b.prepare(rate)&&original.prepare(rate));Patch p;p.original={.25,1,0,0};p.cut=.12;p.ratio=1;auto q=p;q.ratio=8;
        check(a.on(1,48,0,.9,p)&&b.on(1,48,0,.9,q)&&original.on(1,48,0,.9,p.original));
        const auto hold=std::uint64_t(rate*.08),end=hold+std::uint64_t(rate*.05)+2;
        for(std::uint64_t i=0;i<end;++i){if(i==hold){a.off(1);b.off(1);original.off(1);}const auto x=a.tick(),y=b.tick();const auto z=original.tick();
            check(x.primary==y.primary&&x.middle==y.middle&&x.primary==z.l);
            check(std::abs(x.middle)+std::abs(x.deep)<=std::abs(z.r)+1e-16);
            check(std::abs(x.primary)+std::abs(x.middle)+std::abs(x.deep)<=.05+1e-16);
            diff=std::max(diff,std::abs(x.deep-y.deep));++frames;
        }check(a.tick().sum()==0&&b.tick().sum()==0);
    }
    check(diff>.001);
    Engine a,b,c;check(!a.prepare(NAN)&&a.prepare(48000)&&b.prepare(48000)&&c.prepare(48000));Patch p;
    for(int i=0;i<8;++i)check(a.on(i,48+i,0,1,p)&&b.on(i,48+i,0,1,p)&&c.on(i,48+i,0,1,p));
    check(!a.on(8,60,0,1,p)&&!a.on(0,60,0,1,p));
    std::array<double,1024> l{},m{},r{},ll{},mm{},rr{};std::array<float,1024> f{};
    a.render(l.data(),m.data(),r.data(),1024);for(int i=0;i<1024;i+=17)b.render(ll.data()+i,mm.data()+i,rr.data()+i,std::min(17,1024-i));
    c.render(f.data(),static_cast<float*>(nullptr),static_cast<float*>(nullptr),1024);
    check(l==ll&&m==mm&&r==rr);for(unsigned i=0;i<l.size();++i){check(f[i]==float(l[i]));check(std::abs(l[i])+std::abs(m[i])+std::abs(r[i])<=.400000000000001);}
    a.reset();check(a.tick().sum()==0);p.cut=NAN;p.depth=INFINITY;p.ratio=NAN;
    check(!a.on(1,60,0,NAN,p)&&a.on(1,127,INFINITY,2,p));a.off(1);for(int i=0;i<2000;++i)check(a.tick().sum()==0);
    check(a.on(1,127,1200,2,p));for(int i=0;i<1000;++i)check(std::isfinite(a.tick().sum()));a.off(1);for(int i=0;i<1921;++i)check(std::isfinite(a.tick().sum()));check(a.tick().sum()==0);
    const auto start=std::chrono::steady_clock::now();double total=0;for(int i=0;i<480000;++i)total+=std::abs(b.tick().sum());check(total>1&&std::isfinite(total));
    std::cout<<"partition cases="<<cases<<" full reconstruction error="<<err<<" paired frames="<<frames<<" deepest delta="<<diff<<" eight voice 10s benchmark="<<std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count()<<" s\n";
    if(argc>1){std::string d=argv[1];demo(d+"/nested-slow.wav",1,false);demo(d+"/nested-fast.wav",8,false);demo(d+"/nested-mix.wav",8,true);}
}
