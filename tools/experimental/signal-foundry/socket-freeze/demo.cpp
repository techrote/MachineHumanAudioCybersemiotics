#include "freeze.hpp"
#include <fstream>
#include <iostream>
#include <string>
using namespace mhac;
void le(std::ostream& o,uint32_t n,unsigned bytes){for(unsigned i=0;i<bytes;++i)o.put(char(n>>(8*i)));}
int main(int argc,char** argv){
 const std::string path=argc>1?argv[1]:"socket-freeze-demo.wav";
 std::ofstream o(path,std::ios::binary);if(!o)return 1;
 constexpr int sr=48000, segment=sr*6, n=segment*4;
 o.write("RIFF",4);le(o,36+n*4,4);o.write("WAVEfmt ",8);le(o,16,4);le(o,1,2);le(o,2,2);le(o,sr,4);le(o,sr*4,4);le(o,4,2);le(o,16,2);o.write("data",4);le(o,n*4,4);
 for(int m=-1;m<3;++m){Freeze f;f.prepare(sr);f.set(Rate,0.5);f.set(Wet,1);f.set(Mode,m<0?0:m/2.0);
 for(int i=0;i<segment;++i){double t=double(i)/sr; if(i==sr&&m>=0)f.set(Hold,1);if(i==2*sr){f.set(S0,0.8);f.set(S1,0.2);f.set(S2,0.9);}if(i==4*sr)f.set(Hold,0);
 double g=f.step();double env=std::min({1.0,t*100,(6-t)*100});double l=env*(0.18*std::sin(6.283185307179586*220*t)+0.09*std::sin(6.283185307179586*331*t));double r=env*(0.18*std::sin(6.283185307179586*220*t)+0.09*std::sin(6.283185307179586*443*t));
 for(double x:{l,r})le(o,uint16_t(int16_t(std::lround(32767*x*(m<0?1:g)))),2);
 }} if(!o)return 2;std::cout<<path<<" 24 s stereo PCM16\n";
}
