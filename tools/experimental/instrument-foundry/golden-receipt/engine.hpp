#pragma once
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <limits>
namespace mhac::golden {
constexpr double pi=3.14159265358979323846;
constexpr double phi=1.6180339887498948482;
enum Param: unsigned { Shape, Delete, Span, Width, Gain, Count };
using Params=std::array<double,Count>;
constexpr Params defaults{0,0,.4,.5,.7};
inline double unit(double v,double fallback=0){return std::isfinite(v)?std::clamp(v,0.,1.):fallback;}
struct Motif {std::array<double,4> t{}; unsigned count=0;};
inline Motif motif(bool equal,unsigned deletion){
    const double a=equal?1.:phi;
    const std::array<double,4> p{0,a,a+1,2*a+1};
    if(deletion==0||deletion>4)return {{0,p[1]/p[3],p[2]/p[3],1},4};
    if(!equal)return {{0,(deletion==1||deletion==3)?1./(phi*phi):1./phi,1,0},3};
    Motif m;for(unsigned i=0;i<4;++i)if(i+1!=deletion)m.t[m.count++]=p[i];
    const double first=m.t[0],span=m.t[2]-first;
    for(unsigned i=0;i<3;++i)m.t[i]=(m.t[i]-first)/span;
    return m;
}
// Stable, little-endian Q24 parameter state. No transient voice state persisted.
using State=std::array<std::uint8_t,4+4*Count>;
inline State encode(const Params& p){State s{'G','R','0','1'};for(unsigned i=0;i<Count;++i){auto q=std::uint32_t(std::llround(unit(p[i],defaults[i])*16777216.));for(unsigned j=0;j<4;++j)s[4+4*i+j]=std::uint8_t(q>>(8*j));}return s;}
inline bool decode(const State& s,Params& p){if(s[0]!='G'||s[1]!='R'||s[2]!='0'||s[3]!='1')return false;Params tmp{};for(unsigned i=0;i<Count;++i){std::uint32_t q=0;for(unsigned j=0;j<4;++j)q|=std::uint32_t(s[4+4*i+j])<<(8*j);if(q>16777216)return false;tmp[i]=q/16777216.;}p=tmp;return true;}
class Engine {
    struct Voice {bool active=false,releasing=false;int channel=0,pitch=0,id=-1;unsigned count=0;std::array<std::uint32_t,4> onset{};std::uint32_t age=0,width=0,end=0,release=0;double omega=0,velocity=0;};
    std::array<Voice,16> voices{}; Params p=defaults; double sr=48000,gain=defaults[Gain]; std::uint32_t releaseSamples=480;
public:
    const Params& params() const{return p;}
    void set(unsigned id,double v){if(id<Count)p[id]=unit(v,p[id]);}
    void restore(const Params& q){for(unsigned i=0;i<Count;++i)set(i,q[i]);}
    bool reset(double rate){if(!std::isfinite(rate)||rate<8000||rate>384000)return false;sr=rate;voices={};gain=p[Gain];releaseSamples=std::uint32_t(std::round(sr*.01));return true;}
    bool noteOn(int channel,int pitch,int id,double vel,double tuning=0){
        if(pitch<0||pitch>127||channel<0||channel>15||!std::isfinite(vel)||vel<=0)return false;
        Voice* slot=nullptr;for(auto& v:voices)if(!v.active){slot=&v;break;}if(!slot)return false; // drop excess, no discontinuous steals
        Voice v;v.active=true;v.channel=channel;v.pitch=pitch;v.id=id;v.velocity=unit(vel);
        const auto m=motif(p[Shape]>=.5,unsigned(std::llround(p[Delete]*4)));v.count=m.count;
        const double span=.2+1.3*p[Span];v.width=std::uint32_t(std::round(sr*(.015+.065*p[Width])));
        for(unsigned i=0;i<v.count;++i)v.onset[i]=std::uint32_t(std::llround(m.t[i]*span*sr));
        v.end=v.onset[v.count-1]+v.width;
        const double cents=std::isfinite(tuning)?std::clamp(tuning,-1200.,1200.):0.;
        const double hz=440*std::exp2((pitch-69+cents/100.)/12.);v.omega=2*pi*std::min(hz,.45*sr)/sr;
        *slot=v;return true;
    }
    void noteOff(int channel,int pitch,int id){for(auto& v:voices)if(v.active&&!v.releasing&&v.channel==channel&&(id>=0?v.id==id:v.pitch==pitch)){v.releasing=true;v.release=0;}}
    unsigned active() const{unsigned n=0;for(auto& v:voices)n+=v.active;return n;}
    double next(){
        const double step=1./(.005*sr);gain+=std::clamp(p[Gain]-gain,-step,step);
        double sum=0;
        for(auto& v:voices)if(v.active){
            double envelope=1.;if(v.releasing)envelope=1.-double(v.release)/releaseSamples;
            double y=0;for(unsigned i=0;i<v.count;++i)if(v.age>=v.onset[i]){const auto dt=v.age-v.onset[i];if(dt<v.width){const double w=std::sin(pi*dt/v.width);y+=w*w*std::sin(v.omega*dt);}}
            // Same per-pulse gain for complete and damaged motifs. Soft-bound the voice sum.
            sum+=y*v.velocity*envelope/8.;
            ++v.age;if(v.releasing)++v.release;
            if(v.age>=v.end||(v.releasing&&v.release>=releaseSamples))v.active=false;
        }
        const double y=(sum/(1.+2.*std::abs(sum)))*gain;return std::abs(y)<1e-20?0.:y;
    }
};
}
