#include "escape_policy.hpp"
#include "harmonic_bank.hpp"
#include <cstdlib>
#include <iostream>
#include <fstream>
using namespace mhac::counterfactual;
static void check(bool ok){if(!ok){std::cerr<<"stereo escape failure\n";std::exit(1);}}
static bool same(IntegerState a,IntegerState b){return a.x==b.x&&a.y==b.y;}
static void u16(std::ostream& s,unsigned v){s.put(char(v&255));s.put(char((v>>8)&255));}
static void u32(std::ostream& s,unsigned v){u16(s,v);u16(s,v>>16);}
static void demo(const char* path,bool optimal,unsigned gate){
    HarmonicBank b;auto c=b.config();c.wet=1000;
    for(auto& band:c.bands){band.excite=false;band.gain=0;}
    c.bands[0]={110,1000,1000,true,false,0,false};
    check(b.set(c)&&b.prepare(48000));
    std::ofstream f(path,std::ios::binary);check(bool(f));
    constexpr unsigned frames=48000;
    f.write("RIFF",4);u32(f,36+frames*4);f.write("WAVEfmt ",8);u32(f,16);u16(f,1);u16(f,2);u32(f,48000);u32(f,192000);u16(f,4);u16(f,16);f.write("data",4);u32(f,frames*4);
    for(unsigned i=0;i<frames;++i){
        if(i==12000){c.bands[0].excite=false;check(b.set(c));check(b.discardPendingInput(0));}
        if(i==gate){check(magnitude(b.lattice(0,0))||magnitude(b.lattice(0,1)));if(optimal)check(b.beginOptimalEscape(0));else{c.bands[0].erase=true;check(b.set(c));}}
        const double x=i<12000?0.8*std::sin(6.283185307179586*110*i/48000):0;
        const auto s=b.process(x,x*0.63);check(std::isfinite(s.left)&&std::isfinite(s.right)&&std::abs(s.left)<=1&&std::abs(s.right)<=1);
        if(i>=30000)check(s.left==0&&s.right==0);
        u16(f,unsigned(int(std::lround(s.left*32767)))&65535);u16(f,unsigned(int(std::lround(s.right*32767)))&65535);
    }
    check(bool(f));
}
int main(int argc,char** argv){
    EscapePolicy p;unsigned pairs=0,maxTicks=0,maxDebt=0;
    for(int x=-16;x<=16;++x)for(int y=-16;y<=16;++y)for(int a=-16;a<=16;++a)for(int b=-16;b<=16;++b){
        IntegerState l{x,y},r{a,b};const int m=std::max(magnitude(l),magnitude(r));
        const auto d=p.lookup({m,0});unsigned ticks=0,debt=0;
        while(magnitude(l)||magnitude(r)){
            const int old=std::max(magnitude(l),magnitude(r));const bool t=optimalStereoTruncate(l,r);
            check(t==p.lookup({old,0}).truncate&&ticks<16);l=step(l,0,t);r=step(r,0,t);++ticks;debt+=t;
            check(std::max(magnitude(l),magnitude(r))==quant(8*old,t));
        }
        check(ticks==d.ticks&&debt==d.interventions);maxTicks=std::max(maxTicks,ticks);maxDebt=std::max(maxDebt,debt);++pairs;
    }
    Processor a,b;Controls c;c.hz=1000;c.peakMix=1000;c.wet=1000;check(a.set(c)&&b.set(c)&&a.prepare(48000)&&b.prepare(48000));
    for(unsigned i=0;i<120;++i){a.process(1,-0.6);b.process(1,-0.6);}
    const auto l=a.lattice(0),r=a.lattice(1);check(magnitude(l)||magnitude(r));
    const auto d=p.lookup({std::max(magnitude(l),magnitude(r)),0});const auto t0=a.ticks(),n0=a.interventions();
    a.process(1,1);check(a.beginOptimalEscape());b.process(0,0);check(b.beginOptimalEscape());
    for(unsigned i=0;i<1000;++i){const auto sa=a.process(0,0),sb=b.process(0,0);check(sa.left==sb.left&&sa.right==sb.right);if(!a.optimalEscapeActive())break;}
    check(!a.optimalEscapeActive()&&a.ticks()-t0==d.ticks&&a.interventions()-n0==d.interventions);
    check(same(a.lattice(0),{})&&same(a.lattice(1),{}));
    a.requestIntervention();check(!a.beginOptimalEscape());a.reset();check(a.beginOptimalEscape());a.process(1,1);for(unsigned i=0;i<12;++i)a.process(1,1);check(!a.optimalEscapeActive());
    check(a.beginOptimalEscape());a.requestIntervention();check(!a.optimalEscapeActive());a.reset();check(a.beginOptimalEscape());c.erase=true;check(a.set(c)&&!a.optimalEscapeActive()&&!a.beginOptimalEscape());
    HarmonicBank bank;check(!bank.beginOptimalEscape(0)&&!bank.beginOptimalEscape(4));auto cfg=bank.config();cfg.bands[0].excite=false;check(bank.set(cfg)&&bank.beginOptimalEscape(0));cfg.bands[0].excite=true;check(bank.set(cfg)&&!bank.optimalEscapeActive(0));
    if(argc==5){demo(argv[1],false,24000);demo(argv[2],true,24000);demo(argv[3],false,12000);demo(argv[4],true,12000);}
    std::cout<<"PASS pairs="<<pairs<<" max_debt="<<maxDebt<<" max_ticks="<<maxTicks<<'\n';
}
