#include "xl.hpp"
#include <cstdlib>
#include <iostream>
#include <memory>
static void check(bool b,const char* msg){if(!b){std::cerr<<msg<<'\n';std::exit(1);}}
int main(){
    using namespace loomxl;
    auto e=std::make_unique<Live>();auto ref=std::make_unique<loomscale::Engine>();
    unsigned long long pairs=0;
    for(double sr:{1000.,1234.5678,8000.,44100.,48000.,96000.,192000.,1234567.8,2000000.}){
        check(e->restore(defaults)&&e->prepare(sr)&&ref->prepare(sr),"prepare");
        auto p=defaults;
        auto sync=[&](){ref->set({{1u+unsigned(std::lround(p[Separation]*3)),unsigned(std::lround(p[Rotation]*8)),1+15*p[Budget],p[Repair],p[Wet],p[Gain],p[Bypass]>=.5},p[Probe],p[Edge]},unsigned(std::lround(p[Scale]*2)));};
        sync();ref->reset();
        for(unsigned i=0;i<latency*3;++i){
            if(i%113==0){unsigned k=(i/113)%Count;double v=double((i/113*37)%101)/100;p[k]=v;e->set(k,v);sync();}
            const double l=.15*std::sin(i*.033),r=.1*std::cos(i*.097);
            check(e->step(l,r)==ref->step(l,r),"control bridge mismatch");++pairs;
        }
        check(e->params()==p,"parameter readback");auto bytes=encode(p);Normalized q=defaults;
        check(decode(bytes.data(),bytes.size(),q)&&q==p,"state roundtrip");
        for(unsigned n=0;n<bytes.size();++n)check(!decode(bytes.data(),n,q)&&q==p,"truncated state transactional");
        auto bad=bytes;bad[0]='Z';check(!decode(bad.data(),bad.size(),q)&&q==p,"bad magic");
        auto old=loom2::encode(loom2::defaults);check(!decode(old.data(),old.size(),q),"different latency state rejected");
        q[Scale]=std::numeric_limits<double>::quiet_NaN();bad=encode(q);check(!decode(bad.data(),bad.size(),p),"nonfinite state");
        check(!e->restore(q),"invalid restore");auto before=e->params();e->set(Scale,std::numeric_limits<double>::infinity());e->set(Count,1);check(e->params()==before,"invalid automation");
        for(double scale:{0.,.5,1.}){p=defaults;p[Bypass]=1;p[Scale]=scale;check(e->restore(p),"bypass patch");e->reset();
            for(unsigned i=0;i<tail+1;++i){auto y=e->step(i==0?.25:0.,0.);check(y[0]==(i==latency?.25:0.)&&y[1]==0.,"fixed bypass latency/tail");}}
    }
    for(double sr:{0.,999.,2000001.,std::numeric_limits<double>::infinity(),std::numeric_limits<double>::quiet_NaN()})check(!e->prepare(sr),"invalid rate");
    std::cout<<"XL exact paired frames="<<pairs<<"; 27 bypass impulse trials; nine rates\n";
}
