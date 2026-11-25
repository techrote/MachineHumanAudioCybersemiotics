#include "socket.hpp"
#include <fstream>
#include <string>
void word(std::ofstream& o,unsigned v,int n){for(int i=0;i<n;++i)o.put(char((v>>(8*i))&255));}
int main(int argc,char** argv){
    if(argc!=3)return 2;
    const bool neutral=std::string(argv[2])=="neutral";
    constexpr unsigned rate=48000, frames=rate*6;
    winters::timbre::Engine e;if(!e.prepare(rate))return 1;
    std::ofstream o(argv[1],std::ios::binary);
    o.write("RIFF",4);word(o,36+frames*6,4);o.write("WAVEfmt ",8);word(o,16,4);word(o,1,2);word(o,3,2);word(o,rate,4);word(o,rate*6,4);word(o,6,2);word(o,16,2);o.write("data",4);word(o,frames*6,4);
    if(!neutral){e.socket.edit(1,.85);e.socket.edit(2,.3);e.socket.edit(3,1);}
    for(unsigned i=0;i<frames;++i){
        if(i==0){e.pitch.on(1,48,0,.8);e.pitch.on(2,55,0,.7);e.pitch.parameter(6,1);}
        if(i==rate)e.socket.hold();
        if(i==rate*3/2&&!neutral)e.socket.edit(2,.95);
        if(i==rate*2&&!neutral)e.socket.edit(0,.7);
        if(i==rate*3)e.socket.release();
        if(i>0&&i%(rate/2)==0)e.socket.tick();
        if(i==rate*5){e.pitch.off(1);e.pitch.off(2);}
        auto f=e.sample();for(double x:{f.primary,f.middle,f.deep})word(o,unsigned(std::lround(x*32767)),2);
    }
    return o?0:1;
}
