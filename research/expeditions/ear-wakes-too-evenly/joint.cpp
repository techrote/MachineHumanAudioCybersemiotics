#include <algorithm>
#include <iostream>
#include <vector>
using namespace std;
int main(){
 for(int n=2;n<=20;n++){
 long long fail=0, balanced_fail=0; int full=(1<<n)-1;
 for(int a=1;a<=n;a++){
 int lim=(1<<a)-1;
 vector<int> bestg(n+1,n+1),bestgc(n+1,n+1),bestc(n+1,-1),bg(n+1,n+1);
 for(int mask=0;mask<=full;mask++){
 int b=__builtin_popcount((unsigned)mask), minc=a, maxg=0, r=mask;
 for(int t=0;t<n;t++){
 unsigned h=r&lim;
 if(!h){minc=0;maxg=n+1;break;}
 minc=min(minc,__builtin_popcount(h));
 maxg=max(maxg,n-((31-__builtin_clz(h))-__builtin_ctz(h)));
 r=(r>>1)|((r&1)<<(n-1));
 }
 bestg[b]=min(bestg[b],maxg);
 if(minc>bestc[b]){bestc[b]=minc;bestgc[b]=maxg;}else if(minc==bestc[b])bestgc[b]=min(bestgc[b],maxg);
 bool bal=true; for(int i=0;i<n&&bal;i++)if(((mask>>i)&1)!=(((i+1)*b/n)-(i*b/n)))bal=false;
 if(bal)bg[b]=maxg;
 }
 for(int b=0;b<=n;b++){
 if(bestc[b]!=a*b/n){cerr<<"count mismatch";return 1;}
 if(bestgc[b]>bestg[b]){cout<<"COUNTEREXAMPLE "<<n<<' '<<a<<' '<<b<<' '<<bestc[b]<<' '<<bestg[b]<<' '<<bestgc[b]<<endl;fail++;}
 if(bg[b]>bestg[b])balanced_fail++;
 }
 }
 cout<<n<<" jointfail "<<fail<<" balancedfail "<<balanced_fail<<endl;
 }
}
