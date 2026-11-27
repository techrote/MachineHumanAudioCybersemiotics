#pragma once
#include "orbit.hpp"
#include <atomic>
namespace mhac::orbit::host {
constexpr unsigned firstID=1810, count=3;
constexpr std::uint32_t pending=1u<<31;
inline std::uint32_t pack(Patch p) noexcept {
    return p.blend|(p.releaseMs<<10)|(unsigned(p.cents+100)<<20);
}
inline Patch unpack(std::uint32_t w) noexcept {
    return {w&1023u,(w>>10)&1023u,int((w>>20)&1023u)-100};
}
inline double normalized(Patch p,unsigned i) noexcept {
    return i==0?p.blend/1000.:i==1?(p.releaseMs-10)/990.:(p.cents+100)/200.;
}
class Live {
    struct Key {int id=-1,channel=0,pitch=0;};
    std::array<Key,8> keys_{};
    Engine engine_;
    static bool matches(Key k,int id,int channel,int pitch) noexcept {
        return id>=0?k.id==id:k.id<0&&k.channel==channel&&k.pitch==pitch;
    }
public:
    bool prepare(double rate) noexcept {if(!engine_.prepare(rate))return false;keys_={};return true;}
    void reset() noexcept {engine_.reset();keys_={};}
    Patch patch() const noexcept {return engine_.patch();}
    bool setPatch(Patch p) noexcept {return engine_.setPatch(p);}
    bool parameter(unsigned i,double value) noexcept {
        if(i>=count||!std::isfinite(value))return false;
        value=std::clamp(value,0.,1.);auto p=patch();
        if(i==0)p.blend=unsigned(std::lround(value*1000.));
        else if(i==1)p.releaseMs=10u+unsigned(std::lround(value*990.));
        else p.cents=int(std::lround(value*200.))-100;
        return setPatch(p);
    }
    bool off(int id,int channel,int pitch) noexcept {
        if(id< -1||channel<0||channel>15||pitch<0||pitch>127)return false;
        for(unsigned i=0;i<keys_.size();++i)if(engine_.noteActive(int(i))&&matches(keys_[i],id,channel,pitch))return engine_.noteOff(int(i));
        return false;
    }
    bool on(int id,int channel,int pitch,double tuning,double velocity) noexcept {
        if(id< -1||channel<0||channel>15||pitch<0||pitch>127)return false;
        if(velocity==0.)return off(id,channel,pitch);
        for(unsigned i=0;i<keys_.size();++i)if(engine_.noteActive(int(i))&&matches(keys_[i],id,channel,pitch))return false;
        for(unsigned i=0;i<keys_.size();++i)if(!engine_.noteActive(int(i))){
            if(!engine_.noteOn(int(i),pitch,velocity,tuning))return false;
            keys_[i]={id,channel,pitch};return true;
        }
        return false;
    }
    unsigned active() const noexcept {return engine_.active();}
    void tick(double& l,double& r) noexcept {engine_.tick(l,r);}
};
// Single audio-thread consumer. State requests are coherent, last-writer-wins.
// A concurrent request wins over audio publication; no retry loop in begin/end.
class Bridge {
    static_assert(std::atomic<std::uint32_t>::is_always_lock_free,"Lock-free state word required");
    std::atomic<std::uint32_t> word_{pack(Patch{})};
public:
    bool request(Patch p) noexcept {if(!p.valid())return false;word_.store(pack(p)|pending);return true;}
    Patch save() const noexcept {return unpack(word_.load());}
    std::uint32_t begin(Live& e) noexcept {
        auto w=word_.load();if(!(w&pending))return w;
        const auto clean=w&~pending;
        if(!word_.compare_exchange_strong(w,clean))return pending;
        e.setPatch(unpack(clean));return clean;
    }
    void end(std::uint32_t token,const Live& e) noexcept {
        if(!(token&pending))word_.compare_exchange_strong(token,pack(e.patch()));
    }
};
} // namespace mhac::orbit::host
