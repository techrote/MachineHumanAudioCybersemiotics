#include "control.hpp"
#include <cstdlib>
#include <iostream>
#include <limits>
using namespace restbus::control;
unsigned checks=0;
void ck(bool b){++checks;if(!b){std::cerr<<"failure "<<checks<<'\n';std::exit(1);}}
int main(){
    for(double sr:{1000.,1234.568,44100.,48000.,96000.,192000.,1234567.8,2000000.}){
        Live a;restbus::Engine b;ck(a.prepare(sr)&&b.prepare(sr));
        unsigned n=unsigned(std::lround(sr*.3));
        for(unsigned i=0;i<n;++i)ck(a.tick()==b.tick());
        ck(a.index()==1&&a.partial()==0);
        ck(a.on(0,57,0,.75)&&b.on(0,57,0,.75));
        for(unsigned i=0;i<128;++i)ck(a.tick()==b.tick());
        ck(a.parameter(0,1)&&a.parameter(2,1));ck(a.index()==2);
        ck(a.parameter(2,1)&&a.index()==2);
        ck(a.parameter(2,0)&&a.parameter(2,1)&&a.index()==3);
        for(unsigned i=0;i<128;++i)ck(a.tick()==b.tick());
        ck(a.on(0,57,0,0));b.off(0);
        for(unsigned i=0;i<unsigned(std::ceil(sr*.04));++i)ck(a.tick()==b.tick());
        ck(a.tick()==0&&a.index()==3);
        ck(a.parameter(1,0)&&a.index()==3&&a.partial()==0);
        ck(a.parameter(0,0));unsigned m=unsigned(std::lround(sr*.01));
        for(unsigned i=0;i<m-1;++i){ck(a.tick()==0);ck(a.parameter(1,0));}
        ck(a.index()==3);ck(a.tick()==0&&a.index()==4);
        Params saved=a.parameters(),p{};auto s=encode(saved);ck(decode(s.data(),s.size(),p)&&p==saved);
        ck(a.restore(p)&&a.index()==0&&a.partial()==0&&a.tick()==0);
        auto bad=s;bad[0]='X';ck(!decode(bad.data(),bad.size(),p)&&p==saved);
        ck(!decode(s.data(),s.size()-1,p)&&!decode(nullptr,s.size(),p));
        bad=encode({0.,std::numeric_limits<double>::quiet_NaN()});ck(!decode(bad.data(),bad.size(),p)&&p==saved);
        ck(!a.restore({1.,2.})&&a.parameters()==saved);
        ck(!a.parameter(4,0)&&!a.parameter(0,-1)&&!a.parameter(1,std::numeric_limits<double>::infinity()));
    }
    // Offset ordering: controls, then notes, then sample. Partitioning is irrelevant.
    Live a,b;ck(a.prepare(1000)&&b.prepare(1000));
    auto run=[](Live& e,unsigned i){if(i==9)e.parameter(1,0);if(i==19)e.on(1,60,0,1);if(i==39)e.off(1);if(i==50){e.parameter(0,1);e.parameter(2,1);e.on(2,60,0,1);}if(i==70)e.off(2);return e.tick();};
    std::array<double,128> x{},y{};for(unsigned i=0;i<x.size();++i)x[i]=run(a,i);
    for(unsigned j=0;j<y.size();j+=7)for(unsigned i=j;i<std::min<unsigned>(j+7,y.size());++i)y[i]=run(b,i);
    ck(x==y&&a.index()==b.index());ck(x[18]==0&&x[19]!=0&&x[127]==0);
    std::cout<<"PASS "<<checks<<" assertions\n";
}
