#pragma once
#include "../residual-582/residual.hpp"
namespace prism {
inline constexpr unsigned Retention=Count, IntegratedCount=Count+1;
using IntegratedParams=std::array<double,IntegratedCount>;
inline constexpr IntegratedParams integratedDefaults{.75,1.,.5,.5,0.,0.,1.};
using IntegratedState=std::array<std::uint8_t,4+4*IntegratedCount>;
inline IntegratedState encodeIntegrated(const IntegratedParams& p) noexcept {
    IntegratedState s{'P','C','0','2'};
    for(unsigned i=0;i<IntegratedCount;++i){float f=static_cast<float>(p[i]);std::uint32_t u;std::memcpy(&u,&f,4);for(unsigned b=0;b<4;++b)s[4+4*i+b]=std::uint8_t(u>>(8*b));}
    return s;
}
inline bool decodeIntegrated(const std::uint8_t* s,std::size_t size,IntegratedParams& out) noexcept {
    if(!s||size<4||s[0]!='P'||s[1]!='C'||s[2]!='0')return false;
    IntegratedParams p{};
    if(s[3]=='1'){
        LiveParams old{};if(!decode(s,size,old))return false;
        std::copy(old.begin(),old.end(),p.begin());p[Retention]=0.;
    }else if(s[3]=='2'&&size==IntegratedState{}.size()){
        for(unsigned i=0;i<IntegratedCount;++i){std::uint32_t u=0;for(unsigned b=0;b<4;++b)u|=std::uint32_t(s[4+4*i+b])<<(8*b);float f;std::memcpy(&f,&u,4);if(!std::isfinite(f)||f<0||f>1)return false;p[i]=f;}
    }else return false;
    out=p;return true;
}
class IntegratedPrism {
    ResidualPrism dsp;
    IntegratedParams target=integratedDefaults;
public:
    bool prepare(double sr){restore(target);return dsp.prepare(sr);}
    void set(unsigned id,double v) noexcept {if(id<IntegratedCount&&std::isfinite(v)){target[id]=std::clamp(v,0.,1.);dsp.set(id,target[id]);}}
    void restore(const IntegratedParams& p) noexcept {for(unsigned i=0;i<IntegratedCount;++i)set(i,p[i]);}
    const IntegratedParams& params() const noexcept {return target;}
    void reset() noexcept {dsp.reset();}
    std::size_t latency() const noexcept {return dsp.latency();}
    std::size_t tailBound() const noexcept {return dsp.tailBound();}
    C step(double l,double r) noexcept {return dsp.step(l,r);}
};
}
