#pragma once
#include "probe.hpp"
#include <cstdint>
#include <cstring>
#include <limits>
namespace loom2 {
using namespace loom;
enum Control : unsigned { Separation, Rotation, Budget, Repair, Wet, Gain, Bypass, Probe, Edge, Count };
using Normalized=std::array<double,Count>;
inline constexpr Normalized defaults{1,0,1./15,1,.5,1,0,0,0};
using State=std::array<std::uint8_t,4+8*Count>;
static_assert(sizeof(double)==8 && std::numeric_limits<double>::is_iec559,"EL02 requires IEEE binary64");
inline State encode(const Normalized& p) noexcept {
    State b{'E','L','0','2'};
    for(unsigned i=0;i<Count;++i){std::uint64_t u=0;std::memcpy(&u,&p[i],8);for(unsigned j=0;j<8;++j)b[4+8*i+j]=std::uint8_t(u>>(8*j));}
    return b;
}
inline bool decode(const std::uint8_t* b,std::size_t n,Normalized& out) noexcept {
    if(!b||n<4||b[0]!='E'||b[1]!='L'||b[2]!='0')return false;
    const unsigned count=b[3]=='1'?7u:b[3]=='2'?unsigned(Count):0u;
    if(!count||n!=4+8*count)return false;
    Normalized p=defaults;
    for(unsigned i=0;i<count;++i){std::uint64_t u=0;for(unsigned j=0;j<8;++j)u|=std::uint64_t(b[4+8*i+j])<<(8*j);std::memcpy(&p[i],&u,8);if(!std::isfinite(p[i])||p[i]<0||p[i]>1)return false;}
    out=p;return true;
}
class Live {
    ProbeEngine engine; Normalized values=defaults;
    void sync() noexcept {engine.set({{1u+unsigned(std::lround(values[Separation]*3)),unsigned(std::lround(values[Rotation]*8)),1+15*values[Budget],values[Repair],values[Wet],values[Gain],values[Bypass]>=.5},values[Probe],values[Edge]});}
public:
    Live() noexcept {sync();}
    bool prepare(double rate) noexcept {return engine.prepare(rate);}
    void reset() noexcept {engine.reset();}
    const Normalized& params() const noexcept {return values;}
    void set(unsigned id,double v) noexcept {if(id>=Count||!std::isfinite(v))return;values[id]=unit(v,values[id]);sync();}
    bool restore(const Normalized& p) noexcept {for(double v:p)if(!std::isfinite(v)||v<0||v>1)return false;values=p;sync();return true;}
    Stereo step(double l,double r) noexcept {return engine.step(l,r);}
};
}
