#pragma once
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
namespace mhac::choir {
constexpr double pi=3.14159265358979323846;
constexpr bool validRate(double r){return r>=1000.&&r<=2000000.;}
enum Param:unsigned { Score, Seed, Rate, Colour, Gain, Count };
using Params=std::array<double,Count>;
constexpr Params defaults{85./255.,.5,.35,.5,.7};
inline double unit(double x,double fallback=0){return std::isfinite(x)?std::clamp(x,0.,1.):fallback;}
struct Word {std::array<int,72> symbols{};unsigned size=0;};
inline Word compile(unsigned mask){
    Word w;int x=0,hi=0,lo=0;
    auto go=[&](int target){while(x!=target){int d=target>x?1:-1;w.symbols[w.size++]=d;x+=d;}};
    for(unsigned i=0;i<8;++i)go(mask&(1u<<i)?++hi:--lo);
    go(0);std::reverse(w.symbols.begin(),w.symbols.begin()+w.size);return w;
}
using Bank=std::array<int,8>;
inline void step(Bank& b,int d){for(unsigned i=0;i<8;++i)b[i]=std::clamp(b[i]+d,0,int(i+1));}
using State=std::array<std::uint8_t,4+4*Count>;
inline State encode(const Params& p){State s{'R','C','0','1'};for(unsigned i=0;i<Count;++i){auto q=std::uint32_t(std::llround(unit(p[i],defaults[i])*16777216.));for(unsigned j=0;j<4;++j)s[4+4*i+j]=std::uint8_t(q>>(8*j));}return s;}
inline bool decode(const State& s,Params& p){if(s[0]!='R'||s[1]!='C'||s[2]!='0'||s[3]!='1')return false;Params t{};for(unsigned i=0;i<Count;++i){std::uint32_t q=0;for(unsigned j=0;j<4;++j)q|=std::uint32_t(s[4+4*i+j])<<(8*j);if(q>16777216)return false;t[i]=q/16777216.;}p=t;return true;}
class Engine {
    struct Voice {bool active=false,releasing=false;int channel=0,pitch=0,id=-1;Word word;Bank bank{};std::array<double,8> levels{},weights{};unsigned tick=0,until=0,interval=1;double phase=0,omega=0,velocity=0,env=0;};
    std::array<Voice,16> voices{};Params p=defaults;double sr=48000,gain=defaults[Gain];
public:
    const Params& params() const{return p;}
    void set(unsigned id,double x){if(id<Count)p[id]=unit(x,p[id]);}
    void restore(const Params& q){for(unsigned i=0;i<Count;++i)set(i,q[i]);}
    bool reset(double r){if(!validRate(r))return false;sr=r;voices={};gain=p[Gain];return true;}
    bool noteOn(int channel,int pitch,int id,double vel,double tuning=0){
        if(channel<0||channel>15||pitch<0||pitch>127||!std::isfinite(vel)||vel<=0)return false;
        Voice* slot=nullptr;for(auto& v:voices)if(!v.active){slot=&v;break;}if(!slot)return false;
        Voice v;v.active=true;v.channel=channel;v.pitch=pitch;v.id=id;v.velocity=unit(vel);
        v.word=compile(unsigned(std::llround(p[Score]*255)));v.interval=unsigned(std::llround(sr*(.015+.105*p[Rate])));v.until=v.interval;
        double cents=std::isfinite(tuning)?std::clamp(tuning,-1200.,1200.):0.;double hz=440*std::exp2((pitch-69+cents/100.)/12.);v.omega=2*pi*std::min(hz,.45*sr)/sr;
        for(unsigned i=0;i<8;++i){v.bank[i]=int(std::llround(p[Seed]*(i+1)));v.levels[i]=double(v.bank[i])/(i+1);double f=hz*(i+1)/sr;v.weights[i]=std::clamp((.45-f)/.05,0.,1.)*std::pow(double(i+1),-2.*(1.-p[Colour]));}
        *slot=v;return true;
    }
    void noteOff(int channel,int pitch,int id){for(auto& v:voices)if(v.active&&v.channel==channel&&(id>=0?v.id==id:v.pitch==pitch))v.releasing=true;}
    unsigned active() const{unsigned n=0;for(const auto& v:voices)n+=v.active;return n;}
    double next(){
        const double slew=1./(.005*sr),release=1./(.02*sr);gain+=std::clamp(p[Gain]-gain,-slew,slew);double sum=0;
        for(auto& v:voices)if(v.active){
            if(v.releasing){v.env=std::max(0.,v.env-release);if(v.env<=1e-12){v.active=false;continue;}}else v.env=std::min(1.,v.env+slew);
            double s=std::sin(v.phase),c=std::cos(v.phase),a=s,b=0,y=0;
            for(unsigned i=0;i<8;++i){double target=double(v.bank[i])/(i+1);v.levels[i]+=std::clamp(target-v.levels[i],-slew,slew);y+=a*v.levels[i]*v.weights[i];double n=2*c*a-b;b=a;a=n;}
            sum+=y*v.env*v.velocity/16.;v.phase+=v.omega;if(v.phase>=2*pi)v.phase-=2*pi;
            if(v.tick<v.word.size&&!--v.until){step(v.bank,v.word.symbols[v.tick++]);v.until=v.interval;}
        }
        double y=gain*sum/(1.+2.*std::abs(sum));return std::abs(y)<1e-20?0.:y;
    }
};
}
