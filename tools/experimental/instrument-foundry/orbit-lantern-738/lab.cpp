#include "orbit.hpp"
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <limits>
#include <vector>
#include <string>
#include <chrono>
using namespace mhac::orbit;
static unsigned long long checks=0;
static void check(bool b){++checks;if(!b){std::cerr<<"FAIL at check "<<checks<<'\n';std::exit(1);}}
static void orbitTests(){
    for(int q=2;q<=32;++q)for(int x=-q/2;x<=q/2;++x)for(int y=-q/2;y<=q/2;++y){Point p{x,y},z;
        check(step(p,0,q-1,q,true,z)&&z==Point{-y,x});
        check(step(p,0,q-1,q,false,z));check(std::max(std::abs(z.x),std::abs(z.y))==std::max(0,std::max(std::abs(x),std::abs(y))-1));}
    Point p{-16,4};const auto start=p;for(int i=1;i<=68;++i){check(step(p,8,4,9,true,p));check((p==start)==(i==68));}
    int steps=0;while(!(p==Point{})){const int old=p.x*p.x+p.y*p.y;check(step(p,8,4,9,false,p));check(p.x*p.x+p.y*p.y<old);++steps;}
    Point unchanged{1,2};check(!step({1,2},8,8,9,true,unchanged)&&unchanged==Point{1,2});
    std::cout<<"68-cycle truncation steps="<<steps<<'\n';
}
static void spectrumTests(){Spectrum s;check(s.build<68>({-16,4},8,4,9));check(s.dominant==5);
    Point p{-16,4};double x=0,y=0;s.sample(0,34,x,y);const double gain=x/p.x;check(gain>0);
    for(int i=0;i<68;++i){s.sample(tau*i/68.,34,x,y);check(std::abs(x-gain*p.x)<1e-12&&std::abs(y-gain*p.y)<1e-12);check(step(p,8,4,9,true,p));}
    s.sample(std::numeric_limits<double>::infinity(),999,x,y);check(x==0&&y==0);
    // Tuning oracle: dominant spectral line of a sustained 68-state MIDI A4 is 440 Hz.
    Engine e;check(e.prepare(48000));check(e.setPatch({1000,160,0}));check(e.noteOn(1,69,1));
    for(int i=0;i<4800;++i)e.tick(x,y);
    std::array<double,35> re{},im{};
    for(int i=0;i<48000;++i){e.tick(x,y);for(int k=1;k<=34;++k){const double t=tau*k*88.*i/48000.;re[k]+=x*std::cos(t);im[k]+=x*std::sin(t);}}
    int dominant=1;for(int k=2;k<=34;++k)if(std::hypot(re[k],im[k])>std::hypot(re[dominant],im[dominant]))dominant=k;check(dominant==5);
    // Existing voices retain captured parameters; a new patch must not affect them.
    Engine a,b;check(a.prepare(48000)&&b.prepare(48000));check(a.noteOn(1,60,1)&&b.noteOn(1,60,1));check(a.setPatch({1000,10,100}));
    for(int i=0;i<1000;++i){double u=0,v=0;a.tick(x,y);b.tick(u,v);check(x==u&&y==v);}check(a.noteOff(1)&&b.noteOff(1));
    for(int i=0;i<8000;++i){double u=0,v=0;a.tick(x,y);b.tick(u,v);check(x==u&&y==v);}check(a.active()==0&&b.active()==0);
}
static void stateTests(){for(unsigned b: {0u,1u,500u,999u,1000u})for(unsigned r:{10u,160u,1000u})for(int c:{-100,0,100}){Patch p{b,r,c},v{};check(decode(encode(p),v)&&v.blend==b&&v.releaseMs==r&&v.cents==c);}
    Patch p{};auto bytes=encode(p);bytes[4]=255;bytes[5]=255;check(!decode(bytes,p)&&p.blend==500);bytes=encode(p);bytes[0]='X';check(!decode(bytes,p));}
static std::vector<Event> score(double rate,unsigned blend){const auto at=[=](double t){return std::size_t(std::llround(t*rate));};
    std::vector<Event> e{{0,Event::Kind::patch,0,0,0,{blend,240,0}}};int id=0;
    for(int chord=0;chord<4;++chord){for(int n:{0,7,12}){const double t=chord*.75+n*.005;e.push_back({at(t),Event::Kind::on,id,48+chord*2+n,.8,{}});e.push_back({at(t+.5),Event::Kind::off,id,0,0,{}});++id;}}
    std::stable_sort(e.begin(),e.end(),[](auto a,auto b){return a.offset<b.offset;});return e;}
template<class T> static void renderScore(double rate,unsigned blend,std::size_t block,std::vector<T>& l,std::vector<T>& r){Engine engine;check(engine.prepare(rate));auto events=score(rate,blend);std::size_t j=0;
    for(std::size_t i=0;i<l.size();){const auto n=std::min(block,l.size()-i);std::array<Event,32> local{};std::size_t k=0;
        while(j<events.size()&&events[j].offset<i+n){local[k]=events[j++];local[k++].offset-=i;}
        unsigned refused=0;check(engine.render(l.data()+i,r.data()+i,n,local.data(),k,refused)&&refused==0);i+=n;}check(j==events.size()&&engine.active()==0);}
