#include "trace_bell_state.hpp"
#include <cassert>
#include <cstdio>
#include <limits>
using namespace mhac::accel;
int main(){
    unsigned long long frames=0,poles=0;
    for(float rate:{1000.f,1234.568f,8000.f,44100.f,192000.f,384000.f,1234567.8f,1250000.f}){
        TraceBellPerformance a,b;assert(a.prepare(rate)&&b.prepare(rate));
        for(float pitch:{80.f,220.f,500.f})for(float spread:{0.f,1.f})for(float decay:{.03f,1.2f}){
            TracePatch p{pitch,decay,.8f,.7f,spread,false};
            const float effective=traceEffectivePitch(rate,pitch,spread);
            assert(effective>0&&effective<=pitch);
            if(rate>=8000)assert(effective==pitch);
            for(float ratio:{1.f,1.5f,2.125f,3.25f})for(float side:{-1.f,1.f}){
                const float frequency=effective*ratio*(1.f+side*.012f*spread);
                assert(frequency<=.450001f*rate);
                const float angle=6.283185307179586f*frequency/rate;
                const float radius=std::exp(-1.f/(decay*rate));
                assert(std::hypot(double(radius*std::cos(angle)),double(radius*std::sin(angle)))<1.);
                ++poles;
            }
            assert(a.configure(p)&&b.configure(p));
            const unsigned n=unsigned(std::ceil(rate*.01f))+1024;
            for(unsigned i=0;i<n;++i){
                const TraceFrame x{i%17==0?.8f:0.f,i%31==0?-.4f:0.f};
                const auto y=a.process(x),z=b.process(x);
                assert(y.l==z.l&&y.r==z.r&&std::isfinite(y.l)&&std::isfinite(y.r)&&std::abs(y.l)<=1&&std::abs(y.r)<=1);
                ++frames;
            }
        }
        auto ref=a;
        for(float invalid:{0.f,999.f,1250001.f,std::numeric_limits<float>::infinity(),std::numeric_limits<float>::quiet_NaN()})assert(!a.prepare(invalid));
        for(unsigned i=0;i<1024;++i){auto y=a.process({0,0}),z=ref.process({0,0});assert(y.l==z.l&&y.r==z.r);++frames;}
    }
    std::printf("%llu bounded deterministic frames; %llu stable modal poles; invalid prepare transactional PASS\n",frames,poles);
}
