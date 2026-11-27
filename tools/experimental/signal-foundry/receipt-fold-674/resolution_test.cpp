#include "resolution.hpp"
#include <cstdio>
#include <cstdlib>
#include <limits>
#include <fstream>
#include <string>
namespace r=mhac::receipt;
namespace v=r::resolution;
static void check(bool b){if(!b){std::fputs("resolution regression failed\n",stderr);std::abort();}}
static void put(std::ofstream& f,unsigned v,unsigned n){for(unsigned j=0;j<n;++j)f.put(static_cast<char>((v>>(8*j))&255));}
static void render(r::Mode mode,const char* name){
    constexpr unsigned n=48000*4;
    std::ofstream f(name,std::ios::binary);
    f.write("RIFF",4);put(f,36+4*n,4);f.write("WAVEfmt ",8);put(f,16,4);put(f,1,2);put(f,2,2);put(f,48000,4);put(f,192000,4);put(f,4,2);put(f,16,2);f.write("data",4);put(f,4*n,4);
    v::Live e;check(e.prepare(48000));
    for(unsigned i=0;i<n;++i){
        if(i%48000==0){const unsigned bits=3+i/48000;const unsigned bins=1u<<bits;
            check(e.apply({bits,bins/8,3*bins/4,1,mode,false,.8}));}
        const double t=i/48000.,env=std::max(0.,std::min({1.,t*40,(3.9-t)*40}));
        double l=env*(.7*std::sin(6.283185307179586*110*t)+.15*std::sin(6.283185307179586*220*t));
        double rr=env*.8*std::sin(6.283185307179586*165*t);
        e.frame(l,rr);put(f,static_cast<unsigned>(static_cast<int>(l*32767)),2);put(f,static_cast<unsigned>(static_cast<int>(rr*32767)),2);
    }
    check(bool(f));
}
int main(int argc,char** argv){
    std::uint64_t cases=0;
    for(unsigned bits=3;bits<=8;++bits){const unsigned n=1u<<bits;
        for(unsigned a=0;a<n;++a)for(unsigned b=a+1;b<n;++b){
            for(unsigned m=0;m<4;++m)for(unsigned k=0;k<=bits;++k){
                v::Config p{bits,a,b,k,static_cast<r::Mode>(m),false,1};
                const unsigned expect=m==0?a:m>=2?b:((a^b)&((1u<<k)-1))?b:a;
                check(v::recover(a,p)==a&&v::recover(b,p)==expect);++cases;
                const auto s=v::save(p);v::Config copy;check(v::load(s.data(),s.size(),copy)&&v::save(copy)==s);
            }
        }
    }
    std::uint64_t frames=0;
    for(double rate:{1234.568,44100.,48000.,192000.,1234567.8}){
        r::Live old;v::Live now;check(old.prepare(rate)&&now.prepare(rate));
        for(unsigned i=0;i<24000;++i){
            if(i%31==0){r::Patch p{r::pair(i%8,(i/31)%8),static_cast<r::Mode>((i/31)%4),i%217==0,.7};
                const auto s=r::save(p);v::Config c;check(v::load(s.data(),s.size(),c));check(old.apply(p)&&now.apply(c));}
            double l=std::sin(i*.017),rr=std::cos(i*.031),a=l,b=rr;
            old.frame(l,rr);now.frame(a,b);check(l==a&&rr==b);++frames;
        }
    }
    for(double rate:{1000.,48000.,384000.,2000000.}){
        v::Live x;check(x.prepare(rate));v::Config p{8,0,255,0,r::Mode::absent,false,1};check(x.apply(p));
        const unsigned length=static_cast<unsigned>(std::ceil(rate*.005));
        for(unsigned i=0;i<length*2;++i){double l=.99,rr=0;x.frame(l,rr);check(rr==0&&std::abs(l)<=1);}
        double prev=.99,zero=0;x.frame(prev,zero);
        for(unsigned i=0;i<length*2;++i){
            if(i%3==0){p.bits=(i%2)?3u:8u;p.hi=(1u<<p.bits)-1;p.mode=i%2?r::Mode::full:r::Mode::absent;check(x.apply(p));}
            double l=.99,rr=0;x.frame(l,rr);check(std::abs(l-prev)<=1.0/length+1e-12&&rr==0);prev=l;
        }
        auto bad=p;bad.bits=9;check(!x.apply(bad)&&!x.prepare(std::numeric_limits<double>::infinity()));
        auto s=v::save(p);s[10]=1;auto copy=p;check(!v::load(s.data(),s.size(),copy)&&v::save(copy)==v::save(p));
        p.bypass=true;check(x.apply(p));for(unsigned i=0;i<length+1;++i){float l=.5f,rr=0;x.frame(l,rr);check(rr==0);}
        float l=.5f,rr=std::numeric_limits<float>::quiet_NaN();x.frame(l,rr);check(l==.5f&&rr==0);
    }
    if(argc==2&&std::string(argv[1])=="--render"){
        render(r::Mode::absent,"resolution-absent.wav");render(r::Mode::preview,"resolution-preview.wav");
    }
    std::printf("%llu endpoint contract/state cases; %llu exact legacy frames; rate/retarget/bypass PASS\n",static_cast<unsigned long long>(cases),static_cast<unsigned long long>(frames));
}
