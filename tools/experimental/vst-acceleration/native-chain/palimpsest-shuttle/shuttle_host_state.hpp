#pragma once
#include "shuttle_control.hpp"
namespace mhac::accel {
// Persisted host control bank; the legacy native patch API remains unchanged.
struct ShuttleHostPatch {
    ShuttlePatch base{};
    uint16_t stagger=0;
};
using ShuttleHostState=std::array<uint8_t,15>;
inline bool valid(ShuttleHostPatch p) noexcept {
    return valid(p.base)&&p.stagger<=1000;
}
inline ShuttleHostState encodeHost(ShuttleHostPatch p) noexcept {
    const auto old=encode(p.base);
    ShuttleHostState s{};
    std::copy(old.begin(),old.end(),s.begin());
    if(p.stagger){s[3]='2';s[13]=uint8_t(p.stagger);s[14]=uint8_t(p.stagger>>8);}
    return s;
}
inline unsigned hostStateSize(const ShuttleHostState& s) noexcept {return s[3]=='2'?15u:13u;}
inline bool decodeHost(const ShuttleHostState& s,unsigned size,ShuttleHostPatch& out) noexcept {
    if((size!=13||s[3]!='1')&&(size!=15||s[3]!='2'))return false;
    ShuttleState old{};
    std::copy_n(s.begin(),old.size(),old.begin());old[3]='1';
    ShuttleHostPatch p{};
    if(!decode(old,p.base))return false;
    if(size==15)p.stagger=uint16_t(unsigned(s[13])|(unsigned(s[14])<<8));
    if(!valid(p))return false;
    out=p;return true;
}
inline double hostNormalized(ShuttleHostPatch p,unsigned id) noexcept {
    return id==5?p.stagger/1000.:shuttleNormalized(p.base,id);
}
inline bool applyHostNormalized(ShuttleHostPatch& p,unsigned id,double v) noexcept {
    if(id!=5)return applyShuttleNormalized(p.base,id,v);
    if(!std::isfinite(v)||v<0||v>1)return false;
    p.stagger=static_cast<uint16_t>(std::floor(v*1000.+.5));return true;
}
template<unsigned N> inline bool configureHost(PalimpsestShuttle<N>& e,ShuttleHostPatch p) noexcept {
    if(!valid(p))return false;
    return e.configure(p.base)&&e.configureStagger(p.stagger);
}
template<unsigned N> inline ShuttleHostPatch snapshotHost(const PalimpsestShuttle<N>& e) noexcept {
    return {e.patch(),static_cast<uint16_t>(e.stagger())};
}
}
