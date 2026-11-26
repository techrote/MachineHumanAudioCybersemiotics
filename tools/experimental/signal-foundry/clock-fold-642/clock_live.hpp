#pragma once
#include "clock.hpp"
#include "quality/resampler.hpp"
#include <memory>
#include <new>
#include <cstdint>
#include <cstring>
#include <limits>

namespace mhac::clock_fold {
enum Parameter : unsigned { Drift, Curvature, Compensation, Wet, Edge, Bypass, Quality, Count };
constexpr unsigned firstID=1400;
using Normalized=std::array<double,Count>;
inline constexpr Normalized defaults{.5,.5,0,1,.12,0,0};
using State=std::array<std::uint8_t,4+8*Count>;
static_assert(sizeof(double)==8 && std::numeric_limits<double>::is_iec559,"binary64 required");
inline bool valid(const Normalized& p) noexcept {
    for(double v:p) if(!std::isfinite(v)||v<0||v>1)return false;
    return true;
}
inline Controls controls(const Normalized& p) noexcept {
    Controls c; c.drift=p[Drift]-.5;c.curvature=p[Curvature]-.5;
    c.compensation=p[Compensation];c.wet=p[Wet];c.edge=p[Edge]*.25;c.bypass=p[Bypass]>=.5;
    return c;
}
inline State encode(const Normalized& p) noexcept {
    State s{'C','F','0','2'};
    for(unsigned i=0;i<Count;++i){std::uint64_t bits=0;std::memcpy(&bits,&p[i],8);
        for(unsigned b=0;b<8;++b)s[4+8*i+b]=static_cast<std::uint8_t>(bits>>(8*b));}
    return s;
}
inline bool decode(const std::uint8_t* s,std::size_t n,Normalized& p) noexcept {
    if(!s||n<4||s[0]!='C'||s[1]!='F'||s[2]!='0')return false;
    const unsigned count=s[3]=='1'?6u:s[3]=='2'?unsigned(Count):0u;
    if(!count||n!=4+8*count)return false;
    Normalized q=defaults;
    for(unsigned i=0;i<count;++i){std::uint64_t bits=0;
        for(unsigned b=0;b<8;++b)bits|=std::uint64_t(s[4+8*i+b])<<(8*b);
        std::memcpy(&q[i],&bits,8);}
    if(!valid(q))return false;
    p=q;return true;
}
// Single audio-thread owner; restore/reset only while processing is stopped.
class Live {
    Engine engine_;
    std::unique_ptr<quality::KernelBank> bank_;
    Normalized p_=defaults;
    Controls c_=controls(defaults);
public:
    bool prepare(double rate) noexcept {
        if(!std::isfinite(rate)||rate<1000||rate>2000000)return false;
        if(!bank_){bank_.reset(new(std::nothrow) quality::KernelBank);if(!bank_)return false;bank_->prepare();}
        return engine_.prepare(rate);
    }
    void reset() noexcept {engine_.reset();}
    const Normalized& params() const noexcept {return p_;}
    bool set(unsigned id,double v) noexcept {
        if(id>=Count||!std::isfinite(v)||v<0||v>1)return false;
        p_[id]=v;c_=controls(p_);return true;
    }
    bool restore(const Normalized& p) noexcept {
        if(!valid(p))return false;
        p_=p;c_=controls(p_);reset();return true;
    }
    Stereo step(double l,double r) noexcept {
        return engine_.tickWith({l,r},c_,bank_&&p_[Quality]>=.5,
            [this](const auto& frame,const Plan& plan,std::size_t pos){return bank_->render(frame,plan,pos,true);});
    }
};
}
