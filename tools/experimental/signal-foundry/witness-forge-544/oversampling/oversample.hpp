#pragma once
#include "../forge.hpp"
namespace mhac::forge {
// Fixed-quality, constant-latency wet-only oversampling experiment.
// prepare() is non-RT; process() uses only fixed storage and bounded loops.
class Oversampled {
    using Frame=std::array<double,2>;
    static constexpr unsigned Max=129, Hist=33;
    std::array<double,Max> h{};
    std::array<Frame,Hist> input{}, direct{};
    std::array<Frame,Max> wet{};
    unsigned factor=1, taps=1, pos=0, wp=0;
    Params target=defaults;
    std::array<double,Count> current{};
    double slew=1./240;
    static Frame cubic(Frame x,const std::array<double,Count>& p){
        const double l=x[0],r=x[1],g=2*p[Drive]-1,c=p[Coupling],k=1-p[Isolate];
        return {l*(k*(1+g*l*l)+g*c*r*r),r*(k*(1+g*r*r)+g*c*l*l)};
    }
public:
    static constexpr unsigned latency=32, tail=64;
    Oversampled(){prepare(48000,1);}
    bool prepare(double rate,unsigned f){
        if(!validSampleRate(rate)||(f!=1&&f!=2&&f!=4))return false;
        factor=f; taps=f==1?1:32*f+1; h.fill(0);
        constexpr double pi=3.14159265358979323846;
        if(f>1){double sum=0;for(unsigned i=0;i<taps;++i){const int n=int(i)-int(taps/2);const double fc=.45/f;
            const double sinc=n==0?2*fc:std::sin(2*pi*fc*n)/(pi*n);
            const double w=.42-.5*std::cos(2*pi*i/(taps-1))+.08*std::cos(4*pi*i/(taps-1));
            h[i]=sinc*w;sum+=h[i];}for(unsigned i=0;i<taps;++i)h[i]/=sum;}
        else h[0]=1;
        input={};direct={};wet={};pos=wp=0;slew=1./std::ceil(rate*.005);
        for(unsigned i=0;i<Count;++i)current[i]=target[i];
        return true;
    }
    bool restore(const Params& p){if(!valid(p))return false;target=p;return true;}
    const Params& params()const{return target;}
    void set(unsigned id,double x){if(id<Count&&std::isfinite(x))target[id]=float(std::clamp(x,0.,1.));}
    template<class T> std::array<T,2> process(T left,T right){
        for(unsigned i=0;i<Count;++i)current[i]+=std::clamp(double(target[i])-current[i],-slew,slew);
        const Frame x{guard(left),guard(right)};input[pos]=x;
        const unsigned delayed=(pos+1)%Hist;const Frame dry=input[delayed];
        Frame w{};
        if(factor==1){direct[pos]=cubic(x,current);w=direct[delayed];}
        else for(unsigned phase=0;phase<factor;++phase){
            Frame u{};for(unsigned k=phase,j=0;k<taps;k+=factor,++j){const auto& a=input[(pos+Hist-j)%Hist];for(unsigned c=0;c<2;++c)u[c]+=factor*h[k]*a[c];}
            // Interpolated samples can overshoot. Preserve polynomial before final guard.
            wet[wp]=cubic(u,current);
            if(phase==0)for(unsigned k=0;k<taps;++k){const auto& a=wet[(wp+Max-k)%Max];for(unsigned c=0;c<2;++c)w[c]+=h[k]*a[c];}
            wp=(wp+1)%Max;
        }
        pos=(pos+1)%Hist;
        const double m=current[Mix]*(1-current[Bypass]),g=current[Gain];
        return {T(guard((1-m)*dry[0]+m*g*w[0])),T(guard((1-m)*dry[1]+m*g*w[1]))};
    }
};
}
