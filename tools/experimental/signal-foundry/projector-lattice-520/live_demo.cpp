#include "live.hpp"
#include <fstream>
#include <iostream>
using namespace mhac::lattice;
static void sample(std::ofstream& o,double x){auto u=static_cast<std::uint16_t>(static_cast<std::int16_t>(std::lround(x*32767)));o.put(static_cast<char>(u&255));o.put(static_cast<char>(u>>8));}
int main(){
    Live moving, fixed;moving.set(Mix,1);fixed.set(Mix,1);moving.reset(48000);fixed.reset(48000);
    std::ofstream dry("live-dry.pcm",std::ios::binary),base("live-fixed.pcm",std::ios::binary),wet("live-automated.pcm",std::ios::binary);
    double peak=0;constexpr double pi=3.14159265358979323846;
    for(unsigned n=0;n<192000+4096;++n){
        if(n==48000){moving.set(Axis1,0);moving.set(Delay1,1);moving.set(Axis2,1);}
        if(n==96000){moving.set(Inverse,1);moving.set(Delay3,0);}
        if(n==144000)moving.set(Bypass,1);
        double t=n/48000.,env=n<192000?std::min({1.,t*20.,(4.-t)*20.}):0.;
        Frame x{env*.035*(std::sin(2*pi*(110*t+35*t*t))+std::sin(2*pi*330*t)),env*.03*std::sin(2*pi*220*t)};
        auto a=fixed.process(x.l,x.r),b=moving.process(x.l,x.r);
        for(auto v:{x.l,x.r})sample(dry,v);for(auto v:a)sample(base,v);for(auto v:b){sample(wet,v);peak=std::max(peak,std::abs(v));}
    }
    std::cout<<"Automated peak FS "<<peak<<"\n";return dry&&base&&wet?0:1;
}
