#include "clock.hpp"
#include <cstdlib>
#include <iostream>
#include <memory>
#include <limits>
#include <vector>
using namespace mhac::clock_fold;
static unsigned checks=0;
static void require(bool ok) { ++checks; if(!ok) { std::cerr<<"failure at check "<<checks<<'\n'; std::exit(1); } }
int main(){
    for(int k=-10;k<=10;++k) for(int d=-10;d<=10;++d) {
        Controls c; c.curvature=k*.05; c.drift=d*.05;
        auto p=Plan::make(c); c.compensation=1; auto q=Plan::make(c);
        require(std::abs(p.radius-q.radius)<1e-14);
        require(std::abs(p.radius-std::abs(c.curvature))<1e-14);
        require(p.source(0)==0 && p.source(1)==1);
        for(std::size_t j=0;j<4;++j){ require(p.boundary[j+1]>p.boundary[j]); require(std::abs(p.source(p.boundary[j])-.25*j)<1e-14); }
        for(int j=0;j<100;++j) require(p.source(j*.01)<=p.source((j+1)*.01));
    }
    auto owner=std::make_unique<Engine>(), other=std::make_unique<Engine>();
    auto& e=*owner; auto& f=*other; Controls c;
    for(double rate:{1000.,1234.568,44100.,48000.,96000.,192000.,1234567.8,2000000.}){
        require(e.prepare(rate));
        for(std::size_t i=0;i<3*frameSize;++i){ auto y=e.tick({i==0?.5:0,0},c); require(y[0]==(i==frameSize?.5:0)&&y[1]==0); }
    }
    for(double rate:{0.,999.,2000001.,std::numeric_limits<double>::infinity(),std::numeric_limits<double>::quiet_NaN()}) require(!e.prepare(rate));
    require(e.prepare(48000)&&f.prepare(48000));
    c.drift=.5; c.curvature=-.5; c.wet=.8;
    const auto n=4*frameSize+13;
    std::vector<double> x(n),y(n),r(n),z(n),s(n);
    for(std::size_t i=0;i<n;++i)x[i]=.7*std::sin(.021*i);
    e.process(x.data(),static_cast<const double*>(nullptr),y.data(),r.data(),n,c);
    z=x;
    for(std::size_t i=0;i<n;){ auto m=std::min<std::size_t>(1+i%257,n-i); f.process(z.data()+i,static_cast<const double*>(nullptr),z.data()+i,s.data()+i,m,c);i+=m; }
    for(std::size_t i=0;i<n;++i){ require(y[i]==z[i]&&r[i]==0&&s[i]==0); require(std::isfinite(y[i])&&std::abs(y[i])<=1); }
    require(y[frameSize]==x[0] && y[2*frameSize-1]==x[frameSize-1]);
    e.reset(); f.reset(); c.compensation=1; c.curvature=0;c.wet=1;
    for(std::size_t i=0;i<n;++i){auto a=e.tick({x[i],0},c);auto b=f.tick({x[i],0},Controls{});require(a==b);}
    e.reset(); c.compensation=0;c.curvature=.5;c.bypass=true;
    for(std::size_t i=0;i<3*frameSize;++i){auto a=e.tick({i<frameSize?1.:0,0},c); require(a[0]==(i>=frameSize&&i<2*frameSize?1:0));}
    e.reset(); c.bypass=false;c.wet=1;
    for(std::size_t i=0;i<3*frameSize;++i){auto a=e.tick({i==0?std::numeric_limits<double>::infinity():0,i==0?std::numeric_limits<double>::quiet_NaN():0},c);require(a[0]==0&&a[1]==0);}
    e.reset(); f.reset();
    std::array<float,64> xf{},yf{};xf[0]=.25f;
    for(std::size_t j=0;j<frameSize/64+1;++j){e.process(xf.data(),static_cast<const float*>(nullptr),yf.data(),static_cast<float*>(nullptr),64,Controls{});for(std::size_t i=0;i<64;++i){auto a=f.tick({xf[i],0},Controls{});require(yf[i]==static_cast<float>(a[0]));}xf.fill(0);}
    std::cout<<checks<<" checks passed\n";
}
