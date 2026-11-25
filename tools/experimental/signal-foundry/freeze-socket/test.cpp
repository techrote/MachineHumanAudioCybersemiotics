#include "freeze.hpp"
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <chrono>
#include <string>
#include <vector>
#include <random>
using namespace mhac::freeze;
static unsigned checks=0;
void check(bool ok){++checks;if(!ok){std::cerr<<"FAIL at check "<<checks<<'\n';std::exit(1);}}
void close(double a,double b,double eps=1e-10){check(std::abs(a-b)<=eps);}

// Independent literal finite state oracle for #423. Test every bank, all 341
// sequences up to four events, and all three contracts; compare each step.
void finite(){
    for(unsigned code=0;code<256;++code)for(unsigned m=0;m<3;++m)
    for(unsigned len=0,count=1;len<=4;++len,count*=4)for(unsigned word=0;word<count;++word){
        Bank bank{};for(unsigned j=0;j<4;++j)bank[j]=double((code>>(2*j))&3)/3.;
        Socket s; s.configure(bank,false,static_cast<Contract>(m));
        Bank snap=bank; unsigned phase=0;double lat=0.;bool hold=false;unsigned w=word;
        close(s.token(),bank[0]);
        for(unsigned j=0;j<len;++j){
            const unsigned action=w%4;w/=4;
            if(action==0){if(!hold){snap=bank;lat=bank[phase];}hold=true;}
            if(action==1){if(!(hold&&m==1))phase=(phase+1)%4;s.tick();}
            if(action==2)bank[1]=double((unsigned(std::lround(bank[1]*3))+1)%4)/3.;
            if(action==3)hold=false;
            s.configure(bank,hold,static_cast<Contract>(m));
            const double expect=!hold||m==1?bank[phase]:m==0?lat:snap[phase];
            close(s.token(),expect);check(s.slot==phase);
        }
    }
}
void states(){
    Params p=defaults; p[Rate]=.1234567;p[Hold]=1.;p[Mode]=.5;
    auto bytes=encode(p);Params q{};check(decode(bytes,q));
    for(unsigned i=0;i<Count;++i)close(p[i],q[i],.0000005);
    auto good=q;bytes[4]=2;check(!decode(bytes,q));check(q==good);
    bytes=encode(p);put(bytes,8,1000001);check(!decode(bytes,q));check(q==good);
    Engine e;e.restore(p);check(e.slot()==0);close(e.gain(),1.);
    e.set(Rate,std::numeric_limits<double>::quiet_NaN());close(e.params()[Rate],p[Rate]);
    e.set(Count,1);check(e.params()==p);
}
// The same absolute timeline under arbitrary host block partitioning.
template<class T> std::vector<T> timeline(unsigned block,double sr){
    Engine e;e.reset(sr);e.set(Rate,1);e.set(Depth,1);e.set(Mix,1);
    std::vector<T> out;out.reserve(24000);
    for(unsigned base=0;base<24000;base+=block)for(unsigned i=base;i<std::min(base+block,24000u);++i){
        if(i==700)e.set(Hold,1);
        if(i==1100)e.set(B,.9);
        if(i==1500)e.set(Mode,.5);
        if(i==3000)e.set(Mode,1);
        if(i==4500)e.set(Hold,0);
        if(i==5500)e.set(Bypass,1);
        if(i==6200)e.set(Bypass,0);
        if(i==9000)e.set(A,0);
        const auto g=e.nextGain();const auto x=T(std::sin(i*.031)*.8);const auto y=Engine::apply(x,g);
        check(g>=0&&g<=1);check(std::abs(y)<=std::abs(x));check(std::isfinite(y));out.push_back(y);
    }
    return out;
}
void audio(){
    for(double sr:{8000.,44100.,48000.,96000.,192000.}){
        auto f=timeline<float>(1,sr);auto d=timeline<double>(1,sr);
        for(unsigned b:{7u,64u,127u,511u,1024u}){check(f==timeline<float>(b,sr));check(d==timeline<double>(b,sr));}
        for(unsigned i=0;i<f.size();++i)close(f[i],d[i],1e-7);
    }
    Engine e;e.reset(8000);e.set(Rate,1);e.set(Depth,1);e.set(A,0);
    double prev=1;for(unsigned i=0;i<500;++i){double v=e.nextGain();check(std::abs(v-prev)<=.0250000001);prev=v;}
    check(e.slot()==1);e.set(Hold,1);e.set(Mode,.5);for(unsigned i=0;i<1000;++i)e.nextGain();check(e.slot()==1);
    e.set(B,0);e.set(Bypass,1);for(unsigned i=0;i<40;++i)e.nextGain();close(e.gain(),1.);
    for(double x:{0.,-0.,1.,-1.,1e300,-1e300}){check(Engine::apply(x,1.)==x);close(Engine::apply(x,0.),0.);}
    close(Engine::apply(std::numeric_limits<double>::infinity(),.5),0.);
    close(Engine::apply(std::numeric_limits<float>::quiet_NaN(),.5),0.);
    close(Engine::apply(std::numeric_limits<float>::denorm_min(),1.),0.);
    Socket s;s.configure({0.,.25,.5,1.},true,Contract::Latch);s.tick();close(s.token(),0.);
    s.configure({.2,.8,.5,1.},true,Contract::Snapshot);close(s.token(),.8);s.tick();close(s.token(),.5);
}
// Exercise fractional and extreme SDK validator sample rates. A fallback to
// 48 kHz would silently advance the modulation clock too quickly at high rates.
void sampleRateContract(){
    check(!validSampleRate(999.));check(validSampleRate(1000.));
    check(validSampleRate(2000000.));check(!validSampleRate(2000001.));
    check(!validSampleRate(std::numeric_limits<double>::infinity()));
    check(!validSampleRate(std::numeric_limits<double>::quiet_NaN()));
    Engine e;
    for(double sr:{1000.,1234.5678,44100.1,768000.,1234567.8,2000000.}){
        e.reset(sr);e.set(Rate,1);e.set(Hold,0);e.set(Bypass,0);
        e.set(A,0);e.set(Depth,1);e.set(Mix,1);
        const auto first=static_cast<unsigned>(std::ceil(sr/16.));
        check(e.slot()==0);
        double prev=1.;
        for(unsigned i=0;i<first;++i){
            const auto g=e.nextGain();
            check(std::isfinite(g)&&g>=0.&&g<=1.);
            check(std::abs(g-prev)<=200./sr+1e-12);
            if(i+1<first)check(e.slot()==0);
            prev=g;
        }
        check(e.slot()==1);
        check(prev<=1e-8);
        e.set(Mode,.5);e.set(Hold,1);
        for(unsigned i=0;i<first+1;++i)e.nextGain();
        check(e.slot()==1);
    }
    e.reset(std::numeric_limits<double>::quiet_NaN());e.set(Hold,0);
    for(unsigned i=0;i<2999;++i)e.nextGain();
    check(e.slot()==0);e.nextGain();check(e.slot()==1);
}

