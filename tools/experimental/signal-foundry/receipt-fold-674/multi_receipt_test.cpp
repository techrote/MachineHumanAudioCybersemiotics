#include "multi_receipt.hpp"
#include <iostream>
#include <fstream>
#include <chrono>
#include <cstdlib>
#include <limits>
namespace randomized=mhac::receipt::randomized;
using namespace mhac::receipt::multi;
static void check(bool b){if(!b){std::cerr<<"multi check failed\n";std::exit(1);}}
// Independent graph test for the pinned 5-action/10-triangle witness.
static bool bipartite(const std::array<Matching,5>& a,unsigned subset){
    std::array<int,32> c{};c.fill(-1);
    for(unsigned root=0;root<32;++root){if(c[root]>=0)continue;c[root]=0;
        std::array<unsigned,32> queue{};unsigned read=0,end=1;queue[0]=root;
        while(read<end){const unsigned u=queue[read++];for(unsigned i=0;i<5;++i){if(!(subset&(1u<<i)))continue;
            const unsigned v=a[i].mate[u];if(v==u)continue;if(c[v]==c[u])return false;
            if(c[v]<0){c[v]=1-c[u];queue[end++]=v;}}}}
    return true;
}
static void witness(){
    std::array<Matching,5> a{Matching(5),Matching(5),Matching(5),Matching(5),Matching(5)};
    unsigned v=0;for(unsigned i=0;i<5;++i)for(unsigned j=i+1;j<5;++j)for(unsigned k=j+1;k<5;++k){
        check(a[i].pair(v,v+1));check(a[j].pair(v+1,v+2));check(a[k].pair(v,v+2));v+=3;}
    check(v==30);for(unsigned s=0;s<32;++s){unsigned n=0;for(unsigned i=0;i<5;++i)n+=(s>>i)&1u;
        check(bipartite(a,s)==(n<=2));check(!(bipartite(a,s)&&bipartite(a,31^s)));}
    check(bipartite(a,3)&&bipartite(a,12)&&bipartite(a,16));
    Matching m;check(m.pair(0,1)&&m.pair(4,6)&&m.pair(3,7)); // no common differing digit
    Receipt p{Contract::preview,1,preview_digit(m),{1,false}};
    unsigned errors=0;for(unsigned q=0;q<8;++q)errors+=p.decode(m,m.collapse(q),p.tag(m,q))!=q?1u:0u;
    check(errors==2);
    Matching correlated;check(correlated.pair(0,1)&&correlated.pair(2,3));
    for(unsigned a=1;a<8;++a)for(bool upper:{false,true}){
        Receipt r{Contract::balanced,1,0,{a,upper}};
        check((r.decode(correlated,0,r.tag(correlated,0))!=0)==(r.decode(correlated,2,r.tag(correlated,2))!=2));
    }
}
static void put(std::ofstream& f,std::uint32_t v,unsigned n){for(unsigned i=0;i<n;++i)f.put(static_cast<char>((v>>(8*i))&255));}
static void render(const std::string& prefix,Contract mode,const char* name){
    Config p{5,16,1,35,mode,9,42,false,.8};Live e;check(e.apply(p));e.reset();
    std::ofstream f(prefix+name+".wav",std::ios::binary);check(bool(f));const unsigned frames=192000;
    f.write("RIFF",4);put(f,36+frames*4,4);f.write("WAVEfmt ",8);put(f,16,4);put(f,1,2);put(f,2,2);put(f,48000,4);put(f,192000,4);put(f,4,2);put(f,16,2);f.write("data",4);put(f,frames*4,4);
    for(unsigned i=0;i<frames;++i){const double t=double(i)/48000,env=std::min(1.0,double(i)/240)*std::clamp(double(189600)-i,0.0,2400.0)/2400;
        double l=env*(.55*std::sin(6.283185307179586*110*t)+.18*std::sin(6.283185307179586*173*t)),r=env*(.55*std::sin(6.283185307179586*137*t)+.18*std::sin(6.283185307179586*211*t));
        e.frame(l,r);for(double x:{l,r})put(f,static_cast<std::uint16_t>(static_cast<std::int16_t>(std::lround(x*32767))),2);}
    check(bool(f));const auto s=save(p);std::ofstream patch(prefix+name+".mr01",std::ios::binary);patch.write(reinterpret_cast<const char*>(s.data()),static_cast<std::streamsize>(s.size()));check(bool(patch));
}
int main(int argc,char** argv){
    witness();std::uint64_t worlds=0,frames=0;
    for(unsigned b=3;b<=8;++b){const unsigned n=1u<<b;
        for(unsigned seed:{0u,17u,4294967295u})for(unsigned count:{0u,1u,n/4,n/2}){
            Config p{b,count,0,25,Contract::balanced,seed,seed,false,.8};const auto m=geometry(p);
            unsigned pairs=0;for(unsigned q=0;q<n;++q){check(m.mate[m.mate[q]]==q);pairs+=q<m.mate[q]?1u:0u;}check(pairs==count);
            for(unsigned k=0;k<=b;++k){p.budget=k;randomized::Schedule seq;seq.reset(b,seed);std::array<unsigned,256> errors{};
                for(unsigned i=0;i<2*(n-1);++i){Receipt r{p.contract,k,0,seq.next()};for(unsigned q=0;q<n;++q){const auto x=r.decode(m,m.collapse(q),r.tag(m,q));check(x==q||x==m.mate[q]);errors[q]+=x!=q?1u:0u;++worlds;}}
                for(unsigned q=0;q<n;++q)check(errors[q]==(q==m.mate[q]?0:n/(1u<<k)-1));
                for(auto mode:{Contract::fixed,Contract::preview,Contract::known}){p.contract=mode;Receipt r{mode,k,preview_digit(m),{1,false}};
                    for(unsigned q=0;q<n;++q){const auto x=r.decode(m,m.collapse(q),r.tag(m,q));check(x==q||x==m.mate[q]);if(mode==Contract::known)check(x==q);}}
                p.contract=Contract::balanced;auto state=save(p);Config out;check(load(state.data(),state.size(),out)&&save(out)==state);state[11]=1;check(!load(state.data(),state.size(),out)&&save(out)==save(p));
            }
        }
    }
    for(double rate:{1000.,44100.,48000.,96000.,2000000.}){Live a,b;check(a.prepare(rate)&&b.prepare(rate));Config p{8,128,3,5,Contract::balanced,17,42,false,.8};check(a.apply(p)&&b.apply(p));a.reset();b.reset();
        for(unsigned i=0;i<24000;++i){if(i%257==0){p.geometry+=1;p.pairs=i%129;check(a.apply(p)&&b.apply(p));}
            double l=std::sin(double(i)*.01),r=-l;double x=l,y=r;a.frame(l,r);b.frame(x,y);check(l==x&&r==y&&std::abs(l)<=1&&std::abs(r)<=1);++frames;}
        float l=0,r=0;for(unsigned i=0;i<12000;++i){a.frame(l,r);check(l==0&&r==0);}p.bypass=true;check(a.apply(p));for(unsigned i=0;i<10001;++i){l=.25f;r=-.5f;a.frame(l,r);}check(l==.25f&&r==-.5f);
        auto invalid=p;invalid.pairs=129;check(!a.apply(invalid)&&save(a.config())==save(p));
    }
    // Single-pair numerical compatibility with the previous laboratory.
    for(unsigned bits:{3u,8u}){Config p{bits,1,2,25,Contract::balanced,17,42,false,.8};
        auto m=geometry(p);unsigned lo=0;while(m.mate[lo]==lo)++lo;
        randomized::Config old{bits,lo,m.mate[lo],2,25,42,true,false,.8};
        Live a;randomized::Live b;check(a.apply(p)&&b.apply(old));a.reset();b.reset();
        for(unsigned i=0;i<48000;++i){float l=static_cast<float>(std::sin(double(i)*.01)),r=-l,x=l,y=r;a.frame(l,r);b.frame(x,y);check(l==x&&r==y);}
        double l=std::numeric_limits<double>::infinity(),r=std::numeric_limits<double>::quiet_NaN();a.frame(l,r);check(l==0&&r==0);
    }
    Live e;Config p{8,128,3,5,Contract::balanced,17,42,false,.8};check(e.apply(p));e.reset();
    const auto start=std::chrono::steady_clock::now();double sum=0;for(unsigned i=0;i<480000;++i){double l=.31,r=-.47;e.frame(l,r);sum+=l+r;}
    const auto elapsed=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
    std::cout<<"worlds="<<worlds<<" paired_frames="<<frames<<" benchmark_seconds="<<elapsed<<" checksum="<<sum<<"\n";
    if(argc==3&&std::string(argv[1])=="--render"){for(auto mode:{Contract::fixed,Contract::balanced,Contract::preview,Contract::known})render(argv[2],mode,mode==Contract::fixed?"fixed":mode==Contract::balanced?"balanced":mode==Contract::preview?"preview":"known");}
}
