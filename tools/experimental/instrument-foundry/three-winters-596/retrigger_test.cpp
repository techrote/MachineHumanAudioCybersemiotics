#include "live.hpp"
#include <cstdlib>
#include <iostream>
#define CHECK(x) do { if(!(x)){std::cerr<<"FAIL "<<__LINE__<<" "<<#x<<'\n';std::exit(1);} } while(false)
int main(){
    using winters::live::Engine;
    unsigned cases=0;
    for(double rate:{1000.,1234.5678,8000.,44100.,48000.,96000.,192000.,384000.,1234567.8,2000000.}){
        for(double velocity:{.1,.5,1.}){
            Engine a,b;CHECK(a.prepare(rate)&&b.prepare(rate));
            // Negative ID represents channel/pitch fallback from the VST3 adapter.
            CHECK(a.on(-61,60,0,.5)&&b.on(-61,60,0,.5));
            for(int k=0;k<3;++k){CHECK(a.on(k,67+k,0,.25)&&b.on(k,67+k,0,.25));}
            for(unsigned i=0;i<unsigned(std::ceil(rate*.01));++i){CHECK(a.tick().l==b.tick().l);}
            a.off(-61);b.off(-61);
            for(unsigned i=0;i<unsigned(std::ceil(rate*.01));++i){CHECK(a.tick().l==b.tick().l);}
            CHECK(a.on(-61,60,0,velocity));CHECK(b.on(-61,60,0,.5));
            CHECK(!a.on(-61,60,0,1));CHECK(!a.on(9,70,0,1));
            // Same-velocity reference is a continuously phased attack; new velocity slews.
            auto f=a.tick(),g=b.tick();
            CHECK(std::abs(f.primary-g.primary)<=.05/std::max(1.,rate*.005)+1e-12);
            for(unsigned i=0;i<unsigned(std::ceil(rate*.006));++i){f=a.tick();CHECK(std::isfinite(f.l)&&std::abs(f.l)<=.300001);}
            a.off(-61);for(int k=0;k<3;++k)a.off(k);
            for(unsigned i=0;i<unsigned(std::ceil(rate*.041))+2;++i)a.tick();
            f=a.tick();CHECK(f.l==0&&f.r==0&&f.primary==0&&f.middle==0&&f.deep==0);
            CHECK(a.on(-61,60,0,velocity));++cases;
        }
    }
    // Native voice state is observable for precise continuity checks.
    winters::Engine e;CHECK(e.setup(48000));CHECK(e.noteOn(5,60,.2));
    for(int i=0;i<480;++i)e.sample();
    e.noteOff(5);
    for(int i=0;i<120;++i)e.sample();
    auto before=e.voices[0];CHECK(e.noteOn(5,62,1));auto after=e.voices[0];
    CHECK(!after.releasing&&after.active&&after.note==62&&after.env==before.env&&after.phase==before.phase&&after.inc==before.inc&&after.velocity==before.velocity);
    CHECK(after.target!=before.target);e.sample();CHECK(e.voices[0].velocity>before.velocity&&e.voices[0].velocity<=before.velocity+e.attack+1e-12);
    for(int i=0;i<240;++i)e.sample();
    CHECK(e.voices[0].velocity==1);
    std::cout<<"PASS "<<cases<<" saturated-polyphony retrigger cases across 10 rates; phase, envelope, tuning and velocity continuity\n";
}
