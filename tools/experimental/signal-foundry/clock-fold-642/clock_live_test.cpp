#include "clock_live.hpp"
#include <cstdlib>
#include <iostream>
#include <memory>
using namespace mhac::clock_fold;
static unsigned checks=0;
static void require(bool ok){++checks;if(!ok){std::cerr<<"failure "<<checks<<'\n';std::exit(1);}}
int main(){
    auto owner=std::make_unique<Live>(); auto directOwner=std::make_unique<Engine>();
    auto& live=*owner; auto& direct=*directOwner;
    Normalized p{.92,.16,.25,.8,.12,0},q=defaults;
    auto bytes=encode(p);require(bytes.size()==60&&decode(bytes.data(),bytes.size(),q)&&q==p);
    require(!decode(bytes.data(),bytes.size()-1,q)&&q==p);
    auto bad=bytes;bad[0]='X';require(!decode(bad.data(),bad.size(),q)&&q==p);
    auto invalid=p;invalid[0]=std::numeric_limits<double>::quiet_NaN();bad=encode(invalid);
    require(!decode(bad.data(),bad.size(),q)&&q==p);
    require(!live.restore(invalid)&&live.params()==defaults);
    require(!live.set(Count,0)&&!live.set(Wet,-1)&&!live.set(Wet,2)&&!live.set(Wet,invalid[0]));
    for(double rate:{1000.,1234.568,44100.,48000.,96000.,192000.,1234567.8,2000000.}){
        require(live.prepare(rate)&&direct.prepare(rate));require(live.restore(p));q=p;
        for(std::size_t i=0;i<5*frameSize;++i){
            if(i%31==0){unsigned id=unsigned((i/31)%Quality);double v=double((i/31)%17)/16;
                q[id]=v;require(live.set(id,v));}
            const double x=.6*std::sin(double(i)*.03),y=.3*std::cos(double(i)*.011);
            auto a=live.step(x,y),b=direct.tick({x,y},controls(q));require(a==b);
        }
        require(live.restore(defaults));
        for(std::size_t i=0;i<3*frameSize;++i){auto a=live.step(i==0?.25:0,0);require(a[0]==(i==frameSize?.25:0)&&a[1]==0);}
    }
    require(!live.prepare(0));require(live.params()==defaults);
    std::cout<<checks<<" live/state assertions passed\n";
}
