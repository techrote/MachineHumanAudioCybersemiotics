#pragma once
#include "resonator.hpp"
#include <atomic>

namespace mhac::counterfactual::host {
// Host-independent normalized parameter contract. Pulse is never serialized.
constexpr unsigned firstID=1900;
enum Parameter : unsigned { Frequency, Wet, Gain, Monitor, Erase, Bypass, Pulse, Count };
inline double normalized(Controls c,unsigned id) noexcept {
    switch(id){
    case Frequency:return (c.hz-40)/5960.0;
    case Wet:return c.wet/1000.0;
    case Gain:return c.gain/1000.0;
    case Monitor:return c.monitor/2.0;
    case Erase:return c.erase?1:0;
    case Bypass:return c.bypass?1:0;
    default:return 0;
    }
}
inline bool change(Controls& c,unsigned id,double v) noexcept {
    if(!std::isfinite(v)||id>=Pulse)return false;
    v=std::clamp(v,0.0,1.0);
    switch(id){
    case Frequency:c.hz=static_cast<std::uint16_t>(40+std::lround(v*5960));break;
    case Wet:c.wet=static_cast<std::uint16_t>(std::lround(v*1000));break;
    case Gain:c.gain=static_cast<std::uint16_t>(std::lround(v*1000));break;
    case Monitor:c.monitor=static_cast<std::uint8_t>(std::lround(v*2));break;
    case Erase:c.erase=v>=0.5;break;
    case Bypass:c.bypass=v>=0.5;break;
    default:return false;
    }
    return true;
}
// Pack all persistent parameters into one lock-free atomic word. Zero is a
// mailbox sentinel, impossible for a valid configuration (frequency >= 40).
constexpr std::uint64_t pack(Controls c) noexcept {
    return std::uint64_t(c.hz)|(std::uint64_t(c.wet)<<13)|(std::uint64_t(c.gain)<<23)|
        (std::uint64_t(c.monitor)<<33)|(std::uint64_t(c.erase)<<35)|(std::uint64_t(c.bypass)<<36);
}
constexpr Controls unpack(std::uint64_t w) noexcept {
    return {static_cast<std::uint16_t>(w&8191),static_cast<std::uint16_t>((w>>13)&1023),
        static_cast<std::uint16_t>((w>>23)&1023),static_cast<std::uint8_t>((w>>33)&3),
        bool((w>>35)&1),bool((w>>36)&1)};
}
static_assert(std::atomic<std::uint64_t>::is_always_lock_free,"requires lock-free 64-bit atomic state");
class Host {
    Processor dsp_{};
    Controls current_{};
    bool pulse_=false;
    std::atomic<std::uint64_t> requested_{0}, published_{pack(Controls{})};
public:
    // Called only while the audio thread is stopped, like prepare/reset.
    bool prepare(double rate) noexcept { if(!dsp_.prepare(rate))return false;reset();return true; }
    void reset() noexcept { begin();dsp_.reset();pulse_=false;end(); }
    // Non-audio thread: last complete request wins; no live DSP mutation.
    bool request(Controls c) noexcept {
        if(!valid(c))return false;
        requested_.store(pack(c),std::memory_order_release);return true;
    }
    bool request(const Patch& p) noexcept { Controls c;return decode(p,c)&&request(c); }
    // A coherent completed-block snapshot, or a not-yet-admitted preset.
    Controls snapshot() const noexcept {
        const auto next=requested_.load(std::memory_order_acquire);
        return unpack(next?next:published_.load(std::memory_order_acquire));
    }
    Patch save() const noexcept {return encode(snapshot());}
    // Audio-thread lifecycle. No spin loops, allocations or blocking calls.
    void begin() noexcept {
        const auto w=requested_.exchange(0,std::memory_order_acq_rel);
        if(w){current_=unpack(w);dsp_.set(current_);}
    }
    void end() noexcept {published_.store(pack(current_),std::memory_order_release);}
    bool parameter(unsigned id,double value) noexcept {
        if(id==Pulse){
            if(!std::isfinite(value))return false;
            const bool high=value>=0.5;
            if(high&&!pulse_)dsp_.requestIntervention();
            pulse_=high;return true;
        }
        if(!change(current_,id,value))return false;
        return dsp_.set(current_);
    }
    template<class Sample> void frame(Sample& l,Sample& r) noexcept {
        const auto s=dsp_.process(l,r);l=static_cast<Sample>(s.left);r=static_cast<Sample>(s.right);
    }
    Controls current() const noexcept {return current_;} // audio thread only
    std::uint64_t interventions() const noexcept {return dsp_.interventions();}
    std::uint64_t ticks() const noexcept {return dsp_.ticks();}
};
} // namespace mhac::counterfactual::host
