#include "state.hpp"
#include <iostream>
#include <stdexcept>
#include <thread>
using namespace mhac;
void check(bool b){if(!b)throw std::runtime_error("state test failed");}
int main(){
 Params p=defaults,q{};check(decode(encode(p),q)&&p==q);
 auto bad=encode(p);bad[3]=2;check(!decode(bad,q)&&q==p);bad=encode(p);for(unsigned j=4;j<12;++j)bad[j]=255;check(!decode(bad,q)&&q==p);
 AtomicBank bank;uint64_t v=0;check(bank.tryRead(q,v)&&q==defaults&&v==0);
 p.fill(0.25);check(bank.write(p)==2&&bank.tryRead(q,v)&&v==2&&q==p);
 std::atomic<bool> done{false};std::thread writer([&]{for(unsigned n=0;n<100000;++n){Params a;a.fill((n&1)?0.75:0.25);bank.write(a);}done.store(true);});
 unsigned reads=0;bool coherent=true;while(!done.load()){if(bank.tryRead(q,v)){++reads;for(double a:q)if(a!=q[0]||(a!=0.25&&a!=0.75))coherent=false;}}
 writer.join();check(coherent);check(bank.tryRead(q,v)&&v==200002&&q[0]==0.75);std::cout<<"state codec and 100000 atomic publications passed; concurrent coherent reads "<<reads<<"\n";
}
