#include "guest.hpp"
#include <cstdlib>
#include <iostream>
#include <limits>
#include <vector>
#define CHECK(x) do{if(!(x)){std::cerr<<"failure line "<<__LINE__<<": "<<#x<<'\n';return 1;}}while(0)
int main(){
    unsigned long long frames=0;
    for(double rate:{1000.,8000.,44100.,48000.,96000.,192000.}){
        guest::Engine plain,cited,adopted,both;
        guest::Patch p; p.stepsPerSecond=12;
        CHECK(plain.prepare(rate)&&cited.prepare(rate)&&adopted.prepare(rate)&&both.prepare(rate));
        CHECK(plain.configure(p));p.cite=true;CHECK(cited.configure(p));p.adopt=true;CHECK(both.configure(p));p.cite=false;CHECK(adopted.configure(p));
        CHECK(plain.on(1,57,13,.8)&&cited.on(1,57,13,.8)&&adopted.on(1,57,13,.8)&&both.on(1,57,13,.8));
        const unsigned boundary=4*unsigned(std::lround(rate/12)); bool divergence=false;
        for(unsigned i=0;i<boundary*2;++i){auto a=plain.tick(),b=cited.tick(),c=adopted.tick(),d=both.tick();++frames;
            CHECK(a.left==b.left&&a.right==b.right&&c.left==d.left&&c.right==d.right);
            CHECK(a.left==c.left&&a.counter==0&&std::isfinite(c.right)&&std::abs(c.right)<=.52);
            if(i<boundary)CHECK(a.right==c.right&&c.counter==0);else if(a.right!=c.right)divergence=true;
        }
        CHECK(divergence);
        // Configure does not retroactively adopt a playing quote; a new note has independent scope.
        p.adopt=true;CHECK(plain.configure(p));for(unsigned i=0;i<boundary;++i)CHECK(plain.tick().counter==0);
        for(auto* e:{&plain,&cited,&adopted,&both}){e->off(1);for(unsigned i=0;i<unsigned(rate*.031)+2;++i)e->tick();auto f=e->tick();CHECK(f.left==0&&f.right==0);}
        guest::Engine a,b;CHECK(a.prepare(rate)&&b.prepare(rate));CHECK(a.configure(p)&&b.configure(p));
        for(unsigned i=0;i<guest::Engine::capacity;++i){CHECK(a.on(int(i),127,1200,100)&&b.on(int(i),127,1200,100));}
        CHECK(!a.on(99,60,0,1)&&!a.on(0,60,0,1));
        std::vector<double> l(997),r(997);std::vector<float> lf(997),rf(997);a.process(l.data(),r.data(),997);
        for(unsigned pos=0;pos<997;){unsigned n=std::min(997-pos,1+pos%71);b.process(lf.data()+pos,rf.data()+pos,n);pos+=n;}
        for(unsigned i=0;i<997;++i)CHECK(float(l[i])==lf[i]&&float(r[i])==rf[i]&&std::abs(r[i])<=.52);
        a.reset();b.reset();CHECK(a.tick().right==0);
        p.adopt=false;CHECK(a.configure(p)&&b.configure(p));CHECK(a.on(10,60,0,1)&&b.on(10,60,0,1));
        std::array<double,64> mono{},alias{};a.process(mono.data(),static_cast<double*>(nullptr),64);b.process(alias.data(),alias.data(),64);CHECK(mono==alias);
        for(unsigned i=0;i<boundary*2;++i)CHECK(a.tick().counter==0);
        a.reset();CHECK(a.tick().right==0);CHECK(!a.on(1,60,0,std::numeric_limits<double>::quiet_NaN()));
        p.counterGain=std::numeric_limits<double>::infinity();CHECK(!a.configure(p));
        CHECK(!a.prepare(0));
    }
    std::cout<<"PASS: six rates, "<<frames<<" paired history frames, scope, release, saturation, partition and formats\n";
}
