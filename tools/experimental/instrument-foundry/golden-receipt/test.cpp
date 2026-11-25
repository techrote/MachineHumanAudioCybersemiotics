#include "engine.hpp"
#include <iostream>
#include <cstdlib>
#include <vector>
#include <fstream>
#include <string>
using namespace mhac::golden;
unsigned long long checks=0;
void check(bool yes){++checks;if(!yes){std::cerr<<"FAIL at assertion "<<checks<<'\n';std::exit(1);}}
std::vector<double> render(unsigned deletion,bool equal,double rate,unsigned chunk){Engine e;e.set(Shape,equal);e.set(Delete,deletion/4.);check(e.reset(rate));check(e.noteOn(0,69,7,.9));std::vector<double> out(size_t(rate*1.7));for(size_t start=0;start<out.size();start+=chunk)for(size_t i=start;i<std::min(start+chunk,out.size());++i){out[i]=e.next();check(std::isfinite(out[i])&&std::abs(out[i])<=.5);}check(!e.active());return out;}
void wav(const std::string& path,const std::vector<double>& x){std::ofstream f(path,std::ios::binary);auto le=[&](unsigned v,unsigned n){for(unsigned i=0;i<n;++i)f.put(char(v>>(8*i)));};f.write("RIFF",4);le(36+4*x.size(),4);f.write("WAVEfmt ",8);le(16,4);le(1,2);le(2,2);le(48000,4);le(192000,4);le(4,2);le(16,2);f.write("data",4);le(4*x.size(),4);for(double y:x){auto q=std::int16_t(std::lround(y*32767));le(std::uint16_t(q),2);le(std::uint16_t(q),2);}check(bool(f));}
int main(int argc,char** argv){
 for(double sr:{8000.,44100.,48000.,96000.,192000.}){
  auto a=render(1,false,sr,1),b=render(3,false,sr,127),c=render(2,false,sr,64),d=render(4,false,sr,511);check(a==b);check(c==d);check(a!=c);check(a!=render(0,false,sr,17));check(render(1,true,sr,19)!=render(2,true,sr,23));
  Engine e;check(e.reset(sr));for(unsigned i=0;i<16;++i)check(e.noteOn(0,60+i,i,1));check(!e.noteOn(0,80,99,1));for(unsigned i=0;i<300;++i)check(std::abs(e.next())<=.5);e.noteOff(0,60,0);for(unsigned i=0;i<unsigned(sr*.011);++i)e.next();check(e.active()==15);for(unsigned i=1;i<16;++i)e.noteOff(0,60+i,i);for(unsigned i=0;i<unsigned(sr*.011);++i)e.next();check(e.active()==0);check(e.next()==0);
  check(e.noteOn(1,60,-1,1));e.noteOff(0,60,-1);check(e.active()==1);e.noteOff(1,60,-1);for(unsigned i=0;i<unsigned(sr*.011);++i)e.next();check(e.active()==0);
 }
 // Extreme and fractional validator rates: full longest motif, aliases, release, and rejection.
 for(double sr:{1000.,1234.568,384000.,1234567.8,2000000.}){
  Engine a,b;check(a.reset(sr)&&b.reset(sr));a.set(Delete,.25);b.set(Delete,.75);a.set(Span,1);b.set(Span,1);a.set(Width,1);b.set(Width,1);check(a.noteOn(0,127,1,1,1200)&&b.noteOn(0,127,1,1,1200));
  unsigned nonzero=0;for(unsigned i=0;i<unsigned(std::ceil(sr*1.59));++i){double x=a.next(),y=b.next();check(x==y&&std::isfinite(x)&&std::abs(x)<=.5);nonzero+=x!=0;}
  check(nonzero>0&&!a.active()&&!b.active()&&a.next()==0&&b.next()==0);
  check(a.noteOn(0,60,2,1));a.noteOff(0,60,2);for(unsigned i=0;i<unsigned(std::ceil(sr*.011));++i)check(std::abs(a.next())<=.5);check(!a.active()&&a.next()==0);
 }
 Engine e;check(!e.reset(0));check(!e.reset(999.999));check(!e.reset(2000000.1));check(!e.reset(std::numeric_limits<double>::infinity()));check(!e.reset(std::numeric_limits<double>::quiet_NaN()));check(!e.noteOn(0,128,0,1));check(!e.noteOn(0,60,0,0));e.set(Gain,std::numeric_limits<double>::infinity());check(e.params()[Gain]==defaults[Gain]);Params p{1,.25,.3,.95,.1},q{};auto s=encode(p);check(decode(s,q));for(unsigned i=0;i<Count;++i)check(std::abs(p[i]-q[i])<1e-7);s[0]=0;check(!decode(s,q));s=encode(p);s[7]=255;check(!decode(s,q));
 if(argc>1){for(unsigned d=0;d<=4;++d)wav(std::string(argv[1])+"/golden-"+std::to_string(d)+".wav",render(d,false,48000,127));wav(std::string(argv[1])+"/equal-delete-1.wav",render(1,true,48000,127));}
 std::cout<<"PASS "<<checks<<" assertions\n";
}
