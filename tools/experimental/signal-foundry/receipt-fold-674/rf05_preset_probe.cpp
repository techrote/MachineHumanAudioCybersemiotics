// Refs #674 / #339. Offline canonical RF05 preset bank and RF01-04 migration probe.
// c++ -std=c++17 -O2 -pthread rf05_preset_probe.cpp -o rf05_probe
// ./rf05_probe OUTPUT_DIRECTORY [LEGACY_PRESET_DIRECTORY]
#include "multi_host.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <iomanip>
#include <iterator>
#include <stdexcept>
#include <vector>
namespace h=mhac::receipt::multi_host;
namespace b=mhac::receipt::balanced_host;
namespace fs=std::filesystem;
using Bytes=std::vector<std::uint8_t>;
constexpr char cid[]="302FA8177F104E13BFC8A3EF4356888E";
void check(bool ok){if(!ok)throw std::runtime_error("RF05 preset probe failed");}
void put(Bytes& v,unsigned at,std::uint64_t x,unsigned n){for(unsigned i=0;i<n;++i)v[at+i]=static_cast<std::uint8_t>(x>>(8*i));}
Bytes wrap(const Bytes& state){const auto n=static_cast<unsigned>(state.size());Bytes v(76+n);std::memcpy(v.data(),"VST3",4);put(v,4,1,4);std::memcpy(v.data()+8,cid,32);put(v,40,48+n,8);
    std::copy(state.begin(),state.end(),v.begin()+48);std::memcpy(v.data()+48+n,"List",4);put(v,52+n,1,4);std::memcpy(v.data()+56+n,"Comp",4);put(v,60+n,48,8);put(v,68+n,n,8);return v;}
Bytes wrap(const h::Patch& p){check(h::valid(p));const auto s=h::save(p);return wrap(Bytes(s.begin(),s.end()));}
bool unwrap(const Bytes& v,h::Patch& p){if(v.size()!=92&&v.size()!=96&&v.size()!=104)return false;const auto n=v.size()-76;const Bytes s(v.begin()+48,v.begin()+48+n);h::Patch q;
    if(wrap(s)!=v||!h::load(s.data(),s.size(),q))return false;
    if(n==28&&wrap(q)!=v)return false;
    p=q;return true;}
Bytes read(const fs::path& path){std::ifstream f(path,std::ios::binary);check(bool(f));return Bytes(std::istreambuf_iterator<char>(f),{});}
void write(const fs::path& path,const Bytes& v){std::ofstream f(path,std::ios::binary);f.write(reinterpret_cast<const char*>(v.data()),static_cast<std::streamsize>(v.size()));f.close();check(bool(f)&&read(path)==v);}
struct Entry{const char* name;unsigned bits,pairs,budget,epoch,geometry,seed;h::m::Contract mode;double wet;bool bypass;};
constexpr Entry bank[]={
    {"26 Coarse Matching",3,4,0,25,9,42,h::m::Contract::fixed,.8,false},
    {"27 Balanced Matching",5,16,1,25,9,42,h::m::Contract::balanced,.8,false},
    {"28 Preview Matching",5,16,1,25,9,42,h::m::Contract::preview,.8,false},
    {"29 Known Matching",5,16,1,25,9,42,h::m::Contract::known,.8,false},
    {"30 Fine Flutter",8,128,3,5,123,42,h::m::Contract::balanced,.8,false},
    {"31 Fine Slow",8,128,3,250,123,42,h::m::Contract::balanced,.8,false},
    {"32 Fine Alternate Geometry",8,128,3,5,321,42,h::m::Contract::balanced,.8,false},
    {"33 Dry Matching",5,16,1,25,9,42,h::m::Contract::balanced,.8,true}
};
h::Patch patch(const Entry& e){h::Patch p;p.multi=true;p.multiBits=e.bits;p.pairs=e.pairs;p.multiBudget=e.budget;p.multiEpoch=e.epoch;p.geometry=e.geometry;p.multiSeed=e.seed;p.multiContract=e.mode;p.legacy.wet=e.wet;p.legacy.bypass=e.bypass;return p;}
struct Metrics{double peak=0,energy=0,error=0;};
template<class T> Metrics probe(const h::Patch& p,const Bytes& bytes,bool legacy){h::Patch q;check(unwrap(bytes,q)&&h::save(p)==h::save(q));h::Host a,z;b::Live old;check(a.prepare(48000)&&z.prepare(48000)&&old.prepare(48000)&&a.apply(p)&&z.request(q)&&old.apply(p));a.reset();z.begin();z.reset();old.reset();
    Metrics m;double phase=0;for(unsigned i=0;i<48000;++i){if(i%257==0)z.begin();phase+=6.283185307179586*40*std::pow(300.,double(i)/47999.)/48000.;const T in=static_cast<T>(.8*std::sin(phase));T l=in,r=-in,x=l,y=r,u=l,v=r;
        a.frame(l,r);z.frame(x,y);check(l==x&&r==y&&std::isfinite(l)&&std::isfinite(r)&&std::abs(l)<=1&&std::abs(r)<=1);if(legacy){old.frame(u,v);check(l==u&&r==v);}
        m.peak=std::max({m.peak,std::abs(double(l)),std::abs(double(r))});m.energy+=double(l)*l+double(r)*r;m.error+=(double(l)-in)*(double(l)-in)+(double(r)+in)*(double(r)+in);if(i%257==256)z.end();}
    z.end();check(z.snapshot(q)&&h::save(q)==h::save(p));for(unsigned i=0;i<1024;++i){T l=0,r=0;a.frame(l,r);check(l==0&&r==0);}return m;}
int main(int argc,char** argv){try{check(argc>=1&&argc<=3);unsigned cases=0,mutations=0,migrated=0;
    for(unsigned bits=3;bits<=8;++bits)for(unsigned pairs:{0u,1u,16u,128u})for(unsigned budget=0;budget<=8;++budget)for(unsigned mode=0;mode<4;++mode)for(unsigned epoch:{5u,1000u}){auto p=patch(bank[0]);p.multiBits=bits;p.pairs=pairs;p.multiBudget=budget;p.multiContract=static_cast<h::m::Contract>(mode);p.multiEpoch=epoch;h::Patch q;check(unwrap(wrap(p),q)&&h::save(p)==h::save(q));++cases;}
    for(const auto& e:bank){const auto p=patch(e);const auto bytes=wrap(p);for(unsigned i=0;i<bytes.size();++i){if(i>=48&&i<76)continue;auto bad=bytes;bad[i]^=1;h::Patch q;const auto before=h::save(q);check(!unwrap(bad,q)&&h::save(q)==before);++mutations;}
        const auto m=probe<double>(p,bytes,false);probe<float>(p,bytes,false);if(e.bypass)check(m.error==0);std::cout<<e.name<<','<<std::setprecision(12)<<m.peak<<','<<std::sqrt(m.energy/96000)<<','<<std::sqrt(m.error/96000)<<'\n';if(argc>=2){fs::create_directories(argv[1]);write(fs::path(argv[1])/(std::string(e.name)+".vstpreset"),bytes);}}
    if(argc==3)for(const auto& e:fs::directory_iterator(argv[2])){if(e.path().extension()!=".vstpreset")continue;const auto bytes=read(e.path());h::Patch p;check(unwrap(bytes,p)&&!p.multi);probe<float>(p,bytes,true);probe<double>(p,bytes,true);++migrated;}
    std::cout<<cases<<" RF05 roundtrips, "<<mutations<<" structural mutations rejected, "<<migrated<<" legacy presets compared, "<<(8u+migrated)*96000u<<" paired stereo frames\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
