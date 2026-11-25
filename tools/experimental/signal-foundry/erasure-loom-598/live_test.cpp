#include "live.hpp"
#include <cstdlib>
#include <iostream>
using namespace loom;
void require(bool ok,const char* msg){if(!ok){std::cerr<<msg<<'\n';std::exit(1);}}
int main(){
    Live a,b; Normalized p{0,.25,.6,.9,.8,.7,0},q{};
    auto state=encode(p);require(decode(state.data(),state.size(),q)&&p==q,"state exact roundtrip");
    require(!decode(state.data(),state.size()-1,q)&&q==p,"short state atomic rejection");
    state[0]='X';require(!decode(state.data(),state.size(),q)&&q==p,"header rejection");
    auto bad=p;bad[2]=std::numeric_limits<double>::infinity();state=encode(bad);
    require(!decode(state.data(),state.size(),q)&&q==p&&!a.restore(bad),"nonfinite state rejection");
    bad=p;bad[3]=1.1;state=encode(bad);require(!decode(state.data(),state.size(),q)&&q==p,"range rejection");
    require(a.params()==defaults,"defaults unchanged");
    unsigned long long compared=0;
    for(double rate:{1234.568,8000.,44100.,48000.,96000.,192000.,1234567.8}){
        require(a.prepare(rate)&&b.prepare(rate),"prepare");a.restore(p);b.restore(p);a.reset();b.reset();
        Engine oracle;require(oracle.prepare(rate),"oracle prepare");oracle.set({1,2,10,.9,.8,.7,false});oracle.reset();
        for(unsigned i=0;i<frames*4;++i){double x=.1*std::sin(i*.13);auto y=a.step(x,-x),z=oracle.step(x,-x);require(std::abs(y[0]-z[0])<1e-14&&std::abs(y[1]-z[1])<1e-14,"normalized mapping");}
        a.reset();b.reset();unsigned index=0;
        for(unsigned block:{1u,17u,64u,511u,3u,144u,1024u})for(unsigned j=0;j<block;++j,++index){
            if(index%37==0){unsigned k=(index/37)%Count;double v=(index%19)/18.;a.set(k,v);b.set(k,v);}
            float x=float(.3*std::sin(index*.041));auto y=a.step(x,0),z=b.step(double(x),0);require(y==z&&y[1]==0,"block/format/channel comparison");++compared;
        }
        for(unsigned i=0;i<Engine::tail;++i)a.step(0,0);
        require(a.step(0,0)==Stereo{},"finite tail");
        a.set(Bypass,1);a.reset();for(unsigned i=0;i<frames*2;++i){auto y=a.step(i==0?.25:0,0);require(y[0]==(i==frames?.25:0)&&y[1]==0,"bypass latency");}
        a.set(Wet,std::numeric_limits<double>::quiet_NaN());require(std::isfinite(a.params()[Wet]),"invalid automation");
    }
    std::cout<<"paired_frames="<<compared<<" rates=7 EL01_bytes="<<State{}.size()<<'\n';
}
