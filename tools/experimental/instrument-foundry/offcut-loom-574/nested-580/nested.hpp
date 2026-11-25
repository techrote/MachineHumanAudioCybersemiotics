#pragma once
#include "../core.hpp"
namespace offcut::nested {
struct Stems { double primary=0,middle=0,deep=0; double sum() const noexcept {return primary+middle+deep;} };
struct Patch { Params original=defaults; double cut=.2,depth=1,ratio=5; };
// The threshold is in the same units as the first residual, not the original carrier.
inline Stems partition(Pair p,double threshold,double articulation) noexcept {
    const auto s=split(p.r,threshold,articulation);
    return {p.l,s.primary,s.residual};
}
struct Voice {
    offcut::Voice source;
    double cut=.2,depth=1,phase=0,inc=0;
    void start(int id,int note,double cents,double velocity,double rate,Patch p) noexcept {
        p.original[3]=0; source.start(id,note,cents,velocity,rate,p.original);
        cut=unit(p.cut,.2);depth=unit(p.depth,1);phase=0;
        const double ratio=std::isfinite(p.ratio)?std::clamp(p.ratio,1.,16.):5.;
        inc=std::min(.45,source.inc*ratio);
    }
    Stems tick() noexcept {
        if(!source.active)return {};
        const auto p=source.tick();
        const auto s=partition(p,.05*source.velocity*source.level*cut,depth*(.5+.5*std::cos(tau*phase)));
        phase+=inc;if(phase>=1)phase-=1;
        return s;
    }
};
class Engine {
    std::array<Voice,8> voices{}; double rate=48000;
public:
    bool prepare(double r) noexcept {if(!supported(r))return false;rate=r;reset();return true;}
    void reset() noexcept {voices={};}
    bool on(int id,int note,double cents,double velocity,const Patch& p) noexcept {
        if(!std::isfinite(velocity)||velocity<=0){off(id);return false;}
        for(auto& v:voices)if(v.source.active&&v.source.id==id)return false;
        for(auto& v:voices)if(!v.source.active){v.start(id,note,cents,velocity,rate,p);return true;}
        return false;
    }
    void off(int id) noexcept {for(auto& v:voices)if(v.source.active&&v.source.id==id)v.source.off();}
    Stems tick() noexcept {
        Stems s;for(auto& v:voices){const auto x=v.tick();s.primary+=x.primary;s.middle+=x.middle;s.deep+=x.deep;}return s;
    }
    template<class T> void render(T* primary,T* middle,T* deep,int n) noexcept {
        for(int i=0;i<n;++i){const auto s=tick();if(primary)primary[i]=T(s.primary);if(middle)middle[i]=T(s.middle);if(deep)deep[i]=T(s.deep);}
    }
};
}
