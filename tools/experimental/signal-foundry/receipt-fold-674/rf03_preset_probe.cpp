// Receipt Fold RF03 offline preset and signal probe, Refs #674.
// Component-only VST3 format from SDK 3.8.0 public.sdk a3911a46,
// source/vst/vstpresetfile.cpp. Windows CID verified against moduleinfo.json.
#include "resolution_host.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <iomanip>
using namespace mhac::receipt::extended;
using mhac::receipt::Mode;
namespace {
using Bytes=std::array<std::uint8_t,92>;
constexpr char cid[]="302FA8177F104E13BFC8A3EF4356888E";
void put(Bytes& b,unsigned at,std::uint64_t v,unsigned n){
    for(unsigned i=0;i<n;++i)b[at+i]=static_cast<std::uint8_t>(v>>(8*i));
}
Bytes wrap(const Patch& p){
    if(!valid(p))throw std::invalid_argument("invalid RF03 patch");
    Bytes b{};std::memcpy(b.data(),"VST3",4);put(b,4,1,4);
    std::memcpy(b.data()+8,cid,32);put(b,40,64,8);
    const auto s=save(p);std::copy(s.begin(),s.end(),b.begin()+48);
    std::memcpy(b.data()+64,"List",4);put(b,68,1,4);
    std::memcpy(b.data()+72,"Comp",4);put(b,76,48,8);put(b,84,16,8);
    return b;
}
// Strict reader only for our minimal generated format, not arbitrary presets.
bool unwrap(const Bytes& b,Patch& p){
    Patch x;if(!load(b.data()+48,16,x)||wrap(x)!=b)return false;
    p=x;return true;
}
struct Entry {const char* name;Patch patch;};
constexpr Entry bank[]={
    {"09 Coarse Collapse",{{{0,7},Mode::absent,false,.8},3,0,0,255,true}},
    {"10 Fine Distortion",{{{1,6},Mode::absent,false,.8},8,0,96,175,true}},
    {"11 Budget Ambiguity",{{{1,6},Mode::fixed,false,.8},8,4,96,176,true}},
    {"12 Budget Witness",{{{1,6},Mode::fixed,false,.8},8,5,96,176,true}},
    {"13 Preview Recovery",{{{1,6},Mode::preview,false,.8},8,4,96,176,true}},
    {"14 Full Reference",{{{1,6},Mode::full,false,.8},8,4,96,176,true}},
    {"15 Adjacent Expansion",{{{1,6},Mode::absent,false,.6},6,0,255,255,true}},
    {"16 Legacy Geometry",{{{2,6},Mode::fixed,false,.6},5,2,32,192,false}},
    {"17 Dry Reference",{{{1,6},Mode::full,true,1},8,8,96,176,true}}
};
void require(bool ok){if(!ok)throw std::runtime_error("preset/probe regression failed");}
struct Metrics {double peak=0,energy=0,error=0;};
template<class T> Metrics probe(const Patch& p){
    Host direct,restored;require(direct.prepare(48000)&&restored.prepare(48000));
    Patch recovered;require(unwrap(wrap(p),recovered)&&restored.request(recovered));
    require(direct.apply(p));restored.begin();
    for(unsigned i=0;i<240;++i){T l=0,r=0;direct.frame(l,r);restored.frame(l,r);}
    restored.end();Patch snapshot;require(restored.snapshot(snapshot)&&save(snapshot)==save(p));
    Metrics m;double phase=0;
    // 1 s logarithmic chirp, 40 Hz to 12 kHz, opposing stereo input.
    // Compare direct and restored engines through variable block boundaries.
    for(unsigned i=0;i<48000;++i){
        if(i%127==0)restored.begin();
        phase+=6.283185307179586*40*std::pow(300.,double(i)/47999)/48000;
        const T x=static_cast<T>(.9*std::sin(phase));T l=x,r=-x,a=l,b=r;
        direct.frame(l,r);restored.frame(a,b);
        require(l==a&&r==b&&std::isfinite(l)&&std::isfinite(r));
        m.peak=std::max({m.peak,std::abs(double(l)),std::abs(double(r))});
        m.energy+=double(l)*l+double(r)*r;
        m.error+=(double(l)-x)*(double(l)-x)+(double(r)+x)*(double(r)+x);
        if(i%127==126)restored.end();
    }
    restored.end();require(m.peak<=1.0);
    // A single impulse followed by zeros must have no audio tail.
    T l=static_cast<T>(1),r=0;direct.frame(l,r);require(r==0&&std::abs(l)<=1);
    for(unsigned i=0;i<1024;++i){l=r=0;direct.frame(l,r);require(l==0&&r==0);}
    return m;
}
void test(){
    unsigned cases=0,mutations=0;
    for(unsigned bits=3;bits<=8;++bits)for(unsigned budget=0;budget<=8;++budget)
        for(unsigned m=0;m<4;++m)for(bool fine:{false,true})for(bool bypass:{false,true}){
            Patch p{{{2,6},static_cast<Mode>(m),bypass,.12345678901234567},bits,budget,96,176,fine},q;
            require(unwrap(wrap(p),q)&&save(p)==save(q));++cases;
            Patch controls;for(unsigned id=0;id<count;++id)require(control(controls,id,normalized(p,id)));
            require(save(controls)==save(p));
        }
    for(unsigned rank=0;rank<28;++rank){
        mhac::receipt::Patch old{mhac::receipt::unrank(rank),Mode::fixed,false,.6};
        const auto bytes=mhac::receipt::save(old);Patch p;
        require(load(bytes.data(),bytes.size(),p)&&p.bits==3&&p.budget==1&&!p.fine);
        require(mhac::receipt::save(p.legacy)==bytes);
    }
    for(const auto& e:bank){
        auto bytes=wrap(e.patch);
        for(unsigned i=0;i<bytes.size();++i){
            // Valid alternative RF03 controls are not corruption detectable by this format.
            if(i>=52&&i<64)continue;
            auto bad=bytes;bad[i]^=1;Patch q;const auto before=save(q);
            require(!unwrap(bad,q)&&save(q)==before);++mutations;
        }
        const auto a=probe<float>(e.patch),b=probe<double>(e.patch);
        require(std::abs(a.energy-b.energy)<.01);
    }
    const auto a=probe<double>(bank[3].patch),b=probe<double>(bank[4].patch),c=probe<double>(bank[5].patch);
    require(a.energy==b.energy&&b.energy==c.energy&&a.error==b.error&&b.error==c.error);
    require(probe<double>(bank[8].patch).error==0);
    std::cout<<cases<<" RF03 roundtrips, "<<mutations<<" rejected structural mutations, "
             <<9*2*48000<<" paired stereo sweep frames, 18 zero-tail probes\n";
}
}
int main(int argc,char** argv){
    try{
        test();if(argc==1)return 0;
        if(argc!=2)throw std::invalid_argument("usage: receipt_fold_rf03_preset_probe [output-directory]");
        const std::filesystem::path dir(argv[1]);std::filesystem::create_directories(dir);
        std::ofstream csv(dir/"sweep.csv");csv<<"preset,peak,rms,error_rms\n"<<std::setprecision(12);
        for(const auto& e:bank){
            const auto b=wrap(e.patch);const auto path=dir/(std::string(e.name)+".vstpreset");
            std::ofstream f(path,std::ios::binary|std::ios::trunc);
            f.write(reinterpret_cast<const char*>(b.data()),static_cast<std::streamsize>(b.size()));f.close();require(bool(f));
            Bytes read{};std::ifstream in(path,std::ios::binary);
            in.read(reinterpret_cast<char*>(read.data()),static_cast<std::streamsize>(read.size()));
            require(bool(in)&&in.peek()==std::char_traits<char>::eof()&&read==b);
            const auto m=probe<double>(e.patch);
            csv<<e.name<<','<<m.peak<<','<<std::sqrt(m.energy/96000)<<','<<std::sqrt(m.error/96000)<<'\n';
        }
        csv.close();require(bool(csv));return 0;
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
