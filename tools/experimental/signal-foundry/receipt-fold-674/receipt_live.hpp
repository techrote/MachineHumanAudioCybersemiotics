#pragma once
#include "receipt_fold.hpp"
#include <array>
#include <cstring>
#include <limits>
namespace mhac::receipt {
struct Patch {
    Pair action{1,6}; Mode mode=Mode::preview; bool bypass=false; double wet=0;
};
inline bool valid(const Patch& p) noexcept {
    return p.action.lo<p.action.hi && p.action.hi<8 && static_cast<unsigned>(p.mode)<4 &&
        std::isfinite(p.wet) && p.wet>=0 && p.wet<=1;
}
using State=std::array<std::uint8_t,16>;
inline State save(const Patch& p) noexcept {
    static_assert(sizeof(double)==8 && std::numeric_limits<double>::is_iec559,"binary64 required");
    State b{'R','F','0','1',static_cast<std::uint8_t>(p.action.lo),static_cast<std::uint8_t>(p.action.hi),
        static_cast<std::uint8_t>(p.mode),static_cast<std::uint8_t>(p.bypass)};
    std::uint64_t bits=0;std::memcpy(&bits,&p.wet,8);
    for(unsigned i=0;i<8;++i)b[8+i]=static_cast<std::uint8_t>(bits>>(8*i));
    return b;
}
inline bool load(const std::uint8_t* b,std::size_t n,Patch& p) noexcept {
    if(!b||n!=16||b[0]!='R'||b[1]!='F'||b[2]!='0'||b[3]!='1'||b[7]>1)return false;
    Patch next{{b[4],b[5]},static_cast<Mode>(b[6]),b[7]!=0,0};
    std::uint64_t bits=0;for(unsigned i=0;i<8;++i)bits|=std::uint64_t(b[8+i])<<(8*i);
    std::memcpy(&next.wet,&bits,8);if(!valid(next))return false;p=next;return true;
}
// Audio-thread-owned. Apply a complete patch at its sample offset before frame().
// Blend transfer tables, not receipts: intermediate audio is intentionally not a decoded index.
class Live {
    using Table=std::array<double,8>;
    Patch patch_{}; Table current_{},start_{},goal_{};
    unsigned length_=240,remaining_=0; double wet_=0;
    static Table table(const Patch& p) noexcept {
        Table t{};for(unsigned q=0;q<8;++q){const auto r=encode(q,p.mode,hint(p.action));
            t[q]=level(decode(collapse(q,p.action),p.action,r).index);}return t;
    }
    double sample(double in) const noexcept {
        const double x=clean(in);if(x==0||wet_==0)return x;
        return clean(x*(1-wet_)+current_[quantize(x)]*wet_);
    }
public:
    Live() noexcept {reset();}
    const Patch& patch() const noexcept {return patch_;}
    bool prepare(double rate) noexcept {
        if(!std::isfinite(rate)||rate<8000||rate>384000)return false;
        length_=static_cast<unsigned>(std::ceil(rate*.005));reset();return true;
    }
    void reset() noexcept {current_=start_=goal_=table(patch_);remaining_=0;wet_=0;}
    bool apply(const Patch& p) noexcept {
        if(!valid(p))return false;
        const auto next=table(p);
        if(next!=goal_){start_=current_;goal_=next;remaining_=length_;}
        patch_=p;return true;
    }
    template<class T> void frame(T& l,T& r) noexcept {
        if(remaining_){--remaining_;const double a=double(length_-remaining_)/length_;
            for(unsigned i=0;i<8;++i)current_[i]=remaining_?start_[i]+(goal_[i]-start_[i])*a:goal_[i];}
        const double target=patch_.bypass?0:patch_.wet,step=1.0/length_;
        wet_+=std::clamp(target-wet_,-step,step);
        l=static_cast<T>(sample(l));r=static_cast<T>(sample(r));
    }
};
}
