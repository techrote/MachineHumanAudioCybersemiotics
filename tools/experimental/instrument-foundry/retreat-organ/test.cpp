#include "engine.hpp"
#include <fstream>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <vector>
using namespace mhac::organ;
void req(bool ok,const char* m){if(!ok)throw std::runtime_error(m);}
void le(std::ostream& o,unsigned x,unsigned n){for(unsigned i=0;i<n;++i)o.put(char((x>>(8*i))&255));}
void wav(const std::string& name,const std::vector<double>& v){std::ofstream o(name,std::ios::binary);req(bool(o),"open wav");unsigned n=unsigned(v.size()*2);o.write("RIFF",4);le(o,36+n,4);o.write("WAVEfmt ",8);le(o,16,4);le(o,1,2);le(o,1,2);le(o,48000,4);le(o,96000,4);le(o,2,2);le(o,16,2);o.write("data",4);le(o,n,4);for(double x:v)le(o,unsigned(std::lround(x*32767)),2);o.close();req(bool(o),"write wav");}
std::vector<double> render(unsigned mode,double blend){Engine e;e.set(Mode,mode/2.);e.set(Blend,blend);e.set(Rate,0.);req(e.reset(48000)&&e.noteOn(0,48,1,.9),"render init");std::vector<double> y;for(unsigned i=0;i<57600;++i){if(i==52800)e.noteOff(0,48,1);auto s=e.next();req(std::isfinite(s)&&std::abs(s)<=.5,"bounds");y.push_back(s);}req(e.active()==0&&y.back()==0,"release");return y;}
int main(int argc,char** argv){try{
    req(argc==1||(argc==2&&std::string(argv[1])=="--render"),"usage: organ_test [--render]");
    Relays major,nested;for(unsigned i=0;i<pathSize(1);++i){major.visit(pathLevel(1,i));req(major.mass(0)==major.mass(1),"major equality");}for(unsigned i=0;i<pathSize(2);++i)nested.visit(pathLevel(2,i));req(nested.mass(0)==.875&&nested.mass(1)==0,"nested endpoint");
    for(unsigned n=0;n<83521;++n){Relays r;std::array<bool,8>a{},b{};unsigned k=n;for(int j=0;j<4;++j){unsigned x=k%17;k/=17;r.visit(x);for(unsigned i=0;i<8;++i){a[i]=x>=9+i||(x>=(i==7?8:7-i)&&a[i]);b[i]=x>=9+i||(x>=8-i&&b[i]);req(bool(r.a&(1u<<i))==a[i]&&bool(r.b&(1u<<i))==b[i],"relay oracle");}}}
    for(double sr:{1000.,1234.568,8000.,44100.,48000.,96000.,192000.,1234567.8,2000000.}){Engine e;req(e.reset(sr),"rate");for(int i=0;i<16;++i)req(e.noteOn(0,48+i,i,1),"voice admission");req(!e.noteOn(0,60,20,1),"capacity");for(unsigned i=0;i<unsigned(sr*.025);++i){auto s=e.next();req(std::isfinite(s)&&std::abs(s)<=.5,"poly bounds");}for(int i=0;i<16;++i)e.noteOff(0,48+i,i);for(unsigned i=0;i<unsigned(sr*.025)+1;++i)e.next();req(e.active()==0&&e.next()==0,"poly release");req(e.noteOn(0,127,5,1,1200),"high note");req(std::isfinite(e.next()),"high finite");}
    Engine e;req(!e.reset(999)&&!e.reset(2000001)&&!e.reset(std::numeric_limits<double>::quiet_NaN()),"invalid rate");req(!e.noteOn(-1,0,0,1)&&!e.noteOn(0,128,0,1)&&!e.noteOn(0,60,0,std::numeric_limits<double>::infinity()),"invalid notes");Params p{};auto state=encode(defaults);req(decode(state,p),"decode");for(unsigned i=0;i<Count;++i)req(std::abs(p[i]-defaults[i])<1e-7,"roundtrip");state[7]=255;auto before=p;req(!decode(state,p)&&p==before,"reject corrupt");
    auto a=render(1,0),b=render(1,1),c=render(2,0),d=render(2,1);req(a==b,"major audio equality");req(c==render(2,0)&&d==render(2,1),"determinism");double energy=0;for(unsigned i=24000;i<48000;++i)energy+=(c[i]-d[i])*(c[i]-d[i]);req(energy>.01,"nested audio divergence");
    if(argc==2){wav("major-a.wav",a);wav("major-b.wav",b);wav("nested-a.wav",c);wav("nested-b.wav",d);}
    std::cout<<"83521 histories, 9 rates, major exact equality, nested final difference energy "<<energy<<" PASS\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
