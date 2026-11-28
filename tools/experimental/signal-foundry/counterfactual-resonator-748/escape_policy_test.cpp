#include "escape_policy.hpp"
#include <cstdlib>
#include <iostream>
#include <queue>
#include <utility>
using namespace mhac::counterfactual;
static void check(bool b){if(!b){std::cerr<<"escape policy failure\n";std::exit(1);}}
// Independent forward BFS with a hard truncation budget, not scalar costs.
static unsigned bfs(IntegerState start,unsigned budget){
    constexpr unsigned side=33, count=side*side;
    std::array<int,17*count> seen{};seen.fill(-1);
    const auto idx=[](IntegerState s,unsigned k){return k*count+unsigned(s.x+16)*side+unsigned(s.y+16);};
    struct Node{IntegerState s;unsigned used;};
    std::queue<Node> q;q.push({start,0});seen[idx(start,0)]=0;
    while(!q.empty()){
        const auto n=q.front();q.pop();const auto d=seen[idx(n.s,n.used)];
        if(!n.s.x&&!n.s.y)return unsigned(d);
        for(unsigned t=0;t<2;++t){if(n.used+t>budget)continue;
            const auto s=step(n.s,0,t!=0);const auto i=idx(s,n.used+t);
            if(seen[i]<0){seen[i]=d+1;q.push({s,n.used+t});}}
    }
    return EscapePolicy::infinity;
}
int main(){
    EscapePolicy p;unsigned maxDebt=0,maxTicks=0,saved=0,states=0;
    for(int x=-16;x<=16;++x)for(int y=-16;y<=16;++y){
        IntegerState s{x,y};const auto d=p.lookup(s);check(d.valid&&d.interventions<=16);
        check(bfs(s,d.interventions)==d.ticks);
        if(d.interventions)check(bfs(s,d.interventions-1)==EscapePolicy::infinity);
        auto z=s;unsigned debt=0,ticks=0;
        while(z.x||z.y){const auto a=p.lookup(z);check(a.valid&&ticks<1089);z=step(z,0,a.truncate);debt+=a.truncate;++ticks;}
        check(debt==d.interventions&&ticks==d.ticks);
        unsigned pure=0;while(s.x||s.y){s=step(s,0,true);++pure;check(pure<=16);}
        check(debt<=pure);saved+=debt<pure;maxDebt=std::max(maxDebt,debt);maxTicks=std::max(maxTicks,ticks);++states;
    }
    check(!p.lookup({17,0}).valid&&!p.lookup({0,-17}).valid);
    std::cout<<"PASS states="<<states<<" max_debt="<<maxDebt<<" max_ticks="<<maxTicks<<" fewer_than_pure="<<saved<<'\n';
}
