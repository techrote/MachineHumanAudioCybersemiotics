#pragma once
#include "band_input.hpp"

namespace mhac::counterfactual {
// Four independently clocked memories. Fixed normalization prevents gain jumps
// when individual resonators are muted; muting never destroys their history.
struct MemoryBand {
    std::uint16_t hz=220, gain=750, peakMix=250;
    bool excite=true, erase=false;
    std::uint16_t selectivity=0; // per mille; 0 preserves broadband excitation
    bool discardOnClose=false; // opt-in zero-fill of pending resonator drive
};
struct MemoryConfig {
    std::array<MemoryBand,4> bands{{{110,750,250},{165,750,250},{220,750,250},{330,750,250}}};
    std::uint16_t wet=700;
    bool bypass=false;
};
class HarmonicBank {
    std::array<Processor,4> bands_{};
    MemoryConfig config_{};
    std::array<BandInput,4> filters_{};
    double rate_=48000;
    double wet_=0.7, slew_=1.0/240;
    static double clean(double x) noexcept {
        return std::isfinite(x)&&std::abs(x)>=1e-20?std::clamp(x,-1.0,1.0):0;
    }
public:
    HarmonicBank() noexcept { set(config_); prepare(rate_); }
    bool set(const MemoryConfig& c) noexcept {
        if(c.wet>1000) return false;
        for(const auto& b:c.bands)
            if(b.hz<40||b.hz>6000||b.gain>1000||b.peakMix>1000||b.selectivity>1000) return false;
        for(unsigned i=0;i<bands_.size();++i){
            const auto& b=c.bands[i];
            if(b.excite)bands_[i].cancelOptimalEscape();
            if(b.hz!=config_.bands[i].hz)filters_[i].tune(rate_,b.hz);
            if(!b.excite&&config_.bands[i].excite){
                filters_[i].reset();
                if(b.discardOnClose)bands_[i].discardPendingInput();
            }
            bands_[i].set({b.hz,1000,b.gain,1,b.erase,false,b.peakMix});
        }
        config_=c;
        return true;
    }
    MemoryConfig config() const noexcept { return config_; }
    bool prepare(double rate) noexcept {
        if(!validSampleRate(rate)) return false;
        rate_=rate;
        for(unsigned i=0;i<bands_.size();++i){bands_[i].prepare(rate);filters_[i].tune(rate,config_.bands[i].hz);}
        slew_=1.0/std::ceil(rate*0.005); reset(); return true;
    }
    void reset() noexcept {
        for(auto& b:bands_) b.reset();
        for(auto& f:filters_)f.reset();
        wet_=config_.bypass?0:config_.wet/1000.0;
    }
    bool pulse(unsigned band) noexcept {
        if(band>=bands_.size()) return false;
        bands_[band].requestIntervention(); return true;
    }
    bool discardPendingInput(unsigned band) noexcept {
        if(band>=bands_.size())return false;
        bands_[band].discardPendingInput();return true;
    }
    // Momentary command; intentionally not serialized in HM01.
    bool beginOptimalEscape(unsigned band) noexcept {
        return band<bands_.size()&&!config_.bands[band].excite&&bands_[band].beginOptimalEscape();
    }
    bool canBeginNewOptimalEscape(unsigned band) const noexcept {
        return band<bands_.size()&&!config_.bands[band].excite&&bands_[band].canBeginNewOptimalEscape();
    }
    std::uint64_t interventions(unsigned band) const noexcept {
        return band<bands_.size()?bands_[band].interventions():0;
    }
    bool optimalEscapeActive(unsigned band) const noexcept {
        return band<bands_.size()&&bands_[band].optimalEscapeActive();
    }
    IntegerState lattice(unsigned band,unsigned channel) const noexcept {
        return band<bands_.size()?bands_[band].lattice(channel):IntegerState{};
    }
    Stereo process(double left,double right) noexcept {
        left=clean(left); right=clean(right);
        const double target=config_.bypass?0:config_.wet/1000.0;
        wet_+=std::clamp(target-wet_,-slew_,slew_);
        Stereo result{};
        for(unsigned i=0;i<bands_.size();++i){
            const auto& b=config_.bands[i];
            double l=0,r=0;
            if(b.excite){
                const auto f=filters_[i].process(left,right);
                const double m=b.selectivity/1000.0;
                l=b.selectivity?left*(1-m)+f.left*m:left;
                r=b.selectivity?right*(1-m)+f.right*m:right;
            }
            const auto s=bands_[i].process(l,r);
            result.left+=s.left*0.25; result.right+=s.right*0.25;
        }
        return {std::clamp((1-wet_)*left+wet_*result.left,-1.0,1.0),
                std::clamp((1-wet_)*right+wet_*result.right,-1.0,1.0)};
    }
    template<class Sample> void processBlock(const Sample* l,const Sample* r,Sample* ol,Sample* oright,unsigned n) noexcept {
        for(unsigned i=0;i<n;++i){const auto s=process(l[i],r[i]);ol[i]=static_cast<Sample>(s.left);oright[i]=static_cast<Sample>(s.right);}
    }
};
} // namespace mhac::counterfactual
