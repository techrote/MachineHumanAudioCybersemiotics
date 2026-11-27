#include "harmonic_bank.hpp"
#include <chrono>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <limits>
#include <string>
#include <vector>
using namespace mhac::counterfactual;
static unsigned long long checks=0;
static void check(bool ok){++checks;if(!ok){std::cerr<<"FAIL "<<checks<<'\n';std::exit(1);}}
static bool same(IntegerState a,IntegerState b){return a.x==b.x&&a.y==b.y;}
static constexpr double pi=3.14159265358979323846;
static double response(double rate,unsigned hz,double ratio){
    BandInput f;check(f.tune(rate,hz));double sum=0;
    const double center=std::min(double(hz),rate/16);
    const unsigned n=static_cast<unsigned>(std::ceil(80*rate/center));
    for(unsigned i=0;i<n;++i){const auto s=f.process(0.5*std::sin(2*pi*center*ratio*i/rate),0);
        check(s.right==0&&std::isfinite(s.left));if(i>=n/2)sum+=s.left*s.left;}
    return std::sqrt(sum/(n-n/2));
}
static void wav(const std::string& path,const std::vector<Stereo>& samples){
    std::ofstream f(path,std::ios::binary);const auto u=[&](unsigned v,unsigned n){for(unsigned i=0;i<n;++i)f.put(static_cast<char>((v>>(8*i))&255));};
    const unsigned bytes=static_cast<unsigned>(samples.size()*4);
    f.write("RIFF",4);u(36+bytes,4);f.write("WAVEfmt ",8);u(16,4);u(1,2);u(2,2);u(48000,4);u(192000,4);u(4,2);u(16,2);f.write("data",4);u(bytes,4);
    for(auto s:samples){u(static_cast<unsigned>(static_cast<int>(std::round(s.left*32767))),2);u(static_cast<unsigned>(static_cast<int>(std::round(s.right*32767))),2);}check(bool(f));
}
int main(int argc,char** argv){
    for(double rate:{1000.,1234.5678,44100.,48000.,96000.,1234567.8,2000000.}){
        const double center=response(rate,6000,1),half=response(rate,6000,0.5),octave=response(rate,6000,2);
        check(center>0.34&&center<0.37&&half<center*0.19&&octave<center*0.19);
        std::cout<<rate<<" Hz: RMS half/center/octave "<<half<<' '<<center<<' '<<octave<<'\n';
        HarmonicBank a,b;MemoryConfig c;c.wet=1000;for(auto& x:c.bands){x.selectivity=1000;x.peakMix=1000;}
        check(a.set(c)&&b.set(c)&&a.prepare(rate)&&b.prepare(rate));
        std::array<float,63> l{},r{},ol{},orr{};
        for(unsigned j=0;j<100;++j){const unsigned n=1+j%63;
            for(unsigned i=0;i<n;++i){l[i]=static_cast<float>(0.7*std::sin(0.1*(j+i)));r[i]=0;}
            a.processBlock(l.data(),r.data(),ol.data(),orr.data(),n);
            for(unsigned i=0;i<n;++i){const auto s=b.process(l[i],r[i]);check(ol[i]==static_cast<float>(s.left)&&orr[i]==0&&s.right==0&&std::abs(s.left)<=1);}
        }
        auto bad=c;bad.bands[3].selectivity=1001;check(!a.set(bad)&&a.config().bands[3].selectivity==1000);
        check(!a.prepare(std::numeric_limits<double>::infinity()));
        auto s=a.process(std::numeric_limits<double>::quiet_NaN(),std::numeric_limits<double>::infinity());check(std::isfinite(s.left)&&s.right==0);
    }
    // Two exact-clock bands: 250 Hz excitation, 900 Hz rejection. Gate at 0.5 s,
    // preserving accumulated memory but discarding filter history.
    HarmonicBank broad,selective;MemoryConfig c;c.wet=1000;
    for(auto& b:c.bands){b.gain=800;b.peakMix=1000;b.excite=false;}
    c.bands[0].hz=250;c.bands[1].hz=900;c.bands[0].excite=c.bands[1].excite=true;
    check(broad.set(c)&&broad.prepare(48000));c.bands[0].selectivity=c.bands[1].selectivity=1000;
    check(selective.set(c)&&selective.prepare(48000));
    std::vector<Stereo> x,y;x.reserve(144000);y.reserve(144000);
    for(unsigned i=0;i<144000;++i){
        if(i==24000){
            check(!same(broad.lattice(0,0),{})&&!same(broad.lattice(1,0),{}));
            check(!same(selective.lattice(0,0),{})&&same(selective.lattice(1,0),{}));
            c.bands[0].excite=c.bands[1].excite=false;check(selective.set(c));auto d=c;d.bands[0].selectivity=d.bands[1].selectivity=0;check(broad.set(d));}
        if(i==96000){c.bands[0].erase=c.bands[1].erase=true;check(selective.set(c));auto d=c;d.bands[0].selectivity=d.bands[1].selectivity=0;check(broad.set(d));}
        const double in=i<24000?0.35*std::sin(2*pi*250*i/48000):0;
        auto a=broad.process(in,0),b=selective.process(in,0);check(a.right==0&&b.right==0);
        if(i>=120000)check(a.left==0&&b.left==0);
        x.push_back(a);y.push_back(b);
    }
    check(same(selective.lattice(0,0),{})&&same(selective.lattice(1,0),{}));
    if(argc==2){wav(std::string(argv[1])+"/broadband.wav",x);wav(std::string(argv[1])+"/selective-input.wav",y);}
    // Closing the input gate clears filter history without clearing the lattice.
    // Per-band pulse/gain must not disturb sibling histories.
    HarmonicBank control,altered;MemoryConfig p;p.wet=1000;
    for(auto& band:p.bands){band.peakMix=1000;band.selectivity=500;}
    check(control.set(p)&&altered.set(p)&&control.prepare(48000)&&altered.prepare(48000));
    for(unsigned i=0;i<96000;++i){
        if(i==24000){for(auto& band:p.bands)band.excite=false;check(control.set(p)&&altered.set(p));}
        if(i==48000){p.bands[1].gain=0;check(altered.set(p)&&altered.pulse(1)&&altered.pulse(1));}
        if(i==72000){p.bands[1].gain=750;p.bands[1].hz=500;check(altered.set(p));}
        const double in=i<24000?0.8*std::sin(2*pi*165*i/48000):0;
        const auto a=control.process(in,0),b=altered.process(in,0);
        check(a.right==0&&b.right==0&&std::isfinite(b.left));
        for(unsigned j:{0u,2u,3u})check(same(control.lattice(j,0),altered.lattice(j,0)));
        if(i==47999)check(!same(control.lattice(1,0),{})&&same(control.lattice(1,0),altered.lattice(1,0)));
    }
    check(!altered.pulse(4));
    HarmonicBank bench;for(auto& b:c.bands){b.excite=true;b.erase=false;b.selectivity=1000;}check(bench.set(c)&&bench.prepare(96000));
    double sink=0,maxUs=0,total=0;unsigned misses=0;
    std::array<double,384> tone{};for(unsigned i=0;i<tone.size();++i)tone[i]=0.8*std::sin(2*pi*i/tone.size());
    for(unsigned k=0;k<4000;++k){const auto start=std::chrono::steady_clock::now();for(unsigned i=0;i<32;++i)sink+=std::abs(bench.process(tone[(k*32+i)%tone.size()],0).left);
        const double us=std::chrono::duration<double,std::micro>(std::chrono::steady_clock::now()-start).count();total+=us;maxUs=std::max(maxUs,us);if(us>333.333)++misses;}
    check(sink>0);
    std::cout<<checks<<" checks PASS; mean "<<total/4000<<" us, max "<<maxUs<<" us, misses "<<misses<<"/4000, sink "<<sink<<'\n';
}
