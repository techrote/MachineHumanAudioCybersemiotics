#include "clock_state_bridge.hpp"
#include <cstdlib>
#include <iostream>
using namespace mhac::clock_fold;
static void check(bool ok,const char* why){if(!ok){std::cerr<<why<<'\n';std::abort();}}
int main(){
    auto live=std::make_unique<Live>();auto reference=std::make_unique<Live>();
    std::size_t compared=0;
    const Normalized warp{1,0,.1,.7,.12,0,1}, dry{0,1,0,.4,.12,1,0};
    for(double rate:{1000.,44100.,48000.,96000.,192000.,2000000.}){
        for(std::size_t offset:{std::size_t(0),std::size_t(1),frameSize/2,frameSize-1}){
            check(live->prepare(rate)&&reference->prepare(rate),"prepare");
            check(live->restore(defaults)&&reference->restore(defaults),"initial state");
            StateBridge bridge;
            for(std::size_t i=0;i<5*frameSize;++i){
                if(i==frameSize+offset||i==2*frameSize+offset||i==3*frameSize+offset){
                    const auto& p=i<2*frameSize?warp:i<3*frameSize?dry:defaults;
                    check(bridge.request(p)&&bridge.begin(*live,true),"active request");
                    check(!bridge.begin(*live,true),"duplicate request");
                    for(unsigned k=0;k<Count;++k)check(reference->set(k,p[k]),"reference automation");
                }
                const auto x=.31*std::sin(.037*double(i)),r=.27*std::cos(.061*double(i));
                const auto y=live->step(x,r);
                check(y==reference->step(x,r),"active patch differs from uninterrupted automation");
                check(std::abs(y[0])<=1&&std::abs(y[1])<=1,"output bound");
                ++compared;
                if(i%127==0)bridge.end(*live);
            }
            bridge.end(*live);Normalized p{};check(bridge.save(p)&&p==defaults,"final snapshot");
        }
    }
    check(live->prepare(48000)&&live->restore(defaults),"impulse prepare");
    StateBridge bridge;
    for(std::size_t i=0;i<2*frameSize;++i){
        if(i==frameSize/2){check(bridge.request(defaults)&&bridge.begin(*live,true),"identical active restore");}
        const auto y=live->step(i==0?.5:0,i==0?-.25:0);
        check(y==(i==frameSize?Stereo{.5,-.25}:Stereo{}),"restore lost or displaced delayed impulse");
    }
    // Constant identity input: hard restore loses one packet; active restore does not.
    check(live->restore(defaults)&&reference->restore(defaults),"DC prepare");
    for(std::size_t i=0;i<2*frameSize;++i){live->step(.25,-.25);reference->step(.25,-.25);}
    check(bridge.request(defaults)&&bridge.begin(*live,true)&&reference->restore(defaults),"DC restore");
    std::size_t hardZeros=0,softZeros=0;
    for(std::size_t i=0;i<2*frameSize;++i){
        if(reference->step(.25,-.25)==Stereo{})++hardZeros;
        const auto y=live->step(.25,-.25);if(y==Stereo{})++softZeros;
        check(y==Stereo{.25,-.25},"active restore DC dropout");
    }
    check(hardZeros==frameSize&&softZeros==0,"dropout comparison");
    auto invalid=defaults;invalid[Wet]=std::numeric_limits<double>::quiet_NaN();
    check(!live->applyPatch(invalid)&&live->params()==defaults,"invalid patch changed state");
    check(live->restore(defaults)&&live->step(0,0)==Stereo{},"explicit hard reset still clears");
    std::cout<<"six rates, four offsets, "<<compared<<" exact stereo frames; impulse retained; hard dropout "<<hardZeros<<", active dropout "<<softZeros<<"\n";
}
