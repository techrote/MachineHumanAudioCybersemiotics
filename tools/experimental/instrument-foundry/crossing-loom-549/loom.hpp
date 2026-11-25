#pragma once
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
namespace loom {
struct Pair { double l=0,r=0; };
struct Patch { double spread=.25, seconds=.5, width=1; bool bounce=false; };
inline double finite(double x,double fallback=0) noexcept { return std::isfinite(x)?x:fallback; }
inline double bound(double x,double lo,double hi) noexcept {return std::clamp(finite(x),lo,hi);}
struct Voice {
    bool active=false, released=false; int id=0; std::uint64_t age=0,half=1,attack=1,release=1,remaining=0;
    double rate=48000,center=440,span=110,velocity=0,width=1,releaseStart=0; bool bounce=false;
    void start(int key,int note,double cents,double vel,double sr,Patch p) noexcept {
        *this=Voice{}; active=true; id=key; rate=sr;
        half=std::max<std::uint64_t>(1,std::llround(bound(p.seconds,.025,2)*rate));
        attack=std::max<std::uint64_t>(1,std::llround(.005*rate)); release=std::max<std::uint64_t>(1,std::llround(.04*rate));
        center=std::min(440*std::exp2((std::clamp(note,0,127)-69+bound(cents,-1200,1200)/100)/12),.25*rate);
        span=center*bound(p.spread,0,.8); velocity=bound(vel,0,1); width=bound(p.width,0,1); bounce=p.bounce;
    }
    double envelope() const noexcept {return released?releaseStart*double(remaining)/double(release):std::min(1.,double(age)/double(attack));}
    void off() noexcept {if(active&&!released){releaseStart=envelope();remaining=release;released=true;}}
    Pair tick() noexcept {
        if(!active)return {};
        const double t=double(age)/rate, T=double(half)/rate;
        const double u=std::min(t,2*T), drift=span*(u-u*u/(2*T))-span*std::max(0.,t-2*T);
        // Phase difference at the meeting is an integer multiple of 2pi (zero in cycles).
        const double mid=center*t, delta=drift-span*T/2;
        constexpr double tau=6.283185307179586476925286766559;
        const double a=std::sin(tau*std::remainder(mid-delta,1.)), b=std::sin(tau*std::remainder(mid+delta,1.));
        const double gain=.05*velocity*envelope(), m=(a+b)*.5, s=(a-b)*.5*width*(bounce&&age>=half?-1.:1.);
        if(age<UINT64_MAX)++age;
        if(released&&--remaining==0)active=false;
        return {gain*(m+s),gain*(m-s)};
    }
};
class Engine {
    std::array<Voice,8> voices{}; double rate=48000;
public:
    bool prepare(double sr) noexcept {if(!std::isfinite(sr)||sr<8000||sr>384000)return false; rate=sr;reset();return true;}
    void reset() noexcept {voices={};}
    bool on(int id,int note,double cents,double velocity,Patch p) noexcept {
        if(!std::isfinite(velocity)||velocity<=0){off(id);return false;}
        for(auto& v:voices)if(v.active&&v.id==id)return false;
        for(auto& v:voices)if(!v.active){v.start(id,note,cents,velocity,rate,p);return true;}
        return false;
    }
    void off(int id) noexcept {for(auto& v:voices)if(v.active&&v.id==id)v.off();}
    Pair tick() noexcept {Pair out; for(auto& v:voices){auto p=v.tick();out.l+=p.l;out.r+=p.r;}return out;}
    template<class T> void render(T* l,T* r,int n) noexcept {for(int i=0;i<n;++i){auto p=tick();if(r){l[i]=T(p.l);r[i]=T(p.r);}else l[i]=T((p.l+p.r)*.5);}}
};
}
