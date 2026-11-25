#pragma once
#include "loom.hpp"
namespace loom {
// One erased node, with the second observation restored. Section 2 of #321.
inline Row singleProbe(unsigned e) noexcept {
    Row w{};
    for(unsigned j=0;j<nodes;++j)if(j!=e)
        w[j]=-std::cos(2*pi*4*(int(j)-int(e))/nodes);
    return w;
}
inline Row boundedSingle(unsigned e,double budget) noexcept {
    auto w=singleProbe(e);double norm=0;
    for(double v:w)norm+=std::abs(v);
    const double a=std::clamp((budget-1)/(norm-1),0.,1.);
    for(double& v:w)v*=a;
    w[(e+nodes-1)%nodes]+=(1-a)*.5;
    w[(e+1)%nodes]+=(1-a)*.5;
    return w;
}
// Rows include the repair amount. Probe=0 never reads either erased node;
// probe=1 restores the second node verbatim and reads it to repair the first.
inline std::array<Row,2> probeRows(const Plan& p,double budget,double repair,double probe) noexcept {
    budget=std::isfinite(budget)?std::clamp(budget,1.,16.):2.;
    repair=unit(repair,1);probe=unit(probe,0);
    auto a=weights(p,0,budget),b=weights(p,1,budget);
    const auto s=boundedSingle(p.missing[0],budget);
    for(unsigned j=0;j<nodes;++j){
        a[j]=repair*((1-probe)*a[j]+probe*s[j]);
        b[j]=repair*(1-probe)*b[j];
    }
    b[p.missing[1]]=probe;
    return {a,b};
}
struct ProbeParams { Params base{}; double probe=0; };
class ProbeEngine {
    std::array<std::array<Plan,nodes>,4> plans{};
    std::array<Stereo,frames> capture{},dry{},effect{};
    ProbeParams target{},latched{};unsigned pos=0;
    double wet=.5,gain=1,slew=1./240.;bool prepared=false;
    static double approach(double x,double y,double s) noexcept {return x+std::clamp(y-x,-s,s);}
    void finish() noexcept {
        dry=capture;effect=capture;
        const auto& p=plans[latched.base.separation-1][latched.base.rotation];
        const auto rows=probeRows(p,latched.base.budget,latched.base.repair,latched.probe);
        for(unsigned k=0;k<2;++k){const auto w=weights(p,k,latched.base.budget);
        for(unsigned lane=0;lane<stride;++lane)for(unsigned ch=0;ch<2;++ch){
            double v=0;
            // Preserve original arithmetic in the zero-probe endpoint.
            if(latched.probe==0){for(unsigned j=0;j<nodes;++j)v+=w[j]*capture[j*stride+lane][ch];v*=latched.base.repair;}
            else for(unsigned j=0;j<nodes;++j)v+=rows[k][j]*capture[j*stride+lane][ch];
            effect[p.missing[k]*stride+lane][ch]=clean(v);
        }}
    }
public:
    static constexpr unsigned latency=frames,tail=2*frames;
    bool prepare(double sr) noexcept {
        if(!std::isfinite(sr)||sr<1000||sr>2000000)return false;
        for(unsigned d=1;d<=4;++d)for(unsigned r=0;r<nodes;++r)plans[d-1][r]=makePlan(d,r);
        slew=1./std::ceil(sr*.005);prepared=true;reset();return true;
    }
    void set(ProbeParams p) noexcept {
        auto& b=p.base;b.separation=std::clamp(b.separation,1u,4u);b.rotation%=nodes;
        b.budget=std::isfinite(b.budget)?std::clamp(b.budget,1.,16.):target.base.budget;
        b.repair=unit(b.repair,target.base.repair);b.wet=unit(b.wet,target.base.wet);b.gain=unit(b.gain,target.base.gain);
        p.probe=unit(p.probe,target.probe);target=p;
    }
    void reset() noexcept {capture={};dry={};effect={};pos=0;latched=target;wet=target.base.bypass?0:target.base.wet;gain=target.base.gain;}
    Stereo step(double l,double r) noexcept {
        if(!prepared)return {};
        if(pos==0)latched=target;
        wet=approach(wet,target.base.bypass?0:target.base.wet,slew);gain=approach(gain,target.base.gain,slew);
        Stereo y{};for(unsigned c=0;c<2;++c)y[c]=clean(dry[pos][c]+wet*(gain*effect[pos][c]-dry[pos][c]));
        capture[pos]={clean(l),clean(r)};
        if(++pos==frames){finish();pos=0;}return y;
    }
};
}
