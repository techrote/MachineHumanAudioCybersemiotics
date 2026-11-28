#pragma once
#include "timbre/socket.hpp"
namespace winters::integrated {
constexpr unsigned Count=19;
using Params=std::array<double,Count>;
constexpr Params defaults{0,1./3,2./3,1,0,0,0,.2,1,1,1,0,0,0,0,0,0,0,.2};
inline bool transient(unsigned i) noexcept {return i==4||i==5||i==15||i==16;}
inline double normalized(unsigned i,double x) noexcept {
    if(i<live::Count)return live::normalized(i,x);
    x=std::clamp(x,0.,1.);return i>=15&&i<=17?double(x>=.5):x;
}
using State=std::array<std::uint8_t,4+4*Count>;
inline State encode(const Params& p) noexcept {
    State s{'T','W','0','2'};
    for(unsigned i=0;i<Count;++i){float f=float(transient(i)?0:p[i]);std::uint32_t u;std::memcpy(&u,&f,4);for(unsigned j=0;j<4;++j)s[4+4*i+j]=std::uint8_t(u>>(8*j));}return s;
}
inline bool decode(const std::uint8_t* s,std::size_t n,Params& p) noexcept {
    if(!s||n<4||s[0]!='T'||s[1]!='W'||s[2]!='0')return false;
    Params q=defaults;
    if(s[3]=='1'){live::Params old{};if(!live::decode(s,n,old))return false;std::copy(old.begin(),old.end(),q.begin());}
    else if(s[3]=='2'&&n==State{}.size()){
        for(unsigned i=0;i<Count;++i){std::uint32_t u=0;for(unsigned j=0;j<4;++j)u|=std::uint32_t(s[4+4*i+j])<<(8*j);float f;std::memcpy(&f,&u,4);if(!std::isfinite(f)||f<0||f>1||(transient(i)&&f!=0))return false;q[i]=normalized(i,f);}
    }else return false;
    p=q;return true;
}
class Engine {
    timbre::Engine e;
    Params p=defaults;
    double rate=48000,phase=0;
public:
    const Params& parameters() const noexcept{return p;}
    std::array<double,3> targets() const noexcept{return e.socket.values();}
    const std::array<double,3>& amounts() const noexcept{return e.amounts();}
    bool prepare(double sr) noexcept {if(!e.prepare(sr))return false;rate=sr;reset();return true;}
    void reset() noexcept {
        e.reset();phase=0;
        for(unsigned i=0;i<Count;++i)if(transient(i))p[i]=0;
        live::Params old{};std::copy_n(p.begin(),live::Count,old.begin());e.pitch.restore(old);
        for(unsigned i=0;i<4;++i)e.socket.edit(i,p[11+i]);
    }
    void restore(const Params& values) noexcept {auto q=values;p=defaults;for(unsigned i=0;i<Count;++i)if(std::isfinite(q[i]))p[i]=normalized(i,q[i]);reset();}
    void parameter(unsigned i,double x) noexcept {
        if(i>=Count||!std::isfinite(x))return;
        x=normalized(i,x);if(x==p[i])return;p[i]=x;
        if(i<live::Count)e.pitch.parameter(i,x);
        else if(i<15)e.socket.edit(i-11,x);
        else if(i==15){if(x)e.socket.hold();else e.socket.release();}
        else if(i==16&&x)e.socket.tick();
        else if(i==17)phase=0;
    }
    bool on(int id,int note,double tuning,double velocity) noexcept{return e.pitch.on(id,note,tuning,velocity);}
    void off(int id) noexcept{e.pitch.off(id);}
    live::Frame tick() noexcept {
        if(p[17]){if(phase>=1-1e-10){phase=std::max(0.,phase-1);e.socket.tick();}phase+=(.5+7.5*p[18])/rate;}
        return e.sample();
    }
};
}
