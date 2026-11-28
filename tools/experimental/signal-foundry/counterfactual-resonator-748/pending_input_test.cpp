#include "harmonic_bank.hpp"
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>
using namespace mhac::counterfactual;
static unsigned checks=0;
static void check(bool ok){++checks;if(!ok){std::cerr<<"FAIL "<<checks<<'\n';std::exit(1);}}
static bool same(IntegerState a,IntegerState b){return a.x==b.x&&a.y==b.y;}
static constexpr double pi=3.14159265358979323846;
static void wav(const std::string& path,const std::vector<Stereo>& samples){
    std::ofstream f(path,std::ios::binary);
    const auto u=[&](unsigned v,unsigned n){for(unsigned i=0;i<n;++i)f.put(static_cast<char>((v>>(8*i))&255));};
    const unsigned bytes=static_cast<unsigned>(samples.size()*4);
    f.write("RIFF",4);u(36+bytes,4);f.write("WAVEfmt ",8);u(16,4);u(1,2);u(2,2);u(48000,4);u(192000,4);u(4,2);u(16,2);f.write("data",4);u(bytes,4);
    for(auto s:samples){u(static_cast<unsigned>(static_cast<int>(std::round(s.left*32767))),2);u(static_cast<unsigned>(static_cast<int>(std::round(s.right*32767))),2);}check(bool(f));
}
int main(int argc,char** argv){
    for(double rate:{1000.,1234.5678,44100.,48000.,96000.,1234567.8,2000000.}){
        for(unsigned mix:{0u,250u,1000u}){
            Processor a,b;Controls c{250,1000,800,1,false,false,static_cast<std::uint16_t>(mix)};
            check(a.set(c)&&b.set(c)&&a.prepare(rate)&&b.prepare(rate));
            // Both start the window at the same clock phase; oracle sees a zero prefix.
            a.process(1,-1);b.process(0,0);
            a.requestIntervention();b.requestIntervention();a.discardPendingInput();a.discardPendingInput();
            for(unsigned i=0;i<static_cast<unsigned>(std::ceil(rate/1000))+32;++i){
                const auto x=a.process(0.25,-0.5),y=b.process(0.25,-0.5);
                check(x.left==y.left&&x.right==y.right&&a.ticks()==b.ticks()&&a.interventions()==b.interventions());
                check(same(a.lattice(0),b.lattice(0))&&same(a.lattice(1),b.lattice(1)));
            }
            check(a.interventions()==1);
        }
    }
    // The original half-second gate fixture, with a 33-sample boundary census.
    // Four treatments: broadband/filtered x retained/discarded pending drive.
    unsigned distinguish[2]={0,0};
    for(unsigned gate=23984;gate<=24016;++gate){
        std::array<HarmonicBank,4> banks;std::array<MemoryConfig,4> configs;
        std::array<std::vector<Stereo>,4> renders;
        for(unsigned j=0;j<4;++j){auto& c=configs[j];c.wet=1000;
            for(auto& b:c.bands){b.gain=800;b.peakMix=1000;b.excite=false;}
            c.bands[0].hz=250;c.bands[1].hz=900;
            for(unsigned k=0;k<2;++k){c.bands[k].excite=true;c.bands[k].selectivity=(j%2)?1000:0;c.bands[k].discardOnClose=j>=2;}
            check(banks[j].set(c)&&banks[j].prepare(48000));
        }
        double diff[2]={0,0};
        const unsigned end=gate==24000?144000:gate+2400;
        for(unsigned i=0;i<end;++i){
            if(i==gate||i==96000){for(unsigned j=0;j<4;++j){for(auto& b:configs[j].bands){b.excite=false;b.erase=i==96000;}check(banks[j].set(configs[j]));}}
            const double in=i<gate?0.35*std::sin(2*pi*250*i/48000):0;
            std::array<Stereo,4> s{};
            for(unsigned j=0;j<4;++j){s[j]=banks[j].process(in,0);check(s[j].right==0&&std::abs(s[j].left)<=1);
                if(i>=120000)check(s[j].left==0);
                if(gate==24000&&argc==2)renders[j].push_back(s[j]);}
            if(i>=gate+240&&i<gate+2400){for(unsigned j=0;j<2;++j){const double d=s[2*j].left-s[2*j+1].left;diff[j]+=d*d;}}
        }
        for(unsigned j=0;j<2;++j)if(diff[j]>1e-12)++distinguish[j];
        if(gate==24000){
            std::cout<<"gate 24000 tail difference RMS retained/discarded "<<std::sqrt(diff[0]/2160)<<' '<<std::sqrt(diff[1]/2160)<<'\n';
            check(diff[0]==0&&diff[1]>1e-6);
            if(argc==2){const char* names[]={"broad-retain.wav","selective-retain.wav","broad-discard.wav","selective-discard.wav"};for(unsigned j=0;j<4;++j)wav(std::string(argv[1])+"/"+names[j],renders[j]);}
        }
    }
    std::cout<<"33 gate offsets, nonidentical tails retained/discarded "<<distinguish[0]<<' '<<distinguish[1]<<'\n';
    // Explicit per-band discard leaves siblings unaffected and does not erase a lattice.
    HarmonicBank a,b;MemoryConfig c;c.wet=1000;for(auto& x:c.bands)x.peakMix=1000;
    check(a.set(c)&&b.set(c)&&a.prepare(48000)&&b.prepare(48000));
    for(unsigned i=0;i<4800;++i){a.process(0.7,-0.4);b.process(0.7,-0.4);}
    const auto before=a.lattice(1,0);check(!same(before,{}));check(a.discardPendingInput(1)&&!a.discardPendingInput(4));check(same(before,a.lattice(1,0)));
    for(unsigned i=0;i<2400;++i){a.process(0,0);b.process(0,0);for(unsigned j:{0u,2u,3u})for(unsigned k=0;k<2;++k)check(same(a.lattice(j,k),b.lattice(j,k)));}
    std::cout<<checks<<" checks PASS\n";
}