void u16(std::ostream& o,unsigned v){o.put(char(v));o.put(char(v>>8));}
void u32(std::ostream& o,unsigned v){u16(o,v);u16(o,v>>16);}
// Identical original carrier, same timed gestures, three separate mode renders.
void demo(const std::string& prefix){
    constexpr unsigned sr=48000,n=sr*5;
    for(unsigned mode=0;mode<3;++mode){
        std::ofstream o(prefix+std::to_string(mode)+".wav",std::ios::binary);
        o.write("RIFF",4);u32(o,36+n*4);o.write("WAVEfmt ",8);u32(o,16);u16(o,1);u16(o,2);u32(o,sr);u32(o,sr*4);u16(o,4);u16(o,16);o.write("data",4);u32(o,n*4);
        Engine e;e.reset(sr);e.set(Mode,mode/2.);e.set(Depth,1.);e.set(A,.15);e.set(B,.45);e.set(C,1.);e.set(D,.25);
        for(unsigned i=0;i<n;++i){
            if(i==sr+sr/8)e.set(Hold,1);
            if(i==2*sr)e.set(A,.95);
            if(i==2*sr+sr/4)e.set(C,.1);
            if(i==3*sr+sr/4)e.set(Hold,0);
            const double t=double(i)/sr,g=e.nextGain();
            const double env=std::min({1.,i/960.,(n-1-i)/960.});
            const double left=env*(.22*std::sin(6.283185307179586*110*t)+.12*std::sin(6.283185307179586*220*t));
            const double right=env*(.22*std::sin(6.283185307179586*110*t)+.12*std::sin(6.283185307179586*330*t));
            u16(o,static_cast<std::uint16_t>(std::lround(32767*Engine::apply(left,g))));
            u16(o,static_cast<std::uint16_t>(std::lround(32767*Engine::apply(right,g))));
        }
        check(bool(o));
    }
}
int main(int argc,char** argv){
    finite();states();audio();sampleRateContract();if(argc==2)demo(argv[1]);
    std::cout<<"PASS "<<checks<<" assertions\n";
    Engine e;double sink=0.;auto begin=std::chrono::steady_clock::now();
    for(unsigned i=0;i<4800000;++i)sink+=e.nextGain();
    auto sec=std::chrono::duration<double>(std::chrono::steady_clock::now()-begin).count();
    std::cout<<"4800000 control frames: "<<sec<<" s; checksum "<<sink<<'\n';
}
