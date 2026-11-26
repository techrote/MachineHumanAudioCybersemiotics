#pragma once
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include "resonance/modal.hpp"
namespace restbus {
enum class Domain { idle, held, rendered, manual };
enum class Destination { pitch, resonance, both };
class Clock {
    unsigned period_=1, partial_=0, index_=0;
    Domain domain_=Domain::idle;
public:
    void reset() noexcept {partial_=index_=0;}
    bool period(unsigned n) noexcept {if(!n)return false;period_=n;partial_=0;return true;}
    void domain(Domain d) noexcept {domain_=d;}
    unsigned index() const noexcept {return index_;}
    unsigned partial() const noexcept {return partial_;}
    void step() noexcept {if(domain_==Domain::manual)index_=(index_+1)%5;}
    void tick(bool held) noexcept {
        if(domain_==Domain::rendered||(domain_==Domain::idle&&!held)||(domain_==Domain::held&&held)){
            if(++partial_==period_){partial_=0;index_=(index_+1)%5;}
        }
    }
};
class Engine {
    struct Voice {bool active=false,held=false;int id=0;double phase=0,inc=0,env=0,velocity=0;bool modal=false;resonance::Bank bank{};};
    std::array<Voice,8> voices_{};
    Clock clock_;
    Destination destination_=Destination::pitch;
    double sr_=48000, attack_=1./240, release_=1./1440;
    static constexpr double tau=6.28318530717958647692;
public:
    static constexpr std::array<int,5> offsets{0,2,5,7,10};
    bool prepare(double sr,double seconds=.3) noexcept {
        if(!std::isfinite(sr)||sr<1000||sr>2000000||!std::isfinite(seconds)||seconds<.01||seconds>10)return false;
        sr_=sr;attack_=1/std::max(1.,sr*.005);release_=1/std::max(1.,sr*.03);
        clock_.period(unsigned(std::lround(sr*seconds)));reset();return true;
    }
    bool period(double seconds) noexcept {
        if(!std::isfinite(seconds)||seconds<.01||seconds>10)return false;
        return clock_.period(unsigned(std::lround(sr_*seconds)));
    }
    void reset() noexcept {voices_={};clock_.reset();}
    void domain(Domain d) noexcept {clock_.domain(d);}
    void step() noexcept {clock_.step();}
    void destination(Destination d) noexcept {destination_=d;}
    unsigned index() const noexcept {return clock_.index();}
    unsigned partial() const noexcept {return clock_.partial();}
    bool on(int id,int note,double tuning,double velocity) noexcept {
        if(note<0||note>127||!std::isfinite(tuning)||!std::isfinite(velocity)||velocity<=0)return false;
        for(const auto& v:voices_)if(v.held&&v.id==id)return false;
        for(auto& v:voices_)if(!v.active){
            double hz=440*std::exp2((note+(destination_==Destination::resonance?0:offsets[index()])-69+std::clamp(tuning,-1200.,1200.)/100)/12);
            v={true,true,id,0,std::min(.45,hz/sr_),0,std::min(1.,velocity)};
            v.modal=destination_!=Destination::pitch;
            if(v.modal&&!v.bank.strike(sr_,hz,velocity,index())){v={};return false;}
            return true;
        }
        return false;
    }
    void off(int id) noexcept {for(auto& v:voices_)if(v.held&&v.id==id){v.held=false;if(v.modal)v.bank.release();}}
    double tick() noexcept {
        bool held=false;double y=0;
        for(auto& v:voices_)if(v.active){
            held|=v.held;
            v.env=v.held?std::min(1.,v.env+attack_):std::max(0.,v.env-release_);
            if(!v.held&&v.env<=0){v={};continue;}
            if(v.modal){y+=v.bank.tick();continue;}
            v.phase+=v.inc;if(v.phase>=1)v.phase-=1;
            y+=.06*v.velocity*v.env*std::sin(tau*v.phase);
        }
        clock_.tick(held);return y;
    }
    template<class T> void process(T* l,T* r,unsigned n) noexcept {
        for(unsigned i=0;i<n;++i){T y=T(tick());if(l)l[i]=y;if(r&&r!=l)r[i]=y;}
    }
};
}
