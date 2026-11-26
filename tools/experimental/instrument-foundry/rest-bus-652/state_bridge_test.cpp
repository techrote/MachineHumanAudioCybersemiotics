#include "state_bridge.hpp"
#include <cstdlib>
#include <iostream>
using namespace restbus::control;
static void check(bool x){if(!x){std::cerr<<"state bridge assertion failed\n";std::abort();}}
static Params uniform(double x){return {x,x,x};}
static bool coherent(const Params& p){return valid(p[0])&&p==uniform(p[0]);}
int main(){
    Live e, ref;check(e.prepare(48000)&&ref.prepare(48000));
    StateBridge bridge;Params p{};check(bridge.save(p)&&p==defaults);
    check(e.on(1,57,0,.8)&&ref.on(1,57,0,.8));
    for(int i=0;i<128;++i)check(e.tick()==ref.tick());
    auto a=uniform(.25),b=uniform(.75);
    check(bridge.request(a)&&bridge.request(b));check(bridge.save(p)&&p==b);
    check(e.parameters()==defaults);for(int i=0;i<128;++i)check(e.tick()==ref.tick());
    check(bridge.begin(e)&&e.parameters()==b&&e.index()==0&&e.partial()==0&&e.tick()==0);
    check(!bridge.begin(e));bridge.end(e);check(bridge.save(p)&&p==b);
    check(e.parameter(3,.5));bridge.end(e);check(bridge.save(p)&&p==Params{.75,.75,.5});
    auto invalid=b;invalid[2]=std::numeric_limits<double>::quiet_NaN();
    check(!bridge.request(invalid)&&bridge.save(p)&&p==Params{.75,.75,.5});
    check(bridge.request(defaults)&&bridge.begin(e));bridge.end(e);
    check(e.on(1,57,0,.8));check(!bridge.begin(e));check(e.tick()!=0);
    // Accepted mailbox reads must be coherent even during publication.
    StateMailbox mail;mail.publish(a,1);std::atomic<bool> ready{false},done{false};
    unsigned accepted=0,rejected=0;
    std::thread reader([&]{StateMailbox::Snapshot s;check(mail.read(s)&&s.params==a);++accepted;ready=true;
        do{if(mail.read(s)){check(coherent(s.params));check(s.ack==1||s.params[0]==double(s.ack%997)/997.);++accepted;}else ++rejected;}while(!done.load());});
    while(!ready.load())std::this_thread::yield();
    for(unsigned i=2;i<100002;++i)mail.publish(uniform(double(i%997)/997.),i);
    done=true;reader.join();StateMailbox::Snapshot s;check(mail.read(s)&&s.ack==100001&&coherent(s.params));
    std::cout<<"mailbox accepted="<<accepted<<" rejected="<<rejected<<"\n";
    check(bridge.request(a)&&bridge.begin(e));bridge.end(e);done=false;ready=false;
    unsigned saves=0,busy=0;
    std::thread ui([&]{while(!ready.load())std::this_thread::yield();for(unsigned i=0;i<30000;++i){
        check(bridge.request(uniform(double(i%997)/997.)));Params q;
        if(bridge.save(q)){check(coherent(q));++saves;}else ++busy;
    }done=true;});
    ready=true;unsigned blocks=0;do{
        bridge.begin(e);double v=double(blocks%997)/997.;
        check(e.parameter(0,v)&&e.parameter(1,v)&&e.parameter(3,v));
        e.on(1,57,0,.8);for(int i=0;i<17;++i){double y=e.tick();check(std::isfinite(y)&&std::abs(y)<=.480000000001);}e.off(1);
        bridge.end(e);++blocks;
    }while(!done.load());ui.join();check(saves>0&&blocks>0&&saves+busy==30000);
    check(bridge.request(b)&&bridge.save(p)&&p==b&&bridge.begin(e));bridge.end(e);check(bridge.save(p)&&p==b);
    std::cout<<"blocks="<<blocks<<" saves="<<saves<<" busy="<<busy<<"\n";
}
