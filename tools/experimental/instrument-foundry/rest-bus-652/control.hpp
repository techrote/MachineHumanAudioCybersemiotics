#pragma once
#include "rest.hpp"
#include <cstring>
#include <limits>
namespace restbus::control {
constexpr unsigned Count=4;
constexpr unsigned FirstID=1500;
using Params=std::array<double,3>;
inline constexpr Params defaults{0.,(.3-.01)/9.99,0.};
using State=std::array<std::uint8_t,28>;
static_assert(sizeof(double)==8 && std::numeric_limits<double>::is_iec559);
inline bool valid(double v) noexcept {return std::isfinite(v)&&v>=0&&v<=1;}
inline Domain domain(double v) noexcept {return static_cast<Domain>(std::lround(3*v));}
inline Destination destination(double v) noexcept {return static_cast<Destination>(std::lround(2*v));}
inline double seconds(double v) noexcept {return .01+9.99*v;}
inline State encode(const Params& p) noexcept {
    State b{'R','B','0','2'};
    for(unsigned i=0;i<p.size();++i){std::uint64_t bits;std::memcpy(&bits,&p[i],8);for(unsigned j=0;j<8;++j)b[4+8*i+j]=std::uint8_t(bits>>(8*j));}
    return b;
}
inline bool decode(const std::uint8_t* b,std::size_t n,Params& p) noexcept {
    if(!b||n<4)return false;
    const bool legacy=n==20&&std::memcmp(b,"RB01",4)==0;
    if(!legacy&&(n!=State{}.size()||std::memcmp(b,"RB02",4)!=0))return false;
    Params candidate=defaults;
    for(unsigned i=0;i<(legacy?2:candidate.size());++i){std::uint64_t bits=0;for(unsigned j=0;j<8;++j)bits|=std::uint64_t(b[4+8*i+j])<<(8*j);std::memcpy(&candidate[i],&bits,8);if(!valid(candidate[i]))return false;}
    p=candidate;return true;
}
class Live {
    restbus::Engine engine_;
    Params p_=defaults;
    bool stepHigh_=false;
public:
    bool prepare(double sr) noexcept {if(!engine_.prepare(sr,seconds(p_[1])))return false;engine_.domain(domain(p_[0]));engine_.destination(destination(p_[2]));stepHigh_=false;return true;}
    void reset() noexcept {engine_.reset();stepHigh_=false;}
    const Params& parameters() const noexcept {return p_;}
    bool restore(const Params& p) noexcept {
        if(!valid(p[0])||!valid(p[1])||!valid(p[2]))return false;
        p_=p;engine_.domain(domain(p_[0]));engine_.period(seconds(p_[1]));engine_.destination(destination(p_[2]));reset();return true;
    }
    bool parameter(unsigned id,double v) noexcept {
        if(id>=Count||!valid(v))return false;
        if(id==2){bool high=v>=.5;if(high&&!stepHigh_)engine_.step();stepHigh_=high;return true;}
        if(id==3){p_[2]=v;engine_.destination(destination(v));return true;}
        if(p_[id]==v)return true;
        p_[id]=v;
        if(id==0)engine_.domain(domain(v));else engine_.period(seconds(v));
        return true;
    }
    unsigned index() const noexcept {return engine_.index();}
    unsigned partial() const noexcept {return engine_.partial();}
    bool on(int id,int note,double tune,double velocity) noexcept {if(velocity==0){off(id);return true;}return engine_.on(id,note,tune,velocity);}
    void off(int id) noexcept {engine_.off(id);}
    double tick() noexcept {return engine_.tick();}
};
}
