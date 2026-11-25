#include "live.hpp"
#include <cstdlib>
#include <cstdio>
#include <fstream>
#include <string>
#include <chrono>
using namespace mhac::forge;
void check(bool ok,const char* what){if(!ok){std::fprintf(stderr,"FAIL: %s\n",what);std::exit(1);}}
int main(int argc,char** argv){
    const Params old{1,1,0,1,1,0};const LiveParams patch{1,1,0,1,1,0,0};
    auto legacy=encode(old);LiveParams p=liveDefaults;
    check(decodeLive(legacy.data(),legacy.size(),p)&&p==patch,"legacy");
    p[Quality]=1;auto bytes=encodeLive(p);LiveParams decoded{};
    check(decodeLive(bytes.data(),bytes.size(),decoded)&&decoded==p,"state");
    for(std::size_t n=0;n<bytes.size();++n)check(!decodeLive(bytes.data(),n,decoded)&&decoded==p,"truncated");
    bytes[30]=0xc0;bytes[31]=0x7f;check(!decodeLive(bytes.data(),bytes.size(),decoded)&&decoded==p,"nan quality");
    auto bad=p;bad[Quality]=.25f;LiveForge invalid;check(!invalid.restore(bad)&&invalid.params()==liveDefaults,"invalid quality");
    for(double sr:{1234.568,8000.,12345.678,44100.,48000.,96000.,123456.78,192000.,384000.,1234567.8}){
        LiveForge e;check(e.restore(patch)&&e.reset(sr),"prepare");
        std::array<Oversampled,3> ref;for(unsigned i=0;i<3;++i)check(ref[i].restore(old)&&ref[i].prepare(sr,1u<<i),"reference");
        const unsigned fade=unsigned(std::ceil(sr*.005));
        // 1x -> 4x, then interrupt halfway with a move to 2x.
        const unsigned change=100, interrupt=change+std::max(1u,fade/2);
        const double partial=double(interrupt-change)/fade;
        for(unsigned n=0;n<interrupt+fade+100;++n){
            if(n==change)e.set(Quality,1);
            if(n==interrupt)e.set(Quality,.5);
            const double l=.15*std::sin(n*.17),r=.12*std::cos(n*.31);auto y=e.process(l,r);
            std::array<double,3> w{1,0,0};
            if(n>=interrupt){double t=std::min(1.,double(n-interrupt+1)/fade);w={(1-t)*(1-partial),t,(1-t)*partial};}
            else if(n>=change){double t=double(n-change+1)/fade;w={1-t,0,t};}
            std::array<double,2> expected{};for(unsigned i=0;i<3;++i){auto a=ref[i].process(l,r);for(unsigned c=0;c<2;++c)expected[c]+=w[i]*a[c];}
            for(unsigned c=0;c<2;++c)check(std::abs(y[c]-expected[c])<1e-14,"warm transition oracle");
        }
        auto bypass=patch;bypass[Bypass]=1;check(e.restore(bypass)&&e.reset(sr),"bypass setup");
        for(unsigned n=0;n<100;++n){e.set(Quality,double(n%3)*.5);auto y=e.process(n==0?.25f:0.f,n==0?-.5f:0.f);check(y[0]==(n==32?.25f:0.f)&&y[1]==(n==32?-.5f:0.f),"aligned bypass");}
        check(e.restore(patch)&&e.reset(sr),"reset");
        for(unsigned n=0;n<256;++n){e.set(Quality,double(n%3)*.5);auto y=e.process(1e200,-1e200);check(std::isfinite(y[0])&&std::abs(y[0])<=1&&std::abs(y[1])<=1,"extreme");}
        for(unsigned n=0;n<100;++n){auto y=e.process(std::numeric_limits<double>::quiet_NaN(),0.);if(n>64)check(y[0]==0&&y[1]==0,"finite tail");}
    }
    LiveForge e;check(!e.reset(0)&&!e.reset(2000001)&&!e.reset(std::numeric_limits<double>::infinity()),"reject rates");
    std::ofstream raw;if(argc>1)raw.open(std::string(argv[1])+"/quality-sweep.raw",std::ios::binary);
    check(e.restore(patch)&&e.reset(48000),"demo setup");double peak=0, sum=0;auto start=std::chrono::steady_clock::now();
    for(unsigned n=0;n<192000;++n){if(n==48000)e.set(Quality,.5);if(n==96000)e.set(Quality,1);if(n==144000)e.set(Quality,0);
        const double t=n/48000.,phase=6.283185307179586*(500*t+1800*t*t);auto y=e.process(.20*std::cos(phase)+.12*std::cos(6.283185307179586*12000*t),.20*std::sin(phase)-.12*std::sin(6.283185307179586*12000*t));
        for(double v:y){peak=std::max(peak,std::abs(v));sum+=v;if(raw){auto s=std::uint16_t(std::int16_t(std::lround(v*32767)));char b[2]={char(s&255),char(s>>8)};raw.write(b,2);}}
    }
    std::printf("4s quality sweep peak %.9g checksum %.9g elapsed %.6fs\n",peak,sum,std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count());
    std::puts("PASS: state migration, interrupted warm fades, bypass, extreme input, tail and ten rates");
}
