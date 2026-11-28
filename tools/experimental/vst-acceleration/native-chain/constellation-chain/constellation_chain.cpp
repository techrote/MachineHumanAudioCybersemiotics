// Refs #632; offline creative performance integration, not VST3 host validation.
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
void check(bool ok){if(!ok){std::cerr<<"CHAIN_FAIL\n";std::exit(1);}}
struct Mode {const char* name;unsigned budget;bool energy;unsigned stagger;};
constexpr Mode modes[]={{"persistent",0,false,1000},{"count",4,false,1000},{"energy",4,true,1000},{"full",16,true,1000},{"aligned",4,true,0}};
struct Result {std::vector<Frame> dry,bank,out;unsigned mask=0,cost=0;};
Result run(unsigned rate,unsigned block,Mode mode){
    const unsigned n=rate*5,close=rate,erase=2*rate,shift=rate*3;
    Result r; r.dry.resize(n);r.bank.resize(n);r.out.resize(n);
    o::host::Live synth; const o::Patch patch{180,650,-12,2,700,900,1400};
    check(synth.prepare(rate)&&synth.setPatch(patch));
    b::MemoryConfig c{};c.wet=1000;c.budget=mode.budget;c.energyFirst=mode.energy;
    for(unsigned k=0;k<4;++k){c.bands[k].gain=800;c.bands[k].peakMix=1000;c.bands[k].selectivity=0;}
    h::Host bank; b::HarmonicBank oracle;
    check(bank.request(c)&&bank.prepare(rate)&&oracle.set(c)&&oracle.prepare(rate));
    auto sh=std::make_unique<s::DesktopShuttle>();s::ShuttleHostPatch sp{{650,850,200,400,false},0};
    check(s::configureHost(*sh,sp)&&sh->prepareRate(rate));
    std::vector<double> l(block),rr(block),ol(block),orr(block);
    for(unsigned start=0;start<n;start+=block){
        const unsigned count=std::min(block,n-start);std::array<h::Event,6> events{};unsigned m=0;
        for(unsigned i=0;i<count;++i){const unsigned t=start+i;
            if(t==0)for(int k=0;k<4;++k)check(synth.on(k,0,45+k*7,0.,.8));
            if(t==rate*3/4)for(int k=0;k<4;++k)check(synth.off(k,0,45+k*7));
            if(t==shift)check(synth.on(4,0,69,0.,.7));
            if(t==shift+rate/2)check(synth.off(4,0,69));
            auto& d=r.dry[t];synth.tick(d.l,d.r);
            l[i]=std::clamp(d.l*8.,-.9,.9);rr[i]=std::clamp(d.r*8.,-.9,.9);
            if(t==close)for(unsigned k=0;k<4;++k)events[m++]={i,h::FirstBand+k*h::Stride+h::Excite,0};
            if(t==erase||t==erase+1)events[m++]={i,h::AdmitBudget,t==erase?1.:0.};
        }
        check(bank.process(l.data(),rr.data(),ol.data(),orr.data(),count,events.data(),m));
        for(unsigned i=0;i<count;++i){const unsigned t=start+i;
            if(t==close){for(auto& v:c.bands)v.excite=false;check(oracle.set(c));}
            if(t==erase){const auto p=b::beginBudgetedEscape(oracle,mode.budget,mode.energy?b::BudgetObjective::energy:b::BudgetObjective::count);r.mask=p.mask;r.cost=p.cost;check(p.cost<=mode.budget);}
            const auto x=oracle.process(l[i],rr[i]);check(x.left==ol[i]&&x.right==orr[i]);r.bank[t]={x.left,x.right};
            if(t==erase){check(s::applyHostNormalized(sp,5,mode.stagger/1000.)&&s::configureHost(*sh,sp));}
            const auto y=sh->process({float(x.left),float(x.right)});
            r.out[t]={.4*r.dry[t].l+.35*y.l,.4*r.dry[t].r+.35*y.r};
            for(double v:{x.left,x.right,r.out[t].l,r.out[t].r})check(std::isfinite(v)&&std::abs(v)<=1.);
            if(mode.budget==16&&t>=erase+rate/2)check(x.left==0&&x.right==0);
        }
    }
    check(synth.active()==0&&bank.save()==h::encode(c));return r;
}
void same(const std::vector<Frame>& a,const std::vector<Frame>& b){check(a.size()==b.size());for(unsigned i=0;i<a.size();++i)check(a[i].l==b[i].l&&a[i].r==b[i].r);}
void wav(const std::string& path,const std::vector<Frame>& a,unsigned rate){
    std::ofstream f(path,std::ios::binary);check(bool(f));auto put=[&](unsigned x,unsigned n){while(n--){f.put(char(x&255));x>>=8;}};
    f.write("RIFF",4);put(36+4*a.size(),4);f.write("WAVEfmt ",8);put(16,4);put(1,2);put(2,2);put(rate,4);put(rate*4,4);put(4,2);put(16,2);f.write("data",4);put(4*a.size(),4);
    for(unsigned i=0;i<a.size();++i){const double fade=std::min({1.,i/(rate*.01),(a.size()-1-i)/(rate*.05)});for(double x:{a[i].l,a[i].r})put(unsigned(int(std::lround(x*fade*32767))),2);}
    f.close();check(bool(f));
}
int main(int argc,char** argv){check(argc==1||argc==2);unsigned long long frames=0;
    for(unsigned rate:{44100u,48000u,96000u}){
        double persistent=0,full=0,aligned=0,staggered=0;
        for(const auto mode:modes){const auto a=run(rate,1,mode),b=run(rate,257,mode);same(a.dry,b.dry);same(a.bank,b.bank);same(a.out,b.out);check(a.mask==b.mask&&a.cost==b.cost);frames+=a.out.size();
            double rms=0,side=0,peak=0;for(unsigned i=rate*5/2;i<rate*3;++i){const auto x=a.out[i];rms+=x.l*x.l+x.r*x.r;side+=(x.l-x.r)*(x.l-x.r);peak=std::max({peak,std::abs(x.l),std::abs(x.r)});}
            rms=std::sqrt(rms/rate);side=std::sqrt(side/(2*rate));
            if(mode.budget==0)persistent=rms;
            if(mode.budget==16)full=rms;
            if(mode.budget==4&&mode.energy){if(mode.stagger)staggered=side;else aligned=side;}
            if(rate==48000&&argc==2){const std::string p=argv[1];wav(p+"/"+mode.name+".wav",a.out,rate);if(mode.budget==0)wav(p+"/orbit-dry.wav",a.dry,rate);}
            std::cout<<rate<<','<<mode.name<<",mask="<<a.mask<<",cost="<<a.cost<<",rms="<<rms<<",side="<<side<<",peak="<<peak<<'\n';
        }
        check(persistent>full&&persistent>1.e-5&&std::abs(aligned-staggered)>1.e-6);
    }
    std::cout<<"CHAIN_PASS paired_frames="<<frames<<"\n";
}
