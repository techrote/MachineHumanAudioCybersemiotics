#pragma once
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <limits>

namespace mhac::freeze {
enum Param : unsigned { Rate, Depth, Mix, Mode, Hold, A, B, C, D, Bypass, Count };
using Params = std::array<double, Count>;
inline constexpr Params defaults{.5,.8,1,0,0,1,.25,.75,.1,0};
enum class Contract { Latch, Pause, Snapshot };
using Bank = std::array<double,4>;
inline double unit(double x) noexcept { return std::isfinite(x) ? std::clamp(x,0.,1.) : 0.; }

// Transport, live bank and observation are deliberately separate.
struct Socket {
    Bank live{}, captured{};
    unsigned slot = 0;
    bool held = false;
    Contract mode = Contract::Latch;
    double latch = 0.;
    void configure(const Bank& bank, bool hold, Contract m) noexcept {
        live = bank;
        // Changing contract during hold starts a new capture at current live phase.
        if (hold && (!held || mode != m)) { captured = live; latch = live[slot]; }
        held = hold; mode = m;
    }
    double token() const noexcept {
        if (!held || mode == Contract::Pause) return live[slot];
        return mode == Contract::Latch ? latch : captured[slot];
    }
    bool paused() const noexcept { return held && mode == Contract::Pause; }
    void tick() noexcept { if (!paused()) slot = (slot+1u)%4u; }
};

// State is fixed size: ASCII MHFZ, version 1, ten little-endian 32-bit
// millionths. Presets store parameters only, not transport or capture history.
using State = std::array<std::uint8_t,8+4*Count>;
inline void put(State& a,unsigned offset,std::uint32_t x) noexcept {
    for(unsigned j=0;j<4;++j) a[offset+j]=static_cast<std::uint8_t>(x>>(8*j));
}
inline std::uint32_t get(const State& a,unsigned offset) noexcept {
    std::uint32_t x=0; for(unsigned j=0;j<4;++j) x|=std::uint32_t(a[offset+j])<<(8*j); return x;
}
inline State encode(const Params& p) noexcept {
    State a{'M','H','F','Z'}; put(a,4,1);
    for(unsigned i=0;i<Count;++i) put(a,8+4*i,static_cast<std::uint32_t>(std::lround(unit(p[i])*1000000.)));
    return a;
}
inline bool decode(const State& a,Params& p) noexcept {
    if(a[0]!='M'||a[1]!='H'||a[2]!='F'||a[3]!='Z'||get(a,4)!=1) return false;
    Params tmp{};
    for(unsigned i=0;i<Count;++i){auto v=get(a,8+4*i);if(v>1000000u)return false;tmp[i]=v/1000000.;}
    p=tmp;return true;
}

class Engine {
    Params p_=defaults;
    Socket socket_{};
    double sr_=48000., fraction_=0., increment_=0., gain_=1., slew_=1./240.;
    void updateRate() noexcept { increment_=.25*std::exp2(6*p_[Rate])/sr_; }
public:
    Engine() noexcept { reset(48000.); }
    void reset(double sr) noexcept {
        sr_=(std::isfinite(sr)&&sr>=1000.&&sr<=768000.)?sr:48000.;
        socket_={};fraction_=0.;gain_=1.;slew_=std::min(1.,200./sr_);updateRate();
    }
    const Params& params() const noexcept { return p_; }
    void set(unsigned id,double value) noexcept {
        if(id>=Count||!std::isfinite(value))return;
        const double v=unit(value);
        if(p_[id]==v)return;
        p_[id]=v;if(id==Rate)updateRate();
    }
    void restore(const Params& p) noexcept { for(unsigned i=0;i<Count;++i)set(i,p[i]); reset(sr_); }
    unsigned slot() const noexcept { return socket_.slot; }
    double token() const noexcept { return socket_.token(); }
    double gain() const noexcept { return gain_; }
    // Apply ALL events at a given sample before calling nextGain exactly once.
    // One shared control clock for mono/stereo; no per-channel phase drift.
    double nextGain() noexcept {
        socket_.configure({p_[A],p_[B],p_[C],p_[D]},p_[Hold]>=.5,
                          static_cast<Contract>(static_cast<unsigned>(p_[Mode]*2.+.5)));
        const double target=p_[Bypass]>=.5?1.:1.-p_[Depth]*p_[Mix]*(1.-socket_.token());
        gain_+=std::clamp(target-gain_,-slew_,slew_);
        gain_=std::clamp(gain_,0.,1.);
        if(!socket_.paused()) {
            fraction_+=increment_;
            if(fraction_>=1.-1e-12){fraction_=std::max(0.,fraction_-1.);socket_.tick();}
        }
        return gain_;
    }
    template<class T> static T apply(T sample,double gain) noexcept {
        if(!std::isfinite(sample)||std::abs(sample)<std::numeric_limits<T>::min())return T(0);
        const T out=static_cast<T>(sample*gain);
        return std::abs(out)<std::numeric_limits<T>::min()?T(0):out;
    }
};
}
