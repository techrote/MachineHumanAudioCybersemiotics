#pragma once
#include "../oversampling/oversample.hpp"
namespace mhac::forge {
inline constexpr unsigned Quality=Count, LiveCount=Count+1;
using LiveParams=std::array<float,LiveCount>;
inline constexpr LiveParams liveDefaults{.75f,1.f,0.f,.5f,.75f,0.f,.5f};
using LiveState=std::array<std::uint8_t,4+4*LiveCount>;
inline unsigned qualityIndex(double q){return unsigned(std::floor(2*q+.5));}
inline bool validLive(const LiveParams& p){
    for(float x:p)if(!std::isfinite(x)||x<0||x>1)return false;
    return p[Quality]==0||p[Quality]==.5f||p[Quality]==1;
}
inline LiveState encodeLive(const LiveParams& p){
    Params old{};std::copy_n(p.begin(),Count,old.begin());auto s=encode(old);
    LiveState out{};std::copy(s.begin(),s.end(),out.begin());out[3]='2';
    std::uint32_t u;std::memcpy(&u,&p[Quality],4);
    for(unsigned j=0;j<4;++j)out[s.size()+j]=std::uint8_t(u>>(8*j));
    return out;
}
inline bool decodeLive(const std::uint8_t* data,std::size_t size,LiveParams& p){
    if(!data||(size!=State{}.size()&&size!=LiveState{}.size()))return false;
    if(data[0]!='W'||data[1]!='F'||data[2]!='0'||data[3]!=(size==State{}.size()?'1':'2'))return false;
    State old{};std::copy_n(data,old.size(),old.begin());old[3]='1';Params q{};
    if(!decode(old,q))return false;
    LiveParams next{};std::copy(q.begin(),q.end(),next.begin());
    if(size==LiveState{}.size()){
        std::uint32_t u=0;for(unsigned j=0;j<4;++j)u|=std::uint32_t(data[old.size()+j])<<(8*j);
        std::memcpy(&next[Quality],&u,4);
    } // WF01 migration deliberately selects aligned 1x, not 2x.
    if(!validLive(next))return false;
    p=next;return true;
}
class LiveForge {
    std::array<Oversampled,3> paths{};
    LiveParams target=liveDefaults;
    std::array<double,3> weights{0,1,0}, start{0,1,0};
    unsigned destination=1, elapsed=0, fade=240;
public:
    static constexpr unsigned latency=Oversampled::latency, tail=Oversampled::tail;
    LiveForge(){reset(48000);}
    const LiveParams& params()const{return target;}
    bool restore(const LiveParams& p){
        if(!validLive(p))return false;
        Params old{};std::copy_n(p.begin(),Count,old.begin());
        for(auto& path:paths)path.restore(old);
        target=p;return true;
    }
    void set(unsigned id,double x){
        if(id>=LiveCount||!std::isfinite(x))return;
        x=std::clamp(x,0.,1.);
        if(id==Quality)target[id]=float(qualityIndex(x))*.5f;
        else {target[id]=float(x);for(auto& path:paths)path.set(id,x);}
    }
    bool reset(double rate){
        if(!validSampleRate(rate))return false;
        for(unsigned i=0;i<3;++i)if(!paths[i].prepare(rate,1u<<i))return false;
        fade=unsigned(std::ceil(rate*.005));destination=qualityIndex(target[Quality]);elapsed=fade;
        weights={};weights[destination]=1;start=weights;return true;
    }
    template<class T> std::array<T,2> process(T l,T r){
        const unsigned q=qualityIndex(target[Quality]);
        if(q!=destination){start=weights;destination=q;elapsed=0;}
        if(elapsed<fade){
            const double t=double(++elapsed)/fade;
            for(unsigned i=0;i<3;++i)weights[i]=(1-t)*start[i]+t*double(i==destination);
        }
        // All histories stay warm even while inaudible. Bounded work, no reset on automation.
        const auto base=paths[0].process(double(l),double(r));
        auto result=base;
        for(unsigned i=1;i<3;++i){const auto y=paths[i].process(double(l),double(r));
            for(unsigned c=0;c<2;++c)result[c]+=weights[i]*(y[c]-base[c]);}
        return {T(guard(result[0])),T(guard(result[1]))};
    }
};
}
