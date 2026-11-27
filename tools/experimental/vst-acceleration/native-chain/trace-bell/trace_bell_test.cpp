#include "trace_bell.hpp"
#include <cassert>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <limits>
#include <vector>
using namespace mhac::accel;
static bool equal(TraceFrame a,TraceFrame b) { return a.l==b.l && a.r==b.r; }
static bool bounded(TraceFrame a) { return std::isfinite(a.l)&&std::isfinite(a.r)&&std::abs(a.l)<=1&&std::abs(a.r)<=1; }
static std::vector<TraceFrame> render(float rate,unsigned block) {
    TraceBell b; assert(b.prepare(rate));
    TracePatch p; p.mix=.7f; assert(b.configure(p)); b.reset();
    const unsigned n=static_cast<unsigned>(rate*2);
    std::vector<TraceFrame> out(n);
    uint32_t rng=1234567;
    for(unsigned k=0;k<n;) {
        const unsigned end=std::min(n,k+block);
        for(;k<end;++k) {
            if(k==n/3) { p.pitch=330;p.decay=.8f;p.mix=.9f;assert(b.configure(p)); }
            if(k==n/2) { p.bypass=true;assert(b.configure(p)); }
            if(k==n*2/3) { p.bypass=false;assert(b.configure(p)); }
            rng=rng*1664525u+1013904223u;
            float x=(static_cast<float>(rng>>8)/8388608.f-1.f)*.8f;
            TraceFrame input={x,-x*.5f}; if(k>n*3/4) input={0,0};
            out[k]=b.process(input); assert(bounded(out[k]));
            if(p.bypass) assert(equal(out[k],input));
        }
    }
    return out;
}
int main() {
    uint64_t compared=0;
    for(float rate:{8000.f,22050.f,44100.f,48000.f,96000.f,192000.f}) {
        auto a=render(rate,1), b=render(rate,257), c=render(rate,1024);
        for(size_t i=0;i<a.size();++i) { assert(equal(a[i],b[i])&&equal(a[i],c[i])); compared+=2; }
        TraceBell t; assert(t.prepare(rate)); TracePatch p; p.mix=1;p.decay=.03f;p.spread=0;
        assert(t.configure(p)); t.reset(); float early=0,late=0;
        for(unsigned i=0;i<static_cast<unsigned>(rate);++i) {
            auto y=t.process({i==0?1.f:0.f,0}); assert(bounded(y)&&y.r==0);
            if(i<rate*.05f) early=std::max(early,std::abs(y.l));
            if(i>rate*.8f) late=std::max(late,std::abs(y.l));
        }
        assert(early>0 && late<early*1.e-6f);
        t.reset(); assert(equal(t.process({0,0}),{0,0}));
        TraceBell ref=t; p.mix=std::numeric_limits<float>::quiet_NaN(); assert(!t.configure(p));
        assert(!t.prepare(0)); assert(!t.prepare(1250001));
        for(int i=0;i<100;++i) assert(equal(t.process({.3f,-.3f}),ref.process({.3f,-.3f})));
        assert(bounded(t.process({std::numeric_limits<float>::infinity(),std::numeric_limits<float>::quiet_NaN()})));
        printf("rate %.0f: impulse peak %.9g late %.9g PASS\n",rate,early,late);
    }
    TraceBell t; TracePatch p; p.mix=1;p.contrast=0;p.decay=1.2f;p.pitch=500;
    assert(t.configure(p));t.reset();float peak=0;
    for(unsigned i=0;i<480000;++i) {
        float x=2.f*std::sin(6.2831853f*500.f*i/48000.f);
        auto y=t.process({x,-x});assert(bounded(y));peak=std::max(peak,std::abs(y.l));
    }
    printf("%llu exact stereo-frame comparisons; extreme peak %.9g; sizeof %zu bytes PASS\n",static_cast<unsigned long long>(compared),peak,sizeof(TraceBell));
}
