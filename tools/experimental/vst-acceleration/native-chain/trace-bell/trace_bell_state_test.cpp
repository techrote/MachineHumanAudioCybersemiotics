#include "trace_bell_state.hpp"
#include <cassert>
#include <cstdio>
#include <vector>
using namespace mhac::accel;
static bool eq(TraceFrame a,TraceFrame b){return a.l==b.l&&a.r==b.r;}
static bool bounded(TraceFrame a){return std::isfinite(a.l)&&std::isfinite(a.r)&&std::abs(a.l)<=1&&std::abs(a.r)<=1;}
static std::vector<TraceFrame> render(float rate,unsigned block){
    TraceBellPerformance t;assert(t.prepare(rate));const unsigned n=unsigned(rate),fade=unsigned(std::ceil(rate*.01f));
    std::vector<TraceFrame> out(n);uint32_t rng=123;
    for(unsigned k=0;k<n;){const unsigned end=std::min(n,k+block);for(;k<end;++k){
        if(k==n/8)assert(t.setNormalized(0,.85));
        if(k==n/4)assert(t.setNormalized(1,.9));
        if(k==n/3)assert(t.setNormalized(5,1));
        if(k==n/2)assert(t.setNormalized(5,0));
        if(k==n/2+fade/2)assert(t.setNormalized(5,1));
        if(k==n*3/4)assert(t.setNormalized(5,0));
        rng=rng*1664525u+1013904223u;float x=float(rng>>8)/8388608.f-1.f;TraceFrame in{x,-x*.5f};
        out[k]=t.process(in);assert(bounded(out[k]));
        if((k>=n/3+fade&&k<n/2)||(k>=n/2+fade/2+fade&&k<n*3/4))assert(eq(out[k],in));
    }}return out;
}
int main(){
    TraceBellPerformance t;TraceState s{},s2{};assert(t.save(s));
    const TraceState golden{{'T','B','0','1',1,0,0,0,0,0,92,67,51,51,179,62,205,204,76,63,154,153,153,62,0,0,0,63,0,0,0,0}};assert(s==golden);
    for(unsigned id=0;id<6;++id)for(unsigned i=0;i<=100;++i){assert(t.setNormalized(id,i/100.));assert(t.save(s));TraceBellPerformance copy;assert(copy.restore(s.data(),s.size()));assert(copy.save(s2)&&s==s2);}
    assert(t.save(s));unsigned rejected=0;
    for(size_t n=0;n<32;++n){assert(!t.restore(s.data(),n));++rejected;}
    for(unsigned i:{0u,1u,2u,3u,4u,5u,6u,7u,29u,30u,31u}){auto bad=s;bad[i]^=128;assert(!t.restore(bad.data(),bad.size()));++rejected;}
    auto bad=s;bad[28]=2;assert(!t.restore(bad.data(),bad.size()));++rejected;
    for(unsigned i=0;i<5;++i){bad=s;bad[8+4*i]=0;bad[9+4*i]=0;bad[10+4*i]=128;bad[11+4*i]=127;assert(!t.restore(bad.data(),bad.size()));++rejected;}
    assert(!t.restore(nullptr,32));++rejected;assert(!t.setNormalized(6,.5));++rejected;
    for(double v:{-1.,2.,std::numeric_limits<double>::infinity(),std::numeric_limits<double>::quiet_NaN()}){assert(!t.setNormalized(0,v));++rejected;}
    assert(t.save(s2)&&s==s2);
    uint64_t compared=0;
    for(float rate:{8000.f,22050.f,44100.f,48000.f,96000.f,192000.f}){
        auto a=render(rate,1),b=render(rate,257),c=render(rate,1024);for(size_t i=0;i<a.size();++i){assert(eq(a[i],b[i])&&eq(a[i],c[i]));compared+=2;}
        TraceBellPerformance p,q;assert(p.prepare(rate)&&q.prepare(rate));assert(p.setNormalized(3,.9));p.reset();assert(p.save(s));assert(q.restore(s.data(),s.size()));q.reset();
        for(int i=0;i<1000;++i)assert(eq(p.process({.2f,-.1f}),q.process({.2f,-.1f})));
        assert(p.setNormalized(5,1));unsigned fade=unsigned(std::ceil(rate*.01f));
        for(unsigned i=1;i<=fade;++i){auto wet=q.process({.2f,-.1f});auto got=p.process({.2f,-.1f});float w=float(i)/float(fade);assert(std::abs(got.l-(wet.l+w*(.2f-wet.l)))<.0001f);assert(std::abs(got.r-(wet.r+w*(-.1f-wet.r)))<.0001f);if(i==fade)assert(eq(got,{.2f,-.1f}));}
    }
    printf("606 state round trips; %u negative controls; %llu exact partition comparisons; six-rate fade oracle; sizeof %zu PASS\n",rejected,(unsigned long long)compared,sizeof(TraceBellPerformance));
}
