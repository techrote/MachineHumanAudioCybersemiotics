#include "integrated.hpp"
#include <iostream>
#include <cstdlib>
#include <limits>
#define CHECK(x) do {if(!(x)){std::cerr<<__LINE__<<": "<<#x<<'\n';std::exit(1);}}while(false)
using namespace winters;
int main(){
    using namespace integrated;
    auto old=live::defaults;old[6]=1;old[7]=.4;old[8]=.75;auto bytes=live::encode(old);Params p{};CHECK(decode(bytes.data(),bytes.size(),p));
    for(unsigned i=11;i<19;++i)CHECK(p[i]==defaults[i]);
    for(double sr:{1000.,8000.,44100.,48000.,96000.,192000.,2000000.}){
        integrated::Engine e;live::Engine ref;CHECK(e.prepare(sr)&&ref.prepare(sr));e.restore(p);live::Params migrated{};std::copy_n(p.begin(),live::Count,migrated.begin());ref.restore(migrated);
        for(int n=0;n<4;++n){CHECK(e.on(n,48+n*7,0,.7));CHECK(ref.on(n,48+n*7,0,.7));}
        for(int i=0;i<4096;++i){if(i%257==0){e.parameter(5,0);ref.parameter(5,0);e.parameter(5,1);ref.parameter(5,1);}auto a=e.tick(),b=ref.tick();CHECK(a.l==b.l&&a.r==b.r&&a.primary==b.primary&&a.middle==b.middle&&a.deep==b.deep);}
        e.reset();e.parameter(11,.2);e.parameter(12,.6);e.parameter(13,.8);e.parameter(14,1);e.parameter(15,1);e.parameter(12,.4);e.parameter(16,1);e.parameter(16,1);
        CHECK((e.targets()==std::array<double,3>{.2,.2,.6}));e.parameter(15,0);CHECK((e.targets()==std::array<double,3>{.4,.2,.4}));
        e.parameter(17,1);e.parameter(18,1);for(int i=0;i<int(sr/8);++i)e.tick();CHECK(e.targets()[0]==.4);e.tick();if(std::floor(sr/8)==sr/8)CHECK(e.targets()[0]==.8);else {e.tick();CHECK(e.targets()[0]==.8);}
        e.parameter(11,std::numeric_limits<double>::quiet_NaN());CHECK(e.parameters()[11]==.2);
        auto saved=encode(e.parameters());Params restored{};CHECK(decode(saved.data(),saved.size(),restored));CHECK(restored[15]==0&&restored[16]==0&&restored[17]==1);CHECK(std::abs(restored[12]-.4)<1e-7);CHECK(!decode(saved.data(),saved.size()-1,restored));saved[3]='9';CHECK(!decode(saved.data(),saved.size(),restored));
        e.restore(restored);for(int n=0;n<4;++n)CHECK(e.on(n,60+n,0,1));for(int i=0;i<int(sr*.01)+1;++i){auto f=e.tick();CHECK(std::isfinite(f.l)&&std::abs(f.l)<=.3000001&&std::abs(f.r)<=.3000001);}
        for(int n=0;n<4;++n){e.off(n);}for(int i=0;i<int(sr*.041)+2;++i)e.tick();auto f=e.tick();CHECK(f.l==0&&f.r==0&&f.primary==0&&f.middle==0&&f.deep==0);
    }
    std::cout<<"TW01/TW02; 28672 exact legacy frames; seven rates; independent clock and trigger; release silence PASS\n";
}
