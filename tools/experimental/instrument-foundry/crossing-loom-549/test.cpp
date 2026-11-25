#include "params.hpp"
#include <iostream>
#include <vector>
#include <fstream>
#include <string>
#include <cstdlib>
#include <limits>
using namespace loom;
void require(bool x){if(!x){std::cerr<<"failure\n";std::exit(1);}}
void word(std::ofstream& o,unsigned v,int n){for(int i=0;i<n;++i)o.put(char((v>>(8*i))&255));}
void wav(const std::string& path,const std::vector<Pair>& x,bool mono){std::ofstream o(path,std::ios::binary);unsigned ch=mono?1:2,n=unsigned(x.size()*ch*2);o.write("RIFF",4);word(o,36+n,4);o.write("WAVEfmt ",8);word(o,16,4);word(o,1,2);word(o,ch,2);word(o,48000,4);word(o,48000*ch*2,4);word(o,ch*2,2);word(o,16,2);o.write("data",4);word(o,n,4);for(auto p:x){word(o,unsigned(std::lround((mono?(p.l+p.r)*.5:p.l)*32767)),2);if(!mono)word(o,unsigned(std::lround(p.r*32767)),2);}require(bool(o));}
int main(int argc,char** argv){
    Params prm=defaults;set(prm,0,.5);set(prm,3,.9);auto state=encode(prm);Params decoded{};require(decode(state,decoded)&&encode(decoded)==state);auto bad=state;bad[0]=0;require(!decode(bad,decoded)&&encode(decoded)==state);bad=state;bad[4]=0;bad[5]=0;bad[6]=128;bad[7]=127;require(!decode(bad,decoded));
    double maxMono=0, maxStereo=0; std::uint64_t checked=0;
    for(double rate:{8000.,44100.,48000.,96000.,192000.,384000.}){
        Engine a,b;require(a.prepare(rate)&&b.prepare(rate));Patch p; p.seconds=.025;p.spread=.6;
        require(a.on(1,57,13,.8,p));p.bounce=true;require(b.on(1,57,13,.8,p));auto half=std::llround(p.seconds*rate);
        for(int i=0;i<int(.15*rate);++i){if(i==int(.09*rate)){a.off(1);b.off(1);}auto x=a.tick(),y=b.tick();double err=std::abs((x.l+x.r)-(y.l+y.r));maxMono=std::max(maxMono,err);require(err==0);if(i<half)require(x.l==y.l&&x.r==y.r);else{require(x.l==y.r&&x.r==y.l);maxStereo=std::max(maxStereo,std::abs(x.l-y.l));}if(i>=int(.14*rate))require(x.l==0&&x.r==0);++checked;}
    }
    Engine a,b;require(!a.prepare(NAN));require(a.prepare(48000)&&b.prepare(48000));Patch p;p.spread=NAN;p.width=INFINITY;
    for(int i=0;i<8;++i){require(a.on(i,127,INFINITY,1,p));require(b.on(i,127,INFINITY,1,p));}require(!a.on(9,60,0,1,p));require(!a.on(0,60,0,1,p));
    std::array<double,1024> l{},r{},ll{},rr{};a.render(l.data(),r.data(),1024);for(int i=0;i<1024;i+=17)b.render(ll.data()+i,rr.data()+i,std::min(17,1024-i));require(l==ll&&r==rr);for(auto x:l)require(std::isfinite(x)&&std::abs(x)<=.4);a.reset();require(a.tick().l==0);std::array<float,10> f{};a.render(f.data(),static_cast<float*>(nullptr),10);for(auto x:f)require(x==0);
    Engine e1,e2;e1.prepare(48000);e2.prepare(48000);Patch w;w.seconds=.025;e1.on(1,69,0,1,w);e2.on(1,69,0,1,w);std::array<float,1201> fl{},fr{};e1.render(fl.data(),fr.data(),1201);for(int i=0;i<1201;++i){auto s=e2.tick();require(fl[i]==float(s.l)&&fr[i]==float(s.r));}require(std::abs(fl[1200]-fr[1200])<1e-7);
    require(maxStereo>.001);std::cout<<"checked frames="<<checked<<" max mono error="<<maxMono<<" max stereo delta="<<maxStereo<<"\n";
    if(argc>1){Engine c,d;c.prepare(48000);d.prepare(48000);Patch q;q.seconds=.5;q.spread=.35;c.on(1,69,0,1,q);q.bounce=true;d.on(1,69,0,1,q);std::vector<Pair> x,y;for(int i=0;i<72000;++i){if(i==60000){c.off(1);d.off(1);}x.push_back(c.tick());y.push_back(d.tick());}std::string dir=argv[1];wav(dir+"/cross.wav",x,false);wav(dir+"/bounce.wav",y,false);wav(dir+"/cross-mono.wav",x,true);wav(dir+"/bounce-mono.wav",y,true);}
}
