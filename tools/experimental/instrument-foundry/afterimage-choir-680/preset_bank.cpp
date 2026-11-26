// Offline Afterimage Choir preset bank, Refs #680. No SDK or audio-thread use.
// Container layout checked against VST3 SDK 3.8.0 public.sdk a3911a46,
// source/vst/vstpresetfile.cpp (writeHeader/writeChunkList/loadPreset).
#include "live.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
using namespace mhac::afterimage::live;
namespace {
using Bytes=std::array<unsigned char,84>;
constexpr char cid[]="BD0B8CB3B82E43EB9613F0C9A37FBA83";
void put(Bytes& b,unsigned at,std::uint64_t x,unsigned n){
    for(unsigned j=0;j<n;++j)b[at+j]=static_cast<unsigned char>(x>>(8*j));
}
Bytes wrap(Word w){
    if(!valid(w))throw std::invalid_argument("invalid AC01 patch");
    Bytes b{};
    std::memcpy(b.data(),"VST3",4);put(b,4,1,4);
    std::memcpy(b.data()+8,cid,32);put(b,40,56,8);
    const auto s=encode(w);std::copy(s.begin(),s.end(),b.begin()+48);
    std::memcpy(b.data()+56,"List",4);put(b,60,1,4);
    std::memcpy(b.data()+64,"Comp",4);put(b,68,48,8);put(b,76,8,8);
    return b;
}
// Deliberately strict reader for our minimal component-only format, not a
// general-purpose parser for arbitrary third-party VST3 preset files.
bool unwrap(const Bytes& b,Word& w){
    Word x=0;if(!decode(b.data()+48,8,x)||wrap(x)!=b)return false;
    w=x;return true;
}
struct Entry {const char* name;Word w;};
constexpr Entry bank[]{
    {"01 Ambiguous Parity",pack(16,1,80,800)},
    {"02 Informed Memory",pack(16,2,80,1000)},
    {"03 Late Bound Complete",pack(11,3,150,650)},
    {"04 Pure Fundamental",pack(16,0,80,0)},
    {"05 Wide Collapse",pack(6,0,25,1000)},
    {"06 Slow Commit",pack(16,3,600,900)},
    {"07 Flicker Memory",pack(16,2,0,500)},
    {"08 Parity Separation",pack(11,1,80,1000)}
};
void require(bool ok){if(!ok)throw std::runtime_error("preset regression failed");}
void test(){
    unsigned cases=0;
    for(unsigned p=0;p<28;++p)for(unsigned m=0;m<4;++m)
        for(unsigned ms:{0u,80u,2000u})for(unsigned a:{0u,800u,1000u}){
            const Word w=pack(p,m,ms,a);Word x=0;
            const auto b=wrap(w);require(unwrap(b,x)&&x==w);++cases;
        }
    unsigned mutations=0;std::uint64_t frames=0;
    for(const auto& entry:bank){
        const auto b=wrap(entry.w);Word x=0;require(unwrap(b,x));
        for(unsigned j=0;j<b.size();++j){
            // AC01 payload bits may describe another valid patch; test only
            // container bytes and the AC01 magic as mandatory invariants.
            if(j>=52&&j<56)continue;
            auto bad=b;bad[j]^=1;Word sentinel=Default;
            require(!unwrap(bad,sentinel)&&sentinel==Default);++mutations;
        }
        Live a,c;Bridge bridge;require(a.prepare(48000)&&c.prepare(48000));
        require(a.applyPatch(entry.w)&&bridge.request(x));bridge.begin(c);bridge.end(c);
        require(bridge.save()==entry.w);
        for(int note:{62,60,67}){
            require(a.on(note,note,0,.8)&&c.on(note,note,0,.8));
            for(unsigned i=0;i<32000;++i){const double y=a.tick();require(y==c.tick()&&std::abs(y)<=.52);++frames;}
            require(a.off(note)&&c.off(note));
            for(unsigned i=0;i<1600;++i){require(a.tick()==c.tick());++frames;}
            require(a.active()==0&&c.active()==0&&a.remembered()==c.remembered());
        }
    }
    std::cout<<cases<<" patch roundtrips, "<<mutations<<" rejected mutations, "<<frames<<" exact audio frames\n";
}
}
int main(int argc,char** argv){
    try{
        test();
        if(argc==1)return 0;
        if(argc!=2)throw std::invalid_argument("usage: preset_bank [output-directory]");
        const std::filesystem::path dir(argv[1]);std::filesystem::create_directories(dir);
        for(const auto& e:bank){
            const auto b=wrap(e.w);const auto path=dir/(std::string(e.name)+".vstpreset");
            std::ofstream f(path,std::ios::binary|std::ios::trunc);
            f.write(reinterpret_cast<const char*>(b.data()),static_cast<std::streamsize>(b.size()));
            f.close();require(bool(f));
            Bytes read{};std::ifstream in(path,std::ios::binary);
            in.read(reinterpret_cast<char*>(read.data()),static_cast<std::streamsize>(read.size()));
            require(bool(in)&&in.peek()==std::char_traits<char>::eof()&&read==b);
        }
        return 0;
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
