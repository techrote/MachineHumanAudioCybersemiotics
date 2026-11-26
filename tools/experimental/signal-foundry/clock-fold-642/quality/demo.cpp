#include "resampler.hpp"
#include <cstdint>
#include <fstream>
#include <memory>
using namespace mhac::clock_fold;
using namespace mhac::clock_fold::quality;
static void le(std::ostream& f,unsigned n,int bytes){for(int i=0;i<bytes;++i)f.put(static_cast<char>((n>>(8*i))&255));}
int main(){
    constexpr unsigned sr=48000, packets=24,n=packets*frameSize;
    constexpr double pi=3.14159265358979323846;
    auto bank=std::make_unique<KernelBank>();bank->prepare();
    auto frame=std::make_unique<std::array<Stereo,frameSize>>();
    Controls c;c.drift=.5;c.curvature=-.5;const auto plan=Plan::make(c);
    std::ofstream a("quality-linear.wav",std::ios::binary),b("quality-filtered.wav",std::ios::binary);
    for(auto* f:{&a,&b}){if(!*f)return 1;f->write("RIFF",4);le(*f,36+n*4,4);f->write("WAVEfmt ",8);le(*f,16,4);le(*f,1,2);le(*f,2,2);le(*f,sr,4);le(*f,sr*4,4);le(*f,4,2);le(*f,16,2);f->write("data",4);le(*f,n*4,4);}
    for(unsigned packet=0;packet<packets;++packet){
        for(unsigned i=0;i<frameSize;++i){const double t=double(packet*frameSize+i)/sr;const double env=packet==packets-1?0:std::exp(-12*std::fmod(t,.25));(*frame)[i]={env*(.12*std::sin(2*pi*220*t)+.12*std::sin(2*pi*16800*t)),env*(.12*std::sin(2*pi*330*t)+.12*std::sin(2*pi*14400*t))};}
        for(unsigned i=0;i<frameSize;++i){const double t=double(i)/(frameSize-1),src=plan.source(t)*(frameSize-1);const auto lo=std::min(std::size_t(src),frameSize-1),hi=std::min(lo+1,frameSize-1);const double frac=src-lo,w=std::min(1.,std::min(t,1-t)/.03);auto q=bank->render(*frame,plan,i);for(int ch=0;ch<2;++ch){const double dry=(*frame)[i][ch],linear=(1-frac)*(*frame)[lo][ch]+frac*(*frame)[hi][ch];le(a,std::uint16_t(std::lround(((1-w)*dry+w*linear)*32767)),2);le(b,std::uint16_t(std::lround(((1-w)*dry+w*q[ch])*32767)),2);}}
    }
    return !a||!b;
}
