#include "loom.hpp"
#include <chrono>
#include <cstdlib>
#include <iostream>
#include <limits>
using namespace loom;
void check(bool ok,const char* msg){if(!ok){std::cerr<<msg<<'\n';std::exit(1);}}
int main(){
    double maxError=0, maxBudget=0, peak=0;unsigned cases=0;
    for(unsigned d=1;d<=4;++d)for(unsigned r=0;r<nodes;++r){auto p=makePlan(d,r);
        for(unsigned k=0;k<2;++k){
            check(std::abs(p.gain[k]-(1/std::tan(pi/18)/std::sin(pi*d/9)-1))<1e-12,"sharp gain formula");
            for(unsigned h=0;h<=3;++h)for(unsigned s=0;s<2;++s){double pred=0;
                auto f=[&](unsigned j){return s?std::sin(2*pi*h*j/nodes):std::cos(2*pi*h*j/nodes);};
                for(unsigned j=0;j<nodes;++j)pred+=p.exact[k][j]*f(j);
                maxError=std::max(maxError,std::abs(pred-f(p.missing[k])));++cases;
            }
            for(double b:{1.,2.,4.,8.,16.}){auto w=weights(p,k,b);double sum=0;for(double a:w)sum+=std::abs(a);
                maxBudget=std::max(maxBudget,sum-b);check(sum<=b+1e-12,"budget");check(w[p.missing[0]]==0&&w[p.missing[1]]==0,"no erased reads");}
        }
    }
    check(maxError<1e-12,"Fourier basis oracle");
    for(double sr:{1000.,8000.,44100.,48000.,96000.,192000.,2000000.}){
        Engine e;check(e.prepare(sr),"prepare");Params p;p.wet=1;p.budget=16;p.separation=1;e.set(p);e.reset();
        auto signal=[](unsigned t){return .02*std::cos(2*pi*(t/stride)/nodes)+.03*std::sin(6*pi*(t/stride)/nodes);};
        for(unsigned t=0;t<frames*5;++t){auto y=e.step(signal(t),-signal(t));double ref=t<frames?0:signal(t-frames);check(std::abs(y[0]-ref)<1e-12&&std::abs(y[1]+ref)<1e-12,"exact periodic render");}
        p.bypass=true;e.set(p);e.reset();for(unsigned t=0;t<frames*3;++t){auto y=e.step(t==0?.5:0,0);check(y[0]==(t==frames?.5:0)&&y[1]==0,"bypass impulse");}
        p.bypass=false;p.repair=0;e.set(p);e.reset();for(unsigned t=0;t<frames*2;++t){auto y=e.step(.25,0);if(t>=frames){unsigned j=(t-frames)/stride;check(y[0]==(j==0||j==1?0:.25)&&y[1]==0,"known erasure");}}
        Engine b;check(b.prepare(sr),"second prepare");p.repair=1;e.set(p);b.set(p);e.reset();b.reset();
        for(unsigned t=0;t<frames*30;++t){if(t%37==0){p.rotation=t%9;p.separation=1+t%4;p.budget=1+t%16;p.wet=(t%11)/10.;e.set(p);b.set(p);}double x=t%17==0?std::numeric_limits<double>::infinity():std::sin(t*.13)*2;
            auto y=e.step(x,0),z=b.step(x,0);check(y==z&&y[1]==0&&std::isfinite(y[0])&&std::abs(y[0])<=1,"determinism and channel safety");peak=std::max(peak,std::abs(y[0]));}
        // An unfinished capture can still contain past input, but after one full latency of silence no further output can be nonzero only if at a frame boundary.
        for(unsigned t=0;t<2*frames;++t)e.step(0,0);
        check(e.step(0,0)==Stereo{},"silence tail");
    }
    Engine e;check(!e.prepare(0)&&e.prepare(48000),"invalid rate");auto start=std::chrono::steady_clock::now();double sink=0;
    for(unsigned i=0;i<480000;++i)sink+=e.step(.2,.1)[0];
    std::cout<<"basis_cases="<<cases<<" max_error="<<maxError<<" budget_excess="<<maxBudget<<" peak="<<peak<<" 10s_ms="<<std::chrono::duration<double,std::milli>(std::chrono::steady_clock::now()-start).count()<<" sink="<<sink<<'\n';
}
