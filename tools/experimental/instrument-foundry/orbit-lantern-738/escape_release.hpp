#pragma once
#include "orbit.hpp"
namespace mhac::orbit::escape {
// Fixed witness from PR #265; zero-based indices of truncation updates.
constexpr std::array<unsigned,9> interventions{12,30,36,42,44,55,57,58,59};
constexpr unsigned steps=60;
struct Route {
    std::array<Point,steps+1> states{};
    std::array<double,steps+1> gain{};
    bool prepare() noexcept {
        states[0]={-16,4}; gain[0]=1.; unsigned j=0;
        for(unsigned i=0;i<steps;++i){
            const bool truncate=j<interventions.size()&&i==interventions[j];
            if(truncate)++j;
            if(!step(states[i],8,4,9,!truncate,states[i+1]))return false;
            const auto p=states[i+1];
            gain[i+1]=std::min(1.,double(p.x*p.x+p.y*p.y)/272.);
        }
        return j==interventions.size()&&states.back()==Point{};
    }
    // Time-expanded energy envelope, not direct audio-rate state iteration.
    double sample(unsigned elapsed,unsigned duration) const noexcept {
        if(!duration||elapsed>=duration)return 0.;
        const double t=double(elapsed)*steps/duration;
        const auto i=std::min(steps-1,unsigned(t));
        const double fraction=t-i;
        return gain[i]+fraction*(gain[i+1]-gain[i]);
    }
};
// Independent native instrument. Uses Orbit's spectrum and OL01 patch, but release
// mode is an explicit note-off event, not a new persisted or VST3 parameter.
class Instrument {
    struct Voice { bool active=false,releasing=false,intervened=false; int id=0;
        double level=0.,releaseLevel=0.,velocity=0.,mix=0.,a=0.,b=0.,da=0.,db=0.;
        int cutA=0,cutB=0; unsigned duration=0,elapsed=0; };
    std::array<Voice,8> voices_{}; Spectrum a_{},b_{}; Route route_{};
    double rate_=0.,attack_=0.; Patch patch_{};
public:
    bool prepare(double rate) noexcept {
        if(!validSampleRate(rate))return false;
        if(!a_.build<4>({4,4},0,8,9)||!b_.build<68>({-16,4},8,4,9)||!route_.prepare())return false;
        rate_=rate;attack_=1./std::ceil(.005*rate);reset();return true;
    }
    void reset() noexcept {voices_={};}
    bool setPatch(Patch p) noexcept {if(!p.valid())return false;patch_=p;return true;}
    unsigned active() const noexcept {unsigned n=0;for(const auto& v:voices_)n+=v.active;return n;}
    bool on(int id,int note,double velocity) noexcept {
        if(rate_==0||id<0||note<0||note>127||!std::isfinite(velocity)||velocity<=0||velocity>1)return false;
        for(const auto& v:voices_)if(v.active&&v.id==id)return false;
        const double f=440.*std::exp2((double(note)-69.+patch_.cents/100.)/12.);
        if(f>.45*rate_)return false;
        for(auto& v:voices_)if(!v.active){
            v={};v.active=true;v.id=id;v.velocity=velocity;v.mix=patch_.blend/1000.;
            const double fa=f/a_.dominant,fb=f/b_.dominant;
            v.da=tau*fa/rate_;v.db=tau*fb/rate_;
            v.cutA=std::min(a_.harmonics,int(std::floor(.45*rate_/fa)));
            v.cutB=std::min(b_.harmonics,int(std::floor(.45*rate_/fb)));
            v.duration=unsigned(std::ceil(rate_*patch_.releaseMs/1000.));return true;
        }
        return false;
    }
    bool off(int id,bool intervened) noexcept {
        for(auto& v:voices_)if(v.active&&v.id==id){
            if(!v.releasing){v.releasing=true;v.intervened=intervened;v.releaseLevel=v.level;}
            return true;
        }
        return false;
    }
    void tick(double& l,double& r) noexcept {
        l=r=0.;
        for(auto& v:voices_)if(v.active){
            if(v.releasing){
                if(++v.elapsed>=v.duration){v={};continue;}
                v.level=v.releaseLevel*(v.intervened?route_.sample(v.elapsed,v.duration):1.-double(v.elapsed)/v.duration);
            }
            double al=0.,ar=0.,bl=0.,br=0.;
            if(v.mix<1.)a_.sample(v.a,v.cutA,al,ar);
            if(v.mix>0.)b_.sample(v.b,v.cutB,bl,br);
            const double g=.065*v.velocity*v.level;
            l+=g*((1.-v.mix)*al+v.mix*bl);r+=g*((1.-v.mix)*ar+v.mix*br);
            if(!v.releasing)v.level=std::min(1.,v.level+attack_);
            v.a+=v.da;if(v.a>=tau)v.a-=tau;
            v.b+=v.db;if(v.b>=tau)v.b-=tau;
        }
        l=std::clamp(l,-.52,.52);r=std::clamp(r,-.52,.52);
    }
};
} // namespace mhac::orbit::escape
