#include "trace_bell_mailbox.hpp"
#include <cassert>
#include <cstdio>
#include <thread>
using namespace mhac::accel;
struct Patch {
    unsigned n=0,a=0,b=0,c=0,d=0,e=0;
};
static Patch make(unsigned n){return {n,n*3u,n*5u,n*7u,n*11u,n*13u};}
static void check(Patch p){const auto x=make(p.n);assert(p.a==x.a&&p.b==x.b&&p.c==x.c&&p.d==x.d&&p.e==x.e);}
int main(){
    TraceStateBridge<Patch> bridge;
    assert(bridge.snapshot().n==0);
    auto p=make(0);assert(!bridge.take(p));
    bridge.request(make(1));bridge.request(make(2));
    assert(bridge.snapshot().n==2);
    assert(bridge.take(p)&&p.n==2);assert(!bridge.take(p));
    bridge.publish(make(3));assert(bridge.snapshot().n==3);
    bridge.request(make(4));bridge.publish(make(5));
    assert(bridge.snapshot().n==4);assert(bridge.take(p)&&p.n==4);
    bridge.publish(make(6));assert(bridge.snapshot().n==6);
    constexpr unsigned N=500000;
    std::atomic<bool> done{false};unsigned accepted=0;
    std::thread audio([&]{Patch q=make(6);unsigned last=0;
        do {
            if(bridge.take(q)){check(q);assert(q.n>last);last=q.n;++accepted;}
            bridge.publish(make(q.n));
        }while(!done.load(std::memory_order_acquire));
        if(bridge.take(q)){check(q);assert(q.n>last);++accepted;}
        assert(q.n==N+6);bridge.publish(make(q.n));
    });
    std::thread reader([&]{unsigned last=0;do{auto s=bridge.snapshot();check(s);assert(s.n>=last);last=s.n;}while(!done.load(std::memory_order_acquire));});
    for(unsigned i=7;i<=N+6;++i){bridge.request(make(i));auto s=bridge.snapshot();check(s);assert(s.n==i);}
    done.store(true,std::memory_order_release);audio.join();reader.join();
    assert(bridge.snapshot().n==N+6);assert(accepted>0);
    std::printf("PASS %u restores; %u consumed (coalescing expected)\n",N,accepted);
}
