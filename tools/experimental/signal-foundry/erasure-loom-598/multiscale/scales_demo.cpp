#include "scales.hpp"
#include <fstream>
#include <memory>
#include <cstdint>
static void le(std::ofstream& f,std::uint32_t x,unsigned n){for(unsigned i=0;i<n;++i)f.put(char((x>>(8*i))&255));}
int main(){
    using namespace loom;constexpr unsigned sr=48000,n=6*sr+loomscale::tail;
    auto e=std::make_unique<loomscale::Engine>();if(!e->prepare(sr))return 1;
    const char* names[]={"scales-reference.wav","scales-fine.wav","scales-medium.wav","scales-coarse.wav","scales-switch.wav"};
    for(unsigned k=0;k<5;++k){ProbeParams p{};p.base.separation=1;p.base.budget=2;p.base.wet=1;p.base.bypass=k==0;p.edge=.5;p.probe=.25;
        e->set(p,k==4?0:k==0?0:k-1);e->reset();std::ofstream f(names[k],std::ios::binary);if(!f)return 2;
        f.write("RIFF",4);le(f,36+4*n,4);f.write("WAVEfmt ",8);le(f,16,4);le(f,1,2);le(f,2,2);le(f,sr,4);le(f,4*sr,4);le(f,4,2);le(f,16,2);f.write("data",4);le(f,4*n,4);
        for(unsigned i=0;i<n;++i){const double t=double(i)/sr;double x=0,r=0;if(i<6*sr){const double env=std::exp(-5*std::fmod(t,.375));x=.12*env*std::sin(2*pi*(130*t+17*t*t))+.05*std::sin(2*pi*311*t);r=.12*env*std::sin(2*pi*(164*t+13*t*t))+.05*std::sin(2*pi*397*t);}
            if(k==4&&i%24000==0)e->set(p,(i/24000)%3);
            const auto y=e->step(x,r);for(double v:y)le(f,std::uint16_t(std::lround(v*32767)),2);
        }if(!f)return 3;
    }
}
