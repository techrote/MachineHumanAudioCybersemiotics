#include "live.hpp"
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
using namespace mhac::lattice;
static unsigned checks=0;
static void ck(bool b){++checks;if(!b)throw std::runtime_error("rate check "+std::to_string(checks));}
static Frame signal(unsigned n){return {.03*std::sin(n*.031),.04*std::cos(n*.017)};}
static void change(Live& e){e.set(Axis1,0);e.set(Axis2,1);e.set(Delay1,1);e.set(Inverse,1);}
template<class T> static void exercise(double sr){
    ck(validSampleRate(sr));
    Live e,old,next;
    for(auto* v:{&e,&old,&next})v->set(Mix,1);
    change(next);
    for(auto* v:{&e,&old,&next})v->reset(sr);
    const unsigned start=300,warm=1024+127+256+511,fade=unsigned(std::lround(sr*.005));
    for(unsigned n=0;n<start+warm+fade+4097;++n){
        if(n==start)change(e);
        auto x=signal(n);T l=T(x.l),r=T(x.r);
        auto actual=e.process(l,r);
        // Double reference captures pre-output-conversion blend arithmetic.
        auto a=old.process(double(l),double(r)),b=next.process(double(l),double(r));
        if(n<start+warm)ck(actual==(std::array<T,2>{T(a[0]),T(a[1])}));
        else if(n>=start+warm+fade)ck(actual==(std::array<T,2>{T(b[0]),T(b[1])})&&!e.transitioning());
        else {
            double t=double(n-(start+warm)+1)/fade;
            for(unsigned j=0;j<2;++j)ck(std::abs(double(actual[j])-double(T(a[j]+(b[j]-a[j])*t)))<=4*std::numeric_limits<T>::epsilon());
            ck(e.transitioning()==(n+1<start+warm+fade));
        }
    }
    auto saved=encode(e.params());e.reset(sr);ck(encode(e.params())==saved&&!e.transitioning());
    for(unsigned n=0;n<4097;++n)ck(e.process(T(0),T(0))==(std::array<T,2>{}));
    e.set(Bypass,1);
    for(unsigned n=0;n<fade+2;++n)e.process(T(.01),T(-.01));
    ck(e.process(T(.01),T(-.01))==(std::array<T,2>{T(.01),T(-.01)}));
    e.set(Bypass,0);
    for(unsigned n=0;n<fade+2;++n){auto y=e.process(T(1),T(-1));for(auto v:y)ck(std::isfinite(v)&&std::abs(v)<=T(1));}
    for(unsigned n=0;n<4097;++n)e.process(T(0),T(0));
    ck(e.process(T(0),T(0))==(std::array<T,2>{}));
}
int main(){
    const double inf=std::numeric_limits<double>::infinity(),nan=std::numeric_limits<double>::quiet_NaN();
    for(double sr:{-inf,-1.,0.,999.999,2000000.001,inf,nan}){
        ck(!validSampleRate(sr));Live a,b;a.reset(sr);b.reset(48000);change(a);change(b);
        for(unsigned n=0;n<3000;++n){auto x=signal(n);ck(a.process(x.l,x.r)==b.process(x.l,x.r));}
    }
    for(double sr:{1000.,1234.568,8000.,44100.,48000.,96000.,192000.,384000.,1234567.8,2000000.}){
        exercise<float>(sr);exercise<double>(sr);
    }
    // Reset during a pending transition at a different rate: history is cleared,
    // desired state is retained and installed immediately.
    Live a,b;change(a);a.process(.2,-.2);ck(a.transitioning());
    a.reset(1234567.8);change(b);b.reset(1234567.8);
    ck(!a.transitioning()&&a.params()==b.params());
    for(unsigned n=0;n<8192;++n){auto x=signal(n);ck(a.process(x.l,x.r)==b.process(x.l,x.r));}
    std::cout<<checks<<" rate assertions; 10 valid rates, 7 invalid rates, float/double PASS\n";
}
