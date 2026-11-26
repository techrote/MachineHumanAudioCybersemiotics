#pragma once
#include "balanced_host.hpp"
#include "multi_scheduled.hpp"
namespace mhac::receipt::multi_host {
namespace b=balanced_host;
namespace m=multi;
constexpr unsigned firstID=b::firstID,count=20;
using b::Action;using b::Contract;using b::Wet;using b::Bypass;using b::Resolution;using b::Budget;
using b::FineA;using b::FineB;using b::FineSource;using b::Balanced;using b::Epoch;using b::Seed;
enum Extra : unsigned { Multi=12, MultiBits, Pairs, MultiBudget, MultiContract, MultiEpoch, Geometry, MultiSeed };
struct Patch : b::Patch {
    bool multi=false;
    unsigned multiBits=5,pairs=16,multiBudget=1,multiEpoch=25,geometry=9,multiSeed=42;
    m::Contract multiContract=m::Contract::balanced;
};
inline bool valid(const Patch& p) noexcept {
    return b::valid(p)&&p.multiBits>=3&&p.multiBits<=8&&p.pairs<=128&&p.multiBudget<=8&&
        p.multiEpoch>=5&&p.multiEpoch<=1000&&p.geometry<=65535&&p.multiSeed<=65535&&
        static_cast<unsigned>(p.multiContract)<4;
}
inline m::Config config(const Patch& p) noexcept {
    return {p.multiBits,std::min(p.pairs,1u<<(p.multiBits-1)),std::min(p.multiBudget,p.multiBits),p.multiEpoch,
        p.multiContract,p.geometry,p.multiSeed,p.legacy.bypass,p.legacy.wet};
}
inline double normalized(const Patch& p,unsigned id) noexcept {
    if(id<b::count)return b::normalized(p,id);
    switch(id){case Multi:return p.multi?1.:0.;case MultiBits:return (p.multiBits-3)/5.;case Pairs:return p.pairs/128.;
    case MultiBudget:return p.multiBudget/8.;case MultiContract:return static_cast<unsigned>(p.multiContract)/3.;
    case MultiEpoch:return (p.multiEpoch-5)/995.;case Geometry:return p.geometry/65535.;case MultiSeed:return p.multiSeed/65535.;default:return 0.;}
}
inline bool control(Patch& p,unsigned id,double v) noexcept {
    if(id<b::count)return b::control(p,id,v);
    if(!std::isfinite(v)||id>=count)return false;
    v=std::clamp(v,0.,1.);
    auto scaled=[&](unsigned top){return static_cast<unsigned>(std::lround(v*top));};
    switch(id){case Multi:p.multi=v>=.5;break;case MultiBits:p.multiBits=3+scaled(5);break;case Pairs:p.pairs=scaled(128);break;
    case MultiBudget:p.multiBudget=scaled(8);break;case MultiContract:p.multiContract=static_cast<m::Contract>(scaled(3));break;
    case MultiEpoch:p.multiEpoch=5+scaled(995);break;case Geometry:p.geometry=scaled(65535);break;
    case MultiSeed:p.multiSeed=scaled(65535);break;default:return false;}return true;
}
inline std::uint64_t extra(const Patch& p) noexcept {
    return std::uint64_t(p.multi)|(std::uint64_t(p.multiBits-3)<<1)|(std::uint64_t(p.pairs)<<4)|
        (std::uint64_t(p.multiBudget)<<12)|(std::uint64_t(p.multiContract)<<16)|(std::uint64_t(p.multiEpoch)<<18)|
        (std::uint64_t(p.geometry)<<28)|(std::uint64_t(p.multiSeed)<<44);
}
inline bool unpack(std::uint64_t legacy,std::uint64_t more,double wet,Patch& p) noexcept {
    Patch q;if((more>>60)||!b::unpack(legacy,wet,q))return false;
    q.multi=(more&1)!=0;q.multiBits=3+static_cast<unsigned>((more>>1)&7);q.pairs=static_cast<unsigned>((more>>4)&255);
    q.multiBudget=static_cast<unsigned>((more>>12)&15);q.multiContract=static_cast<m::Contract>((more>>16)&3);
    q.multiEpoch=static_cast<unsigned>((more>>18)&1023);q.geometry=static_cast<unsigned>((more>>28)&65535);
    q.multiSeed=static_cast<unsigned>((more>>44)&65535);if(!valid(q))return false;
    p=q;return true;
}
// RF05: RF04 payload followed by the 60-bit multi control word, all little endian.
using State=std::array<std::uint8_t,28>;
inline State save(const Patch& p) noexcept {
    State s{};const auto old=b::save(p);std::copy(old.begin(),old.end(),s.begin());s[3]='5';const auto w=extra(p);
    for(unsigned i=0;i<8;++i)s[20+i]=static_cast<std::uint8_t>(w>>(8*i));
    return s;
}
inline bool load(const std::uint8_t* s,std::size_t n,Patch& p) noexcept {
    if(!s||n<4)return false;
    Patch q;if(s[3]!='5'){if(!b::load(s,n,q))return false;p=q;return true;}
    if(n!=28||s[0]!='R'||s[1]!='F'||s[2]!='0')return false;
    std::uint64_t legacy=0,wetBits=0,more=0;double wet=0;
    for(unsigned i=0;i<8;++i){legacy|=std::uint64_t(s[4+i])<<(8*i);wetBits|=std::uint64_t(s[12+i])<<(8*i);more|=std::uint64_t(s[20+i])<<(8*i);}
    std::memcpy(&wet,&wetBits,8);return unpack(legacy,more,wet,p);
}
// Both deterministic clocks advance even when their output is not selected.
// The exact endpoints bypass the crossfade arithmetic, retaining legacy samples.
class Live {
    b::Live legacy_;m::Scheduled multi_;Patch patch_{};unsigned length_=240,mix_=0;
    template<class T> T blend(T a,T z) const noexcept {
        if(!mix_||a==z)return a;
        if(mix_==length_)return z;
        const double f=double(mix_)/length_;return static_cast<T>(clean(double(a)*(1-f)+double(z)*f));
    }
public:
    Live() noexcept {apply(patch_);reset();}
    bool prepare(double rate) noexcept {
        if(!std::isfinite(rate)||rate<1000||rate>2000000)return false;
        if(!legacy_.prepare(rate)||!multi_.prepare(rate))return false;
        length_=static_cast<unsigned>(std::ceil(rate*.005));reset();return true;
    }
    void reset() noexcept {legacy_.reset();multi_.reset();mix_=patch_.multi?length_:0;}
    bool apply(const Patch& p) noexcept {
        if(!valid(p))return false;
        if(!legacy_.apply(p)||!multi_.request(config(p)))return false;
        patch_=p;return true;
    }
    template<class T> void frame(T& l,T& r) noexcept {
        T x=l,y=r;legacy_.frame(l,r);multi_.frame(x,y);
        if(patch_.multi){if(mix_<length_)++mix_;}else if(mix_)--mix_;
        l=blend(l,x);r=blend(r,y);
    }
};
class Mailbox {
    static_assert(std::atomic<std::uint64_t>::is_always_lock_free,"64-bit atomics required");
    std::atomic<std::uint64_t> seq_{0},legacy_{0},more_{0},wet_{0},ack_{0};
public:
    struct Snapshot {Patch patch{};std::uint64_t seq=0,ack=0;};
    explicit Mailbox(std::uint64_t ack=0) noexcept {publish(Patch{},ack);}
    void publish(const Patch& p,std::uint64_t ack=0) noexcept {
        const auto s=seq_.load();seq_.store(s+1);legacy_.store(b::pack(p));more_.store(extra(p));
        std::uint64_t w=0;std::memcpy(&w,&p.legacy.wet,8);wet_.store(w);ack_.store(ack);seq_.store(s+2);
    }
    std::uint64_t acknowledged() const noexcept {return ack_.load();}
    bool read(Snapshot& out) const noexcept {
        Snapshot s;s.seq=seq_.load();if(s.seq&1u)return false;
        const auto c=legacy_.load(),mword=more_.load(),w=wet_.load();s.ack=ack_.load();if(seq_.load()!=s.seq)return false;
        double wet=0;std::memcpy(&wet,&w,8);if(!unpack(c,mword,wet,s.patch))return false;out=s;return true;
    }
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
