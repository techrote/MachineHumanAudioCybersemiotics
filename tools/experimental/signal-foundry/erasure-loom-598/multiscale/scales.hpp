#pragma once
#include "../probe.hpp"
namespace loomscale {
using namespace loom;
inline constexpr unsigned latency=9*1024, tail=2*latency;
using Plans=std::array<std::array<Plan,nodes>,4>;
// Each ring is both capture and scheduled playback. Frames divide the ring exactly.
template<unsigned S> class Path {
    static constexpr unsigned F=nodes*S;
    static_assert(latency%F==0,"aligned frames required");
    std::array<Stereo,latency> ring{};
    ProbeParams latched{};
    void finish(unsigned start,const Plans& plans) noexcept {
        const auto& p=plans[latched.base.separation-1][latched.base.rotation];
        const auto rows=probeRows(p,latched.base.budget,latched.base.repair,latched.probe);
        const auto w0=weights(p,0,latched.base.budget),w1=weights(p,1,latched.base.budget);
        for(unsigned lane=0;lane<S;++lane){
            Stereo v[2]{};
            for(unsigned k=0;k<2;++k)for(unsigned ch=0;ch<2;++ch){
                double x=0;
                if(latched.probe==0){const auto& w=k==0?w0:w1;for(unsigned j=0;j<nodes;++j)x+=w[j]*ring[start+j*S+lane][ch];x*=latched.base.repair;}
                else for(unsigned j=0;j<nodes;++j)x+=rows[k][j]*ring[start+j*S+lane][ch];
                if(latched.edge>0){const double a=std::min(1.,double(std::min(lane,S-1-lane))/(latched.edge*(S*.5)));x=a*x+(1-a)*ring[start+p.missing[k]*S+lane][ch];}
                v[k][ch]=clean(x);
            }
            for(unsigned k=0;k<2;++k)ring[start+p.missing[k]*S+lane]=v[k];
        }
    }
public:
    void reset() noexcept {ring.fill({});latched={};}
    Stereo step(unsigned pos,Stereo input,const ProbeParams& target,const Plans& plans) noexcept {
        if(pos%F==0)latched=target;
        const auto y=ring[pos];ring[pos]=input;
        if(pos%F==F-1)finish(pos+1-F,plans);
        return y;
    }
};
class Engine {
    Plans plans{};
    Path<16> fine;Path<128> medium;Path<1024> coarse;
    std::array<Stereo,latency> dry{};
    ProbeParams target{};unsigned pos=0,selection=0,remaining=0,fade=960;
    std::array<double,3> mix{1,0,0};
    double wet=.5,gain=1,slew=1./240.;bool prepared=false;
    static double approach(double a,double b,double step) noexcept {return a+std::clamp(b-a,-step,step);}
public:
    bool prepare(double sr) noexcept {
        if(!std::isfinite(sr)||sr<1000||sr>2000000)return false;
        for(unsigned d=1;d<=4;++d)for(unsigned r=0;r<nodes;++r)plans[d-1][r]=makePlan(d,r);
        fade=unsigned(std::ceil(sr*.020));slew=1./std::ceil(sr*.005);prepared=true;reset();return true;
    }
    void set(ProbeParams p,unsigned scale) noexcept {
        auto& b=p.base;b.separation=std::clamp(b.separation,1u,4u);b.rotation%=nodes;
        b.budget=std::isfinite(b.budget)?std::clamp(b.budget,1.,16.):target.base.budget;
        b.repair=unit(b.repair,target.base.repair);b.wet=unit(b.wet,target.base.wet);b.gain=unit(b.gain,target.base.gain);
        p.probe=unit(p.probe,target.probe);p.edge=unit(p.edge,target.edge);target=p;
        scale=std::min(scale,2u);if(scale!=selection){selection=scale;remaining=fade;}
    }
    void reset() noexcept {
        fine.reset();medium.reset();coarse.reset();dry.fill({});pos=remaining=0;mix={};mix[selection]=1;
        wet=target.base.bypass?0:target.base.wet;gain=target.base.gain;
    }
    Stereo step(double l,double r) noexcept {
        if(!prepared)return {};
        const Stereo in{clean(l),clean(r)},d=dry[pos];dry[pos]=in;
        const std::array<Stereo,3> paths{fine.step(pos,in,target,plans),medium.step(pos,in,target,plans),coarse.step(pos,in,target,plans)};
        if(remaining){for(unsigned k=0;k<3;++k)mix[k]+=((k==selection?1.:0.)-mix[k])/remaining;--remaining;}
        wet=approach(wet,target.base.bypass?0:target.base.wet,slew);gain=approach(gain,target.base.gain,slew);
        Stereo y{};for(unsigned c=0;c<2;++c){double e=0;for(unsigned k=0;k<3;++k)e+=mix[k]*paths[k][c];y[c]=clean(d[c]+wet*(gain*e-d[c]));}
        if(++pos==latency)pos=0;
        return y;
    }
};
}
