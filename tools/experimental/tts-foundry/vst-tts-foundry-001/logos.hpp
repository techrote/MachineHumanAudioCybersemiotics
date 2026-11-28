#pragma once
#include "fixed_queue.hpp"
#include "phonetics.hpp"
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>

namespace mhac::tts {

constexpr double kTau = 6.283185307179586476925286766559;
inline bool valid_rate(double sr) noexcept { return std::isfinite(sr) && sr >= 8000.0 && sr <= 384000.0; }
inline double midi_hz(double note) noexcept { return 440.0 * std::pow(2.0, (note - 69.0) / 12.0); }
inline double clamp1(double x) noexcept { return std::max(-1.0, std::min(1.0, x)); }

struct LogosParameters {
    float pitchSemitones = 0.f;
    float rate = 1.f;
    float whisper = 0.f;
    float formantShiftSemitones = 0.f;
    float articulation = .65f;
    float gain = .75f;
};

class Logos {
    double sr_ = 48000.0;
    PhrasePlan plan_ = phrase_program(0);
    SpscQueue<PhrasePlan,4> pending_{};
    std::uint32_t noise_ = 0x12345678u;
    std::size_t phone_ = 0;
    std::uint64_t inPhone_ = 0;
    double phase_ = 0.0;
    double note_ = 60.0;
    double velocity_ = 0.0;
    bool gate_ = false;
    LogosParameters p_{};

    double noise() noexcept {
        noise_ ^= noise_ << 13; noise_ ^= noise_ >> 17; noise_ ^= noise_ << 5;
        return (double(noise_) / double(0xffffffffu)) * 2.0 - 1.0;
    }
    static double gaussian(double x, double mu, double width) noexcept {
        const double d=(x-mu)/width; return std::exp(-0.5*d*d);
    }
public:
    bool prepare(double sr) noexcept { if(!valid_rate(sr)) return false; sr_=sr; reset(); return true; }
    void reset() noexcept { phone_=0; inPhone_=0; phase_=0; velocity_=0; gate_=false; }
    void set_parameters(LogosParameters p) noexcept {
        p.pitchSemitones=std::clamp(p.pitchSemitones,-24.f,24.f);
        p.rate=std::clamp(p.rate,.35f,3.f);
        p.whisper=std::clamp(p.whisper,0.f,1.f);
        p.formantShiftSemitones=std::clamp(p.formantShiftSemitones,-18.f,18.f);
        p.articulation=std::clamp(p.articulation,0.f,1.f);
        p.gain=std::clamp(p.gain,0.f,1.f);
        p_=p;
    }
    LogosParameters parameters() const noexcept { return p_; }
    void set_plan(PhrasePlan p) noexcept { if(p.valid()){plan_=p;phone_=0;inPhone_=0;} }
    bool enqueue_plan(const PhrasePlan& p) noexcept { return p.valid() && pending_.push(p); }
    void begin_block() noexcept { PhrasePlan p{}; while(pending_.pop(p)) set_plan(p); }
    void note_on(double midi, double velocity) noexcept { note_=std::clamp(midi,0.0,127.0);velocity_=std::clamp(velocity,0.0,1.0);gate_=velocity_>0;phone_=0;inPhone_=0; }
    void note_off() noexcept { gate_=false; }
    bool active() const noexcept { return gate_ && velocity_>0.0; }

    double tick() noexcept {
        if (!active() || !plan_.count) return 0.0;
        const auto a = spec(plan_.phones[phone_]);
        const auto nextIndex = (phone_ + 1 < plan_.count) ? phone_+1 : phone_;
        const auto b = spec(plan_.phones[nextIndex]);
        const double dur = std::max(1.0, double(a.duration) * sr_ / double(p_.rate));
        const double u = std::min(1.0, double(inPhone_) / dur);
        const double transitionStart = 0.72 + 0.22*(1.0-double(p_.articulation));
        const double blend = u <= transitionStart ? 0.0 : std::min(1.0,(u-transitionStart)/(1.0-transitionStart));
        const auto lerp=[&](double x,double y){return x+(y-x)*blend;};
        const double shift = std::pow(2.0,double(p_.formantShiftSemitones)/12.0);
        const double f1=lerp(a.f1,b.f1)*shift, f2=lerp(a.f2,b.f2)*shift, f3=lerp(a.f3,b.f3)*shift;
        const double voiced=lerp(a.voiced,b.voiced)*(1.0-double(p_.whisper));
        const double hiss=std::max(lerp(a.noise,b.noise),double(p_.whisper)*0.65);
        const double gain=lerp(a.gain,b.gain)*double(p_.gain)*velocity_;
        const double f0=midi_hz(note_+double(p_.pitchSemitones));
        phase_ += f0/sr_; phase_ -= std::floor(phase_);
        double harmonic=0.0, norm=0.0;
        const unsigned maxH=24;
        for(unsigned h=1;h<=maxH;++h){
            const double fh=f0*double(h); if(fh>0.46*sr_) break;
            const double env=0.15 + 1.35*gaussian(fh,f1,120.0) + 1.0*gaussian(fh,f2,180.0) + .7*gaussian(fh,f3,240.0);
            const double amp=env/double(h);
            harmonic += amp*std::sin(kTau*phase_*double(h)); norm += amp;
        }
        if(norm>0.0) harmonic/=norm;
        const double onset=std::min(1.0,double(inPhone_)/(0.006*sr_+1.0));
        const double end=std::min(1.0,std::max(0.0,(dur-double(inPhone_))/(0.008*sr_+1.0)));
        const double y=(harmonic*voiced + noise()*hiss*0.28)*gain*onset*end;
        ++inPhone_;
        if(double(inPhone_)>=dur){
            inPhone_=0;
            if(phone_+1<plan_.count) ++phone_; else { phone_=0; if(!gate_) velocity_=0.0; }
        }
        return clamp1(y);
    }
};

} // namespace mhac::tts
