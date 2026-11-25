#pragma once
#include "winters.hpp"
#include <cstring>
namespace winters::live {
constexpr unsigned Count=11;
using Params=std::array<double,Count>;
constexpr Params defaults{0,1./3,2./3,1,0,0,0,.2,1,1,1};
inline double normalized(unsigned id,double x) noexcept {
    x=std::clamp(x,0.,1.);
    return id<4?std::round(x*3)/3:id<7?double(x>=.5):x;
}
using State=std::array<std::uint8_t,4+4*Count>;
inline State encode(const Params& p) noexcept {
    State s{'T','W','0','1'};
    for(unsigned i=0;i<Count;++i){float f=float((i==4||i==5)?0:p[i]);std::uint32_t u;std::memcpy(&u,&f,4);for(unsigned j=0;j<4;++j)s[4+4*i+j]=std::uint8_t(u>>(8*j));}return s;
}
inline bool decode(const std::uint8_t* s,std::size_t n,Params& p) noexcept {
    if(!s||n!=State{}.size()||s[0]!='T'||s[1]!='W'||s[2]!='0'||s[3]!='1')return false;
    Params q=defaults;
    for(unsigned i=0;i<Count;++i){std::uint32_t u=0;for(unsigned j=0;j<4;++j)u|=std::uint32_t(s[4+4*i+j])<<(8*j);float f;std::memcpy(&f,&u,4);if(!std::isfinite(f)||f<0||f>1||((i==4||i==5)&&f!=0))return false;q[i]=normalized(i,f);}
    p=q;return true;
}
struct Frame {double l=0,r=0,primary=0,middle=0,deep=0;};
class Engine {
    winters::Engine e;
    Params p=defaults;
    std::array<double,4> cents{};
    std::array<double,3> gain{{1,1,1}};
    double phase=0;
    void retune() noexcept {
        constexpr int intervals[]={0,3,7,10};
        for(unsigned i=0;i<e.voices.size();++i){auto& v=e.voices[i];if(!v.active)continue;for(int k=0;k<3;++k)v.target[k]=std::min(.45,440*std::exp2((v.note+intervals[e.score.token(k)]-69+cents[i]/100.)/12.)/e.rate);}
    }
public:
    const Params& parameters() const noexcept{return p;}
    const Score& score() const noexcept{return e.score;}
    bool prepare(double r) noexcept {if(!e.setup(r))return false;reset();return true;}
    void reset() noexcept {e.reset();cents={};phase=0;p[4]=p[5]=0;for(int i=0;i<4;++i)e.score.edit(i,int(std::lround(p[i]*3)));for(int i=0;i<3;++i)gain[i]=p[8+i];}
    void restore(const Params& values) noexcept {p=defaults;for(unsigned i=0;i<Count;++i)if(std::isfinite(values[i]))p[i]=normalized(i,values[i]);reset();}
    void parameter(unsigned i,double x) noexcept {
        if(i>=Count||!std::isfinite(x))return;
        x=normalized(i,x);if(x==p[i])return;p[i]=x;
        if(i<4){e.score.edit(int(i),int(std::lround(x*3)));retune();}
        else if(i==4){if(x)e.score.hold();else e.score.release();retune();}
        else if(i==5&&x){e.score.tick();retune();}
        else if(i==6)phase=0;
    }
    bool on(int id,int note,double tuning,double velocity) noexcept {
        if(!std::isfinite(velocity)||velocity<=0){if(velocity==0)off(id);return false;}
        if(!std::isfinite(tuning))return false;
        bool retrigger=false;
        for(const auto& v:e.voices)if(v.active&&v.id==id&&v.releasing)retrigger=true;
        if(!e.noteOn(id,note,velocity))return false;
        for(unsigned i=0;i<e.voices.size();++i)if(e.voices[i].active&&e.voices[i].id==id){cents[i]=std::clamp(tuning,-1200.,1200.);retune();if(!retrigger)e.voices[i].inc=e.voices[i].target;break;}
        return true;
    }
    void off(int id) noexcept {e.noteOff(id);}
    template<class Render> Frame tickWith(Render render) noexcept {
        if(p[6]){if(phase>=1-1e-10){phase=std::max(0.,phase-1);e.score.tick();retune();}phase+=(.5+7.5*p[7])/e.rate;}
        auto s=e.sampleWith(render);for(int i=0;i<3;++i){gain[i]+=std::clamp(p[8+i]-gain[i],-e.attack,e.attack);s[i]*=gain[i];}
        return {s[0]+.5*s[1],s[2]+.5*s[1],s[0],s[1],s[2]};
    }
    Frame tick() noexcept {return tickWith([](double phase,double,int){return std::sin(2*winters::Engine::pi*phase);});}
};
template<class T> void write(const Frame& f,T* const* main,unsigned channels,T* primary,T* middle,T* deep,unsigned i) noexcept {
    if(main&&channels==1&&main[0])main[0][i]=T((f.l+f.r)*.5);
    if(main&&channels==2){if(main[0])main[0][i]=T(f.l);if(main[1])main[1][i]=T(f.r);}
    if(primary)primary[i]=T(f.primary);
    if(middle)middle[i]=T(f.middle);
    if(deep)deep[i]=T(f.deep);
}
}
