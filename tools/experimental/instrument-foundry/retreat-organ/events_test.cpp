#include "engine.hpp"
#include <chrono>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <vector>
using namespace mhac::organ;
void require(bool ok,const char* msg){if(!ok)throw std::runtime_error(msg);}
std::vector<double> manual(bool automatic,unsigned block){
    Engine e;e.set(Mode,automatic?1.:0.);e.set(Rate,0);e.set(Blend,0);require(e.reset(48000),"reset");
    std::vector<double> out(24000);for(unsigned start=0;start<out.size();start+=block){for(unsigned i=start;i<std::min<unsigned>(start+block,out.size());++i){
        if(i==17)require(e.noteOn(2,60,10,.8),"note on");
        if(i>=17&&!automatic){unsigned tick=std::min((i-17)/1200,14u);e.set(Dial,pathLevel(2,tick)/16.);}
        if(i==18000)e.set(Blend,1);
        if(i==21111)e.noteOff(2,60,10);
        out[i]=e.next();require(std::isfinite(out[i])&&std::abs(out[i])<=.5,"bounds");
    }}require(e.active()==0,"release");return out;
}
int main(){try{
    auto ref=manual(true,1);for(unsigned b:{1u,7u,64u,511u,1024u})require(ref==manual(false,b)&&ref==manual(true,b),"trajectory or block mismatch");
    Engine e;e.set(Mode,0);e.set(Dial,1);e.reset(48000);require(e.noteOn(0,60,42,1)&&e.noteOn(1,60,42,1),"notes");e.noteOff(0,60,42);for(int i=0;i<1100;++i)e.next();require(e.active()==1,"channel ID isolation");e.noteOff(1,60,42);for(int i=0;i<1100;++i)e.next();require(e.active()==0,"release");
    auto p=e.params();e.set(Gain,std::numeric_limits<double>::quiet_NaN());require(e.params()==p,"nonfinite automation");e.set(Gain,100);require(e.params()[Gain]==1,"gain clamp");
    e.reset(48000);for(int i=0;i<16;++i)require(e.noteOn(0,36+i,i,1),"benchmark note");double accum=0;auto t=std::chrono::steady_clock::now();for(int i=0;i<480000;++i)accum+=std::abs(e.next());auto elapsed=std::chrono::duration<double>(std::chrono::steady_clock::now()-t).count();require(accum>0&&std::isfinite(accum),"benchmark output");
    std::cout<<"manual/auto exact, 5 block partitions, note isolation, bounds PASS; 10 audio seconds/16 voices in "<<elapsed<<" s\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
