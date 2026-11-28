// Negative witness only: the original direct adapter state access is deliberately racy.
#include "freeze.hpp"
#include <atomic>
#include <thread>
#include <iostream>
int main(){mhac::freeze::Engine e;std::atomic<bool> go{false};std::thread state([&]{while(!go.load(std::memory_order_acquire)){};for(int i=0;i<100000;i++){auto p=mhac::freeze::defaults;p[mhac::freeze::Rate]=double(i%100)/100.;e.restore(p);}});go.store(true,std::memory_order_release);double sum=0.;for(int i=0;i<100000;i++)sum+=e.nextGain();state.join();std::cout<<sum<<'\n';}
