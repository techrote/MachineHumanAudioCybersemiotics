// Refs #622: original note-scoped quotation/adoption score, no plugin ABI changes.
#include "borrowed_score.hpp"
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
namespace {
using namespace borrowed;
void validate(int rate,const std::vector<Frame>& mixed,const std::vector<Frame>& baseline){
    const auto ev=events(rate);std::array<Engine,score.size()> isolated;for(auto& e:isolated)check(e.prepare(rate),"isolated prepare");std::size_t next=0;double error=0;std::array<double,score.size()> energy{};
    for(unsigned s=0;s<mixed.size();++s){
        while(next<ev.size()&&ev[next].at==int(s)){const auto v=ev[next++];admit(isolated[v.note],v);}
        Frame sum{};for(unsigned i=0;i<score.size();++i){const auto a=isolated[i].tick();sum.left+=a.left;sum.right+=a.right;sum.base+=a.base;sum.counter+=a.counter;energy[i]+=a.counter*a.counter;
            const int opening=sample(score[i].on,rate)+4*int(std::lround(rate/double(score[i].speed)));
            if(int(s)<opening||score[i].mode==0)check(a.counter==0,"local quotation/cycle boundary");}
        const auto a=mixed[s],b=baseline[s];check(a.left==b.left&&a.base==b.base&&b.counter==0&&b.right==b.left,"base/citation preservation");
        check(a.left==a.base&&a.right==a.base+a.counter,"stem reconstruction");
        for(double x:{a.left,a.right,a.base,a.counter})check(std::isfinite(x)&&std::abs(x)<=.52,"safe bound");
        error=std::max({error,std::abs(a.left-sum.left),std::abs(a.right-sum.right),std::abs(a.base-sum.base),std::abs(a.counter-sum.counter)});
        if(s>=mixed.size()-std::size_t(rate/20))check(exact(a,Frame{})&&exact(b,Frame{}),"tail silence");
    }
    check(error<1e-12,"isolated sum");check(energy[0]==0,"non-adoption inherited");for(unsigned i=1;i<energy.size();++i)check(energy[i]>0,"missing adopted countervoice");
    std::cout<<"rate="<<rate<<" frames="<<mixed.size()<<" isolation_error="<<error<<" local_counter_energy=";for(double e:energy)std::cout<<e<<',';std::cout<<'\n';
}
void put(std::ostream& f,std::uint32_t v,int bytes,bool big=false){for(int i=0;i<bytes;++i)f.put(char(v>>(8*(big?bytes-1-i:i))));}
void wav(const std::string& path,const std::vector<Frame>& frames,bool stems){
    std::ofstream f(path,std::ios::binary);check(bool(f),"wav open");const auto bytes=std::uint32_t(frames.size()*4);
    f.write("RIFF",4);put(f,36+bytes,4);f.write("WAVEfmt ",8);put(f,16,4);put(f,1,2);put(f,2,2);put(f,48000,4);put(f,192000,4);put(f,4,2);put(f,16,2);f.write("data",4);put(f,bytes,4);
    for(const auto a:frames)for(double x:{stems?a.base:a.left,stems?a.counter:a.right})put(f,std::uint16_t(std::int16_t(std::lround(x*32767))),2);
    check(bool(f),"wav write");
}
void vlq(std::vector<unsigned char>& v,unsigned n){unsigned a[4]{n&127};int i=0;while((n>>=7)!=0)a[++i]=(n&127)|128;while(i>=0)v.push_back(static_cast<unsigned char>(a[i--]));}
void midi(const std::string& path){
    std::vector<unsigned char> t{0,0xff,0x51,3,7,0xa1,0x20};int last=0;
    for(auto e:events(ticksPerSecond)){if(e.type==0)continue;const auto& n=score[e.note];vlq(t,unsigned(e.at-last));last=e.at;t.push_back(e.type==1?0x90:0x80);t.push_back(static_cast<unsigned char>(n.pitch));t.push_back(static_cast<unsigned char>(e.type==1?n.velocity:0));}
    vlq(t,unsigned(duration-last));t.insert(t.end(),{0xff,0x2f,0});std::ofstream f(path,std::ios::binary);check(bool(f),"midi open");f.write("MThd",4);put(f,6,4,true);put(f,0,2,true);put(f,1,2,true);put(f,ppq,2,true);f.write("MTrk",4);put(f,std::uint32_t(t.size()),4,true);f.write(reinterpret_cast<const char*>(t.data()),std::streamsize(t.size()));check(bool(f),"midi write");
}
void csv(const std::string& path,bool baseline){std::ofstream f(path);check(bool(f),"csv open");f<<"tick,seconds,param_id,normalized,note,mode\n"<<std::setprecision(17);for(const auto& n:score){const auto p=params(n,baseline);for(unsigned i=0;i<p.size();++i)f<<n.on-24<<','<<double(n.on-24)/ticksPerSecond<<','<<1200+i<<','<<p[i]<<','<<n.pitch<<','<<(baseline?0:n.mode)<<'\n';}check(bool(f),"csv write");}
}
int main(int argc,char** argv){try{
    for(int rate:{44100,48000,96000}){auto a=render(rate,1),b=render(rate,257),c=render(rate,1024,false,true),d=render(rate,257,true);check(a.size()==b.size()&&a.size()==c.size(),"render length");for(unsigned i=0;i<a.size();++i)check(exact(a[i],b[i])&&exact(a[i],c[i]),"partition/citation invariance");validate(rate,a,d);if(rate==48000&&argc==2){const std::string dir=argv[1];wav(dir+"/mixed.wav",a,false);wav(dir+"/quotation.wav",d,false);wav(dir+"/stems.wav",a,true);midi(dir+"/borrowed-rooms.mid");csv(dir+"/mixed-automation.csv",false);csv(dir+"/quotation-automation.csv",true);}}
    std::cout<<"BORROWED_ROOMS_PASS\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
