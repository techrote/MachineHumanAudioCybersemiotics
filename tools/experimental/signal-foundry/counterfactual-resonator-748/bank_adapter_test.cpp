#include "bank_adapter.hpp"
#include <cstdlib>
#include <iostream>
using namespace mhac::counterfactual;
namespace bh=mhac::counterfactual::bankhost;
static unsigned checks=0;
static void check(bool ok){++checks;if(!ok){std::cerr<<"failed "<<checks<<'\n';std::exit(1);}}
int main(){
    MemoryConfig c{};c.wet=500;c.bands[0].gain=312;
    for(unsigned i=0;i<bh::ParamCount;++i){const auto id=bh::paramID(i);check(bh::known(id)&&bh::index(id)==i);auto copy=c;if(!bh::command(id)){bh::change(copy,id,bh::normalized(c,id));check(bh::encode(copy)==bh::encode(c));}}
    bh::Host h;check(h.request(c)&&h.save()==bh::encode(c));check(h.prepare(48000)&&h.save()==bh::encode(c));
    bh::EventBatch batch;batch.clear(16);check(batch.queue(bh::Wet)&&batch.point(0,.7)&&batch.point(9,.2));
    check(batch.queue(bh::FirstBand+bh::Gain)&&batch.point(0,.4)&&batch.point(7,.8));check(batch.finish()&&batch.size()==4);
    check(batch.data()[0].id==bh::Wet&&batch.data()[1].id==bh::FirstBand+bh::Gain&&batch.data()[2].offset==7&&batch.data()[3].offset==9);
    double out[16]{};check(h.processOptional<double>(nullptr,nullptr,out,nullptr,16,batch.data(),batch.size()));
    for(double v:out)check(v==0);
    c.wet=200;c.bands[0].gain=800;check(h.save()==bh::encode(c));
    auto pending=c;pending.wet=900;check(h.request(pending)&&h.save()==bh::encode(pending)&&h.snapshot()==bh::encode(c));
    batch.clear(0);check(batch.queue(bh::Wet)&&batch.point(0,.6)&&batch.finish());
    check(h.processOptional<double>(nullptr,nullptr,nullptr,nullptr,0,batch.data(),batch.size()));pending.wet=600;check(h.save()==bh::encode(pending));
    batch.clear(1);check(batch.queue(bh::Wet));for(unsigned i=0;i<bh::MaxEvents;++i)check(batch.point(0,double(i)/bh::MaxEvents));check(batch.finish());
    for(unsigned i=0;i<bh::MaxEvents;++i)check(batch.data()[i].value==double(i)/bh::MaxEvents);
    check(!batch.point(0,0)&&!batch.finish());batch.clear(2);check(batch.queue(bh::Wet)&&batch.point(1,.2)&&!batch.point(0,.1)&&!batch.finish());
    batch.clear(2);check(batch.queue(bh::Wet)&&!batch.queue(bh::Wet));batch.clear(0);check(batch.queue(bh::Wet)&&!batch.point(1,0));
    batch.clear(1);check(batch.queue(bh::Wet)&&!batch.point(0,std::numeric_limits<double>::infinity()));
    std::cout<<"bank adapter PASS checks="<<checks<<'\n';
}
