#pragma once
#include "receipt_live.hpp"
namespace mhac::receipt::resolution {
struct Config {
    unsigned bits=3, lo=1, hi=6, budget=1;
    Mode mode=Mode::preview;
    bool bypass=false;
    double wet=0;
};
inline bool valid(const Config& p) noexcept {
    return p.bits>=3 && p.bits<=8 && p.lo<p.hi && p.hi<(1u<<p.bits) &&
        p.budget<=p.bits && static_cast<unsigned>(p.mode)<4 &&
        std::isfinite(p.wet) && p.wet>=0 && p.wet<=1;
}
// Preconditions: valid config and q < 2^bits. Fixed budget counts low bits.
inline unsigned mask(const Config& p) noexcept {
    const unsigned d=p.lo^p.hi;
    return p.mode==Mode::full?(1u<<p.bits)-1u:p.mode==Mode::preview?(d&(~d+1u)):
        p.mode==Mode::fixed?(1u<<p.budget)-1u:0u;
}
inline unsigned recover(unsigned q,const Config& p) noexcept {
    return q==p.hi && ((p.lo^p.hi)&mask(p))==0?p.lo:q;
}
inline double amplitude(unsigned q,unsigned bits) noexcept {
    const double n=static_cast<double>(1u<<bits);
    return (static_cast<double>(q)+.5)/n-.5;
}
using State=std::array<std::uint8_t,20>;
inline State save(const Config& p) noexcept {
    State b{'R','F','0','2',static_cast<std::uint8_t>(p.bits),static_cast<std::uint8_t>(p.lo),
        static_cast<std::uint8_t>(p.hi),static_cast<std::uint8_t>(p.mode),
        static_cast<std::uint8_t>(p.budget),static_cast<std::uint8_t>(p.bypass),0,0};
    std::uint64_t w=0;std::memcpy(&w,&p.wet,8);
    for(unsigned i=0;i<8;++i)b[12+i]=static_cast<std::uint8_t>(w>>(8*i));
    return b;
}
inline bool load(const std::uint8_t* b,std::size_t n,Config& p) noexcept {
    if(!b)return false;
    if(n==16){Patch old;if(!mhac::receipt::load(b,n,old))return false;
        p={3,old.action.lo,old.action.hi,1,old.mode,old.bypass,old.wet};return true;}
    if(n!=20||b[0]!='R'||b[1]!='F'||b[2]!='0'||b[3]!='2'||b[9]>1||b[10]||b[11])return false;
    Config next{b[4],b[5],b[6],b[8],static_cast<Mode>(b[7]),b[9]!=0,0};
    std::uint64_t w=0;for(unsigned i=0;i<8;++i)w|=std::uint64_t(b[12+i])<<(8*i);
    std::memcpy(&next.wet,&w,8);if(!valid(next))return false;p=next;return true;
}
// Fixed finest-grid representation makes transitions across resolutions coherent.
// Audio-thread owned; no allocation. A law change costs at most 256 table entries.
class Live {
    using Table=std::array<double,256>;
    Config p_{};Table start_{},goal_{};
    unsigned length_=240,remaining_=0;double wet_=0;
    static Table table(const Config& p) noexcept {
        Table t{};for(unsigned i=0;i<256;++i)t[i]=amplitude(recover(i>>(8-p.bits),p),p.bits);return t;
    }
    double at(unsigned i) const noexcept {
        return remaining_?start_[i]+(goal_[i]-start_[i])*(double(length_-remaining_)/length_):goal_[i];
    }
    double sample(double in) const noexcept {
        const double x=clean(in);if(x==0||wet_==0)return x;
        const unsigned q=std::min(255u,static_cast<unsigned>((x+1)*128));
        return clean(x*(1-wet_)+at(q)*wet_);
    }
public:
    Live() noexcept {reset();}
    const Config& config() const noexcept{return p_;}
    bool prepare(double rate) noexcept {
        if(!std::isfinite(rate)||rate<1000||rate>2000000)return false;
        length_=static_cast<unsigned>(std::ceil(rate*.005));reset();return true;
    }
    void reset() noexcept {start_=goal_=table(p_);remaining_=0;wet_=0;}
    bool apply(const Config& p) noexcept {
        if(!valid(p))return false;
        if(p.bits!=p_.bits||p.lo!=p_.lo||p.hi!=p_.hi||p.budget!=p_.budget||p.mode!=p_.mode){
            const auto next=table(p);
            if(next!=goal_){for(unsigned i=0;i<256;++i)start_[i]=at(i);goal_=next;remaining_=length_;}
        }
        p_=p;return true;
    }
    template<class T> void frame(T& l,T& r) noexcept {
        if(remaining_)--remaining_;
        const double target=p_.bypass?0:p_.wet,step=1.0/length_;
        wet_+=std::clamp(target-wet_,-step,step);
        l=static_cast<T>(sample(l));r=static_cast<T>(sample(r));
    }
};
}
