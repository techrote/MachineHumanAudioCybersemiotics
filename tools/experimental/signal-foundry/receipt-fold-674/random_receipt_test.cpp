#include "random_receipt.hpp"
#include <chrono>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <vector>
namespace r=mhac::receipt;
namespace z=r::randomized;
static void check(bool b){if(!b){std::cerr<<"random receipt regression failed\n";std::abort();}}
static void finite(){
    std::uint64_t worlds=0;
    for(unsigned bits=3;bits<=8;++bits){const unsigned n=1u<<bits;
        for(unsigned a=1;a<n;++a){std::array<bool,256> seen{};for(unsigned x=0;x<n;++x){const auto y=z::multiply(x,a,bits);check(y<n&&!seen[y]);seen[y]=true;}}
        for(unsigned k=0;k<=bits;++k){const unsigned size=n>>k;
            // GF linearity reduces all pairs to their nonzero XOR difference.
            for(unsigned d=1;d<n;++d){z::Config p{bits,0,d,k};unsigned lo=0,hi=0,coll=0;
                for(unsigned a=1;a<n;++a){for(bool upper:{false,true}){z::Draw draw{a,upper};
                    lo+=z::recover(0,p,draw)!=0;hi+=z::recover(d,p,draw)!=d;coll+=z::collision(p,draw);worlds+=2;}}
                check(lo==size-1&&hi==size-1&&coll==2*(size-1));}
            // Check balanced tag classes directly for every multiplier.
            for(unsigned a=1;a<n;++a){z::Config p{bits,0,1,k};std::array<unsigned,256> counts{};
                for(unsigned x=0;x<n;++x)++counts[z::tag(x,p,{a,false})];
                for(unsigned i=0;i<(1u<<k);++i)check(counts[i]==size);}
        }
        for(unsigned seed:{0u,1u,42u,0xffffffffu}){z::Schedule s;s.reset(bits,seed);std::array<bool,510> seen{};
            for(unsigned cycle=0;cycle<4;++cycle){seen.fill(false);for(unsigned i=0;i<2*(n-1);++i){auto d=s.next();unsigned j=(d.multiplier-1)*2+unsigned(d.upper);check(j<2*(n-1)&&!seen[j]);seen[j]=true;}}}
    }
    z::Config fixed{8,96,176,4};fixed.balanced=false;
    check(z::collision(fixed,{1,false})&&z::recover(176,fixed,{1,false})==96&&z::recover(96,fixed,{1,true})==176);
    fixed.budget=5;check(!z::collision(fixed,{1,false})&&z::recover(176,fixed,{1,false})==176);
    std::cout<<"finite endpoint worlds="<<worlds<<'\n';
}
static void streaming(){
    for(double rate:{1000.,8000.,44100.,48000.,96000.,192000.,2000000.}){
        z::Live a,b;check(a.prepare(rate)&&b.prepare(rate));z::Config p{5,4,20,2,17,42,true,false,.8};
        check(a.apply(p)&&b.apply(p));auto invalid=p;invalid.epoch_ms=0;check(!a.apply(invalid)&&z::save(a.config())==z::save(p));auto state=z::save(p);z::Config q;check(z::load(state.data(),state.size(),q)&&z::save(q)==state);
        auto bad=state;bad[10]=2;check(!z::load(bad.data(),bad.size(),q)&&z::save(q)==state);
        for(unsigned i=0;i<25000;++i){if(i%997==0){p.budget=(i/997)%6;p.balanced=i%2==0;p.wet=(i%7)/6.;check(a.apply(p)&&b.apply(p));}
            double l=std::sin(i*.015),rr=std::cos(i*.023),x=l,y=rr;
            a.frame(l,rr);b.frame(x,y);check(l==x&&rr==y&&std::abs(l)<=1&&std::abs(rr)<=1);
            if(i%1000==0){float f=0,g=std::numeric_limits<float>::infinity();a.frame(f,g);b.frame(f,g);check(f==0&&g==0);}}
        p.bypass=true;check(a.apply(p));for(unsigned i=0;i<10001;++i){double l=.8,rr=-.6;a.frame(l,rr);if(i==10000)check(l==.8&&rr==-.6);}
        a.reset();b.apply(p);b.reset();double l=.7,rr=-.9,x=l,y=rr;a.frame(l,rr);b.frame(x,y);check(l==x&&rr==y);
    }
    // Block partition independent: caller supplies absolute frame offsets for changes.
    z::Config p{8,96,176,4,7,77,true,false,1};z::Live a,b;check(a.apply(p)&&b.apply(p));
    std::vector<float> ref(48000);for(unsigned i=0;i<ref.size();++i){float l=.65f*std::sin(i*.02f),rr=l;a.frame(l,rr);check(l==rr);ref[i]=l;}
    unsigned pos=0;for(unsigned block=1;pos<ref.size();block=block*3%511+1){unsigned end=std::min<unsigned>(pos+block,static_cast<unsigned>(ref.size()));
        for(;pos<end;++pos){float l=.65f*std::sin(pos*.02f),rr=l;b.frame(l,rr);check(l==ref[pos]&&rr==l);}}
    z::Live impulse;check(impulse.apply(p));double l=.8,rr=-.8;impulse.frame(l,rr);
    for(unsigned i=0;i<48000;++i){l=rr=0;impulse.frame(l,rr);check(l==0&&rr==0);}
    const auto start=std::chrono::steady_clock::now();
    double sum=0;for(unsigned i=0;i<480000;++i){p.lo=i%128;p.hi=p.lo+128;check(impulse.apply(p));l=.25;rr=-.7;impulse.frame(l,rr);sum+=l+rr;}
    const auto seconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
    std::cout<<"streaming rates=7 paired frames=175000 partition frames=48000 impulse silence=48000\n";
    std::cout<<"dense automation frames=480000 seconds="<<seconds<<" checksum="<<sum<<'\n';
}
static void put(std::ofstream& f,unsigned v,unsigned n){for(unsigned i=0;i<n;++i)f.put(static_cast<char>(v>>(8*i)));}
static void render(const char* path,bool balanced){
    constexpr unsigned rate=48000,n=rate*4;std::ofstream f(path,std::ios::binary);check(bool(f));
    f.write("RIFF",4);put(f,36+n*4,4);f.write("WAVEfmt ",8);put(f,16,4);put(f,1,2);put(f,2,2);put(f,rate,4);put(f,rate*4,4);put(f,4,2);put(f,16,2);f.write("data",4);put(f,n*4,4);
    z::Live a;z::Config p{3,1,5,1,25,42,balanced,false,.8};check(a.apply(p));double peak=0,energy=0;
    for(unsigned i=0;i<n;++i){if(i==rate||i==2*rate||i==3*rate){p.bits=3+i/rate;p.lo=1u<<(p.bits-3);p.hi=5u<<(p.bits-3);p.budget=p.bits-2;check(a.apply(p));}
        double t=double(i)/rate,env=std::max(0.,std::min({1.,t*100.,(3.9-t)*100.}));
        double l=env*(.66*std::sin(6.283185307179586*110*t)+.09*std::sin(6.283185307179586*331*t)),rr=env*.7*std::sin(6.283185307179586*165*t);
        a.frame(l,rr);peak=std::max({peak,std::abs(l),std::abs(rr)});energy+=l*l+rr*rr;
        put(f,static_cast<unsigned>(static_cast<int>(std::lround(l*32767))),2);put(f,static_cast<unsigned>(static_cast<int>(std::lround(rr*32767))),2);}
    check(bool(f));std::cout<<path<<" peak="<<peak<<" rms="<<std::sqrt(energy/(2*n))<<'\n';
}
int main(int argc,char** argv){finite();streaming();if(argc==3){render(argv[1],false);render(argv[2],true);}return 0;}
