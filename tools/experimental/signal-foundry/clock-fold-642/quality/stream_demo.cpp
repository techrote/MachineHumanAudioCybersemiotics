#include "../clock_live.hpp"
#include <cstdint>
#include <fstream>
#include <memory>
using namespace mhac::clock_fold;
static void le(std::ostream& f,unsigned n,int bytes){for(int i=0;i<bytes;++i)f.put(static_cast<char>((n>>(8*i))&255));}
int main(){
    constexpr unsigned sr=48000,n=sr*4+2*frameSize;
    constexpr double pi=3.14159265358979323846;
    for(unsigned mode=0;mode<2;++mode){
        auto live=std::make_unique<Live>();if(!live->prepare(sr)||!live->restore({1,0,0,1,.12,0,double(mode)}))return 1;
        std::ofstream f(mode?"stream-filtered.wav":"stream-linear.wav",std::ios::binary);if(!f)return 2;
        f.write("RIFF",4);le(f,36+n*4,4);f.write("WAVEfmt ",8);le(f,16,4);le(f,1,2);le(f,2,2);le(f,sr,4);le(f,sr*4,4);le(f,4,2);le(f,16,2);f.write("data",4);le(f,n*4,4);
        for(unsigned i=0;i<n;++i){const double t=double(i)/sr,env=i<4*sr?std::exp(-12*std::fmod(t,.25)):0;
            const auto y=live->step(env*(.12*std::sin(2*pi*220*t)+.12*std::sin(2*pi*16800*t)),env*(.12*std::sin(2*pi*330*t)+.12*std::sin(2*pi*14400*t)));
            for(double v:y)le(f,std::uint16_t(std::lround(v*32767)),2);
        }if(!f)return 3;
    }
}
