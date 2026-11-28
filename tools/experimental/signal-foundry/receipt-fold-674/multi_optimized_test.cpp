#include "multi_receipt.hpp"
#include <chrono>
#include <cstdlib>
#include <iostream>
#include <limits>
#include <type_traits>
namespace mr=mhac::receipt::multi;
namespace rr=mhac::receipt::randomized;
namespace rs=mhac::receipt::resolution;
static void require(bool ok){if(!ok){std::cerr<<"optimized multi equivalence failed\n";std::exit(1);}}
// Deliberately retain the slow encoder/decoder oracle and the old ramp order.
class Reference {
    using Table=std::array<double,256>;
    mr::Config cfg{};mr::Matching matching=mr::geometry(cfg);
    rr::Schedule schedule;rr::Draw draw{1,false};
    Table from{},to{};double rate=48000,wet=0;
    unsigned ramp=240,left=0,epoch=1200,until=1200;
    double at(unsigned i) const noexcept{return left?from[i]+(to[i]-from[i])*double(ramp-left)/ramp:to[i];}
    Table table() const noexcept {
        Table t{};mr::Receipt receipt{cfg.contract,cfg.budget,mr::preview_digit(matching),draw};
        for(unsigned i=0;i<256;++i){const unsigned q=i>>(8-cfg.bits);
            t[i]=rs::amplitude(receipt.decode(matching,matching.collapse(q),receipt.tag(matching,q)),cfg.bits);}
        return t;
    }
    void target() noexcept {const auto t=table();if(t==to)return;for(unsigned i=0;i<256;++i)from[i]=at(i);to=t;left=ramp;}
    void restart() noexcept {schedule.reset(cfg.bits,cfg.seed);draw=schedule.next();epoch=static_cast<unsigned>(std::ceil(rate*cfg.epoch_ms*.001));until=epoch;}
    double sample(double in) const noexcept {const double x=mhac::receipt::clean(in);if(x==0||wet==0)return x;
        const unsigned q=std::min(255u,static_cast<unsigned>((x+1)*128));return mhac::receipt::clean(x*(1-wet)+at(q)*wet);}
public:
    Reference(){reset();}
    void prepare(double sr){rate=sr;ramp=static_cast<unsigned>(std::ceil(rate*.005));reset();}
    void reset(){restart();from=to=table();left=0;wet=0;}
    void apply(const mr::Config& p){const bool clock=p.bits!=cfg.bits||p.seed!=cfg.seed||p.epoch_ms!=cfg.epoch_ms;
        const bool geom=p.bits!=cfg.bits||p.pairs!=cfg.pairs||p.geometry!=cfg.geometry;
        const bool law=clock||geom||p.budget!=cfg.budget||p.contract!=cfg.contract;
        cfg=p;if(geom)matching=mr::geometry(cfg);if(clock)restart();if(law)target();}
    template<class T>void frame(T& l,T& r){if(!until){draw=schedule.next();until=epoch;if(cfg.contract==mr::Contract::balanced)target();}
        --until;if(left)--left;const double dest=cfg.bypass?0:cfg.wet,step=1.0/ramp;wet+=std::clamp(dest-wet,-step,step);
        l=static_cast<T>(sample(l));r=static_cast<T>(sample(r));}
};
template<class T>static std::uint64_t exercise(double rate){
    mr::Live fast;Reference slow;require(fast.prepare(rate));slow.prepare(rate);
    mr::Config p{8,128,3,5,mr::Contract::balanced,17,42,false,.8};
    require(fast.apply(p));slow.apply(p);fast.reset();slow.reset();
    std::uint64_t key=1234,frames=0;
    for(unsigned i=0;i<48000;++i){
        key=rr::hash(key);
        // Change geometry every frame in the first section, then mix clock,
        // resolution, budget, contract, bypass and wet changes at odd offsets.
        if(i<4096)++p.geometry;
        else if(i%17==0){p.bits=3+static_cast<unsigned>(key%6);p.pairs=static_cast<unsigned>((key>>8)%((1u<<p.bits)/2+1));p.budget=static_cast<unsigned>((key>>16)%(p.bits+1));
            p.contract=static_cast<mr::Contract>((key>>24)%4);p.geometry=static_cast<std::uint32_t>(key>>32);}
        if(i%257==0){p.seed=static_cast<std::uint32_t>(key);p.epoch_ms=5+static_cast<unsigned>(key%996);}
        if(i%61==0){p.wet=double(key%101)/100;p.bypass=(key&256)!=0;}
        if(i%4093==0){fast.reset();slow.reset();}
        require(fast.apply(p));slow.apply(p);
        T l=static_cast<T>(double(i%256)/128-.997),r=static_cast<T>(double((i*17)%256)/128-.997);
        if(i%109==0)l=std::numeric_limits<T>::infinity();
        if(i%113==0)r=std::numeric_limits<T>::quiet_NaN();
        T x=l,y=r;fast.frame(l,r);slow.frame(x,y);require(l==x&&r==y&&std::abs(l)<=1&&std::abs(r)<=1);++frames;
    }
    return frames;
}
int main(){std::uint64_t frames=0;for(double rate:{1000.,44100.,48000.,96000.,2000000.}){frames+=exercise<float>(rate);frames+=exercise<double>(rate);}
    std::cout<<"exact_reference_stereo_frames="<<frames<<'\n';}
