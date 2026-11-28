#include "phase_routes.hpp"
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <limits>
#include <string>
using namespace mhac::orbit;
static unsigned checks=0;
static void check(bool ok){++checks;if(!ok){std::cerr<<"FAIL "<<checks<<'\n';std::exit(1);}}
static void le(std::ostream& o,unsigned v,unsigned n){for(unsigned i=0;i<n;++i)o.put(char((v>>(8*i))&255u));}
static void render(const std::string& path,bool shaped,const escape::PhaseBank& bank){
    constexpr unsigned rate=48000, frames=rate*5;
    Engine e;check(e.prepare(rate));check(e.setPatch({300,500,0}));
    std::ofstream o(path,std::ios::binary);check(bool(o));
    o.write("RIFF",4);le(o,36+frames*4,4);o.write("WAVEfmt ",8);le(o,16,4);le(o,1,2);le(o,2,2);
    le(o,rate,4);le(o,rate*4,4);le(o,4,2);le(o,16,2);o.write("data",4);le(o,frames*4,4);
    for(unsigned i=0;i<frames;++i){
        for(unsigned j=0;j<4;++j){
            if(i==j*rate/5){check(e.noteOn(int(j),std::array<int,4>{45,52,57,64}[j],.7));
                if(shaped){const auto& route=bank.route(j*17);check(e.noteSustain(int(j),route.gain,route.length,.85,900.+j*400.));}}
            if(i==rate*3+j*rate/5){const auto& route=bank.route(j*17);check(e.noteOffShaped(int(j),route.gain,route.length,.5));}
        }
        double l,r;e.tick(l,r);check(std::isfinite(l)&&std::isfinite(r)&&std::abs(l)<=.52&&std::abs(r)<=.52);
        le(o,unsigned(int(std::lround(l*32767.))),2);le(o,unsigned(int(std::lround(r*32767.))),2);
    }
    check(e.active()==0);check(bool(o));
}
int main(int argc,char** argv){
    escape::PhaseBank bank;check(bank.prepare());
    for(unsigned phase=0;phase<68;++phase){
        const auto& route=bank.route(phase);SustainPath p;
        check(p.configure(route.gain,route.length,.8,1000.,200.));
        std::array<double,200> first{};
        for(auto& v:first){v=p.tick();check(v>=0.&&v<=.8);}
        check(first[0]==0.&&first[100]==.8);
        for(unsigned i=1;i<100;++i)check(first[i]==first[200-i]);
        for(double v:first)check(v==p.tick());
        check(!p.configure(route.gain,route.length,1.,1000.,199.));check(p.tick()==first[0]);
    }
    for(double rate:{1000.,44100.,48000.,96000.,2000000.}){
        const auto& route=bank.route(17);Engine a,b,c;
        for(auto* e:{&a,&b,&c}){check(e->prepare(rate));check(e->setPatch({250,10,0}));check(e->noteOn(0,45,.8));}
        check(!b.noteSustain(0,route.gain,route.length,std::numeric_limits<double>::quiet_NaN(),200.));
        check(b.noteSustain(0,route.gain,route.length,0.,200.));check(c.noteSustain(0,route.gain,route.length,1.,200.));
        check(!c.noteSustain(0,route.gain,route.length,1.,200.));
        bool differs=false;const unsigned held=unsigned(rate*.12);
        for(unsigned i=0;i<held+unsigned(rate*.011)+2;++i){
            if(i==held){for(auto* e:{&a,&b,&c})check(e->noteOffShaped(0,route.gain,route.length,.5));}
            double al,ar,bl,br,cl,cr;a.tick(al,ar);b.tick(bl,br);c.tick(cl,cr);
            check(al==bl&&ar==br);check(std::isfinite(cl)&&std::isfinite(cr)&&std::abs(cl)<=.52&&std::abs(cr)<=.52);
            differs|=al!=cl||ar!=cr;
            if(i==1)check(!a.noteSustain(0,route.gain,route.length,.5,200.));
        }
        check(differs&&a.active()==0&&b.active()==0&&c.active()==0);double l,r;c.tick(l,r);check(l==0.&&r==0.);
    }
    if(argc==3){render(argv[1],false,bank);render(argv[2],true,bank);}
    std::cout<<"SUSTAIN_PASS checks="<<checks<<'\n';
}
