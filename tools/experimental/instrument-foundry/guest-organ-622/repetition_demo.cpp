#include "guest.hpp"
#include <fstream>
#include <iostream>
void word(std::ofstream& o,std::uint32_t n,unsigned bytes){for(unsigned i=0;i<bytes;++i)o.put(char((n>>(8*i))&255));}
int main(int argc,char** argv){
    if(argc!=2)return 1;
    constexpr unsigned rate=48000,n=rate*2,period=2400,gate=1440;
    guest::Engine e;e.prepare(rate);guest::Patch p;p.adopt=true;e.configure(p);
    std::ofstream o(argv[1],std::ios::binary);if(!o)return 2;
    o.write("RIFF",4);word(o,36+n*4,4);o.write("WAVEfmt ",8);word(o,16,4);word(o,1,2);word(o,2,2);word(o,rate,4);word(o,rate*4,4);word(o,4,2);word(o,16,2);o.write("data",4);word(o,n*4,4);
    unsigned accepted=0;
    for(unsigned i=0;i<n;++i){if(i<24*period){if(i%period==0)accepted+=e.on(1,48+int(i/period)%4,0,.8);if(i%period==gate)e.off(1);}auto f=e.tick();word(o,std::uint16_t(std::lround(f.left*32767)),2);word(o,std::uint16_t(std::lround(f.right*32767)),2);}
    std::cout<<accepted<<"/24 accepted\n";return o?0:3;
}
