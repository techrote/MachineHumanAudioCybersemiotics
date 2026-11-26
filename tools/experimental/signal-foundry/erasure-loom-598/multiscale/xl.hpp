#pragma once
#include "scales.hpp"
#include "../live2.hpp"
namespace loomxl {
using namespace loom;
using loom2::Separation; using loom2::Rotation; using loom2::Budget;
using loom2::Repair; using loom2::Wet; using loom2::Gain; using loom2::Bypass;
using loom2::Probe; using loom2::Edge;
inline constexpr unsigned Scale=loom2::Count, Count=Scale+1;
inline constexpr unsigned latency=loomscale::latency, tail=loomscale::tail;
using Normalized=std::array<double,Count>;
inline constexpr Normalized defaults{1,0,1./15,1,.5,1,0,0,0,0};
using State=std::array<std::uint8_t,4+8*Count>;
inline State encode(const Normalized& p) noexcept {
    State b{'E','X','0','1'};
    for(unsigned i=0;i<Count;++i){std::uint64_t u=0;std::memcpy(&u,&p[i],8);for(unsigned j=0;j<8;++j)b[4+8*i+j]=std::uint8_t(u>>(8*j));}
    return b;
}
inline bool decode(const std::uint8_t* b,std::size_t n,Normalized& out) noexcept {
    if(!b||n!=State{}.size()||b[0]!='E'||b[1]!='X'||b[2]!='0'||b[3]!='1')return false;
    Normalized p{};
    for(unsigned i=0;i<Count;++i){std::uint64_t u=0;for(unsigned j=0;j<8;++j)u|=std::uint64_t(b[4+8*i+j])<<(8*j);std::memcpy(&p[i],&u,8);if(!std::isfinite(p[i])||p[i]<0||p[i]>1)return false;}
    out=p;return true;
}
class Live {
    loomscale::Engine engine; Normalized values=defaults;
    void sync() noexcept {
        engine.set({{1u+unsigned(std::lround(values[Separation]*3)),unsigned(std::lround(values[Rotation]*8)),1+15*values[Budget],values[Repair],values[Wet],values[Gain],values[Bypass]>=.5},values[Probe],values[Edge]},unsigned(std::lround(values[Scale]*2)));
    }
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
