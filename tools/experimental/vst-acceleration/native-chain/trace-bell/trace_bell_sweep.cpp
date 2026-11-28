#include "trace_bell_state.hpp"
#include <array>
#include <fstream>
#include <string>
using namespace mhac::accel;
// Offline comparison of immediate vs polar-retuned poles, using identical
// 48 kHz stereo signed little-endian PCM16 input and an attenuated output.
int main(int argc,char** argv){
    if(argc!=4||std::string(argv[1])==argv[2])return 2;
    const std::string style=argv[3];if(style!="instant"&&style!="polar")return 2;
    std::ifstream in(argv[1],std::ios::binary);if(!in)return 2;
    in.seekg(0,std::ios::end);const auto bytes=in.tellg();if(bytes!=720000*4)return 2;in.seekg(0);
    std::ofstream out(argv[2],std::ios::binary);if(!out)return 2;
    TraceBell bell;bell.setTuningSmoothing(style=="polar");
    TracePatch p{110,.8f,.45f,.7f,.3f,false};if(!bell.configure(p))return 2;bell.reset();
    std::array<unsigned char,4> b{};
    const auto load=[&](unsigned i){int x=b[i]+256*int(b[i+1]);return float(x>=32768?x-65536:x)/32768.f;};
    const auto store=[&](unsigned i,float x){int y=std::clamp(int(std::lround(x*16384.f)),-32768,32767);unsigned u=static_cast<unsigned>(y)&65535u;b[i]=u&255u;b[i+1]=u>>8;};
    for(unsigned i=0;i<720000;++i){
        // Deliberate held-memory retuning and shorter rhythmic intervals.
        if(i&&i<576000&&i%24000==0){
            constexpr float pitches[]={110,165,220,330,440,220,146.83f,293.66f};
            const unsigned k=i/24000;p.pitch=pitches[k%8];p.spread=(k%3)*.5f;p.decay=k%4==0?.35f:.8f;
            if(!bell.configure(p))return 2;
        }
        if(!in.read(reinterpret_cast<char*>(b.data()),4))return 2;
        const auto y=bell.process({load(0),load(2)});store(0,y.l);store(2,y.r);
        if(!out.write(reinterpret_cast<const char*>(b.data()),4))return 2;
    }
    out.close();return out?0:2;
}
