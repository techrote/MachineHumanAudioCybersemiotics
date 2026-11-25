#include "trajectory.hpp"
#include <fstream>
#include <iostream>
#include <string>
using namespace mhac::organ;
void require(bool x,const char* m){if(!x)throw std::runtime_error(m);}
void le(std::ostream& o,unsigned x,unsigned n){for(unsigned i=0;i<n;++i)o.put(char((x>>(8*i))&255));}
void wav(const std::string& name,const std::vector<double>& a,const std::vector<double>& b){
    require(a.size()==b.size(),"stereo length");std::ofstream o(name,std::ios::binary);unsigned n=unsigned(a.size()*4);
    o.write("RIFF",4);le(o,36+n,4);o.write("WAVEfmt ",8);le(o,16,4);le(o,1,2);le(o,2,2);le(o,48000,4);le(o,192000,4);le(o,4,2);le(o,16,2);o.write("data",4);le(o,n,4);
    for(unsigned i=0;i<a.size();++i){le(o,unsigned(std::lround(a[i]*32767)),2);le(o,unsigned(std::lround(b[i]*32767)),2);}o.close();require(bool(o),"write WAV");
}
std::vector<double> render(const std::vector<unsigned>& path,double blend,unsigned block){
    Engine e;e.set(Mode,0);e.set(Dial,0);e.set(Blend,blend);e.set(Gain,1);require(e.reset(48000),"reset");
    std::vector<double> y(96000);for(unsigned start=0;start<y.size();start+=block)for(unsigned i=start;i<std::min<unsigned>(start+block,y.size());++i){
        if(i==0)for(int k:{48,55,60,64})require(e.noteOn(0,k,k,.9),"admit");
        if(i%2400==0)e.set(Dial,path[std::min<unsigned>(i/2400,unsigned(path.size()-1))]/16.);
        if(i==86400)for(int k:{48,55,60,64})e.noteOff(0,k,k);
        y[i]=e.next();require(std::isfinite(y[i])&&std::abs(y[i])<=.5,"bounds");
    }require(e.active()==0&&y.back()==0,"release");return y;
}
int main(int argc,char** argv){try{
    require(argc==1||(argc==2&&std::string(argv[1])=="--render"),"usage: organ_trajectory [--render]");
    TrajectoryCompiler c;require(c.reachable()==4188,"reachable census");
    const int upper[17]={0,1,2,3,4,5,6,7,7,6,5,4,3,2,1,0,0};
    const unsigned depth[17]={0,2,4,6,8,10,12,14,15,13,11,9,7,5,3,1,1};
    unsigned targets=0;std::ofstream csv;if(argc==2){csv.open("trajectory-atlas.csv");csv<<"final_level,signed_relay_difference,transitions,levels\n";}
    for(unsigned x=0;x<17;++x){
        const int lower=x>=8&&x<=15?-1:0;
        for(int d=-8;d<=8;++d){auto p=c.shortest(x,d);require(p.empty()==(d<lower||d>upper[x]),"target reachability");if(p.empty())continue;++targets;
            require(p.front()==0&&p.back()==x,"endpoints");Relays r;for(auto v:p)r.visit(v);require(int(Relays::count(r.a))-int(Relays::count(r.b))==d,"replay");
            if(d==upper[x])require(p.size()==depth[x]+1,"minimum upper path");
            if(csv){csv<<x<<','<<d<<','<<p.size()-1<<',';for(auto v:p)csv<<v<<' ';csv<<'\n';}
        }
    }
    if(argc==2){csv.close();require(bool(csv),"write atlas");}
    bool rejected=false;try{c.shortest(17,0);}catch(const std::out_of_range&){rejected=true;}require(rejected,"invalid target");
    const auto rich=c.shortest(7,7),plain=c.shortest(7,0);auto a=render(rich,0,1),b=render(plain,0,511),z=render(rich,1,64);
    require(a==render(rich,0,1024),"partition invariance");require(b==render(plain,1,7),"zero-bank witness");
    // Identical final dial, different histories, same chord and gain.
    double diff=0,control=0;for(unsigned i=48000;i<80000;++i){diff+=(a[i]-b[i])*(a[i]-b[i]);control+=(z[i]-b[i])*(z[i]-b[i]);}
    require(diff>0.01&&control==0,"history contrast / negative control");
    if(argc==2){wav("history-contrast.wav",a,b);wav("bank-control.wav",z,b);std::ofstream f("dial-automation.csv");f<<"seconds,rich_normalized,plain_normalized\n";for(unsigned i=0;i<rich.size();++i)f<<i*.05<<','<<rich[i]/16.<<','<<plain[std::min<unsigned>(i,unsigned(plain.size()-1))]/16.<<'\n';f.close();require(bool(f),"write automation");}
    std::cout<<c.reachable()<<" reachable states; "<<targets<<" endpoint/difference targets; rich vs plain squared difference "<<diff<<"; negative control "<<control<<" PASS\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
