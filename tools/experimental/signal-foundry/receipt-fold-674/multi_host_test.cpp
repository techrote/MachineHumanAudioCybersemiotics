#include "multi_host.hpp"
#include <cstdlib>
#include <iostream>
#include <fstream>
#include <thread>
#include <chrono>
namespace r=mhac::receipt;
namespace h=r::multi_host;
namespace b=r::balanced_host;
namespace m=r::multi;
static void check(bool ok){if(!ok){std::cerr<<"multi host regression failed\n";std::abort();}}
static h::Patch patch(unsigned i){h::Patch p;p.legacy.action=r::unrank(i%28);p.legacy.mode=static_cast<r::Mode>(i%4);
    p.legacy.wet=(i%101)/100.;p.legacy.bypass=i%17==0;p.bits=3+i%6;p.budget=i%9;p.a=i%256;p.b=(i*7)%256;
    p.fine=i%2!=0;p.balanced=i%3!=0;p.epoch=5+i%996;p.seed=(i*71)%65536;
    p.multi=i%5!=0;p.multiBits=3+(i/3)%6;p.pairs=i%129;p.multiBudget=(i/7)%9;p.multiEpoch=5+(i*3)%996;
    p.geometry=(i*17)%65536;p.multiSeed=(i*97)%65536;p.multiContract=static_cast<m::Contract>((i/11)%4);return p;}
static void state(){for(unsigned i=0;i<10000;++i){auto p=patch(i);auto s=h::save(p);h::Patch q;
    check(h::load(s.data(),s.size(),q)&&h::save(q)==s);h::Patch v;
    for(unsigned k=0;k<h::count;++k)check(h::control(v,k,h::normalized(p,k)));
    check(h::save(v)==s);auto old=b::save(p);check(h::load(old.data(),old.size(),q)&&!q.multi&&b::save(q)==old);
    auto prior=h::save(q);auto bad=s;bad[27]|=128;check(!h::load(bad.data(),bad.size(),q)&&h::save(q)==prior);
    check(!h::load(s.data(),27,q)&&h::save(q)==prior);check(!h::control(q,h::MultiBits,std::numeric_limits<double>::infinity()));}
    for(unsigned i=0;i<28;++i){auto p=patch(i);h::Patch q;b::Patch ref;auto a=r::save(p.legacy);auto c=r::resolution::save(b::e::config(p));auto d=b::e::save(p);
        check(h::load(a.data(),a.size(),q)&&b::load(a.data(),a.size(),ref)&&!q.multi&&b::save(q)==b::save(ref));
        check(h::load(c.data(),c.size(),q)&&b::load(c.data(),c.size(),ref)&&!q.multi&&b::save(q)==b::save(ref));
        check(h::load(d.data(),d.size(),q)&&b::load(d.data(),d.size(),ref)&&!q.multi&&b::save(q)==b::save(ref));}
    std::cout<<"RF05 roundtrips=10000 normalized rebuilds=10000 RF04 migrations=10000 RF01/02/03 migrations=84 malformed=20000\n";
}
template<class T> static void stream(double rate){h::Host a,c;b::Host old;m::Scheduled oracle;
    check(a.prepare(rate)&&c.prepare(rate)&&old.prepare(rate)&&oracle.prepare(rate));
    auto p=patch(1);p.multi=false;check(a.apply(p)&&old.apply(p));a.reset();old.reset();
    for(unsigned i=0;i<12000;++i){if(i%97==0){p=patch(i);p.multi=false;check(a.apply(p)&&old.apply(p));}
        T l=static_cast<T>(std::sin(i*.03)),rr=static_cast<T>(std::cos(i*.07)),x=l,y=rr;a.frame(l,rr);old.frame(x,y);check(l==x&&rr==y);}
    p=patch(7);p.multi=true;check(a.apply(p)&&oracle.request(h::config(p)));a.reset();oracle.reset();
    for(unsigned i=0;i<12000;++i){p=patch(i);p.multi=true;check(a.apply(p)&&oracle.request(h::config(p)));
        T l=static_cast<T>(std::sin(i*.03)),rr=static_cast<T>(std::cos(i*.07)),x=l,y=rr;
        a.frame(l,rr);oracle.frame(x,y);check(l==x&&rr==y);}
    p=patch(7);check(a.apply(p)&&c.apply(p));a.reset();c.reset();unsigned i=0;
    while(i<12000){const unsigned end=std::min(12000u,i+257);c.begin();
        for(;i<end;++i){a.begin();if(i%37==0){p=patch(i);check(a.apply(p)&&c.apply(p));}
            T l=static_cast<T>(std::sin(i*.03)),rr=static_cast<T>(std::cos(i*.07)),x=l,y=rr;
            if(i%113==0)l=x=std::numeric_limits<T>::infinity();
            a.frame(l,rr);c.frame(x,y);check(l==x&&rr==y&&std::abs(l)<=1&&std::abs(rr)<=1);a.end();}c.end();}
    p.multi=true;p.legacy.bypass=true;check(a.request(p));a.begin();a.end();h::Patch q;check(a.snapshot(q)&&h::save(q)==h::save(p));
    for(unsigned j=0;j<10001;++j){T l=T(.7),rr=T(-.4);a.frame(l,rr);if(j==10000)check(l==T(.7)&&rr==T(-.4));}
    T l=0,rr=std::numeric_limits<T>::infinity();a.frame(l,rr);check(l==0&&rr==0);
}
static void crossfade(){h::Live a;b::Live old;m::Scheduled oracle;h::Patch p;p.legacy.wet=1.;p.multiBits=3;p.pairs=4;p.multiBudget=0;
    check(a.prepare(48000)&&old.prepare(48000)&&oracle.prepare(48000));check(a.apply(p)&&old.apply(p)&&oracle.request(h::config(p)));
    a.reset();old.reset();oracle.reset();unsigned mix=0;unsigned distinct=0;
    for(unsigned i=0;i<2000;++i){if(i==300||i==410||i==470||i==1200){p.multi=!p.multi;check(a.apply(p));}
        if(p.multi){if(mix<240)++mix;}else if(mix)--mix;
        double l=.71,rr=-.63,x=l,y=rr,u=l,v=rr;a.frame(l,rr);old.frame(x,y);oracle.frame(u,v);
        auto expected=[&](double aa,double zz){if(!mix||aa==zz)return aa;if(mix==240)return zz;const double f=double(mix)/240;return r::clean(aa*(1-f)+zz*f);};
        check(l==expected(x,u)&&rr==expected(y,v));if(x!=u||y!=v)++distinct;
    }check(distinct>500);std::cout<<"crossfade oracle frames=2000\n";
}
static void concurrency(){h::Host a;std::atomic<bool> done{false};std::thread audio([&]{while(!done.load()){a.begin();double l=.2,rr=-.4;a.frame(l,rr);a.end();}});
    unsigned busy=0;for(unsigned i=0;i<30000;++i){auto p=patch(i);check(a.request(p));h::Patch q;if(a.snapshot(q))check(h::save(q)==h::save(p));else ++busy;}
    done.store(true);audio.join();std::cout<<"state requests=30000 busy="<<busy<<'\n';}
