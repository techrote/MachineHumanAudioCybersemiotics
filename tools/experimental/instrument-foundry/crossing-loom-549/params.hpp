#pragma once
#include "loom.hpp"
#include <cstring>
#include <limits>
namespace loom {
constexpr unsigned Count=4;
using Params=std::array<double,Count>;
constexpr Params defaults{.3125,.475/1.975,1.,0.};
inline void set(Params& p,unsigned i,double x) noexcept {if(i<Count&&std::isfinite(x))p[i]=i==3?double(x>=.5):std::clamp(x,0.,1.);}
inline Patch patch(const Params& p) noexcept {return {p[0]*.8,.025+1.975*p[1],p[2],p[3]>=.5};}
using State=std::array<std::uint8_t,4+Count*4>;
inline State encode(const Params& p) noexcept {
    static_assert(sizeof(float)==4&&std::numeric_limits<float>::is_iec559,"IEEE float required");
    State s{'C','L','0','1'};
    for(unsigned i=0;i<Count;++i){float f=float(p[i]);std::uint32_t u=0;std::memcpy(&u,&f,4);for(unsigned j=0;j<4;++j)s[4+4*i+j]=std::uint8_t(u>>(8*j));}return s;
}
inline bool decode(const State& s,Params& p) noexcept {
    if(s[0]!='C'||s[1]!='L'||s[2]!='0'||s[3]!='1')return false;
    Params next{};
    for(unsigned i=0;i<Count;++i){std::uint32_t u=0;for(unsigned j=0;j<4;++j)u|=std::uint32_t(s[4+4*i+j])<<(8*j);float f;std::memcpy(&f,&u,4);if(!std::isfinite(f)||f<0||f>1||(i==3&&f!=0&&f!=1))return false;next[i]=f;}
    p=next;return true;
}
}
