#include "shuttle_stagger_test.hpp"
#include <fstream>
#include <string>
using namespace mhac::accel;
static void put(std::ostream& out,unsigned x,unsigned bytes){for(unsigned i=0;i<bytes;++i)out.put(char((x>>(8*i))&255));}
int main(int argc,char** argv){
    if(argc==1){qualifyShuttleStagger();return 0;}
    if(argc!=2)return 2;
    constexpr unsigned rate=48000,frames=rate*4;
    const double notes[]={110,196,164.8138,261.6256,146.8324,220};
    for(unsigned amount:{0u,500u,1000u}){
        auto e=std::make_unique<DesktopShuttle>();if(!e->prepareRate(rate)||!e->configure({850,1000,400,0,false})||!e->configureStagger(amount))return 3;e->reset();
        std::ofstream out(std::string(argv[1])+"/stagger-"+std::to_string(amount)+".wav",std::ios::binary);if(!out)return 4;
        out.write("RIFF",4);put(out,36+frames*4,4);out.write("WAVEfmt ",8);put(out,16,4);put(out,1,2);put(out,2,2);put(out,rate,4);put(out,rate*4,4);put(out,4,2);put(out,16,2);out.write("data",4);put(out,frames*4,4);
        for(unsigned n=0;n<frames;++n){const unsigned j=n/24000;const double t=double(n%24000)/rate;float x=0.;if(j<6){const double p=6.283185307179586*notes[j]*t;const double env=std::min(1.,t/.008)*std::max(0.,1.-t/.32);x=float(.14*env*(std::sin(p)+.3*std::sin(2*p)+.15*std::sin(3*p)));}
            const auto y=e->process({x,x});for(float v:{y.l,y.r}){if(!std::isfinite(v)||std::abs(v)>.3f)return 5;put(out,uint16_t(int(std::lround(v*32767.f))),2);}}
        if(!out)return 6;
    }
}
