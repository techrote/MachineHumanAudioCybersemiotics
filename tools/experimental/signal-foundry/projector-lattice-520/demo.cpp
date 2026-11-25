#include "lattice.hpp"
#include <fstream>
#include <cstdint>
#include <iostream>
using namespace mhac::lattice;
static void sample(std::ofstream& o,double x){auto s=static_cast<std::int16_t>(std::lround(x*32767));auto u=static_cast<std::uint16_t>(s);o.put(static_cast<char>(u&255));o.put(static_cast<char>(u>>8));}
int main(){
    Program p{{{Axis::Sum,32},{Axis::Left,127},{Axis::Difference,256},{Axis::Right,511}}};
    Lattice f,g; if(!f.configure(p)||!g.configure(p,true))return 1;
    std::ofstream dry("dry.pcm",std::ios::binary),split("split.pcm",std::ios::binary),returned("returned.pcm",std::ios::binary);
    constexpr unsigned N=144000; constexpr double pi=3.14159265358979323846;
    for(unsigned n=0;n<N+2*f.tail();++n){
        double t=n/48000.,env=n<N?std::min({1.,t*20.,(3.-t)*20.}):0.;
        Frame x{env*.06*(std::sin(2*pi*(110*t+350*t*t))+std::sin(2*pi*330*t)),env*.035*std::sin(2*pi*220*t)};
        auto y=f.step(x),z=g.step(y);
        for(auto v:{x.l,x.r})sample(dry,v);for(auto v:{y.l,y.r})sample(split,v);for(auto v:{z.l,z.r})sample(returned,v);
    }
    return dry&&split&&returned?0:1;
}
