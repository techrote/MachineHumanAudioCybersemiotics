#pragma once
#include "params.hpp"
#include "repeated-557/cycle.hpp"
namespace loom::live {
constexpr unsigned Count=21;
using Params=std::array<double,Count>;
constexpr Params defaults{.3125,.475/1.975,1.,0.,0.};
inline void set(Params& p,unsigned i,double x) noexcept {
    if(i<Count&&std::isfinite(x))p[i]=i>=3?double(x>=.5):std::clamp(x,0.,1.);
}
inline bool supported(double sr) noexcept {return std::isfinite(sr)&&sr>=1000&&sr<=2000000;}
inline std::uint16_t mask(const Params& p) noexcept {
    std::uint16_t m=0;for(unsigned i=0;i<16;++i)if(p[5+i]>=.5)m|=std::uint16_t(1u<<i);return m;
}
using State=std::array<std::uint8_t,4+Count*4>;
inline State encode(const Params& p) noexcept {
    State s{'C','L','0','2'};
    for(unsigned i=0;i<Count;++i){float f=float(p[i]);std::uint32_t u;std::memcpy(&u,&f,4);for(unsigned j=0;j<4;++j)s[4+4*i+j]=std::uint8_t(u>>(8*j));}return s;
}
inline bool decode(const std::uint8_t* s,std::size_t n,Params& p) noexcept {
    if(!s||n<4||s[0]!='C'||s[1]!='L'||s[2]!='0')return false;
    Params next=defaults;
    if(s[3]=='1'&&n==loom::State{}.size()){
        loom::State old{};std::copy_n(s,n,old.begin());loom::Params op{};
        if(!loom::decode(old,op))return false;
        std::copy(op.begin(),op.end(),next.begin());
    }else if(s[3]=='2'&&n==State{}.size()){
        for(unsigned i=0;i<Count;++i){std::uint32_t u=0;for(unsigned j=0;j<4;++j)u|=std::uint32_t(s[4+4*i+j])<<(8*j);float f;std::memcpy(&f,&u,4);if(!std::isfinite(f)||f<0||f>1||(i>=3&&f!=0&&f!=1))return false;next[i]=f;}
    }else return false;
    p=next;return true;
}
class Engine {
    struct Slot {
        Voice single;CycleVoice cycle;int id=0;bool periodic=false;
        bool active() const noexcept {return periodic?cycle.active:single.active;}
        void off() noexcept {if(periodic)cycle.off();else single.off();}
        Pair tick() noexcept {return periodic?cycle.tick():single.tick();}
    };
    std::array<Slot,8> slots{};double rate=48000;
public:
    bool prepare(double sr) noexcept {if(!supported(sr))return false;rate=sr;reset();return true;}
    void reset() noexcept {slots={};}
    bool on(int id,int note,double cents,double velocity,const Params& params) noexcept {
        if(!std::isfinite(velocity)||velocity<=0){off(id);return false;}
        for(auto& s:slots)if(s.active()&&s.id==id)return false;
        for(auto& s:slots)if(!s.active()){
            s=Slot{};s.id=id;s.periodic=params[4]>=.5;
            loom::Params old{params[0],params[1],params[2],params[3]};auto p=loom::patch(old);
            if(s.periodic)return s.cycle.start(rate,note,cents,velocity,{p.spread,p.seconds,p.width,mask(params)});
            s.single.start(id,note,cents,velocity,rate,p);return true;
        }return false;
    }
    void off(int id) noexcept {for(auto& s:slots)if(s.active()&&s.id==id)s.off();}
    Pair tick() noexcept {Pair out;for(auto& s:slots){auto p=s.tick();out.l+=p.l;out.r+=p.r;}return out;}
    template<class T> void render(T* l,T* r,int n) noexcept {for(int i=0;i<n;++i){auto p=tick();if(r){l[i]=T(p.l);r[i]=T(p.r);}else l[i]=T((p.l+p.r)*.5);}}
};
}
