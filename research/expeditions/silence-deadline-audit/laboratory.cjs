'use strict';
function laboratory(){
 const assert=(v,m)=>{if(!v)throw Error(m)};
 const sum=a=>a.reduce((s,x)=>s+x,0);
 const tv=(a,b)=>sum(a.map((v,i)=>Math.abs(v-b[i])))/2;
 function greedy(A,B,M){
  let a=A.slice(),b=B.slice(),i=0,j=0,pairs=[];
  while(i<a.length&&j<b.length){
   if(!a[i]){i++;continue} if(!b[j]){j++;continue}
   if(i+M<j){i++;continue}if(j+M<i){j++;continue}
   let n=Math.min(a[i],b[j]);pairs.push([i,j,n]);a[i]-=n;b[j]-=n;
  }
  let u=Array(A.length+M).fill(0),v=u.slice();
  a.forEach((n,i)=>u[i]+=n);b.forEach((n,i)=>v[i]+=n);
  for(let [i,j,n] of pairs){assert(Math.abs(i-j)<=M,"cap");u[Math.max(i,j)]+=n;v[Math.max(i,j)]+=n}
  return {mass:sum(pairs.map(x=>x[2])),u,v,pairs};
 }
 function hall(A,B,M){
  let worst=0;
  for(let mask=0;mask<2**A.length;mask++){
   let demand=0,supply=0;
   for(let i=0;i<A.length;i++)if(mask>>i&1)demand+=A[i];
   for(let j=0;j<B.length;j++)if(A.some((_,i)=>(mask>>i&1)&&Math.abs(i-j)<=M))supply+=B[j];
   worst=Math.max(worst,demand-supply)
  }
  return worst;
 }
 function* compositions(n,k,prefix=[]){
  if(k===1){yield [...prefix,n];return}
  for(let i=0;i<=n;i++)yield* compositions(n-i,k-1,[...prefix,i]);
 }
 let profiles=0,subsets=0,releaseChecks=0;
 const laws=[...compositions(5,5)];
 for(const a of laws)for(const b of laws)for(let M=0;M<=4;M++){
  let g=greedy(a,b,M),h=hall(a,b,M);
  assert(g.mass===5-h,"Hall mismatch");
  assert(sum(g.u)===5&&sum(g.v)===5&&tv(g.u,g.v)===h,"release mismatch");
  profiles++;subsets+=2**a.length;
 }
 // Literal individual release choices; no matching logic in this oracle.
 function releases(a,M){
  const ts=a.flatMap((n,i)=>Array(n).fill(i)),out=[];
  function rec(i,h,c){
   if(i===ts.length){out.push([h.slice(),c]);return}
   for(let d=0;d<=M;d++){h[ts[i]+d]++;rec(i+1,h,c+d);h[ts[i]+d]--}
  }
  rec(0,Array(a.length+M).fill(0),0);return out;
 }
 // Enumerate all partial matchings of individual atoms. Costs are total added ticks
 // for equal branch weights, before division by twice inventory size.
 function partial(a,b,M){
  let x=a.flatMap((n,i)=>Array(n).fill(i)),y=b.flatMap((n,i)=>Array(n).fill(i));
  let best=Array(x.length+1).fill(Infinity);
  function rec(i,mask,k,c){
   if(i===x.length){best[k]=Math.min(best[k],c);return}
   rec(i+1,mask,k,c);
   y.forEach((t,j)=>{if(!(mask>>j&1)&&Math.abs(x[i]-t)<=M)rec(i+1,mask|1<<j,k+1,c+Math.abs(x[i]-t))});
  }
  rec(0,0,0,0);return best;
 }
 let budgetProfiles=0;
 const tiny=[...compositions(3,4)];
 for(const a of tiny)for(const b of tiny)for(let M=0;M<=2;M++){
  let p=partial(a,b,M),best=Array(4).fill(Infinity);
  for(const [u,c] of releases(a,M))for(const [v,d] of releases(b,M)){
   let k=3-tv(u,v);for(let j=0;j<=k;j++)best[j]=Math.min(best[j],c+d);
   releaseChecks++;
  }
  assert(best.every((v,k)=>v===p[k]),"budget mismatch");budgetProfiles++;
 }
 let comb=0;
 for(let n=1;n<=32;n++)for(let M=0;M<=4;M++){
  let a=Array(2*n*(M+1)).fill(0),b=a.slice();
  for(let j=0;j<n;j++){a[2*j*(M+1)]=1;b[(2*j+1)*(M+1)]=1}
  let g=greedy(a,b,M),ca=0,cb=0,maxDiff=0;
  for(let t=0;t<a.length;t++){ca+=a[t];cb+=b[t];maxDiff=Math.max(maxDiff,Math.abs(ca-cb))}
  assert(g.mass===0&&maxDiff===1,"comb");comb++;
 }
 const q=greedy([1,0,1,0],[0,0,1,1],0);assert(q.mass===1,"quantile counterexample");
 // Exact geometric masses with w=u/v, verify adaptive kernel by fractions.
 let geo=0;
 const add=(a,b)=>[a[0]*b[1]+b[0]*a[1],a[1]*b[1]];
 const mul=(a,b)=>[a[0]*b[0],a[1]*b[1]];
 const eq=(a,b)=>a[0]*b[1]===b[0]*a[1];
 for(let v=4;v<=40;v++)for(let u=1;4*u<=v;u++){
  let U=BigInt(u),V=BigInt(v),L=V-U,R=V-2n*U;
  const B=k=>k<1?[0n,1n]:[R*(2n*U)**BigInt(k-1),V**BigInt(k)];
  const A=k=>k<0?[0n,1n]:k===0?[R,L]:mul([U,L],B(k));
  const gt=(a,b)=>a[0]*b[1]>b[0]*a[1];
  assert(gt(A(0),B(1)),"first mass");
  for(let k=1;k<=24;k++){
   assert(gt(B(k),A(k)),"raw tail");
   if(k>=2)assert(gt(B(k),A(k-1)),"shifted tail");
   let padded=add(mul(A(k-1),k===1?[L,V]:[R,V]),mul(A(k-2),k===2?[U,V]:[2n*U,V]));
   assert(eq(padded,B(k)),"adaptive geometric identity");geo++;
  }
 }
 return {profiles,hall_subsets:subsets,budget_profiles:budgetProfiles,literal_release_pairs:releaseChecks,comb_controls:comb,geometric_coefficients:geo,assertion_failures:0};
}
console.log(JSON.stringify(laboratory(),null,2));
