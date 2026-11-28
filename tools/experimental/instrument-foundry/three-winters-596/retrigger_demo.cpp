#include "live.hpp"
#include <fstream>
#include <iostream>
void word(std::ofstream& o,unsigned v,int n){for(int i=0;i<n;++i)o.put(char((v>>(8*i))&255));}
int main(int argc,char** argv){
    if(argc!=2)return 2;
    constexpr unsigned rate=48000, period=2400, count=24, frames=rate*2;
    winters::live::Engine e;if(!e.prepare(rate))return 1;
    std::ofstream o(argv[1],std::ios::binary);
    o.write("RIFF",4);word(o,36+frames*4,4);o.write("WAVEfmt ",8);word(o,16,4);word(o,1,2);word(o,2,2);word(o,rate,4);word(o,rate*4,4);word(o,4,2);word(o,16,2);o.write("data",4);word(o,frames*4,4);
    unsigned accepted=0;
    for(unsigned i=0;i<frames;++i){
        if(i<count*period&&i%period==0){if(e.on(-61,60,0,.3+.2*((i/period)%4)))++accepted;}
        if(i<count*period&&i%period==1440)e.off(-61);
        if(i==0)e.parameter(6,1);
        if(i==12000)e.parameter(4,1);
        if(i==24000)e.parameter(1,1);
        if(i==36000)e.parameter(4,0);
        const auto f=e.tick();for(double x:{f.l,f.r})word(o,unsigned(std::lround(x*32767)),2);
    }
    std::cout<<"accepted "<<accepted<<"/"<<count<<" note-ons\n";return o?0:1;
}
