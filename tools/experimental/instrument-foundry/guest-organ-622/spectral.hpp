#pragma once
#include <algorithm>
#include <array>
#include <cmath>
namespace guest {
// A fixed, note-local spectral rule: the four motif pitches become simultaneous
// octave-up partials. Attenuate rather than fold partials near Nyquist.
class SpectralBank {
    std::array<double,4> phase{},inc{},gain{};
public:
    void prepare(double sr,double root,const std::array<int,4>& motif) noexcept {
        phase={};inc={};gain={};
        if(!std::isfinite(sr)||sr<=0||!std::isfinite(root)||root<=0)return;
        for(unsigned i=0;i<4;++i){
            const double f=root*std::exp2((std::clamp(motif[i],-12,12)+12)/12.);
            const double x=f/sr;
            if(x>=.45)continue;
            inc[i]=x;gain[i]=.25*std::clamp((.45-x)/.05,0.,1.);
        }
    }
    // Advance identical phase history even when the bank is inaudible.
    double tick(bool audible=true) noexcept {
        double y=0;
        for(unsigned i=0;i<4;++i)if(gain[i]>0){
            phase[i]+=inc[i];if(phase[i]>=1)phase[i]-=1;
            if(audible)y+=gain[i]*std::sin(6.28318530717958647692*phase[i]);
        }
        return y;
    }
};
}
