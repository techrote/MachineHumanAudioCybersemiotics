#pragma once
#include "../engine.hpp"
namespace mhac::neighbours {
// Independent one-shot resonator. Configure only before starting a note.
struct AnchorPatch {
    bool shr=false;
    unsigned root=0, second=1;
    double hz=220, coupling=.45, decay=.9, time=.1, strength=.5;
};
class AnchorVoice {
    Wave field{};
    Field injection{};
    Propagator prop{};
    unsigned root=0, age=0, trigger=0;
    double rate=48000, env=0, level=0;
    bool held=false, running=false, fired=false;
public:
    bool start(const AnchorPatch& p,double sr,double velocity=1){
        if(!validRate(sr)||p.root>=16||p.second>=16||p.root==p.second||
           !std::isfinite(p.hz)||p.hz<=0||!std::isfinite(p.decay)||p.decay<.01||p.decay>10||
           !std::isfinite(p.time)||p.time<0||p.time>2||!std::isfinite(velocity)||velocity<=0)return false;
        *this=AnchorVoice{};rate=sr;root=p.root;field[root]=1;
        const double ratio=.35*unit(p.coupling), f=std::min(p.hz,.45*sr);
        level=unit(velocity)*std::clamp((.45-p.hz*(1+ratio)/sr)/.05,0.,1.)/16;
        prop=Propagator::make(2*pi*f/sr,2*pi*f*ratio/(6*sr),std::exp(-1/(sr*p.decay)));
        injection=witness(p.shr,p.root,p.second);for(auto& x:injection)x*=unit(p.strength);
        trigger=unsigned(std::llround(p.time*sr));held=running=true;shr=p.shr;return true;
    }
    void release(){held=false;}
    bool active() const{return running;}
    bool intervened() const{return fired;}
    double next(){
        if(!running)return 0;
        env=held?std::min(1.,env+1/(.005*rate)):std::max(0.,env-1/(.04*rate));
        if(!held&&env<=1e-12){running=false;field={};return 0;}
        if(!fired&&held&&age==trigger){for(unsigned i=0;i<16;++i)field[i]+=injection[i];fired=true;}
        if(age<=trigger)++age;
        const double y=field[root].real()*env*level;
        prop.step(field,shr);for(auto& x:field)if(std::norm(x)<1e-40)x={};
        return std::isfinite(y)&&std::abs(y)>=1e-20?std::clamp(y,-.25,.25):0.;
    }
private:
    bool shr=false;
};
}
