#pragma once
#include "lattice.hpp"
#include <cstdint>
namespace mhac::lattice {
enum Param : unsigned { Axis1,Axis2,Axis3,Axis4,Delay1,Delay2,Delay3,Delay4,Inverse,Mix,Bypass,Count };
using Params=std::array<double,Count>;
inline constexpr Params defaults{2./3,0,1,1./3,31./1023,126./1023,255./1023,510./1023,0,32768./65535,0};
inline unsigned steps(unsigned id) noexcept {return id<4?3:id<8?1023:id==Mix?65535:1;}
inline double canonical(unsigned id,double x) noexcept {return std::round(std::clamp(x,0.,1.)*steps(id))/steps(id);}
inline bool validSampleRate(double x) noexcept {return std::isfinite(x)&&x>=8000&&x<=384000;}
using State=std::array<std::uint8_t,4+2*Count>;
inline State encode(const Params& p) noexcept {
    State s{'P','L',1,0};
    for(unsigned i=0;i<Count;++i){unsigned n=unsigned(std::round(canonical(i,std::isfinite(p[i])?p[i]:defaults[i])*steps(i)));s[4+2*i]=std::uint8_t(n&255);s[5+2*i]=std::uint8_t(n>>8);}
    return s;
}
inline bool decode(const State& s,Params& p) noexcept {
    if(s[0]!='P'||s[1]!='L'||s[2]!=1||s[3]!=0)return false;
    Params candidate{};
    for(unsigned i=0;i<Count;++i){unsigned n=unsigned(s[4+2*i])+(unsigned(s[5+2*i])<<8);if(n>steps(i))return false;candidate[i]=double(n)/steps(i);}
    p=candidate;return true;
}
class Live {
    std::array<Lattice,2> engines{};
    Params desired=defaults, current=defaults, building=defaults;
    unsigned active=0,warm=0,fade=0,fadeLength=240;
    double wet=defaults[Mix];
    bool busy=false;
    static bool sameProgram(const Params& a,const Params& b) noexcept {for(unsigned i=0;i<=Inverse;++i)if(a[i]!=b[i])return false;return true;}
    static Program program(const Params& p) noexcept {Program s{};for(unsigned i=0;i<4;++i)s[i]={static_cast<Axis>(std::lround(p[i]*3)),unsigned(std::lround(p[4+i]*1023))+1};return s;}
    double targetWet() const noexcept {return desired[Bypass]>.5?0:desired[Mix];}
public:
    const Params& params() const noexcept {return desired;}
    bool transitioning() const noexcept {return busy||!sameProgram(desired,current);}
    void set(unsigned id,double value) noexcept {if(id<Count&&std::isfinite(value))desired[id]=canonical(id,value);}
    // Restore queues a transition; reset installs parameters immediately off callback.
    void restore(const Params& p) noexcept {for(unsigned i=0;i<Count;++i)set(i,p[i]);}
    void reset(double sr) noexcept {
        fadeLength=unsigned(std::lround((validSampleRate(sr)?sr:48000.)*.005));
        active=0;busy=false;warm=fade=0;current=building=desired;
        engines[0].configure(program(current),current[Inverse]>.5);wet=targetWet();
    }
    Live() noexcept {reset(48000);}
    template<class T> std::array<T,2> process(T l,T r) noexcept {
        Frame x{guard(double(l)),guard(double(r))};
        if(!busy&&!sameProgram(desired,current)){
            building=desired;auto& next=engines[1-active];next.configure(program(building),building[Inverse]>.5);
            warm=next.tail();fade=0;busy=true;
        }
        auto y=engines[active].step(x);
        if(busy){
            const auto z=engines[1-active].step(x);
            if(warm)--warm;
            else {const double a=double(++fade)/fadeLength;y={y.l+(z.l-y.l)*a,y.r+(z.r-y.r)*a};if(fade==fadeLength){active=1-active;current=building;busy=false;}}
        }
        const double target=targetWet(),delta=target-wet,limit=1./fadeLength;
        wet=std::abs(delta)<=limit?target:wet+std::clamp(delta,-limit,limit);
        return {T(guard(x.l+wet*(y.l-x.l))),T(guard(x.r+wet*(y.r-x.r)))};
    }
};
}
