#pragma once
#include <algorithm>
#include <array>
#include <cmath>
#include <cstddef>
namespace loom {
constexpr unsigned nodes=9, stride=16, frames=nodes*stride;
constexpr double pi=3.14159265358979323846;
using Row=std::array<double,nodes>;
struct Plan { std::array<unsigned,2> missing{}; std::array<Row,2> exact{}, baseline{}; std::array<double,2> gain{}; };
inline Plan makePlan(unsigned separation,unsigned rotation) noexcept {
    Plan p; p.missing={rotation%nodes,(rotation+std::clamp(separation,1u,4u))%nodes};
    for(unsigned k=0;k<2;++k){
        const int e=int(p.missing[k]), h=int(p.missing[1-k]);
        for(int j=0;j<int(nodes);++j){
            if(j==e||j==h)continue;
            const double w=((j-e+1)%2!=0?-1.:1.)*std::sin(pi*(j-h)/nodes)/std::sin(pi*(e-h)/nodes);
            p.exact[k][unsigned(j)]=w; p.gain[k]+=std::abs(w);
        }
        unsigned l=1,r=1; while((unsigned(e)+nodes-l)%nodes==unsigned(h))++l;
        while((unsigned(e)+r)%nodes==unsigned(h))++r;
        p.baseline[k][(unsigned(e)+nodes-l)%nodes]=double(r)/(l+r);
        p.baseline[k][(unsigned(e)+r)%nodes]=double(l)/(l+r);
    }
    return p;
}
inline Row weights(const Plan& p,unsigned k,double budget) noexcept {
    const double a=std::clamp((budget-1.)/(p.gain[k]-1.),0.,1.); Row w{};
    for(unsigned j=0;j<nodes;++j)w[j]=(1-a)*p.baseline[k][j]+a*p.exact[k][j];
    return w;
}
struct Params { unsigned separation=4, rotation=0; double budget=2, repair=1, wet=.5, gain=1; bool bypass=false; };
inline double clean(double v) noexcept {return std::isfinite(v)&&std::abs(v)>=1e-30?std::clamp(v,-1.,1.):0.;}
inline double unit(double v,double fallback) noexcept {return std::isfinite(v)?std::clamp(v,0.,1.):fallback;}
using Stereo=std::array<double,2>;
class Engine {
    std::array<std::array<Plan,nodes>,4> plans{};
    std::array<Stereo,frames> capture{},dry{},effect{};
    Params target{},latched{}; unsigned pos=0; double wet=.5,gain=1, slew=1./240.; bool prepared=false;
    static double approach(double x,double y,double s) noexcept {return x+std::clamp(y-x,-s,s);}
    void finish() noexcept {
        dry=capture; effect=capture;
        const auto& p=plans[latched.separation-1][latched.rotation];
        for(unsigned k=0;k<2;++k){const auto w=weights(p,k,latched.budget);
            for(unsigned lane=0;lane<stride;++lane)for(unsigned ch=0;ch<2;++ch){double v=0;
                for(unsigned j=0;j<nodes;++j)v+=w[j]*capture[j*stride+lane][ch];
                effect[p.missing[k]*stride+lane][ch]=clean(v*latched.repair);
            }
        }
    }
public:
    static constexpr unsigned latency=frames, tail=2*frames;
    bool prepare(double sr) noexcept {
        if(!std::isfinite(sr)||sr<1000||sr>2000000)return false;
        for(unsigned d=1;d<=4;++d)for(unsigned r=0;r<nodes;++r)plans[d-1][r]=makePlan(d,r);
        slew=1./std::ceil(sr*.005);prepared=true;reset();return true;
    }
    void set(Params p) noexcept {
        p.separation=std::clamp(p.separation,1u,4u);p.rotation%=nodes;
        p.budget=std::isfinite(p.budget)?std::clamp(p.budget,1.,16.):target.budget;
        p.repair=unit(p.repair,target.repair);p.wet=unit(p.wet,target.wet);p.gain=unit(p.gain,target.gain);target=p;
    }
    void reset() noexcept {capture={};dry={};effect={};pos=0;latched=target;wet=target.bypass?0.:target.wet;gain=target.gain;}
    Stereo step(double l,double r) noexcept {
        if(!prepared)return {};
        if(pos==0)latched=target;
        wet=approach(wet,target.bypass?0.:target.wet,slew);gain=approach(gain,target.gain,slew);
        Stereo y{};for(unsigned c=0;c<2;++c)y[c]=clean(dry[pos][c]+wet*(gain*effect[pos][c]-dry[pos][c]));
        capture[pos]={clean(l),clean(r)};
        if(++pos==frames){finish();pos=0;}
        return y;
    }
};
}
