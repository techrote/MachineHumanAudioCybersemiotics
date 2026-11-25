#include "splitter.hpp"
#include <iostream>
#include <stdexcept>
#include <limits>
#include <vector>
#include <chrono>
using namespace mhac::splitter;
unsigned long long checks=0;
void ck(bool x){++checks;if(!x)throw std::runtime_error("check "+std::to_string(checks));}
int main(){
    for(double rate:{1000.,1234.568,44100.,48000.,96000.,192000.,1234567.8,2000000.})for(unsigned k=0;k<4;++k){
        Engine a,b;a.set(Delay,k/3.);b.set(Delay,k/3.);a.set(Mix,1);b.set(Mix,1);b.set(Inverse,1);ck(a.reset(rate)&&b.reset(rate));
        std::vector<std::array<double,2>> x(4096+1024);unsigned seed=42;double e=0,f=0;
        for(unsigned i=0;i<4096;++i)for(auto& v:x[i]){seed=1664525u*seed+1013904223u;v=(int(seed>>16)-32768)/131072.;e+=v*v;}
        for(unsigned i=0;i<x.size();++i){auto y=a.process(x[i][0],x[i][1]);auto z=b.process(y[0],y[1]);f+=y[0]*y[0]+y[1]*y[1];for(unsigned c=0;c<2;++c)ck(z[c]==(i>=delays[k]?x[i-delays[k]][c]:0));}
        ck(std::abs(e-f)<1e-8);
        a.reset(rate);for(unsigned i=0;i<delays[k]+2;++i){auto y=a.process(i==0?.5:0.,0.);ck(y[0]==((i==0||i==delays[k])?.25:0));ck(y[1]==(i==0?-.25:i==delays[k]?.25:0));}
    }
    Engine a,b; a.reset(48000);b.reset(48000);
    for(unsigned i=0;i<100000;++i){if(i%997==0){a.set(Delay,(i%4)/3.);b.set(Delay,(i%4)/3.);a.set(Inverse,(i%2));b.set(Inverse,(i%2));}if(i==80000){a.set(Bypass,1);b.set(Bypass,1);}float x=i%3==0?1.f:-1.f;auto y=a.process(x,-x),z=b.process(x,-x);ck(y==z);for(auto v:y)ck(std::isfinite(v)&&std::abs(v)<=1);if(i>95000)ck(y[0]==x&&y[1]==-x);}
    auto p=a.params();Params q{};ck(decode(encode(p),q)&&p==q);auto s=encode(p);s[4]=2;ck(!decode(s,q)&&q==p);p[0]=std::numeric_limits<double>::quiet_NaN();ck(!decode(encode(p),q));ck(!a.reset(0));a.reset(48000);auto y=a.process(std::numeric_limits<double>::infinity(),std::numeric_limits<double>::quiet_NaN());ck(y[0]==0&&y[1]==0);
    std::cout<<checks<<" checks passed\n";
}
