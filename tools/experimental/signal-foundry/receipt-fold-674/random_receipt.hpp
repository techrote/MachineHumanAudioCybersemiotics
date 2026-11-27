#pragma once
#include "resolution.hpp"
#include <numeric>
namespace mhac::receipt::randomized {
// Multiplication in GF(2^bits), for bits 3..8. All nonzero multipliers are bijections.
inline unsigned multiply(unsigned x,unsigned a,unsigned bits) noexcept {
    constexpr unsigned poly[]={0xbu,0x13u,0x25u,0x43u,0x83u,0x11bu};
    const unsigned n=1u<<bits;unsigned y=0;
    for(unsigned i=0;i<bits;++i){if(a&1u)y^=x;a>>=1;x<<=1;if(x&n)x^=poly[bits-3];}
    return y;
}
struct Draw {unsigned multiplier;bool upper;};
inline std::uint64_t hash(std::uint64_t x) noexcept {
    x+=0x9e3779b97f4a7c15ull;x=(x^(x>>30))*0xbf58476d1ce4e5b9ull;
    x=(x^(x>>27))*0x94d049bb133111ebull;return x^(x>>31);
}
// Exact finite traversal, not IID: every multiplier/tie pair once per cycle.
class Schedule {
    unsigned count_=14,offset_=0,stride_=1,position_=0;
    std::uint64_t seed_=0,cycle_=0;
    void reorder() noexcept {
        const auto key=hash(seed_^hash(cycle_));
        offset_=static_cast<unsigned>(key%count_);
        stride_=1+static_cast<unsigned>(hash(key)%(count_-1));
        // Bounded search: at worst encounter 1, which is always coprime.
        for(unsigned i=0;i<count_&&std::gcd(stride_,count_)!=1;++i)
            if(++stride_==count_)stride_=1;
    }
public:
    void reset(unsigned bits,std::uint32_t seed) noexcept {
        count_=2*((1u<<bits)-1);position_=0;seed_=seed;cycle_=0;reorder();
    }
    Draw next() noexcept {
        const unsigned i=(offset_+position_*stride_)%count_;
        if(++position_==count_){position_=0;++cycle_;reorder();}
        return {1+i/2,(i&1u)!=0};
    }
};
struct Config {
    unsigned bits=3,lo=1,hi=6,budget=1,epoch_ms=25;
    std::uint32_t seed=0;bool balanced=true,bypass=false;double wet=0;
};
inline bool valid(const Config& p) noexcept {
    return p.bits>=3&&p.bits<=8&&p.lo<p.hi&&p.hi<(1u<<p.bits)&&p.budget<=p.bits&&
        p.epoch_ms>=5&&p.epoch_ms<=1000&&std::isfinite(p.wet)&&p.wet>=0&&p.wet<=1;
}
// Trusted action, exact tag and collapsed state; only collided endpoints are ambiguous.
inline unsigned tag(unsigned x,const Config& p,Draw d) noexcept {
    return multiply(x,p.balanced?d.multiplier:1u,p.bits)&((1u<<p.budget)-1);
}
inline bool collision(const Config& p,Draw d) noexcept {return tag(p.lo,p,d)==tag(p.hi,p,d);}
inline unsigned recover(unsigned q,const Config& p,Draw d) noexcept {
    if((q==p.lo||q==p.hi)&&collision(p,d))return d.upper?p.hi:p.lo;
    return q;
}
using State=std::array<std::uint8_t,24>;
inline State save(const Config& p) noexcept {
    State s{'R','R','0','1',static_cast<std::uint8_t>(p.bits),static_cast<std::uint8_t>(p.lo),
        static_cast<std::uint8_t>(p.hi),static_cast<std::uint8_t>(p.budget),
        static_cast<std::uint8_t>(p.epoch_ms),static_cast<std::uint8_t>(p.epoch_ms>>8),
        static_cast<std::uint8_t>(p.balanced),static_cast<std::uint8_t>(p.bypass)};
    std::uint64_t w=0;std::memcpy(&w,&p.wet,8);
    for(unsigned i=0;i<4;++i)s[12+i]=static_cast<std::uint8_t>(p.seed>>(8*i));
    for(unsigned i=0;i<8;++i)s[16+i]=static_cast<std::uint8_t>(w>>(8*i));
    return s;
}
inline bool load(const std::uint8_t* s,std::size_t n,Config& p) noexcept {
    if(!s||n!=24||s[0]!='R'||s[1]!='R'||s[2]!='0'||s[3]!='1'||s[10]>1||s[11]>1)return false;
    Config q{s[4],s[5],s[6],s[7],unsigned(s[8])+(unsigned(s[9])<<8),0,s[10]!=0,s[11]!=0,0};
    std::uint64_t w=0;for(unsigned i=0;i<4;++i)q.seed|=std::uint32_t(s[12+i])<<(8*i);
    for(unsigned i=0;i<8;++i)w|=std::uint64_t(s[16+i])<<(8*i);
    std::memcpy(&q.wet,&w,8);if(!valid(q))return false;p=q;return true;
}
// Audio-thread-owned. Stereo uses one draw and one clock. Reset replays the seed.
// Fixed tables crossfade the decoded audio levels, not the mathematical receipt.
class Live {
    using Table=std::array<double,256>;
    Config p_{};Schedule seq_{};Draw draw_{1,false};Table start_{},goal_{};
    double rate_=48000,wet_=0;unsigned ramp_=240,left_=0,epoch_=1200,until_=1200;
    double at(unsigned i) const noexcept {
        return left_?start_[i]+(goal_[i]-start_[i])*double(ramp_-left_)/ramp_:goal_[i];
    }
    Table table() const noexcept {
        Table t{};const bool c=collision(p_,draw_);
        for(unsigned i=0;i<256;++i){unsigned q=i>>(8-p_.bits);
            if(c&&(q==p_.lo||q==p_.hi))q=draw_.upper?p_.hi:p_.lo;
            t[i]=resolution::amplitude(q,p_.bits);}
        return t;
    }
    void target() noexcept {
        const auto t=table();if(t==goal_)return;
        for(unsigned i=0;i<256;++i)start_[i]=at(i);
        goal_=t;left_=ramp_;
    }
    void restart() noexcept {
        seq_.reset(p_.bits,p_.seed);draw_=seq_.next();
        epoch_=static_cast<unsigned>(std::ceil(rate_*p_.epoch_ms*.001));until_=epoch_;
    }
    double sample(double in) const noexcept {
        const double x=clean(in);if(x==0||wet_==0)return x;
        const unsigned q=std::min(255u,static_cast<unsigned>((x+1)*128));
        return clean(x*(1-wet_)+at(q)*wet_);
    }
public:
    Live() noexcept {reset();}
    bool prepare(double rate) noexcept {
        if(!std::isfinite(rate)||rate<1000||rate>2000000)return false;
        rate_=rate;ramp_=static_cast<unsigned>(std::ceil(rate*.005));reset();return true;
    }
    void reset() noexcept {restart();start_=goal_=table();left_=0;wet_=0;}
    const Config& config() const noexcept{return p_;}
    bool apply(const Config& p) noexcept {
        if(!valid(p))return false;
        const bool clock=p.bits!=p_.bits||p.seed!=p_.seed||p.epoch_ms!=p_.epoch_ms;
        const bool law=clock||p.lo!=p_.lo||p.hi!=p_.hi||p.budget!=p_.budget||p.balanced!=p_.balanced;
        p_=p;if(clock)restart();if(law)target();return true;
    }
    template<class T> void frame(T& l,T& r) noexcept {
        if(!until_){draw_=seq_.next();until_=epoch_;target();}
        --until_;if(left_)--left_;
        const double dest=p_.bypass?0:p_.wet,step=1.0/ramp_;
        wet_+=std::clamp(dest-wet_,-step,step);
        l=static_cast<T>(sample(l));r=static_cast<T>(sample(r));
    }
};
}
