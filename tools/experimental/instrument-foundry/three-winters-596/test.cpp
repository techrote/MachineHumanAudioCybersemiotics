#include "winters.hpp"
#include <iostream>
#include <limits>
#include <cstdlib>
#define CHECK(x) do{if(!(x)){std::cerr<<"FAIL "<<__LINE__<<" "<<#x<<'\n';std::exit(1);}}while(false)
using namespace winters;
int main(){
    unsigned cases=0;
    for(int b=0;b<256;++b){
        Score s;for(int i=0;i<4;++i)s.edit(i,(b>>(2*i))&3);
        const auto initial=s.bank; s.hold();s.hold();s.edit(1,(initial[1]+1)%4);s.tick();
        CHECK(s.token(0)==initial[0]);CHECK(s.token(1)==initial[0]);CHECK(s.token(2)==initial[1]);
        s.release();CHECK(s.token(0)==(initial[1]+1)%4);CHECK(s.token(1)==initial[0]);CHECK(s.token(2)==s.token(0));s.tick();CHECK(s.token(1)==s.bank[1]);++cases;
    }
    for(double rate:{1000.,1234.5678,8000.,44100.,48000.,96000.,192000.,384000.,1234567.8,2000000.}){
        Engine a,b;CHECK(a.setup(rate));CHECK(b.setup(rate));CHECK(!a.setup(0));CHECK(!a.setup(std::numeric_limits<double>::infinity()));
        for(int n=0;n<4;++n){CHECK(a.noteOn(n,60+n*3,.8));CHECK(b.noteOn(n,60+n*3,.8));}
        CHECK(!a.noteOn(4,60,1));CHECK(!a.noteOn(0,60,1));CHECK(!a.noteOn(5,60,NAN));
        std::array<double,257> l{},r{},l2{},r2{};
        for(int block=0;block<8;++block){
            if(block==1){a.hold();b.hold();}if(block==2){a.edit(1,3);b.edit(1,3);}if(block==3){a.tick();b.tick();}if(block==4){a.release();b.release();}if(block==5){a.tick();b.tick();}
            a.process(l.data(),r.data(),257);b.process(l2.data(),r2.data(),1);b.process(l2.data()+1,r2.data()+1,63);b.process(l2.data()+64,r2.data()+64,193);
            CHECK(l==l2&&r==r2);for(unsigned i=0;i<257;++i){CHECK(std::isfinite(l[i])&&std::abs(l[i])<=.300001);CHECK(std::isfinite(r[i])&&std::abs(r[i])<=.300001);}
        }
        for(int n=0;n<4;++n){a.noteOff(n);b.noteOff(n);}for(unsigned i=0;i<unsigned(rate*.041)+2;++i){const auto s=a.sample();const auto t=b.sample();CHECK(s==t);}
        CHECK((a.sample()==std::array<double,3>{}));CHECK(a.noteOn(4,127,1));CHECK(b.noteOn(4,127,1));
        std::array<float,257> f{};a.process(f.data(),f.data(),257);b.process<double>(l.data(),nullptr,257);for(unsigned i=0;i<257;++i)CHECK(f[i]==static_cast<float>(l[i]));
        a.reset();CHECK((a.sample()==std::array<double,3>{}));
    }
    std::cout<<"PASS "<<cases<<" bank witnesses; 10 rates, block partition, capacity, release, mono float/double, bounds\n";
}
