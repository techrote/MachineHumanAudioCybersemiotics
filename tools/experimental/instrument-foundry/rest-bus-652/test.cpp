#include "rest.hpp"
#include <cstdlib>
#include <iostream>
#include <limits>
#include <set>
#include <vector>
using namespace restbus;
unsigned checks=0;
void check(bool b){++checks;if(!b){std::cerr<<"failure at assertion "<<checks<<'\n';std::exit(1);}}
int main(){
    for(unsigned total:{0u,4u,8u,11u,12u}){
        std::set<unsigned> paths;
        for(unsigned a=0;a<=total;++a)for(unsigned b=0;b<=total-a;++b)for(unsigned c=0;c<=total-a-b;++c){
            Clock clock;clock.period(3);unsigned code=0;
            for(unsigned g:{a,b,c,total-a-b-c}){
                for(unsigned i=0;i<3*g;++i)clock.tick(false);
                code=code*5+clock.index();unsigned prev=clock.index();
                for(unsigned i=0;i<7;++i)clock.tick(true);
                check(clock.index()==prev);
            }
            check(clock.index()==total%5);paths.insert(code);
        }
        check(paths.size()==(total==0?1:total==4?35:total==8?105:total==11?124:125));
        std::cout<<"T="<<total<<" paths="<<paths.size()<<'\n';
    }
    for(double sr:{1000.,1234.568,44100.,48000.,96000.,192000.,1234567.8,2000000.}){
        Engine a,b;check(a.prepare(sr,.01)&&b.prepare(sr,.01));unsigned n=unsigned(std::lround(sr*.01));
        for(unsigned i=0;i<n-1;++i)check(a.tick()==0&&b.tick()==0);
        check(a.index()==0);check(a.tick()==0&&b.tick()==0&&a.index()==1);
        for(int j=0;j<8;++j){check(a.on(j,60+j,0,1));check(b.on(j,60+j,0,1));}
        check(!a.on(9,60,0,1));check(!a.on(0,60,0,1));
        std::vector<double> x(n),y(n);std::vector<float> z(n);
        a.process(x.data(),y.data(),n);
        for(unsigned pos=0;pos<n;){unsigned len=std::min(17u,n-pos);b.process(z.data()+pos,z.data()+pos,len);pos+=len;}
        for(unsigned i=0;i<n;++i)check(x[i]==y[i]&&float(x[i])==z[i]&&std::isfinite(x[i])&&std::abs(x[i])<=.481);
        check(a.index()==1&&b.index()==1);
        for(int j=0;j<8;++j)a.off(j);
        for(unsigned i=0;i<unsigned(std::ceil(sr*.04));++i)check(std::abs(a.tick())<=.481);
        check(a.tick()==0);a.reset();check(a.tick()==0);
        check(!a.on(0,128,0,1)&&!a.on(0,60,0,std::numeric_limits<double>::quiet_NaN()));
    }
    Clock c;c.period(2);c.tick(false);check(c.partial()==1);c.tick(true);check(c.partial()==1);c.tick(false);check(c.index()==1);
    c.domain(Domain::held);c.tick(false);c.tick(true);c.tick(true);check(c.index()==2);
    c.domain(Domain::rendered);c.tick(false);c.tick(true);check(c.index()==3);
    c.domain(Domain::manual);for(int i=0;i<20;++i)c.tick(false);check(c.index()==3);c.step();check(c.index()==4);c.step();check(c.index()==0);
    Engine e;check(!e.prepare(0)&&!e.prepare(48000,0)&&!e.prepare(std::numeric_limits<double>::infinity()));
    std::cout<<"PASS "<<checks<<" assertions\n";
}
