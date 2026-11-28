#include "clock_state_bridge.hpp"
#include <cstdlib>
#include <iostream>
#include <thread>
using namespace mhac::clock_fold;
static void check(bool x){if(!x){std::cerr<<"state bridge assertion failed\n";std::abort();}}
static Normalized uniform(double x){Normalized p;p.fill(x);return p;}
static bool coherent(const Normalized& p){return valid(p)&&std::all_of(p.begin(),p.end(),[&](double x){return x==p[0];});}
int main(){
    auto engine=std::make_unique<Live>();check(engine->prepare(48000));
    StateBridge bridge;Normalized p{};check(bridge.save(p)&&p==defaults);
    auto a=uniform(.25), b=uniform(.75);
    check(bridge.request(a));check(bridge.request(b));check(bridge.save(p)&&p==b);
    check(engine->params()==defaults);check(bridge.begin(*engine));check(engine->params()==b);
    check(!bridge.begin(*engine));bridge.end(*engine);check(bridge.save(p)&&p==b);
    check(engine->set(Wet,.125));bridge.end(*engine);check(bridge.save(p)&&p[Wet]==.125);
    auto invalid=b;invalid[Wet]=std::numeric_limits<double>::quiet_NaN();
    check(!bridge.request(invalid));check(bridge.save(p)&&p[Wet]==.125);
    // State requests do not touch live audio until the block begins; restore
    // clears both packets, and a second begin without a request never resets.
    check(bridge.request(defaults));check(bridge.begin(*engine));bridge.end(*engine);
    for(std::size_t i=0;i<2*frameSize;++i)engine->step(.5,-.5);
    check(!bridge.begin(*engine));check(engine->step(.5,-.5)[0]==.5);
    check(bridge.request(defaults));check(bridge.begin(*engine));
    for(std::size_t i=0;i<frameSize;++i)check(engine->step(0,0)==Stereo{});
    bridge.end(*engine);check(bridge.save(p)&&p==defaults);
    // Isolate mailbox contention: exact binary64 words, no torn accepted reads.
    StateMailbox mail;mail.publish(a,1);std::atomic<bool> start{false},done{false},ready{false};
    std::atomic<unsigned> accepted{0},rejected{0};
    std::thread reader([&]{StateMailbox::Snapshot first;check(mail.read(first)&&first.params==a);++accepted;ready=true;while(!start.load())std::this_thread::yield();do{
        StateMailbox::Snapshot s;if(mail.read(s)){check(coherent(s.params));check(s.params[0]==double(s.ack%997)/997.||s.ack==1);++accepted;}else ++rejected;
    }while(!done.load());});
    while(!ready.load())std::this_thread::yield();
    start.store(true);for(unsigned i=2;i<100002;++i)mail.publish(uniform(double(i%997)/997.),i);done.store(true);reader.join();
    check(accepted>0);StateMailbox::Snapshot s;check(mail.read(s)&&s.ack==100001);
    std::cout<<"mailbox accepted="<<accepted<<" rejected="<<rejected<<"\n";
    // Concurrent UI restores/saves vs audio block ownership. Every parameter
    // vector is one of the uniform transactions; audio automation is simulated
    // as a complete vector per block. No other thread accesses Live.
    check(bridge.request(a));check(bridge.begin(*engine));bridge.end(*engine);
    start=false;done=false;std::atomic<unsigned> saves{0},busy{0};
    std::thread ui([&]{while(!start.load())std::this_thread::yield();for(unsigned i=0;i<30000;++i){
        check(bridge.request(uniform(double(i%997)/997.)));
        Normalized q;if(bridge.save(q)){check(coherent(q));++saves;}else ++busy;
    }done=true;});
    start=true;unsigned blocks=0;do{
        bridge.begin(*engine);const auto v=double(blocks%997)/997.;
        for(unsigned k=0;k<Count;++k)check(engine->set(k,v));
        for(unsigned k=0;k<17;++k){auto y=engine->step(.2,-.2);check(std::isfinite(y[0])&&std::isfinite(y[1]));}
        bridge.end(*engine);++blocks;
    }while(!done.load());ui.join();check(saves>0&&blocks>0);
    check(bridge.request(b));check(bridge.save(p)&&p==b);check(bridge.begin(*engine));bridge.end(*engine);check(bridge.save(p)&&p==b);
    std::cout<<"blocks="<<blocks<<" saves="<<saves<<" busy="<<busy<<"\n";
}
