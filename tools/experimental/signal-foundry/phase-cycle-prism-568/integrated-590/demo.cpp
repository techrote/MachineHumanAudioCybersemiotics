#include "integrated.hpp"
#include <fstream>
#include <iostream>
using namespace prism;
void word(std::ostream& o,unsigned v,unsigned n){for(unsigned i=0;i<n;++i)o.put(char((v>>(8*i))&255));}
int main(){
    constexpr unsigned sr=48000, frames=sr*4, tail=1800;
    IntegratedPrism p;if(!p.prepare(sr))return 1;
    for(unsigned mode=0;mode<3;++mode){
        p.restore({mode==0?.5:1.,1.,1.,1.,0.,0.,mode==2?0.:1.});p.reset();
        const char* names[]={"reference.wav","broadband.wav","retention-sweep.wav"};std::ofstream o(names[mode],std::ios::binary);if(!o)return 2;
        const unsigned n=frames+tail;o.write("RIFF",4);word(o,36+4*n,4);o.write("WAVEfmt ",8);word(o,16,4);word(o,1,2);word(o,2,2);word(o,sr,4);word(o,sr*4,4);word(o,4,2);word(o,16,2);o.write("data",4);word(o,4*n,4);
        double peak=0;
        for(unsigned t=0;t<n;++t){
            C x{};const double s=double(t)/sr;
            if(t<frames){const double env=std::min({1.,s*25.,(4.-s)*25.});for(unsigned j=1;j<4;++j)x+=std::polar(.12,tau*bins[j]*double(t%600)/600.);x+=std::polar(.1,tau*(211*s+38*s*s));x+=C(.04*std::sin(tau*110*s)*std::exp(-8*std::fmod(s,.5)),0);x*=env;}
            if(mode==2&&t<frames)p.set(Retention,.5-.5*std::cos(tau*s/4.));
            const auto y=p.step(x.real(),x.imag());peak=std::max({peak,std::abs(y.real()),std::abs(y.imag())});
            word(o,unsigned(std::int32_t(std::lround(y.real()*32767))),2);word(o,unsigned(std::int32_t(std::lround(y.imag()*32767))),2);
        }
        if(!o)return 3;
        std::cout<<names[mode]<<" peak="<<peak<<'\n';
    }
}
