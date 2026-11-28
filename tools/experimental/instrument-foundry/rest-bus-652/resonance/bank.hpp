#pragma once
#include "../rest.hpp"
#include "modal.hpp"
namespace restbus::resonance {
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
        }
        return false;
    }
    void off(int id) noexcept {for(auto& v:voices_)if(v.id==id)v.bank.release();}
    double tick() noexcept {double y=0;bool held=false;for(auto& v:voices_){held|=v.bank.held();if(v.bank.active())y+=v.bank.tick();}clock_.tick(held);return y;}
    template<class T> void process(T* l,T* r,unsigned n) noexcept {for(unsigned i=0;i<n;++i){const T y=T(tick());if(l)l[i]=y;if(r&&r!=l)r[i]=y;}}
};
}
