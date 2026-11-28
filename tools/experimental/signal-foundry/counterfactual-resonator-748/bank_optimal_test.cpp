#include "bank_adapter.hpp"
#include <cstdlib>
#include <iostream>
#include <fstream>
using namespace mhac::counterfactual;
namespace bh=mhac::counterfactual::bankhost;
static unsigned checks=0;
static void check(bool ok){++checks;if(!ok){std::cerr<<"optimal host failure "<<checks<<'\n';std::exit(1);}}

template<class T,class Engine> static void replay(Engine& host,double rate,unsigned band,unsigned block,bool reverse,bool manual,bool mono){
    MemoryConfig c{};c.wet=1000;
    for(auto& b:c.bands){b.excite=false;b.gain=0;}
    c.bands[band]={110,1000,1000,true,false,0,false};
    HarmonicBank ref;
    check(ref.set(c)&&ref.prepare(rate)&&host.request(c)&&host.prepare(rate));
    const unsigned id=bh::FirstBand+band*bh::Stride, opt=bh::FirstOptimal+band;
    // Close at a non-block-aligned offset, reopen while command remains high,
    // close again with a repeated high (must not fire), then release/rearm.
    constexpr unsigned gate=12000, reopen=18000, gate2=30000, rearm=34000, end=42000;
    std::array<T,257> l{},r{},ol{},orr{};
    bh::EventBatch batch;
    bool heardSecond=false;
    for(unsigned start=0;start<end;){
        const unsigned n=std::min(block,end-start);batch.clear(n);
        const auto queue=[&](unsigned param){check(batch.queue(param));};
        const auto point=[&](unsigned t,double value){if(t>=start&&t<start+n)check(batch.point(t-start,value));};
        const auto captures=[&](){queue(id+bh::Excite);point(gate,0);point(reopen,1);point(gate2,0);};
        const auto escapes=[&](){queue(opt);point(gate,1);point(gate2,1);point(rearm,0);point(rearm+1,1);};
        const auto pulses=[&](){if(manual){queue(id+bh::Pulse);point(gate,1);point(gate+1,0);}};
        if(reverse){escapes();pulses();captures();}else{captures();pulses();escapes();}
        check(batch.finish());
        for(unsigned i=0;i<n;++i){const unsigned t=start+i;const bool drive=t<gate||(t>=reopen&&t<gate2);
            l[i]=drive?static_cast<T>(0.8*std::sin(6.283185307179586*110*t/rate)):T(0);r[i]=mono?T(0):static_cast<T>(l[i]*0.63);}
        check(host.processOptional(l.data(),mono?nullptr:r.data(),ol.data(),mono?nullptr:orr.data(),n,batch.data(),batch.size()));
        for(unsigned i=0;i<n;++i){const unsigned t=start+i;
            if(t==gate||t==gate2||t==reopen){c.bands[band].excite=t==reopen;check(ref.set(c));}
            if(t==gate){check(magnitude(ref.lattice(band,0))||magnitude(ref.lattice(band,1)));if(manual)check(ref.pulse(band));check(ref.beginOptimalEscape(band)==!manual);}
            if(t==rearm+1)check(ref.beginOptimalEscape(band));
            const auto s=ref.process(l[i],r[i]);check(ol[i]==static_cast<T>(s.left)&&(mono||orr[i]==static_cast<T>(s.right)));
            if(t>=gate2+2500&&t<rearm&&(ol[i]!=0||(!mono&&orr[i]!=0)))heardSecond=true;
            if(t>=39000)check(ol[i]==0&&(mono||orr[i]==0));
        }
        start+=n;
    }
    check(heardSecond);check(host.save()==bh::encode(c));
}
static void demo(const char* path,bool optimal){
    MemoryConfig c{};c.wet=1000;
    for(auto& b:c.bands){b.excite=false;b.gain=0;}
    c.bands[0]={110,1000,1000,true,false,0,false};
    bh::Host h;check(h.request(c)&&h.prepare(48000));
    std::ofstream f(path,std::ios::binary);check(bool(f));
    const auto u=[&](unsigned v,unsigned n){for(unsigned i=0;i<n;++i)f.put(static_cast<char>((v>>(8*i))&255));};
    constexpr unsigned frames=48000,bytes=frames*4;
    f.write("RIFF",4);u(36+bytes,4);f.write("WAVEfmt ",8);u(16,4);u(1,2);u(2,2);u(48000,4);u(192000,4);u(4,2);u(16,2);f.write("data",4);u(bytes,4);
    std::array<double,127> l{},r{};
    for(unsigned start=0;start<frames;){const unsigned n=std::min(127u,frames-start);
        std::array<bh::Event,3> ev{};unsigned m=0;
        for(unsigned i=0;i<n;++i){const unsigned t=start+i;
            l[i]=t<12000?0.8*std::sin(6.283185307179586*110*t/48000):0;r[i]=l[i]*0.63;
            if(t==12000){ev[m++]={i,bh::FirstBand+bh::Excite,0};ev[m++]={i,bh::FirstBand+bh::Discard,1};ev[m++]={i,optimal?bh::FirstOptimal:bh::FirstBand+bh::Erase,1};}}
        check(h.process(l.data(),r.data(),l.data(),r.data(),n,ev.data(),m));
        for(unsigned i=0;i<n;++i){if(start+i>=30000)check(l[i]==0&&r[i]==0);
            for(double v:{l[i],r[i]})u(static_cast<unsigned>(static_cast<int>(std::lround(v*32767))),2);}
        start+=n;
    }
    check(bool(f));
}
#include "bank_budget_replay.hpp"
static void nativeTests(int argc,char** argv){
    budgetStateTests();
    for(bool energy:{false,true})for(unsigned block:{127u,257u})for(bool mono:{false,true}){bh::Host a,b;budgetReplay<float>(a,48000,block,energy,mono);budgetReplay<double>(b,96000,block,energy,mono);}
    check(bh::ParamCount==45);
    for(unsigned i=0;i<bh::ParamCount;++i){const unsigned id=bh::paramID(i);check(bh::known(id)&&bh::index(id)==i);if(i>=38)check(id==2050+i-38&&bh::command(id)==(i<42||i==44)&&bh::normalized(MemoryConfig{},id)==0);}
    for(unsigned id:{2002u,2046u,2049u,2057u,9999u})check(!bh::known(id));
    bh::EventBatch b;b.clear(0);check(b.queue(2050)&&b.point(0,1)&&!b.queue(2050));
    for(unsigned band=0;band<4;++band)for(bool reverse:{false,true})for(bool manual:{false,true}){
        for(unsigned block:{127u,257u})for(bool mono:{false,true}){bh::Host a,other;replay<float>(a,48000,band,block,reverse,manual,mono);replay<double>(other,96000,band,block,reverse,manual,mono);}
    }
    if(argc==3){demo(argv[1],false);demo(argv[2],true);}
    std::cout<<"optimal host PASS checks="<<checks<<'\n';
}

#ifndef MHAC_BANK_SDK_REPLAY
int main(int argc,char** argv){nativeTests(argc,argv);}
#endif
