#include "prism.hpp"
#include <cstdlib>
#include <iostream>
#include <limits>
using namespace prism;
void check(bool b){if(!b){std::cerr<<"FAIL\n";std::exit(1);}}
C tone(const Coeff& a,std::size_t p,std::size_t n){C x{};for(int j=0;j<4;++j)x+=a[j]*std::polar(1.,tau*bins[j]*double(p%n)/double(n));return x;}
int main(){
    std::size_t cases=0;
    for(int word=0;word<625;++word){int q=word;Coeff a{};for(auto& v:a){int k=q%5;q/=5;v=k==0?C{}:std::polar(.13,(k-1)*tau/4);}
        double energy=0;for(auto v:a)energy+=std::norm(v);
        auto y=cycle(a,.8);for(int j=0;j<4;++j){check(std::abs(y[j]-a[j]*(1+.8*(2*energy-std::norm(a[j]))))<1e-14);++cases;}}
    const Coeff a{C{},.18,.18,.18};
    check(std::abs(cubic(a,1)[0]-C(.011664))<1e-14);check(std::abs(cycle(a,1)[0])<1e-14);
    double maxResidual=0,maxRawError=0;
    for(double sr:{8000.,44100.,48000.,96000.,192000.}){
        Prism p;check(p.prepare(sr));auto n=p.latency();
        for(double cancel:{0.,.5,1.}){p.set({1,cancel,1,1});p.reset();C c{};
            for(std::size_t t=0;t<5*n;++t){auto x=tone(a,t,n),y=p.step(x.real(),x.imag());if(t>=4*n)c+=y*std::polar(1.,-tau*bins[0]*double(t%n)/double(n));}
            c/=double(n);double err=std::abs(c-C(.011664*(1-cancel)));check(err<1e-13);
            if(cancel==1)maxResidual=std::max(maxResidual,std::abs(c));else if(cancel==0)maxRawError=std::max(maxRawError,err);
            for(std::size_t t=0;t<p.tailBound();++t)p.step(0,0);
            check(p.step(0,0)==C{});
        }
        p.set({0,1,0,1});p.reset();for(std::size_t t=0;t<2*n;++t)check(p.step(t==0?.25:0,0)==C(t==n?.25:0,0));
        p.set({1,1,1,1});p.reset();for(std::size_t t=0;t<4*n;++t){auto y=p.step(t%2?1e300:std::numeric_limits<double>::quiet_NaN(),-1e300);check(std::isfinite(y.real())&&std::isfinite(y.imag())&&std::abs(y.real())<=1&&std::abs(y.imag())<=1);}
    }
    Prism p;check(!p.prepare(0));check(p.step(1,1)==C{});check(p.prepare(48000));p.set({1,1,1,1});p.reset();
    // Off-grid leakage: a 440 Hz tone is not exactly orthogonal to the 400 Hz bin.
    C c{};for(std::size_t t=0;t<p.latency();++t)c+=std::polar(.2,tau*(440.-400.)*double(t)/48000.);
    check(std::abs(c/double(p.latency()))>.1);
    std::cout<<"coefficient checks="<<cases<<" max corrected residual="<<maxResidual<<" max raw error="<<maxRawError<<"\n";
}
