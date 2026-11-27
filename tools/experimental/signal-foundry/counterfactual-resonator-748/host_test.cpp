#include "host.hpp"
#include <cstdlib>
#include <iostream>
#include <limits>
#include <thread>
using namespace mhac::counterfactual;
namespace h=mhac::counterfactual::host;
static unsigned checks=0;
static void check(bool b){++checks;if(!b){std::cerr<<"FAIL "<<checks<<'\n';std::exit(1);}}
int main(){
    for(unsigned hz=40;hz<=6000;++hz){Controls c;c.hz=static_cast<std::uint16_t>(hz);Controls d;check(h::change(d,h::Frequency,h::normalized(c,h::Frequency))&&d.hz==c.hz);}
    for(unsigned i=0;i<=1000;++i){Controls c;c.wet=static_cast<std::uint16_t>(i);c.gain=static_cast<std::uint16_t>(1000-i);for(unsigned m=0;m<3;++m){c.monitor=static_cast<std::uint8_t>(m);for(unsigned f=0;f<4;++f){c.erase=bool(f&1);c.bypass=bool(f&2);check(encode(h::unpack(h::pack(c)))==encode(c));}}}
    h::Host host;Controls a{250,1000,1000,1,false,false},b{6000,0,1,2,true,true};
    check(host.request(a)&&host.save()==encode(a));check(host.request(b)&&host.save()==encode(b));check(host.request(a)&&host.prepare(48000));check(host.save()==encode(a));
    auto bad=encode(a);bad[11]=128;check(!host.request(bad)&&host.save()==encode(a));
    check(!host.parameter(h::Wet,std::numeric_limits<double>::quiet_NaN()));check(!host.parameter(h::Count,0));
    // Held-high pulse cannot retrigger. Multiple edges before a tick coalesce.
    host.begin();check(host.parameter(h::Pulse,1));check(host.parameter(h::Pulse,1));
    for(int i=0;i<240;++i){double l=.5,r=0;host.frame(l,r);}
    check(host.interventions()==1);check(host.parameter(h::Pulse,1));
    for(int i=0;i<240;++i){double l=0,r=0;host.frame(l,r);}check(host.interventions()==1);
    check(host.parameter(h::Pulse,0)&&host.parameter(h::Pulse,1)&&host.parameter(h::Pulse,0)&&host.parameter(h::Pulse,1));
    for(int i=0;i<240;++i){double l=0,r=0;host.frame(l,r);}check(host.interventions()==2);host.end();check(host.save()==encode(a));
    // Direct DSP oracle; two block partitions, both formats, dense automation.
    for(double rate:{1000.,1234.568,8000.,44100.,48000.,96000.,384000.,1234567.8,2000000.}){
        h::Host x,y;Processor oracle;Controls c=a;check(x.request(c)&&y.request(c)&&oracle.set(c));check(x.prepare(rate)&&y.prepare(rate)&&oracle.prepare(rate));bool prior=false;
        for(unsigned i=0;i<32000;++i){
            if(i%31==0)x.begin();
            if(i%127==0)y.begin();
            const unsigned id=i%h::Count;const double v=double((i*71)%1001)/1000;
            check(x.parameter(id,v)&&y.parameter(id,v));
            if(id==h::Pulse){const bool high=v>=.5;if(high&&!prior)oracle.requestIntervention();prior=high;}
            else {check(h::change(c,id,v));check(oracle.set(c));}
            const float in=static_cast<float>(double(int(i%97)-48)/48);float fl=in,fr=-in;double dl=in,dr=-in;
            x.frame(fl,fr);y.frame(dl,dr);auto s=oracle.process(in,-in);
            check(dl==s.left&&dr==s.right&&fl==static_cast<float>(dl)&&fr==static_cast<float>(dr));
            if(i%31==30)x.end();
            if(i%127==126)y.end();
        }
        x.end();y.end();check(x.save()==encode(c)&&y.save()==encode(c));check(x.interventions()==oracle.interventions()&&y.ticks()==oracle.ticks());
    }
    // Reject bad rates without changing the live clock or configured patch.
    Processor rateProbe;check(rateProbe.set(a)&&rateProbe.prepare(1234.568));
    check(rateProbe.effectiveHz()==1234.568/16.0);
    for(int i=0;i<64;++i)rateProbe.process(.5,0);
    const auto priorTicks=rateProbe.ticks();
    for(double invalid:{0.,999.,2000001.,std::numeric_limits<double>::infinity(),std::numeric_limits<double>::quiet_NaN()}){
        check(!rateProbe.prepare(invalid));check(rateProbe.ticks()==priorTicks&&encode(rateProbe.controls())==encode(a));
    }
    check(rateProbe.prepare(1234567.8)&&rateProbe.ticks()==0&&rateProbe.effectiveHz()==250.);
    // At the highest rate, a long tick accumulation still converges under erase.
    Controls high{40,1000,1000,1,false,false};check(rateProbe.set(high)&&rateProbe.prepare(2000000.));
    for(int i=0;i<12501;++i)rateProbe.process(.8,0);
    check(rateProbe.ticks()==1&&rateProbe.lattice(0).x!=0);
    high.erase=true;check(rateProbe.set(high));
    Stereo tail{};for(int i=0;i<225000;++i)tail=rateProbe.process(0,0);
    check(rateProbe.lattice(0).x==0&&rateProbe.lattice(0).y==0&&tail.left==0&&tail.right==0);
    // Concurrent whole-patch submission and snapshot; either complete patch is legal.
    h::Host concurrent;check(concurrent.request(a)&&concurrent.prepare(48000));
    std::atomic<bool> ok{true};std::thread writer([&]{for(unsigned i=0;i<100000;++i){if(!concurrent.request(i%2?a:b))ok=false;auto p=concurrent.save();if(p!=encode(a)&&p!=encode(b))ok=false;}});
    for(unsigned i=0;i<100000;++i){concurrent.begin();double l=.1,r=-.1;concurrent.frame(l,r);concurrent.end();auto p=concurrent.save();check(p==encode(a)||p==encode(b));}
    writer.join();check(ok.load());std::cout<<"PASS "<<checks<<" host checks\n";
}
