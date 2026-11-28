#pragma once
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <cstring>
namespace offcut {
constexpr unsigned Count=4;
using Params=std::array<double,Count>;
constexpr Params defaults{.5,.6,2./7.,0.};
constexpr double tau=6.2831853071795864769;
inline bool supported(double sr) noexcept {return std::isfinite(sr)&&sr>=1000&&sr<=2000000;}
inline double unit(double x,double fallback=0) noexcept {return std::isfinite(x)?std::clamp(x,0.,1.):fallback;}
inline void set(Params& p,unsigned i,double x) noexcept {
    if(i<Count&&std::isfinite(x)){x=unit(x);p[i]=i==3?double(x>=.5):i==2?std::round(x*7)/7:x;}
}
using State=std::array<std::uint8_t,4+Count*4>;
inline State encode(const Params& p) noexcept {
    State s{'O','C','0','1'};
    for(unsigned i=0;i<Count;++i){float f=float(p[i]);std::uint32_t u;std::memcpy(&u,&f,4);for(unsigned j=0;j<4;++j)s[4+4*i+j]=std::uint8_t(u>>(8*j));}return s;
}
inline bool decode(const State& s,Params& p) noexcept {
    if(s[0]!='O'||s[1]!='C'||s[2]!='0'||s[3]!='1')return false;
    Params next=defaults;
    for(unsigned i=0;i<Count;++i){std::uint32_t u=0;for(unsigned j=0;j<4;++j)u|=std::uint32_t(s[4+4*i+j])<<(8*j);float f;std::memcpy(&f,&u,4);if(!std::isfinite(f)||f<0||f>1||(i==3&&f!=0&&f!=1))return false;set(next,i,f);}
    p=next;return true;
}
struct Pair {double l=0,r=0;};
struct Complement {double primary=0,residual=0;};
inline Complement split(double x,double threshold,double articulation) noexcept {
    x=std::isfinite(x)?std::clamp(x,-1.,1.):0.;threshold=unit(threshold,.5);
    const double y=std::clamp(x,-threshold,threshold);
    return {y,(x-y)*unit(articulation)};
}
struct Voice {
    bool active=false,releasing=false,reconstruct=false;int id=0;
    double phase=0,colour=0,inc=0,colourInc=0,level=0,velocity=0,threshold=.5,amount=0,releaseStart=0;
    std::uint64_t age=0,attack=1,release=1,released=0;
    void start(int key,int note,double cents,double vel,double sr,const Params& p) noexcept {
        *this=Voice{};active=true;id=key;velocity=unit(vel);
        const double pitch=std::clamp(note,0,127)+(std::isfinite(cents)?std::clamp(cents,-1200.,1200.):0.)/100.;
        const double f=440*std::exp2((pitch-69)/12);
        inc=std::min(.45,f/sr);colourInc=std::min(.45,inc*(1+std::round(7*unit(p[2],defaults[2]))));
        threshold=.2+.6*unit(p[0],defaults[0]);amount=unit(p[1],defaults[1]);reconstruct=unit(p[3])>=.5;
        attack=std::max<std::uint64_t>(1,std::llround(.005*sr));release=std::max<std::uint64_t>(1,std::llround(.04*sr));
    }
    void off() noexcept {if(active&&!releasing){releasing=true;releaseStart=level;released=0;}}
    Pair tick() noexcept {
        if(!active)return {};
        if(releasing){if(released>=release){active=false;return {};}level=releaseStart*(1-double(++released)/double(release));}
        else {if(age<attack)++age;level=double(age)/double(attack);}
        const auto c=split(std::sin(tau*phase),threshold,amount*(.5+.5*std::cos(tau*colour)));
        phase+=inc;if(phase>=1)phase-=1;colour+=colourInc;if(colour>=1)colour-=1;
        const double gain=.05*velocity*level;
        if(reconstruct){const double x=gain*(c.primary+c.residual);return {x,x};}
        return {gain*c.primary,gain*c.residual};
    }
};
class Engine {
    std::array<Voice,8> voices{};double sr=48000;
public:
    bool prepare(double rate) noexcept {if(!supported(rate))return false;sr=rate;reset();return true;}
    void reset() noexcept {voices={};}
    bool on(int id,int note,double cents,double velocity,const Params& p) noexcept {
        if(!std::isfinite(velocity)||velocity<=0){off(id);return false;}
        for(auto& v:voices)if(v.active&&v.id==id)return false;
        for(auto& v:voices)if(!v.active){v.start(id,note,cents,velocity,sr,p);return true;}
        return false;
    }
    void off(int id) noexcept {for(auto& v:voices)if(v.active&&v.id==id)v.off();}
    Pair tick() noexcept {Pair p;for(auto& v:voices){const auto x=v.tick();p.l+=x.l;p.r+=x.r;}return p;}
    template<class T> void render(T* l,T* r,int n) noexcept {for(int i=0;i<n;++i){const auto p=tick();if(r){l[i]=T(p.l);r[i]=T(p.r);}else l[i]=T((p.l+p.r)*.5);}}
};
}
