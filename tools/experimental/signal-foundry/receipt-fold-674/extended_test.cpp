#include "resolution_host.hpp"
#include <cstdlib>
#include <iostream>
#include <thread>
#include <chrono>
#include <fstream>
#include <string>
namespace r=mhac::receipt;
namespace e=r::extended;
namespace v=r::resolution;
static void check(bool b){if(!b){std::cerr<<"extended regression failed\n";std::abort();}}
static e::Patch pattern(unsigned i){e::Patch p;p.legacy={r::unrank(i%28),static_cast<r::Mode>(i%4),i%7==0,double(i%1009)/1009};
    p.bits=3+i%6;p.budget=i%9;p.a=i%256;p.b=(i*17)%256;p.fine=i%3!=0;return p;}
static void states(){
    for(unsigned bits=3;bits<=8;++bits)for(unsigned a=0;a<(1u<<bits);++a)for(unsigned b=a+1;b<(1u<<bits);++b){
        v::Config c{bits,a,b,bits,r::Mode::fixed,false,.327};auto s=v::save(c);e::Patch p;
        check(e::load(s.data(),s.size(),p)&&v::save(e::config(p))==s);
        auto x=e::save(p);e::Patch q;check(e::load(x.data(),x.size(),q)&&e::save(q)==x);
    }
    for(unsigned i=0;i<10008;++i){auto p=pattern(i);auto s=e::save(p);e::Patch q;check(e::load(s.data(),s.size(),q)&&e::save(q)==s);
        for(unsigned id=0;id<e::count;++id)check(e::control(q,id,e::normalized(p,id)));
        check(e::save(q)==s);auto bad=s;bad[4]=static_cast<std::uint8_t>(bad[4]|31u);
        check(!e::load(bad.data(),bad.size(),q)&&e::save(q)==s);
        check(!e::control(q,e::Wet,std::numeric_limits<double>::quiet_NaN())&&e::save(q)==s);
    }
    for(unsigned i=0;i<28;++i){r::Patch p{r::unrank(i),r::Mode::fixed,false,.61};auto s=r::save(p);e::Patch q;
        check(e::load(s.data(),s.size(),q)&&r::save(q.legacy)==s&&q.bits==3&&q.budget==1&&!q.fine);
        check(e::normalized(q,e::Action)==i/27.);}
    for(unsigned bits=3;bits<=8;++bits)for(unsigned a=0;a<256;++a)for(unsigned b=0;b<256;++b){e::Patch p;p.bits=bits;p.a=a;p.b=b;p.fine=true;check(v::valid(e::config(p)));}
}
template<class T> static void legacy(double rate){r::Host old;e::Host next;check(old.prepare(rate)&&next.prepare(rate));
    for(unsigned i=0;i<8192;++i){if(i%97==0){old.begin();next.begin();}
        if(i%13==0){const auto id=(i/13)%4;const double val=(i%101)/100.;check(old.set(id,val)&&next.set(id,val));}
        T l=static_cast<T>(std::sin(i*.031)),rr=static_cast<T>(std::cos(i*.017)),a=l,b=rr;old.frame(l,rr);next.frame(a,b);check(l==a&&rr==b);
        if(i%97==96){old.end();next.end();}}
}
template<class T> static void blocks(double rate){e::Host a,b;check(a.prepare(rate)&&b.prepare(rate));
    for(unsigned i=0;i<16384;++i){if(i%7==0)a.begin();if(i%251==0)b.begin();
        if(i%3==0){auto p=pattern(i);check(a.apply(p)&&b.apply(p));}
        T l=static_cast<T>(std::sin(i*.013)),r=static_cast<T>(std::cos(i*.047)),x=l,y=r;
        a.frame(l,r);b.frame(x,y);check(l==x&&r==y&&std::abs(l)<=1&&std::abs(r)<=1);
        if(i%7==6)a.end();
        if(i%251==250)b.end();}
    a.end();b.end();e::Patch p,q;check(a.snapshot(p)&&b.snapshot(q)&&e::save(p)==e::save(q));
    auto s=pattern(799);check(a.request(s)&&a.snapshot(p)&&e::save(s)==e::save(p));a.begin();a.end();check(e::save(a.patch())==e::save(s));
}
static void stress(){e::Host h;check(h.prepare(48000));std::atomic<bool> stop{false};std::atomic<unsigned> blocks{0};
    std::thread audio([&]{while(!stop.load()){h.begin();for(unsigned i=0;i<64;++i){double l=.9,r=0;h.frame(l,r);check(std::abs(l)<=1&&r==0);}h.end();++blocks;}});
    while(!blocks.load())std::this_thread::yield();
    unsigned busy=0;for(unsigned i=0;i<30000;++i){auto p=pattern(i);check(h.request(p));e::Patch q;if(h.snapshot(q))check(e::save(p)==e::save(q));else ++busy;}
    stop=true;audio.join();h.begin();h.end();e::Patch p;check(h.snapshot(p)&&e::save(p)==e::save(pattern(29999)));
    std::cout<<"30000 concurrent requests; "<<busy<<" busy saves; "<<blocks.load()<<" blocks\n";
}
static void benchmark(){e::Host h;check(h.prepare(48000));double sum=0;
    constexpr unsigned samples=480000;auto t=std::chrono::steady_clock::now();
    for(unsigned i=0;i<samples;++i){auto p=pattern(i);p.bits=8;p.fine=true;p.legacy.mode=r::Mode::absent;check(h.apply(p));double l=.87,r=-.71;h.frame(l,r);sum+=l+r;}
    const auto elapsed=std::chrono::duration<double>(std::chrono::steady_clock::now()-t).count();
    std::cout<<"dense law automation: "<<samples<<" stereo frames in "<<elapsed<<" s; checksum "<<sum<<"\n";
}
static void put(std::ofstream& f,unsigned v,unsigned n){for(unsigned j=0;j<n;++j)f.put(static_cast<char>((v>>(8*j))&255));}
static void render(bool fine,const char* name){constexpr unsigned n=48000*4;std::ofstream f(name,std::ios::binary);
    f.write("RIFF",4);put(f,36+4*n,4);f.write("WAVEfmt ",8);put(f,16,4);put(f,1,2);put(f,2,2);put(f,48000,4);put(f,192000,4);put(f,4,2);put(f,16,2);f.write("data",4);put(f,4*n,4);
    e::Host h;check(h.prepare(48000));e::Patch p;p.fine=fine;p.legacy.mode=r::Mode::absent;p.legacy.wet=.8;
    for(unsigned i=0;i<n;++i){if(i%48000==0){p.bits=5+i/48000;p.a=96;p.b=175;check(h.apply(p));}
        const double t=i/48000.,env=std::max(0.,std::min({1.,t*40,(3.9-t)*40}));double l=env*.8*std::sin(6.283185307179586*110*t),rr=env*.8*std::sin(6.283185307179586*165*t);
        h.frame(l,rr);put(f,static_cast<unsigned>(static_cast<int>(l*32767)),2);put(f,static_cast<unsigned>(static_cast<int>(rr*32767)),2);}
    check(bool(f));}
int main(int argc,char** argv){states();for(double rate:{1000.,1234.568,44100.,48000.,192000.,384000.,1234567.8,2000000.}){legacy<float>(rate);legacy<double>(rate);blocks<float>(rate);blocks<double>(rate);}
    stress();benchmark();if(argc==2&&std::string(argv[1])=="--render"){render(false,"coarse-pair.wav");render(true,"fine-pair.wav");}
    std::cout<<"RF01/RF02/RF03, exhaustive fine endpoint mapping, 131072 legacy and 262144 block-partition stereo frames PASS\n";}
