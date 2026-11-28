#include "afterimage.hpp"
#include <cstdio>
#include <cstdlib>
using namespace mhac::afterimage;
static void check(bool ok){if(!ok){std::fputs("additive oracle failed\n",stderr);std::exit(1);}}
int main(){
    constexpr double tau=6.2831853071795864769;
    double worst=0;unsigned long long samples=0;
    for(double sr:{1000.,44100.,48000.,96000.,2000000.})
        for(double f:{8.1758,110.,440.,13000.})for(unsigned h=0;h<8;++h){
            const std::array<double,4> ratios{1,2.+h*.25,3.+h*.5,5.+h*.75};
            const std::array<double,4> raw{1,.5,.3,.2};
            std::array<double,4> step{},weight{},phase{};double sum=0;
            for(unsigned i=0;i<4;++i){step[i]=f*ratios[i]/sr;weight[i]=raw[i]*std::clamp((.45-step[i])/.05,0.,1.);sum+=weight[i];}
            for(auto& g:weight)g/=std::max(1.,sum);
            AdditiveMemory a,b;a.configure(step,weight);
            const unsigned frames=sr==48000&&f==110&&h==7?1000000u:8192u;
            for(unsigned n=0;n<frames;++n){
                if(n==513)b=a;
                double expected=0;
                for(unsigned i=0;i<4;++i)if(weight[i]>0){expected+=weight[i]*std::sin(tau*phase[i]);phase[i]+=step[i];if(phase[i]>=1)phase[i]-=1;}
                const double actual=a.tick(),error=std::abs(actual-expected);
                worst=std::max(worst,error);++samples;
                check(std::isfinite(actual)&&std::abs(actual)<=1.000000000001&&error<2e-11);
                if(n>=513&&n<1024)check(b.tick()==actual);
            }
            a.configure(step,weight);check(a.tick()==0);
        }
    std::printf("PASS %llu samples; maximum absolute error %.12g\n",samples,worst);
}
