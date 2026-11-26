#include "compiler.hpp"
#include <iostream>
using namespace mhac::lattice;
using namespace mhac::lattice::design;
static void check(bool ok){if(!ok)throw std::runtime_error("regression");}
int main(){
    unsigned count=0;
    for(double sr:{8000.,44100.,48000.,96000.,192000.,384000.}){
        for(unsigned code=0;code<256;++code){Program p{};for(unsigned j=0;j<4;++j)p[j]={static_cast<Axis>((code>>(2*j))&3),1u+j*7};Lattice dsp;check(dsp.configure(p));
            std::vector<Frame> h;for(unsigned n=0;n<=dsp.tail();++n)h.push_back(dsp.step({n?0.:.0625,0.}));
            for(double f:{0.,sr/16,sr*.123,sr/3,sr/2}){Response v{};for(unsigned n=0;n<h.size();++n){C z=std::polar(16.,-2*pi*f*n/sr);v.l+=h[n].l*z;v.r+=h[n].r*z;}auto a=response(p,f,sr);check(std::abs(v.l-a.l)<1e-12&&std::abs(v.r-a.r)<1e-12);check(std::abs(std::norm(a.l)+std::norm(a.r)-1)<1e-12);++count;}
        }
    }
    const std::array<unsigned,4> d{8,16,32,64};
    Program known{{{Axis::Sum,8},{Axis::Left,16},{Axis::Difference,32},{Axis::Right,64}}};std::vector<Probe> probes;for(double f:{375.,750.,1125.,1500.,1875.,2250.})probes.push_back({f,std::clamp(std::norm(response(known,f,48000).r),0.,1.)});auto a=compile(probes,48000,d);check(a.evaluated==65536&&a.mse<1e-24);auto b=compile(probes,48000,d,32);check(b.evaluated==256&&b.mse>=a.mse);auto impossible=compile({{0,.5},{24000,.5}},48000,d);check(std::abs(impossible.mse-.25)<1e-12);
    bool rejected=false;try{compile({{25000,.5}},48000,d);}catch(const std::invalid_argument&){rejected=true;}check(rejected);rejected=false;try{compile(probes,48000,d,4);}catch(const std::invalid_argument&){rejected=true;}check(rejected);
    std::cout<<count<<" impulse/frequency cases; 65536-program exact target and restricted budget; DC/Nyquist negative control PASS\n";
}
