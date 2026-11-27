#pragma once
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>

namespace mhac::counterfactual {
struct IntegerState { int x=0,y=0; };
constexpr int limit=16;
constexpr int clampState(int x) noexcept { return x < -limit ? -limit : x > limit ? limit : x; }
// Exact signed nearest (ties away) or truncation for the restricted q=9 model.
constexpr int quant(int numerator,bool truncate) noexcept {
    return truncate ? numerator/9 : (numerator<0 ? -((-numerator+4)/9) : (numerator+4)/9);
}
constexpr IntegerState step(IntegerState s,int drive,bool truncate) noexcept {
    return {clampState(quant(-8*s.y,truncate)+drive),clampState(quant(8*s.x,truncate))};
}
// For undriven stereo, shared N/T acts monotonically on the maximum absolute
// coordinate (rotation only permutes magnitudes). N decreases every m>4;
// neither action can cross from m>4 to m<4. Below 5, only T decreases m.
constexpr int magnitude(IntegerState s) noexcept {
    return std::max(s.x<0?-s.x:s.x,s.y<0?-s.y:s.y);
}
constexpr bool optimalStereoTruncate(IntegerState l,IntegerState r) noexcept {
    const int m=std::max(magnitude(l),magnitude(r));
    return m>0&&m<=4;
}
struct Controls {
    std::uint16_t hz=220,wet=700,gain=800;
    std::uint8_t monitor=1; // 0 reference, 1 nearest/erased, 2 half difference
    bool erase=false,bypass=false;
    std::uint16_t peakMix=0; // per mille; zero preserves CR01 behaviour
};
constexpr bool valid(Controls p) noexcept {
    return p.hz>=40 && p.hz<=6000 && p.wet<=1000 && p.gain<=1000 && p.monitor<=2 && p.peakMix<=1000;
}
using Patch=std::array<std::uint8_t,12>;
inline Patch encode(Controls p) noexcept {
    return {'C','R','0','1',std::uint8_t(p.hz),std::uint8_t(p.hz>>8),std::uint8_t(p.wet),std::uint8_t(p.wet>>8),std::uint8_t(p.gain),std::uint8_t(p.gain>>8),p.monitor,std::uint8_t((p.erase?1:0)|(p.bypass?2:0))};
}
inline bool decode(const Patch& b,Controls& out) noexcept {
    if(b[0]!='C'||b[1]!='R'||b[2]!='0'||b[3]!='1'||(b[11]&0xfc)) return false;
    const Controls p{std::uint16_t(b[4]|(b[5]<<8)),std::uint16_t(b[6]|(b[7]<<8)),std::uint16_t(b[8]|(b[9]<<8)),b[10],bool(b[11]&1),bool(b[11]&2)};
    if(!valid(p)) return false;
    out=p; return true;
}
// Legacy encode/decode intentionally describe CR01 only. Use encodeState for full configurations.
struct State {
    std::array<std::uint8_t,14> bytes{};
    unsigned size=12;
    bool operator==(const State& other) const noexcept {return size==other.size&&bytes==other.bytes;}
    bool operator!=(const State& other) const noexcept {return !(*this==other);}
};
inline State encodeState(Controls p) noexcept {
    State s;const auto legacy=encode(p);std::copy(legacy.begin(),legacy.end(),s.bytes.begin());
    if(p.peakMix){s.size=14;s.bytes[3]='2';s.bytes[12]=std::uint8_t(p.peakMix);s.bytes[13]=std::uint8_t(p.peakMix>>8);}
    return s;
}
inline bool decodeState(const State& s,Controls& out) noexcept {
    if((s.size!=12&&s.size!=14)||s.bytes[3]!=(s.size==12?'1':'2'))return false;
    Patch legacy{};std::copy_n(s.bytes.begin(),legacy.size(),legacy.begin());legacy[3]='1';
    Controls c;if(!decode(legacy,c))return false;
    if(s.size==14)c.peakMix=std::uint16_t(s.bytes[12]|(s.bytes[13]<<8));
    if(!valid(c))return false;
    out=c;return true;
}
inline bool validSampleRate(double rate) noexcept { return std::isfinite(rate)&&rate>=1000&&rate<=2000000; }
struct Stereo { double left=0,right=0; };
struct Channel {
    IntegerState discrete{};
    double rx=0,ry=0,prevDiscrete=0,prevReference=0,sum=0,peak=0;
    void tick(int drive,bool truncate) noexcept {
        prevDiscrete=double(discrete.x)/limit;
        prevReference=rx/limit;
        discrete=step(discrete,drive,truncate);
        const double x=std::clamp(-8.0*ry/9.0+drive,-double(limit),double(limit));
        const double y=std::clamp(8.0*rx/9.0,-double(limit),double(limit));
        rx=std::abs(x)<1e-15?0:x; ry=std::abs(y)<1e-15?0:y;
    }
    double value(double phase,const std::array<double,3>& w) const noexcept {
        const double q=prevDiscrete+(double(discrete.x)/limit-prevDiscrete)*phase;
        const double r=prevReference+(rx/limit-prevReference)*phase;
        return w[0]*r+w[1]*q+w[2]*(q-r)*0.5;
    }
};
class Processor {
    Controls target_{};
    std::array<Channel,2> ch_{};
    std::array<double,3> weights_{0,1,0};
    double rate_=48000,phase_=0,wet_=0.7,gain_=0.8,slew_=1.0/240;
    unsigned count_=0;
    bool pending_=false, optimal_=false;
    std::uint64_t ticks_=0,interventions_=0;
    static double clean(double x) noexcept { return std::isfinite(x)&&std::abs(x)>=1e-20 ? std::clamp(x,-1.0,1.0):0; }
    static void approach(double& x,double y,double delta) noexcept { x+=std::clamp(y-x,-delta,delta); }
public:
    bool prepare(double rate) noexcept {
        if(!validSampleRate(rate)) return false;
        rate_=rate; slew_=1.0/std::ceil(rate_*0.005); reset(); return true;
    }
    void reset() noexcept {
        ch_={}; phase_=0; count_=0; pending_=optimal_=false; ticks_=interventions_=0;
        wet_=target_.bypass?0:target_.wet/1000.0; gain_=target_.gain/1000.0;
        weights_={}; weights_[target_.monitor]=1;
    }
    bool set(Controls p) noexcept { if(!valid(p)) return false; target_=p; if(p.erase)optimal_=false; return true; }
    Controls controls() const noexcept { return target_; }
    // Convenience API for the same persistent control used by the host.
    // The value at a clock tick applies to the entire just-completed window.
    bool setPeakMix(unsigned permille) noexcept {
        if(permille>1000) return false;
        target_.peakMix=static_cast<std::uint16_t>(permille); return true;
    }
    unsigned peakMix() const noexcept { return target_.peakMix; }
    // Last-value coalescing: one or more requests before a tick mean one T update.
    void requestIntervention() noexcept { pending_=true; optimal_=false; }
    // Explicit admission discards drive, but never silently consumes a manual pulse.
    bool beginOptimalEscape() noexcept {
        if(target_.erase||pending_)return false;
        discardPendingInput(); optimal_=true; return true;
    }
    void cancelOptimalEscape() noexcept { optimal_=false; }
    bool optimalEscapeActive() const noexcept { return optimal_; }
    // Zero-fill the elapsed prefix of the current drive window, without
    // changing clock phase, lattice, interpolation, or pending intervention.
    void discardPendingInput() noexcept { for(auto& c:ch_){c.sum=0;c.peak=0;} }
    double effectiveHz() const noexcept { return std::min(double(target_.hz),rate_/16.0); }
    std::uint64_t ticks() const noexcept { return ticks_; }
    std::uint64_t interventions() const noexcept { return interventions_; }
    IntegerState lattice(unsigned channel) const noexcept { return ch_[channel%2].discrete; }
    Stereo process(double left,double right) noexcept {
        const std::array<double,2> input{clean(left),clean(right)};
        approach(wet_,target_.bypass?0:target_.wet/1000.0,slew_);
        approach(gain_,target_.gain/1000.0,slew_);
        // A convex weight transition: every frame is a normalized interpolation.
        const double alpha=std::min(1.0,slew_);
        for(unsigned i=0;i<3;++i) weights_[i]+=(double(i==target_.monitor)-weights_[i])*alpha;
        if(1.0-weights_[target_.monitor]<1e-12){weights_={};weights_[target_.monitor]=1;}
        for(unsigned i=0;i<2;++i){
            auto& c=ch_[i]; c.sum+=input[i];
            // Earliest sample wins equal-magnitude ties; preserve its sign.
            if(std::abs(input[i])>std::abs(c.peak)) c.peak=input[i];
        }
        ++count_; phase_+=4.0*effectiveHz()/rate_;
        if(phase_>=1.0){
            phase_-=1.0;
            std::array<int,2> drives{};
            for(unsigned i=0;i<2;++i){
                const auto& c=ch_[i];
                const double legacy=12.0*c.sum/double(count_);
                const double blend=target_.peakMix/1000.0;
                const double excitation=target_.peakMix==0?legacy:legacy*(1.0-blend)+12.0*c.peak*blend;
                drives[i]=static_cast<int>(std::round(excitation));
            }
            if(drives[0]||drives[1])optimal_=false;
            const bool trunc=target_.erase||pending_||(optimal_&&optimalStereoTruncate(ch_[0].discrete,ch_[1].discrete));
            pending_=false;
            ++ticks_; if(trunc) ++interventions_;
            for(unsigned i=0;i<2;++i){
                auto& c=ch_[i]; c.tick(drives[i],trunc); c.sum=0; c.peak=0;
            }
            if(!magnitude(ch_[0].discrete)&&!magnitude(ch_[1].discrete))optimal_=false;
            count_=0;
        }
        const auto out=[&](unsigned i){return std::clamp((1-wet_)*input[i]+wet_*gain_*ch_[i].value(phase_,weights_),-1.0,1.0);};
        return {out(0),out(1)};
    }
    template<class Sample> void processBlock(const Sample* left,const Sample* right,Sample* outL,Sample* outR,unsigned frames) noexcept {
        for(unsigned i=0;i<frames;++i){const auto s=process(left[i],right[i]);outL[i]=static_cast<Sample>(s.left);outR[i]=static_cast<Sample>(s.right);}
    }
};
} // namespace mhac::counterfactual
