#include "afterimage.hpp"
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <limits>
#include <vector>
#include <string>
#include <chrono>
using namespace mhac::afterimage;
static unsigned checks=0;
static void check(bool b) { ++checks; if(!b) { std::fprintf(stderr,"failed check %u\n",checks); std::exit(1); } }
static void advance(Engine& e,unsigned n) { while(n--) check(std::isfinite(e.tick())); }
static void u16(std::ostream& o,unsigned v) { o.put(static_cast<char>(v&255)); o.put(static_cast<char>((v>>8)&255)); }
static void u32(std::ostream& o,unsigned v) { u16(o,v); u16(o,v>>16); }
static void wav(const std::string& path, const std::vector<double>& data) {
    std::ofstream o(path,std::ios::binary); unsigned n=static_cast<unsigned>(data.size()*2);
    o.write("RIFF",4);u32(o,36+n);o.write("WAVEfmt ",8);u32(o,16);u16(o,1);u16(o,1);u32(o,48000);u32(o,96000);u16(o,2);u16(o,16);o.write("data",4);u32(o,n);
    for(double x:data) u16(o,static_cast<unsigned>(static_cast<int>(std::lround(x*32767))));
    if(!o) std::exit(2);
}
static void demos(const std::string& dir) {
    for(unsigned m=0;m<4;++m) {
        Engine e; Patch p; p.mode=static_cast<Mode>(m); e.configure(p);
        std::vector<double> a(240000); unsigned k=0;
        for(unsigned i=0;i<4;++i) {
            p.pair=i%2==0?Pair{2,6}:Pair{1,6}; e.configure(p);
            e.on(1,62,.9); for(unsigned j=0;j<12000;++j) a[k++]=e.tick(); e.off(1);
            for(unsigned j=0;j<2400;++j) a[k++]=e.tick();
            e.on(2,57,.85); for(unsigned j=0;j<24000;++j) a[k++]=e.tick(); e.off(2,false);
            for(unsigned j=0;j<21600;++j) a[k++]=e.tick();
        }
        wav(dir+"/receipt-"+std::to_string(m)+".wav",a);
    }
}
int main(int argc,char** argv) {
    if(argc==3&&std::string(argv[1])=="--render") { demos(argv[2]); return 0; }
    for(unsigned l=0;l<7;++l) for(unsigned h=l+1;h<8;++h) for(unsigned x=0;x<8;++x) for(unsigned m=0;m<4;++m) {
        Pair p{l,h}; unsigned bit=mask(static_cast<Mode>(m),p); auto r=decode(x==h?l:x,x&bit,bit,p);
        bool amb=(x==l||x==h)&&((l&bit)==(h&bit));
        check(r.ambiguous==amb);check(r.state==(amb?l:x));
    }
    for(double sr:{8000.,44100.,48000.,96000.,192000.}) {
        for(unsigned m=0;m<4;++m) {
            Engine e;check(e.prepare(sr));Patch p;p.mode=static_cast<Mode>(m);check(e.configure(p));
            check(e.on(1,62,1));advance(e,static_cast<unsigned>(sr*.04));check(e.off(1));check(e.remembered()==0);advance(e,static_cast<unsigned>(sr*.031)+2);
            check(e.on(2,62,1));advance(e,static_cast<unsigned>(sr*.1));check(e.off(2));check(e.remembered()==(m<2?2u:6u));check(e.lastAmbiguous()==(m<2));
            check(e.on(3,61,1));advance(e,static_cast<unsigned>(sr*.1));check(e.off(3,false));check(e.remembered()==(m<2?2u:6u));
            advance(e,static_cast<unsigned>(sr*.031)+2);check(e.active()==0);check(e.tick()==0);
        }
        Engine a,b;check(a.prepare(sr)&&b.prepare(sr));Patch p;p.minimumMs=0;check(a.configure(p)&&b.configure(p));
        for(int i=0;i<8;++i) {check(a.on(i,60+i,1));check(b.on(i,60+i,1));} check(!a.on(9,60,1));check(!a.on(0,60,1));
        std::array<double,257> x{},y{},z{}; a.render(x.data(),y.data(),257);b.render(z.data(),static_cast<double*>(nullptr),1);b.render(z.data()+1,static_cast<double*>(nullptr),256);
        for(unsigned i=0;i<257;++i) {check(x[i]==y[i]&&x[i]==z[i]);check(std::abs(x[i])<=.52);}
        a.reset();check(a.active()==0&&a.tick()==0);check(!a.on(1,60,std::numeric_limits<double>::quiet_NaN()));check(!a.prepare(0));p.memory=std::numeric_limits<double>::infinity();check(!a.configure(p));
        std::array<float,17> f{};a.render(f.data(),f.data(),17);for(float s:f)check(s==0);
    }
    // Late pair changes affect fixed mode, while preview binds action at onset.
    for(Mode m:{Mode::fixed,Mode::preview}) {Engine e;Patch p;p.mode=m;p.minimumMs=0;check(e.configure(p));check(e.on(1,62,1));p.pair={1,6};check(e.configure(p));check(e.off(1));check(e.remembered()==6);check(!e.lastAmbiguous());}
    for(Mode m:{Mode::fixed,Mode::preview}) {Engine e;Patch p;p.mode=m;p.minimumMs=0;check(e.configure(p));check(e.on(1,62,1));p.pair={4,6};check(e.configure(p));check(e.off(1));check(e.remembered()==(m==Mode::fixed?4u:6u));check(e.lastAmbiguous()==(m==Mode::fixed));}
    // Completion order, not onset order, owns memory. Held timbre remains unchanged.
    Engine a,b;Patch p;p.minimumMs=0;check(a.configure(p)&&b.configure(p));check(a.on(1,57,1)&&b.on(1,57,1));check(a.on(2,62,0.5));check(a.off(2));check(a.remembered()==2);
    for(unsigned i=0;i<4096;++i) check(a.tick()==b.tick()); // second voice released before first tick
    check(a.off(1));check(a.remembered()==1);
    Engine bench;for(int i=0;i<8;++i)check(bench.on(i,48+i,1));auto start=std::chrono::steady_clock::now();double sum=0;for(unsigned i=0;i<480000;++i)sum+=bench.tick();auto end=std::chrono::steady_clock::now();check(std::isfinite(sum));
    std::printf("PASS %u checks; 480000 eight-voice frames in %.3f ms (offline)\n",checks,std::chrono::duration<double,std::milli>(end-start).count());
}
