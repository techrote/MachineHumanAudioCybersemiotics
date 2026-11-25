#include "forge.hpp"
#include <complex>
#include <iostream>
#include <stdexcept>
#include <vector>
using namespace mhac::forge;
using C=std::complex<double>;
constexpr double pi=3.14159265358979323846;
static void check(bool v,const char* s){if(!v)throw std::runtime_error(s);}
static Params formal(){return {1,1,0,1,1,0};}
// Independent direct triple-convolution oracle; periodic sampled analytic input.
static C oracle(const std::array<int,4>& f,const std::array<C,4>& a,int k,int period){C y{};for(unsigned i=0;i<4;++i){if((f[i]-k)%period==0)y+=a[i];for(unsigned j=0;j<4;++j)for(unsigned h=0;h<4;++h)if((f[i]+f[j]-f[h]-k)%period==0)y+=a[i]*a[j]*std::conj(a[h]);}return y;}
static C measure(const std::array<int,4>& f,const std::array<C,4>& a,int k,int period){Forge e;e.restore(formal());e.reset(48000);C result{};for(int n=0;n<period;++n){C x{};for(unsigned j=0;j<4;++j)x+=a[j]*std::polar(1.,2*pi*f[j]*n/period);auto y=e.process(x.real(),x.imag());result+=C(y[0],y[1])*std::polar(1.,-2*pi*k*n/period);}return result/double(period);}
int main(){
    unsigned cases=0;double maxerr=0;
    for(auto f:{std::array<int,4>{5,6,9,10},std::array<int,4>{5,6,9,11},std::array<int,4>{1,2,3,4}}){
        for(unsigned code=0;code<81;++code){unsigned q=code;std::array<C,4>a{};for(unsigned i=0;i<4;++i){a[i]=double(int(q%3)-1)*C(.075,.025*(i+1));q/=3;}for(int k=0;k<16;++k){double err=std::abs(measure(f,a,k,64)-oracle(f,a,k,64));maxerr=std::max(maxerr,err);check(err<1e-13,"cubic coefficient");++cases;}}
    }
    std::array<C,4>a{0.,.1,.1,.1};auto falseTone=measure({5,6,9,10},a,5,600);auto safe=measure({5,6,9,11},a,5,600);check(std::abs(falseTone-C(.002))<1e-13&&std::abs(safe)<1e-13,"Sidon comparison");
    // 2*23 - 20 = 26 folds to -22 on a 48-bin sampled grid.
    std::array<C,4> alias{.1,.1,0.,0.};auto folded=measure({20,23,0,1},alias,-22,48);check(std::abs(folded-C(.001))<1e-13,"alias negative control");
    for(double sr:{8000.,44100.,48000.,96000.,192000.,384000.}){
        Forge e;check(e.restore(formal())&&e.reset(sr),"setup");auto y=e.process(.25,-.5);check(y[0]==.25*(1+.0625+.25)&&y[1]==-.5*(1+.0625+.25),"formal sample");
        e.set(Isolate,1);for(unsigned n=0;n<unsigned(std::ceil(sr*.005))+2;++n)e.process(.25,-.5);y=e.process(.25,-.5);check(y[0]==.0625&&y[1]==-.03125,"cross-only");check(e.process(.5,0.)==std::array<double,2>{0.,0.},"cross null");
        e.set(Bypass,1);for(unsigned n=0;n<unsigned(std::ceil(sr*.005))+2;++n)e.process(.25,-.5);check(e.process(.25,-.5)==std::array<double,2>{.25,-.5},"bypass");
        check(e.process(std::numeric_limits<double>::infinity(),std::numeric_limits<double>::quiet_NaN())==std::array<double,2>{0.,0.},"nonfinite");check(e.process(1e-300,-1e-300)==std::array<double,2>{0.,0.},"tiny");
        e.restore(formal());e.reset(sr);check(e.process(1e99,-1e99)==std::array<double,2>{1.,-1.},"clipping");
        auto p=e.params();State s=encode(p);Params decoded{};check(decode(s,decoded)&&decoded==p,"state");s[0]=0;check(!decode(s,decoded)&&decoded==p,"state header");s=encode(p);s[4]=0;s[5]=0;s[6]=0xc0;s[7]=0x7f;check(!decode(s,decoded)&&decoded==p,"state NaN");check(!e.reset(0),"invalid rate");
    }
    // Independent-channel negative control, symmetry, impulse/silence and nontrivial state.
    Forge e;Params patch{.8f,.37f,.23f,.6f,.42f,0.f},decoded{};
    check(e.restore(patch)&&decode(encode(patch),decoded)&&decoded==patch,"nontrivial state");
    auto invalid=patch;invalid[Mix]=2;check(!e.restore(invalid)&&e.params()==patch,"transactional restore");
    e.set(Drive,std::numeric_limits<double>::quiet_NaN());check(e.params()==patch,"invalid automation");
    e.restore({1,0,0,1,1,0});e.reset(48000);
    auto x=e.process(.25,.5),y=e.process(.25,-.125);check(x[0]==y[0],"uncoupled channel independence");
    check(e.process(.5,0.)==std::array<double,2>{.625,0.},"impulse");
    check(e.process(0.,0.)==std::array<double,2>{0.,0.},"zero tail");
    e.restore(formal());e.reset(48000);x=e.process(.25,-.5);y=e.process(-.5,.25);check(x[0]==y[1]&&x[1]==y[0],"stereo symmetry");
    auto xf=e.process(.25f,-.5f);check(double(xf[0])==x[0]&&double(xf[1])==x[1],"float and double dyadic");
    // Same event timeline with different caller partitions and sample types.
    auto render=[](unsigned block,auto type){using T=decltype(type);Forge e;std::vector<std::array<T,2>> out;for(unsigned start=0;start<10000;start+=block)for(unsigned n=start;n<std::min(10000u,start+block);++n){if(n==0)e.set(Drive,1);if(n==127)e.set(Coupling,.2);if(n==1024)e.set(Isolate,1);if(n==3000)e.set(Bypass,1);if(n==4500)e.set(Bypass,0);if(n==6000)e.set(Mix,0);auto y=e.process(T(.4*std::sin(n*.1)),T(.3*std::cos(n*.073)));check(std::isfinite(y[0])&&std::abs(y[0])<=1&&std::abs(y[1])<=1,"bounds");out.push_back(y);}return out;};
    auto d=render(1,0.);auto f=render(1,0.f);for(unsigned b:{7u,64u,257u,1024u}){check(render(b,0.)==d,"double partition");check(render(b,0.f)==f,"float partition");}
    std::cout<<"coefficient cases="<<cases<<" max_error="<<maxerr<<" false="<<falseTone.real()<<" Sidon="<<std::abs(safe)<<" alias="<<folded.real()<<"\n";
}
