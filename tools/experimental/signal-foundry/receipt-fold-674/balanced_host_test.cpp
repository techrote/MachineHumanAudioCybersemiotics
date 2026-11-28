#include "balanced_host.hpp"
#include <cstdlib>
#include <iostream>
#include <fstream>
#include <thread>
#include <chrono>
namespace r=mhac::receipt;
namespace e=r::extended;
namespace b=r::balanced_host;
namespace z=r::randomized;
static void check(bool ok){if(!ok){std::cerr<<"balanced host regression failed\n";std::abort();}}
static b::Patch patch(unsigned i){b::Patch p;p.legacy.action=r::unrank(i%28);p.legacy.mode=static_cast<r::Mode>(i%4);
    p.legacy.wet=(i%101)/100.;p.bits=3+i%6;p.budget=i%9;p.a=i%256;p.b=(i*7)%256;p.fine=i%2!=0;
    p.balanced=i%3!=0;p.epoch=5+i%996;p.seed=(i*71)%65536;return p;}
static void state(){for(unsigned i=0;i<10000;++i){auto p=patch(i);auto s=b::save(p);b::Patch q;
    check(b::load(s.data(),s.size(),q)&&b::save(q)==s);b::Patch v;
    for(unsigned k=0;k<b::count;++k)check(b::control(v,k,b::normalized(p,k)));
    check(b::save(v)==s);auto old=e::save(p);check(b::load(old.data(),old.size(),q)&&!q.balanced&&q.epoch==25&&q.seed==0&&e::save(q)==old);
    auto bad=s;bad[11]|=128;check(!b::load(bad.data(),bad.size(),q)&&e::save(q)==old);check(!b::load(s.data(),19,q));}
    for(unsigned i=0;i<28;++i){auto p=patch(i);b::Patch q;auto s=r::save(p.legacy);check(b::load(s.data(),s.size(),q)&&r::save(q.legacy)==s&&!q.balanced);
        auto c=e::config(p);auto x=r::resolution::save(c);check(b::load(x.data(),x.size(),q)&&r::resolution::save(e::config(q))==x&&!q.balanced);}
    std::cout<<"RF04 roundtrips=10000 normalized rebuilds=10000 RF03 migrations=10000 RF01/RF02 migrations=56 malformed=20000\n";
}
template<class T> static void stream(double rate){b::Host a,bh;e::Host old;check(a.prepare(rate)&&bh.prepare(rate)&&old.prepare(rate));
    for(unsigned i=0;i<16000;++i){if(i%89==0){auto p=patch(i);p.balanced=false;check(a.apply(p)&&old.apply(p));}
        T l=static_cast<T>(std::sin(i*.03)),rr=static_cast<T>(std::cos(i*.07)),x=l,y=rr;a.frame(l,rr);old.frame(x,y);check(l==x&&rr==y);}
    auto p=patch(13);p.balanced=true;p.epoch=5;p.legacy.wet=1;check(a.apply(p)&&bh.apply(p));a.reset();bh.reset();
    z::Live oracle;check(oracle.prepare(rate));auto c=e::config(p);check(oracle.apply({c.bits,c.lo,c.hi,c.budget,p.epoch,p.seed,true,c.bypass,c.wet}));oracle.reset();
    for(unsigned i=0;i<16000;++i){T l=static_cast<T>(std::sin(i*.03)),rr=static_cast<T>(std::cos(i*.07)),x=l,y=rr,u=l,v=rr;
        a.frame(l,rr);bh.frame(x,y);oracle.frame(u,v);check(l==x&&rr==y&&std::abs(l-u)<=1e-7&&std::abs(rr-v)<=1e-7);}
    // Absolute offset controls, two different block partitions and state restore via mailbox.
    a.reset();bh.reset();unsigned i=0;while(i<16000){const unsigned end=std::min(16000u,i+257);bh.begin();
        for(;i<end;++i){a.begin();if(i%113==0){p=patch(i);check(a.apply(p)&&bh.apply(p));}
            T l=static_cast<T>(std::sin(i*.03)),rr=static_cast<T>(std::cos(i*.07)),x=l,y=rr;
            a.frame(l,rr);bh.frame(x,y);check(l==x&&rr==y&&std::abs(l)<=1&&std::abs(rr)<=1);a.end();}bh.end();}
    p.balanced=true;p.legacy.bypass=true;check(a.request(p));a.begin();a.end();b::Patch q;check(a.snapshot(q)&&b::save(q)==b::save(p));
    for(unsigned j=0;j<10001;++j){T l=T(.7),rr=T(-.4);a.frame(l,rr);if(j==10000)check(l==T(.7)&&rr==T(-.4));}
    T l=0,rr=std::numeric_limits<T>::infinity();a.frame(l,rr);check(l==0&&rr==0);
}
static void concurrency(){b::Host h;std::atomic<bool> done{false};std::thread audio([&]{while(!done.load()){h.begin();double l=.2,rr=-.4;h.frame(l,rr);h.end();}});
    unsigned busy=0;for(unsigned i=0;i<30000;++i){auto p=patch(i);check(h.request(p));b::Patch q;if(h.snapshot(q))check(b::save(q)==b::save(p));else ++busy;}
    done.store(true);audio.join();std::cout<<"state requests=30000 busy="<<busy<<'\n';}
static void put(std::ofstream& f,unsigned v,unsigned n){for(unsigned i=0;i<n;++i)f.put(static_cast<char>(v>>(8*i)));}
static void render(const char* path,bool enabled){constexpr unsigned rate=48000,n=rate*4;std::ofstream f(path,std::ios::binary);check(bool(f));
    f.write("RIFF",4);put(f,36+n*4,4);f.write("WAVEfmt ",8);put(f,16,4);put(f,1,2);put(f,2,2);put(f,rate,4);put(f,rate*4,4);put(f,4,2);put(f,16,2);f.write("data",4);put(f,n*4,4);
    b::Host a;b::Patch p;p.bits=4;p.fine=true;p.a=32;p.b=160;p.budget=2;p.legacy.mode=r::Mode::fixed;p.legacy.wet=.8;p.epoch=31;p.seed=42;p.balanced=enabled;
    check(a.apply(p));double peak=0,energy=0;for(unsigned i=0;i<n;++i){if(i==rate||i==2*rate||i==3*rate){++p.bits;++p.budget;p.epoch+=17;check(a.apply(p));}
        const double t=double(i)/rate,env=std::max(0.,std::min({1.,t*100.,(3.9-t)*100.}));
        double l=env*(.65*std::sin(6.283185307179586*110*t)+.09*std::sin(6.283185307179586*331*t)),rr=env*.7*std::sin(6.283185307179586*165*t);
        a.frame(l,rr);peak=std::max({peak,std::abs(l),std::abs(rr)});energy+=l*l+rr*rr;
        put(f,static_cast<unsigned>(static_cast<int>(std::lround(l*32767))),2);put(f,static_cast<unsigned>(static_cast<int>(std::lround(rr*32767))),2);}
    check(bool(f));std::cout<<path<<" peak="<<peak<<" rms="<<std::sqrt(energy/(2*n))<<'\n';}
int main(int argc,char** argv){state();for(double rate:{1000.,44100.,48000.,96000.,192000.,2000000.}){stream<float>(rate);stream<double>(rate);}
    std::cout<<"legacy frames=192000 native oracle frames=192000 partition frames=192000\n";concurrency();if(argc==3){render(argv[1],false);render(argv[2],true);}return 0;}
