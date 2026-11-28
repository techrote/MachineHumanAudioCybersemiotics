#include "resampler.hpp"
#include <iostream>
#include <memory>
#include <cstdlib>
#include <chrono>
using namespace mhac::clock_fold;
using namespace mhac::clock_fold::quality;
using Frame=std::array<Stereo,frameSize>;
static void require(bool ok){if(!ok){std::cerr<<"FAIL\n";std::exit(1);}}
int main(){
    auto bank=std::make_unique<KernelBank>(); bank->prepare();
    auto frame=std::make_unique<Frame>();
    constexpr double pi=3.14159265358979323846;
    Controls c;c.drift=.5;c.curvature=-.5; const auto plan=Plan::make(c);
    std::size_t s=0;for(std::size_t i=1;i<4;++i)if(plan.boundary[i+1]-plan.boundary[i]<plan.boundary[s+1]-plan.boundary[s])s=i;
    const double speed=.25/(plan.boundary[s+1]-plan.boundary[s]);
    const auto begin=std::size_t((plan.boundary[s]+.005)*(frameSize-1));
    const auto end=std::size_t((plan.boundary[s+1]-.005)*(frameSize-1));
    require(speed>2 && end>begin);
    for(auto& x:*frame)x={.25,-.125};
    for(std::size_t i=0;i<frameSize;++i){auto y=bank->render(*frame,plan,i);require(std::abs(y[0]-.25)<1e-12 && std::abs(y[1]+.125)<1e-12);}
    for(double hz:{.025,.35}){
        for(std::size_t i=0;i<frameSize;++i)(*frame)[i]={.5*std::sin(2*pi*hz*i),0};
        double linear=0,filtered=0;
        for(auto i=begin;i<end;++i){const double src=plan.source(double(i)/(frameSize-1))*(frameSize-1);const auto a=std::size_t(src);const double f=src-a;const double x=(1-f)*(*frame)[a][0]+f*(*frame)[a+1][0];const auto y=bank->render(*frame,plan,i);linear+=x*x;filtered+=y[0]*y[0];require(y[1]==0);}
        const double db=10*std::log10(filtered/linear);std::cout<<"speed="<<speed<<" tone="<<hz<<" filtered/linear dB="<<db<<'\n';
        require(hz<.1?std::abs(db)<1.0:db<-30);
    }
    for(auto& x:*frame)x={std::numeric_limits<double>::infinity(),-1e-100};
    for(std::size_t i=0;i<frameSize;++i)require(bank->render(*frame,plan,i)==Stereo{});
    for(std::size_t i=0;i<frameSize;++i)(*frame)[i]={double(i%7)/7,-.25};
    const auto identity=Plan::make({});for(std::size_t i=0;i<frameSize;++i)require(bank->render(*frame,identity,i)==(*frame)[i]);
    volatile double sum=0;const auto start=std::chrono::steady_clock::now();
    for(int repeat=0;repeat<128;++repeat)for(std::size_t i=0;i<frameSize;++i)sum+=bank->render(*frame,plan,i)[0];
    const auto elapsed=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
    std::cout<<"million-frame seconds="<<elapsed<<" checksum="<<sum<<'\n';
}
