#include "winters.hpp"
#include <fstream>
#include <iostream>
using namespace winters;
static void u(std::ofstream& f,unsigned v,int n){for(int i=0;i<n;++i)f.put(static_cast<char>((v>>(i*8))&255));}
int main(int argc,char** argv){
    if(argc!=2)return 2;
    std::ofstream f(argv[1],std::ios::binary);if(!f)return 1;
    constexpr unsigned sr=48000,n=sr*6,bytes=n*6;
    f.write("RIFF",4);u(f,36+bytes,4);f.write("WAVEfmt ",8);u(f,16,4);u(f,1,2);u(f,3,2);u(f,sr,4);u(f,sr*6,4);u(f,6,2);u(f,16,2);f.write("data",4);u(f,bytes,4);
    Engine e;e.setup(sr);
    for(unsigned i=0;i<n;++i){
        if(i==0)e.noteOn(1,60,.9);
        if(i==sr/2)e.noteOn(2,67,.7);
        if(i==sr)e.hold();
        if(i==sr*3/2)e.edit(1,3);
        if(i==sr*2)e.tick();
        if(i==sr*3)e.release();
        if(i==sr*4)e.tick();
        if(i==sr*5){e.noteOff(1);e.noteOff(2);}
        for(double v:e.sample())u(f,static_cast<unsigned>(static_cast<int>(std::lround(v*32767))),2);
    }
    return f?0:1;
}
