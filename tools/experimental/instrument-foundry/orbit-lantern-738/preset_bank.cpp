// Refs #738. Offline component-only VST3 preset generator and native audition.
#include "host.hpp"
#include <vector>
#include <iterator>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
using namespace mhac::orbit;
namespace {
using Container=std::vector<std::uint8_t>;
constexpr char cid[]="24C15B793B8C4F4B98275F233EE969C4";
void require(bool ok){if(!ok)throw std::runtime_error("Orbit preset regression failed");}
void put(Container& b,unsigned at,std::uint64_t x,unsigned n){for(unsigned j=0;j<n;++j)b[at+j]=std::uint8_t(x>>(8*j));}
void tag(Container& b,unsigned at,const char* s,unsigned n){for(unsigned j=0;j<n;++j)b[at+j]=std::uint8_t(s[j]);}
Container wrap(Patch p){
    require(p.valid());const unsigned n=stateSize(p), list=48u+n;
    Container b(list+28u);tag(b,0,"VST3",4);put(b,4,1,4);tag(b,8,cid,32);put(b,40,list,8);
    const auto state=encodeFull(p);std::copy_n(state.begin(),n,b.begin()+48);
    tag(b,list,"List",4);put(b,list+4,1,4);tag(b,list+8,"Comp",4);put(b,list+12,48,8);put(b,list+20,n,8);return b;
}
// Strict parser for this canonical subset, not arbitrary third-party presets.
bool unwrap(const Container& b,Patch& p){Patch candidate{};
    if(b.size()!=86&&b.size()!=87&&b.size()!=89&&b.size()!=93)return false;
    FullState bytes{};const auto n=unsigned(b.size()-76);std::copy_n(b.begin()+48,n,bytes.begin());
    if(!decodeFull(bytes,n,candidate))return false;
    if(wrap(candidate)!=b)return false;
    p=candidate;return true;}
struct Entry {const char* name;Patch p;bool performance=false;};
constexpr Entry bank[]{
    {"01 Quarter Lantern",{0,240,0}},{"02 Interference Lantern",{500,240,0}},{"03 Persistent Orbit",{1000,240,0}},
    {"04 Needle Orbit",{1000,10,0}},{"05 Slow Ember",{850,850,-25}},{"06 Offset Halo",{200,400,25}},
    {"07 Hollow Fifth",{650,120,-100}},{"08 Bright Return",{350,600,100}},
    {"09 Linear Lantern",{1000,800,0,0}},{"10 Fixed Escape",{1000,800,0,1}},{"11 Phase Escape",{1000,800,0,2}},
    {"12 Fixed Spectrum",{1000,800,0,1,1000}},{"13 Phase Spectrum",{1000,800,0,2,1000}},{"14 Half Spectrum",{1000,800,0,2,500}},
    {"15 Breathing Orbit",{250,500,0,2,500,850,900}},{"16 Slow Tidal Halo",{100,600,0,1,400,1000,2100}},{"17 Flutter Lantern",{400,300,0,2,500,750,200}},
    {"18 Glass Constellation",{180,650,-12,2,700,900,1400},true},
    {"19 Tidal Pedal",{700,900,0,1,250,1000,6000},true},
    {"20 Flicker Choir",{550,180,12,2,800,800,320},true},
    {"21 Still Constellation",{180,650,-12,2,700,0,1000},true},
    {"22 Long Arc",{1000,1000,0,2,1000,1000,8000},true}
};
void writeInt(std::ofstream& f,std::uint32_t n,unsigned bytes){for(unsigned j=0;j<bytes;++j){f.put(char(n&255u));n>>=8;}}
void wavHeader(std::ofstream& f,unsigned frames){f.write("RIFF",4);writeInt(f,36+4*frames,4);f.write("WAVEfmt ",8);writeInt(f,16,4);writeInt(f,1,2);writeInt(f,2,2);writeInt(f,48000,4);writeInt(f,192000,4);writeInt(f,4,2);writeInt(f,16,2);f.write("data",4);writeInt(f,4*frames,4);}
// Original 120 BPM score, 480 PPQ. Same events drive MIDI and native audio.
struct ScoreEvent {unsigned tick;int id,pitch,velocity;};
constexpr ScoreEvent performanceScore[]{
    {0,0,45,76},{0,1,52,65},{0,2,60,71},{480,3,64,92},
    {960,3,64,0},{960,4,67,80},{1440,4,67,0},{1440,5,71,88},
    {1920,5,71,0},{1920,2,60,0},{1920,6,62,73},{2400,7,69,93},
    {2880,7,69,0},{2880,8,72,85},{3360,8,72,0},{3360,1,52,0},
    {3360,9,55,70},{3840,10,74,89},{4320,10,74,0},{4320,11,76,84},
    {4800,11,76,0},{4800,6,62,0},{4800,12,64,70},{5280,13,71,91},
    {5760,13,71,0},{5760,9,55,0},{5760,12,64,0},{6240,0,45,0}
};
constexpr unsigned performanceFrames=384000;
void vlq(Container& b,unsigned value){unsigned bytes[4]{},n=0;bytes[n++]=value&127u;while((value>>=7u)!=0){require(n<4);bytes[n++]=(value&127u)|128u;}while(n)b.push_back(std::uint8_t(bytes[--n]));}
void writePerformanceMidi(const std::filesystem::path& path){
    Container track{0,0xff,0x51,3,0x07,0xa1,0x20};unsigned last=0;
    for(const auto& e:performanceScore){require(e.tick>=last);vlq(track,e.tick-last);last=e.tick;track.push_back(e.velocity?0x90:0x80);track.push_back(std::uint8_t(e.pitch));track.push_back(std::uint8_t(e.velocity));}
    vlq(track,7680-last);track.insert(track.end(),{0xff,0x2f,0});
    std::ofstream f(path,std::ios::binary);require(bool(f));f.write("MThd",4);
    auto be=[&](unsigned value,unsigned n){while(n)f.put(char((value>>(8u*--n))&255u));};
    be(6,4);be(0,2);be(1,2);be(480,2);f.write("MTrk",4);be(unsigned(track.size()),4);
    f.write(reinterpret_cast<const char*>(track.data()),static_cast<std::streamsize>(track.size()));f.close();require(bool(f));
}
void render(const Entry& entry,Patch restored,const std::filesystem::path* dir){
    host::Live a,b;require(a.prepare(48000)&&b.prepare(48000)&&a.setPatch(entry.p)&&b.setPatch(restored));
    std::ofstream f;const unsigned frames=entry.performance?performanceFrames:144000u;unsigned eventIndex=0;
    if(dir){f.open(*dir/(std::string(entry.name)+".wav"),std::ios::binary);require(bool(f));wavHeader(f,frames);}
    double sum=0,peak=0;
    for(unsigned i=0;i<frames;++i){
        if(entry.performance){while(eventIndex<std::size(performanceScore)&&performanceScore[eventIndex].tick*50u==i){
            const auto e=performanceScore[eventIndex++];
            if(e.velocity)require(a.on(e.id,0,e.pitch,0.,e.velocity/127.)&&b.on(e.id,0,e.pitch,0.,e.velocity/127.));
            else require(a.off(e.id,0,e.pitch)&&b.off(e.id,0,e.pitch));
        }}else{
        if(i==0||i==24000||i==48000){const int id=int(i/24000);const int note=48+7*id;require(a.on(id,0,note,0.,.8)&&b.on(id,0,note,0.,.8));}
        if(i==36000||i==60000||i==84000){const int id=int((i-36000)/24000);require(a.off(id,0,0)&&b.off(id,0,0));}
        }
        double l=0,r=0,x=0,y=0;a.tick(l,r);b.tick(x,y);
        require(l==x&&r==y&&std::isfinite(l)&&std::isfinite(r)&&std::abs(l)<=.52&&std::abs(r)<=.52);
        if(i>=frames-2400)require(l==0&&r==0);
        for(double v:{l,r}){sum+=v*v;peak=std::max(peak,std::abs(v));if(dir)writeInt(f,std::uint32_t(int(std::lround(v*32767))),2);}
    }
    require(a.active()==0&&b.active()==0);if(entry.performance)require(eventIndex==std::size(performanceScore));if(dir){f.close();require(bool(f));}
    std::cout<<entry.name<<" peak="<<peak<<" rms="<<std::sqrt(sum/(2*frames))<<'\n';
}
}
int main(int argc,char** argv){try{
    require(argc==1||argc==3);std::filesystem::path presets,audio;
    if(argc==3){presets=argv[1];audio=argv[2];std::filesystem::create_directories(presets);std::filesystem::create_directories(audio);}
    unsigned cases=0,mutations=0,frames=0;
    for(unsigned depth:{0u,1u,500u,999u,1000u})for(unsigned period=200;period<=8000;++period){const Patch p{250,500,0,2,500,depth,period};Patch x{};require(unwrap(wrap(p),x)&&host::pack(p)==host::pack(x));++cases;}
    for(unsigned mix=0;mix<=1000;++mix)for(unsigned ms:{10u,160u,1000u})for(int cents:{-100,0,100})for(unsigned mode=0;mode<3;++mode){
        const Patch p{mix,ms,cents,mode};Patch x{};require(unwrap(wrap(p),x)&&host::pack(p)==host::pack(x));++cases;}
    for(const auto& entry:bank){const auto bytes=wrap(entry.p);Patch x{};require(unwrap(bytes,x));
        for(unsigned j=0;j<bytes.size();++j){if(j>=52&&j<58)continue; if(j>=58&&j<48+stateSize(entry.p))continue;auto bad=bytes;bad[j]^=1;Patch sentinel{111,222,33};require(!unwrap(bad,sentinel)&&host::pack(sentinel)==host::pack({111,222,33}));++mutations;}
        for(unsigned mode:{3u,255u})if(entry.p.releaseMode){auto bad=bytes;bad[58]=std::uint8_t(mode);Patch sentinel{111,222,33};require(!unwrap(bad,sentinel)&&host::pack(sentinel)==host::pack({111,222,33}));++mutations;}
        for(unsigned n=0;n<bytes.size();++n){Container bad(bytes.begin(),bytes.begin()+n);Patch sentinel{111,222,33};require(!unwrap(bad,sentinel)&&host::pack(sentinel)==host::pack({111,222,33}));++mutations;}
        if(argc==3){const auto path=presets/(std::string(entry.name)+".vstpreset");std::ofstream f(path,std::ios::binary);f.write(reinterpret_cast<const char*>(bytes.data()),static_cast<std::streamsize>(bytes.size()));f.close();require(bool(f));Container read(bytes.size());std::ifstream in(path,std::ios::binary);in.read(reinterpret_cast<char*>(read.data()),static_cast<std::streamsize>(read.size()));require(bool(in)&&in.peek()==std::char_traits<char>::eof()&&unwrap(read,x)&&read==bytes);}
        render(entry,x,argc==3?&audio:nullptr);frames+=entry.performance?performanceFrames:144000u;
    }
    if(argc==3)writePerformanceMidi(audio/"Constellation Score.mid");
    std::cout<<"PASS "<<cases<<" roundtrips, "<<mutations<<" rejected mutations, "<<frames<<" exact stereo frames\n";
    return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
