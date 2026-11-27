#include "escape_release.hpp"
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <queue>
#include <string>
#include <vector>
#include <limits>
#include <chrono>
using namespace mhac::orbit;
using namespace mhac::orbit::escape;
static unsigned long long checks=0;
static void check(bool ok){++checks;if(!ok){std::cerr<<"FAIL "<<checks<<'\n';std::exit(1);}}
// Independent forward search: minimize (truncations,steps) by tuple order.
static void oracle(){
    using Cost=std::pair<int,int>;using Item=std::pair<Cost,int>;
    constexpr int side=33,N=side*side;
    const auto index=[](Point p){check(std::abs(p.x)<=16&&std::abs(p.y)<=16);return (p.x+16)*side+p.y+16;};
    std::array<Cost,N> d;d.fill({10000,10000});
    std::priority_queue<Item,std::vector<Item>,std::greater<Item>> q;
    const int start=index({-16,4}),zero=index({});d[start]={0,0};q.push({d[start],start});
    while(!q.empty()){
        const auto item=q.top();q.pop();const int i=item.second;if(item.first!=d[i])continue;
        const Point p{i/side-16,i%side-16};
        for(int a=0;a<2;++a){Point z;check(step(p,8,4,9,a==0,z));const int j=index(z);
            Cost c{item.first.first+a,item.first.second+1};if(c<d[j]){d[j]=c;q.push({c,j});}}
    }
    check(d[zero]==Cost{9,60});unsigned reachable=0;for(auto c:d)reachable+=c.first!=10000;check(reachable==857);
    Route route;check(route.prepare());check(route.states.front()==Point{-16,4}&&route.states.back()==Point{});
    for(unsigned i=0;i<steps;++i){check(!(route.states[i]==Point{}));check(route.gain[i]>=0&&route.gain[i]<=1);}
    Point p{-16,4};unsigned pure=0;while(!(p==Point{})){check(step(p,8,4,9,false,p));++pure;}check(pure==25);
    for(unsigned n:{10u,60u,61u,480u,48000u}){check(route.sample(0,n)==1&&route.sample(n,n)==0);
        for(unsigned i=0;i<n;++i)check(route.sample(i,n)>=0&&route.sample(i,n)<=1);}
    std::cout<<"reachable="<<reachable<<" optimal=9/60 pure-truncation="<<pure<<'\n';
}
static void regression(){
    for(double rate:{1000.,1234.568,44100.,48000.,96000.,1234567.8,2000000.})for(unsigned mix:{0u,500u,1000u}){
        Instrument a,b;check(a.prepare(rate)&&b.prepare(rate));check(!a.prepare(0));check(!a.on(1,48,std::numeric_limits<double>::quiet_NaN()));
        check(a.setPatch({mix,10,0})&&b.setPatch({mix,10,0}));
        for(int i=0;i<8;++i)check(a.on(i,36+i,.9)&&b.on(i,36+i,.9));
        check(!a.on(9,36,1)&&!a.on(0,36,1));
        double l=0,r=0,x=0,y=0;
        for(unsigned i=0;i<unsigned(std::ceil(rate*.006));++i){a.tick(l,r);b.tick(x,y);check(l==x&&r==y);}
        for(int i=0;i<8;++i)check(a.off(i,true)&&b.off(i,true));
        check(a.off(0,false)); // Duplicate off cannot change the selected release.
        for(unsigned i=0;i<unsigned(std::ceil(rate*.01))+2;++i){a.tick(l,r);b.tick(x,y);check(l==x&&r==y&&std::isfinite(l)&&std::isfinite(r)&&std::abs(l)<=.52&&std::abs(r)<=.52);}
        check(a.active()==0&&b.active()==0&&l==0&&r==0);check(!a.off(0,true));
        check(a.on(0,36,1));check(a.off(0,true));for(unsigned i=0;i<unsigned(std::ceil(rate*.01));++i){a.tick(l,r);check(l==0&&r==0);}
        check(a.active()==0);
    }
}
static void compare(){
    Engine baseline;Instrument linear,intervention;
    check(baseline.prepare(48000)&&linear.prepare(48000)&&intervention.prepare(48000));
    const Patch patch{500,800,0};check(baseline.setPatch(patch)&&linear.setPatch(patch)&&intervention.setPatch(patch));
    check(baseline.noteOn(0,60,.8)&&linear.on(0,60,.8)&&intervention.on(0,60,.8));
    double a=0,b=0,c=0,d=0,e=0,f=0;
    for(int i=0;i<24000;++i){baseline.tick(a,b);linear.tick(c,d);intervention.tick(e,f);check(a==c&&b==d&&c==e&&d==f);}
    check(baseline.noteOff(0)&&linear.off(0,false)&&intervention.off(0,true));
    double error=0;bool differs=false;
    for(int i=0;i<38400;++i){baseline.tick(a,b);linear.tick(c,d);intervention.tick(e,f);
        error=std::max({error,std::abs(a-c),std::abs(b-d)});differs|=c!=e||d!=f;}
    check(error<1e-12&&differs&&linear.active()==0&&intervention.active()==0&&e==0&&f==0);
    std::cout<<"linear baseline max error="<<error<<'\n';
    Instrument stress;check(stress.prepare(96000)&&stress.setPatch({500,1000,0}));
    for(int i=0;i<8;++i)check(stress.on(i,48+i,1));
    for(int i=0;i<480;++i)stress.tick(a,b);
    for(int i=0;i<8;++i)check(stress.off(i,true));
    double sum=0,worst=0;unsigned misses=0;
    for(int i=0;i<2000;++i){auto start=std::chrono::steady_clock::now();for(int j=0;j<32;++j)stress.tick(a,b);
        const auto us=std::chrono::duration<double,std::micro>(std::chrono::steady_clock::now()-start).count();
        sum+=us;worst=std::max(worst,us);misses+=us>32e6/96000.;check(std::isfinite(a)&&std::isfinite(b));}
    std::cout<<"96k/32 eight release voices mean_us="<<sum/2000<<" max_us="<<worst<<" misses="<<misses<<"/2000\n";
}
static void put(std::ofstream& o,unsigned x,int n){for(int i=0;i<n;++i){o.put(char(x&255));x>>=8;}}
static void render(const std::string& path,bool intervention){
    constexpr unsigned rate=48000,n=rate*4;Instrument e;check(e.prepare(rate));check(e.setPatch({1000,800,0}));
    std::ofstream o(path,std::ios::binary);check(bool(o));o.write("RIFF",4);put(o,36+4*n,4);o.write("WAVEfmt ",8);put(o,16,4);put(o,1,2);put(o,2,2);put(o,rate,4);put(o,rate*4,4);put(o,4,2);put(o,16,2);o.write("data",4);put(o,4*n,4);
    for(unsigned i=0;i<n;++i){if(i==0||i==rate*2){for(int k=0;k<3;++k)check(e.on(k,48+k*7+(i?3:0),.8));}
        if(i==rate/2||i==rate*5/2){for(int k=0;k<3;++k)check(e.off(k,intervention));}
        double l=0,r=0;e.tick(l,r);if(i>=rate*7/2)check(l==0&&r==0);
        for(double s:{l,r})put(o,unsigned(int(std::lround(s*32767))),2);}
    check(bool(o)&&e.active()==0);
}
int main(int argc,char** argv){oracle();regression();compare();if(argc==2){const std::string p=argv[1];render(p+"/linear.wav",false);render(p+"/intervention.wav",true);}std::cout<<"PASS checks="<<checks<<'\n';}
