#include "resampler.hpp"
#include <chrono>
#include <cstdlib>
#include <iostream>
#include <memory>
using namespace mhac::clock_fold;
using namespace mhac::clock_fold::quality;
using Frame=std::array<Stereo,frameSize>;
static void check(bool b,const char* why){if(!b){std::cerr<<why<<'\n';std::exit(1);}}
int main(){
    auto bank=std::make_unique<KernelBank>();bank->prepare();
    auto frame=std::make_unique<Frame>();
    constexpr double pi=3.14159265358979323846;
    double abrupt=0, smooth=0;std::size_t count=0;
    for(int d=-5;d<=5;++d)for(int k=-5;k<=5;++k){
        Controls c;c.drift=d*.1;c.curvature=k*.1;const auto plan=Plan::make(c);
        for(auto& x:*frame)x={.25,-.125};
        for(std::size_t i=0;i<frameSize;++i){const auto y=bank->render(*frame,plan,i,true);check(std::abs(y[0]-.25)<1e-12&&std::abs(y[1]+.125)<1e-12,"DC");++count;}
        for(std::size_t i=0;i<frameSize;++i){const double t=double(i)/(frameSize-1);(*frame)[i]={.4*std::sin(2*pi*(.015*i+.22*i*t)),0};}
        for(std::size_t i=0;i<frameSize;++i){
            const auto y=bank->render(*frame,plan,i,true);check(std::isfinite(y[0])&&std::abs(y[0])<=1&&y[1]==0,"sweep bounds/isolation");
            const double t=double(i)/(frameSize-1);bool interior=true;
            for(int j=1;j<4;++j)if(std::abs(t-plan.boundary[j])*(frameSize-1)<=64)interior=false;
            if(interior)check(y==bank->render(*frame,plan,i),"interior equivalence");
        }
        // Compare the actual sample step across every internal join for many
        // high-frequency phases. This includes the source slope change; it is
        // not an isolated measurement of the filter's frequency response.
        for(int p=0;p<16;++p){
            for(std::size_t i=0;i<frameSize;++i)(*frame)[i]={.5*std::sin(2*pi*(.35*i+p/16.)),0};
            for(int j=1;j<4;++j){const auto i=std::size_t(plan.boundary[j]*(frameSize-1));
                const double a=bank->render(*frame,plan,i+1)[0]-bank->render(*frame,plan,i)[0];
                const double b=bank->render(*frame,plan,i+1,true)[0]-bank->render(*frame,plan,i,true)[0];
                abrupt+=a*a;smooth+=b*b;
            }
        }
    }
    check(smooth<abrupt,"aggregate join energy");
    std::cout<<"DC frames="<<count<<" joins="<<121*16*3<<" abrupt step energy="<<abrupt<<" smooth step energy="<<smooth<<" ratio dB="<<10*std::log10(smooth/abrupt)<<'\n';
    Controls c;c.drift=.5;c.curvature=-.5;const auto plan=Plan::make(c);
    volatile double sink=0;double worst=0,total=0;
    for(int block=0;block<16384;++block){const auto t=std::chrono::steady_clock::now();
        for(int i=0;i<64;++i)sink+=bank->render(*frame,plan,(block*64+i)%frameSize,true)[0];
        const double us=std::chrono::duration<double,std::micro>(std::chrono::steady_clock::now()-t).count();worst=std::max(worst,us);total+=us;
    }
    std::cout<<"64-frame mean us="<<total/16384<<" max us="<<worst<<" checksum="<<sink<<'\n';
}