static void timing(){constexpr unsigned blocks=1500,size=32;constexpr double rate=48000,deadline=size/rate;
    h::Host a;h::Patch p;p.multi=true;p.multiBits=8;p.pairs=128;p.multiBudget=3;p.multiEpoch=5;p.legacy.wet=.8;
    check(a.prepare(rate)&&a.apply(p));a.reset();std::array<double,blocks> dt{};double sum=0;unsigned misses=0;
    for(unsigned j=0;j<blocks;++j){const auto start=std::chrono::steady_clock::now();a.begin();
        for(unsigned i=0;i<size;++i){p.geometry=(p.geometry+1)%65536;check(a.apply(p));double l=.31,rr=-.47;a.frame(l,rr);sum+=l+rr;}
        a.end();dt[j]=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();misses+=dt[j]>deadline?1u:0u;}
    std::sort(dt.begin(),dt.end());std::cout<<"dense geometry blocks="<<blocks<<" p50_us="<<dt[blocks/2]*1e6<<" p99_us="<<dt[blocks*99/100]*1e6<<" max_us="<<dt.back()*1e6<<" misses="<<misses<<" checksum="<<sum<<'\n';
}
static void put(std::ofstream& f,unsigned v,unsigned n){for(unsigned i=0;i<n;++i)f.put(static_cast<char>(v>>(8*i)));}
static void render(const char* path,bool enabled){constexpr unsigned rate=48000,n=rate*4;std::ofstream f(path,std::ios::binary);check(bool(f));
    f.write("RIFF",4);put(f,36+n*4,4);f.write("WAVEfmt ",8);put(f,16,4);put(f,1,2);put(f,2,2);put(f,rate,4);put(f,rate*4,4);put(f,4,2);put(f,16,2);f.write("data",4);put(f,n*4,4);
    h::Host a;h::Patch p;p.legacy.wet=.8;p.balanced=true;p.bits=5;p.budget=1;p.multiBits=5;p.pairs=16;p.multiBudget=1;
    check(a.apply(p));a.reset();double peak=0,energy=0;for(unsigned i=0;i<n;++i){if(i==rate||i==2*rate||i==3*rate){p.multi=enabled&&i!=2*rate;check(a.apply(p));}
        const double t=double(i)/rate,env=std::max(0.,std::min({1.,t*100.,(3.9-t)*100.}));
        double l=env*(.65*std::sin(6.283185307179586*110*t)+.09*std::sin(6.283185307179586*331*t)),rr=env*.7*std::sin(6.283185307179586*165*t);
        a.frame(l,rr);peak=std::max({peak,std::abs(l),std::abs(rr)});energy+=l*l+rr*rr;
        put(f,static_cast<unsigned>(static_cast<int>(std::lround(l*32767))),2);put(f,static_cast<unsigned>(static_cast<int>(std::lround(rr*32767))),2);}
    check(bool(f));auto preset=h::save(p);std::ofstream pf(std::string(path)+".rf05",std::ios::binary);
    pf.write(reinterpret_cast<const char*>(preset.data()),static_cast<std::streamsize>(preset.size()));check(bool(pf));std::cout<<path<<" peak="<<peak<<" rms="<<std::sqrt(energy/(2*n))<<'\n';}
int main(int argc,char** argv){state();for(double rate:{1000.,44100.,48000.,96000.,192000.,2000000.}){stream<float>(rate);stream<double>(rate);}
    std::cout<<"legacy frames=144000 multi oracle frames=144000 partition frames=144000\n";crossfade();concurrency();timing();if(argc==3){render(argv[1],false);render(argv[2],true);}return 0;}
