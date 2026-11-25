#include "cycle.hpp"
#include <cstdlib>
#include <iostream>
#include <fstream>
#include <string>
using namespace loom;
void check(bool b){if(!b){std::cerr<<"failure\n";std::exit(1);}}
void word(std::ofstream& o,unsigned v,int n){for(int i=0;i<n;++i)o.put(char((v>>(8*i))&255));}
void demo(const std::string& path,std::uint16_t mask,bool mono){
    CycleVoice v;CyclePatch p;p.period=.32;p.swaps=mask;check(v.start(48000,69,0,1,p));
    std::ofstream o(path,std::ios::binary);unsigned ch=mono?1:2,n=192000*ch*2;
    o.write("RIFF",4);word(o,36+n,4);o.write("WAVEfmt ",8);word(o,16,4);word(o,1,2);word(o,ch,2);word(o,48000,4);word(o,48000*ch*2,4);word(o,ch*2,2);word(o,16,2);o.write("data",4);word(o,n,4);
    for(int i=0;i<192000;++i){if(i==180000)v.off();auto x=v.tick();word(o,unsigned(std::lround((mono?(x.l+x.r)*.5:x.l)*32767)),2);if(!mono)word(o,unsigned(std::lround(x.r*32767)),2);}check(bool(o));
}
int main(int argc,char** argv){
    unsigned long long frames=0;double maxDiff=0;
    for(double sr:{8000.,44100.,48000.,96000.,192000.,384000.}){
        for(unsigned mask:{0u,1u,0xaaaau,0xffffu}){
            CycleVoice a,b;CyclePatch p;p.period=.025;p.swaps=0;check(a.start(sr,57,13,.8,p));p.swaps=std::uint16_t(mask);check(b.start(sr,57,13,.8,p));
            const auto period=a.period;bool parity=false;unsigned k=0;
            for(std::uint64_t i=0;i<20*period+std::uint64_t(sr*.05);++i){
                if(i&&i%period==0){parity^=bool((mask>>(k++%16))&1u);}
                if(i==20*period){a.off();b.off();}
                check(a.position==b.position);if(b.active)check(b.swapped==parity);
                auto x=a.tick(),y=b.tick();check(x.l+x.r==y.l+y.r);check(parity?(x.l==y.r&&x.r==y.l):(x.l==y.l&&x.r==y.r));
                if(i%period==0)check(x.l==x.r&&y.l==y.r);
                check(std::isfinite(x.l)&&std::abs(x.l)<=.05&&std::abs(x.r)<=.05);maxDiff=std::max(maxDiff,std::abs(x.l-y.l));++frames;
            }check(!a.active&&!b.active&&a.tick().l==0&&b.tick().r==0);
        }
    }
    CycleVoice v;check(!v.start(NAN,69,0,1,{}));CyclePatch p;p.spread=NAN;p.width=INFINITY;p.period=NAN;check(v.start(48000,127,NAN,1,p));for(int i=0;i<1000;++i){auto x=v.tick();check(std::isfinite(x.l)&&x.l==x.r);}
    check(maxDiff>.01);std::cout<<"paired frames="<<frames<<" max stereo delta="<<maxDiff<<" exact mono equality\n";
    if(argc>1){std::string d=argv[1];demo(d+"/cross.wav",0,false);demo(d+"/swap.wav",0xffff,false);demo(d+"/pattern.wav",0xaaaa,false);demo(d+"/cross-mono.wav",0,true);demo(d+"/swap-mono.wav",0xffff,true);}
}
