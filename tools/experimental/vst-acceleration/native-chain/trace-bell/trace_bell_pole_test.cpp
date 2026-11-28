#include "trace_bell_state.hpp"
#include <cassert>
#include <cstdio>
#include <complex>
using namespace mhac::accel;
using C=std::complex<double>;
static C pole(float rate,float pitch,float decay,float spread,unsigned c,unsigned i){
    constexpr float ratios[]={1,1.5f,2.125f,3.25f};
    const float r=std::exp(-1.f/(decay*rate));
    const float angle=6.283185307179586f*pitch*ratios[i]*(1.f+(c?1.f:-1.f)*.012f*spread)/rate;
    return {r*std::cos(angle),r*std::sin(angle)};
}
int main(){
    unsigned long long checks=0; double worst=0;
    for(float rate:{8000.f,22050.f,44100.f,48000.f,96000.f,192000.f}){
        const unsigned n=unsigned(std::ceil(rate*.01f));
        for(unsigned c=0;c<2;++c)for(unsigned i=0;i<4;++i){
            TracePoleRamp p; C start=pole(rate,80,.03f,0,c,i);
            p.set(float(start.real()),float(start.imag()),0);
            for(unsigned turn=0;turn<17;++turn){
                const C end=turn%2?pole(rate,80,.03f,0,c,i):pole(rate,500,1.2f,1,c,i);
                start={p.real,p.imag};p.set(float(end.real()),float(end.imag()),n);
                const unsigned limit=turn%3==0?n/3:n;
                for(unsigned k=1;k<=limit;++k){
                    p.advance();
                    const double t=double(k)/n;
                    const C expected=start*std::exp(t*std::log(end/start));
                    const C got={p.a,p.b};const double error=std::abs(got-expected);
                    worst=std::max(worst,error);assert(error<1.e-7&&std::abs(got)<1);
                    const auto left=p.remaining;p.set(float(end.real()),float(end.imag()),n);assert(left==p.remaining);
                    ++checks;
                }
                if(limit==n){assert(p.remaining==0&&C(p.a,p.b)==end);}
            }
            p.snap();assert(p.remaining==0&&p.a==p.targetA&&p.b==p.targetB);
        }
        TraceBell immediate; TraceBellPerformance smooth; assert(immediate.prepare(rate)&&smooth.prepare(rate));
        for(unsigned k=0;k<unsigned(rate/2);++k){
            const TraceFrame in{.08f*std::sin(6.2831853f*220.f*k/rate),.04f};
            const auto a=immediate.process(in),b=smooth.process(in);assert(a.l==b.l&&a.r==b.r);
        }
        TracePatch target;target.pitch=500;target.decay=1.2f;target.spread=1;
        assert(smooth.configure(target));auto reference=smooth;
        for(unsigned k=0;k<n;++k){
            assert(smooth.configure(target)); // identical writes must not restart ramp
            const auto a=smooth.process({.2f,-.1f}),b=reference.process({.2f,-.1f});
            assert(a.l==b.l&&a.r==b.r&&std::isfinite(a.l)&&std::abs(a.l)<=1);
        }
        smooth.reset();TraceBellPerformance fresh;assert(fresh.prepare(rate)&&fresh.configure(target));fresh.reset();
        for(unsigned k=0;k<1000;++k){const auto a=smooth.process({.1f,0}),b=fresh.process({.1f,0});assert(a.l==b.l&&a.r==b.r);}
    }
    printf("%llu analytic polar comparisons; max error %.9g; static identity, retarget, repeat and reset PASS; core %zu B wrapper %zu B\n",checks,worst,sizeof(TraceBell),sizeof(TraceBellPerformance));
}
