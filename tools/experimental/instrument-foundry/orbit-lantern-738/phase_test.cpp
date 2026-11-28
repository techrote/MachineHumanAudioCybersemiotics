#include "escape_release.hpp"
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <queue>
#include <vector>
#include <string>
#include <limits>
using namespace mhac::orbit;
using namespace mhac::orbit::escape;
static unsigned checks=0;
static void check(bool b){++checks;if(!b){std::cerr<<"FAIL "<<checks<<'\n';std::exit(1);}}
// Independent forward tuple-cost Dijkstra, starting from each phase.
static std::pair<int,int> oracle(Point p){
    using Cost=std::pair<int,int>;using Item=std::pair<Cost,int>;
    const auto index=[](Point z){check(std::abs(z.x)<=16&&std::abs(z.y)<=16);return (z.x+16)*33+z.y+16;};
    std::array<Cost,1089> d;d.fill({9999,9999});
    std::priority_queue<Item,std::vector<Item>,std::greater<Item>> q;
    const int s=index(p),zero=index({});d[s]={0,0};q.push({d[s],s});
    while(!q.empty()){
        const auto v=q.top();q.pop();const int u=v.second;if(v.first!=d[u])continue;
        if(u==zero)return v.first;
        for(int a=0;a<2;++a){Point z;check(step({u/33-16,u%33-16},8,4,9,a==0,z));
            const int j=index(z);const Cost c{v.first.first+a,v.first.second+1};
            if(c<d[j]){d[j]=c;q.push({c,j});}}
    }
    return {9999,9999};
}
static void routes(){
    PhaseBank bank;check(bank.prepare());Point p{-16,4};unsigned lo=60,hi=0;
    for(unsigned i=0;i<68;++i){const auto& r=bank.route(i);const auto c=oracle(p);
        check(c==std::make_pair(int(r.interventions),int(r.length))&&r.interventions==9);
        lo=std::min(lo,r.length);hi=std::max(hi,r.length);
        check(r.gain[0]==1.&&r.gain[r.length]==0.&&r.sample(0,480)==1.&&r.sample(480,480)==0.);
        for(unsigned j=0;j<480;++j){const double g=r.sample(j,480);check(g>=0&&g<=1);}
        check(PhaseBank::phaseIndex(tau*(i+.5)/68.)==i);check(step(p,8,4,9,true,p));
    }
    check(p==Point{-16,4}&&lo==48&&hi==60);
    check(PhaseBank::phaseIndex(std::numeric_limits<double>::quiet_NaN())==0);
    std::cout<<"68 phase routes, nine interventions each, steps="<<lo<<".."<<hi<<'\n';
}
static void audio(){
    bool differs=false;
    for(double rate:{1000.,1234.568,48000.,96000.,1234567.8,2000000.}){
        Instrument a,b,c;check(a.prepare(rate)&&b.prepare(rate)&&c.prepare(rate));
        for(auto* e:{&a,&b,&c}){check(e->setPatch({1000,10,0}));for(int k=0;k<8;++k)check(e->on(k,36+k,.8));}
        double l=0,r=0,x=0,y=0,z=0,w=0;
        for(unsigned i=0;i<unsigned(rate*.011);++i){a.tick(l,r);b.tick(x,y);c.tick(z,w);check(l==x&&r==y&&l==z&&r==w);}
        for(int k=0;k<8;++k){check(a.offPhase(k)&&b.offPhase(k)&&c.off(k,true));check(b.off(k,false));}
        for(unsigned i=0;i<unsigned(std::ceil(rate*.01))+2;++i){
            a.tick(l,r);b.tick(x,y);c.tick(z,w);check(l==x&&r==y&&std::isfinite(l)&&std::isfinite(r)&&std::abs(l)<=.52&&std::abs(r)<=.52);differs|=l!=z||r!=w;}
        check(a.active()==0&&b.active()==0&&c.active()==0&&l==0&&r==0);
        check(!a.offPhase(0));check(a.on(0,36,.8)&&a.offPhase(0));
        for(unsigned i=0;i<unsigned(std::ceil(rate*.01));++i){a.tick(l,r);check(l==0&&r==0);}
    }
    check(differs);
}
static void put(std::ofstream& o,unsigned x,int n){for(int i=0;i<n;++i){o.put(char(x&255));x>>=8;}}
static void render(const std::string& path,bool phase){
    constexpr unsigned rate=48000,n=rate*4;Instrument e;check(e.prepare(rate)&&e.setPatch({1000,800,0}));
    std::ofstream o(path,std::ios::binary);check(bool(o));o.write("RIFF",4);put(o,36+4*n,4);o.write("WAVEfmt ",8);put(o,16,4);put(o,1,2);put(o,2,2);put(o,rate,4);put(o,rate*4,4);put(o,4,2);put(o,16,2);o.write("data",4);put(o,4*n,4);
    for(unsigned i=0;i<n;++i){
        if(i==0||i==rate*2)for(int k=0;k<3;++k)check(e.on(k,48+k*7+(i?3:0),.8));
        for(int k=0;k<3;++k)if(i==rate/2+unsigned(k)*733||i==rate*5/2+unsigned(k)*733)check(phase?e.offPhase(k):e.off(k,true));
        double l=0,r=0;e.tick(l,r);if(i>=rate*7/2)check(l==0&&r==0);
        for(double s:{l,r})put(o,unsigned(int(std::lround(s*32767))),2);
    }
    check(bool(o)&&e.active()==0);
}
int main(int argc,char** argv){routes();audio();if(argc==2){const std::string p=argv[1];render(p+"/fixed.wav",false);render(p+"/phase.wav",true);}std::cout<<"PASS checks="<<checks<<'\n';}
