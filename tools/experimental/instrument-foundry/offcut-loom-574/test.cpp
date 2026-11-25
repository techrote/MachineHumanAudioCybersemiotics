#include "core.hpp"
#include <cstdlib>
#include <iostream>
#include <fstream>
#include <string>
#include <chrono>
using namespace offcut;
void check(bool v){if(!v){std::cerr<<"failure\n";std::exit(1);}}
void word(std::ofstream& o,unsigned v,int n){for(int i=0;i<n;++i)o.put(char((v>>(8*i))&255));}
void demo(const std::string& name,double colour,bool reconstruct){
    Engine e;check(e.prepare(48000));auto p=defaults;p[0]=.25;p[1]=1;p[2]=colour;p[3]=double(reconstruct);
    std::ofstream o(name,std::ios::binary);constexpr unsigned frames=192000,n=frames*4;
    o.write("RIFF",4);word(o,36+n,4);o.write("WAVEfmt ",8);word(o,16,4);word(o,1,2);word(o,2,2);word(o,48000,4);word(o,192000,4);word(o,4,2);word(o,16,2);o.write("data",4);word(o,n,4);
    for(unsigned i=0;i<frames;++i){if(i%24000==0&&i<168000){const int notes[]={48,55,60,64,67,62,55};check(e.on(int(i),notes[i/24000],0,.9,p));}if(i>=18000&&(i-18000)%24000==0)e.off(int(i-18000));const auto x=e.tick();word(o,unsigned(std::lround(x.l*32767)),2);word(o,unsigned(std::lround(x.r*32767)),2);}check(bool(o));
}
int main(int argc,char** argv){
    unsigned cases=0;double err=0;
    for(int i=-100;i<=100;++i)for(int j=0;j<=10;++j)for(int k=0;k<=10;++k){double x=i/100.,t=j/10.,a=k/10.;const auto p=split(x,t,a);const double z=p.primary+p.residual;err=std::max(err,std::abs(std::clamp(z,-t,t)-p.primary));check(std::clamp(z,-t,t)==p.primary);check(p.residual==0||(std::abs(p.primary)==t&&p.residual*x>0));check(std::abs(z)<=1);++cases;}
    check(split(NAN,.5,1).primary==0);
    auto p=defaults;set(p,2,.7);auto s=encode(p);Params q{};check(decode(s,q)&&encode(q)==s);auto bad=s;bad[0]='X';check(!decode(bad,q)&&encode(q)==s);bad=s;bad[7]=255;check(!decode(bad,q)&&encode(q)==s);
    std::uint64_t frames=0;double delta=0;
    for(double rate:{1000.,1234.568,8000.,44100.,48000.,96000.,192000.,384000.,1234567.8,2000000.}){
        Engine a,b,c;check(a.prepare(rate)&&b.prepare(rate)&&c.prepare(rate));p=defaults;p[1]=1;p[2]=0;auto r=p;r[2]=1;auto z=p;z[3]=1;
        check(a.on(1,48,0,.9,p)&&b.on(1,48,0,.9,r)&&c.on(1,48,0,.9,z));
        const auto hold=std::uint64_t(rate*.08),end=hold+std::uint64_t(rate*.05)+2;
        for(std::uint64_t i=0;i<end;++i){if(i==hold){a.off(1);b.off(1);c.off(1);}const auto x=a.tick(),y=b.tick(),w=c.tick();check(x.l==y.l);check(std::abs(x.l+x.r-w.l)<2e-17&&w.l==w.r);check(x.r==0||x.l*x.r>0);check(std::isfinite(x.l)&&std::abs(x.l)+std::abs(x.r)<=.05);delta=std::max(delta,std::abs(x.r-y.r));++frames;}check(a.tick().l==0&&b.tick().r==0&&c.tick().l==0);
    }
    check(delta>.001);
    Engine a,b;check(!a.prepare(NAN)&&!a.prepare(999)&&a.prepare(48000)&&b.prepare(48000));p=defaults;
    for(int i=0;i<8;++i)check(a.on(i,48+i,0,1,p)&&b.on(i,48+i,0,1,p));
    check(!a.on(8,60,0,1,p)&&!a.on(0,60,0,1,p));
    std::array<float,1024> l{},r{},ll{},rr{};a.render(l.data(),r.data(),1024);for(int i=0;i<1024;i+=17)b.render(ll.data()+i,rr.data()+i,std::min(17,1024-i));check(l==ll&&r==rr);for(unsigned i=0;i<l.size();++i)check(std::abs(l[i])+std::abs(r[i])<=.400001f);
    a.reset();a.render(l.data(),static_cast<float*>(nullptr),1024);for(auto x:l)check(x==0);
    std::cout<<"clip cases="<<cases<<" max reclip error="<<err<<" paired frames="<<frames<<" max residual difference="<<delta<<"; state, capacity, partition, silence PASS\n";
    if(argc>1){std::string d=argv[1];demo(d+"/split-low.wav",0,false);demo(d+"/split-high.wav",1,false);demo(d+"/reconstructed.wav",1,true);}
}
