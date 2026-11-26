#include "rest.hpp"
#include <cstdlib>
#include <iostream>
using namespace restbus;
void check(bool ok){if(!ok)std::exit(1);}
int main(){
    Engine a,b;check(a.prepare(48000,.01)&&b.prepare(48000,.01));
    a.domain(Domain::manual);b.domain(Domain::manual);
    check(a.on(1,57,0,1)&&b.on(1,57,0,1));
    a.step();a.step();
    for(int i=0;i<4800;++i)check(a.tick()==b.tick()); // changing selector cannot retune a held note
    check(a.on(2,57,0,1)&&b.on(2,57,0,1));
    bool differs=false;for(int i=0;i<4800;++i)if(a.tick()!=b.tick())differs=true;
    check(differs);
    a.reset();a.domain(Domain::idle);check(a.on(1,57,0,1)&&a.on(2,57,0,1));
    for(int i=0;i<4800;++i)a.tick();
    a.off(1);
    for(int i=0;i<960;++i)a.tick();
    check(a.index()==0);
    a.off(2);bool audible=false;for(int i=0;i<480;++i)if(a.tick()!=0)audible=true;
    check(audible&&a.index()==1); // idle measures keys, not residual audio
    for(int i=0;i<1440;++i)a.tick();
    check(a.tick()==0);
    std::cout<<"PASS note-local pitch and gate/release independence\n";
}
