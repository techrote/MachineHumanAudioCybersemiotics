// Synthetic finite oracle; Node >=18. No external packages.
"use strict";
function assert(ok,msg){if(!ok)throw Error(msg);}
function pop(x){let c=0;for(;x;x&=x-1)c++;return c;}
function edges(n){let e=[];for(let i=0;i<n;i++)for(let j=i+1;j<n;j++)e.push([i,j]);return e;}
function cutmask(e,S,A){let m=0;for(let i=0;i<e.length;i++){let [u,v]=e[i],U=1<<u,V=1<<v;if((S&U)&&(S&V)&&!!(A&U)!==!!(A&V))m|=1<<i;}return m;}
function cuts(e,S){let a=[];const anchor=S&-S;for(let A=(S-1)&S;A;A=(A-1)&S)if(A&anchor)a.push(cutmask(e,S,A));return a;}
function distance(G,C){let d=Infinity;for(const m of C)d=Math.min(d,pop(G&m));return d;}
function graphCensus(){
 let rows=[], graphs=0, supports=0, cutEvaluations=0, powerComparisons=0;
 for(let n=2;n<=6;n++){
  const e=edges(n), full=(1<<n)-1, C=Array.from({length:full+1},(_,S)=>pop(S)>=2?cuts(e,S):[]);
  let opt=Array.from({length:n+1},()=>Array(n).fill(Infinity));
  for(let G=0;G<1<<e.length;G++){
   graphs++;let bySize=Array(n+1).fill(Infinity);
   for(let S=1;S<=full;S++)if(pop(S)>=2){
    let k=pop(S),d=distance(G,C[S]);supports++;cutEvaluations+=C[S].length;
    bySize[k]=Math.min(bySize[k],d);
    // Independent literal square-intensity code against positive reference.
    if(n<=4){
     let actual=Infinity, A=S&-S;
     for(let B=(S-1)&S;B;B=(B-1)&S)if(B&A){
      let count=0;
      for(let i=0;i<e.length;i++)if(G&(1<<i)){
       const [u,v]=e[i],x=(S>>u)&1,y=(S>>v)&1;
       const a=x*((B>>u)&1?-1:1),b=y*((B>>v)&1?-1:1);
       if((x+y)**2!==(a+b)**2)count++;
      }
      actual=Math.min(actual,count);powerComparisons++;
     }
     assert(actual===d,"literal powers");
    }
   }
   for(let k=2;k<=n;k++)for(let d=1;d<k;d++){
    if(bySize[k]>=d)opt[k][d]=Math.min(opt[k][d],pop(G));
   }
   for(let k=2;k<n;k++)assert(bySize[k]<=bySize[k+1],"support monotonicity");
  }
  for(let k=2;k<=n;k++)for(let d=1;d<k;d++){
   const R=n-k+d,pred=R===1?n-1:Math.ceil(n*R/2);
   assert(opt[k][d]===pred,"optimal graph");
   rows.push({n,k,d,edges:pred});
  }
 }
 return {graphs,supports,cutEvaluations,powerComparisons,rows};
}
function harary(n,r){
 const E=new Set();function add(i,j){i%=n;j%=n;if(i!==j)E.add(Math.min(i,j)+","+Math.max(i,j));}
 if(r===1){for(let i=1;i<n;i++)add(i-1,i);}
 else {
  for(let i=0;i<n;i++)for(let j=1;j<=Math.floor(r/2);j++)add(i,i+j);
  if(r%2){if(n%2===0){for(let i=0;i<n/2;i++)add(i,i+n/2);}
    else{for(let i=0;i<=Math.floor(n/2);i++)add(i,i+Math.floor(n/2));}}
 }
 return [...E].map(s=>s.split(",").map(Number));
}
function hararyCensus(){
 let constructions=0,deletions=0;
 for(let n=2;n<=13;n++)for(let r=1;r<n;r++){
  const e=harary(n,r),full=(1<<n)-1;
  assert(e.length===(r===1?n-1:Math.ceil(n*r/2)),"Harary size");
  for(let S=1;S<=full;S++)if(pop(S)>n-r){
   let R=S&-S,old=0;
   while(R!==old){old=R;for(const [u,v] of e)if((S&(1<<u))&&(S&(1<<v))&&(R&((1<<u)|(1<<v))))R|=(1<<u)|(1<<v);}
   assert(R===S,"Harary connectivity");deletions++;
  }
  constructions++;
 }
 return {constructions,deletions};
}
function analogCensus(){
 let vectors=0,thresholds=0,cutEvaluations=0,noiseIntervals=0,decoderCases=0;
 for(let n=2;n<=5;n++){
  const e=edges(n),full=(1<<n)-1,C=cuts(e,full);
  for(let word=0;word<4**n;word++){
   let a=Array.from({length:n},(_,i)=>1+((word>>(2*i))&3)),sorted=a.slice().sort((a,b)=>a-b);
   vectors++;
   for(let eta=0;eta<=32;eta++){
    let G=0;
    for(let i=0;i<e.length;i++){
     const [u,v]=e[i],L=(a[u]-a[v])**2,H=(a[u]+a[v])**2;
     const disjoint=L+eta<H-eta;
     assert(disjoint===(4*a[u]*a[v]>2*eta),"interval overlap");
     noiseIntervals++;if(disjoint)G|=1<<i;
    }
    let d=distance(G,C),expected=0;
    for(let j=1;j<n;j++)if(2*sorted[0]*sorted[j]>eta)expected++;
    assert(d===expected,"threshold minimum cut");
    for(let b=0;b<n;b++)assert((d>b)===(b<n-1&&2*sorted[0]*sorted[n-1-b]>eta),"sharp noise frontier");
    thresholds++;cutEvaluations+=C.length;
   }
  }
 }
 // Direct received-vector enumeration for all four-vertex graphs; binary labels,
 // erasure mask disjoint from the error pattern, tie/confusion tested explicitly.
 let n=4,e=edges(n),full=(1<<n)-1,C=cuts(e,full);
 for(let G=0;G<1<<e.length;G++){
  const words=[0,...C.map(m=>m&G)],d=distance(G,C);
  for(let E=G;;E=(E-1)&G){
   const remaining=G^E;
   for(let t=0;t<=2;t++){
    let ambiguous=false;
    for(let Y=remaining;;Y=(Y-1)&remaining){
     let count=words.filter(w=>pop((w^Y)&remaining)<=t).length;
     if(count>1)ambiguous=true;
     if(!Y)break;
    }
    // Fixed erasure mask: use surviving distance, not worst case d.
    assert(ambiguous===(distance(remaining,C)<=2*t),"error ball intersection");
    decoderCases++;
   }
   if(!E)break;
  }
  for(let s=0;s<=e.length;s++)for(let t=0;t<=2;t++){
   let found=false;
   for(let E=G;;E=(E-1)&G){if(pop(E)<=s&&distance(G^E,C)<=2*t)found=true;if(!E)break;}
   assert(found===(d<=2*t+s),"worst case errors and erasures");
  }
 }
 return {vectors,thresholds,cutEvaluations,noiseIntervals,decoderCases};
}
function weakLoudCensus(){
 let cases=0;
 for(let r=1;r<=4;r++)for(let w=r;w<=7;w++){
  const n=r+w;let e=edges(n),G=e.filter(([i,j])=>i<r&&j>=r);
  assert(G.length===r*w,"mandatory edge count");
  // Use direct cuts (not 32-bit edge masks for large graph).
  let d=Infinity,S=(1<<n)-1;
  for(let A=1;A<S;A++)if(A&1){
   let c=G.filter(([u,v])=>!!(A&(1<<u))!==!!(A&(1<<v))).length;
   d=Math.min(d,c);
  }
  assert(d===r,"bipartite cut");cases++;
 }
 return {cases};
}
function run(){return {status:"pass",scope:"synthetic finite model",graph:graphCensus(),harary:hararyCensus(),analog:analogCensus(),weakLoud:weakLoudCensus()};}
if(typeof module!=="undefined")module.exports={run};
if(typeof require!=="undefined"&&require.main===module)console.log(JSON.stringify(run(),null,2));
