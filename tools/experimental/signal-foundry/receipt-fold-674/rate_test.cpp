#include "host.hpp"
#include <cstdlib>
#include <iostream>
#include <limits>
using namespace mhac::receipt;
static void check(bool b){if(!b)std::abort();}
template<class T> static void rateTest(double rate){
    const auto n=static_cast<unsigned>(std::ceil(rate*.005));
    Host a,b;check(a.prepare(rate)&&b.prepare(rate));
    Patch p{{0,7},Mode::preview,false,1.};check(a.apply(p)&&b.apply(p));
    for(unsigned i=0;i<n+2;++i){T l=T(.9),r=T(-.9),ll=l,rr=r;a.frame(l,r);b.frame(ll,rr);check(l==ll&&r==rr);}
    p.mode=Mode::absent;check(a.apply(p)&&b.apply(p));
    for(unsigned i=0;i<n;++i){
        if(i==n/2){for(double invalid:{0.,-1.,999.,2000001.,std::numeric_limits<double>::infinity(),std::numeric_limits<double>::quiet_NaN()})check(!a.prepare(invalid));}
        T l=T(.9),r=T(-.9),ll=l,rr=r;a.frame(l,r);b.frame(ll,rr);
        const double expected=i+1==n?-.4375:.4375-.875*double(i+1)/n;
        check(l==ll&&r==rr&&std::abs(double(l)-expected)<=1e-7&&r==T(-.4375));
    }
    // Valid setup resets interpolation and mix, but retains patch parameters.
    check(a.prepare(rate)&&save(a.patch())==save(p));
    T l=T(.9),r=T(0);a.frame(l,r);
    const double x=double(T(.9));check(std::abs(double(l)-(x*(1.-1./n)-.4375/n))<=1e-7&&r==0);
    l=std::numeric_limits<T>::quiet_NaN();r=std::numeric_limits<T>::infinity();a.frame(l,r);check(l==0&&r==0);
    // No audio history, even while control ramps continue.
    for(unsigned i=0;i<n;++i){l=0;r=0;a.frame(l,r);check(l==0&&r==0);}
}
int main(){
    for(double rate:{1000.,1234.568,8000.,12345.678,22050.,32000.,44100.,48000.,88200.,96000.,123456.78,192000.,384000.,1234567.8,2000000.}){
        rateTest<float>(rate);rateTest<double>(rate);
    }
    std::cout<<"15 sample rates, both formats: transition length, invalid setup atomicity, valid setup reset, silence PASS\n";
}
