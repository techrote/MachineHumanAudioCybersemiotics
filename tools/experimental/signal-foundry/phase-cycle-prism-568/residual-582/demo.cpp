#include "residual.hpp"
#include <fstream>
#include <iostream>
#include <string>
using namespace prism;
void word(std::ostream& o,unsigned v,unsigned n){for(unsigned i=0;i<n;++i)o.put(char((v>>(8*i))&255));}
int main(){
    constexpr unsigned sr=48000,N=sr*4;ResidualPrism p;if(!p.prepare(sr))return 1;
    for(unsigned mode=0;mode<4;++mode){
        p.set(Drive,mode==0?.5:1);p.set(Cancel,mode==2?0:1);p.set(Wet,1);p.set(Gain,1);p.set(Count,mode==3?0:1);p.reset();
        const char* names[]={"neutral.wav","corrected.wav","raw.wav","isolated.wav"};std::ofstream o(names[mode],std::ios::binary);if(!o)return 2;
        o.write("RIFF",4);word(o,36+4*N,4);o.write("WAVEfmt ",8);word(o,16,4);word(o,1,2);word(o,2,2);word(o,sr,4);word(o,sr*4,4);word(o,4,2);word(o,16,2);o.write("data",4);word(o,4*N,4);
        for(unsigned t=0;t<N;++t){const double s=double(t)/sr,env=std::min({1.,s*20.,(4.-s)*20.});C x{};for(unsigned j=1;j<4;++j)x+=std::polar(.12,tau*bins[j]*double(t%600)/600.);x+=std::polar(.09,tau*(233*s+18*s*s));x+=C(.035*std::sin(tau*110*s)*std::exp(-8*std::fmod(s,.5)),0);x*=env;auto y=p.step(x.real(),x.imag());word(o,unsigned(std::int32_t(std::lround(y.real()*32767))),2);word(o,unsigned(std::int32_t(std::lround(y.imag()*32767))),2);}
        if(!o)return 3;
    }
}
