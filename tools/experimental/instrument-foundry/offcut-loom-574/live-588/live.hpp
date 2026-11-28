#pragma once
#include "../nested-580/nested.hpp"
namespace offcut::live {
constexpr unsigned Count=8;
using Params=std::array<double,Count>;
constexpr Params defaults{.5,.6,2./7.,0.,0.,.2,1.,4./15.};
inline void set(Params& p,unsigned i,double x) noexcept {
    if(i>=Count||!std::isfinite(x))return;
    x=unit(x);
    p[i]=(i==3||i==4)?double(x>=.5):i==2?std::round(x*7)/7:i==7?std::round(x*15)/15:x;
}
using State=std::array<std::uint8_t,4+4*Count>;
inline State encode(const Params& p) noexcept {
    State s{'O','C','0','2'};
    for(unsigned i=0;i<Count;++i){float f=float(p[i]);std::uint32_t u;std::memcpy(&u,&f,4);for(unsigned j=0;j<4;++j)s[4+4*i+j]=std::uint8_t(u>>(8*j));}return s;
}
inline bool decode(const std::uint8_t* s,std::size_t n,Params& p) noexcept {
    if(!s||n<4||s[0]!='O'||s[1]!='C'||s[2]!='0')return false;
    Params q=defaults;
    if(s[3]=='1'&&n==offcut::State{}.size()){
        offcut::State b{};std::copy_n(s,n,b.begin());offcut::Params old{};if(!offcut::decode(b,old))return false;
        std::copy(old.begin(),old.end(),q.begin());
    }else if(s[3]=='2'&&n==State{}.size()){
        for(unsigned i=0;i<Count;++i){std::uint32_t u=0;for(unsigned j=0;j<4;++j)u|=std::uint32_t(s[4+4*i+j])<<(8*j);float f;std::memcpy(&f,&u,4);if(!std::isfinite(f)||f<0||f>1||((i==3||i==4)&&f!=0&&f!=1))return false;set(q,i,f);}
    }else return false;
    p=q;return true;
}
struct Frame {double l=0,r=0,primary=0,middle=0,deep=0;};
struct Slot {
    nested::Voice voice;bool nestedMode=false,reconstruct=false;
    void start(int id,int note,double cents,double vel,double rate,const Params& p) noexcept {
        offcut::Params old{};std::copy_n(p.begin(),4,old.begin());
        nestedMode=unit(p[4])>=.5;reconstruct=unit(p[3])>=.5;
        if(nestedMode){nested::Patch patch;patch.original=old;patch.cut=unit(p[5],.2);patch.depth=unit(p[6],1);patch.ratio=1+std::round(15*unit(p[7],defaults[7]));voice.start(id,note,cents,vel,rate,patch);}
        else voice.source.start(id,note,cents,vel,rate,old);
    }
    Frame tick() noexcept {
        if(!voice.source.active)return {};
        if(!nestedMode){auto p=voice.source.tick();return {p.l,p.r,0,0,0};}
        auto s=voice.tick();double l=s.primary+s.middle,r=s.deep;
        if(reconstruct)l=r=s.sum();
        return {l,r,s.primary,s.middle,s.deep};
    }
};
class Engine {
    std::array<Slot,8> slots{};double rate=48000;
public:
    bool prepare(double r) noexcept {if(!supported(r))return false;rate=r;reset();return true;}
    void reset() noexcept {slots={};}
    bool on(int id,int note,double cents,double velocity,const Params& p) noexcept {
        if(!std::isfinite(velocity)||velocity<=0){off(id);return false;}
        for(auto& s:slots)if(s.voice.source.active&&s.voice.source.id==id)return false;
        for(auto& s:slots)if(!s.voice.source.active){s.start(id,note,cents,velocity,rate,p);return true;}
        return false;
    }
    void off(int id) noexcept {for(auto& s:slots)if(s.voice.source.active&&s.voice.source.id==id)s.voice.source.off();}
    Frame tick() noexcept {Frame f;for(auto& s:slots){auto x=s.tick();f.l+=x.l;f.r+=x.r;f.primary+=x.primary;f.middle+=x.middle;f.deep+=x.deep;}return f;}
};
// Main remains a monitor even with aux buses enabled. Aux stems are nested voices only.
// Null/omitted buffers never alter the state or the main signal.
template<class T> void write(const Frame& f,T* const* main,unsigned channels,T* primary,T* middle,T* deep,unsigned i) noexcept {
    if(main&&channels==1&&main[0])main[0][i]=T((f.l+f.r)*.5);
    if(main&&channels==2){if(main[0])main[0][i]=T(f.l);if(main[1])main[1][i]=T(f.r);}
    if(primary)primary[i]=T(f.primary);
    if(middle)middle[i]=T(f.middle);
    if(deep)deep[i]=T(f.deep);
}
}
