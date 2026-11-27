#include "host.hpp"
#include <chrono>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <limits>
#include <string>
using namespace mhac::orbit;
using namespace mhac::orbit::host;
static unsigned checks=0;
static void check(bool x){++checks;if(!x){std::cerr<<"FAIL "<<checks<<'\n';std::exit(1);}}
static void carrierOracle(){
    Spectrum b;check(b.build<68>({-16,4},8,4,9));
    for(int i=0;i<=4096;++i){
        const double phase=tau*i/4096.;
        for(int cut=0;cut<=b.harmonics;++cut){
            double l=0,r=0,x=0,y=0,c[2]{};
            b.sample(phase,cut,l,r);b.sampleCarrier(phase,cut,x,y,c);
            check(l==x&&r==y);
            if(cut>=b.dominant){
                check(std::abs(c[0]-std::cos(phase*b.dominant))<1e-12);
                check(std::abs(c[1]-std::sin(phase*b.dominant))<1e-12);
            }else check(c[0]==0.&&c[1]==0.);
        }
    }
}
static void exercise(){
    carrierOracle();
    for(double rate:{1000.,1234.568,44100.,48000.,96000.,192000.,2000000.}){
        Live a,b,c,d;for(auto* e:{&a,&b,&c,&d}){
            check(e->prepare(rate)&&e->setPatch({1000,10,0,2}));
            for(int k=0;k<8;++k)check(e->on(k,0,36+k,0.,.9));
            check(!e->on(8,0,48,0.,1.));
        }
        double l=0,r=0,x=0,y=0,u=0,v=0,w=0,z=0;bool difference=false;
        for(unsigned i=0;i<unsigned(rate*.007);++i){a.tick(l,r);b.tick(x,y);c.tick(u,v);d.tick(w,z);check(l==x&&r==y&&l==u&&r==v&&l==w&&r==z);}
        for(int k=0;k<8;++k){check(!a.offSpectral(k,0,36+k,std::numeric_limits<double>::quiet_NaN()));check(!a.offSpectral(k,0,36+k,1.1));
            check(a.off(k,0,36+k)&&b.offSpectral(k,0,36+k,0.)&&c.offSpectral(k,0,36+k,1.)&&d.offSpectral(k,0,36+k,1.));
            check(d.offSpectral(k,0,36+k,0.));}
        for(unsigned i=0;i<unsigned(std::ceil(rate*.01))+1;++i){
            a.tick(l,r);b.tick(x,y);c.tick(u,v);d.tick(w,z);
            check(l==x&&r==y&&u==w&&v==z&&std::isfinite(u)&&std::isfinite(v)&&std::abs(u)<=.52&&std::abs(v)<=.52);
            difference|=l!=u||r!=v;
        }
        if(rate>=44100.)check(difference);
        check(a.active()==0&&b.active()==0&&c.active()==0&&d.active()==0&&l==0&&r==0&&u==0&&v==0);
    }
    // No octave allowed by the existing 0.45-times-sample-rate guard: exact fallback.
    Live a,b;for(auto* e:{&a,&b})check(e->prepare(1000.)&&e->setPatch({1000,100,0,2})&&e->on(1,0,69,0.,1.));
    double l=0,r=0,x=0,y=0;for(int i=0;i<20;++i){a.tick(l,r);b.tick(x,y);check(l==x&&r==y);}
    check(a.off(1,0,69)&&b.offSpectral(1,0,69,1.));
    for(int i=0;i<110;++i){a.tick(l,r);b.tick(x,y);check(l==x&&r==y);}
    check(a.active()==0&&b.active()==0);
}
static void put(std::ofstream& o,unsigned x,int n){for(int i=0;i<n;++i){o.put(char(x&255));x>>=8;}}
static void render(const std::string& path,double depth){
    constexpr unsigned rate=48000,n=rate*4;Live e;check(e.prepare(rate)&&e.setPatch({1000,800,0,2}));
    std::ofstream o(path,std::ios::binary);check(bool(o));o.write("RIFF",4);put(o,36+4*n,4);o.write("WAVEfmt ",8);put(o,16,4);put(o,1,2);put(o,2,2);put(o,rate,4);put(o,rate*4,4);put(o,4,2);put(o,16,2);o.write("data",4);put(o,4*n,4);
    for(unsigned i=0;i<n;++i){
        if(i==0||i==rate*2)for(int k=0;k<3;++k)check(e.on(k,0,48+k*7+(i?3:0),0.,.8));
        for(int k=0;k<3;++k)if(i==rate/2+unsigned(k)*733||i==rate*5/2+unsigned(k)*733)check(e.offSpectral(k,0,48+k*7+(i>=rate*2?3:0),depth));
        double l,r;e.tick(l,r);if(i>=rate*7/2)check(l==0&&r==0);
        for(double s:{l,r})put(o,unsigned(int(std::lround(s*32767))),2);
    }
    check(bool(o)&&e.active()==0);
}
static void benchmark(){
    Live e;check(e.prepare(96000)&&e.setPatch({1000,1000,0,2}));
    using Clock=std::chrono::steady_clock;double worst=0,total=0;unsigned misses=0;
    for(unsigned block=0;block<4000;++block){
        if(block%250==0){e.reset();for(int k=0;k<8;++k)check(e.on(k,0,36+k,0.,.8));for(int i=0;i<480;++i){double l,r;e.tick(l,r);}for(int k=0;k<8;++k)check(e.offSpectral(k,0,36+k,1.));}
        double l=0,r=0;const auto start=Clock::now();for(int i=0;i<32;++i)e.tick(l,r);const double us=std::chrono::duration<double,std::micro>(Clock::now()-start).count();
        check(std::isfinite(l)&&std::isfinite(r));total+=us;worst=std::max(worst,us);misses+=us>1000./3.;
    }
    std::cout<<"benchmark 96k/32 mean_us="<<total/4000<<" max_us="<<worst<<" misses="<<misses<<"/4000\n";
}
int main(int argc,char** argv){exercise();if(argc==2){const std::string p=argv[1];render(p+"/spectral-0.wav",0.);render(p+"/spectral-100.wav",1.);benchmark();}std::cout<<"PASS spectral checks="<<checks<<'\n';}
