// Refs #738. Offline automation score and independent voice-latch witness.
#include "host.hpp"
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <vector>
using namespace mhac::orbit;
namespace {
void require(bool x){if(!x)throw std::runtime_error("expressive performance regression");}
struct Note {unsigned on,off;int pitch;double velocity;Patch attack;unsigned mode,depth;};
constexpr Note score[]{
    {0,1800,48,.76,{180,650,-12,0,0,900,1400},2,700},
    {500,2300,55,.68,{700,900,0,0,0,1000,6000},1,250},
    {1000,2800,64,.82,{550,180,12,0,0,800,320},2,800},
    {2000,3400,69,.70,{350,500,-7,0,0,500,780},0,0}
};
constexpr Patch fixed{180,650,-12,2,700,0,1000};
struct Control {unsigned at,index;double value;};
std::vector<Control> controls(bool expressive){
    std::vector<Control> c;
    for(const auto& n:score){const auto p=expressive?n.attack:fixed;
        for(unsigned k=0;k<host::count;++k)c.push_back({n.on,k,host::normalized(p,k)});
        c.push_back({n.off,3,expressive?n.mode/2.:fixed.releaseMode/2.});
        c.push_back({n.off,4,expressive?n.depth/1000.:fixed.spectralDepth/1000.});}
    // Mid-note change: neither note admission nor release at this offset.
    if(expressive){c.push_back({750,5,0.});c.push_back({750,6,1.});}
    std::stable_sort(c.begin(),c.end(),[](auto a,auto b){return a.at<b.at||(a.at==b.at&&a.index<b.index);});return c;
}
using Frame=std::array<double,2>;
std::vector<Frame> render(unsigned rate,unsigned block,bool expressive){
    host::Live mix;require(mix.prepare(rate));std::array<host::Live,4> solo{};
    for(auto& v:solo)require(v.prepare(rate));
    auto c=controls(expressive);std::size_t next=0;const unsigned frames=5*rate;
    auto at=[&](unsigned ms){return unsigned(std::uint64_t(ms)*rate/1000);};
    std::vector<Frame> y(frames);double maxError=0.;
    for(unsigned base=0;base<frames;base+=block){const auto end=std::min(frames,base+block);
        for(unsigned i=base;i<end;++i){
            while(next<c.size()&&at(c[next].at)==i){require(mix.parameter(c[next].index,c[next].value));++next;}
            for(unsigned j=0;j<std::size(score);++j){const auto& n=score[j];
                if(i==at(n.on)){const Patch p=expressive?n.attack:fixed;require(host::pack(mix.patch())==host::pack(p));
                    require(solo[j].setPatch(p)&&solo[j].on(int(j),0,n.pitch,0.,n.velocity)&&mix.on(int(j),0,n.pitch,0.,n.velocity));}
                if(i==at(n.off)){auto p=expressive?n.attack:fixed;p.releaseMode=expressive?n.mode:fixed.releaseMode;p.spectralDepth=expressive?n.depth:fixed.spectralDepth;
                    require(solo[j].setPatch(p)&&solo[j].off(int(j),0,n.pitch)&&mix.off(int(j),0,n.pitch));}
            }
            mix.tick(y[i][0],y[i][1]);Frame ref{};
            for(auto& v:solo){double l=0,r=0;v.tick(l,r);ref[0]+=l;ref[1]+=r;}
            for(unsigned k=0;k<2;++k){const double s=y[i][k];require(std::isfinite(s)&&std::abs(s)<=.52);maxError=std::max(maxError,std::abs(s-ref[k]));if(i>=frames-rate/10)require(s==0.);}
        }
    }
    require(next==c.size()&&mix.active()==0&&maxError<=1e-14);for(auto& v:solo)require(v.active()==0);
    std::cout<<rate<<" block="<<block<<" expressive="<<expressive<<" oracle_error="<<maxError<<'\n';return y;
}
void le(std::ofstream& f,unsigned n,unsigned bytes){while(bytes--){f.put(char(n&255u));n>>=8;}}
void wav(const std::filesystem::path& path,const std::vector<Frame>& y){
    std::ofstream f(path,std::ios::binary);require(bool(f));const auto n=unsigned(y.size()*4);
    f.write("RIFF",4);le(f,36+n,4);f.write("WAVEfmt ",8);le(f,16,4);le(f,1,2);le(f,2,2);le(f,48000,4);le(f,192000,4);le(f,4,2);le(f,16,2);f.write("data",4);le(f,n,4);
    for(auto v:y)for(double s:v)le(f,unsigned(int(std::lround(s*32767))),2);
    f.close();require(bool(f));
}
void csv(const std::filesystem::path& dir,bool expressive){
    const std::string name=expressive?"expressive":"fixed";
    std::ofstream a(dir/(name+"-automation.csv"));require(bool(a));a<<"ms,sample_48000,param_id,normalized\n"<<std::setprecision(17);
    for(auto c:controls(expressive))a<<c.at<<','<<c.at*48<<','<<host::firstID+c.index<<','<<c.value<<'\n';
    a.close();require(bool(a));
}
}
int main(int argc,char** argv){try{
    require(argc==1||argc==2);std::uint64_t paired=0;
    for(unsigned rate:{44100u,48000u,96000u}){
        auto a=render(rate,1,true),b=render(rate,257,true),c=render(rate,1,false),d=render(rate,257,false);
        require(a==b&&c==d&&a!=c);paired+=a.size()+c.size();
        if(argc==2&&rate==48000){const std::filesystem::path dir=argv[1];std::filesystem::create_directories(dir);wav(dir/"expressive.wav",a);wav(dir/"fixed.wav",c);csv(dir,true);csv(dir,false);
            std::ofstream f(dir/"notes.csv");f<<"id,pitch,velocity,on_ms,off_ms\n"<<std::setprecision(17);for(unsigned j=0;j<std::size(score);++j){auto n=score[j];f<<j<<','<<n.pitch<<','<<n.velocity<<','<<n.on<<','<<n.off<<'\n';}f.close();require(bool(f));}
    }
    std::cout<<"EXPRESSIVE_PASS paired_frames="<<paired<<'\n';return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
