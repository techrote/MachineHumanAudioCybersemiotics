#include "guest.hpp"
#include <chrono>
#include <cstring>
#include <iomanip>
#include <iostream>
#include <vector>
int main(){
    using Clock=std::chrono::steady_clock;
    std::vector<double> prefix,continuation;
    std::uint64_t hash=14695981039346656037ull;
    for(unsigned trial=0;trial<12;++trial){
        guest::Engine e;if(!e.prepare(48000))return 1;
        guest::Patch p;p.adopt=p.fm=true;p.fmDepth=1.;e.configure(p);
        for(int i=0;i<8;++i)if(!e.on(i,48+i,0,.8))return 2;
        for(unsigned block=0;block<1500;++block){
            std::array<guest::Frame,64> frames{};
            auto t=Clock::now();for(auto& f:frames)f=e.tick();auto elapsed=std::chrono::duration<double,std::micro>(Clock::now()-t).count();
            (block<750?prefix:continuation).push_back(elapsed);
            for(const auto& f:frames)for(double x:{f.left,f.right,f.base,f.counter}){std::uint64_t bits;std::memcpy(&bits,&x,8);hash=(hash^bits)*1099511628211ull;}
        }
    }
    for(auto* v:{&prefix,&continuation}){std::sort(v->begin(),v->end());std::cout<<(v==&prefix?"opening":"continuation")<<" n="<<v->size()<<" median_us="<<(*v)[v->size()/2]<<" p99_us="<<(*v)[v->size()*99/100]<<" max_us="<<v->back()<<'\n';}
    std::cout<<"frame_hash="<<std::hex<<hash<<'\n';
}
