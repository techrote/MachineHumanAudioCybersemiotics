#include "state_bridge.hpp"
#include "freeze.hpp"
#include <atomic>
#include <cstdlib>
#include <iostream>
#include <thread>
using namespace mhac::freeze;
using mhac::mainline::StateBridge;
static void check(bool ok){if(!ok)std::abort();}
int main(){
    Engine engine;StateBridge<Params> bridge(engine.params());
    check(bridge.snapshot()==defaults);
    Params p=defaults,q=defaults,out{};p[Rate]=.2;q[Rate]=.8;
    bridge.request(p);check(bridge.snapshot()==p);bridge.request(q);
    check(bridge.take(out)&&out==q);check(!bridge.take(out));
    engine.restore(out);engine.set(Depth,.7);bridge.publish(engine.params());
    q[Depth]=.7;check(bridge.snapshot()==q);
    bridge.request(p);bridge.publish(q);check(bridge.snapshot()==p);
    check(bridge.take(out)&&out==p);engine.restore(out);bridge.publish(engine.params());
    check(bridge.snapshot()==p);
    std::atomic<bool> start{false},done{false};std::atomic<unsigned> saved{0};
    auto make=[](unsigned i){Params x{};x.fill(double(i%1000)/1000.);return x;};
    std::thread writer([&]{while(!start.load(std::memory_order_acquire)){};
        for(unsigned i=0;i<100000;++i)bridge.request(make(i));
        done.store(true,std::memory_order_release);});
    std::thread saver([&]{while(!start.load(std::memory_order_acquire)){};
        while(!done.load(std::memory_order_acquire)){
            auto x=bridge.snapshot();for(double v:x)check(v>=0&&v<=1);++saved;
        }});
    start.store(true,std::memory_order_release);
    double sum=0;for(unsigned block=0;block<100000;++block){
        if(bridge.take(out))engine.restore(out);
        for(unsigned i=0;i<64;++i)sum+=engine.nextGain();
        bridge.publish(engine.params());
    }
    writer.join();saver.join();if(bridge.take(out))engine.restore(out);
    bridge.publish(engine.params());check(bridge.snapshot()==make(99999));
    check(std::isfinite(sum));std::cout<<"PASS 100000 concurrent restores, 100000 audio blocks, "<<saved.load()<<" concurrent saves; checksum "<<sum<<'\n';
}
