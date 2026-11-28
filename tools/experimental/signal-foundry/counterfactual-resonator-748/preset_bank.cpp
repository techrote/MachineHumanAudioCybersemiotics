#include "resonator.hpp"
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <string>
using namespace mhac::counterfactual;
namespace {
using Preset=std::array<std::uint8_t,88>;
constexpr char cid[]="FBC2EF81CA534C7A8B3BC61D9929C901";
unsigned checks=0;
void require(bool ok){++checks;if(!ok){std::cerr<<"FAIL preset "<<checks<<'\n';std::exit(1);}}
Preset wrap(Controls c){
    Preset b{};std::copy_n("VST3",4,b.begin());b[4]=1;
    std::copy_n(cid,32,b.begin()+8);b[40]=60;
    const auto patch=encode(c);std::copy(patch.begin(),patch.end(),b.begin()+48);
    std::copy_n("List",4,b.begin()+60);b[64]=1;
    std::copy_n("Comp",4,b.begin()+68);b[72]=48;b[80]=12;return b;
}
// Strict canonical component-only reader, not a general VST3 preset parser.
bool unwrap(const Preset& b,Controls& c){
    const auto expected=wrap(Controls{});
    for(unsigned i=0;i<b.size();++i)if((i<48||i>=60)&&b[i]!=expected[i])return false;
    Patch p{};std::copy_n(b.begin()+48,p.size(),p.begin());return decode(p,c);
}
struct Entry{const char* name;Controls c;};
constexpr Entry bank[]={
    {"01 Reference 250",{250,1000,800,0,false,false}},
    {"02 Persistent 250",{250,1000,800,1,false,false}},
    {"03 Residual 250",{250,1000,800,2,false,false}},
    {"04 Erase 250",{250,1000,800,1,true,false}},
    {"05 Low Memory",{110,600,600,1,false,false}},
    {"06 Octave Glint",{880,700,650,1,false,false}},
    {"07 Transient Spark",{6000,800,500,2,false,false}},
    {"08 Dry Reference",{250,1000,800,1,false,true}}
};
void word(std::ostream& f,unsigned v,unsigned n){for(unsigned i=0;i<n;++i)f.put(static_cast<char>((v>>(8*i))&255));}
void render(const Entry& e,const std::string& dir){
    const auto b=wrap(e.c);Controls c;require(unwrap(b,c)&&encode(c)==encode(e.c));
    Processor a,d;require(a.set(e.c)&&d.set(c)&&a.prepare(48000)&&d.prepare(48000));
    constexpr unsigned n=96000;constexpr double pi=3.14159265358979323846;
    std::ofstream wav;
    if(!dir.empty()){
        std::ofstream preset(dir+"/Presets/"+e.name+".vstpreset",std::ios::binary);
        preset.write(reinterpret_cast<const char*>(b.data()),static_cast<std::streamsize>(b.size()));preset.close();require(bool(preset));
        wav.open(dir+"/Audio/"+e.name+".wav",std::ios::binary);require(bool(wav));
        wav.write("RIFF",4);word(wav,36+n*4,4);wav.write("WAVEfmt ",8);word(wav,16,4);word(wav,1,2);word(wav,2,2);word(wav,48000,4);word(wav,192000,4);word(wav,4,2);word(wav,16,2);wav.write("data",4);word(wav,n*4,4);
    }
    double peak=0,energy=0,tail=0;
    for(unsigned i=0;i<n;++i){
        const double t=double(i)/48000.0;
        const double phase=2*pi*40*std::expm1(std::log(300.0)*2*t)/(2*std::log(300.0));
        const Stereo in=i<24000?Stereo{0.5*std::sin(phase),0.5*std::sin(phase+pi/2)}:Stereo{};
        const auto x=a.process(in.left,in.right),y=d.process(in.left,in.right);
        require(x.left==y.left&&x.right==y.right);
        if(c.bypass)require(x.left==in.left&&x.right==in.right);
        for(double v:{x.left,x.right}){
            require(std::isfinite(v)&&std::abs(v)<=1);peak=std::max(peak,std::abs(v));energy+=v*v;if(i>=n-2400)tail+=v*v;
            if(wav.is_open())word(wav,static_cast<std::uint16_t>(static_cast<std::int16_t>(std::lround(v*32767))),2);
        }
    }
    if(c.erase||c.monitor==0||c.bypass)require(tail==0);
    if(wav.is_open()){wav.close();require(bool(wav));}
    std::cout<<e.name<<",peak="<<peak<<",rms="<<std::sqrt(energy/(2*n))<<",tail50ms="<<std::sqrt(tail/4800)<<'\n';
}
}
int main(int argc,char** argv){
    require(argc==1||argc==2);
    for(unsigned hz:{40u,110u,250u,880u,6000u})for(unsigned wet:{0u,1u,500u,1000u})for(unsigned gain:{0u,1u,800u,1000u})for(unsigned monitor=0;monitor<3;++monitor)for(bool erase:{false,true})for(bool bypass:{false,true}){
        Controls c{static_cast<std::uint16_t>(hz),static_cast<std::uint16_t>(wet),static_cast<std::uint16_t>(gain),static_cast<std::uint8_t>(monitor),erase,bypass},d;
        require(unwrap(wrap(c),d)&&encode(c)==encode(d));
    }
    const auto b=wrap(bank[0].c);for(unsigned i=0;i<b.size();++i)if(i<48||i>=60)for(unsigned bit=0;bit<8;++bit){auto bad=b;bad[i]^=std::uint8_t(1u<<bit);Controls c=bank[1].c;require(!unwrap(bad,c)&&encode(c)==encode(bank[1].c));}
    for(unsigned i:{48u,49u,50u,51u,53u,55u,57u,58u,59u}){auto bad=b;bad[i]=255;Controls c=bank[1].c;require(!unwrap(bad,c)&&encode(c)==encode(bank[1].c));}
    for(const auto& e:bank)render(e,argc==2?argv[1]:"");
    std::cout<<"PASS "<<checks<<" checks\n";
}
