#pragma once
#include "guest.hpp"
#include <cstring>
#include <limits>
namespace guest::control {
constexpr unsigned Count=11;
using Params=std::array<double,Count>;
constexpr Params defaults{.5,19./24,15./24,22./24,3./11,.65,0,0,0,0,.5};
inline double normalized(unsigned i,double x) noexcept {
    x=std::clamp(x,0.,1.);
    return i<4?std::round(x*24)/24:i>=6&&i<=9?double(x>=.5):x;
}
using State=std::array<std::uint8_t,4+4*Count>;
static_assert(sizeof(float)==4&&std::numeric_limits<float>::is_iec559,"GO01/GO02/GO03 require IEEE binary32");
inline State encode(const Params& p) noexcept {
    State s{'G','O','0','3'};
    for(unsigned i=0;i<Count;++i){float f=float(p[i]);std::uint32_t u;std::memcpy(&u,&f,4);for(unsigned j=0;j<4;++j)s[4+4*i+j]=std::uint8_t(u>>(8*j));}
    return s;
}
inline bool decode(const std::uint8_t* s,std::size_t n,Params& p) noexcept {
    if(!s||n<4||s[0]!='G'||s[1]!='O'||s[2]!='0')return false;
    const unsigned count=s[3]=='1'?8:s[3]=='2'?9:s[3]=='3'?Count:0;
    if(!count||n!=4+4*count)return false;
    Params q=defaults;
    for(unsigned i=0;i<count;++i){std::uint32_t u=0;for(unsigned j=0;j<4;++j)u|=std::uint32_t(s[4+4*i+j])<<(8*j);float f;std::memcpy(&f,&u,4);if(!std::isfinite(f)||f<0||f>1)return false;q[i]=normalized(i,f);}
    p=q;return true;
}
class Engine {
    guest::Engine e;
    Params p=defaults;
    void sync() noexcept {
        Patch patch;
        for(unsigned i=0;i<4;++i)patch.motif[i]=int(std::lround(p[i]*24))-12;
        patch.stepsPerSecond=1+11*p[4];patch.counterGain=p[5];patch.cite=p[6]!=0;patch.adopt=p[7]!=0;patch.spectral=p[8]!=0;patch.fm=p[9]!=0;patch.fmDepth=p[10];
        e.configure(patch);
    }
public:
    Engine() noexcept {sync();}
    const Params& parameters() const noexcept{return p;}
    bool prepare(double sr) noexcept {if(!e.prepare(sr))return false;sync();return true;}
    void reset() noexcept {e.reset();sync();}
    void restore(const Params& q) noexcept {auto v=q;for(unsigned i=0;i<Count;++i)if(std::isfinite(v[i]))p[i]=normalized(i,v[i]);reset();}
    void parameter(unsigned i,double x) noexcept {if(i>=Count||!std::isfinite(x))return;p[i]=normalized(i,x);sync();}
    bool on(int id,int note,double tuning,double velocity) noexcept{return e.on(id,note,tuning,velocity);}
    void off(int id) noexcept{e.off(id);}
    Frame tick() noexcept{return e.tick();}
};
template<class T> void write(Frame f,T** main,unsigned channels,T* base,T* counter,unsigned i) noexcept {
    if(channels==1){if(main[0])main[0][i]=T((f.left+f.right)*.5);}
    else if(channels==2){if(main[0]&&main[0]==main[1])main[0][i]=T((f.left+f.right)*.5);else{if(main[0])main[0][i]=T(f.left);if(main[1])main[1][i]=T(f.right);}}
    if(base)base[i]=T(f.base);
    if(counter)counter[i]=T(f.counter);
}
}
