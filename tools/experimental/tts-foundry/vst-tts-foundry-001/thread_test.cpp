#include "logos.hpp"
#include <atomic>
#include <cmath>
#include <iostream>
#include <stdexcept>
#include <thread>
using namespace mhac::tts;
static void need(bool ok,const char* msg){if(!ok)throw std::runtime_error(msg);}
int main(){
    Logos e; need(e.prepare(48000),"prepare"); e.note_on(60,.8);
    std::atomic<bool> done{false}; std::atomic<unsigned> accepted{0};
    std::thread producer([&]{
        for(unsigned i=0;i<20000;++i){
            auto p=phrase_program(i);
            while(!e.enqueue_plan(p)) std::this_thread::yield();
            accepted.fetch_add(1,std::memory_order_relaxed);
        }
        done.store(true,std::memory_order_release);
    });
    unsigned blocks=0; double energy=0;
    while(!done.load(std::memory_order_acquire)||blocks<20000){
        e.begin_block();
        for(int j=0;j<16;++j){const double y=e.tick();need(std::isfinite(y),"nonfinite audio");energy+=y*y;}
        ++blocks;
        if(blocks>40000) break;
    }
    producer.join();
    need(accepted.load()==20000,"all phrase writes accepted");
    need(blocks<=40000,"consumer progress");
    need(energy>0.1,"audio energy");
    std::cout<<"VST-TTS-FOUNDRY SPSC phrase exchange PASS\n";
}
