// Offline paired-engine convergence laboratory. No SDK required.
#include "engine.hpp"
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
using namespace mhac::choir;
constexpr unsigned sr=48000;
void require(bool ok,const char* what){if(!ok)throw std::runtime_error(what);}
void little(std::ostream& out,unsigned x,unsigned n){for(unsigned i=0;i<n;++i)out.put(char((x>>(8*i))&255));}
void header(std::ostream& out,unsigned frames){out.write("RIFF",4);little(out,36+4*frames,4);out.write("WAVEfmt ",8);little(out,16,4);little(out,1,2);little(out,2,2);little(out,sr,4);little(out,sr*4,4);little(out,4,2);little(out,16,2);out.write("data",4);little(out,frames*4,4);}
void pcm(std::ostream& out,double x){little(out,unsigned(std::lround(x*32767)),2);}
Engine make(unsigned mask,double seed,double rate){Engine e;e.set(Score,mask/255.);e.set(Seed,seed);e.set(Rate,rate);e.set(Colour,.8);e.set(Gain,.7);require(e.reset(sr),"reset");require(e.noteOn(0,48,1,.8),"note on");return e;}
struct Result{unsigned last=0,bound=0;double peak=0,energy=0;};
Result compare(unsigned mask,double rate,const std::string& wav={}){
    auto a=make(mask,0,rate),b=make(mask,1,rate);
    const unsigned interval=unsigned(std::llround(sr*(.015+.105*rate)));
    const unsigned bound=compile(mask).size*interval+unsigned(std::ceil(.005*sr))+2;
    const unsigned frames=bound+sr/4;
    std::ofstream out;if(!wav.empty()){out.open(wav,std::ios::binary);require(bool(out),"open WAV");header(out,frames);}
    Result r;r.bound=bound;
    for(unsigned i=0;i<frames;++i){
        double l=a.next(),rr=b.next();require(std::isfinite(l)&&std::isfinite(rr)&&std::abs(l)<=.5&&std::abs(rr)<=.5,"output bounds");
        if(l!=rr)r.last=i+1;
        if(i>=bound)require(l==rr,"post-bound divergence");
        r.peak=std::max(r.peak,std::abs(l-rr));r.energy+=(l-rr)*(l-rr);
        if(out.is_open()){pcm(out,l);pcm(out,rr);}
    }
    require(r.last>0,"no initial contrast");
    if(out.is_open()){out.close();require(bool(out),"write WAV");}
    a.noteOff(0,48,1);b.noteOff(0,48,1);
    for(unsigned i=0;i<sr/20;++i){a.next();b.next();}
    require(a.active()==0&&b.active()==0&&a.next()==0&&b.next()==0,"release silence");
    return r;
}
int main(int argc,char** argv){try{
    require(argc<=2,"usage: convergence [--render]");const bool render=argc==2;require(!render||std::string(argv[1])=="--render","unknown option");
    std::ofstream csv;if(render){csv.open("convergence.csv");require(bool(csv),"open CSV");csv<<"mask,program_steps,last_different_sample_plus_one,conservative_bound_samples,peak_difference,difference_energy\n";}
    unsigned latest=0,latestMask=0;
    for(unsigned m=0;m<256;++m){auto r=compare(m,0);if(r.last>latest){latest=r.last;latestMask=m;}if(render)csv<<m<<','<<compile(m).size<<','<<r.last<<','<<r.bound<<','<<r.peak<<','<<r.energy<<'\n';}
    auto a=make(0,0,0),b=make(255,0,0);double diff=0;
    for(unsigned i=0;i<sr;++i){double l=a.next(),r=b.next();if(i>sr/2)diff+=std::abs(l-r);}
    require(diff>1.,"different-target negative control");
    if(render){for(unsigned m:{0u,85u,170u,255u})compare(m,.25,"score-"+std::to_string(m)+"-paired.wav");csv.close();require(bool(csv),"write CSV");}
    std::cout<<"256 profiles PASS; latest convergence boundary "<<latest<<" samples (mask "<<latestMask<<"); negative control difference "<<diff<<'\n';
    return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
