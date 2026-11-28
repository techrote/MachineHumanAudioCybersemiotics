#include "guest.hpp"
#include <fstream>
#include <string>
void word(std::ofstream& o,std::uint32_t n,unsigned bytes){for(unsigned i=0;i<bytes;++i)o.put(char((n>>(8*i))&255));}
int main(int argc,char** argv){
    if(argc!=2)return 1;
    constexpr unsigned rate=48000,n=rate*6;
    for(unsigned mode=0;mode<3;++mode){
        guest::Engine e;e.prepare(rate);guest::Patch p;p.adopt=true;p.spectral=mode==0;p.fm=mode>0;p.fmDepth=mode==1?0.:1.;e.configure(p);
        std::ofstream o(std::string(argv[1])+"/fm-"+std::to_string(mode)+".wav",std::ios::binary);if(!o)return 2;
        o.write("RIFF",4);word(o,36+n*4,4);o.write("WAVEfmt ",8);word(o,16,4);word(o,1,2);word(o,2,2);word(o,rate,4);word(o,rate*4,4);word(o,4,2);word(o,16,2);o.write("data",4);word(o,n*4,4);
        for(unsigned i=0;i<n;++i){if(i==0)e.on(1,48,0,.8);if(i==2*rate)e.on(2,55,0,.7);if(i==4*rate)e.off(1);if(i==5*rate)e.off(2);auto f=e.tick();word(o,std::uint16_t(std::lround(f.left*32767)),2);word(o,std::uint16_t(std::lround(f.right*32767)),2);}
        if(!o)return 3;
    }
}
