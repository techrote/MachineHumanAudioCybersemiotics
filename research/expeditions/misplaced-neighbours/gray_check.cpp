// Independent exhaustive Gray feasibility check using prefix masks.
#include <array>
#include <cstdint>
#include <iostream>
using namespace std;
uint64_t adj[32], calls;
int order[32], N, cap;
bool dfs(int depth,uint64_t visited){
 ++calls;
 if(depth==N)return true;
 uint64_t candidates=adj[order[depth-1]]&~visited;
 if(depth==1)candidates&=uint64_t(1)<<1;
 while(candidates){
   int v=__builtin_ctzll(candidates);uint64_t bit=uint64_t(1)<<v;candidates^=bit;
   uint64_t next=visited|bit;
   // All vertices whose latest neighbour position is now reached must have all neighbours placed.
   if(depth>=cap && (adj[order[depth-cap]]&~next))continue;
   order[depth]=v;
   if(dfs(depth+1,next))return true;
 }
 return false;
}
int main(){
 for(auto params: {array<int,2>{4,7}, {4,9}, {5,13}, {5,15}, {5,17}}){
   int n=params[0];cap=params[1];N=1<<n;
   for(int i=0;i<N;i++){adj[i]=0;for(int b=0;b<n;b++)adj[i]|=uint64_t(1)<<(i^(1<<b));}
   calls=0;order[0]=0;bool feasible=dfs(1,1);
   cout<<n<<","<<cap<<","<<feasible<<","<<calls<<"\n";
   if(feasible!=(cap==(1<<(n-1))+1))return 1;
 }
}
