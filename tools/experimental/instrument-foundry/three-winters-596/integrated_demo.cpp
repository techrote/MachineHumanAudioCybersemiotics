#include "integrated.hpp"
#include <fstream>
#include <string>
void word(std::ofstream& o,unsigned v,int n){for(int i=0;i<n;++i)o.put(char((v>>(8*i))&255));}
int main(int argc,char** argv){
    if(argc!=3)return 2;
    const bool neutral=std::string(argv[2])=="neutral";
    constexpr unsigned rate=48000,frames=rate*6;
    winters::integrated::Engine e;if(!e.prepare(rate))return 1;
    std::ofstream o(argv[1],std::ios::binary);
    o.write("RIFF",4);word(o,36+frames*4,4);o.write("WAVEfmt ",8);word(o,16,4);word(o,1,2);word(o,2,2);word(o,rate,4);word(o,rate*4,4);word(o,4,2);word(o,16,2);o.write("data",4);word(o,frames*4,4);
    e.parameter(6,1);e.parameter(7,.2);e.parameter(17,1);e.parameter(18,.36);
    if(!neutral){e.parameter(12,.85);e.parameter(13,.3);e.parameter(14,1);}
    for(unsigned i=0;i<frames;++i){
        if(i==0){e.on(1,48,0,.8);e.on(2,55,0,.7);}
        if(i==rate)e.parameter(15,1);
        if(i==rate*3/2&&!neutral)e.parameter(13,.95);
        if(i==rate*2)e.parameter(4,1);
        if(i==rate*5/2&&!neutral)e.parameter(11,.7);
        if(i==rate*3)e.parameter(15,0);
        if(i==rate*4)e.parameter(4,0);
        if(i==rate*5){e.off(1);e.off(2);}
        auto f=e.tick();for(double x:{f.l,f.r})word(o,unsigned(std::lround(x*32767)),2);
    }
    return o?0:1;
}
