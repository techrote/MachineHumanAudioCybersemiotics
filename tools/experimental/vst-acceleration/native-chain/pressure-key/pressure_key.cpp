// Refs #632, #738, #748: creative native performance, not VST3 qualification.
#include "host.hpp"
#include "bank_host.hpp"
#include "shuttle_host_state.hpp"
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <memory>
#include <vector>
namespace o=mhac::orbit;
namespace b=mhac::counterfactual;
namespace h=b::bankhost;
namespace s=mhac::accel;
struct Frame { double l=0,r=0; };
void check(bool ok){if(!ok){std::cerr<<"PRESSURE_KEY_FAIL\n";std::exit(1);}}
struct Mode {const char* name;bool pressure,key;unsigned budget;};
constexpr Mode modes[]={{"baseline",false,false,4},{"pressure",true,false,4},{"keyed",true,true,4},{"full",true,true,16}};
struct Result {std::vector<Frame> dry,bank,out,key;};
bool onset(unsigned t,unsigned rate){return t==rate*3/2||t==rate*2||t==rate*5/2;}
bool pulse(unsigned t,unsigned rate){for(unsigned a:{rate*3/2,rate*153/100,rate*2,rate*5/2})if(t>=a&&t<a+rate/100)return true;return false;}
Result run(unsigned rate,unsigned block,Mode mode,bool manual){
    Result r;const unsigned n=rate*5;r.dry.resize(n);r.bank.resize(n);r.out.resize(n);r.key.resize(n);
    o::host::Live synth;check(synth.prepare(rate)&&synth.setPatch({180,650,-12,2,700,900,1400}));
    b::MemoryConfig c{};c.wet=1000;c.budget=mode.budget;c.energyFirst=true;
    for(auto& band:c.bands){band.gain=800;band.peakMix=1000;band.selectivity=0;}
    h::Host bank;check(bank.request(c)&&bank.prepare(rate));
    auto sh=std::make_unique<s::DesktopShuttle>();s::ShuttleHostPatch sp{{650,850,200,400,false},1000};
    check(s::configureHost(*sh,sp)&&sh->prepareRate(rate));
    std::vector<double> l(block),rr(block),ol(block),orr(block),key(block);
    for(unsigned start=0;start<n;start+=block){
        const unsigned count=std::min(block,n-start);std::array<h::Event,32> events{};unsigned m=0;
        for(unsigned i=0;i<count;++i){const unsigned t=start+i;
            if(t==0)for(int k=0;k<4;++k)check(synth.on(k,0,45+k*7,0.,.8));
            if(mode.pressure&&t==rate/4)check(synth.pressure(0,0,45,1.));
            if(mode.pressure&&t==rate/2)check(synth.pressure(2,0,59,.8));
            if(t==rate*3/4)for(int k=0;k<4;++k)check(synth.off(k,0,45+k*7));
            if(t==rate*3)check(synth.on(4,0,69,0.,.7));
            if(mode.pressure&&t==rate*13/4)check(synth.pressure(4,0,69,1.));
            if(t==rate*7/2)check(synth.off(4,0,69));
            auto& d=r.dry[t];synth.tick(d.l,d.r);
            l[i]=std::clamp(d.l*8.,-.9,.9);rr[i]=std::clamp(d.r*8.,-.9,.9);
            key[i]=pulse(t,rate)?-.8:0.;r.key[t]={0.,key[i]};
            if(t==rate)for(unsigned k=0;k<4;++k)events[m++]={i,h::FirstBand+k*h::Stride+h::Excite,0.};
            if(manual&&mode.key&&(onset(t,rate)||(t&&onset(t-1,rate))))events[m++]={i,h::AdmitBudget,onset(t,rate)?1.:0.};
        }
        check(bank.processOptional(l.data(),rr.data(),ol.data(),orr.data(),count,events.data(),m,mode.key&&!manual,static_cast<const double*>(nullptr),key.data()));
        for(unsigned i=0;i<count;++i){const unsigned t=start+i;r.bank[t]={ol[i],orr[i]};
            const auto y=sh->process({float(ol[i]),float(orr[i])});
            r.out[t]={.4*r.dry[t].l+.35*y.l,.4*r.dry[t].r+.35*y.r};
            for(double v:{ol[i],orr[i],r.out[t].l,r.out[t].r})check(std::isfinite(v)&&std::abs(v)<=1.);
            if(mode.key&&mode.budget==16&&t>=rate*2)check(ol[i]==0&&orr[i]==0);
        }
    }
    for(auto& band:c.bands)band.excite=false;
    check(synth.active()==0&&bank.save()==h::encode(c));return r;
}
void same(const std::vector<Frame>& a,const std::vector<Frame>& b){check(a.size()==b.size());for(unsigned i=0;i<a.size();++i)check(a[i].l==b[i].l&&a[i].r==b[i].r);}
double rms(const std::vector<Frame>& a,unsigned start,unsigned end){double sum=0;for(unsigned i=start;i<end;++i)sum+=a[i].l*a[i].l+a[i].r*a[i].r;return std::sqrt(sum/(2*(end-start)));}
void wav(const std::string& path,const std::vector<Frame>& a,unsigned rate){
    std::ofstream f(path,std::ios::binary);check(bool(f));auto put=[&](unsigned x,unsigned n){while(n--){f.put(char(x&255));x>>=8;}};
    f.write("RIFF",4);put(36+4*a.size(),4);f.write("WAVEfmt ",8);put(16,4);put(1,2);put(2,2);put(rate,4);put(rate*4,4);put(4,2);put(16,2);f.write("data",4);put(4*a.size(),4);
    for(unsigned i=0;i<a.size();++i){const double fade=std::min({1.,i/(rate*.01),(a.size()-1-i)/(rate*.05)});for(double x:{a[i].l,a[i].r})put(unsigned(int(std::lround(x*fade*32767))),2);}
    f.close();check(bool(f));
}
int main(int argc,char** argv){check(argc==1||argc==2);unsigned long long frames=0;
    for(unsigned rate:{44100u,48000u,96000u}){
        double base=0,press=0,unkeyed=0,keyed=0;
        for(const auto mode:modes){const auto a=run(rate,1,mode,false),b=run(rate,257,mode,false),c=run(rate,1024,mode,true);
            same(a.dry,b.dry);same(a.bank,b.bank);same(a.out,b.out);same(a.dry,c.dry);same(a.bank,c.bank);same(a.out,c.out);frames+=2*a.out.size();
            const double attack=rms(a.dry,rate/4,rate*3/4),tail=rms(a.bank,rate*11/4,rate*3);
            if(!mode.pressure)base=attack;else if(!mode.key){press=attack;unkeyed=tail;}else if(mode.budget==4)keyed=tail;
            if(rate==48000&&argc==2){const std::string p=argv[1];wav(p+"/"+mode.name+".wav",a.out,rate);if(mode.pressure&&!mode.key){wav(p+"/dry-pressure.wav",a.dry,rate);wav(p+"/key.wav",a.key,rate);}}
            std::cout<<rate<<','<<mode.name<<",dry_rms="<<attack<<",bank_tail_rms="<<tail<<'\n';
        }
        check(std::abs(base-press)>1e-6&&unkeyed>1e-5&&std::abs(unkeyed-keyed)>1e-6);
    }
    std::cout<<"PRESSURE_KEY_PASS paired_frames="<<frames<<'\n';
}
