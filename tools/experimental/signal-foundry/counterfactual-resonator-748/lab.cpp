#include "resonator.hpp"
#include <chrono>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <limits>
#include <string>
#include <vector>
using namespace mhac::counterfactual;
static unsigned checks=0;
static void check(bool yes){++checks;if(!yes){std::cerr<<"FAIL check "<<checks<<'\n';std::exit(1);}}
static bool same(Stereo a,Stereo b){return a.left==b.left&&a.right==b.right;}
static void test(){
    for(int x=-16;x<=16;++x)for(int y=-16;y<=16;++y){
        const IntegerState s{x,y};auto t=step(s,0,true);
        check((x==0&&y==0)||(t.x*t.x+t.y*t.y<x*x+y*y));
        for(int i=0;i<16;++i)t=step(t,0,true);
        check(t.x==0&&t.y==0);
        if(std::abs(x)<=4&&std::abs(y)<=4){auto n=step(s,0,false);check(n.x==-y&&n.y==x);for(int i=0;i<3;++i)n=step(n,0,false);check(n.x==x&&n.y==y);}
        for(int d=-12;d<=12;++d)for(bool trunc:{false,true}){auto n=step(s,d,trunc);check(std::abs(n.x)<=16&&std::abs(n.y)<=16);}
    }
    for(unsigned hz:{40u,220u,6000u})for(unsigned wet:{0u,700u,1000u})for(unsigned gain:{0u,800u,1000u})for(unsigned mode=0;mode<3;++mode)for(unsigned flags=0;flags<4;++flags){
        Controls p{static_cast<std::uint16_t>(hz),static_cast<std::uint16_t>(wet),static_cast<std::uint16_t>(gain),static_cast<std::uint8_t>(mode),bool(flags&1),bool(flags&2)},q;
        const auto b=encode(p);check(decode(b,q)&&encode(q)==b);
    }
    Controls q;auto bad=encode(q);bad[11]=128;check(!decode(bad,q));bad=encode(q);bad[10]=3;check(!decode(bad,q));bad=encode(q);bad[4]=0;bad[5]=0;check(!decode(bad,q));
    Processor p;check(!p.prepare(0));check(!p.prepare(std::numeric_limits<double>::infinity()));auto invalid=p.controls();invalid.wet=1001;check(!p.set(invalid));
    Controls c{250,1000,1000,1,false,false};check(p.set(c));check(p.prepare(48000));
    // Exactly one tick of half-scale excitation. Thereafter nearest settles into a nonzero cycle.
    for(int i=0;i<48;++i)p.process(0.5,0);
    for(int i=0;i<48000;++i){auto s=p.process(0,0);check(s.right==0&&std::abs(s.left)<=1);}
    const auto before=p.lattice(0);check(std::max(std::abs(before.x),std::abs(before.y))==4);
    const auto tick=p.ticks();p.requestIntervention();p.requestIntervention();while(p.ticks()==tick)p.process(0,0);
    auto after=p.lattice(0);check(p.interventions()==1&&std::max(std::abs(after.x),std::abs(after.y))==3);
    c.erase=true;check(p.set(c));for(int i=0;i<48*18;++i)p.process(0,0);check(same(p.process(0,0),{}));
    c.erase=false;c.monitor=0;check(p.set(c));p.reset();for(int i=0;i<48;++i)p.process(0.5,0);for(int i=0;i<48000;++i)p.process(0,0);check(same(p.process(0,0),{}));
    c.bypass=true;check(p.set(c));p.reset();check(same(p.process(0.25,-0.5),{0.25,-0.5}));check(same(p.process(std::numeric_limits<double>::quiet_NaN(),std::numeric_limits<double>::infinity()),{}));check(same(p.process(2,-2),{1,-1}));
    // Block partition and float/double conversion agreement, plus stereo independence.
    for(double rate:{8000.,44100.,48000.,96000.,192000.,384000.}){
        constexpr unsigned n=10007;std::vector<float> l(n),r(n),a(n),b(n),aa(n),bb(n);std::vector<double> dl(n),dr(n),da(n),db(n);
        for(unsigned i=0;i<n;++i){l[i]=float(int(i%129)-64)/64;r[i]=float(int((i*17)%127)-63)/63;dl[i]=l[i];dr[i]=r[i];}
        for(unsigned mode=0;mode<3;++mode){
            c={6000,1000,1000,static_cast<std::uint8_t>(mode),false,false};Processor whole,split,dbl,isolated;for(auto* proc:{&whole,&split,&dbl,&isolated}){check(proc->set(c));check(proc->prepare(rate));}
            whole.processBlock(l.data(),r.data(),a.data(),b.data(),n);dbl.processBlock(dl.data(),dr.data(),da.data(),db.data(),n);
            for(unsigned i=0;i<n;){const unsigned len=std::min(1+i%257,n-i);split.processBlock(l.data()+i,r.data()+i,aa.data()+i,bb.data()+i,len);i+=len;}
            for(unsigned i=0;i<n;++i){const auto iso=isolated.process(l[i],0);check(a[i]==aa[i]&&b[i]==bb[i]&&a[i]==float(da[i])&&b[i]==float(db[i]));check(a[i]==float(iso.left)&&iso.right==0);check(std::isfinite(a[i])&&std::abs(a[i])<=1&&std::abs(b[i])<=1);}
        }
        // Mixed automation and reset replay, including hostile input.
        Processor a1,a2;check(a1.prepare(rate)&&a2.prepare(rate));for(int pass=0;pass<2;++pass){a1.reset();a2.reset();for(unsigned i=0;i<20000;++i){Controls z{static_cast<std::uint16_t>(40+i%5961),static_cast<std::uint16_t>(i%1001),static_cast<std::uint16_t>((i*13)%1001),static_cast<std::uint8_t>(i%3),i%19==0,i%17==0};check(a1.set(z)&&a2.set(z));if(i%71==0){a1.requestIntervention();a2.requestIntervention();}const double in=i%11?0.9:std::numeric_limits<double>::infinity();auto s=a1.process(in,-in);check(same(s,a2.process(in,-in))&&std::isfinite(s.left)&&std::abs(s.left)<=1&&std::abs(s.right)<=1);}}
    }
    std::cout<<"PASS "<<checks<<" checks\n";
}
static void word(std::ostream& f,unsigned v,unsigned n){for(unsigned i=0;i<n;++i)f.put(static_cast<char>((v>>(8*i))&255));}
static void render(const std::string& dir){
    constexpr unsigned rate=48000,n=rate*4;const char* names[]={"reference","persistent","residual","intervention"};
    for(unsigned k=0;k<4;++k){
        Controls c{250,1000,800,static_cast<std::uint8_t>(k==3?1:k),false,false};Processor p;check(p.set(c)&&p.prepare(rate));
        std::ofstream wav(dir+"/Audio/"+names[k]+".wav",std::ios::binary);check(bool(wav));wav.write("RIFF",4);word(wav,36+n*4,4);wav.write("WAVEfmt ",8);word(wav,16,4);word(wav,1,2);word(wav,2,2);word(wav,rate,4);word(wav,rate*4,4);word(wav,4,2);word(wav,16,2);wav.write("data",4);word(wav,n*4,4);
        std::ofstream patch(dir+"/Presets/"+names[k]+".cr01",std::ios::binary);const auto bytes=encode(c);patch.write(reinterpret_cast<const char*>(bytes.data()),static_cast<std::streamsize>(bytes.size()));check(bool(patch));
        double energy=0,peak=0,tail=0;
        for(unsigned i=0;i<n;++i){
            const double l=i<48?0.5:0,r=i>=96&&i<144?-0.75:0;
            if(k==3&&i==rate)p.requestIntervention();
            if(k==3&&i==2*rate){c.erase=true;check(p.set(c));}
            const auto s=p.process(l,r);for(double v:{s.left,s.right}){peak=std::max(peak,std::abs(v));energy+=v*v;if(i>=n-2400)tail+=v*v;const auto pcm=static_cast<std::int16_t>(std::lround(v*32767));word(wav,static_cast<std::uint16_t>(pcm),2);}
        }
        check(bool(wav));std::cout<<names[k]<<",peak="<<peak<<",rms="<<std::sqrt(energy/(2*n))<<",final50ms_rms="<<std::sqrt(tail/4800)<<",interventions="<<p.interventions()<<'\n';
    }
}
static void bench(){
    Processor p;check(p.prepare(96000));constexpr unsigned blocks=4000,frames=32;std::vector<double> times;times.reserve(blocks);double sink=0;
    for(unsigned b=0;b<blocks;++b){auto start=std::chrono::steady_clock::now();for(unsigned i=0;i<frames;++i){const unsigned j=b*frames+i;Controls c{static_cast<std::uint16_t>(40+j%5961),static_cast<std::uint16_t>(j%1001),800,static_cast<std::uint8_t>(j%3),j%17==0,j%23==0};p.set(c);if(j%19==0)p.requestIntervention();sink+=p.process(.8,-.8).left;}auto end=std::chrono::steady_clock::now();times.push_back(std::chrono::duration<double,std::micro>(end-start).count());}
    std::sort(times.begin(),times.end());const auto misses=std::count_if(times.begin(),times.end(),[](double v){return v>1e6*frames/96000;});std::cout<<"blocks="<<blocks<<",median_us="<<times[blocks/2]<<",p99_us="<<times[blocks*99/100]<<",max_us="<<times.back()<<",misses="<<misses<<",sink="<<sink<<'\n';
}
int main(int argc,char** argv){if(argc==3&&std::string(argv[1])=="--render")render(argv[2]);else if(argc==2&&std::string(argv[1])=="--bench")bench();else test();}
