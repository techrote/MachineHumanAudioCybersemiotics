#include "splitter.hpp"
#include <iostream>
#include <stdexcept>
#include <limits>
#include <vector>
#include <chrono>
#include <string>
using namespace mhac::splitter;
unsigned long long checks=0;
void ck(bool x){++checks;if(!x)throw std::runtime_error("check "+std::to_string(checks));}
// Compare finite, non-dyadic streams under different host-style block partitions.
// The streaming core has no block API: the partitions exercise caller scheduling,
// not the VST3 parameter queue or bus adapter.
template<class T> void partitionRegression(double rate,unsigned k){
    using Frame=std::array<T,2>;
    constexpr unsigned length=4093;
    const unsigned d=delays[k];
    std::vector<Frame> input(length+2*d), reference(input.size());
    for(unsigned i=0;i<length;++i){
        input[i]={T(.21*std::sin(.071*i)),T(.19*std::cos(.113*i))};
    }
    Engine forward,inverse;
    forward.set(Delay,k/3.);inverse.set(Delay,k/3.);
    forward.set(Mix,1);inverse.set(Mix,1);inverse.set(Inverse,1);
    ck(forward.reset(rate)&&inverse.reset(rate));
    for(unsigned i=0;i<input.size();++i)reference[i]=forward.process(input[i][0],input[i][1]);
    ck(forward.reset(rate));
    const unsigned blocks[]={1,17,64,257,511};
    double error=0,energyIn=0,energyOut=0;
    for(unsigned i=0,b=0;i<input.size();++b){
        const unsigned end=std::min<unsigned>(unsigned(input.size()),i+blocks[b%5]);
        for(;i<end;++i){
            auto y=forward.process(input[i][0],input[i][1]);
            ck(y==reference[i]);
            auto z=inverse.process(y[0],y[1]);
            for(unsigned c=0;c<2;++c){
                const double expected=i>=d?input[i-d][c]:0;
                error=std::max(error,std::abs(double(z[c])-expected));
                energyIn+=double(input[i][c])*input[i][c];
                energyOut+=double(y[c])*y[c];
                if(i>=length+d)ck(y[c]==0);
                if(i>=length+2*d-1)ck(std::abs(double(z[c]))<=8*std::numeric_limits<T>::epsilon());
            }
        }
    }
    const double eps=std::numeric_limits<T>::epsilon();
    ck(error<=8*eps);ck(std::abs(energyIn-energyOut)<=energyIn*64*eps);
}
void clippingNegativeControl(){
    // Delayed common mode + current differential mode can reach 2 FS.
    // The safety clamp is intentional and destroys invertibility.
    Engine f,g;f.set(Mix,1);g.set(Mix,1);g.set(Inverse,1);
    ck(f.reset(48000)&&g.reset(48000));
    std::array<double,2> at{};
    for(unsigned i=0;i<=32;++i){
        const double l=i==0||i==16?1.:0.,r=i==0?1.:i==16?-1.:0.;
        auto y=f.process(l,r);auto z=g.process(y[0],y[1]);
        if(i==16){ck(y[0]==1&&y[1]==0);at=z;}
    }
    ck(at[0]!=1||at[1]!=1);
}
int main(){
    for(double rate:{44100.,48000.,96000.,192000.})for(unsigned k=0;k<4;++k){
        partitionRegression<float>(rate,k);partitionRegression<double>(rate,k);
    }
    clippingNegativeControl();
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
