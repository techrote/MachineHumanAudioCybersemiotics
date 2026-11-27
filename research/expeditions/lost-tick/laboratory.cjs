// Exact integer experiment; Node >=18 or any BigInt-capable JS runtime.
// No repository dependencies, human data, external libraries, or floating rank tests.
"use strict";
function run() {
  const assert = (ok, msg) => { if (!ok) throw Error(msg); };
  const abs = x => x < 0n ? -x : x;
  const periods = [5,7,11,13,17];
  let q = [1n];
  for (const p of periods) {
    const a = Array(q.length+p-1).fill(0n);
    q.forEach((v,i)=>{for(let j=0;j<p;j++)a[i+j]+=v;});
    q=a;
  }
  const d=q.length-1;
  const at=i=>q[i]??0n;
  const col=(i,r)=>Array.from({length:r},(_,j)=>at(i-j));
  const dot=(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0n);
  const det2=(a,b)=>a[0]*b[1]-a[1]*b[0];
  const det3=(a,b,c)=>a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0]);
  const wedge=(a,b)=>[a[0]*b[1]-a[1]*b[0],a[0]*b[2]-a[2]*b[0],a[0]*b[3]-a[3]*b[0],a[1]*b[2]-a[2]*b[1],a[1]*b[3]-a[3]*b[1],a[2]*b[3]-a[3]*b[2]];
  const det4=(a,b)=>a[0]*b[5]-a[1]*b[4]+a[2]*b[3]+a[3]*b[2]-a[4]*b[1]+a[5]*b[0];
  const mins={}; let n2=0,n3=0,n4=0;
  for(let i=0;i<d+2;i++)for(let j=i+1;j<d+2;j++){
    const z=abs(det2(col(i,2),col(j,2)));assert(z>0n,"two-column collision");
    mins[2]=mins[2]===undefined||z<mins[2]?z:mins[2];n2++;
  }
  for(let i=0;i<d+3;i++)for(let j=i+1;j<d+3;j++)for(let k=j+1;k<d+3;k++){
    const z=abs(det3(col(i,3),col(j,3),col(k,3)));assert(z>0n,"three-column collision");
    mins[3]=mins[3]===undefined||z<mins[3]?z:mins[3];n3++;
  }
  const n=d+4, W=Array.from({length:n},(_,i)=>Array.from({length:n},(_,j)=>wedge(col(i,4),col(j,4))));
  const zero=[];
  for(let i=0;i<n;i++)for(let j=i+1;j<n;j++)for(let k=j+1;k<n;k++)for(let l=k+1;l<n;l++){
    const z=abs(det4(W[i][j],W[k][l])); n4++;
    if(!z)zero.push([i,j,k,l]);
    else mins[4]=mins[4]===undefined||z<mins[4]?z:mins[4];
  }
  const exceptions=[
    [[1,4,5,6],[-5n,7n,-7n,2n]],
    [[2,4,5,9],[-49n,64n,-35n,1n]],
    [[42,46,47,49],[1n,-35n,64n,-49n]],
    [[45,46,47,50],[2n,-7n,7n,-5n]]
  ];
  assert(JSON.stringify(zero)===JSON.stringify(exceptions.map(x=>x[0])),"unexpected zero minors");
  const fifth=[];
  for(const [I,v] of exceptions){
    for(let j=0;j<4;j++)assert(dot(I.map(i=>at(i-j)),v)===0n,"invalid dependence");
    // first three columns of each old triple are independent in H52:
    // the nonzero-codeword prefix has distance >=4 by the H51 checks.
    const s=dot(I.map(i=>at(i-4)),v);assert(s!==0n,"fifth row fails");fifth.push(s);
  }
  // H53 first four rows are H52 plus a zero column; any <=3 old columns
  // independent by the H51 prefix argument. New column is nonzero in row five.
  // Therefore every <=4 columns in H53 are independent.
  const recurrence=(h,start)=>dot(q,h.slice(start,start+d+1));
  function extend(h,N) {
    assert(h.length>=d,"need initial state");
    for(let t=0;t+d<h.length;t++)assert(recurrence(h,t)===0n,"bad initial recurrence");
    h=h.slice();
    while(h.length<N){let t=h.length-d; h.push(-dot(q.slice(0,d),h.slice(t))); }
    return h;
  }
  function integrate(h){let x=[0n];for(const v of h)x.push(x[x.length-1]+v);return x;}
  const deletion=(x,N,k)=>Array.from({length:N},(_,t)=>x[t+(t>=k?1:0)]);
  const mismatch=(x,y)=>x.reduce((s,v,i)=>s+Number(v!==null&&y[i]!==null&&v!==y[i]),0);
  // null is a flagged erasure. A candidate is retained iff <=e surviving substitutions.
  function list(x,z,e) {
    assert(x.length>=z.length+1,"template too short");
    let c=0;const out=[];
    for(let t=0;t<z.length;t++)if(z[t]!==null&&z[t]!==x[t+1])c++;
    for(let k=0;k<=z.length;k++){
      if(c<=e)out.push(k);
      if(k<z.length&&z[k]!==null)c+=Number(z[k]!==x[k])-Number(z[k]!==x[k+1]);
    }
    return out;
  }
  const naive=(x,z,e)=>Array.from({length:z.length+1},(_,k)=>k).filter(k=>mismatch(z,deletion(x,z.length,k))<=e);
  const witnessSpecs=[
    {L:47, I:[], v:[], e:0,f:0},
    {L:48, I:[0],v:[1n],e:0,f:1},
    {L:49, I:[0,1],v:[5n,-1n],e:1,f:0},
    {L:50, I:[0,1,2],v:[10n,-5n,1n],e:1,f:1},
    {L:52, I:exceptions[0][0],v:exceptions[0][1],e:2,f:0}
  ];
  const witnesses=[];
  for(const {L,I,v,e,f} of witnessSpecs){
    let h=Array(Math.max(L,d)).fill(0n);
    I.forEach((i,j)=>h[i]=v[j]);if(L===47)h[47]=1n;
    h=extend(h,L+4);
    const x=integrate(h), N=L+2, a=deletion(x,N,0),b=deletion(x,N,L);
    const support=Array.from({length:L},(_,i)=>i).filter(i=>h[i]!==0n);
    assert(JSON.stringify(support)===JSON.stringify(I),"support mismatch");
    const z=a.slice();for(const i of support.slice(0,f))z[i]=null;
    for(const i of support.slice(f,f+e))z[i]=b[i];
    const candidates=list(x,z,e);
    assert(candidates.includes(0)&&candidates.includes(L),"missing ambiguous endpoint");
    assert(mismatch(a,b)===support.length&&mismatch(z,a)<=e&&mismatch(z,b)<=e,"bad witness");
    assert(JSON.stringify(candidates)===JSON.stringify(naive(x,z,e)),"list mismatch");
    // x obeys (E-1)q(E)=0. Verify directly.
    for(let t=0;t+d+1<x.length;t++)assert(dot(q,x.slice(t+1,t+d+2))-dot(q,x.slice(t,t+d+1))===0n,"integral not admissible");
    witnesses.push({separation:L,errors:e,erasures:f,support,values:v.map(String),list:candidates,received:z.map(x=>x===null?null:String(x)),template:x.map(String)});
  }
  // Independent literal periodic templates and exhaustive list cross-check.
  let state=775;const rand=n=>{state=(Math.imul(state,1664525)+1013904223)>>>0;return state%n;};
  let trials=0, unique=0, multiple=0, phaseTrials=0;
  for(let it=0;it<40;it++){
    const tables=periods.map(p=>Array.from({length:p},()=>BigInt(rand(41)-20)));
    const value=t=>tables.reduce((s,a)=>s+a[((t%a.length)+a.length)%a.length],0n);
    const N=110,x=Array.from({length:N+1},(_,t)=>value(t));
    const h=x.slice(1).map((v,i)=>v-x[i]);
    for(let t=0;t+d<h.length;t++)assert(recurrence(h,t)===0n,"literal periodic recurrence");
    for(let k=0;k<=N;k++){
      const e=it%3,f=it%2,z=deletion(x,N,k), used=new Set();
      for(let j=0;j<e+f;j++){let i;do{i=rand(N)}while(used.has(i));used.add(i);z[i]=j<f?null:z[i]+1000n+BigInt(j);}
      const c=list(x,z,e);assert(c.includes(k),"truth excluded");
      assert(JSON.stringify(c)===JSON.stringify(naive(x,z,e)),"fast vs brute list");
      if(c.length===1)unique++;else multiple++;
      // use only qualified r=0..4; r=5 is not asserted.
      const L=[47,48,49,50,52][2*e+f];
      if(L!==undefined)assert(c[c.length-1]-c[0]<=L,"diameter bound");
      trials++;
    }
    for(const [N,e,f] of [[48,0,0],[49,0,1],[50,1,0],[51,1,1],[53,2,0]]){
      for(const s of [-1,0,1]){
        const z=Array.from({length:N},(_,t)=>value(t+37+s));
        for(let j=0;j<f;j++)z[j]=null;
        for(let j=f;j<f+e;j++)z[j]+=1234n;
        const c=[-1,0,1].filter(a=>mismatch(z,Array.from({length:N},(_,t)=>value(t+37+a)))<=e);
        assert(c.length===1&&c[0]===s,"settled phase not recovered");phaseTrials++;
      }
    }
  }
  // A deletion followed by a duplicate can be invisible even without noise.
  const x=witnesses[0].template.map(BigInt);
  const excursion=x.slice(0,50).map((v,t)=>t<47?x[t+1]:v);
  assert(excursion.every((v,t)=>v===x[t]),"invisible excursion");
  return {periods,dimension:d,polynomial:q.map(String),minorChecks:{two:n2,three:n3,four:n4},minimumNonzeroDeterminants:Object.fromEntries(Object.entries(mins).map(([k,v])=>[k,String(v)])),zeroFourMinors:zero,exceptionFifthRow:fifth.map(String),thresholds:[48,49,50,51,53],witnesses,randomListTrials:trials,unique,multiple,settledPhaseTrials:phaseTrials,invisibleExcursion:47,assertions:"pass"};
}
if(typeof module!=="undefined")module.exports=run;
if(typeof require!=="undefined"&&require.main===module)console.log(JSON.stringify(run(),null,2));
