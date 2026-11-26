#include "afterimage.hpp"
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <limits>
#include <string>
using namespace mhac::afterimage;
static unsigned checks=0;
static void check(bool ok){++checks;if(!ok){std::fprintf(stderr,"phase check %u failed\n",checks);std::exit(1);}}
static void prime(Engine& e,int older,int middle){
    check(e.configure({{2,6},Mode::full,0,1})&&e.setHistoryDepth(3));
    for(int pitch:{older,middle,62})check(e.on(pitch,pitch,1)&&e.off(pitch)&&e.tick()==0);
}
static void put16(std::ostream& o,unsigned n){o.put(static_cast<char>(n&255));o.put(static_cast<char>((n>>8)&255));}
static void put32(std::ostream& o,unsigned n){put16(o,n);put16(o,n>>16);}
static void demo(const std::string& path,double mix){
    constexpr unsigned frames=192000;std::ofstream o(path,std::ios::binary);
    o.write("RIFF",4);put32(o,36+frames*2);o.write("WAVEfmt ",8);put32(o,16);put16(o,1);put16(o,1);put32(o,48000);put32(o,96000);put16(o,2);put16(o,16);o.write("data",4);put32(o,frames*2);
    Engine e;check(e.prepare(48000)&&e.configure({{2,6},Mode::full,0,1})&&e.setHistoryDepth(3)&&e.setPhaseMix(mix));
    const int notes[]{57,59,62,48,60,61,62,48};
    for(unsigned i=0;i<frames;++i){const auto step=i/24000,offset=i%24000;
        if(offset==0)check(e.on(0,notes[step],.85));
        if(offset==18000)check(e.off(0,step%4!=3));
        put16(o,static_cast<unsigned>(static_cast<int>(std::lround(e.tick()*32767))));
    }
    check(bool(o));
}
// Independent direct-trigonometric oracle for the previous finite sideband law.
static void rotationRegression(){
    constexpr double tau=6.2831853071795864769;
    struct Probe{double sr,carrier,ratio,beta;unsigned frames;};
    const Probe probes[]{
        {48000,110,2,1.46,1000000}, {96000,13200,1.25,1.5,131072},
        {2000000,8.1758,3,.2,131072}, {1000,400,1,1.5,131072},
        {44100,440,2,0,131072}, {48000,48000*.449,1.5,1.2,131072}
    };
    double worst=0,anchorWorst=0;
    for(const auto& p:probes){
        std::array<double,13> phase{},step{},gain{};
        double total=0;
        for(int k=-6;k<=6;++k){
            const auto i=static_cast<unsigned>(k+6), order=static_cast<unsigned>(std::abs(k));
            // Longer long-double power series, separate from the production coefficient code.
            long double t=1;
            for(unsigned j=1;j<=order;++j)t*=static_cast<long double>(p.beta)/(2*j);
            long double b=t;
            for(unsigned j=1;j<=18;++j){t*=-static_cast<long double>(p.beta)*p.beta/(4*j*(j+order));b+=t;}
            step[i]=p.carrier*(1+k*p.ratio)/p.sr;
            gain[i]=static_cast<double>(b)*(k<0&&order%2?-1.:1.)*std::clamp((.45-std::abs(step[i]))/.05,0.,1.);
            total+=std::abs(gain[i]);
        }
        for(auto& g:gain)g/=std::max(1.,total);
        PhaseMemory oscillator,copy;check(oscillator.configure(p.sr,p.carrier,p.ratio,p.beta));
        for(unsigned frame=0;frame<p.frames;++frame){
            if(frame==513){copy=oscillator;check(!oscillator.configure(p.sr,0,p.ratio,p.beta));}
            double expected=0;
            for(unsigned i=0;i<13;++i)if(gain[i]!=0){
                expected+=gain[i]*std::sin(tau*phase[i]);phase[i]+=step[i];
                if(phase[i]>=1)phase[i]-=1;else if(phase[i]<0)phase[i]+=1;
            }
            const double actual=oscillator.tick();
            const double error=std::abs(actual-std::clamp(expected,-1.,1.));
            worst=std::max(worst,error);if(frame%256==0)anchorWorst=std::max(anchorWorst,error);
            check(std::isfinite(actual)&&std::abs(actual)<=1&&error<2e-11);
            if(frame>=513&&frame<4096)check(copy.tick()==actual);
        }
        check(oscillator.configure(p.sr,p.carrier,p.ratio,p.beta));check(oscillator.tick()==0);
    }
    std::printf("Rotation oracle: worst absolute error %.9g; anchor error %.9g; 1655360 samples\n",worst,anchorWorst);
}
int main(int argc,char** argv){
    rotationRegression();
    constexpr double tau=6.2831853071795864769;
    double worst=0;
    for(double beta:{0.,.2,.8,1.5})for(double ratio:{1.25,1.75,3.}){
        PhaseMemory p;check(p.configure(48000,110,ratio,beta));
        for(unsigned i=0;i<4800;++i){const double a=tau*i*110/48000;
            const double expected=p.normalization()*std::sin(a+beta*std::sin(a*ratio));
            const double y=p.tick(),err=std::abs(y-expected);worst=std::max(worst,err);check(std::isfinite(y)&&std::abs(y)<=1&&err<.0001);
        }
    }
    for(double sr:{1000.,1234.568,8000.,44100.,48000.,96000.,192000.,384000.,1234567.8,2000000.}){
        Engine a,b,c;for(auto* e:{&a,&b,&c})check(e->prepare(sr));
        prime(a,57,59);prime(b,60,61);prime(c,57,59);
        check(a.setPhaseMix(1)&&b.setPhaseMix(1)&&c.setPhaseMix(1));
        check(a.on(0,36,1)&&b.on(0,36,1)&&c.on(0,36,1));
        check(!a.setPhaseMix(std::numeric_limits<double>::quiet_NaN())&&!a.setPhaseMix(-1)&&!a.setPhaseMix(2));
        check(c.setPhaseMix(0)); // captured blend unaffected on active note
        bool differs=false;
        for(unsigned i=0;i<2048;++i){const auto x=a.tick(),y=b.tick(),z=c.tick();check(x==z&&std::isfinite(x)&&std::abs(x)<=.52&&std::isfinite(y)&&std::abs(y)<=.52);differs|=x!=y;}
        check(differs);
        for(auto* e:{&a,&b,&c})check(e->off(0,false));
        for(unsigned i=0;i<static_cast<unsigned>(sr*.032)+2;++i){check(a.tick()==c.tick());check(std::abs(b.tick())<=.52);}
        check(a.tick()==0&&b.tick()==0&&c.tick()==0);
        b.reset();check(b.tick()==0);
        // High pitches and voice replacement: bounded and silent after reset.
        a.reset();check(a.setPhaseMix(1));for(int i=0;i<8;++i)check(a.on(i,127,1,1200));
        for(unsigned i=0;i<64;++i)check(std::abs(a.tick())<=.52);
        int victim=-1;check(a.on(8,36,1,0,&victim)&&victim==0);
        for(unsigned i=0;i<2048;++i){float l=0,r=0;a.render(&l,&r,1);check(l==r&&std::isfinite(l)&&std::abs(l)<=.520001f);}
        a.reset();check(a.tick()==0);
    }
    PhaseMemory clipped;check(clipped.configure(1000,1000,2,1.5));
    for(unsigned i=0;i<100;++i)check(clipped.tick()==0);
    Engine a,b;for(auto* e:{&a,&b}){check(e->prepare(48000));prime(*e,57,59);check(e->setPhaseMix(1));for(int i=0;i<8;++i)check(e->on(i,36+i,1));}
    std::array<double,4096> full{},split{};a.render(full.data(),static_cast<double*>(nullptr),4096);
    for(unsigned i=0;i<4096;){const unsigned n=std::min(257u,4096-i);b.render(split.data()+i,static_cast<double*>(nullptr),n);i+=n;}
    check(full==split);
    for(auto* e:{&a,&b}){int victim=-1;check(e->on(8,55,1,0,&victim)&&victim==0);}
    for(unsigned i=0;i<4096;++i){const auto x=a.tick(),y=b.tick();check(x==y&&std::abs(x)<=.52);}
    if(argc==3&&std::string(argv[1])=="--render"){demo(std::string(argv[2])+"/additive.wav",0);demo(std::string(argv[2])+"/phase.wav",1);}
    std::printf("PASS %u phase-memory checks; worst direct PM error %.9g\n",checks,worst);
}
