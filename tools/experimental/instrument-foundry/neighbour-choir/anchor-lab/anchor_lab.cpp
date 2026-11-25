#include "anchor_voice.hpp"
#include <fstream>
#include <iostream>
#include <vector>
#include <string>
#include <cstdlib>
using namespace mhac::neighbours;
unsigned checks=0;
void check(bool b){++checks;if(!b){std::cerr<<"FAIL "<<checks<<'\n';std::exit(1);}}
using Samples=std::vector<double>;
Samples render(AnchorPatch p,double rate=48000,unsigned block=127,double off=.45){
    AnchorVoice v;check(v.start(p,rate,.8));Samples out;
    const unsigned n=unsigned(rate*.7), end=unsigned(rate*off);
    for(unsigned k=0;k<n;k+=block)for(unsigned i=k;i<std::min(n,k+block);++i){if(i==end)v.release();double x=v.next();check(std::isfinite(x)&&std::abs(x)<=.25);out.push_back(x);}
    check(!v.active()&&out.back()==0);return out;
}
double error(const Samples& a,const Samples& b){check(a.size()==b.size());double s=0;for(unsigned i=0;i<a.size();++i)s+=std::pow(a[i]-b[i],2);return s;}
void wav(const std::string& path,const Samples& a,const Samples& b){
    check(a.size()==b.size());std::ofstream f(path,std::ios::binary);auto u=[&](unsigned x,unsigned n){for(unsigned i=0;i<n;++i)f.put(char((x>>(8*i))&255));};
    f.write("RIFF",4);u(36+unsigned(a.size())*4,4);f.write("WAVEfmt ",8);u(16,4);u(1,2);u(2,2);u(48000,4);u(192000,4);u(4,2);u(16,2);f.write("data",4);u(unsigned(a.size())*4,4);
    for(unsigned i=0;i<a.size();++i){u(std::uint16_t(std::lround(a[i]*32767)),2);u(std::uint16_t(std::lround(b[i]*32767)),2);}check(bool(f));
}
int main(int argc,char** argv){
    unsigned census[2][2][3]={};
    for(unsigned g=0;g<2;++g)for(unsigned u=0;u<16;++u)for(unsigned v=u+1;v<16;++v){auto w=witness(g,u,v);unsigned mass=0;for(auto x:w)mass+=unsigned(x);check(mass==0||mass==2);++census[g][adjacent(g,u,v)][mass];}
    check(census[0][1][2]==48&&census[0][0][0]==72&&census[1][1][0]==48&&census[1][0][0]==24&&census[1][0][2]==48);
    AnchorPatch p;auto r=render(p);p.shr=true;auto s=render(p);double adjacentContrast=error(r,s);check(adjacentContrast>1e-4);for(unsigned i=0;i<4800;++i)check(std::abs(r[i]-s[i])<1e-12);
    p.strength=0;auto baseline=render(p);check(error(s,baseline)<1e-24);p.shr=false;check(error(render(p),baseline)<1e-24);
    p.strength=.5;p.second=5;auto rn=render(p);p.shr=true;p.second=0;unsigned nonedge=0;for(unsigned i=1;i<16;++i)if(!adjacent(true,0,i)){auto w=witness(true,0,i);double m=0;for(auto x:w)m+=x;if(m==2){nonedge=i;break;}}check(nonedge>0);p.second=nonedge;auto sn=render(p);double nonadjacentContrast=error(rn,sn);check(nonadjacentContrast>1e-4);
    for(double rate:{8000.,44100.,48000.,96000.,192000.}){p.shr=false;p.second=1;p.time=.23;auto x=render(p,rate,1);check(x==render(p,rate,511));p.time=.6;auto late=render(p,rate);p.strength=0;check(late==render(p,rate));p.strength=.5;}
    AnchorVoice v;p.root=16;check(!v.start(p,48000));p.root=0;check(!v.start(p,NAN));p.time=0;check(v.start(p,48000));v.next();check(v.intervened());v.release();for(unsigned i=0;i<2000;++i)v.next();check(!v.active());
    std::cout<<"checks="<<checks<<" adjacent_difference_energy="<<adjacentContrast<<" nonadjacent_difference_energy="<<nonadjacentContrast<<" shrikhande_nonedge="<<nonedge<<'\n';
    if(argc>1){std::string path=argv[1];wav(path+"/adjacent.wav",r,s);wav(path+"/nonadjacent.wav",rn,sn);wav(path+"/linear-control.wav",baseline,baseline);}
}
