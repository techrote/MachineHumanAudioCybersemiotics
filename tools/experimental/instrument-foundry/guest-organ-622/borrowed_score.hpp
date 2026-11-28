#pragma once
#include "control.hpp"
#include <algorithm>
#include <array>
#include <cmath>
#include <stdexcept>
#include <vector>
namespace borrowed {
using guest::Frame;
using guest::control::Engine;
constexpr int ppq=480, ticksPerSecond=960, duration=7680;
struct Note {int on,off,pitch,velocity,mode; std::array<int,4> motif; int speed; double gain,depth;};
constexpr std::array<Note,6> score{{
    {120,4080,48,86,0,{0,7,3,10},4,.65,.5},
    {600,4320,55,83,1,{0,5,-2,9},5,.60,.5},
    {1080,4560,60,76,2,{0,7,12,3},4,.70,.5},
    {1560,4800,64,72,3,{0,12,-5,7},8,.65,1.},
    {3240,6240,67,77,2,{0,-5,2,7},6,.70,.5},
    {4200,6720,72,69,3,{0,7,3,10},3,.55,.75}
}};
void check(bool b,const char* why){if(!b)throw std::runtime_error(why);}
using Params=guest::control::Params;
Params params(const Note& n,bool baseline=false,bool invertCitation=false){
    Params p{};for(unsigned i=0;i<4;++i)p[i]=(n.motif[i]+12)/24.;
    p[4]=(n.speed-1)/11.;p[5]=n.gain;p[6]=double((n.mode==0)!=invertCitation);
    p[7]=double(n.mode!=0&&!baseline);p[8]=double(n.mode==2);p[9]=double(n.mode==3);p[10]=n.depth;return p;
}
void setPatch(Engine& e,const Params& p){for(unsigned i=0;i<p.size();++i)e.parameter(i,p[i]);}
int sample(int tick,int rate){return int(std::llround(double(tick)*rate/ticksPerSecond));}
bool exact(Frame a,Frame b){return a.left==b.left&&a.right==b.right&&a.base==b.base&&a.counter==b.counter;}
struct Event {int at;unsigned note;int type;};
std::vector<Event> events(int rate){
    std::vector<Event> e;for(unsigned i=0;i<score.size();++i){const auto& n=score[i];e.push_back({sample(n.on-24,rate),i,0});e.push_back({sample(n.on,rate),i,1});e.push_back({sample(n.off,rate),i,2});}
    std::sort(e.begin(),e.end(),[](Event a,Event b){return a.at<b.at;});return e;
}
void admit(Engine& e,Event v,bool baseline=false,bool invert=false){
    const auto& n=score[v.note];const int id=int(v.note)+1;
    if(v.type==0)setPatch(e,params(n,baseline,invert));else if(v.type==1)check(e.on(id,n.pitch,0,n.velocity/127.),"note admission");else e.off(id);
}
std::vector<Frame> render(int rate,int block,bool baseline=false,bool invert=false){
    Engine e;check(e.prepare(rate),"prepare");const auto ev=events(rate);std::size_t next=0;const int end=sample(duration,rate);std::vector<Frame> out;out.reserve(std::size_t(end));
    for(int start=0;start<end;start+=block)for(int s=start;s<std::min(start+block,end);++s){while(next<ev.size()&&ev[next].at==s)admit(e,ev[next++],baseline,invert);out.push_back(e.tick());}
    check(next==ev.size(),"event consumption");return out;
}
}
