#include "engine.hpp"
#include <chrono>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <vector>
#include <string>
using namespace mhac::neighbours;
unsigned checks=0;
void check(bool b){++checks;if(!b){std::cerr<<"FAIL check "<<checks<<'\n';std::exit(1);}}
std::vector<double> render(bool shr,bool intervention,unsigned block=64,double rate=48000){Engine e;e.set(Topology,shr);e.set(Intervention,intervention);e.reset(rate);std::vector<double> y;unsigned n=unsigned(rate*.6),off=unsigned(rate*.45);for(unsigned start=0;start<n;start+=block)for(unsigned i=start;i<std::min(n,start+block);++i){if(i==0)check(e.noteOn(0,57,7,.8));if(i==off)e.noteOff(0,57,7);double v=e.next();check(std::isfinite(v)&&std::abs(v)<=.5);y.push_back(v);}check(!e.active()&&y.back()==0);return y;}
void wav(const std::string& name,const std::vector<double>& x){std::ofstream f(name,std::ios::binary);auto u=[&](unsigned v,unsigned n){for(unsigned i=0;i<n;++i)f.put(char((v>>(8*i))&255));};f.write("RIFF",4);u(36+unsigned(x.size())*2,4);f.write("WAVEfmt ",8);u(16,4);u(1,2);u(1,2);u(48000,4);u(96000,4);u(2,2);u(16,2);f.write("data",4);u(unsigned(x.size())*2,4);for(double v:x)u(std::uint16_t(std::lround(v*32767)),2);check(bool(f));}
int main(int argc,char** argv){
    for(unsigned g=0;g<2;++g)for(unsigned u=0;u<16;++u)for(unsigned v=0;v<16;++v){unsigned c=0;for(unsigned k=0;k<16;++k)c+=adjacent(g,u,k)&&adjacent(g,v,k);check(c==(u==v?6:2));if(adjacent(g,u,v)){auto w=witness(g,u,v);double s=0;for(double a:w)s+=a;check(s==(g?0:2));}}
    for(unsigned g=0;g<2;++g){Wave x{};x[0]=1;auto p=Propagator::make(.09,.017,1.);for(unsigned i=0;i<4000;++i){p.step(x,g);double energy=0;for(auto z:x)energy+=std::norm(z);check(std::abs(energy-1)<1e-10);}}
    double maxdiff=0,contrast=0;auto a=render(false,false),b=render(true,false),c=render(false,true),d=render(true,true);for(unsigned i=0;i<a.size();++i){maxdiff=std::max(maxdiff,std::abs(a[i]-b[i]));contrast+=std::pow(c[i]-d[i],2);check(std::abs(b[i]-d[i])<1e-13);if(i<4800)check(a[i]==c[i]);}check(maxdiff<1e-12&&contrast>1e-5);check(c==render(false,true,1)&&c==render(false,true,511));
    for(double rate:{1000.,1234.568,44100.,48000.,96000.,192000.,1234567.8,2000000.}){Engine e;check(e.reset(rate));check(e.next()==0);for(int i=0;i<8;++i)check(e.noteOn(i,60,i,1));check(!e.noteOn(0,60,99,1));for(int i=0;i<8;++i)e.noteOff(i,60,i);check(e.next()==0&&e.active()==0);}
    Params p=defaults,q{};check(decode(encode(p),q));for(unsigned i=0;i<Count;++i)check(std::abs(p[i]-q[i])<1e-7);auto bad=encode(p);bad[0]=0;check(!decode(bad,q));Engine e;check(!e.reset(0));check(!e.noteOn(0,128,0,1));e.set(Gain,NAN);check(e.params()[Gain]==defaults[Gain]);
    auto begin=std::chrono::steady_clock::now();for(int i=0;i<8;++i)e.noteOn(0,60+i,i,1);double sum=0;for(int i=0;i<48000;++i)sum+=std::abs(e.next());double sec=std::chrono::duration<double>(std::chrono::steady_clock::now()-begin).count();check(sum>0);std::cout<<"checks="<<checks<<" linear_maxdiff="<<maxdiff<<" intervention_difference_energy="<<contrast<<" 8voice_1s_cpu_wall="<<sec<<'\n';
    if(argc>1){std::string root=argv[1];wav(root+"/rook-linear.wav",a);wav(root+"/shrikhande-linear.wav",b);wav(root+"/rook-intervention.wav",c);wav(root+"/shrikhande-intervention.wav",d);}
}
