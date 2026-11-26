#pragma once
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
namespace guest {
constexpr double pi=3.14159265358979323846;
struct Patch {
    std::array<int,4> motif{0,7,3,10};
    double stepsPerSecond=4, counterGain=.65;
    bool cite=false, adopt=false;
};
struct Frame {double left=0,right=0,base=0,counter=0;};
class Engine {
    struct Voice {
        bool active=false, releasing=false, continuation=false;
        int id=0, note=0;
        unsigned slot=0, position=0, length=1;
        double tuning=0, velocity=0, env=0, a=0,b=0, blend=0;
        double incA=0,incB=0;
        Patch patch{};
    };
    std::array<Voice,8> voices{};
    Patch patch{};
    double rate=48000, attack=1./240, release=1./1440;
    double increment(const Voice& v,int offset) const noexcept {
        return std::min(.45,440*std::exp2((v.note+offset-69+v.tuning/100)/12)/rate);
    }
    static double oscillator(double& phase,double increment) noexcept {
        phase+=increment;if(phase>=1)phase-=1;
        return std::sin(2*pi*phase);
    }
    void retune(Voice& v) noexcept {
        v.incA=increment(v,v.patch.motif[v.slot]);
        v.incB=increment(v,v.patch.motif[3-v.slot]+12);
    }
public:
    static constexpr unsigned capacity=8;
    bool prepare(double sr) noexcept {
        if(!std::isfinite(sr)||sr<1000||sr>2000000)return false;
        rate=sr;attack=1/std::max(1.,rate*.005);release=1/std::max(1.,rate*.03);reset();return true;
    }
    void reset() noexcept {voices={};}
    bool configure(Patch p) noexcept {
        if(!std::isfinite(p.stepsPerSecond)||!std::isfinite(p.counterGain))return false;
        p.stepsPerSecond=std::clamp(p.stepsPerSecond,1.,12.);
        p.counterGain=std::clamp(p.counterGain,0.,1.);
        for(int& x:p.motif)x=std::clamp(x,-12,12);
        patch=p;return true;
    }
    bool on(int id,int note,double tuning,double velocity) noexcept {
        if(!std::isfinite(velocity)||!std::isfinite(tuning)||note<0||note>127)return false;
        if(velocity==0){off(id);return false;}if(velocity<0)return false;
        for(const auto& v:voices)if(v.active&&!v.releasing&&v.id==id)return false;
        for(auto& v:voices)if(!v.active){
            v=Voice{};v.active=true;v.id=id;v.note=note;v.tuning=std::clamp(tuning,-1200.,1200.);
            v.velocity=std::min(1.,velocity);v.patch=patch;
            v.length=unsigned(std::lround(rate/patch.stepsPerSecond));retune(v);return true;
        }
        return false;
    }
    void off(int id) noexcept {for(auto& v:voices)if(v.active&&!v.releasing&&v.id==id)v.releasing=true;}
    Frame tick() noexcept {
        Frame f{};
        for(auto& v:voices)if(v.active){
            v.env=v.releasing?std::max(0.,v.env-release):std::min(1.,v.env+attack);
            if(v.env<=0&&v.releasing){v=Voice{};continue;}
            const double target=v.continuation&&v.patch.adopt?v.patch.counterGain:0;
            v.blend+=std::clamp(target-v.blend,-attack,attack);
            f.base+=.04*v.velocity*v.env*oscillator(v.a,v.incA);
            f.counter+=.025*v.velocity*v.env*v.blend*oscillator(v.b,v.incB);
            if(++v.position==v.length){v.position=0;v.slot=(v.slot+1)%4;if(v.slot==0)v.continuation=true;retune(v);}
        }
        f.left=f.base;f.right=f.base+f.counter;return f;
    }
    template<class T> void process(T* left,T* right,unsigned n) noexcept {
        for(unsigned i=0;i<n;++i){const auto f=tick();if(left&&left==right)left[i]=T((f.left+f.right)*.5);else{if(left)left[i]=T(right?f.left:(f.left+f.right)*.5);if(right)right[i]=T(left?f.right:(f.left+f.right)*.5);}}
    }
};
}
