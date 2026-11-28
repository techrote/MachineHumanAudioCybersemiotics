#pragma once
#include <algorithm>
#include <array>
#include <cmath>
namespace guest {
// Two ordered carrier/modulator pairs; finite phase-modulation sidebands.
// Fixed seven-term spectrum per pair, signed frequencies preserved, no feedback.
class FmBank {
    struct Partial { double phase=0, inc=0, gain=0; };
    std::array<Partial,14> partials{};
    static double bessel(unsigned n,double x) noexcept {
        double term=1;
        for(unsigned i=1;i<=n;++i)term*=x/(2*i);
        double sum=term;
        for(unsigned k=1;k<12;++k){term*=(-x*x/4)/(k*(k+n));sum+=term;}
        return sum;
    }
public:
    void prepare(double sr,double root,const std::array<int,4>& motif,double depth) noexcept {
        partials={};
        if(!std::isfinite(sr)||sr<=0||!std::isfinite(root)||root<=0||!std::isfinite(depth))return;
        const double index=2*std::clamp(depth,0.,1.);
        for(unsigned pair=0;pair<2;++pair){
            const double c=root*std::exp2((std::clamp(motif[2*pair],-12,12)+12)/12.);
            const double m=root*std::exp2((std::clamp(motif[2*pair+1],-12,12)+12)/12.);
            double norm=0;
            for(int k=-3;k<=3;++k){
                auto& p=partials[7*pair+unsigned(k+3)];
                double a=bessel(unsigned(std::abs(k)),index);
                if(k<0&&(-k)%2)a=-a;
                norm+=std::abs(a);
                const double f=(c+k*m)/sr;
                if(!std::isfinite(f)||std::abs(f)>=.45)continue;
                p.inc=f;p.gain=a*std::clamp((.45-std::abs(f))/.05,0.,1.);
            }
            for(unsigned i=0;i<7;++i)partials[7*pair+i].gain*=.5/std::max(1.,norm);
        }
    }
    // Advance identical phase history even when the bank is inaudible.
    double tick(bool audible=true) noexcept {
        double y=0;
        for(auto& p:partials)if(p.gain!=0){
            p.phase+=p.inc;if(p.phase>=1)p.phase-=1;else if(p.phase<0)p.phase+=1;
            if(audible)y+=p.gain*std::sin(6.28318530717958647692*p.phase);
        }
        return y;
    }
};
}
