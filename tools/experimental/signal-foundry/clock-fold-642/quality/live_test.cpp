#include "../clock_live.hpp"
#include <cstdlib>
#include <iostream>
#include <memory>
using namespace mhac::clock_fold;
static void check(bool b,const char* why){if(!b){std::cerr<<why<<'\n';std::exit(1);}}
int main(){
    auto live=std::make_unique<Live>();auto legacy=std::make_unique<Engine>();
    auto bank=std::make_unique<quality::KernelBank>();bank->prepare();
    auto frame=std::make_unique<std::array<Stereo,frameSize>>();
    Normalized p{1,0,0,1,0,0,1},q=defaults;
    auto bytes=encode(p);check(bytes.size()==60&&decode(bytes.data(),bytes.size(),q)&&p==q,"CF02");
    bytes[3]='1';check(decode(bytes.data(),52,q)&&q[Quality]==0&&q[Drift]==1,"CF01 migration");
    check(!decode(bytes.data(),60,q)&&q[Quality]==0,"wrong length");
    for(double rate:{1000.,44100.,48000.,96000.,192000.,2000000.}){
        check(live->prepare(rate)&&legacy->prepare(rate),"prepare");
        check(live->restore(p),"restore");const auto c=controls(p);const auto plan=Plan::make(c);
        for(std::size_t i=0;i<frameSize;++i){const double x=.5*std::sin(2*3.14159265358979323846*.35*i);(*frame)[i]={x,0};}
        for(std::size_t i=0;i<4*frameSize;++i){const auto pos=i%frameSize;
            // First packet filtered, second linear, third filtered again. A
            // mid-capture toggle cannot change that packet's selected mode.
            if(i==frameSize/2||i==2*frameSize)check(live->set(Quality,i==frameSize/2?0:1),"set");
            const auto x=(*frame)[pos];const auto y=live->step(x[0],x[1]);const auto z=legacy->tick(x,c);
            if(i<frameSize||i/frameSize==2)check(y==z,"linear/initial equivalence");
            else check(y==bank->render(*frame,plan,pos,true),"latched filtered playback");
        }
        check(live->restore(q),"legacy restore");legacy->reset();
        for(std::size_t i=0;i<2*frameSize;++i){const auto x=(*frame)[i%frameSize];check(live->step(x[0],x[1])==legacy->tick(x,c),"migrated exact linear");}
        check(live->restore(p),"filtered bypass restore");
        check(live->set(Bypass,1),"bypass");
        for(std::size_t i=0;i<3*frameSize;++i){
            const auto x=(*frame)[i%frameSize];const auto y=live->step(x[0],x[1]);
            // At 2 MHz the 5 ms slew spans more than one packet.
            if(i<frameSize||i>=std::max(frameSize,std::size_t(std::ceil(.005*rate))+1))
                check(y==(i<frameSize?Stereo{}:x),"latency-aligned bypass");
            else check(std::isfinite(y[0])&&std::abs(y[0])<=1&&y[1]==0,"bypass slew bounds");
        }
        check(live->restore(p),"nonfinite restore");
        for(std::size_t i=0;i<2*frameSize;++i)check(live->step(std::numeric_limits<double>::infinity(),1e-100)==Stereo{},"nonfinite/denormal");
        check(live->restore(defaults),"identity restore");check(live->set(Quality,1),"quality");
        for(std::size_t i=0;i<3*frameSize;++i)check(live->step(i==0?.25:0,0)==Stereo{i==frameSize?.25:0,0},"identity latency/reset");
    }
    std::cout<<"six rates, 688128 streaming frames; CF01/CF02 migration, packet latch, bypass and identity latency passed\n";
}
