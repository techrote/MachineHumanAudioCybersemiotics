#pragma once
#include "logos.hpp"
#include <array>
#include <algorithm>
#include <cmath>
#include <cstdint>

namespace mhac::tts {

struct ArticulumParameters {
    float tongueFront = .5f;
    float tongueHeight = .5f;
    float lipRound = .25f;
    float aspiration = .08f;
    float nasal = .05f;
    float pitchSemitones = 0.f;
    float gain = .8f;
};

class Articulum {
    static constexpr std::size_t N=24;
    double sr_=48000.0;
    std::array<double,N> right_{};
    std::array<double,N> left_{};
    std::array<double,N> area_{};
    std::array<double,N> target_{};
    std::uint32_t noise_=0x9e3779b9u;
    double phase_=0.0,note_=60.0,velocity_=0.0,nasalState_=0.0;
    bool gate_=false;
    ArticulumParameters p_{};

    double noise() noexcept {
        noise_^=noise_<<13;noise_^=noise_>>17;noise_^=noise_<<5;
        return (double(noise_)/double(0xffffffffu))*2.0-1.0;
    }
    void rebuild_target() noexcept {
        for(std::size_t i=0;i<N;++i) target_[i]=1.0;
        const double center=5.0 + double(p_.tongueFront)*(double(N)-10.0);
        const double depth=0.78*double(p_.tongueHeight);
        for(std::size_t i=0;i<N;++i){
            const double d=(double(i)-center)/3.5;
            target_[i]=std::max(.16,1.0-depth*std::exp(-0.5*d*d));
        }
        const double lip=std::clamp(double(p_.lipRound),0.0,1.0);
        target_[N-1]=std::max(.12,1.0-.72*lip);
        target_[N-2]=std::max(.16,1.0-.48*lip);
        target_[N-3]=std::max(.20,1.0-.28*lip);
        // A modest pharyngeal expansion keeps the model from collapsing into a single constriction.
        target_[2]*=1.15; target_[3]*=1.10;
    }
public:
    bool prepare(double sr) noexcept {
        if(!valid_rate(sr)) return false;
        sr_=sr;
        reset();
        for(auto& a:area_) a=1.0;
        rebuild_target();
        return true;
    }
    void reset() noexcept { right_.fill(0.0);left_.fill(0.0);phase_=0;velocity_=0;gate_=false;nasalState_=0; }
    void set_parameters(ArticulumParameters p) noexcept {
        p.tongueFront=std::clamp(p.tongueFront,0.f,1.f);p.tongueHeight=std::clamp(p.tongueHeight,0.f,1.f);
        p.lipRound=std::clamp(p.lipRound,0.f,1.f);p.aspiration=std::clamp(p.aspiration,0.f,1.f);
        p.nasal=std::clamp(p.nasal,0.f,1.f);p.pitchSemitones=std::clamp(p.pitchSemitones,-24.f,24.f);p.gain=std::clamp(p.gain,0.f,1.f);
        p_=p; rebuild_target();
    }
    ArticulumParameters parameters() const noexcept { return p_; }
    void note_on(double midi,double velocity) noexcept {note_=std::clamp(midi,0.0,127.0);velocity_=std::clamp(velocity,0.0,1.0);gate_=velocity_>0;}
    void note_off() noexcept {gate_=false;}
    bool active() const noexcept {return gate_&&velocity_>0;}
    void begin_block() noexcept {}

    double tick() noexcept {
        const double f0=midi_hz(note_+double(p_.pitchSemitones));
        phase_ += f0/sr_; phase_-=std::floor(phase_);
        const double open=phase_<0.62 ? std::sin(3.14159265358979323846*phase_/0.62) : 0.0;
        const double glottal=(open*open*2.0-0.65) * (active()?velocity_:0.0);
        const double excitation=glottal + noise()*double(p_.aspiration)*0.22*velocity_;
        for(std::size_t i=0;i<N;++i) area_[i]+=0.0015*(target_[i]-area_[i]);
        std::array<double,N> nr{}; std::array<double,N> nl{};
        nr[0]=0.985*(excitation + 0.55*left_[0]);
        for(std::size_t i=0;i+1<N;++i){
            const double denom=area_[i]+area_[i+1];
            const double k=std::clamp((area_[i]-area_[i+1])/std::max(1e-9,denom),-.82,.82);
            const double ri=right_[i], li=left_[i+1];
            nr[i+1]=0.997*((1.0+k)*ri - k*li);
            nl[i]=0.997*(k*ri + (1.0-k)*li);
        }
        nl[N-1]=-0.78*right_[N-1];
        const double lip=right_[N-1]*0.42;
        right_=nr; left_=nl;
        nasalState_ = 0.94*nasalState_ + 0.06*(right_[7]-left_[7]);
        const double y=(lip*(1.0-double(p_.nasal)) + nasalState_*double(p_.nasal)*0.38)*double(p_.gain);
        return clamp1(y);
    }
};

} // namespace mhac::tts
