#include "bank_host.hpp"
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <string>
using namespace mhac::counterfactual;
namespace bh=mhac::counterfactual::bankhost;
namespace {
constexpr unsigned rate=48000, frames=rate*3, closeAt=rate/4, admitAt=rate/2;
constexpr char cid[]="AE00577BADF94D9C8F2FB9D04991475C";
using Preset=std::array<std::uint8_t,121>;
void require(bool ok){if(!ok){std::cerr<<"BANK_PERFORMANCE_FAIL\n";std::exit(1);}}
Preset wrap(const MemoryConfig& c){
    Preset b{};std::copy_n("VST3",4,b.begin());b[4]=1;
    std::copy_n(cid,32,b.begin()+8);b[40]=93;
    const auto s=bh::encode(c);std::copy(s.begin(),s.end(),b.begin()+48);
    std::copy_n("List",4,b.begin()+93);b[97]=1;
    std::copy_n("Comp",4,b.begin()+101);b[105]=48;b[113]=45;return b;
}
bool unwrap(const Preset& b,MemoryConfig& c){
    const auto expected=wrap(MemoryConfig{});
    for(unsigned i=0;i<b.size();++i)if((i<48||i>=93)&&b[i]!=expected[i])return false;
    return bh::decode(b.data()+48,45,c);
}
struct Entry{const char* name;unsigned budget;bool energy;};
constexpr Entry bank[]={{"01 Persistent Quartet",0,false},{"02 Count Cut",4,false},
    {"03 Energy Cut",4,true},{"04 Half Budget",8,true},{"05 Full Erasure",16,true}};
MemoryConfig config(Entry e){
    MemoryConfig c{};c.wet=1000;c.budget=e.budget;c.energyFirst=e.energy;
    for(unsigned k=0;k<4;++k){auto& b=c.bands[k];b.peakMix=1000;b.gain=800;b.selectivity=static_cast<std::uint16_t>((177+k*271)%1001);}
    return c;
}
void word(std::ostream& f,unsigned v,unsigned n){for(unsigned i=0;i<n;++i)f.put(static_cast<char>((v>>(8*i))&255));}
void header(std::ostream& f){f.write("RIFF",4);word(f,36+frames*4,4);f.write("WAVEfmt ",8);word(f,16,4);word(f,1,2);word(f,2,2);word(f,rate,4);word(f,rate*4,4);word(f,4,2);word(f,16,2);f.write("data",4);word(f,frames*4,4);}
// A fixed excitation fixture; identical input and sample offsets for every preset.
Stereo input(unsigned t){
    constexpr double tau=6.283185307179586;
    const auto pcm=[](double x){return std::round(x*32768)/32768;};
    return t<closeAt?Stereo{pcm(.85*std::sin(tau*117*t/rate)),pcm(-.55*std::sin(tau*168*t/rate))}:Stereo{};
}
void render(Entry e,const std::string& dir){
    const auto c=config(e);const auto preset=wrap(c);MemoryConfig decoded{};
    require(unwrap(preset,decoded)&&bh::encode(decoded)==bh::encode(c));
    bh::Host a,b;HarmonicBank reference;
    require(a.request(c)&&b.request(decoded)&&a.prepare(rate)&&b.prepare(rate)&&reference.set(c)&&reference.prepare(rate));
    auto active=c;BudgetPlan plan{};std::ofstream wav;
    if(!dir.empty()){
        std::ofstream p(dir+"/Presets/"+e.name+".vstpreset",std::ios::binary);
        p.write(reinterpret_cast<const char*>(preset.data()),static_cast<std::streamsize>(preset.size()));p.close();require(bool(p));
        wav.open(dir+"/Audio/"+e.name+".wav",std::ios::binary);require(bool(wav));header(wav);
    }
    std::array<double,257> l{},r{},ol{},orr{};double peak=0,tail=0;unsigned checks=0;
    for(unsigned start=0;start<frames;){
        const unsigned n=std::min(257u,frames-start);std::array<bh::Event,6> events{};unsigned m=0;
        for(unsigned i=0;i<n;++i){const unsigned t=start+i;const auto x=input(t);l[i]=x.left;r[i]=x.right;
            if(t==closeAt)for(unsigned k=0;k<4;++k)events[m++]={i,bh::FirstBand+k*bh::Stride+bh::Excite,0};
            if(t==admitAt||t==admitAt+1)events[m++]={i,bh::AdmitBudget,t==admitAt?1.:0.};}
        require(a.process(l.data(),r.data(),ol.data(),orr.data(),n,events.data(),m));
        for(unsigned i=0;i<n;++i){const unsigned t=start+i;std::array<bh::Event,6> single{};unsigned count=0;
            for(unsigned k=0;k<m;++k)if(events[k].offset==i){single[count]=events[k];single[count++].offset=0;}
            double bl=0,br=0;require(b.process(&l[i],&r[i],&bl,&br,1,single.data(),count));
            if(t==closeAt){for(auto& band:active.bands)band.excite=false;require(reference.set(active));}
            if(t==admitAt){plan=beginBudgetedEscape(reference,c.budget,c.energyFirst?BudgetObjective::energy:BudgetObjective::count);require(plan.cost<=c.budget);}
            const auto ref=reference.process(l[i],r[i]);require(bl==ol[i]&&br==orr[i]&&bl==ref.left&&br==ref.right);++checks;
            const double fade=std::min({1.,double(t)/480.,double(frames-1-t)/2400.});
            for(double v:{bl,br}){require(std::isfinite(v)&&std::abs(v)<=1);if(t>=frames-2400)tail+=v*v;
                const double y=v*.5*fade;peak=std::max(peak,std::abs(y));if(wav.is_open())word(wav,unsigned(int(std::round(y*32767))),2);}
        }start+=n;
    }
    require(a.save()==bh::encode(active)&&b.save()==bh::encode(active));
    if(e.budget==4)require(plan.mask==(e.energy?2u:12u));
    require((e.budget==16&&plan.count==4&&tail==0)||(e.budget<16&&plan.count<4&&tail>0));
    if(wav.is_open()){wav.close();require(bool(wav));}
    std::cout<<e.name<<",mask="<<plan.mask<<",cost="<<plan.cost<<",energy="<<plan.energy<<",peak="<<peak<<",tail="<<tail<<",frames="<<checks<<'\n';
}
}
int main(int argc,char** argv){
    require(argc==1||argc==2);const std::string dir=argc==2?argv[1]:"";
    unsigned tests=0;
    for(unsigned budget=0;budget<=16;++budget)for(bool energy:{false,true}){
        auto c=config({"",budget,energy});MemoryConfig d{};require(unwrap(wrap(c),d)&&bh::encode(c)==bh::encode(d));++tests;}
    const auto p=wrap(config(bank[0]));
    for(unsigned i=0;i<p.size();++i)if(i<48||i>=93){auto bad=p;bad[i]^=1;MemoryConfig d{};require(!unwrap(bad,d));++tests;}
    for(unsigned i:{48u,49u,50u,51u,54u,91u,92u}){auto bad=p;bad[i]=255;MemoryConfig d{};require(!unwrap(bad,d));++tests;}
    for(const auto& e:bank)render(e,dir);
    if(!dir.empty()){
        std::ofstream a(dir+"/automation.csv");a<<"sample,param_id,normalized\n";
        for(unsigned k=0;k<4;++k)a<<closeAt<<','<<bh::FirstBand+k*bh::Stride+bh::Excite<<",0\n";
        a<<admitAt<<','<<bh::AdmitBudget<<",1\n"<<admitAt+1<<','<<bh::AdmitBudget<<",0\n";a.close();require(bool(a));
        std::ofstream source(dir+"/Excitation.wav",std::ios::binary);header(source);
        for(unsigned t=0;t<frames;++t){const auto s=input(t);for(double x:{s.left,s.right})word(source,unsigned(int(std::round(x*32768))),2);}source.close();require(bool(source));
    }
    std::cout<<"BANK_PERFORMANCE_PASS presets=5 structural_checks="<<tests<<'\n';
}
