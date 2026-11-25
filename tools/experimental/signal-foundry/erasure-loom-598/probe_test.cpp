#include "probe.hpp"
#include <cstdlib>
#include <iostream>
#include <limits>
#include <chrono>
using namespace loom;
void check(bool b,const char* s){if(!b){std::cerr<<s<<'\n';std::exit(1);}}
int main(){
    unsigned count=0;double error=0,excess=0;unsigned long long paired=0;
    for(unsigned d=1;d<=4;++d)for(unsigned r=0;r<nodes;++r){
        const auto p=makePlan(d,r);auto w=singleProbe(r);double norm=0;
        for(double a:w)norm+=std::abs(a);
        check(std::abs(norm-(1/std::sin(pi/18)-1))<1e-12,"single probe sharp norm");
        check(w[r]==0,"no erased target read");
        for(unsigned h=0;h<=3;++h)for(unsigned s=0;s<2;++s){
            auto f=[&](unsigned j){return s?std::sin(2*pi*h*j/nodes):std::cos(2*pi*h*j/nodes);};
            double v=0;for(unsigned j=0;j<nodes;++j)v+=w[j]*f(j);
            error=std::max(error,std::abs(v-f(r)));check(std::abs(v-f(r))<1e-12,"basis");
        }
        for(double b:{1.,2.,4.,8.,16.})for(double repair:{0.,.4,1.})for(double probe:{0.,.25,.5,.75,1.}){
            const auto rows=probeRows(p,b,repair,probe);
            for(const auto& row:rows){double l1=0;for(double a:row)l1+=std::abs(a);excess=std::max(excess,l1-b);check(l1<=b+1e-12,"mixed norm");++count;}
            check(rows[0][r]==0&&rows[1][r]==0,"first target excluded");
            if(probe==0)check(rows[0][p.missing[1]]==0&&rows[1][p.missing[1]]==0,"both excluded");
            if(probe==1){Row expected{};expected[p.missing[1]]=1;check(rows[1]==expected,"second restored");}
        }
    }
    for(double rate:{1000.,8000.,44100.,48000.,96000.,192000.,2000000.}){
        Engine old;ProbeEngine e;check(old.prepare(rate)&&e.prepare(rate),"prepare");ProbeParams p;
        for(unsigned i=0;i<frames*53;++i){
            if(i%31==0){p.base.separation=1+i%4;p.base.rotation=i%9;p.base.budget=1+i%16;p.base.wet=(i%17)/16.;p.base.repair=(i%13)/12.;p.base.gain=(i%11)/10.;p.base.bypass=i%7==0;old.set(p.base);e.set(p);}
            double x=i%41==0?std::numeric_limits<double>::infinity():.9*std::sin(i*.193);
            check(old.step(x,-x)==e.step(x,-x),"legacy exact endpoint");++paired;
        }
        p={};p.base.wet=1;p.base.budget=16;p.base.separation=1;p.probe=1;e.set(p);e.reset();
        auto f=[](unsigned i){return .08*std::sin(2*pi*(i/stride)/nodes)+.03*std::cos(6*pi*(i/stride)/nodes);};
        for(unsigned i=0;i<frames*5;++i){auto y=e.step(f(i),0);check(std::abs(y[0]-(i<frames?0:f(i-frames)))<1e-12&&y[1]==0,"single probe periodic render");}
        p.base.repair=0;e.set(p);e.reset();for(unsigned i=0;i<frames*2;++i){auto y=e.step(.25,0);check(y[0]==(i<frames||i<frames+stride?0:.25)&&y[1]==0,"restored observation unaffected by repair");}
        p.base.repair=1;p.base.bypass=true;e.set(p);e.reset();for(unsigned i=0;i<frames*3;++i){auto y=e.step(i==0?.5:0,0);check(y[0]==(i==frames?.5:0)&&y[1]==0,"bypass impulse");}
        p.base.bypass=false;e.set(p);e.reset();for(unsigned i=0;i<frames*8;++i){p.probe=(i%31)/30.;e.set(p);auto y=e.step(i%2?2.:std::numeric_limits<double>::quiet_NaN(),0);check(std::isfinite(y[0])&&std::abs(y[0])<=1&&y[1]==0,"bounded channels");}
        for(unsigned i=0;i<ProbeEngine::tail;++i)e.step(0,0);
        check(e.step(0,0)==Stereo{},"tail");
    }
    ProbeEngine e;check(e.prepare(48000),"benchmark prepare");ProbeParams p;p.probe=.5;e.set(p);auto start=std::chrono::steady_clock::now();double sink=0;
    for(unsigned i=0;i<480000;++i)sink+=e.step(.2,.1)[0];
    std::cout<<"row_budget_checks="<<count<<" max_basis_error="<<error<<" max_budget_excess="<<excess<<" legacy_paired_frames="<<paired<<" 10s_ms="<<std::chrono::duration<double,std::milli>(std::chrono::steady_clock::now()-start).count()<<" sink="<<sink<<'\n';
}
