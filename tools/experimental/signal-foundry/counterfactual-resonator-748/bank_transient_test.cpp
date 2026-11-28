#include "bank_transient.hpp"
#include "bank_host.hpp"
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <limits>
#include <string>
using namespace mhac::counterfactual;
namespace bh=mhac::counterfactual::bankhost;
namespace {
void require(bool ok){if(!ok){std::cerr<<"BANK_TRANSIENT_FAIL\n";std::exit(1);}}
void word(std::ostream& f,unsigned v,unsigned n){for(unsigned i=0;i<n;++i)f.put(char((v>>(8*i))&255u));}
void header(std::ostream& f,unsigned rate){f.write("RIFF",4);word(f,36+rate*12,4);f.write("WAVEfmt ",8);word(f,16,4);word(f,1,2);word(f,2,2);word(f,rate,4);word(f,rate*4,4);word(f,4,2);word(f,16,2);f.write("data",4);word(f,rate*12,4);}
void sample(std::ostream& f,double x){word(f,unsigned(int(std::round(x*32767))),2);}
bool key(unsigned t,unsigned rate){
    // Second attack is inside refractory interval; third and fourth are valid.
    for(unsigned start:{rate/2,rate/2+rate*3/100,rate,rate*3/2})
        if(t>=start&&t<start+rate/100)return true;
    return false;
}
Stereo program(unsigned t,unsigned rate){
    const auto pcm=[](double x){return std::round(x*32768)/32768;};
    return t<rate/4?Stereo{pcm(.85*std::sin(6.283185307179586*117*t/rate)),pcm(-.55*std::sin(6.283185307179586*168*t/rate))}:Stereo{};
}
bool expected(unsigned t,unsigned rate){return t==rate/2||t==rate||t==rate*3/2;}
void gateTests(unsigned rate){
    TransientGate g;require(g.prepare(rate));require(!g.prepare(rate,.1,.2));
    require(!g.prepare(std::numeric_limits<double>::infinity()));
    require(!g.observe(std::numeric_limits<double>::quiet_NaN(),0));
    require(g.observe(0,-.8));
    for(unsigned i=0;i<rate;++i)require(!g.observe(.8,0));
    for(unsigned i=0;i<rate/10;++i)require(!g.observe(0,0));
    require(g.observe(.8,0));g.reset();require(g.observe(.8,0));
    g.reset();for(unsigned t=0;t<rate*3;++t)require(g.observe(0,key(t,rate)?-26214.0/32768:0)==expected(t,rate));
}
// Compare automatic key routing against explicit sample-offset commands, using
// both one-sample and irregular blocks. The inactive key must be ignored.
template<class T> void hostKey(unsigned rate,unsigned block,unsigned budget,bool enabled,bool simultaneous){
    bh::Host keyed,manual;MemoryConfig c{};c.wet=1000;c.budget=budget;c.energyFirst=true;
    for(unsigned k=0;k<4;++k){auto& b=c.bands[k];b.peakMix=1000;b.gain=800;b.selectivity=static_cast<std::uint16_t>((177+k*271)%1001);}
    require(keyed.request(c)&&manual.request(c)&&keyed.prepare(rate)&&manual.prepare(rate));
    std::array<T,257> l{},r{},keyL{},keyR{},a{},b{},x{},y{};
    std::array<bh::Event,32> ke{},me{};bool different=false;
    for(unsigned start=0;start<rate*3;){
        const unsigned n=std::min(block,rate*3-start);unsigned kc=0,mc=0;
        for(unsigned i=0;i<n;++i){const unsigned t=start+i;const auto in=program(t,rate);
            l[i]=T(in.left);r[i]=T(in.right);keyL[i]=0;keyR[i]=key(t,rate)?T(-26214.0/32768):T(0);
            if(t==rate/4)for(unsigned k=0;k<4;++k){const bh::Event e{i,bh::FirstBand+k*bh::Stride+bh::Excite,0};ke[kc++]=e;me[mc++]=e;}
            const bool manualHere=simultaneous&&(t==rate/2||t==rate/2+1);
            if(manualHere)ke[kc++]={i,bh::AdmitBudget,t==rate/2?1.:0.};
            if((enabled&&(expected(t,rate)||(t&&expected(t-1,rate))))||manualHere)
                me[mc++]={i,bh::AdmitBudget,(expected(t,rate)?1.:0.)};
        }
        require(keyed.processOptional(l.data(),r.data(),a.data(),b.data(),n,ke.data(),kc,enabled,keyL.data(),keyR.data()));
        require(manual.processOptional(l.data(),r.data(),x.data(),y.data(),n,me.data(),mc));
        for(unsigned i=0;i<n;++i){require(a[i]==x[i]&&b[i]==y[i]&&std::isfinite(a[i])&&std::isfinite(b[i]));if(start+i>=rate*2&&(a[i]!=0||b[i]!=0))different=true;}
        start+=n;
    }
    require(keyed.save()==manual.save());
    if(budget==0||(!enabled&&!simultaneous))require(different);
    if(enabled&&budget==16)require(!different);
}
void run(unsigned rate,unsigned budget,const std::string& dir){
    HarmonicBank native;TransientGate detector;bh::Host host;
    MemoryConfig c{};c.wet=1000;c.budget=budget;c.energyFirst=true;
    for(unsigned k=0;k<4;++k){auto& b=c.bands[k];b.peakMix=1000;b.gain=800;b.selectivity=static_cast<std::uint16_t>((177+k*271)%1001);}
    require(native.set(c)&&native.prepare(rate)&&detector.prepare(rate)&&host.request(c)&&host.prepare(rate));
    std::ofstream wav,events;unsigned total=0,mask=0;double tail=0;
    if(!dir.empty()&&rate==48000){wav.open(dir+"/budget-"+std::to_string(budget)+".wav",std::ios::binary);require(bool(wav));header(wav,rate);events.open(dir+"/budget-"+std::to_string(budget)+".csv");require(bool(events));events<<"sample,param_id,normalized\n";}
    for(unsigned t=0;t<rate*3;++t){
        const auto input=program(t,rate);
        std::array<bh::Event,4> e{};unsigned count=0;
        if(t==rate/4){for(unsigned k=0;k<4;++k){c.bands[k].excite=false;e[count++]={0,bh::FirstBand+k*bh::Stride+bh::Excite,0};}require(native.set(c));}
        const auto p=transientErase(detector,native,0,key(t,rate)?-26214.0/32768:0,budget,BudgetObjective::energy);
        require(p.cost<=budget);if(!expected(t,rate))require(p.mask==0);
        if(expected(t,rate)|| (t&&expected(t-1,rate)))e[count++]={0,bh::AdmitBudget,expected(t,rate)?1.:0.};
        if(events.is_open())for(unsigned k=0;k<count;++k)events<<t<<','<<e[k].id<<','<<e[k].value<<'\n';
        total+=p.cost;mask|=p.mask;
        const auto s=native.process(input.left,input.right);double l=0,r=0;
        require(host.process(&input.left,&input.right,&l,&r,1,e.data(),count));
        require(s.left==l&&s.right==r&&std::isfinite(l)&&std::isfinite(r)&&std::abs(l)<=1&&std::abs(r)<=1);
        if(t>=rate*2)tail+=l*l+r*r;
        if(wav.is_open()){const double fade=std::min({1.,double(t)/(.01*rate),double(rate*3-1-t)/(.05*rate)});sample(wav,l*.5*fade);sample(wav,r*.5*fade);}
    }
    unsigned spent=0;for(unsigned k=0;k<4;++k)spent+=static_cast<unsigned>(native.interventions(k));require(spent==total);
    if(budget==0)require(mask==0&&tail>0);else if(budget>=4)require(mask!=0&&total>0);
    if(budget==16)require(mask==15&&tail==0);
    if(wav.is_open()){wav.close();events.close();require(bool(wav)&&bool(events));}
    std::cout<<"rate="<<rate<<" budget="<<budget<<" mask="<<mask<<" reserved="<<total<<" tail_energy="<<tail<<'\n';
}
}
int main(int argc,char** argv){
    require(argc==1||argc==2);const std::string dir=argc==2?argv[1]:"";
    for(unsigned rate:{44100u,48000u,96000u}){gateTests(rate);for(unsigned budget:{0u,2u,4u,16u})run(rate,budget,dir);}
    if(!dir.empty()){
        constexpr unsigned rate=48000;
        std::ofstream source(dir+"/Program.wav",std::ios::binary),side(dir+"/Key.wav",std::ios::binary);
        require(bool(source)&&bool(side));header(source,rate);header(side,rate);
        for(unsigned t=0;t<rate*3;++t){const auto s=program(t,rate);word(source,unsigned(int(std::round(s.left*32768))),2);word(source,unsigned(int(std::round(s.right*32768))),2);word(side,0,2);word(side,key(t,rate)?unsigned(-26214):0,2);}
        source.close();side.close();require(bool(source)&&bool(side));
    }
    unsigned keyCases=0;
    for(unsigned rate:{44100u,48000u,96000u})for(unsigned block:{1u,257u})for(unsigned budget:{0u,4u,16u})for(bool enabled:{false,true})for(bool simultaneous:{false,true}){
        hostKey<float>(rate,block,budget,enabled,simultaneous);hostKey<double>(rate,block,budget,enabled,simultaneous);keyCases+=2;
    }
    std::cout<<"BANK_KEY_ROUTING_PASS cases="<<keyCases<<"\n";
    std::cout<<"BANK_TRANSIENT_PASS rates=3 configurations=12 paired_frames=2257200\n";
}
