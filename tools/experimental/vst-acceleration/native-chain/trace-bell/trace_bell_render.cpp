#include "trace_bell.hpp"
#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <string>
using namespace mhac::accel;
// Offline raw stereo signed PCM16 little-endian at 48 kHz, no header.
int main(int argc,char** argv) {
    if(argc!=4) { std::cerr<<"usage: trace_bell_render INPUT.raw OUTPUT.raw glass|bronze|haze\n";return 2; }
    TracePatch p; const std::string name=argv[3];
    if(name=="glass") p={220,.35f,.8f,.65f,.5f,false};
    else if(name=="bronze") p={110,.8f,.45f,.6f,.9f,false};
    else if(name=="haze") p={330,1.2f,.95f,.8f,1.f,false};
    else return 2;
    if(std::string(argv[1])==argv[2]) return 2;
    std::ifstream in(argv[1],std::ios::binary); if(!in) return 2;
    in.seekg(0,std::ios::end); auto bytes=in.tellg();
    if(bytes<=0||bytes%4!=0||bytes>48000*60*4) return 2;
    in.seekg(0);
    std::ofstream out(argv[2],std::ios::binary); if(!out) return 2;
    TraceBell bell; if(!bell.configure(p)) return 2;bell.reset();
    std::array<unsigned char,4> b{};
    auto sample=[&](unsigned i) { int x=b[i]+256*int(b[i+1]);return float(x>=32768?x-65536:x)/32768.f; };
    auto store=[&](unsigned i,float x) { int y=std::clamp(int(std::lround(x*32768.f)),-32768,32767);unsigned u=static_cast<unsigned>(y)&65535u;b[i]=u&255u;b[i+1]=u>>8; };
    for(std::streamoff i=0;i<bytes/4+48000*3;++i) {
        TraceFrame x{0,0};
        if(i<bytes/4) { if(!in.read(reinterpret_cast<char*>(b.data()),4)) return 2;x={sample(0),sample(2)}; }
        auto y=bell.process(x);store(0,y.l);store(2,y.r);
        if(!out.write(reinterpret_cast<const char*>(b.data()),4)) return 2;
    }
    out.close();return out?0:2;
}
