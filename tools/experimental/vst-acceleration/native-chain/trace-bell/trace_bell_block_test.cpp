#include "trace_bell_block.hpp"
#include <cassert>
#include <cstdio>
#include <vector>
using namespace mhac::accel;
static void same(TraceFrame a,TraceFrame b){assert(a.l==b.l&&a.r==b.r);}
int main(){
    unsigned long long compared=0;unsigned rejected=0;
    for(float rate:{8000.f,22050.f,44100.f,48000.f,96000.f,192000.f}){
        const uint32_t n=uint32_t(rate);
        const std::vector<TraceEvent> events{{0,3,.8},{0,0,.1},{0,0,.2},{1,2,.1},
            {n/8,0,1},{n/8,1,1},{n/8,4,1},{n/8+1,0,0},{n/3,5,1},
            {n/2,5,0},{n-1,3,0}};
        std::vector<float> l(n),r(n),ol(n),orr(n),refL(n),refR(n);
        for(uint32_t i=0;i<n;++i){l[i]=.2f*std::sin(6.2831853f*220.f*i/rate);r[i]=.1f*std::cos(6.2831853f*330.f*i/rate);}
        TraceBellPerformance ref;assert(ref.prepare(rate));size_t e=0;
        for(uint32_t i=0;i<n;++i){
            if(e<events.size()&&events[e].offset==i){
                TracePatch p=ref.patch();
                do{auto v=events[e++];assert(applyTraceNormalized(p,v.id,v.normalized));}
                while(e<events.size()&&events[e].offset==i);
                assert(ref.configure(p));
            }
            const auto y=ref.process({l[i],r[i]});refL[i]=y.l;refR[i]=y.r;
        }
        for(uint32_t block:{1u,31u,257u,1024u,65536u}){
            TraceBellPerformance t;assert(t.prepare(rate));size_t cursor=0;
            for(uint32_t i=0;i<n;){
                const uint32_t len=std::min(block,n-i);std::vector<TraceEvent> local;
                while(cursor<events.size()&&events[cursor].offset<i+len){auto v=events[cursor++];v.offset-=i;local.push_back(v);}
                assert(processTraceBlock(t,l.data()+i,r.data()+i,ol.data()+i,orr.data()+i,len,local.data(),local.size()));i+=len;
            }
            for(uint32_t i=0;i<n;++i){same({ol[i],orr[i]},{refL[i],refR[i]});++compared;}
            TraceState a{},b{};assert(t.save(a)&&ref.save(b)&&a==b);
        }
        TraceBellPerformance t;assert(t.prepare(rate));auto il=l,ir=r;
        assert(processTraceBlock(t,il.data(),ir.data(),il.data(),ir.data(),n,events.data(),events.size()));
        assert(il==refL&&ir==refR);compared+=n;
        const TraceEvent flush[]{ {0,0,.5},{0,5,1} };assert(processTraceBlock(t,nullptr,nullptr,nullptr,nullptr,0,flush,2));
        assert(t.patch().pitch==290.f&&t.patch().bypass);
        const auto before=t;TraceState state{},after{};assert(t.save(state));
        const TraceEvent bad[][2]={{{0,0,.5},{1,6,0}},{{1,0,.5},{0,1,.5}},{{0,0,.5},{2,1,.5}},
            {{0,0,.5},{1,1,-.1}},{{0,0,.5},{1,1,std::numeric_limits<double>::quiet_NaN()}}};
        float x[2]={.1f,.2f},y[2]={.3f,.4f},a[2]={9,9},b[2]={9,9};
        for(auto& v:bad){assert(!processTraceBlock(t,x,y,a,b,2,v,2));++rejected;}
        assert(!processTraceBlock(t,x,y,a,b,2,nullptr,1));++rejected;
        assert(!processTraceBlock(t,nullptr,y,a,b,2,nullptr,0));++rejected;
        assert(!processTraceBlock(t,x,y,a,b,2,bad[0],13));++rejected;
        assert(!processTraceBlock(t,nullptr,nullptr,nullptr,nullptr,0,bad[0],2));++rejected;
        assert(a[0]==9&&a[1]==9&&b[0]==9&&b[1]==9&&t.save(after)&&state==after);
        auto witness=before;for(unsigned i=0;i<100;++i)same(t.process({.2f,.1f}),witness.process({.2f,.1f}));
    }
    printf("%llu exact stereo frames; %u transactional rejects; zero-frame flush and in-place PASS\n",compared,rejected);
}
