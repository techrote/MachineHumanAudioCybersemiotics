#include "control.hpp"
#include <iostream>
#define CHECK(x) do{if(!(x)){std::cerr<<"failure line "<<__LINE__<<": "<<#x<<'\n';return 1;}}while(0)
int main(){
    using namespace guest::control;
    guest::FmBank bank;
    bank.prepare(48000,220,{0,7,3,10},0);
    for(unsigned i=1;i<=48000;++i){double t=2*guest::pi*i/48000;CHECK(std::abs(bank.tick()-.5*(std::sin(t*440)+std::sin(t*440*std::exp2(3./12))))<1e-10);}
    bank.prepare(1000,440,{0,7,3,10},0);for(unsigned i=0;i<1000;++i)CHECK(bank.tick()==0);
    // Independent J0..J3 values at index 2, cross-checked with SciPy.
    bank.prepare(48000,220,{0,7,3,10},1);
    const double reference[]{0.22389077914123562,0.5767248077568736,0.35283402861563773,0.12894324947440208};
    double norm=0;for(int k=-3;k<=3;++k)norm+=std::abs(reference[std::abs(k)]);
    for(unsigned i=1;i<=12000;++i){double expected=0;for(unsigned pair=0;pair<2;++pair){const int m[]{0,7,3,10};double c=440*std::exp2(m[2*pair]/12.),f=440*std::exp2(m[2*pair+1]/12.);for(int k=-3;k<=3;++k){double a=reference[std::abs(k)];if(k<0&&(-k)%2)a=-a;expected+=.5*a/norm*std::sin(2*guest::pi*(c+k*f)*i/48000);}}CHECK(std::abs(bank.tick()-expected)<1e-9);}
    Params p=defaults;p[7]=p[8]=p[9]=1;p[10]=.75;auto state=encode(p);Params q{};
    CHECK(decode(state.data(),state.size(),q)&&encode(q)==state);
    auto old=state;old[3]='2';CHECK(decode(old.data(),40,q)&&q[8]==1&&q[9]==0&&q[10]==.5);
    old[3]='1';CHECK(decode(old.data(),36,q)&&q[8]==0&&q[9]==0&&q[10]==.5);
    unsigned long long prefix=0,after=0;
    for(double sr:{1000.,1234.568,8000.,44100.,48000.,96000.,192000.,1234567.8,2000000.}){
        Engine fm,cited,replay,spectral;
        for(auto* e:{&fm,&cited,&replay,&spectral}){CHECK(e->prepare(sr));e->parameter(4,1);e->parameter(7,1);e->parameter(8,1);}
        fm.parameter(9,1);cited.parameter(9,1);cited.parameter(6,1);replay.parameter(7,0);
        for(auto* e:{&fm,&cited,&replay,&spectral})CHECK(e->on(1,36,0,.8));
        unsigned boundary=4*unsigned(std::lround(sr/12));bool distinct=false;
        for(unsigned i=0;i<boundary*2;++i){auto a=fm.tick(),b=cited.tick(),c=replay.tick(),d=spectral.tick();CHECK(a.base==b.base&&a.base==c.base&&a.base==d.base&&a.right==b.right&&c.counter==0);CHECK(std::isfinite(a.right)&&std::abs(a.right)<=.52);if(i<boundary){CHECK(a.right==c.right&&a.right==d.right);++prefix;}else{distinct|=a.counter!=d.counter;++after;}}
        CHECK(distinct);fm.parameter(9,0);fm.parameter(10,0);
        for(unsigned i=0;i<unsigned(sr*.01)+1;++i)CHECK(fm.tick().right==cited.tick().right);
        for(auto* e:{&fm,&cited,&replay,&spectral}){e->off(1);for(unsigned i=0;i<unsigned(sr*.032)+2;++i)e->tick();CHECK(e->tick().right==0);}
        fm.restore(p);for(int i=0;i<8;++i)CHECK(fm.on(i,127,1200,1));
        for(unsigned i=0;i<4*unsigned(std::lround(sr/4))+16;++i){auto f=fm.tick();CHECK(std::isfinite(f.right)&&std::abs(f.right)<=.52);}
        fm.reset();CHECK(fm.tick().right==0);
    }
    std::cout<<"PASS: finite PM reference, GO01/02 migration, GO03 roundtrip, "<<prefix<<" exact prefix and "<<after<<" continuation frames at nine rates\n";
}
