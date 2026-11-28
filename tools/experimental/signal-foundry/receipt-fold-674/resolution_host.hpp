#pragma once
#include "host.hpp"
#include "resolution.hpp"

namespace mhac::receipt::extended {
constexpr unsigned firstID=receipt::firstID, count=9;
enum Control : unsigned { Action, Contract, Wet, Bypass, Resolution, Budget, FineA, FineB, FineSource };
// The legacy rank never changes meaning. Fine endpoints are a separate opt-in,
// fixed 256-grid coordinate system, even when the active alphabet is smaller.
struct Patch {
    receipt::Patch legacy{};
    unsigned bits=3, budget=1, a=32, b=192;
    bool fine=false;
};
inline bool valid(const Patch& p) noexcept {
    return receipt::valid(p.legacy)&&p.bits>=3&&p.bits<=8&&p.budget<=8&&p.a<=255&&p.b<=255;
}
inline resolution::Config config(const Patch& p) noexcept {
    const unsigned n=1u<<p.bits, scale=n/8;
    unsigned lo=p.legacy.action.lo*scale, hi=p.legacy.action.hi*scale;
    if(p.fine){lo=std::min(p.a,p.b)>>(8-p.bits);hi=std::max(p.a,p.b)>>(8-p.bits);
        if(lo==hi){if(hi+1<n)++hi;else --lo;}}
    return {p.bits,lo,hi,std::min(p.budget,p.bits),p.legacy.mode,p.legacy.bypass,p.legacy.wet};
}
inline double normalized(const Patch& p,unsigned id) noexcept {
    if(id<4)return receipt::normalized(p.legacy,id);
    switch(id){case Resolution:return (p.bits-3)/5.;case Budget:return p.budget/8.;
        case FineA:return p.a/255.;case FineB:return p.b/255.;case FineSource:return p.fine?1.:0.;default:return 0.;}
}
inline bool control(Patch& p,unsigned id,double v) noexcept {
    if(id<4)return receipt::control(p.legacy,id,v);
    if(!std::isfinite(v)||id>=count)return false;
    v=std::clamp(v,0.,1.);
    switch(id){case Resolution:p.bits=3+static_cast<unsigned>(std::lround(v*5));break;
    case Budget:p.budget=static_cast<unsigned>(std::lround(v*8));break;
    case FineA:p.a=static_cast<unsigned>(std::lround(v*255));break;
    case FineB:p.b=static_cast<unsigned>(std::lround(v*255));break;
    case FineSource:p.fine=v>=.5;break;default:return false;}
    return true;
}
inline std::uint32_t pack(const Patch& p) noexcept {
    return receipt::rank(p.legacy.action)|(static_cast<unsigned>(p.legacy.mode)<<5)|
        (static_cast<unsigned>(p.legacy.bypass)<<7)|((p.bits-3)<<8)|(p.budget<<11)|
        (p.a<<15)|(p.b<<23)|(static_cast<std::uint32_t>(p.fine)<<31);
}
inline bool unpack(std::uint32_t w,double wet,Patch& p) noexcept {
    if((w&31u)>=28)return false;
    Patch next;next.legacy={receipt::unrank(w&31u),static_cast<Mode>((w>>5)&3u),(w&128u)!=0,wet};
    next.bits=3+((w>>8)&7u);next.budget=(w>>11)&15u;next.a=(w>>15)&255u;next.b=(w>>23)&255u;next.fine=(w>>31)!=0;
    if(!valid(next))return false;
    p=next;return true;
}
using State=std::array<std::uint8_t,16>;
inline State save(const Patch& p) noexcept {
    State b{'R','F','0','3'};const auto w=pack(p);std::uint64_t wet=0;std::memcpy(&wet,&p.legacy.wet,8);
    for(unsigned i=0;i<4;++i)b[4+i]=static_cast<std::uint8_t>(w>>(8*i));
    for(unsigned i=0;i<8;++i)b[8+i]=static_cast<std::uint8_t>(wet>>(8*i));
    return b;
}
inline bool load(const std::uint8_t* b,std::size_t n,Patch& p) noexcept {
    if(!b||n<4||b[0]!='R'||b[1]!='F'||b[2]!='0')return false;
    if(b[3]=='1'){Patch next;if(!receipt::load(b,n,next.legacy))return false;p=next;return true;}
    if(b[3]=='2'){resolution::Config c;if(!resolution::load(b,n,c))return false;
        Patch next;next.bits=c.bits;next.budget=c.budget;next.a=c.lo<<(8-c.bits);next.b=c.hi<<(8-c.bits);
        next.fine=c.bits!=3;next.legacy={c.bits==3?Pair{c.lo,c.hi}:Pair{1,6},c.mode,c.bypass,c.wet};p=next;return true;}
    if(b[3]!='3'||n!=16)return false;
    std::uint32_t w=0;std::uint64_t wb=0;double wet=0;
    for(unsigned i=0;i<4;++i)w|=std::uint32_t(b[4+i])<<(8*i);
    for(unsigned i=0;i<8;++i)wb|=std::uint64_t(b[8+i])<<(8*i);
    std::memcpy(&wet,&wb,8);return unpack(w,wet,p);
}
// Same single-writer, bounded-read mailbox discipline as the RF01 bridge.
// Wet stays binary64; no audio-thread mutex, heap or spin retry.
class Mailbox {
    static_assert(std::atomic<std::uint64_t>::is_always_lock_free,"64-bit atomics required");
    std::atomic<std::uint64_t> seq_{0}, controls_{0}, wet_{0}, ack_{0};
public:
    struct Snapshot {Patch patch{};std::uint64_t seq=0,ack=0;};
    explicit Mailbox(std::uint64_t ack=0) noexcept {publish(Patch{},ack);}
    void publish(const Patch& p,std::uint64_t ack=0) noexcept {
        const auto s=seq_.load();seq_.store(s+1);controls_.store(pack(p));
        std::uint64_t w=0;std::memcpy(&w,&p.legacy.wet,8);wet_.store(w);ack_.store(ack);seq_.store(s+2);
    }
    std::uint64_t acknowledged() const noexcept {return ack_.load();}
    bool read(Snapshot& out) const noexcept {
        Snapshot s;s.seq=seq_.load();if(s.seq&1u)return false;
        const auto c=controls_.load(),w=wet_.load();s.ack=ack_.load();
        if(seq_.load()!=s.seq)return false;
        double wet=0;std::memcpy(&wet,&w,8);if(!unpack(static_cast<std::uint32_t>(c),wet,s.patch))return false;
        out=s;return true;
    }
};
class Host {
    resolution::Live live_; Patch patch_{};Mailbox requested_,published_{2};std::mutex callers_;
    std::uint64_t applied_=2,lastAck_=2;State last_=extended::save(Patch{});
public:
    bool prepare(double rate) noexcept {return live_.prepare(rate);}
    void reset() noexcept {live_.reset();}
    bool request(const Patch& p) {if(!valid(p))return false;const std::lock_guard<std::mutex> lock(callers_);requested_.publish(p);return true;}
    bool snapshot(Patch& p) {
        const std::lock_guard<std::mutex> lock(callers_);Mailbox::Snapshot r,a;
        if(!requested_.read(r))return false;
        if(published_.acknowledged()!=r.seq){p=r.patch;return true;}
        for(unsigned i=0;i<64;++i)if(published_.read(a)){p=a.ack==r.seq?a.patch:r.patch;return true;}
        return false;
    }
    void begin() noexcept {Mailbox::Snapshot r;if(requested_.read(r)&&r.seq!=applied_){apply(r.patch);applied_=r.seq;}}
    void end() noexcept {const auto p=extended::save(patch_);if(p!=last_||applied_!=lastAck_){published_.publish(patch_,applied_);last_=p;lastAck_=applied_;}}
    bool apply(const Patch& p) noexcept {if(!valid(p)||!live_.apply(config(p)))return false;patch_=p;return true;}
    bool set(unsigned id,double v) noexcept {auto p=patch_;return control(p,id,v)&&apply(p);}
    const Patch& patch() const noexcept {return patch_;}
    template<class T> void frame(T& l,T& r) noexcept {live_.frame(l,r);}
};
}
