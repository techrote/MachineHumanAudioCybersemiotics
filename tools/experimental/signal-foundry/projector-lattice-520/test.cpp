#include "lattice.hpp"
#include <iostream>
#include <stdexcept>
#include <limits>
#include <cstdint>
#include <fstream>
#include <string>
using namespace mhac::lattice;
static void check(bool b){if(!b)throw std::runtime_error("check failed");}
static double energy(Frame x){return x.l*x.l+x.r*x.r;}
static bool equal(Frame a,Frame b){return a.l==b.l&&a.r==b.r;}
int main(){
    double worst=0; unsigned cases=0; bool wrongOrder=false;
    for(unsigned code=0;code<256;++code){
        Program p{}; for(unsigned j=0;j<4;++j)p[j]={static_cast<Axis>((code>>(2*j))&3),j+1};
        Lattice f,g,bad; check(f.configure(p)&&g.configure(p,true));
        auto wrong=p; std::reverse(wrong.begin(),wrong.end()); check(bad.configure(wrong,true));
        std::array<Frame,128> input{}; std::uint32_t seed=17;
        for(auto& x:input){seed=1664525u*seed+1013904223u; x.l=(int(seed%65)-32)/1024.;seed=1664525u*seed+1013904223u;x.r=(int(seed%65)-32)/1024.;}
        double ei=0,eo=0;
        for(unsigned n=0;n<input.size()+2*f.tail()+1;++n){
            Frame x=n<input.size()?input[n]:Frame{}; auto y=f.step(x);auto z=g.step(y);auto w=bad.step(y);
            Frame target=n>=f.tail()&&n-f.tail()<input.size()?input[n-f.tail()]:Frame{};
            check(equal(z,target));if(!equal(w,target))wrongOrder=true;
            ei+=energy(x);eo+=energy(y);
            if(n>=input.size()+f.tail())check(equal(y,{}));
        }
        worst=std::max(worst,std::abs(ei-eo));check(ei==eo);++cases;
    }
    check(wrongOrder);
    double err=0;
    { Lattice a,b; Program s{{{Axis::Sum,16},{Axis::Left,23},{Axis::Difference,64},{Axis::Right,11}}};check(a.configure(s)&&b.configure(s,true));
      for(unsigned n=0;n<10000;++n){auto input=[](unsigned i){return Frame{.04*std::sin(i*.021),.03*std::cos(i*.087)};};auto y=b.step(a.step(input(n)));auto x=n>=a.tail()?input(n-a.tail()):Frame{};err=std::max({err,std::abs(y.l-x.l),std::abs(y.r-x.r)});}
      check(err<1e-14); }
    std::cout<<"non-dyadic peak reconstruction error "<<err<<"\n";
    Lattice f,g; Program p{{{Axis::Sum,1024},{Axis::Left,1024},{Axis::Difference,1024},{Axis::Right,1024}}};
    check(f.configure(p)&&g.configure(p,true)&&f.tail()==4096);
    auto bad=p;bad[2].delay=0;check(!f.configure(bad)&&f.tail()==4096);
    double peak=0;
    for(unsigned n=0;n<9000;++n){auto x=n==0?Frame{.125,-.0625}:Frame{};auto y=f.step(x);auto z=g.step(y);check(equal(z,n==4096?Frame{.125,-.0625}:Frame{}));peak=std::max(peak,std::abs(y.l));}
    check(peak>0);check(equal(f.step({std::numeric_limits<double>::infinity(),std::numeric_limits<double>::quiet_NaN()}),{}));
    std::cout<<cases<<" exact programs; worst energy error "<<worst<<"; wrong-order negative control PASS; max-delay impulse PASS\n";
}
