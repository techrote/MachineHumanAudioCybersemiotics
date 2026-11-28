#include "resonator.hpp"
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <limits>
#include <string>
using namespace mhac::counterfactual;
namespace {
unsigned checks=0;
void check(bool ok){++checks;if(!ok){std::cerr<<"FAIL peak "<<checks<<'\n';std::exit(1);}}
void configure(Processor& p,unsigned mix,double rate=48000){
    check(p.set({250,1000,800,1,false,false})&&p.setPeakMix(mix)&&p.prepare(rate));
}
void windowOracle(){
    // 48 samples/tick at 250 Hz / 48 kHz. Equal absolute peaks retain earliest sign.
    for(unsigned mix:{0u,250u,500u,1000u})for(int sign:{-1,1}){
        Processor p;configure(p,mix);
        for(unsigned i=0;i<48;++i)p.process(i==0?double(sign):i==1?-double(sign):0.0,0);
        // Floating clock may tick on the next frame; zero-sum window remains zero.
        if(p.ticks()==0)p.process(0,0);
        check(p.ticks()==1&&p.lattice(0).x==int(std::round(12.0*sign*mix/1000.0)));
        check(p.lattice(1).x==0&&p.lattice(1).y==0);
        check(!p.setPeakMix(1001)&&p.peakMix()==mix);
        p.reset();check(p.peakMix()==mix&&p.ticks()==0);
        for(unsigned i=0;i<100;++i){auto x=p.process(0,0);check(x.left==0&&x.right==0);}
    }
    Processor p;configure(p,0);p.process(1,0);check(p.setPeakMix(1000));
    while(p.ticks()==0)p.process(0,0);
    check(p.lattice(0).x==12); // selection at window close, not at transient arrival
}
void rateOracle(){
    for(double rate:{1000.,1234.568,8000.,44100.,48000.,96000.,384000.,1234567.8,2000000.}){
        Processor p;configure(p,1000,rate);
        p.process(1,0);unsigned frames=1;
        while(p.ticks()==0&&frames<20001){p.process(0,0);++frames;}
        check(p.ticks()==1&&p.lattice(0).x==12&&p.lattice(1).x==0);
        auto c=p.controls();c.erase=true;check(p.set(c));
        for(unsigned i=0;i<frames*32;++i){auto x=p.process(0,0);check(std::isfinite(x.left)&&std::abs(x.left)<=1&&x.right==0);}
        auto x=p.process(0,0);check(x.left==0&&x.right==0);
        check(!p.prepare(std::numeric_limits<double>::quiet_NaN())&&p.peakMix()==1000);
    }
}
void partitionOracle(){
    constexpr unsigned n=8192;std::array<float,n> l{},r{},a{},b{},c{},d{};
    for(unsigned i=0;i<n;++i){l[i]=i%197==0?0.8f:0;r[i]=i%337==0?-0.9f:0;}
    for(unsigned mix:{0u,250u,1000u}){
        Processor p,q;configure(p,mix);configure(q,mix);
        p.processBlock(l.data(),r.data(),a.data(),b.data(),n);
        for(unsigned i=0;i<n;){const unsigned m=std::min(1+i%127,n-i);q.processBlock(l.data()+i,r.data()+i,c.data()+i,d.data()+i,m);i+=m;}
        check(a==c&&b==d);
        q.reset();for(unsigned i=0;i<n;++i){const auto x=q.process(l[i],r[i]);check(a[i]==static_cast<float>(x.left)&&b[i]==static_cast<float>(x.right));}
        q.reset();for(unsigned i=0;i<200;++i){const auto x=q.process(std::numeric_limits<double>::infinity(),std::numeric_limits<double>::quiet_NaN());check(x.left==0&&x.right==0);}
    }
}
void word(std::ostream& f,unsigned v,unsigned n){for(unsigned i=0;i<n;++i)f.put(static_cast<char>((v>>(8*i))&255));}
void render(unsigned mix,const std::string& dir){
    Processor p;configure(p,mix);constexpr unsigned n=96000;
    std::ofstream f;
    if(!dir.empty()){
        f.open(dir+"/peak-"+std::to_string(mix)+".wav",std::ios::binary);check(bool(f));
        f.write("RIFF",4);word(f,36+n*4,4);f.write("WAVEfmt ",8);word(f,16,4);word(f,1,2);word(f,2,2);word(f,48000,4);word(f,192000,4);word(f,4,2);word(f,16,2);f.write("data",4);word(f,n*4,4);
    }
    double peak=0,tail=0;
    for(unsigned i=0;i<n;++i){
        const double l=i==0?1.0:0.0,r=i==12000?-0.8:0.0;
        const auto x=p.process(l,r);
        for(double v:{x.left,x.right}){
            check(std::isfinite(v)&&std::abs(v)<=1);peak=std::max(peak,std::abs(v));if(i>=n-2400)tail+=v*v;
            if(f.is_open())word(f,static_cast<std::uint16_t>(static_cast<std::int16_t>(std::lround(v*32767))),2);
        }
    }
    if(f.is_open()){f.close();check(bool(f));}
    check(mix==0?peak==0:peak>0&&tail>0);
    std::cout<<"mix="<<mix<<",peak="<<peak<<",tail50ms="<<std::sqrt(tail/4800)<<'\n';
}
}
int main(int argc,char** argv){
    check(argc==1||argc==2);windowOracle();rateOracle();partitionOracle();
    for(unsigned mix:{0u,250u,1000u})render(mix,argc==2?argv[1]:"");
    std::cout<<"PASS "<<checks<<" checks\n";
}
