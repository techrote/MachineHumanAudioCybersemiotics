#pragma once
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <limits>
namespace mhac::forge {
enum Parameter : unsigned { Drive, Coupling, Isolate, Mix, Gain, Bypass, Count };
using Params = std::array<float,Count>;
inline constexpr Params defaults{.75f,1.f,0.f,.5f,.75f,0.f};
using State = std::array<std::uint8_t,4+4*Count>;
static_assert(sizeof(float)==4 && std::numeric_limits<float>::is_iec559,"IEEE binary32 required");
inline bool validSampleRate(double r){return std::isfinite(r)&&r>=8000&&r<=384000;}
inline bool valid(const Params& p){for(float x:p)if(!std::isfinite(x)||x<0||x>1)return false;return true;}
inline State encode(const Params& p){State s{'W','F','0','1'};for(unsigned i=0;i<Count;++i){std::uint32_t u;std::memcpy(&u,&p[i],4);for(unsigned j=0;j<4;++j)s[4+4*i+j]=std::uint8_t(u>>(8*j));}return s;}
inline bool decode(const State& s,Params& p){if(s[0]!='W'||s[1]!='F'||s[2]!='0'||s[3]!='1')return false;Params q{};for(unsigned i=0;i<Count;++i){std::uint32_t u=0;for(unsigned j=0;j<4;++j)u|=std::uint32_t(s[4+4*i+j])<<(8*j);std::memcpy(&q[i],&u,4);}if(!valid(q))return false;p=q;return true;}
inline double guard(double x){return !std::isfinite(x)||std::abs(x)<1e-20?0.:std::clamp(x,-1.,1.);}
class Forge {
    Params target=defaults;
    std::array<double,Count> current{};
    double slew=1./240;
public:
    Forge(){reset(48000);}
    bool reset(double rate){if(!validSampleRate(rate))return false;slew=1./std::ceil(rate*.005);for(unsigned i=0;i<Count;++i)current[i]=target[i];return true;}
    const Params& params()const{return target;}
    bool restore(const Params& p){if(!valid(p))return false;target=p;return true;}
    void set(unsigned id,double x){if(id<Count&&std::isfinite(x))target[id]=static_cast<float>(std::clamp(x,0.,1.));}
    template<class T> std::array<T,2> process(T left,T right){
        for(unsigned i=0;i<Count;++i){double d=double(target[i])-current[i];current[i]+=std::clamp(d,-slew,slew);}
        const double l=guard(left),r=guard(right),g=2*current[Drive]-1,c=current[Coupling],keep=1-current[Isolate];
        const double m=current[Mix]*(1-current[Bypass]),a=current[Gain];
        // At full coupling and zero isolation: z + gamma*z*|z|^2.
        // At full isolation only the cross-channel cubic term survives.
        const double wl=l*(keep*(1+g*l*l)+g*c*r*r);
        const double wr=r*(keep*(1+g*r*r)+g*c*l*l);
        return {T(guard((1-m)*l+m*a*wl)),T(guard((1-m)*r+m*a*wr))};
    }
};
}
