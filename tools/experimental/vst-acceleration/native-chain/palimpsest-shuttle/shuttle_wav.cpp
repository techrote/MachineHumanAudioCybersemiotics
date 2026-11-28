#include "shuttle.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <memory>
#include <string>
using namespace mhac::accel;
static unsigned get(const unsigned char* p,unsigned n) {unsigned v=0;for(unsigned i=0;i<n;++i)v|=unsigned(p[i])<<(8*i);return v;}
static void put(std::ostream& out,unsigned x,unsigned bytes) {for(unsigned i=0;i<bytes;++i)out.put(char((x>>(8*i))&255));}
static bool tag(const unsigned char* p,const char* s) {return std::equal(p,p+4,s);}
static float pcm(const unsigned char* p) {const int v=int(get(p,2));return float(v>=32768?v-65536:v)/32768.f;}
static int fail(const char* why) {std::cerr<<why<<'\n';return 1;}
int main(int argc,char** argv) {
    if(argc!=4) return fail("usage: shuttle_wav INPUT.wav OUTPUT.wav dry|forward|mirror|shuttle");
    ShuttlePatch p{};const std::string preset=argv[3];
    if(preset=="dry")p={0,0,0,0,true};else if(preset=="forward")p={700,0,450,0,false};
    else if(preset=="mirror")p={850,1000,250,0,false};else if(preset=="shuttle")p={800,850,800,1000,false};else return fail("unknown preset");
    std::ifstream in(argv[1],std::ios::binary);if(!in)return fail("cannot read input");
    // Deliberately strict canonical PCM16 WAV subset: reject extended/chunked formats.
    unsigned char h[44]{};in.read(reinterpret_cast<char*>(h),44);
    if(!in||!tag(h,"RIFF")||!tag(h+8,"WAVE")||!tag(h+12,"fmt ")||!tag(h+36,"data")||get(h+16,4)!=16||get(h+20,2)!=1||get(h+34,2)!=16)return fail("need canonical PCM16 WAV");
    const unsigned channels=get(h+22,2),rate=get(h+24,4),bytes=get(h+40,4);
    if((channels!=1&&channels!=2)||rate<8000||rate>192000||get(h+32,2)!=2*channels||get(h+28,4)!=rate*2*channels||bytes%(2*channels)||bytes>0xffffffffu-36u||get(h+4,4)!=bytes+36u)return fail("invalid WAV dimensions");
    in.seekg(0,std::ios::end);if(in.tellg()!=std::streamoff(44)+bytes)return fail("truncated or extra WAV data");in.seekg(44);
    const unsigned frames=bytes/(2*channels);if(frames>(0xffffffffu-36u)/4u)return fail("output exceeds RIFF limit");
    auto engine=std::make_unique<PalimpsestShuttle<>>();if(!engine->prepare(rate)||!engine->configure(p))return fail("invalid processing configuration");engine->reset();
    std::error_code ec;const auto st=std::filesystem::symlink_status(argv[2],ec);
    if(st.type()!=std::filesystem::file_type::not_found)return fail("output already exists or cannot be inspected");
    std::ofstream out(argv[2],std::ios::binary);if(!out)return fail("cannot create output");
    out.write("RIFF",4);put(out,36+frames*4,4);out.write("WAVEfmt ",8);put(out,16,4);put(out,1,2);put(out,2,2);put(out,rate,4);put(out,rate*4,4);put(out,4,2);put(out,16,2);out.write("data",4);put(out,frames*4,4);
    for(unsigned i=0;i<frames;++i) {
        unsigned char raw[4]{};in.read(reinterpret_cast<char*>(raw),2*channels);if(!in)return fail("input read failed");
        const auto y=engine->process({pcm(raw),pcm(raw+(channels==2?2:0))});
        for(float v:{y.l,y.r})put(out,uint16_t(std::clamp(int(std::lround(v*32768.f)),-32768,32767)),2);
    }
    out.close();if(!out)return fail("output write failed");
    std::cout<<"Rendered "<<frames<<" stereo frames at "<<rate<<" Hz, preset "<<preset<<'\n';
}
