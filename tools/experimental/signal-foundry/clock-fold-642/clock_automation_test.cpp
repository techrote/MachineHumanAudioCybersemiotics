#include "clock.hpp"
#include <chrono>
#include <cstdlib>
#include <iostream>
#include <memory>
using namespace mhac::clock_fold;
static unsigned checks=0;
static void require(bool ok){++checks;if(!ok){std::cerr<<"failure at check "<<checks<<'\n';std::exit(1);}}
int main(){
    auto owner=std::make_unique<Engine>(); auto& e=*owner;require(e.prepare(48000));
    Controls a,b;a.drift=.5;a.curvature=.25;a.edge=0;b.drift=-.5;b.curvature=-.25;b.edge=0;
    const auto pa=Plan::make(a),pb=Plan::make(b);
    for(std::size_t i=0;i<3*frameSize;++i){
        const auto pos=i%frameSize, frame=i/frameSize;
        const double t=double(pos)/double(frameSize-1);
        // Capture A at frame zero, then B; mid-frame requests do not alter the latched plan.
        const auto y=e.tick({t,-t},frame==0&&pos<frameSize/2?a:b);
        const double expected=frame==0?0:(frame==1?pa.source(t):pb.source(t));
        require(std::abs(y[0]-expected)<1e-14&&std::abs(y[1]+expected)<1e-14);
    }
    e.reset();
    for(std::size_t i=0;i<3*frameSize;++i){
        const auto pos=i%frameSize;const double t=double(pos)/double(frameSize-1);
        Controls c=a;c.bypass=i>=frameSize+1000;
        auto y=e.tick({t,-t},c);
        if(i>=frameSize+1241)require(y[0]==t&&y[1]==-t);
    }
    // Log sweep, deliberately no anti-alias guarantee. Check finite, bounded and distinct render.
    auto dryOwner=std::make_unique<Engine>(), wetOwner=std::make_unique<Engine>();
    auto& dry=*dryOwner; auto& wet=*wetOwner; require(dry.prepare(48000)&&wet.prepare(48000));
    double phase=0,diff=0;constexpr double pi=3.14159265358979323846;
    for(std::size_t i=0;i<4*frameSize;++i){
        double hz=30*std::pow(20000./30,double(i)/(4*frameSize-1));phase+=2*pi*hz/48000;
        double x=.8*std::sin(phase);auto u=dry.tick({x,0},Controls{}),v=wet.tick({x,0},a);
        require(std::isfinite(v[0])&&std::abs(v[0])<=1&&v[1]==0);diff+=std::abs(u[0]-v[0]);
    }
    require(diff>100);
    // Reset after both buffers contain history, including partial capture.
    for (std::size_t offset : {std::size_t(0),std::size_t(1),frameSize/2,frameSize-1}) {
        for (std::size_t i=0;i<2*frameSize+offset;++i) e.tick({.75,-.5},a);
        e.reset();
        for (std::size_t i=0;i<2*frameSize;++i) {
            const auto y=e.tick({i==0?.25:0,0},Controls{});
            require(y[0]==(i==frameSize?.25:0)&&y[1]==0);
        }
    }
    // Observational native benchmark, not a deadline assertion. No I/O inside measured blocks.
    e.reset();double checksum=0,maximum=0,total=0;
    using clock=std::chrono::steady_clock;
    for(int block=0;block<48000;++block){
        auto start=clock::now();
        for(int j=0;j<64;++j){const double x=double(j%7)*.1;checksum+=e.tick({x,-x},a)[0];}
        double us=std::chrono::duration<double,std::micro>(clock::now()-start).count();maximum=std::max(maximum,us);total+=us;
    }
    require(std::isfinite(checksum)&&checksum>0);
    std::cout<<checks<<" checks passed; sweep L1 difference "<<diff<<"; 64-sample block mean "<<total/48000<<" us, max "<<maximum<<" us\n";
}
