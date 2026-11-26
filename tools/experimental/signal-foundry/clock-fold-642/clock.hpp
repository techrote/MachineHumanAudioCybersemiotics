#pragma once
#include <algorithm>
#include <array>
#include <cmath>
#include <cstddef>

namespace mhac::clock_fold {
constexpr std::size_t frameSize = 8192;
inline double bounded(double x, double lo, double hi, double fallback = 0) noexcept {
    return std::isfinite(x) ? std::clamp(x, lo, hi) : fallback;
}
struct Controls {
    double drift = 0, curvature = 0, compensation = 0, wet = 1, edge = .03;
    bool bypass = false;
};
struct Plan {
    std::array<double, 5> boundary{0,.25,.5,.75,1};
    double radius = 0;
    bool identity = true;
    static Plan make(Controls c) noexcept {
        Plan p;
        const double d = bounded(c.drift,-.5,.5)*(1-bounded(c.compensation,0,1));
        const double k = bounded(c.curvature,-.5,.5);
        const std::array<double,4> bend{1,-1,-1,1};
        std::array<double,4> gap{};
        double sum=0;
        for (std::size_t i=0;i<4;++i) { gap[i]=std::exp(d*(double(i)-1.5)+k*bend[i]); sum+=gap[i]; }
        for (std::size_t i=0;i<4;++i) p.boundary[i+1]=p.boundary[i]+gap[i]/sum;
        p.boundary[4]=1;
        std::array<double,4> z{};
        for (std::size_t i=0;i<4;++i) z[i]=std::log(gap[i]/sum);
        for (std::size_t i=0;i<2;++i) for (std::size_t j=i+1;j<3;++j) for (std::size_t l=j+1;l<4;++l) {
            const double chord=((l-j)*z[i]+(j-i)*z[l])/double(l-i);
            p.radius=std::max(p.radius,.5*std::abs(z[j]-chord));
        }
        p.identity=d==0 && k==0;
        return p;
    }
    double source(double t) const noexcept {
        if (identity) return t;
        std::size_t i=0;
        while (i<3 && t>boundary[i+1]) ++i;
        return .25*(double(i)+(t-boundary[i])/(boundary[i+1]-boundary[i]));
    }
};
using Stereo=std::array<double,2>;
class Engine {
    std::array<std::array<Stereo,frameSize>,2> frames_{};
    std::array<Plan,2> plans_{};
    std::array<double,2> edges_{};
    std::size_t pos_=0, capture_=0;
    double wet_=1, step_=1./240;
public:
    static constexpr std::size_t latency=frameSize, tail=2*frameSize;
    bool prepare(double rate) noexcept {
        if (!std::isfinite(rate) || rate<1000 || rate>2000000) return false;
        step_=1/std::max(1.,.005*rate); reset(); return true;
    }
    void reset() noexcept { frames_={}; plans_={}; edges_={}; pos_=capture_=0; wet_=1; }
    Stereo tick(Stereo x, Controls c) noexcept {
        if (!pos_) { plans_[capture_]=Plan::make(c); edges_[capture_]=bounded(c.edge,0,.25,.03); }
        for (double& v:x) { v=bounded(v,-1,1); if (std::abs(v)<1e-30) v=0; }
        const auto playback=1-capture_;
        const auto& old=frames_[playback];
        const auto& p=plans_[playback];
        const Stereo dry=old[pos_];
        const double t=double(pos_)/double(frameSize-1);
        const double src=std::clamp(p.source(t)*double(frameSize-1),0.,double(frameSize-1));
        const auto a=static_cast<std::size_t>(src), b=std::min(a+1,frameSize-1);
        const double frac=src-double(a), edge=edges_[playback];
        const double seam=edge>0 ? std::min(1.,std::min(t,1-t)/edge) : 1.;
        const double target=c.bypass?0:bounded(c.wet,0,1,1);
        wet_+=std::clamp(target-wet_,-step_,step_);
        Stereo y{};
        for (std::size_t ch=0;ch<2;++ch) {
            const double warped=p.identity ? dry[ch] : (1-frac)*old[a][ch]+frac*old[b][ch];
            const double w=seam*wet_;
            y[ch]=p.identity||w==0 ? dry[ch] : bounded((1-w)*dry[ch]+w*warped,-1,1);
            if (std::abs(y[ch])<1e-30) y[ch]=0;
        }
        frames_[capture_][pos_]=x;
        if (++pos_==frameSize) { pos_=0; capture_=playback; }
        return y;
    }
    template<class T> void process(const T* left,const T* right,T* outL,T* outR,std::size_t n,Controls c) noexcept {
        for (std::size_t i=0;i<n;++i) {
            const double l=left?left[i]:0, r=right?right[i]:0;
            const auto y=tick({l,r},c);
            if(outL) outL[i]=static_cast<T>(y[0]);
            if(outR) outR[i]=static_cast<T>(y[1]);
        }
    }
};
}