static void engineTests(){Engine e;check(!e.prepare(0)&&!e.prepare(std::numeric_limits<double>::infinity()));check(e.prepare(48000));std::cout<<"68-cycle dominant harmonic="<<e.dominantB()<<'\n';
    check(!e.noteOn(0,60,std::numeric_limits<double>::quiet_NaN()));for(int i=0;i<8;++i)check(e.noteOn(i,48+i,1));check(!e.noteOn(8,60,1)&&!e.noteOn(0,60,1));
    double x=0,y=0;for(int i=0;i<1000;++i){e.tick(x,y);check(std::isfinite(x)&&std::abs(x)<=.52&&std::abs(y)<=.52);}for(int i=0;i<8;++i)check(e.noteOff(i));for(int i=0;i<8000;++i)e.tick(x,y);check(x==0&&y==0&&e.active()==0);
    double l[16]{},r[16]{};Event invalid{16,Event::Kind::on,0,60,1,{}};unsigned refused=99;check(!e.render(l,r,16,&invalid,1,refused)&&refused==99&&e.active()==0);
    Event pair[]={{3,Event::Kind::on,0,60,1,{}},{3,Event::Kind::off,0,0,0,{}}};check(e.render(l,r,16,pair,2,refused)&&refused==0);for(int i=0;i<16;++i)check(l[i]==0&&r[i]==0);e.reset();
    for(double rate:{8000.,44100.,48000.,96000.,192000.})for(unsigned mix:{0u,500u,1000u}){const auto n=std::size_t(rate*4);std::vector<double>a(n),b(n),c(n),d(n);std::vector<float> f(n),g(n);
        renderScore(rate,mix,257,a,b);renderScore(rate,mix,32,c,d);renderScore(rate,mix,1024,f,g);
        for(std::size_t i=0;i<n;++i){check(a[i]==c[i]&&b[i]==d[i]&&float(a[i])==f[i]&&float(b[i])==g[i]);check(std::isfinite(a[i])&&std::abs(a[i])<=.52&&std::abs(b[i])<=.52);if(i<1||i>=n-std::size_t(.05*rate))check(a[i]==0&&b[i]==0);}}
    // Saturated polyphony stress, wall clock only; no hard timing assertion.
    check(e.prepare(96000));check(e.setPatch({500,160,0}));for(int i=0;i<8;++i)check(e.noteOn(i,48+i,1));
    constexpr int blocks=2000,frames=32;double worst=0,sum=0;unsigned misses=0;
    for(int i=0;i<blocks;++i){const auto t=std::chrono::steady_clock::now();for(int j=0;j<frames;++j)e.tick(x,y);const double us=std::chrono::duration<double,std::micro>(std::chrono::steady_clock::now()-t).count();worst=std::max(worst,us);sum+=us;misses+=us>frames*1e6/96000.;check(std::isfinite(x)&&std::isfinite(y));}
    std::cout<<"96k 32 frames 8 voices mean_us="<<sum/blocks<<" max_us="<<worst<<" misses="<<misses<<"/"<<blocks<<'\n';}
static void put(std::ofstream& out,unsigned x,int n){for(int i=0;i<n;++i){out.put(char(x&255));x>>=8;}}
static void wav(const std::string& path,unsigned blend){constexpr unsigned rate=48000,n=rate*4;std::vector<double> l(n),r(n);renderScore(rate,blend,257,l,r);
    std::ofstream o(path,std::ios::binary);check(bool(o));o.write("RIFF",4);put(o,36+4*n,4);o.write("WAVEfmt ",8);put(o,16,4);put(o,1,2);put(o,2,2);put(o,rate,4);put(o,rate*4,4);put(o,4,2);put(o,16,2);o.write("data",4);put(o,4*n,4);
    double sum=0,peak=0;for(unsigned i=0;i<n;++i)for(double s:{l[i],r[i]}){put(o,unsigned(int(std::lround(s*32767))),2);sum+=s*s;peak=std::max(peak,std::abs(s));}check(bool(o));std::cout<<path<<" peak="<<peak<<" rms="<<std::sqrt(sum/(2*n))<<'\n';}
int main(int argc,char** argv){if(argc==3&&std::string(argv[1])=="--render"){for(unsigned b:{0u,500u,1000u}){const auto path=std::string(argv[2])+"/orbit-"+std::to_string(b);wav(path+".wav",b);const auto bytes=encode({b,240,0});std::ofstream p(path+".ol01",std::ios::binary);p.write(reinterpret_cast<const char*>(bytes.data()),std::streamsize(bytes.size()));check(bool(p));}return 0;}
    orbitTests();spectrumTests();stateTests();engineTests();std::cout<<"PASS checks="<<checks<<'\n';}
