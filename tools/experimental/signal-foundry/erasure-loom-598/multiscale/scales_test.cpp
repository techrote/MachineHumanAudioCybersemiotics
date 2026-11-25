#include "scales.hpp"
#include <cstdlib>
#include <iostream>
#include <memory>
#include <limits>
static void check(bool b,const char* s){if(!b){std::cerr<<s<<'\n';std::exit(1);}}
int main(){
    using namespace loom;
    auto e=std::make_unique<loomscale::Engine>();
    unsigned long long paired=0,checked=0;
    for(double rate:{8000.,44100.,48000.,96000.,192000.}){
        check(e->prepare(rate),"prepare");ProbeParams p{};p.base.separation=1;p.base.budget=16;p.base.wet=1;p.probe=.4;p.edge=.6;
        ProbeEngine old;old.set(p);check(old.prepare(rate),"old prepare");e->set(p,0);e->reset();
        std::array<Stereo,loomscale::latency-frames> delay{};
        for(unsigned i=0;i<loomscale::latency*4;++i){double x=.3*std::sin(i*.091),r=.2*std::cos(i*.017);auto o=old.step(x,r);auto& d=delay[i%delay.size()];check(e->step(x,r)==d,"fine exact after alignment");d=o;++paired;}
        for(unsigned k=0;k<3;++k){const unsigned s=std::array<unsigned,3>{16,128,1024}[k];
            p.probe=p.edge=p.base.repair=0;e->set(p,k);e->reset();
            for(unsigned i=0;i<loomscale::latency*3;++i){auto y=e->step(.25,0);const double expect=i<loomscale::latency||i%(9*s)<2*s?0:.25;check(y[0]==expect&&y[1]==0,"scale dropout geometry");++checked;}
            p.base.bypass=true;e->set(p,k);e->reset();for(unsigned i=0;i<loomscale::tail+2;++i){auto y=e->step(i==0?.25:0,0);check(y[0]==(i==loomscale::latency?.25:0)&&y[1]==0,"fixed bypass latency");++checked;}p.base.bypass=false;
        }
        // All paths transparent on a constant with exact repair; changing scale must not modulate it.
        p.base.repair=1;p.edge=.7;p.probe=.5;e->set(p,0);e->reset();
        for(unsigned i=0;i<loomscale::latency*4;++i){if(i%71==0)e->set(p,(i/71)%3);auto y=e->step(.02,0);check(y[1]==0&&std::abs(y[0]-(i<loomscale::latency?0:.02))<1e-13,"convex scale retarget");++checked;}
        // Extreme and nonfinite input plus repeated switching, then finite tail.
        for(unsigned i=0;i<loomscale::latency*2;++i){if(i%19==0)e->set(p,(i/19)%3);auto y=e->step(i%17==0?std::numeric_limits<double>::infinity():4*std::sin(i*.2),0);check(std::isfinite(y[0])&&std::abs(y[0])<=1&&y[1]==0,"safe output");++checked;}
        for(unsigned i=0;i<loomscale::tail;++i)e->step(0,0);
        check(e->step(0,0)==Stereo{},"finite tail");
    }
    std::cout<<"exact aligned pairs="<<paired<<" additional frames="<<checked<<'\n';
}
