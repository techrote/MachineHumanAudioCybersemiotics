#include "prism.hpp"
#include <fstream>
#include <filesystem>
#include <iostream>
#include <string>
#include <cstdint>
using namespace prism;
int main(int argc,char** argv){
    if(argc!=8){std::cerr<<"usage: prism_process input.s16le output.s16le rate drive cancel wet gain\n";return 2;}
    if(std::string(argv[1])==argv[2])return 2;
    std::error_code ec;if(std::filesystem::exists(argv[2],ec)||ec)return 2;
    Prism p;double v[5];
    try{for(int i=0;i<5;++i){std::size_t end=0;v[i]=std::stod(argv[i+3],&end);if(end!=std::string(argv[i+3]).size()||!std::isfinite(v[i]))return 2;}}catch(...){return 2;}
    if(v[1]<-1||v[1]>1||v[2]<0||v[2]>1||v[3]<0||v[3]>1||v[4]<0||v[4]>1)return 2;
    p.set({v[1],v[2],v[3],v[4]});if(!p.prepare(v[0]))return 2;
    std::ifstream in(argv[1],std::ios::binary);if(!in)return 2;
    std::ofstream out(argv[2],std::ios::binary);if(!out)return 2;
    auto sample=[](const unsigned char* b){int x=int(b[0])+256*int(b[1]);return (x>=32768?x-65536:x)/32768.;};
    auto write=[&](C y){for(double a:{y.real(),y.imag()}){auto s=static_cast<std::uint16_t>(std::lround(a*32767));out.put(static_cast<char>(s&255));out.put(static_cast<char>(s>>8));}};
    unsigned char b[4];while(in.read(reinterpret_cast<char*>(b),4))write(p.step(sample(b),sample(b+2)));
    if(!in.eof()||in.gcount()!=0){std::cerr<<"invalid or truncated stereo PCM input; output is partial\n";return 3;}
    for(std::size_t i=0;i<p.tailBound();++i)write(p.step(0,0));
    out.close();return out?0:3;
}
