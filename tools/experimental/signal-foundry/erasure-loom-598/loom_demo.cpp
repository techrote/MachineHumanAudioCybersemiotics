#include "loom.hpp"
#include <fstream>
#include <iostream>
using namespace loom;
void word(std::ostream& o,unsigned v,unsigned n){for(unsigned i=0;i<n;++i)o.put(char((v>>(8*i))&255));}
int main(){constexpr unsigned sr=48000,n=sr*4+Engine::tail;
    const char* names[]={"reference.wav","dropout.wav","adjacent-raw.wav","adjacent-guarded.wav","spread-raw.wav"};
    for(unsigned m=0;m<5;++m){Engine e;if(!e.prepare(sr))return 1;Params p;p.wet=m?1:0;p.repair=m==1?0:1;p.separation=m==4?4:1;p.budget=m==3?2:16;e.set(p);e.reset();
        std::ofstream o(names[m],std::ios::binary);if(!o)return 2;o.write("RIFF",4);word(o,36+4*n,4);o.write("WAVEfmt ",8);word(o,16,4);word(o,1,2);word(o,2,2);word(o,sr,4);word(o,sr*4,4);word(o,4,2);word(o,16,2);o.write("data",4);word(o,4*n,4);double peak=0;
        for(unsigned i=0;i<n;++i){double x=0,y=0;if(i<sr*4){double t=double(i)/sr,env=std::min({1.,t*30.,(4-t)*30.});double a=220*std::pow(2.,int(t*2)%4/12.);x=env*(.09*std::sin(2*pi*a*t)+.04*std::sin(2*pi*(333.333*t+80*t*t))+.05*std::sin(2*pi*666.666*t));y=env*(.08*std::sin(2*pi*330*t)+.04*std::sin(2*pi*(444*t+35*t*t)));}auto z=e.step(x,y);for(double v:z){peak=std::max(peak,std::abs(v));word(o,unsigned(int(std::lround(v*32767))),2);}}
        if(!o)return 3;
        std::cout<<names[m]<<" peak="<<peak<<'\n';
    }
}
