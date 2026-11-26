#include "control.hpp"
#include <iostream>
#define CHECK(x) do{if(!(x)){std::cerr<<"failure line "<<__LINE__<<": "<<#x<<'\n';return 1;}}while(0)
int main(){
    using namespace guest::control;
    auto p=defaults;p[7]=1;p[8]=1;auto bytes=encode(p);Params q{};
    CHECK(decode(bytes.data(),bytes.size(),q)&&encode(q)==bytes);
    auto old=bytes;old[3]='1';CHECK(decode(old.data(),36,q)&&q[7]==1&&q[8]==0);
    CHECK(!decode(old.data(),40,q));CHECK(!decode(bytes.data(),36,q));
    old[3]='2';CHECK(decode(old.data(),40,q)&&q[8]==1&&q[9]==0&&q[10]==.5);
    guest::SpectralBank bank;bank.prepare(48000,440,{0,0,0,0});
    for(unsigned i=1;i<=48000;++i)CHECK(std::abs(bank.tick()-std::sin(2*guest::pi*880*i/48000))<1e-10);
    bank.prepare(1000,440,{0,7,3,10});for(unsigned i=0;i<1000;++i)CHECK(bank.tick()==0);
    // Four independent partials agree with the direct sinusoidal sum.
    bank.prepare(48000,220,{0,7,3,10});
    for(unsigned i=1;i<=48000;++i){double expected=0;for(int st:{0,7,3,10})expected+=.25*std::sin(2*guest::pi*220*std::exp2((st+12)/12.)*i/48000);CHECK(std::abs(bank.tick()-expected)<1e-10);}
    unsigned long long prefix=0,continuation=0;
    for(double sr:{1000.,1234.568,8000.,44100.,48000.,96000.,192000.,1234567.8,2000000.}){
        Engine melodic,spectral,plain,cited;
        for(auto* e:{&melodic,&spectral,&plain,&cited}){CHECK(e->prepare(sr));e->parameter(4,1);e->parameter(7,1);}
        spectral.parameter(8,1);cited.parameter(8,1);cited.parameter(6,1);plain.parameter(7,0);plain.parameter(8,1);
        for(auto* e:{&melodic,&spectral,&plain,&cited})CHECK(e->on(1,36,0,.8));
        const auto boundary=4*unsigned(std::lround(sr/12));bool distinct=false;
        for(unsigned i=0;i<boundary*2;++i){
            auto a=melodic.tick(),b=spectral.tick(),c=plain.tick(),d=cited.tick();
            CHECK(a.base==b.base&&b.base==c.base&&b.counter==d.counter&&b.right==d.right&&c.counter==0);
            CHECK(std::isfinite(b.right)&&std::abs(b.right)<=.52);
            if(i<boundary){CHECK(a.right==b.right&&b.right==c.right);++prefix;}
            else{distinct|=a.counter!=b.counter;++continuation;}
        }
        CHECK(distinct);
        spectral.parameter(8,0); // Onset latch: existing spectral voice is unchanged.
        for(unsigned i=0;i<unsigned(sr*.01)+1;++i)CHECK(spectral.tick().right==cited.tick().right);
        for(auto* e:{&melodic,&spectral,&plain,&cited}){e->off(1);for(unsigned i=0;i<unsigned(sr*.032)+2;++i)e->tick();CHECK(e->tick().right==0);}
        spectral.restore(p);for(int i=0;i<8;++i)CHECK(spectral.on(i,127,1200,1));
        for(unsigned i=0;i<4*unsigned(std::lround(sr/4))+16;++i){auto f=spectral.tick();CHECK(std::isfinite(f.right)&&std::abs(f.right)<=.52);}
        spectral.reset();CHECK(spectral.tick().right==0);
    }
    std::cout<<"PASS: GO01 neutral migration, GO02 migration, GO03 roundtrip, direct partials and Nyquist guard; "<<prefix<<" exact prefix and "<<continuation<<" continuation frames at nine rates\n";
}
