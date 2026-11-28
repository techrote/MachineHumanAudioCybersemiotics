#pragma once
#include "escape_release.hpp"
#include <atomic>
namespace mhac::orbit::host {
constexpr unsigned firstID=1810, count=7;
constexpr std::uint64_t pending=std::uint64_t(1)<<63;
inline std::uint64_t pack(Patch p) noexcept {
    return p.blend|(p.releaseMs<<10)|(unsigned(p.cents+100)<<20)|(p.releaseMode<<28)|(std::uint64_t(p.spectralDepth)<<30)|(std::uint64_t(p.sustainDepth)<<40)|(std::uint64_t(p.sustainMs-200)<<50);
}
inline Patch unpack(std::uint64_t w) noexcept {
    return {unsigned(w&1023u),unsigned((w>>10)&1023u),int((w>>20)&255u)-100,unsigned((w>>28)&3u),unsigned((w>>30)&1023u),unsigned((w>>40)&1023u),200u+unsigned((w>>50)&8191u)};
}
inline double normalized(Patch p,unsigned i) noexcept {
    return i==0?p.blend/1000.:i==1?(p.releaseMs-10)/990.:i==2?(p.cents+100)/200.:i==3?p.releaseMode/2.:i==4?p.spectralDepth/1000.:i==5?p.sustainDepth/1000.:(p.sustainMs-200)/7800.;
}
class Live {
    struct Key {int id=-1,channel=0,pitch=0;bool released=false;};
    std::array<Key,8> keys_{};
    Engine engine_; escape::Route fixed_; escape::PhaseBank phases_;
    static bool matches(Key k,int id,int channel,int pitch) noexcept {
        return id>=0?k.id==id:k.id<0&&k.channel==channel&&k.pitch==pitch;
    }
    // Each key has at most one held voice, but may have older tails.
    // Prefer the held voice on note-off; repeated offs with no held voice
    // remain idempotent. Explicit IDs may be recycled after note-off.
    std::size_t releaseKey(int id,int channel,int pitch) const noexcept {
        std::size_t tail=keys_.size();
        for(std::size_t i=0;i<keys_.size();++i)if(engine_.noteActive(int(i))&&matches(keys_[i],id,channel,pitch)){
            if(!keys_[i].released)return i;
            if(tail==keys_.size())tail=i;
        }
        return tail;
    }
public:
    bool prepare(double rate) noexcept {if(!validSampleRate(rate)||!fixed_.prepare()||!phases_.prepare()||!engine_.prepare(rate))return false;keys_={};return true;}
    void reset() noexcept {engine_.reset();keys_={};}
    Patch patch() const noexcept {return engine_.patch();}
    bool setPatch(Patch p) noexcept {return engine_.setPatch(p);}
    bool parameter(unsigned i,double value) noexcept {
        if(i>=count||!std::isfinite(value))return false;
        value=std::clamp(value,0.,1.);auto p=patch();
        if(i==0)p.blend=unsigned(std::lround(value*1000.));
        else if(i==1)p.releaseMs=10u+unsigned(std::lround(value*990.));
        else if(i==2)p.cents=int(std::lround(value*200.))-100;
        else if(i==3)p.releaseMode=unsigned(std::lround(value*2.));
        else if(i==4)p.spectralDepth=unsigned(std::lround(value*1000.));
        else if(i==5)p.sustainDepth=unsigned(std::lround(value*1000.));
        else p.sustainMs=200u+unsigned(std::lround(value*7800.));
        return setPatch(p);
    }
    bool off(int id,int channel,int pitch) noexcept {
        if(id< -1||channel<0||channel>15||pitch<0||pitch>127)return false;
        const auto i=releaseKey(id,channel,pitch);
        if(i==keys_.size())return false;
        bool ok=false;
        if(patch().releaseMode==1)ok=engine_.noteOffShaped(int(i),fixed_.gain,escape::steps,patch().spectralDepth/1000.);
        else if(patch().releaseMode==2){const auto& route=phases_.route(escape::PhaseBank::phaseIndex(engine_.notePhase(int(i))));ok=engine_.noteOffShaped(int(i),route.gain,route.length,patch().spectralDepth/1000.);}
        else ok=engine_.noteOff(int(i));
        if(ok)keys_[i].released=true;
        return ok;
    }
    // Experimental native-only note-off. No changes to state or VST3 IDs.
    bool offSpectral(int id,int channel,int pitch,double depth) noexcept {
        if(id< -1||channel<0||channel>15||pitch<0||pitch>127||!std::isfinite(depth)||depth<0.||depth>1.)return false;
        const auto i=releaseKey(id,channel,pitch);
        if(i==keys_.size())return false;
        const auto& route=phases_.route(escape::PhaseBank::phaseIndex(engine_.notePhase(int(i))));
        const bool ok=engine_.noteOffShaped(int(i),route.gain,route.length,depth);
        if(ok)keys_[i].released=true;
        return ok;
    }
    bool on(int id,int channel,int pitch,double tuning,double velocity) noexcept {
        if(id< -1||channel<0||channel>15||pitch<0||pitch>127)return false;
        if(velocity==0.)return off(id,channel,pitch);
        for(unsigned i=0;i<keys_.size();++i)if(engine_.noteActive(int(i))&&matches(keys_[i],id,channel,pitch)&&!keys_[i].released)return false;
        for(unsigned i=0;i<keys_.size();++i)if(!engine_.noteActive(int(i))){
            const auto p=patch();const auto& route=phases_.route(unsigned(pitch)%68u);
            if(!engine_.noteOn(int(i),pitch,velocity,tuning,p.sustainDepth?&route.gain:nullptr,route.length,p.sustainDepth/1000.,p.sustainMs))return false;
            keys_[i]={id,channel,pitch,false};return true;
        }
        return false;
    }
    unsigned active() const noexcept {return engine_.active();}
    void tick(double& l,double& r) noexcept {engine_.tick(l,r);}
};
// Single audio-thread consumer. State requests are coherent, last-writer-wins.
// A concurrent request wins over audio publication; no retry loop in begin/end.
class Bridge {
    static_assert(std::atomic<std::uint64_t>::is_always_lock_free,"Lock-free state word required");
    std::atomic<std::uint64_t> word_{pack(Patch{})};
public:
    bool request(Patch p) noexcept {if(!p.valid())return false;word_.store(pack(p)|pending);return true;}
    Patch save() const noexcept {return unpack(word_.load());}
    std::uint64_t begin(Live& e) noexcept {
        auto w=word_.load();if(!(w&pending))return w;
        const auto clean=w&~pending;
        if(!word_.compare_exchange_strong(w,clean))return pending;
        e.setPatch(unpack(clean));return clean;
    }
    void end(std::uint64_t token,const Live& e) noexcept {
        if(!(token&pending))word_.compare_exchange_strong(token,pack(e.patch()));
    }
};
} // namespace mhac::orbit::host
