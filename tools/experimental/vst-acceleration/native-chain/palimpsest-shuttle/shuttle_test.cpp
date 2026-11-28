#include "shuttle.hpp"
#include "shuttle_rate_test.hpp"
#include <cassert>
#include <cstdio>
#include <fstream>
#include <iostream>
#include <limits>
#include <memory>
#include <vector>
using namespace mhac::accel;
using Engine=PalimpsestShuttle<>;
static unsigned long long checks=0;
static void check(bool ok) { ++checks; if(!ok) {std::cerr<<"FAIL "<<checks<<'\n'; std::abort();} }
static float fixture(unsigned n) { return float(int((n*1664525u+1013904223u)>>20)-2048)/4096.f; }
static bool same(ShuttleFrame a,ShuttleFrame b) {return a.l==b.l&&a.r==b.r;}
static void qualify(unsigned rate) {
    auto e=std::make_unique<Engine>();
    check(e->prepare(rate)); const unsigned g=e->grainSamples();
    check(g%2==0&&g>=640&&g<=15360);
    std::vector<ShuttleFrame> x(5*g);
    for(unsigned n=0;n<x.size();++n) x[n]={fixture(n),fixture(n+163)};
    const auto at=[&](int n){return n<0?ShuttleFrame{}:x[unsigned(n)];};
    for(unsigned mode=0;mode<2;++mode) {
        check(e->configure({1000,uint16_t(mode*1000),0,0,false})); e->reset();
        for(unsigned n=0;n<x.size();++n) {
            auto y=e->process(x[n]);
            if(!mode) {auto a=at(int(n)-int(g)); check(std::abs(y.l-a.l)<2.e-7f&&std::abs(y.r-a.r)<2.e-7f);}
            else {
                const unsigned p=n%g, q=(p+g/2)%g;
                const double w=2.*std::min(p,g-p)/g;
                const auto a=at(int(n)-int(2*p+1)), b=at(int(n)-int(2*q+1));
                check(std::abs(y.l-(w*a.l+(1-w)*b.l))<3.e-7&&std::abs(y.r-(w*a.r+(1-w)*b.r))<3.e-7);
            }
        }
    }
    auto f=std::make_unique<Engine>(); check(f->prepare(rate));
    check(e->configure({400,800,1000,1000,false})); check(f->configure(e->patch())); e->reset(); f->reset();
    std::vector<ShuttleFrame> y(x.size());
    for(unsigned n=0;n<x.size();++n) {if(n==g) check(e->configure({800,100,900,200,false})); y[n]=e->process(x[n]); check(std::abs(y[n].l)<=1&&std::abs(y[n].r)<=1);}
    for(unsigned n=0;n<x.size();) {const unsigned end=std::min(unsigned(x.size()),n+1+(n%127)); for(;n<end;++n) {if(n==g) check(f->configure({800,100,900,200,false}));check(same(y[n],f->process(x[n])));}}
    check(e->configure({1000,0,1000,1000,false})); e->reset();
    for(unsigned n=0;n<4*g;++n) {
        auto z=e->process(n?ShuttleFrame{}:ShuttleFrame{1,0});
        if(n==g) check(std::abs(z.l-.35f)<2.e-7f&&z.r==0);
        if(n==2*g) check(std::abs(z.r-.2275f)<2.e-7f&&z.l==0);
        if(n==3*g) check(std::abs(z.l-.147875f)<2.e-7f&&z.r==0);
    }
    float peak=0; for(unsigned n=0;n<50*g;++n) {auto z=e->process({}); if(n>=49*g) peak=std::max({peak,std::abs(z.l),std::abs(z.r)});} check(peak<1.e-8f);
    check(e->configure({1000,1000,1000,1000,true}));
    check(same(e->process({std::numeric_limits<float>::infinity(),-2}),{0,-1}));
    check(!e->configure({1001,0,0,0,false})); check(e->patch().bypass); check(!e->prepare(7999)); check(e->grainSamples()==g);
}
static void put(std::ofstream& out,unsigned x,unsigned bytes) {for(unsigned i=0;i<bytes;++i) out.put(char((x>>(8*i))&255));}
static void render(const char* name,ShuttlePatch p) {
    constexpr unsigned rate=48000, count=rate*8;
    auto e=std::make_unique<Engine>(); check(e->prepare(rate)); check(e->configure(p)); e->reset();
    std::ofstream out(name,std::ios::binary); check(bool(out));
    out.write("RIFF",4);put(out,36+count*4,4);out.write("WAVEfmt ",8);put(out,16,4);put(out,1,2);put(out,2,2);put(out,rate,4);put(out,rate*4,4);put(out,4,2);put(out,16,2);out.write("data",4);put(out,count*4,4);
    const double notes[]={110,164.8138,220,146.8324,196,293.6648,130.8128,174.6141,261.6256,196,146.8324,110};
    for(unsigned n=0;n<count;++n) {
        const unsigned step=n/24000, within=n%24000; const double t=double(within)/rate;
        ShuttleFrame in{};
        if(step<12) {
            const double a=std::min(1.,t/.008)*std::max(0.,1.-t/.42);
            const double phase=6.283185307179586*notes[step]*t;
            const float s=float(.22*a*(std::sin(phase)+.32*std::sin(2*phase)+.17*std::sin(3*phase)));
            in=step%2?ShuttleFrame{s*.45f,s}:ShuttleFrame{s,s*.45f};
        }
        const auto y=e->process(in); check(std::isfinite(y.l)&&std::isfinite(y.r)&&std::abs(y.l)<=.4f&&std::abs(y.r)<=.4f);
        for(float v:{y.l,y.r}) put(out,uint16_t(int(std::lround(v*32767.f))),2);
    }
    check(bool(out));
}
int main(int argc,char**) {
    qualifyShuttleRates();
    for(unsigned r:{8000u,24000u,44100u,48000u,96000u,192000u}) qualify(r);
    auto small=std::make_unique<PalimpsestShuttle<2048>>();check(small->prepare(24000));check(!small->prepare(48000));
    for(unsigned i=0;i<=1000;++i) {ShuttlePatch p{uint16_t(i),uint16_t(1000-i),uint16_t(i),uint16_t(i),bool(i&1)};ShuttlePatch q{};auto s=encode(p);check(decode(s,q)&&encode(q)==s);s[12]=2;check(!decode(s,q)&&encode(q)==encode(p));}
    if(argc>1) {render("dry.wav",{0,0,0,0,true});render("forward.wav",{700,0,450,0,false});render("mirror.wav",{850,1000,250,0,false});render("shuttle.wav",{800,850,800,1000,false});}
    std::cout<<"PASS "<<checks<<" checks; desktop bytes "<<sizeof(Engine)<<"; embedded bytes "<<sizeof(PalimpsestShuttle<2048>)<<'\n';
}
