#pragma once
#include "../clock.hpp"
#include <limits>

namespace mhac::clock_fold::quality {
// Prepare outside the audio callback; read-only after preparation.
class KernelBank {
    static constexpr int bins=32, phases=64, taps=48;
    using Row=std::array<double,taps>;
    std::array<std::array<Row,phases+1>,bins> rows_{};
    bool ready_=false;
public:
    void prepare() noexcept {
        constexpr double pi=3.14159265358979323846;
        for(int b=0;b<bins;++b) for(int p=0;p<=phases;++p){
            const double cutoff=.45*(b+1)/bins;
            auto& row=rows_[b][p]; double sum=0;
            for(int j=0;j<taps;++j){
                const double x=j-(taps/2-1)-double(p)/phases;
                const double sinc=x==0?2*cutoff:std::sin(2*pi*cutoff*x)/(pi*x);
                const double w=std::abs(x)<taps/2?.5+.5*std::cos(pi*x/(taps/2)):0;
                row[j]=sinc*w; sum+=row[j];
            }
            for(auto& v:row) v/=sum;
        }
        ready_=true;
    }
    Stereo render(const std::array<Stereo,frameSize>& frame,const Plan& plan,std::size_t pos) const noexcept {
        pos=std::min(pos,frameSize-1);
        auto clean=[](double v){v=bounded(v,-1,1);return std::abs(v)<1e-30?0.:v;};
        if(plan.identity||!ready_) return {clean(frame[pos][0]),clean(frame[pos][1])};
        const double t=double(pos)/double(frameSize-1);
        std::size_t s=0; while(s<3 && t>plan.boundary[s+1]) ++s;
        const double width=plan.boundary[s+1]-plan.boundary[s];
        if(!std::isfinite(width)||width<=0) return {};
        const double speed=.25/width;
        const int b=std::clamp(int(std::floor(bins/std::max(1.,speed)))-1,0,bins-1);
        const double src=bounded(plan.source(t)*double(frameSize-1),0,double(frameSize-1));
        const int base=int(src); const double phase=(src-base)*phases;
        const int p=std::min(int(phase),phases-1); const double f=phase-p;
        Stereo out{};
        for(int j=0;j<taps;++j){
            const auto i=std::size_t(std::clamp(base+j-(taps/2-1),0,int(frameSize)-1));
            const double w=(1-f)*rows_[b][p][j]+f*rows_[b][p+1][j];
            for(int ch=0;ch<2;++ch) out[ch]+=w*clean(frame[i][ch]);
        }
        return {clean(out[0]),clean(out[1])};
    }
};
}
