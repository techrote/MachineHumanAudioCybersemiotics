// Deterministic seeded witness finder, not an infeasibility oracle.
#include <algorithm>
#include <iostream>
#include <random>
#include <cmath>
#include <vector>
#include <cstdlib>
using namespace std;
int main(int argc,char** argv){
 int n=argc>1?atoi(argv[1]):5, cap=argc>2?atoi(argv[2]):13, trials=argc>3?atoi(argv[3]):20;
 if(n<2||n>9||cap<1||cap>=(1<<n)||trials<1)return 2;
 int N=1<<n;mt19937 rng(280);vector<int>a(N),p(N),best;
 for(int i=0;i<N;i++)a[i]=i;
 sort(a.begin(),a.end(),[](int u,int v){return __builtin_popcount(u)==__builtin_popcount(v)?u>v:__builtin_popcount(u)<__builtin_popcount(v);});auto h=a;best=a;
 auto score=[&](){for(int i=0;i<N;i++)p[a[i]]=i;int s=0;
 for(int v=0;v<N;v++)for(int b=0;b<n;b++){int u=v^(1<<b);if(u>v){int z=max(0,abs(p[v]-p[u])-cap);s+=z*z;}}
 for(int i=1;i<N;i++){int z=max(0,__builtin_popcount(a[i]^a[i-1])-2);s+=3*z*z;}return s;};
 int global=score();
 for(int trial=0;trial<trials;trial++){
 a=trial%2?h:best;int s=score();
 if(!s){for(int x:a)cout<<x<<",";cout<<"\n";return 0;}
 for(int k=0;k<100000;k++){
 double t=3*pow(.02,k/100000.);int i=1+rng()%(N-2),j=1+rng()%(N-2);if(i==j)continue;
 if(trial%3&&__builtin_popcount(a[i])!=__builtin_popcount(a[j]))continue;
 swap(a[i],a[j]);int q=score();if(q<=s||generate_canonical<double,53>(rng)<exp((s-q)/t))s=q;else swap(a[i],a[j]);
 if(s<global){global=s;best=a;cerr<<trial<<" "<<k<<" "<<s<<"\n";if(!s){for(int x:a)cout<<x<<",";cout<<"\n";return 0;}}
 }}cerr<<"budget exhausted, best penalty "<<global<<"\n";return 1;}
