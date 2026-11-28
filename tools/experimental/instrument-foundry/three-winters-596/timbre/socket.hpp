#pragma once
#include "../live.hpp"
namespace winters::timbre {
// A separately addressable continuous modulation bank. No waveform/phase freeze.
class Socket {
    std::array<double,4> bank{}, snapshot{};
    unsigned moving=0, paused=0;
    double latched=0;
    bool held=false;
public:
    double slot(unsigned i) const noexcept {return i<bank.size()?bank[i]:0;}
    void edit(unsigned slot,double value) noexcept {
        if(slot<bank.size()&&std::isfinite(value))bank[slot]=std::clamp(value,0.,1.);
    }
    void hold() noexcept {if(!held){held=true;latched=bank[moving];snapshot=bank;}}
    void release() noexcept {held=false;}
    void tick() noexcept {moving=(moving+1)%4;if(!held)paused=(paused+1)%4;}
    std::array<double,3> values() const noexcept {
        return {held?latched:bank[moving],bank[paused],(held?snapshot:bank)[moving]};
    }
};
// Per-oscillator harmonic morph, with conservative high-note suppression.
inline double harmonic(double phase,double inc,double amount) noexcept {
    const double fundamental=std::sin(2*winters::Engine::pi*phase);
    const double mix=amount*std::clamp((.225-inc)/.045,0.,1.);
    if(mix==0)return fundamental;
    return (1-mix)*fundamental+mix*std::sin(4*winters::Engine::pi*phase);
}
class Engine {
    double slew=1./240;
    std::array<double,3> current{};
public:
    live::Engine pitch;
    Socket socket;
    bool prepare(double sr) noexcept {
        if(!pitch.prepare(sr))return false;
        slew=1/std::max(1.,sr*.005);socket=Socket{};current={};return true;
    }
    void reset() noexcept {pitch.reset();socket=Socket{};current={};}
    const std::array<double,3>& amounts() const noexcept {return current;}
    live::Frame sample() noexcept {
        auto target=socket.values();
        for(unsigned i=0;i<3;++i)current[i]+=std::clamp(target[i]-current[i],-slew,slew);
        return pitch.tickWith([this](double phase,double inc,int lane){return harmonic(phase,inc,current[unsigned(lane)]);});
    }
};
}
