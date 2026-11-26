#pragma once
#include "../rest.hpp"
namespace restbus::resonance {
// Struck modal bank: ratios and damping are captured at the attack.
struct Profile {std::array<double,4> ratio, decay;};
inline constexpr std::array<Profile,5> profiles{{
    {{1,2,3,4},{.65,.32,.16,.08}},
    {{1,1.5,2.5,3.5},{.8,.55,.25,.12}},
    {{1,2.76,5.4,8.93},{1.4,.8,.36,.18}},
    {{1,1.01,1.49,1.51},{1.1,1.1,.7,.7}},
    {{1,1.41421356237,2.2360679775,3.14159265359},{1.6,.9,.5,.24}}
}};
class Bank {
    struct Mode {double s=0,c=0,ds=0,dc=0;};
    std::array<Mode,4> modes_{};
    double env_=0,attack_=1./240,release_=1./1440;
    bool held_=false;
public:
    bool active() const noexcept {return held_||env_>0;}
    bool held() const noexcept {return held_;}
    bool strike(double sr,double hz,double velocity,unsigned profile) noexcept {
        if(!std::isfinite(sr)||sr<1000||sr>2000000||!std::isfinite(hz)||hz<=0||!std::isfinite(velocity)||velocity<=0||profile>=profiles.size())return false;
        constexpr double tau=6.28318530717958647692;
        constexpr std::array<double,4> weights{.4,.3,.2,.1};
        const auto& p=profiles[profile];
        for(unsigned i=0;i<4;++i){
            const double f=hz*p.ratio[i]/sr;
            const double a=std::min(1.,velocity)*weights[i]*std::clamp((.45-f)/.05,0.,1.);
            if(a==0){modes_[i]={};continue;}
            const double r=std::exp(-1/(sr*p.decay[i]));
            modes_[i]={0,a,r*std::sin(tau*f),r*std::cos(tau*f)};
        }
        env_=0;held_=true;attack_=1/(sr*.005);release_=1/(sr*.03);return true;
    }
    void release() noexcept {held_=false;}
    double tick() noexcept {
        env_=held_?std::min(1.,env_+attack_):std::max(0.,env_-release_);
        if(!active()){modes_={};return 0;}
        double sum=0;
        for(auto& m:modes_){const double s=m.s*m.dc+m.c*m.ds,c=m.c*m.dc-m.s*m.ds;
            if(std::abs(s)+std::abs(c)<1e-20){m={};continue;}m.s=s;m.c=c;sum+=s;}
        return .06*env_*std::clamp(sum,-1.,1.);
    }
};
class Instrument {
    struct Voice {Bank bank;int id=0;};
    std::array<Voice,8> voices_{};
    Clock clock_; double sr_=48000;
public:
    bool prepare(double sr,double seconds=.3) noexcept {
        if(!std::isfinite(sr)||sr<1000||sr>2000000||!std::isfinite(seconds)||seconds<.01||seconds>10)return false;
        sr_=sr;clock_.period(unsigned(std::lround(sr*seconds)));reset();return true;
    }
    void reset() noexcept {voices_={};clock_.reset();}
    void domain(Domain d) noexcept {clock_.domain(d);}
    void step() noexcept {clock_.step();}
    unsigned index() const noexcept {return clock_.index();}
    bool on(int id,int note,double velocity) noexcept {
        if(note<0||note>127)return false;
        if(velocity==0){off(id);return true;}
        for(const auto& v:voices_)if(v.bank.held()&&v.id==id)return false;
        for(auto& v:voices_)if(!v.bank.active()){
            if(!v.bank.strike(sr_,440*std::exp2((note-69)/12.),velocity,index()))return false;
            v.id=id;return true;
        }return false;
    }
    void off(int id) noexcept {for(auto& v:voices_)if(v.id==id)v.bank.release();}
    double tick() noexcept {double y=0;bool held=false;for(auto& v:voices_){held|=v.bank.held();if(v.bank.active())y+=v.bank.tick();}clock_.tick(held);return y;}
    template<class T> void process(T* l,T* r,unsigned n) noexcept {for(unsigned i=0;i<n;++i){const T y=T(tick());if(l)l[i]=y;if(r&&r!=l)r[i]=y;}}
};
}
