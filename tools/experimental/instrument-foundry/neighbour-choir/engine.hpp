#pragma once
#include <algorithm>
#include <array>
#include <cmath>
#include <complex>
#include <cstdint>
namespace mhac::neighbours {
constexpr double pi=3.14159265358979323846;
constexpr bool validRate(double r){return r>=1000.&&r<=2000000.;}
enum Param:unsigned { Topology, Intervention, Coupling, Decay, Gain, Count };
using Params=std::array<double,Count>;
constexpr Params defaults{0.,1.,.45,.65,.7};
inline double unit(double x,double fallback=0){return std::isfinite(x)?std::clamp(x,0.,1.):fallback;}
using State=std::array<std::uint8_t,4+4*Count>;
inline State encode(const Params& p){State s{'N','C','0','1'};for(unsigned i=0;i<Count;++i){auto q=std::uint32_t(std::llround(unit(p[i],defaults[i])*16777216.));for(unsigned j=0;j<4;++j)s[4+4*i+j]=std::uint8_t(q>>(8*j));}return s;}
inline bool decode(const State& s,Params& p){if(s[0]!='N'||s[1]!='C'||s[2]!='0'||s[3]!='1')return false;Params t{};for(unsigned i=0;i<Count;++i){std::uint32_t q=0;for(unsigned j=0;j<4;++j)q|=std::uint32_t(s[4+4*i+j])<<(8*j);if(q>16777216)return false;t[i]=q/16777216.;}p=t;return true;}
constexpr bool adjacent(bool shr,unsigned u,unsigned v){unsigned x=(u/4+4-v/4)%4,y=(u%4+4-v%4)%4;return shr?((x==0&&(y==1||y==3))||(y==0&&(x==1||x==3))||(x==y&&(x==1||x==3))):u!=v&&(x==0||y==0);}
using Neighbors=std::array<std::array<unsigned,6>,16>;
constexpr Neighbors graph(bool shr){Neighbors g{};for(unsigned i=0;i<16;++i){unsigned k=0;for(unsigned j=0;j<16;++j)if(adjacent(shr,i,j))g[i][k++]=j;}return g;}
constexpr std::array<Neighbors,2> graphs{graph(false),graph(true)};
using Field=std::array<double,16>;
inline Field witness(bool shr,unsigned u,unsigned v){Field c{},w{};if(u>=16||v>=16||u==v)return w;for(unsigned i=0;i<16;++i)c[i]=adjacent(shr,i,u)&&adjacent(shr,i,v)?1.:0.;for(unsigned i=0;i<16;++i)for(auto j:graphs[shr][i])w[i]+=c[i]*c[j];return w;}
using Complex=std::complex<double>;
using Wave=std::array<Complex,16>;
struct Propagator {
    Complex a{},b{},j{};
    static Propagator make(double omega,double theta,double damping){const auto carrier=std::polar(damping,omega);const Complex a=std::cos(2*theta),b(0,std::sin(2*theta)/2);return {carrier*a,carrier*b,carrier*(std::polar(1.,6*theta)-a-6.*b)/16.};}
    void step(Wave& x,bool shr) const{Wave next{};Complex total{};for(auto v:x)total+=v;const auto common=j*total;for(unsigned i=0;i<16;++i){Complex n{};for(auto k:graphs[shr][i])n+=x[k];next[i]=a*x[i]+b*n+common;}x=next;}
};
class Engine {
    struct Voice {bool active=false,releasing=false,shr=false,intervene=false;int channel=0,pitch=0,id=-1;unsigned age=0,trigger=0;double env=0,velocity=0,fade=0;Wave x{};Field injection{};Propagator prop{};};
    std::array<Voice,8> voices{};Params p=defaults;double sr=48000,gain=defaults[Gain];
public:
    const Params& params() const{return p;}
    void set(unsigned id,double x){if(id<Count)p[id]=unit(x,p[id]);}
    void restore(const Params& q){for(unsigned i=0;i<Count;++i)set(i,q[i]);}
    bool reset(double r){if(!validRate(r))return false;sr=r;voices={};gain=p[Gain];return true;}
    bool noteOn(int channel,int pitch,int id,double vel,double tuning=0){
        if(channel<0||channel>15||pitch<0||pitch>127||!std::isfinite(vel)||vel<=0)return false;
        Voice* slot=nullptr;for(auto& v:voices)if(!v.active){slot=&v;break;}if(!slot)return false;
        Voice v;v.active=true;v.channel=channel;v.pitch=pitch;v.id=id;v.velocity=unit(vel);v.shr=p[Topology]>=.5;v.intervene=p[Intervention]>=.5;v.trigger=unsigned(std::llround(.1*sr));v.x[0]=1.;v.injection=witness(v.shr,0,1);
        const double cents=std::isfinite(tuning)?std::clamp(tuning,-1200.,1200.):0.;const double hz=440*std::exp2((pitch-69+cents/100.)/12.);const double ratio=.35*p[Coupling];
        v.fade=std::clamp((.45-hz*(1+ratio)/sr)/.05,0.,1.);const double f=std::min(hz,.45*sr);v.prop=Propagator::make(2*pi*f/sr,2*pi*f*ratio/(6*sr),std::exp(-1/(sr*(.12+1.38*p[Decay]))));*slot=v;return true;
    }
    void noteOff(int channel,int pitch,int id){for(auto& v:voices)if(v.active&&v.channel==channel&&(id>=0?v.id==id:v.pitch==pitch))v.releasing=true;}
    unsigned active() const{unsigned n=0;for(const auto& v:voices)n+=v.active;return n;}
    double next(){const double attack=1/(.005*sr),release=1/(.04*sr);gain+=std::clamp(p[Gain]-gain,-attack,attack);double sum=0;
        for(auto& v:voices)if(v.active){if(v.releasing){v.env=std::max(0.,v.env-release);if(v.env<=1e-12){v=Voice{};continue;}}else v.env=std::min(1.,v.env+attack);
            if(v.age==v.trigger&&v.intervene&&!v.releasing)for(unsigned i=0;i<16;++i)v.x[i]+=.5*v.injection[i];
            if(v.age<=v.trigger)++v.age;
            sum+=v.x[0].real()*v.env*v.velocity*v.fade;
            v.prop.step(v.x,v.shr);for(auto& x:v.x)if(std::norm(x)<1e-40)x={};
        }
        const double y=std::clamp(gain*sum/32.,-.5,.5);return std::isfinite(y)&&std::abs(y)>=1e-20?y:0.;
    }
};
}
