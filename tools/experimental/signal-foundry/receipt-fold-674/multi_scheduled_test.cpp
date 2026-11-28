#include "multi_scheduled.hpp"
#include <chrono>
#include <cstdlib>
#include <iostream>
#include <limits>
namespace mr=mhac::receipt::multi;
static void require(bool ok){if(!ok){std::cerr<<"scheduled multi regression failed\n";std::exit(1);}}
static bool same(const mr::Config& a,const mr::Config& b){return mr::save(a)==mr::save(b);}
template<class T> static void exercise(double rate,unsigned block){
    mr::Scheduled e;mr::Live oracle;
    require(e.prepare(rate)&&oracle.prepare(rate));
    const unsigned period=std::max(32u,static_cast<unsigned>(std::ceil(rate*.001)));
    require(e.period()==period);
    mr::Config p{8,128,3,5,mr::Contract::balanced,17,42,false,.8};
    require(e.request(p)&&oracle.apply(p));e.reset();oracle.reset();
    unsigned pos=0;std::uint64_t key=42;
    for(unsigned offset=0;offset<48000;offset+=block){
        for(unsigned j=0;j<std::min(block,48000-offset);++j){
            const unsigned i=offset+j;key=mhac::receipt::randomized::hash(key);
            if(i%7999==0){e.reset();oracle.apply(e.requested());oracle.reset();pos=0;}
            if(i<12000)++p.geometry;
            else {p.bits=3+static_cast<unsigned>(key%6);p.pairs=static_cast<unsigned>((key>>8)%((1u<<p.bits)/2+1));
                p.budget=static_cast<unsigned>((key>>16)%(p.bits+1));p.contract=static_cast<mr::Contract>((key>>24)%4);
                p.geometry=static_cast<std::uint32_t>(key>>32);p.seed=static_cast<std::uint32_t>(key);p.epoch_ms=5+static_cast<unsigned>(key%996);}
            p.wet=double(key%101)/100;p.bypass=(key&256)!=0;
            require(e.request(p));
            if(i%101==0){auto bad=p;bad.bits=9;require(!e.request(bad)&&same(e.requested(),p));}
            auto expected=pos%period==0?p:oracle.config();expected.wet=p.wet;expected.bypass=p.bypass;
            require(oracle.apply(expected));
            T l=static_cast<T>(double(i%256)/128-.997),r=static_cast<T>(double((i*17)%256)/128-.997);
            if(i%109==0)l=std::numeric_limits<T>::infinity();
            if(i%113==0)r=std::numeric_limits<T>::quiet_NaN();
            T x=l,y=r;e.frame(l,r);oracle.frame(x,y);
            require(l==x&&r==y&&std::abs(l)<=1&&std::abs(r)<=1&&same(e.active(),expected));
            ++pos;require(e.until_boundary()==(period-pos%period)%period);
        }
    }
    auto saved=mr::save(e.requested());mr::Config restored;
    require(mr::load(saved.data(),saved.size(),restored)&&same(restored,e.requested()));
    require(!e.prepare(std::numeric_limits<double>::quiet_NaN())&&e.period()==period);
    e.reset();require(same(e.active(),restored));
    for(unsigned i=0;i<period*2;++i){T l=0,r=0;e.frame(l,r);require(l==0&&r==0);}
}
static void timing(){
    constexpr unsigned blocks=1500,size=32;constexpr double rate=48000,deadline=size/rate;
    mr::Scheduled e;require(e.prepare(rate));mr::Config p{8,128,3,5,mr::Contract::balanced,17,42,false,.8};
    require(e.request(p));e.reset();std::array<double,blocks> dt{};double sum=0;unsigned misses=0,commits=0;
    for(unsigned b=0;b<blocks;++b){const auto start=std::chrono::steady_clock::now();
        for(unsigned i=0;i<size;++i){++p.geometry;require(e.request(p));const auto old=e.active().geometry;
            double l=.31,r=-.47;e.frame(l,r);sum+=l+r;commits+=old!=e.active().geometry?1u:0u;}
        dt[b]=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();misses+=dt[b]>deadline?1u:0u;
    }
    require(commits==1000);std::sort(dt.begin(),dt.end());
    std::cout<<"requests=48000 commits="<<commits<<" p50_us="<<dt[blocks/2]*1e6<<" p99_us="<<dt[blocks*99/100]*1e6<<" max_us="<<dt.back()*1e6<<" deadline_us="<<deadline*1e6<<" misses="<<misses<<" checksum="<<sum<<'\n';
}
int main(){for(double rate:{1000.,44100.,48000.,96000.,2000000.})for(unsigned block:{1u,32u,257u}){exercise<float>(rate,block);exercise<double>(rate,block);}
    std::cout<<"exact_oracle_stereo_frames=1440000\n";timing();}
