#pragma once
#include "receipt_live.hpp"
#include <atomic>
#include <mutex>
namespace mhac::receipt {
constexpr unsigned firstID=1700, count=4;
enum Control : unsigned { Action, Contract, Wet, Bypass };
inline Pair unrank(unsigned rank) noexcept {
    for(unsigned l=0;l<7;++l)for(unsigned h=l+1;h<8;++h)if(rank--==0)return {l,h};
    return {1,6};
}
inline unsigned rank(Pair p) noexcept {
    unsigned n=0;for(unsigned l=0;l<7;++l)for(unsigned h=l+1;h<8;++h,++n)if(p.lo==l&&p.hi==h)return n;
    return 11;
}
inline double normalized(const Patch& p,unsigned id) noexcept {
    switch(id){case Action:return rank(p.action)/27.;case Contract:return static_cast<unsigned>(p.mode)/3.;case Wet:return p.wet;case Bypass:return p.bypass?1.:0.;default:return 0.;}
}
inline bool control(Patch& p,unsigned id,double v) noexcept {
    if(!std::isfinite(v)||id>=count)return false;
    v=std::clamp(v,0.,1.);
    switch(id){case Action:p.action=unrank(static_cast<unsigned>(std::lround(v*27)));break;
    case Contract:p.mode=static_cast<Mode>(std::lround(v*3));break;case Wet:p.wet=v;break;case Bypass:p.bypass=v>=.5;break;}
    return true;
}
// Single writer per mailbox; all words sequentially consistent. One read attempt.
class Mailbox {
    static_assert(std::atomic<std::uint64_t>::is_always_lock_free,"64-bit atomics required");
    std::atomic<std::uint64_t> seq_{0}, controls_{0}, wet_{0}, ack_{0};
public:
    struct Snapshot {Patch patch{};std::uint64_t seq=0,ack=0;};
    explicit Mailbox(std::uint64_t ack=0) noexcept {publish(Patch{},ack);}
    void publish(const Patch& p,std::uint64_t ack=0) noexcept {
        const auto s=seq_.load();seq_.store(s+1);
        controls_.store(rank(p.action)|(static_cast<unsigned>(p.mode)<<5)|(static_cast<unsigned>(p.bypass)<<7));
        std::uint64_t bits=0;std::memcpy(&bits,&p.wet,8);wet_.store(bits);ack_.store(ack);seq_.store(s+2);
    }
    std::uint64_t acknowledged() const noexcept {return ack_.load();}
    bool read(Snapshot& out) const noexcept {
        Snapshot s;s.seq=seq_.load();if(s.seq&1u)return false;
        const auto c=controls_.load(),w=wet_.load();s.ack=ack_.load();
        if(seq_.load()!=s.seq)return false;
        s.patch.action=unrank(static_cast<unsigned>(c&31));s.patch.mode=static_cast<Mode>((c>>5)&3);s.patch.bypass=(c&128)!=0;
        std::memcpy(&s.patch.wet,&w,8);out=s;return true;
    }
};
class Host {
    Live live_; Mailbox requested_,published_{2}; std::mutex callers_;
    std::uint64_t applied_=2,lastAck_=2; State last_=receipt::save(Patch{});
public:
    // Lifecycle calls are serialized by host with processing.
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
    void begin() noexcept {Mailbox::Snapshot r;if(requested_.read(r)&&r.seq!=applied_){live_.apply(r.patch);applied_=r.seq;}}
    void end() noexcept {const auto p=receipt::save(live_.patch());if(p!=last_||applied_!=lastAck_){published_.publish(live_.patch(),applied_);last_=p;lastAck_=applied_;}}
    bool apply(const Patch& p) noexcept {return live_.apply(p);}
    bool set(unsigned id,double v) noexcept {auto p=live_.patch();return control(p,id,v)&&live_.apply(p);}
    const Patch& patch() const noexcept {return live_.patch();} // audio owner only
    template<class T> void frame(T& l,T& r) noexcept {live_.frame(l,r);}
};
}
