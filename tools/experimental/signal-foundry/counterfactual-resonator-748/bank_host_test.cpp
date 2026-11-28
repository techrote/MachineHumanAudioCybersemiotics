#include "bank_host.hpp"
#include <cstdlib>
#include <iostream>
#include <thread>
#include <vector>
using namespace mhac::counterfactual;
namespace bh=mhac::counterfactual::bankhost;
static unsigned checks=0;
static void check(bool b){++checks;if(!b){std::cerr<<"failed check "<<checks<<'\n';std::exit(1);}}
int main(){
    MemoryConfig c{};c.wet=1000;c.bands[0].selectivity=1000;c.bands[0].discardOnClose=true;
    const auto state=bh::encode(c);MemoryConfig d{};check(bh::decode(state,d)&&bh::encode(d)==state);
    for(unsigned i=0;i<4;++i){auto bad=state;bad[i]=0;check(!bh::decode(bad,d)&&bh::encode(d)==state);}
    for(unsigned i=0;i<4;++i){auto bad=state;bad[15+i*9]=8;check(!bh::decode(bad,d)&&bh::encode(d)==state);}
    for(unsigned v=0;v<=1000;++v){c.wet=static_cast<std::uint16_t>(v);c.bands[2].peakMix=c.wet;
        auto s=bh::encode(c);check(bh::decode(s,d)&&bh::encode(d)==s);}
    c.wet=1000;const unsigned b=bh::FirstBand;
    const std::array<bh::Event,8> events{{{31,b+bh::Excite,0},{31,b+bh::DiscardOnClose,1},{31,b+bh::Discard,1},
        {32,b+bh::Discard,0},{33,b+bh::Pulse,1},{63,b+bh::Pulse,0},{71,b+bh::Erase,1},{71,bh::Wet,0.8}}};
    for(double rate:{1000.,44100.,48000.,96000.,192000.,2000000.}){
        bh::Host h,split;HarmonicBank oracle;
        check(h.request(c)&&split.request(c)&&h.prepare(rate)&&split.prepare(rate)&&oracle.set(c)&&oracle.prepare(rate));
        std::array<double,256> l{},r{},ol{},orr{},sl{},sr{};
        for(unsigned i=0;i<l.size();++i){l[i]=i<31?0.7*std::sin(i*0.23):0;r[i]=i<31?-0.4:0;}
        check(h.process(l.data(),r.data(),ol.data(),orr.data(),256,events.data(),static_cast<unsigned>(events.size())));
        auto config=c;unsigned j=0;
        for(unsigned i=0;i<256;++i){const unsigned start=j;while(j<events.size()&&events[j].offset==i){if(!bh::command(events[j].id))bh::change(config,events[j].id,events[j].value);++j;}
            if(j>start)oracle.set(config);
            for(unsigned k=start;k<j;++k){if(events[k].id==b+bh::Discard&&events[k].value==1)oracle.discardPendingInput(0);if(events[k].id==b+bh::Pulse&&events[k].value==1)oracle.pulse(0);}
            const auto expected=oracle.process(l[i],r[i]);check(ol[i]==expected.left&&orr[i]==expected.right);}
        for(unsigned start=0;start<256;){const unsigned n=std::min(17u,256-start);std::array<bh::Event,8> local{};unsigned m=0;
            for(auto e:events)if(e.offset>=start&&e.offset<start+n){e.offset-=start;local[m++]=e;}
            check(split.process(l.data()+start,r.data()+start,sl.data()+start,sr.data()+start,n,local.data(),m));start+=n;}
        check(ol==sl&&orr==sr&&h.snapshot()==split.snapshot());
        const auto before=h.snapshot();bh::Event bad{256,bh::Wet,0};ol.fill(123);
        check(!h.process(l.data(),r.data(),ol.data(),orr.data(),256,&bad,1)&&ol[0]==123&&h.snapshot()==before);
        bad={0,bh::Wet,std::numeric_limits<double>::quiet_NaN()};check(!h.process(l.data(),r.data(),ol.data(),orr.data(),256,&bad,1));
        std::array<float,256> fl{},fr{};h.reset();check(h.process(fl.data(),fr.data(),fl.data(),fr.data(),256));
        for(unsigned i=0;i<256;++i)check(fl[i]==0&&fr[i]==0);
    }
    // Concurrent complete configuration handoff; never accept a torn patch.
    bh::Mailbox box;std::atomic<bool> done{false};std::atomic<unsigned> count{0};
    std::thread writer([&]{for(unsigned i=0;i<200000;++i){MemoryConfig p{};p.wet=static_cast<std::uint16_t>(i%1001);for(auto& band:p.bands)band.gain=p.wet;box.publish(p);}done.store(true,std::memory_order_release);});
    do{MemoryConfig p{};if(box.consume(p)){for(const auto& band:p.bands)check(band.gain==p.wet);++count;}}while(!done.load(std::memory_order_acquire));
    writer.join();MemoryConfig p{};if(box.consume(p)){for(const auto& band:p.bands)check(band.gain==p.wet);++count;}
    check(count.load()>0);std::cout<<"bank host PASS; checks="<<checks<<" coherent concurrent snapshots="<<count.load()<<'\n';
}
