#include "engine.hpp"
#include <array>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>
using namespace mhac::neighbours;
unsigned checks=0;
void require(bool b){++checks;if(!b){std::cerr<<"FAIL "<<checks<<'\n';std::exit(1);}}
using Audio=std::vector<double>;
Audio render(bool shr,unsigned root,unsigned second,double timing,double strength,unsigned block,bool change=false,bool early=false,double sr=48000){
    Engine e;e.set(Topology,shr);e.set(RootAnchor,root/15.);e.set(SecondAnchor,second/15.);e.set(Timing,timing/2);e.set(Strength,strength);require(e.reset(sr));Audio y;const unsigned n=unsigned(.65*sr);
    for(unsigned start=0;start<n;start+=block){for(unsigned i=start;i<std::min(n,start+block);++i){if(i==0)require(e.noteOn(0,57,1,.8));if(i==unsigned(.05*sr)&&change){e.set(RootAnchor,1);e.set(SecondAnchor,0);e.set(Timing,1);e.set(Strength,0);}if(i==unsigned((early?.07:.5)*sr))e.noteOff(0,57,1);double s=e.next();require(std::isfinite(s)&&std::abs(s)<=.5);y.push_back(s);}}require(!e.active()&&y.back()==0);return y;
}
double diff(const Audio& a,const Audio& b){double s=0;for(unsigned i=0;i<a.size();++i)s+=std::pow(a[i]-b[i],2);return s;}
void wav(const std::string& path,const Audio& a,const Audio& b){std::ofstream f(path,std::ios::binary);auto u=[&](unsigned v,unsigned n){for(unsigned i=0;i<n;++i)f.put(char((v>>(8*i))&255));};f.write("RIFF",4);u(36+unsigned(a.size())*4,4);f.write("WAVEfmt ",8);u(16,4);u(1,2);u(2,2);u(48000,4);u(192000,4);u(4,2);u(16,2);f.write("data",4);u(unsigned(a.size())*4,4);for(unsigned i=0;i<a.size();++i){u(std::uint16_t(std::lround(a[i]*32767)),2);u(std::uint16_t(std::lround(b[i]*32767)),2);}require(bool(f));}
int main(int argc,char** argv){
    auto bytes=encode(defaults);std::array<std::uint8_t,24> old{};std::copy_n(bytes.begin(),old.size(),old.begin());old[3]='1';Params q{};require(decodeBytes(old.data(),unsigned(old.size()),q));for(unsigned i=5;i<Count;++i)require(q[i]==defaults[i]);for(unsigned i=0;i<5;++i)require(std::abs(q[i]-defaults[i])<1e-7);require(decode(encode(q),q));auto saved=q;require(!decodeBytes(old.data(),23,q)&&q==saved);bytes[3]='9';require(!decode(bytes,q)&&q==saved);bytes=encode(defaults);bytes.back()=255;require(!decode(bytes,q)&&q==saved);require(!decodeBytes(nullptr,40,q));
    auto r=render(false,0,1,.1,.5,64),s=render(true,0,1,.1,.5,64),rn=render(false,0,5,.1,.5,64),sn=render(true,0,6,.1,.5,64),control=render(false,0,1,.1,0,64);require(diff(r,s)>1e-5);require(diff(r,sn)<1e-20);require(diff(s,rn)<1e-20);require(diff(s,control)<1e-20);require(r==render(false,0,1,.1,.5,511,true));require(r==render(false,0,0,.1,.5,1));require(render(false,0,1,.1,1,64,false,true)==render(false,0,1,.1,0,64,false,true));
    auto late=render(false,0,1,.3,.75,64),late0=render(false,0,1,.3,0,64);require(std::equal(late.begin(),late.begin()+14400,late0.begin()));require(diff(late,late0)>1e-5);
    for(double rate:{8000.,44100.,96000.,192000.}){auto a=render(false,7,6,.2,.8,17,false,false,rate),b=render(false,7,6,.2,.8,511,false,false,rate);require(a==b);}
    if(argc>1){std::string p=argv[1];wav(p+"/adjacent.wav",r,s);wav(p+"/nonadjacent.wav",rn,sn);wav(p+"/late-strength.wav",late,late0);}std::cout<<"checks="<<checks<<" adjacent_difference_energy="<<diff(r,s)<<" late_difference_energy="<<diff(late,late0)<<'\n';
}
