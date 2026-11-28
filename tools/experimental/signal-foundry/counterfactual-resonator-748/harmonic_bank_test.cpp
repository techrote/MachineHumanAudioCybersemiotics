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
static void writeWav(const std::string& path,const std::vector<Stereo>& data){
    std::ofstream f(path,std::ios::binary);
    const auto u=[&](unsigned v,unsigned n){for(unsigned i=0;i<n;++i)f.put(static_cast<char>((v>>(8*i))&255));};
    const unsigned bytes=static_cast<unsigned>(data.size()*4);
    f.write("RIFF",4);u(36+bytes,4);f.write("WAVEfmt ",8);u(16,4);u(1,2);u(2,2);u(48000,4);u(192000,4);u(4,2);u(16,2);f.write("data",4);u(bytes,4);
    for(auto s:data){u(static_cast<unsigned>(static_cast<int>(std::round(s.left*32767))),2);u(static_cast<unsigned>(static_cast<int>(std::round(s.right*32767))),2);}
    check(bool(f));
}
int main(int argc,char** argv){
    for(double rate:{1000.0,1234.5678,44100.0,48000.0,96000.0,1234567.8,2000000.0}){
        HarmonicBank bank,partition; MemoryConfig c; c.wet=1000;
        check(bank.set(c)&&partition.set(c)&&bank.prepare(rate)&&partition.prepare(rate));
        std::array<Processor,4> oracle{};
        for(unsigned j=0;j<4;++j){auto b=c.bands[j];check(oracle[j].set({b.hz,1000,b.gain,1,b.erase,false,b.peakMix})&&oracle[j].prepare(rate));}
        std::array<float,73> l{},r{},ol{},orr{};
        for(unsigned k=0;k<100;++k){
            unsigned n=1+(k*19)%73;
            for(unsigned i=0;i<n;++i){l[i]=((i+k)%13==0)?0.875f:0;r[i]=((i+k)%17==0)?-0.5f:0;}
            partition.processBlock(l.data(),r.data(),ol.data(),orr.data(),n);
            for(unsigned i=0;i<n;++i){
                auto s=bank.process(l[i],r[i]);Stereo expected{};
                for(auto& b:oracle){auto v=b.process(l[i],r[i]);expected.left+=v.left*0.25;expected.right+=v.right*0.25;}
                check(s.left==expected.left&&s.right==expected.right);
                check(static_cast<float>(s.left)==ol[i]&&static_cast<float>(s.right)==orr[i]);
                check(std::abs(s.left)<=1&&std::abs(s.right)<=1);
            }
        }
        auto bad=c;bad.bands[3].hz=0;check(!bank.set(bad)&&bank.config().bands[3].hz==330);
        check(!bank.prepare(std::numeric_limits<double>::infinity()));
        check(!bank.pulse(4));
        const auto finite=bank.process(std::numeric_limits<double>::quiet_NaN(),std::numeric_limits<double>::infinity());
        check(std::isfinite(finite.left)&&std::isfinite(finite.right));
    }
    HarmonicBank reference,selective;MemoryConfig c;c.wet=1000;
    for(auto& b:c.bands){b.peakMix=1000;b.gain=800;}
    check(reference.set(c)&&selective.set(c)&&reference.prepare(48000)&&selective.prepare(48000));
    std::vector<Stereo> baseline,edited;baseline.reserve(144000);edited.reserve(144000);
    for(unsigned i=0;i<144000;++i){
        if(i==24000){c.bands[2].erase=true; c.bands[2].excite=false;check(selective.set(c));}
        if(i==96000){for(auto& b:c.bands){b.erase=true;b.excite=false;}check(selective.set(c));}
        const double input=i==0?1:0;
        auto a=reference.process(input,0),b=selective.process(input,0);
        check(a.right==0&&b.right==0);
        if(i<24000)check(a.left==b.left);
        if(i<96000)for(unsigned j:{0u,1u,3u})check(same(reference.lattice(j,0),selective.lattice(j,0)));
        if(i>=48000)check(same(selective.lattice(2,0),{}));
        if(i>=120000)check(b.left==0);
        baseline.push_back(a);edited.push_back(b);
    }
    check(!same(reference.lattice(2,0),{}));
    if(argc==2){writeWav(std::string(argv[1])+"/retained.wav",baseline);writeWav(std::string(argv[1])+"/selective.wav",edited);}
    c.bypass=true;check(selective.set(c));for(unsigned i=0;i<1000;++i)selective.process(0,0);
    const auto dry=selective.process(0.25,-0.5);check(dry.left==0.25&&dry.right==-0.5);
    selective.reset();check(selective.process(0,0).left==0);
    HarmonicBank bench;bench.prepare(96000);double sink=0,maxUs=0;unsigned misses=0;
    for(unsigned k=0;k<4000;++k){const auto start=std::chrono::steady_clock::now();for(unsigned i=0;i<32;++i)sink+=bench.process(i==0?1:0,0).left;
        const double us=std::chrono::duration<double,std::micro>(std::chrono::steady_clock::now()-start).count();maxUs=std::max(maxUs,us);if(us>333.333)++misses;}
    std::cout<<checks<<" checks PASS; max "<<maxUs<<" us, misses "<<misses<<"/4000, sink "<<sink<<'\n';
}
