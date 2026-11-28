#pragma once
#include <algorithm>
#include <cmath>
#include <cstdint>
namespace mhac::receipt {
struct Pair { unsigned lo, hi; };
inline Pair pair(unsigned a, unsigned b) noexcept {
    a=std::min(a,7u); b=std::min(b,7u);
    if(a==b) b=(a+1)%8;
    return {std::min(a,b),std::max(a,b)};
}
enum class Mode : unsigned { absent, fixed, preview, full };
struct Receipt { unsigned tag, mask; };
struct Result { unsigned index; bool ambiguous; bool invalid; };
inline unsigned hint(Pair p) noexcept {
    const unsigned d=p.lo^p.hi;
    return (d&1u)?1u:((d&2u)?2u:4u);
}
// The mask is trusted schema/preview metadata, not a free extra receipt bit.
inline Receipt encode(unsigned x, Mode m, unsigned previewMask, unsigned fixedMask=1) noexcept {
    const unsigned mask=m==Mode::full?7u:m==Mode::preview?previewMask:m==Mode::fixed?fixedMask:0u;
    return {x&mask,mask};
}
inline unsigned collapse(unsigned x, Pair p) noexcept { return x==p.hi?p.lo:x; }
inline Result decode(unsigned y, Pair p, Receipt r) noexcept {
    if(y>7 || y==p.hi || r.mask>7 || (r.tag&~r.mask)) return {0,false,true};
    const bool l=(y&r.mask)==r.tag;
    const bool h=y==p.lo && (p.hi&r.mask)==r.tag;
    if(l&&h) return {y,true,false};
    if(l) return {y,false,false};
    if(h) return {p.hi,false,false};
    return {y,false,true};
}
inline double clean(double x) noexcept {
    return std::isfinite(x)&&std::abs(x)>=1e-30?std::clamp(x,-1.0,1.0):0.0;
}
inline unsigned quantize(double x) noexcept {
    return std::min(7u,static_cast<unsigned>((clean(x)+1.0)*4.0));
}
inline double level(unsigned x) noexcept { return (static_cast<double>(x)-3.5)*0.125; }
struct Engine {
    Pair action{1,6}; Mode mode=Mode::preview; unsigned fixedMask=1;
    double wet=0.0, target=0.0, step=1.0/240.0;
    void prepare(double rate) noexcept {
        rate=std::isfinite(rate)?std::clamp(rate,8000.0,384000.0):48000.0;
        step=1.0/(0.005*rate); wet=0.0;
    }
    void setWet(double v) noexcept { target=std::isfinite(v)?std::clamp(v,0.0,1.0):0.0; }
    void setAction(unsigned a,unsigned b) noexcept { action=pair(a,b); }
    void setMode(Mode m) noexcept { mode=static_cast<unsigned>(m)<=3?m:Mode::absent; }
    // Call once per frame, including mono. Discrete action changes intentionally
    // change the quantized law immediately. Wet/bypass uses a five-ms slew.
    template<class T> void frame(T& l,T& r) noexcept {
        wet+=std::clamp(target-wet,-step,step);
        l=static_cast<T>(sample(l)); r=static_cast<T>(sample(r));
    }
private:
    double sample(double input) const noexcept {
        const auto x=clean(input); if(wet==0.0 || x==0.0) return x;
        const auto q=quantize(x);
        const auto rec=encode(q,mode,hint(action),fixedMask);
        const auto out=decode(collapse(q,action),action,rec);
        return clean(x*(1.0-wet)+level(out.index)*wet);
    }
};
}
