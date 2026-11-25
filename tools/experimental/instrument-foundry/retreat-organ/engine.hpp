#pragma once
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
namespace mhac::organ {
constexpr double pi=3.14159265358979323846;
constexpr bool validRate(double r){return r>=1000.&&r<=2000000.;}
enum Param:unsigned { Mode, Dial, Blend, Rate, Gain, Count };
using Params=std::array<double,Count>;
constexpr Params defaults{1.,.5,0.,.3,.7};
inline double unit(double x,double fallback=0){return std::isfinite(x)?std::clamp(x,0.,1.):fallback;}
struct Relays {
    unsigned a=0,b=0;
    void visit(unsigned x){
        for(unsigned i=0;i<8;++i){const unsigned bit=1u<<i;
            if(x>=9+i){a|=bit;b|=bit;}
            else {if(x<(i==7?8:7-i))a&=~bit;if(x<8-i)b&=~bit;}
        }
    }
    static unsigned count(unsigned x){unsigned n=0;for(unsigned i=0;i<8;++i)n+=(x>>i)&1u;return n;}
    double mass(double blend) const{return (count(a)*(1.-blend)+count(b)*blend)/8.;}
};
constexpr unsigned pathSize(unsigned mode){return mode==1?33u:15u;}
constexpr unsigned pathLevel(unsigned mode,unsigned tick){
    if(mode==1)return tick<=16?tick:32-tick;
    return tick==0?0:(tick%2?16-(tick+1)/2:tick/2);
}
using State=std::array<std::uint8_t,4+4*Count>;
inline State encode(const Params& p){State s{'R','O','0','1'};for(unsigned i=0;i<Count;++i){auto q=std::uint32_t(std::llround(unit(p[i],defaults[i])*16777216.));for(unsigned j=0;j<4;++j)s[4+4*i+j]=std::uint8_t(q>>(8*j));}return s;}
inline bool decode(const State& s,Params& p){if(s[0]!='R'||s[1]!='O'||s[2]!='0'||s[3]!='1')return false;Params t{};for(unsigned i=0;i<Count;++i){std::uint32_t q=0;for(unsigned j=0;j<4;++j)q|=std::uint32_t(s[4+4*i+j])<<(8*j);if(q>16777216)return false;t[i]=q/16777216.;}p=t;return true;}
class Engine {
    struct Voice {bool active=false,releasing=false;int channel=0,pitch=0,id=-1;unsigned mode=0,tick=0,until=1,interval=1;Relays relays;double phase=0,omega=0,velocity=0,env=0,mass=0,carrier=0,side=0;};
    std::array<Voice,16> voices{};Params p=defaults;double sr=48000,gain=defaults[Gain],blend=defaults[Blend];
public:
    const Params& params() const{return p;}
    void set(unsigned id,double x){if(id<Count)p[id]=unit(x,p[id]);}
    void restore(const Params& q){for(unsigned i=0;i<Count;++i)set(i,q[i]);}
    bool reset(double r){if(!validRate(r))return false;sr=r;voices={};gain=p[Gain];blend=p[Blend];return true;}
    bool noteOn(int channel,int pitch,int id,double vel,double tuning=0){
        if(channel<0||channel>15||pitch<0||pitch>127||!std::isfinite(vel)||vel<=0)return false;
        Voice* slot=nullptr;for(auto& v:voices)if(!v.active){slot=&v;break;}if(!slot)return false;
        Voice v;v.active=true;v.channel=channel;v.pitch=pitch;v.id=id;v.velocity=unit(vel);
        v.mode=unsigned(std::llround(2*p[Mode]));v.interval=unsigned(std::llround(sr*(.025+.175*p[Rate])));v.until=v.interval;
        double cents=std::isfinite(tuning)?std::clamp(tuning,-1200.,1200.):0.;double hz=440*std::exp2((pitch-69+cents/100.)/12.);
        v.omega=2*pi*std::min(hz,.45*sr)/sr;
        auto fade=[&](double f){return std::clamp((.45-f/sr)/.05,0.,1.);};v.carrier=fade(hz);v.side=fade(2.5*hz);
        *slot=v;return true;
    }
    void noteOff(int channel,int pitch,int id){for(auto& v:voices)if(v.active&&v.channel==channel&&(id>=0?v.id==id:v.pitch==pitch))v.releasing=true;}
    unsigned active() const{unsigned n=0;for(const auto& v:voices)n+=v.active;return n;}
    double next(){
        const double slew=1./(.005*sr),release=1./(.02*sr);gain+=std::clamp(p[Gain]-gain,-slew,slew);blend+=std::clamp(p[Blend]-blend,-slew,slew);double sum=0;
        const unsigned dial=unsigned(std::llround(16*p[Dial]));
        for(auto& v:voices)if(v.active){
            if(v.releasing){v.env=std::max(0.,v.env-release);if(v.env<=1e-12){v.active=false;continue;}}else v.env=std::min(1.,v.env+slew);
            v.relays.visit(v.mode?pathLevel(v.mode,v.tick):dial);
            const double target=v.relays.mass(blend);v.mass+=std::clamp(target-v.mass,-slew,slew);
            const double s=std::sin(v.phase),ring=s*std::sin(1.5*v.phase);
            sum+=(.25+.75*v.mass)*((1-v.mass)*v.carrier*s+v.mass*v.side*ring)*v.velocity*v.env/16.;
            v.phase+=v.omega;if(v.phase>=4*pi)v.phase-=4*pi;
            if(v.mode&&v.tick+1<pathSize(v.mode)&&!--v.until){++v.tick;v.until=v.interval;}
        }
        const double y=.5*gain*sum;return std::abs(y)<1e-20?0.:y;
    }
};
}
