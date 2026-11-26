#pragma once
#include <array>
#include <algorithm>
#include <cmath>
#include <cstdint>
#include "phase_memory.hpp"
namespace mhac::afterimage {
// Shared native/host rate contract. No rate-sized buffers are allocated.
inline bool supportsRate(double sr) noexcept {
    return std::isfinite(sr)&&sr>=1000.0&&sr<=2000000.0;
}
enum class Mode { absent, fixed, preview, full };
struct Pair { unsigned low=2, high=6; bool valid() const { return low<high && high<8; } };
inline unsigned mask(Mode m, Pair p) {
    if(m==Mode::full) return 7;
    if(m==Mode::fixed) return 1;
    if(m==Mode::preview) { unsigned x=p.low^p.high; return x&(~x+1u); }
    return 0;
}
struct Result { unsigned state; bool ambiguous; };
inline Result decode(unsigned observed, unsigned tag, unsigned m, Pair p) {
    if(observed!=p.low) return {observed,false};
    const bool l=(p.low&m)==tag, h=(p.high&m)==tag;
    return {l?p.low:p.high,l&&h}; // trusted, internally generated tag only
}
struct Patch { Pair pair; Mode mode=Mode::fixed; double minimumMs=80; double memory=0.8; };
class Engine {
    struct Voice {
        bool used=false, held=false; int id=0; unsigned original=0, tag=0, mask=0, captured=0;
        Pair pair; Mode mode=Mode::fixed; std::uint64_t age=0, minimum=0;
        double velocity=0, gain=0; std::array<double,4> phase{},step{},weight{};
        PhaseMemory pm; double pmMix=0;
    };
    std::array<Voice,8> voices{}, fading{};
    // One bounded fade slot per voice. Oldest-first order never overflows.
    std::array<unsigned,8> order{0,1,2,3,4,5,6,7};
    Patch patch{}; double rate=48000, attack=1.0/240, release=1.0/1440;
    unsigned history=0; bool ambiguous=false; double phaseMix=0;
    std::array<unsigned,3> archive{}; unsigned archiveSize=0, historyDepth=1;
public:
    bool prepare(double sr) {
        if(!supportsRate(sr)) return false;
        rate=sr; attack=1/(.005*sr); release=1/(.030*sr); reset(); return true;
    }
    void reset() { voices={}; fading={}; order={0,1,2,3,4,5,6,7}; history=0; ambiguous=false; archive={}; archiveSize=0; }
    bool configure(Patch p) {
        if(!p.pair.valid()||static_cast<unsigned>(p.mode)>3||!std::isfinite(p.minimumMs)||p.minimumMs<0||p.minimumMs>2000||!std::isfinite(p.memory)||p.memory<0||p.memory>1) return false;
        patch=p; return true;
    }
    // Captured at note-on, never changes existing voices.
    bool setPhaseMix(double mix) noexcept {
        if(!std::isfinite(mix)||mix<0||mix>1)return false;
        phaseMix=mix;return true;
    }
    unsigned remembered() const { return history; }
    // Native experimental control; affects future note onsets only.
    bool setHistoryDepth(unsigned depth) noexcept {
        if(depth<1||depth>3) return false;
        historyDepth=depth; return true;
    }
    unsigned rememberedCount() const noexcept { return archiveSize; }
    unsigned rememberedAt(unsigned index) const noexcept {
        return index<archiveSize?archive[index]:history;
    }
    bool lastAmbiguous() const { return ambiguous; }
    unsigned active() const { unsigned n=0; for(unsigned i=0;i<voices.size();++i) n+=voices[i].used||fading[i].used; return n; }
    bool off(int id, bool commit=true) {
        for(auto& v:voices) if(v.used&&v.held&&v.id==id) {
            v.held=false;
            if(commit&&v.age>=v.minimum) {
                const Pair p=v.mode==Mode::preview?v.pair:patch.pair;
                const auto r=decode(v.original==p.high?p.low:v.original,v.tag,v.mask,p);
                history=r.state; ambiguous=r.ambiguous;
                archive[2]=archive[1]; archive[1]=archive[0]; archive[0]=history;
                archiveSize=std::min(3u,archiveSize+1u);
            }
            return true;
        }
        return false;
    }
    // A non-null displaced pointer opts into bounded replacement. A held
    // victim is cancelled (never commits history); released victims already
    // completed their gesture. Negative displaced means no held victim.
    bool on(int id, int pitch, double velocity, double cents=0, int* displaced=nullptr) {
        if(displaced) *displaced=-1;
        if(id<0||pitch<0||pitch>127||!std::isfinite(velocity)||velocity<0||velocity>1||!std::isfinite(cents)||std::abs(cents)>1200) return false;
        if(velocity==0) return off(id);
        for(const auto& v:voices) if(v.used&&v.held&&v.id==id) return false;
        unsigned slot=static_cast<unsigned>(voices.size());
        for(unsigned i=0;i<voices.size();++i) if(!voices[i].used&&!fading[i].used) { slot=i; break; }
        if(slot==voices.size()&&displaced) {
            // Releasing voices first; then oldest held voice. A slot already
            // crossfading cannot be replaced until its fade has completed.
            for(unsigned i:order) if(!fading[i].used&&!voices[i].held) { slot=i; break; }
            if(slot==voices.size()) for(unsigned i:order) if(!fading[i].used) { slot=i; break; }
        }
        if(slot<voices.size()) {
            auto& v=voices[slot];
            if(v.used) {
                if(v.held) *displaced=v.id;
                if(v.gain>0) { fading[slot]=v; fading[slot].held=false; }
            }
            const auto pos=std::find(order.begin(),order.end(),slot);
            std::rotate(pos,pos+1,order.end());
            v={}; v.used=v.held=true; v.id=id; v.velocity=velocity; v.original=static_cast<unsigned>(pitch)%8;
            v.mode=patch.mode; v.pair=patch.pair; v.mask=mask(v.mode,v.pair); v.tag=v.original&v.mask;
            v.captured=history; v.minimum=static_cast<std::uint64_t>(std::ceil(rate*patch.minimumMs/1000));
            const double f=440*std::exp2((pitch-69+cents/100)/12);
            const unsigned h1=rememberedAt(0), h2=rememberedAt(historyDepth>=2?1:0),
                           h3=rememberedAt(historyDepth>=3?2:0);
            if(phaseMix>0&&patch.memory>0){
                const double beta=.2+.12*h1+.06*h3, ratio=1.25+.25*h2;
                if(v.pm.configure(rate,f,ratio,beta))
                    v.pmMix=phaseMix*patch.memory*std::clamp((.45-f/rate)/.05,0.,1.);
            }
            const std::array<double,4> ratios{1,2.0+h1*.25,3.0+h2*.5,5.0+h3*.75};
            const std::array<double,4> w{1,.5*patch.memory,.3*patch.memory,.2*patch.memory};
            double sum=0;
            for(unsigned k=0;k<4;++k) { const double hz=f*ratios[k]; v.step[k]=hz/rate; v.weight[k]=w[k]*std::clamp((.45-hz/rate)/.05,0.0,1.0); sum+=v.weight[k]; }
            for(auto& a:v.weight) a/=std::max(1.0,sum);
            return true;
        }
        return false; // all slots occupied or already crossfading
    }
private:
    double tickVoice(Voice& v, bool forced) {
        if(v.used) {
            if(v.held) { v.gain=std::min(1.0,v.gain+attack); if(v.age<v.minimum) ++v.age; }
            else { v.gain=std::max(0.0,v.gain-(forced?attack:release)); if(v.gain<=1e-12) { v={}; return 0; } }
            double y=0;
            for(unsigned k=0;k<4;++k) if(v.weight[k]>0) { y+=v.weight[k]*std::sin(6.2831853071795864769*v.phase[k]); v.phase[k]+=v.step[k]; if(v.phase[k]>=1) v.phase[k]-=1; }
            if(v.pmMix>0)y=(1-v.pmMix)*y+v.pmMix*v.pm.tick();
            return .065*v.velocity*v.gain*y;
        }
        return 0;
    }
public:
    double tick() {
        double out=0;
        for(unsigned i=0;i<voices.size();++i) {
            out+=tickVoice(voices[i],false);
            if(fading[i].used) out+=tickVoice(fading[i],true);
        }
        return std::clamp(out,-.52,.52);
    }
    template<class T> void render(T* left,T* right,unsigned frames) {
        for(unsigned i=0;i<frames;++i) { const T s=static_cast<T>(tick()); if(left) left[i]=s; if(right) right[i]=s; }
    }
};
}
