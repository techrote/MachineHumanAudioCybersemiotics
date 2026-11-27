#pragma once
#include "resolution_host.hpp"
#include "random_receipt.hpp"
namespace mhac::receipt::balanced_host {
namespace e=extended;
namespace z=randomized;
constexpr unsigned firstID=e::firstID,count=12;
using e::Action;using e::Contract;using e::Wet;using e::Bypass;using e::Resolution;
using e::Budget;using e::FineA;using e::FineB;using e::FineSource;
enum Extra : unsigned { Balanced=9, Epoch, Seed };
struct Patch : e::Patch { bool balanced=false; unsigned epoch=25,seed=0; };
inline bool valid(const Patch& p) noexcept {return e::valid(p)&&p.epoch>=5&&p.epoch<=1000&&p.seed<=65535;}
inline double normalized(const Patch& p,unsigned id) noexcept {
    if(id<e::count)return e::normalized(p,id);
    switch(id){case Balanced:return p.balanced?1.:0.;case Epoch:return (p.epoch-5)/995.;case Seed:return p.seed/65535.;default:return 0.;}
}
inline bool control(Patch& p,unsigned id,double v) noexcept {
    if(id<e::count)return e::control(p,id,v);
    if(!std::isfinite(v)||id>=count)return false;
    v=std::clamp(v,0.,1.);
    switch(id){case Balanced:p.balanced=v>=.5;break;case Epoch:p.epoch=5+static_cast<unsigned>(std::lround(v*995));break;
    case Seed:p.seed=static_cast<unsigned>(std::lround(v*65535));break;default:return false;}return true;
}
// One 59-bit control word + binary64 wet, little endian RF04.
inline std::uint64_t pack(const Patch& p) noexcept {
    return e::pack(p)|(std::uint64_t(p.balanced)<<32)|(std::uint64_t(p.epoch)<<33)|(std::uint64_t(p.seed)<<43);
}
inline bool unpack(std::uint64_t w,double wet,Patch& p) noexcept {
    Patch q;if((w>>59)||!e::unpack(static_cast<std::uint32_t>(w),wet,q))return false;
    q.balanced=((w>>32)&1)!=0;q.epoch=static_cast<unsigned>((w>>33)&1023);q.seed=static_cast<unsigned>((w>>43)&65535);
    if(!valid(q))return false;
    p=q;return true;
}
using State=std::array<std::uint8_t,20>;
inline State save(const Patch& p) noexcept {
    State s{'R','F','0','4'};const auto w=pack(p);std::uint64_t wet=0;std::memcpy(&wet,&p.legacy.wet,8);
    for(unsigned i=0;i<8;++i){s[4+i]=static_cast<std::uint8_t>(w>>(8*i));s[12+i]=static_cast<std::uint8_t>(wet>>(8*i));}return s;
}
inline bool load(const std::uint8_t* s,std::size_t n,Patch& p) noexcept {
    if(!s||n<4)return false;
    if(s[3]!='4'){Patch q;if(!e::load(s,n,q))return false;p=q;return true;}
    if(n!=20||s[0]!='R'||s[1]!='F'||s[2]!='0')return false;
    std::uint64_t w=0,b=0;double wet=0;for(unsigned i=0;i<8;++i){w|=std::uint64_t(s[4+i])<<(8*i);b|=std::uint64_t(s[12+i])<<(8*i);}
    std::memcpy(&wet,&b,8);return unpack(w,wet,p);
}
// Single transfer table and wet ramp for both modes: no parallel processing or mode-switch discontinuity.
class Live {
    using Table=std::array<double,256>;
    Patch p_{};resolution::Config c_=e::config(p_);Table start_{},goal_{};
    z::Schedule seq_{};z::Draw draw_{1,false};double rate_=48000,wet_=0;
    unsigned length_=240,left_=0,epoch_=1200,until_=1200;
    double at(unsigned i) const noexcept {return left_?start_[i]+(goal_[i]-start_[i])*(double(length_-left_)/length_):goal_[i];}
    Table table() const noexcept {
        Table t{};const z::Config r{c_.bits,c_.lo,c_.hi,c_.budget,p_.epoch,p_.seed,true,c_.bypass,c_.wet};
        const bool coll=p_.balanced&&z::collision(r,draw_);
        for(unsigned i=0;i<256;++i){unsigned q=i>>(8-c_.bits);
            if(p_.balanced){if(coll&&(q==c_.lo||q==c_.hi))q=draw_.upper?c_.hi:c_.lo;}
            else q=resolution::recover(q,c_);
            t[i]=resolution::amplitude(q,c_.bits);}return t;
    }
    void target() noexcept {const auto t=table();if(t==goal_)return;for(unsigned i=0;i<256;++i)start_[i]=at(i);goal_=t;left_=length_;}
    void restart() noexcept {seq_.reset(c_.bits,p_.seed);draw_=seq_.next();epoch_=static_cast<unsigned>(std::ceil(rate_*p_.epoch*.001));until_=epoch_;}
    double sample(double in) const noexcept {const double x=clean(in);if(x==0||wet_==0)return x;
        const unsigned q=std::min(255u,static_cast<unsigned>((x+1)*128));return clean(x*(1-wet_)+at(q)*wet_);}
public:
    Live() noexcept {reset();}
    bool prepare(double rate) noexcept {if(!std::isfinite(rate)||rate<1000||rate>2000000)return false;
        rate_=rate;length_=static_cast<unsigned>(std::ceil(rate*.005));reset();return true;}
    void reset() noexcept {restart();start_=goal_=table();left_=0;wet_=0;}
    bool apply(const Patch& p) noexcept {
        if(!valid(p))return false;
        const auto c=e::config(p);const bool clock=p.balanced&&(!p_.balanced||p.seed!=p_.seed||p.epoch!=p_.epoch||c.bits!=c_.bits);
        const bool law=clock||p.balanced!=p_.balanced||c.bits!=c_.bits||c.lo!=c_.lo||c.hi!=c_.hi||c.budget!=c_.budget||c.mode!=c_.mode;
        p_=p;c_=c;if(clock)restart();if(law)target();return true;
    }
    template<class T> void frame(T& l,T& r) noexcept {
        if(p_.balanced){if(!until_){draw_=seq_.next();until_=epoch_;target();}--until_;}
        if(left_)--left_;
        const double dest=p_.legacy.bypass?0:p_.legacy.wet,step=1.0/length_;wet_+=std::clamp(dest-wet_,-step,step);
        l=static_cast<T>(sample(l));r=static_cast<T>(sample(r));
    }
};
// Each mailbox has a single writer. Sequentially consistent words, one audio-side read attempt.
class Mailbox {
    static_assert(std::atomic<std::uint64_t>::is_always_lock_free,"64-bit atomics required");
    std::atomic<std::uint64_t> seq_{0},controls_{0},wet_{0},ack_{0};
public:
    struct Snapshot {Patch patch{};std::uint64_t seq=0,ack=0;};
    explicit Mailbox(std::uint64_t ack=0) noexcept {publish(Patch{},ack);}
    void publish(const Patch& p,std::uint64_t ack=0) noexcept {const auto s=seq_.load();seq_.store(s+1);controls_.store(pack(p));
        std::uint64_t w=0;std::memcpy(&w,&p.legacy.wet,8);wet_.store(w);ack_.store(ack);seq_.store(s+2);}
    std::uint64_t acknowledged() const noexcept {return ack_.load();}
    bool read(Snapshot& out) const noexcept {Snapshot s;s.seq=seq_.load();if(s.seq&1u)return false;
        const auto c=controls_.load(),w=wet_.load();s.ack=ack_.load();if(seq_.load()!=s.seq)return false;
        double wet=0;std::memcpy(&wet,&w,8);if(!unpack(c,wet,s.patch))return false;out=s;return true;}
};
class Host {
    Live live_;Patch patch_{};Mailbox requested_,published_{2};std::mutex callers_;
    std::uint64_t applied_=2,lastAck_=2;State last_=save(Patch{});
public:
    bool prepare(double rate) noexcept {return live_.prepare(rate);}
    void reset() noexcept {live_.reset();}
    bool request(const Patch& p){if(!valid(p))return false;const std::lock_guard<std::mutex> lock(callers_);requested_.publish(p);return true;}
    bool snapshot(Patch& p){const std::lock_guard<std::mutex> lock(callers_);Mailbox::Snapshot r,a;if(!requested_.read(r))return false;
        if(published_.acknowledged()!=r.seq){p=r.patch;return true;}
        for(unsigned i=0;i<64;++i)if(published_.read(a)){p=a.ack==r.seq?a.patch:r.patch;return true;}
        return false;}
    void begin() noexcept {Mailbox::Snapshot r;if(requested_.read(r)&&r.seq!=applied_){apply(r.patch);applied_=r.seq;}}
    void end() noexcept {const auto p=save(patch_);if(p!=last_||applied_!=lastAck_){published_.publish(patch_,applied_);last_=p;lastAck_=applied_;}}
    bool apply(const Patch& p) noexcept {if(!live_.apply(p))return false;patch_=p;return true;}
    bool set(unsigned id,double v) noexcept {auto p=patch_;return control(p,id,v)&&apply(p);}
    const Patch& patch() const noexcept {return patch_;}
    template<class T> void frame(T& l,T& r) noexcept {live_.frame(l,r);}
};
}
