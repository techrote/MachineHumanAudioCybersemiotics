// Native DSP chain only: no VST3 ABI, host or listening claims.
#include "engine.hpp"
#include "freeze.hpp"
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
namespace gr=mhac::golden;
namespace fs=mhac::freeze;
using Frame=std::array<double,3>; // dry, processed L, processed R
using Audio=std::vector<Frame>;
void check(bool ok,const char* msg){if(!ok)throw std::runtime_error(msg);}
struct Patch {gr::State instrument; fs::State effect;};
Patch patch(){return {gr::encode({0,.25,.18,.8,.55}),fs::encode({.64,.9,1.,0,0,1.,.1,.65,.25,0})};}
Audio render(unsigned sr,const Patch& p,const std::vector<unsigned>& blocks,bool wet){
    gr::Params ip{}; fs::Params fp{};
    check(gr::decode(p.instrument,ip)&&fs::decode(p.effect,fp),"invalid patch");
    gr::Engine synth; fs::Engine fx; synth.restore(ip); check(synth.reset(sr),"rate"); fx.reset(sr); fx.restore(fp);
    const auto at=[sr](unsigned ms){return std::uint64_t(sr)*ms/1000;};
    const auto frames=at(4000); Audio out(frames); std::uint64_t cursor=0; std::size_t block=0;
    while(cursor<frames){
        unsigned n=blocks[block++%blocks.size()]; check(n>0,"zero block");
        const auto end=std::min(frames,cursor+n);
        for(;cursor<end;++cursor){
            // The score is absolute-time; each simulated block processes its local events in order.
            if(cursor==at(0))check(synth.noteOn(0,48,1,.8),"note 1");
            if(cursor==at(137))check(synth.noteOn(0,55,2,.75),"note 2");
            if(cursor==at(503)){synth.set(gr::Delete,.75);check(synth.noteOn(0,60,3,.65),"note 3");}
            if(cursor==at(649))fx.set(fs::Hold,1);
            if(cursor==at(825))fx.set(fs::A,.2);
            if(cursor==at(1001))fx.set(fs::Mode,.5);
            if(cursor==at(1133))fx.set(fs::Hold,0);
            if(cursor==at(1299)){fx.set(fs::Mode,1);fx.set(fs::Hold,1);check(synth.noteOn(0,67,4,.75),"note 4");}
            if(cursor==at(1503))fx.set(fs::C,.05);
            if(cursor==at(1701)){fx.set(fs::Hold,0);fx.set(fs::Bypass,1);check(synth.noteOn(0,52,5,.8),"note 5");}
            if(cursor==at(2101)){fx.set(fs::Bypass,0);synth.set(gr::Gain,.35);check(synth.noteOn(0,57,6,.7),"note 6");}
            if(cursor==at(2401)){for(int id=1;id<=6;++id)synth.noteOff(0,0,id);}
            const double dry=synth.next(); const double gain=fx.nextGain();
            const double l=fs::Engine::apply(dry,wet?gain:1.);
            const double r=fs::Engine::apply(dry*.75,wet?gain:1.);
            check(std::isfinite(dry)&&std::isfinite(l)&&std::isfinite(r),"nonfinite");
            check(std::abs(dry)<=.5&&std::abs(l)<=std::abs(dry)&&std::abs(r)<=std::abs(dry*.75),"gain bound");
            check(std::abs(r-l*.75)<1e-14,"stereo gain incoherence");
            if(cursor>=at(2450))check(dry==0&&l==0&&r==0,"release tail");
            out[cursor]={dry,l,r};
        }
    }
    check(synth.active()==0,"stuck voice"); return out;
}
void write16(std::ostream& s,std::uint16_t v){s.put(char(v&255));s.put(char(v>>8));}
void write32(std::ostream& s,std::uint32_t v){write16(s,std::uint16_t(v));write16(s,std::uint16_t(v>>16));}
void wav(const std::string& name,const Audio& audio,unsigned sr,bool wet){
    std::ofstream f(name,std::ios::binary);check(bool(f),"wav open");
    const auto size=std::uint32_t(audio.size()*4);f.write("RIFF",4);write32(f,36+size);f.write("WAVEfmt ",8);write32(f,16);write16(f,1);write16(f,2);write32(f,sr);write32(f,sr*4);write16(f,4);write16(f,16);f.write("data",4);write32(f,size);
    for(const auto& a:audio){for(double v:{wet?a[1]:a[0],wet?a[2]:a[0]*.75})write16(f,std::uint16_t(std::int16_t(std::lround(v*16384.))));}
    check(bool(f),"wav write");
}
int main(int argc,char** argv){try{
    check(argc<=2,"usage: chain [output-directory]"); const auto p=patch();
    gr::Params ip{}; fs::Params fp{};check(gr::decode(p.instrument,ip)&&fs::decode(p.effect,fp),"decode");
    const Patch restored{gr::encode(ip),fs::encode(fp)};check(p.instrument==restored.instrument&&p.effect==restored.effect,"patch roundtrip");
    auto corrupt=p;corrupt.effect[0]='X';bool rejected=false;try{(void)render(48000,corrupt,{64},true);}catch(const std::runtime_error&){rejected=true;}check(rejected,"corrupt patch accepted");
    std::uint64_t compared=0;
    for(unsigned sr:{8000u,24000u,44100u,48000u,96000u}){
        const auto a=render(sr,p,{64},true),b=render(sr,restored,{1,7,31,127,512,3,1024},true),dry=render(sr,p,{257},false);
        check(a==b,"partition or restored patch changed output");
        double e0=0,e1=0,peak=0;std::uint64_t differences=0;
        for(std::size_t i=0;i<a.size();++i){check(a[i][0]==dry[i][0],"effect influenced synth");check(dry[i][0]==dry[i][1],"dry reference mismatch");e0+=a[i][0]*a[i][0];e1+=a[i][1]*a[i][1];peak=std::max(peak,std::abs(a[i][1]));differences+=a[i][0]!=a[i][1];}
        check(e0>0&&e1>0&&e1<e0&&differences>0,"effect did not alter signal");compared+=a.size();
        std::cout<<sr<<" Hz frames="<<a.size()<<" altered="<<differences<<" wet_peak="<<peak<<" energy_ratio="<<e1/e0<<'\n';
        if(argc==2&&sr==48000){wav(std::string(argv[1])+"/golden-dry.wav",a,sr,false);wav(std::string(argv[1])+"/golden-freeze.wav",a,sr,true);}
    }
    std::cout<<"PASS paired frames="<<compared<<" (exact same-toolchain; DSP only)\n";return 0;
}catch(const std::exception& e){std::cerr<<"FAIL: "<<e.what()<<'\n';return 1;}}
