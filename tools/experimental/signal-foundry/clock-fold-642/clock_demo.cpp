#include "clock.hpp"
#include <cstdint>
#include <fstream>
#include <iostream>
#include <memory>
#include <string>
using namespace mhac::clock_fold;
static void le(std::ostream& f,unsigned n,int bytes){for(int i=0;i<bytes;++i)f.put(static_cast<char>((n>>(8*i))&255));}
int main(){
    constexpr unsigned sr=48000,n=sr*4+2*frameSize;
    constexpr double pi=3.14159265358979323846;
    for(int mode=0;mode<4;++mode){
        auto owner=std::make_unique<Engine>(); auto& e=*owner;e.prepare(sr);Controls c;c.drift=mode? .5:0;c.curvature=mode>=2?.35:0;c.compensation=mode==3?1:0;
        std::ofstream f("clock-"+std::to_string(mode)+".wav",std::ios::binary);if(!f)return 1;
        f.write("RIFF",4);le(f,36+n*4,4);f.write("WAVEfmt ",8);le(f,16,4);le(f,1,2);le(f,2,2);le(f,sr,4);le(f,sr*4,4);le(f,4,2);le(f,16,2);f.write("data",4);le(f,n*4,4);
        for(unsigned i=0;i<n;++i){double t=double(i)/sr,beat=std::fmod(t, .25),a=i<4*sr?std::exp(-beat*24):0;
            double l=a*(.16*std::sin(2*pi*110*t)+.08*std::sin(2*pi*660*t)),r=a*(.14*std::sin(2*pi*165*t)+.07*std::sin(2*pi*880*t));
            auto y=e.tick({l,r},c); for(double v:y)le(f,static_cast<std::uint16_t>(std::lround(v*32767)),2);
        }if(!f)return 2;
    }
}
