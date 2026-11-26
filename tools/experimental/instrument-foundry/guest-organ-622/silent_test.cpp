#include "guest.hpp"
#include <iostream>
#define CHECK(x) do{if(!(x)){std::cerr<<"failure line "<<__LINE__<<": "<<#x<<'\n';return 1;}}while(0)
int main(){
    unsigned long long samples=0;
    for(double sr:{1000.,1234.568,8000.,44100.,48000.,96000.,192000.,1234567.8,2000000.}){
        for(double root:{55.,220.,880.,10000.})for(double depth:{0.,.5,1.}){
            const std::array<int,4> motif{-12,7,3,12};
            guest::FmBank a,b;guest::SpectralBank c,d;
            a.prepare(sr,root,motif,depth);b.prepare(sr,root,motif,depth);
            c.prepare(sr,root,motif);d.prepare(sr,root,motif);
            for(unsigned i=0;i<16384;++i){
                const bool audible=(i%257>=173)&&(i%11!=0);
                const double x=a.tick(),y=b.tick(audible),z=c.tick(),w=d.tick(audible);
                CHECK(y==(audible?x:0.));CHECK(w==(audible?z:0.));++samples;
            }
            CHECK(a.tick()==b.tick());CHECK(c.tick()==d.tick());
        }
    }
    std::cout<<"PASS: "<<samples<<" paired bank frames, signed FM phases, repeated silent/active transitions and nine rates\n";
}
