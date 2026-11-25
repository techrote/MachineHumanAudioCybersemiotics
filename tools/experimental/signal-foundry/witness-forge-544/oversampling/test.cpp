#include "oversample.hpp"
#include <complex>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <chrono>
#include <string>
using namespace mhac::forge;
using C=std::complex<double>;
constexpr double pi=3.14159265358979323846;
void check(bool b){if(!b){std::fputs("FAIL\n",stderr);std::exit(1);}}
C tone(double f,unsigned n){return std::polar(1.,2*pi*f*n/48000);}
int main(int argc,char** argv){
    const Params formal{1,1,0,1,1,0};
    double aliases[3]{}; unsigned idx=0;
    for(unsigned f:{1u,2u,4u}){
        Oversampled o;check(o.restore(formal));check(o.prepare(48000,f));C alias{},carrier{},witness{};
        std::ofstream raw;if(argc>1)raw.open(std::string(argv[1])+"/alias-"+std::to_string(f)+"x.raw",std::ios::binary);
        for(unsigned n=0;n<48128;++n){C x=.18*(tone(15000,n)+tone(-12000,n));auto y=o.process(x.real(),x.imag());C z(y[0],y[1]);if(n>=128){alias+=z*std::conj(tone(-6000,n));carrier+=z*std::conj(tone(15000,n));}if(raw){for(double v:y){auto s=std::uint16_t(std::int16_t(std::lround(v*32767)));char b[2]={char(s&255),char(s>>8)};raw.write(b,2);}}}
        aliases[idx++]=std::abs(alias)/48000;std::printf("%ux alias %.12g carrier %.12g\n",f,std::abs(alias)/48000,std::abs(carrier)/48000);
        check(o.prepare(48000,f));for(unsigned n=0;n<48128;++n){C x=.18*(tone(480,n)+tone(720,n)+tone(800,n));auto y=o.process(x.real(),x.imag());if(n>=128)witness+=C(y[0],y[1])*std::conj(tone(400,n));}const double a=std::abs(witness)/48000;std::printf("%ux wanted 400 Hz %.12g\n",f,a);check(std::abs(a-.011664)<.00002);
        for(double sr:{8000.,44100.,48000.,96000.,192000.,384000.}){
            Params dry=formal;dry[Bypass]=1;check(o.restore(dry));check(o.prepare(sr,f));for(unsigned n=0;n<100;++n){auto y=o.process(n==0?.25:0.,n==0?-.5:0.);check(y[0]==(n==32?.25:0.)&&y[1]==(n==32?-.5:0.));}
            Params neutral=formal;neutral[Drive]=.5;check(o.restore(neutral));check(o.prepare(sr,f));double sum=0,max=0;unsigned peak=0;for(unsigned n=0;n<100;++n){auto y=o.process(n==0?.25:0.,0.);sum+=y[0];check(y[1]==0);if(std::abs(y[0])>max){max=std::abs(y[0]);peak=n;}if(n>64)check(y[0]==0);}
            check(peak==32&&std::abs(sum-.25)<1e-5);
            check(o.restore(formal));check(o.prepare(sr,f));Oversampled p;check(p.restore(formal));check(p.prepare(sr,f));for(unsigned n=0;n<4096;++n){if(n==127){p.set(Drive,.2);o.set(Drive,.2);}float x=float(.4*std::sin(.07*n));auto a1=o.process(x,-x);auto a2=p.process(double(x),double(-x));check(std::abs(a1[0]-a2[0])<1e-7&&std::abs(a1[1]-a2[1])<1e-7);}
            check(o.prepare(sr,f));auto z=o.process(std::numeric_limits<double>::infinity(),std::numeric_limits<double>::quiet_NaN());check(z[0]==0&&z[1]==0);for(unsigned n=0;n<1024;++n){auto y=o.process(1e200,-1e200);check(std::isfinite(y[0])&&std::abs(y[0])<=1&&std::abs(y[1])<=1);}
        }
        check(!o.prepare(48000,3));check(!o.prepare(0,f));
        check(o.restore(formal));check(o.prepare(48000,f));double sum=0;auto start=std::chrono::steady_clock::now();for(unsigned n=0;n<480000;++n){auto y=o.process(.1*std::sin(.1*n),.1);sum+=y[0];}std::printf("%ux 10s render %.6fs checksum %.9g\n",f,std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count(),sum);
    }
    check(std::abs(aliases[0]-.005832)<1e-10);check(aliases[1]<aliases[0]*.001&&aliases[2]<aliases[0]*.001);std::puts("PASS");
}
