#include "integrated.hpp"
#include <chrono>
#include <cstdlib>
#include <iostream>
using namespace prism;
void check(bool b,const char* msg){if(!b){std::cerr<<msg<<'\n';std::exit(1);}}
C input(std::size_t t,double sr){double s=double(t)/sr;return std::polar(.17,tau*(300*s+125*s*s))+std::polar(.13,tau*720*s)+std::polar(.11,tau*800*s);}
int main(){
    const LiveParams old{.75,.5,1,.75,.5,0};const auto legacy=encode(old);IntegratedParams p{};
    check(decodeIntegrated(legacy.data(),legacy.size(),p)&&p[Retention]==0,"legacy migration");for(unsigned i=0;i<Count;++i)check(p[i]==old[i],"legacy values");
    p[Retention]=.625;auto bytes=encodeIntegrated(p);IntegratedParams back{};check(decodeIntegrated(bytes.data(),bytes.size(),back)&&p==back,"roundtrip");
    for(std::size_t n=0;n<bytes.size();++n)check(!decodeIntegrated(bytes.data(),n,back)&&back==p,"truncated state atomicity");
    auto bad=bytes;bad[30]=128;bad[31]=127;check(!decodeIntegrated(bad.data(),bad.size(),back)&&back==p,"infinite retention");bad=bytes;bad[3]='9';check(!decodeIntegrated(bad.data(),bad.size(),back),"unknown version");
    double legacyError=0,formatError=0,peak=0,sweepRms=0;std::size_t tested=0;
    for(double sr:{1000.,1234.5678,8000.,44100.,48000.,96000.,192000.,384000.,1234567.8,2000000.}){
        IntegratedPrism a,b;LivePrism prev;check(a.prepare(sr)&&b.prepare(sr)&&prev.prepare(sr),"prepare");
        check(decodeIntegrated(legacy.data(),legacy.size(),p),"legacy decode");a.restore(p);a.reset();prev.restore(old);prev.reset();
        auto n=a.latency();for(std::size_t t=0;t<4*n;++t){auto x=input(t,sr);auto y=a.step(x.real(),x.imag()),z=prev.step(x.real(),x.imag());legacyError=std::max(legacyError,std::abs(y-z));}check(legacyError<2e-13,"legacy render");
        p={.5,1,1,1,0,0,1};a.restore(p);a.reset();std::vector<C> xs(4*n);for(std::size_t t=0;t<xs.size();++t){xs[t]=input(t,sr);a.set(Grid,double((t/37)%3)*.5);check(a.step(xs[t].real(),xs[t].imag())==(t<n?C{}:xs[t-n]),"exact neutral sweep");++tested;}
        p={1,.5,1,.75,0,0,1};a.restore(p);b.restore(p);a.reset();b.reset();
        for(std::size_t t=0;t<4*n;++t){if(t%31==0){double r=double((t/31)%11)/10;a.set(Retention,r);b.set(Retention,r);}auto x=input(t,sr);float l=float(x.real()),r=float(x.imag());auto y=a.step(l,r),z=b.step(l,r);formatError=std::max({formatError,std::abs(y.real()-double(float(z.real()))),std::abs(y.imag()-double(float(z.imag())))});peak=std::max({peak,std::abs(y.real()),std::abs(y.imag())});check(y==z&&std::isfinite(y.real())&&std::isfinite(y.imag()),"determinism");}
        for(std::size_t t=0;t<3*n;++t){a.step(0,0);}check(a.step(0,0)==C{},"finite tail");
    }
    IntegratedPrism a;check(a.prepare(48000),"48k");a.restore({1,1,1,1,0,0,1});a.reset();for(std::size_t t=0;t<48000;++t){auto x=input(t,48000);auto y=a.step(x.real(),x.imag());if(t>=600)sweepRms+=std::norm(y-input(t-600,48000));}
    check(formatError<6e-8&&peak<=1,"format and bounds");std::cout<<"neutral_frames="<<tested<<" legacy_max="<<legacyError<<" float_output_max="<<formatError<<" peak="<<peak<<" offbin_delta_rms="<<std::sqrt(sweepRms/47400)<<'\n';
    auto start=std::chrono::steady_clock::now();double sink=0;for(std::size_t t=0;t<480000;++t)sink+=a.step(.1,.2).real();std::cout<<"10s_processing_ms="<<std::chrono::duration<double,std::milli>(std::chrono::steady_clock::now()-start).count()<<" sink="<<sink<<'\n';
}
