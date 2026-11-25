#include "live.hpp"
#include <fstream>
#include <iostream>
using namespace loom;
static void word(std::ostream& o,unsigned v,unsigned n){for(unsigned i=0;i<n;++i)o.put(char((v>>(8*i))&255));}
int main(){
    constexpr unsigned sr=48000,n=sr*6+Engine::tail;
    for(bool wet:{false,true}){
        Live e;if(!e.prepare(sr))return 1;e.set(Wet,wet?1:0);e.set(Gain,1);e.reset();
        const char* name=wet?"geometry-sweep.wav":"geometry-reference.wav";
        std::ofstream o(name,std::ios::binary);if(!o)return 2;
        o.write("RIFF",4);word(o,36+4*n,4);o.write("WAVEfmt ",8);word(o,16,4);word(o,1,2);word(o,2,2);word(o,sr,4);word(o,sr*4,4);word(o,4,2);word(o,16,2);o.write("data",4);word(o,4*n,4);
        double peak=0,energy=0;
        for(unsigned i=0;i<n;++i){
            const double t=double(i)/sr;
            if(i%48==0&&i<sr*6){e.set(Separation,t<3?0:1);e.set(Rotation,double((i/(sr/4))%9)/8);e.set(Budget,.5-.5*std::cos(2*pi*t/3));e.set(Repair,1);}
            double x=0,y=0;
            if(i<sr*6){const double env=std::min({1.,t*30.,(6-t)*30.});const double pulse=std::exp(-12*std::fmod(t,.5));x=env*(.10*std::sin(2*pi*(110*t+95*t*t))+.04*pulse*std::sin(2*pi*67*t));y=env*(.09*std::sin(2*pi*(165*t+71*t*t))+.04*pulse*std::sin(2*pi*89*t));}
            auto z=e.step(x,y);for(double v:z){peak=std::max(peak,std::abs(v));energy+=v*v;word(o,unsigned(int(std::lround(v*32767))),2);}
        }
        if(!o)return 3;
        std::cout<<name<<" peak="<<peak<<" rms="<<std::sqrt(energy/(2*n))<<'\n';
    }
}
