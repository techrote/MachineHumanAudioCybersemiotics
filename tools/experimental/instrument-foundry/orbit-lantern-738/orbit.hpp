#pragma once
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <cstddef>
namespace mhac::orbit {
constexpr double tau=6.283185307179586476925286766559;
// Includes the official validator's fractional and extreme test rates.
constexpr double minSampleRate=1000., maxSampleRate=2000000.;
inline bool validSampleRate(double rate) noexcept {
    return std::isfinite(rate)&&rate>=minSampleRate&&rate<=maxSampleRate;
}
struct Point { int x=0,y=0; bool operator==(Point p) const noexcept {return x==p.x&&y==p.y;} };
// Restricted lattice domain; reject out-of-domain input and noncontractive coefficients.
inline bool step(Point p,int a,int b,int q,bool nearest,Point& out) noexcept {
    if(q<2||q>1024||a<0||b<0||a>=q||b>=q||a*a+b*b>=q*q||
       p.x<-1000000||p.x>1000000||p.y<-1000000||p.y>1000000) return false;
    const auto quant=[=](std::int64_t v){const auto m=v<0?-v:v;
        const auto z=(m+(nearest?q/2:0))/q;return static_cast<int>(v<0?-z:z);};
    out={quant(std::int64_t(a)*p.x-std::int64_t(b)*p.y),quant(std::int64_t(b)*p.x+std::int64_t(a)*p.y)};
    return true;
}
struct Patch { unsigned blend=500,releaseMs=160; int cents=0;
    bool valid() const noexcept {return blend<=1000&&releaseMs>=10&&releaseMs<=1000&&cents>=-100&&cents<=100;} };
using Bytes=std::array<std::uint8_t,10>;
inline Bytes encode(Patch p) noexcept {if(!p.valid())return {};const unsigned c=static_cast<unsigned>(p.cents+100);
    return {{'O','L','0','1',std::uint8_t(p.blend),std::uint8_t(p.blend>>8),std::uint8_t(p.releaseMs),std::uint8_t(p.releaseMs>>8),std::uint8_t(c),std::uint8_t(c>>8)}};}
inline bool decode(const Bytes& b,Patch& p) noexcept {
    if(b[0]!='O'||b[1]!='L'||b[2]!='0'||b[3]!='1')return false;
    const auto u=[&](std::size_t i){return unsigned(b[i])|(unsigned(b[i+1])<<8);};
    const Patch candidate{u(4),u(6),int(u(8))-100};if(!candidate.valid())return false;p=candidate;return true;
}
struct Spectrum {
    // For an even cycle, the Nyquist term has no distinct negative-frequency partner.
    std::array<double,35> lx{},ly{},rx{},ry{};
    int harmonics=0,dominant=1;
    template<std::size_t N> bool build(Point start,int a,int b,int q) noexcept {
        static_assert(N<=68&&N%2==0);std::array<Point,N> pts{};auto p=start;
        for(std::size_t i=0;i<N;++i){pts[i]=p;if(!step(p,a,b,q,true,p))return false;
            if(p==start&&i+1<N)return false;}
        if(!(p==start))return false;
        *this=Spectrum{};harmonics=int(N/2);double best=0, boundL=0,boundR=0;
        for(int k=1;k<=harmonics;++k){const double scale=(k==harmonics?1.:2.)/double(N);
            for(std::size_t i=0;i<N;++i){const double t=tau*double(k)*double(i)/double(N);
                const double c=std::cos(t)*scale,s=std::sin(t)*scale;
                lx[k]+=pts[i].x*c;ly[k]+=pts[i].x*s;rx[k]+=pts[i].y*c;ry[k]+=pts[i].y*s;}
            const double l=std::hypot(lx[k],ly[k]),r=std::hypot(rx[k],ry[k]);boundL+=l;boundR+=r;
            if(l*l+r*r>best){best=l*l+r*r;dominant=k;}}
        const double bound=std::max({1.,boundL,boundR});
        for(int k=1;k<=harmonics;++k){lx[k]/=bound;ly[k]/=bound;rx[k]/=bound;ry[k]/=bound;}return true;
    }
    void sample(double phase,int limit,double& l,double& r) const noexcept {
        l=r=0;if(!std::isfinite(phase))return;limit=std::clamp(limit,0,harmonics);
        const double c=std::cos(phase),s=std::sin(phase);double x=c,y=s;
        for(int k=1;k<=limit;++k){l+=lx[k]*x+ly[k]*y;r+=rx[k]*x+ry[k]*y;
            const double nx=x*c-y*s;y=y*c+x*s;x=nx;}
    }
};
struct Event { enum class Kind {on,off,patch}; std::size_t offset=0; Kind kind=Kind::on; int id=0,note=60; double velocity=0; Patch patch{}; };
class Engine {
    struct Voice {bool active=false,releasing=false;int id=0;double level=0,velocity=0,releaseStep=0;
        double mix=0,phaseA=0,phaseB=0,incA=0,incB=0;int cutA=0,cutB=0;unsigned releaseSamples=0;};
    std::array<Voice,8> voices_{}; Spectrum a_{},b_{};Patch patch_{};double rate_=0,attack_=0;
    static void advance(double& phase,double inc) noexcept {phase+=inc;if(phase>=tau)phase-=tau;}
public:
    bool prepare(double rate) noexcept {if(!validSampleRate(rate))return false;
        if(!a_.build<4>({4,4},0,8,9)||!b_.build<68>({-16,4},8,4,9))return false;
        rate_=rate;attack_=1./std::ceil(.005*rate);reset();return true;}
    void reset() noexcept {voices_={};}
    bool setPatch(Patch p) noexcept {if(!p.valid())return false;patch_=p;return true;}
    Patch patch() const noexcept {return patch_;}
    int dominantB() const noexcept {return b_.dominant;}
    unsigned active() const noexcept {unsigned n=0;for(auto& v:voices_)if(v.active)++n;return n;}
    bool noteActive(int id) const noexcept {for(const auto& v:voices_)if(v.active&&v.id==id)return true;return false;}
    bool noteOn(int id,int note,double velocity,double tuning=0.) noexcept {
        if(rate_==0||id<0||note<0||note>127||!std::isfinite(velocity)||velocity<=0||velocity>1||!std::isfinite(tuning)||std::abs(tuning)>1200.)return false;
        for(auto& v:voices_)if(v.active&&v.id==id)return false;
        const double f=440.*std::exp2((double(note)-69.+(double(patch_.cents)+tuning)/100.)/12.);
        if(f>.45*rate_)return false;
        for(auto& v:voices_)if(!v.active){v=Voice{};v.active=true;v.id=id;v.velocity=velocity;v.mix=patch_.blend/1000.;
            const double fa=f/a_.dominant,fb=f/b_.dominant;
            v.incA=tau*fa/rate_;v.incB=tau*fb/rate_;
            v.cutA=std::min(a_.harmonics,int(std::floor(.45*rate_/fa)));
            v.cutB=std::min(b_.harmonics,int(std::floor(.45*rate_/fb)));
            v.releaseSamples=unsigned(std::ceil(rate_*patch_.releaseMs/1000.));return true;}
        return false;
    }
    bool noteOff(int id) noexcept {for(auto& v:voices_)if(v.active&&v.id==id){if(!v.releasing){v.releasing=true;v.releaseStep=v.level/v.releaseSamples;}return true;}return false;}
    void tick(double& l,double& r) noexcept {l=r=0;
        for(auto& v:voices_)if(v.active){if(v.releasing){if(v.releaseSamples<=1){v=Voice{};continue;}--v.releaseSamples;v.level=std::max(0.,v.level-v.releaseStep);}
            double al=0,ar=0,bl=0,br=0;
            if(v.mix<1.)a_.sample(v.phaseA,v.cutA,al,ar);
            if(v.mix>0.)b_.sample(v.phaseB,v.cutB,bl,br);
            const double g=.065*v.velocity*v.level;l+=g*((1.-v.mix)*al+v.mix*bl);r+=g*((1.-v.mix)*ar+v.mix*br);
            if(!v.releasing)v.level=std::min(1.,v.level+attack_);
            advance(v.phaseA,v.incA);advance(v.phaseB,v.incB);
        }
        l=std::clamp(l,-.52,.52);r=std::clamp(r,-.52,.52);
    }
    // Sorted offsets in [0,n), same-offset order is caller order. Invalid stream is nonmutating.
    // Admission failures (full voices, invalid notes, unknown note-off) are counted, not fatal.
    template<class T> bool render(T* l,T* r,std::size_t n,const Event* e,std::size_t count,unsigned& refused) noexcept {
        if(rate_==0||!l||!r||l==r||count>4096||(count&&!e))return false;
        for(std::size_t i=0;i<count;++i)if(e[i].offset>=n||(i&&e[i].offset<e[i-1].offset)||
            (e[i].kind!=Event::Kind::on&&e[i].kind!=Event::Kind::off&&e[i].kind!=Event::Kind::patch)||
            (e[i].kind==Event::Kind::patch&&!e[i].patch.valid()))return false;
        refused=0;std::size_t j=0;for(std::size_t i=0;i<n;++i){while(j<count&&e[j].offset==i){const auto& ev=e[j++];
            bool ok=ev.kind==Event::Kind::on?noteOn(ev.id,ev.note,ev.velocity):ev.kind==Event::Kind::off?noteOff(ev.id):setPatch(ev.patch);if(!ok)++refused;}
            double x=0,y=0;tick(x,y);l[i]=T(x);r[i]=T(y);}return true;
    }
};
} // namespace mhac::orbit
