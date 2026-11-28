// Refs #674. RF04 component-only preset writer and native restoration probe.
// Build: c++ -std=c++17 -O2 -pthread rf04_preset_probe.cpp -o rf04_probe
// Run: ./rf04_probe [output-directory]. No SDK needed; format follows pinned RF03 tool.
#include "balanced_host.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <iomanip>
#include <stdexcept>
namespace b=mhac::receipt::balanced_host;
namespace r=mhac::receipt;
namespace {
using Bytes=std::array<std::uint8_t,96>;
constexpr char cid[]="302FA8177F104E13BFC8A3EF4356888E";
void check(bool ok){if(!ok)throw std::runtime_error("RF04 preset regression failed");}
void put(Bytes& out,unsigned pos,std::uint64_t x,unsigned n){for(unsigned i=0;i<n;++i)out[pos+i]=static_cast<std::uint8_t>(x>>(8*i));}
Bytes wrap(const b::Patch& p){
    check(b::valid(p));Bytes out{};std::memcpy(out.data(),"VST3",4);put(out,4,1,4);
    std::memcpy(out.data()+8,cid,32);put(out,40,68,8);
    auto s=b::save(p);std::copy(s.begin(),s.end(),out.begin()+48);
    std::memcpy(out.data()+68,"List",4);put(out,72,1,4);
    std::memcpy(out.data()+76,"Comp",4);put(out,80,48,8);put(out,88,20,8);return out;
}
// Strict reader for this writer's canonical subset; not a general VST preset reader.
bool unwrap(const Bytes& in,b::Patch& p){b::Patch q;if(!b::load(in.data()+48,20,q)||wrap(q)!=in)return false;p=q;return true;}
struct Entry{const char* name;unsigned bits,budget,epoch,seed,a,z;bool enabled,bypass;double wet;};
constexpr Entry bank[]={
    {"18 Coarse Turbulence",3,1,25,42,32,160,true,false,.8},
    {"19 Fine Pulse",8,3,25,42,32,160,true,false,.8},
    {"20 Fine Slow",8,3,250,42,32,160,true,false,.8},
    {"21 Fine Alternate Seed",8,3,25,65535,32,160,true,false,.8},
    {"22 Full Budget Reference",8,8,25,42,32,160,true,false,.8},
    {"23 Fixed Tag Reference",8,3,25,42,32,160,false,false,.8},
    {"24 Zero Budget Flutter",4,0,5,7,32,224,true,false,.6},
    {"25 Balanced Dry Reference",8,3,25,42,32,160,true,true,.8}
};
b::Patch patch(const Entry& e){b::Patch p;p.legacy.mode=r::Mode::fixed;p.legacy.wet=e.wet;p.legacy.bypass=e.bypass;
    p.bits=e.bits;p.budget=e.budget;p.a=e.a;p.b=e.z;p.fine=true;p.balanced=e.enabled;p.epoch=e.epoch;p.seed=e.seed;return p;}
struct Metrics{double peak=0,energy=0,error=0;};
template<class T> Metrics probe(const b::Patch& p){
    b::Host a,h;check(a.prepare(48000)&&h.prepare(48000));b::Patch q;
    check(unwrap(wrap(p),q)&&a.apply(p)&&h.request(q));a.reset();h.begin();h.reset();
    Metrics m;double phase=0;
    for(unsigned i=0;i<96000;++i){if(i%257==0)h.begin();
        phase+=6.283185307179586*40*std::pow(300.,double(i)/95999.)/48000.;
        const T x=static_cast<T>(.9*std::sin(phase));T l=x,rr=-x,u=l,v=rr;
        a.frame(l,rr);h.frame(u,v);check(l==u&&rr==v&&std::isfinite(l)&&std::isfinite(rr));
        m.peak=std::max({m.peak,std::abs(double(l)),std::abs(double(rr))});
        m.energy+=double(l)*l+double(rr)*rr;m.error+=(double(l)-x)*(double(l)-x)+(double(rr)+x)*(double(rr)+x);
        if(i%257==256)h.end();}
    h.end();check(h.snapshot(q)&&b::save(q)==b::save(p)&&m.peak<=1);
    T l=1,rr=0;a.frame(l,rr);check(rr==0&&std::abs(l)<=1);
    for(unsigned i=0;i<1024;++i){l=rr=0;a.frame(l,rr);check(l==0&&rr==0);}return m;
}
void test(){unsigned cases=0,mutations=0;
    for(unsigned bits=3;bits<=8;++bits)for(unsigned budget=0;budget<=8;++budget)
      for(unsigned epoch:{5u,25u,1000u})for(unsigned seed:{0u,42u,65535u})for(bool enabled:{false,true}){
        auto p=patch(bank[0]);p.bits=bits;p.budget=budget;p.epoch=epoch;p.seed=seed;p.balanced=enabled;b::Patch q;
        check(unwrap(wrap(p),q)&&b::save(q)==b::save(p));++cases;
      }
    for(const auto& e:bank){auto p=patch(e);const auto bytes=wrap(p);
        for(unsigned i=0;i<bytes.size();++i){if(i>=52&&i<68)continue;auto bad=bytes;bad[i]^=1;b::Patch q;const auto before=b::save(q);
            check(!unwrap(bad,q)&&b::save(q)==before);++mutations;}
        probe<float>(p);probe<double>(p);
    }
    check(probe<double>(patch(bank[7])).error==0);
    auto full=patch(bank[4]);auto fixed=full;fixed.balanced=false;
    check(probe<double>(full).error==probe<double>(fixed).error);
    std::cout<<cases<<" RF04 roundtrips, "<<mutations<<" rejected structural mutations, 1536000 paired stereo sweep frames, 16 zero-tail probes (bank only)\n";
}
}
int main(int argc,char** argv){try{test();if(argc==1)return 0;check(argc==2);
    const std::filesystem::path dir(argv[1]);std::filesystem::create_directories(dir);
    std::ofstream csv(dir/"sweep-rf04.csv");csv<<"preset,peak,rms,error_rms\n"<<std::setprecision(12);
    for(const auto& e:bank){auto p=patch(e);auto bytes=wrap(p);auto path=dir/(std::string(e.name)+".vstpreset");
        std::ofstream f(path,std::ios::binary|std::ios::trunc);f.write(reinterpret_cast<const char*>(bytes.data()),static_cast<std::streamsize>(bytes.size()));f.close();check(bool(f));
        Bytes read{};std::ifstream in(path,std::ios::binary);in.read(reinterpret_cast<char*>(read.data()),static_cast<std::streamsize>(read.size()));check(bool(in)&&in.peek()==std::char_traits<char>::eof()&&read==bytes);
        auto m=probe<double>(p);csv<<e.name<<','<<m.peak<<','<<std::sqrt(m.energy/192000)<<','<<std::sqrt(m.error/192000)<<'\n';}
    csv.close();check(bool(csv));return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
