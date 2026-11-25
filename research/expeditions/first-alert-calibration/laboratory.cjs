"use strict";
// Synthetic exact finite-state witnesses; no participant data.
function laboratory(){
  const assert=(x,m)=>{if(!x)throw Error(m)};
  const pop=x=>{let n=0;while(x){x&=x-1;n++}return n};
  const gcd=(a,b)=>b?gcd(b,a%b):a;
  const fraction=(a,b)=>{if(!b)return null;let g=gcd(a,b);return `${a/g}/${b/g}`};
  let schedules=0,profiles=0,extrema=0,endpointPairs=0;
  // Enumerate all labelled event-set schedules, independently for each truth class.
  for(let M=1;M<=4;M++)for(let n=1;n<=4;n++){
    const K=1<<M, groups=new Map();
    function visit(t,counts,union){
      if(t===n){schedules++;const key=counts.join(",");const u=pop(union);let rec=groups.get(key);if(!rec){rec={counts:counts.slice(),seen:new Set()};groups.set(key,rec)}rec.seen.add(u);return;}
      for(let mask=0;mask<K;mask++)visit(t+1,[...counts,pop(mask)],union|mask);
    }
    visit(0,[],0);profiles+=groups.size;
    for(const {counts,seen} of groups.values()){
      const lo=Math.max(...counts),hi=Math.min(M,counts.reduce((a,b)=>a+b,0));
      assert(Math.min(...seen)===lo && Math.max(...seen)===hi,"sharp union");
      for(let u=lo;u<=hi;u++)assert(seen.has(u),"no holes");
      extrema++;
    }
    // All pairs of true/false profiles, equal prior and class sizes.
    for(const a of groups.values())for(const b of groups.values()){
      const l1=Math.min(...a.seen),h1=Math.max(...a.seen),l0=Math.min(...b.seen),h0=Math.max(...b.seen);
      if(!h1||!h0)continue;
      for(const u1 of [l1,h1])for(const u0 of [l0,h0]){
        assert(u1*(l1+h0)>=l1*(u1+u0),"lower precision");
        assert(u1*(h1+l0)<=h1*(u1+u0),"upper precision");
        endpointPairs++;
      }
    }
  }
  function sets(M,counts,spread){
    let cursor=0;
    return counts.map(c=>{let s=new Set();for(let j=0;j<c;j++)s.add((j+(spread?cursor:0))%M);cursor+=c;return s});
  }
  function evaluate(M,counts1,counts0,spread1,spread0,pi1,pi0){
    const a=sets(M,counts1,spread1),b=sets(M,counts0,spread0);
    let first1=Array(a.length).fill(0),first0=Array(a.length).fill(0);
    for(let i=0;i<M;i++){
      for(const [ss,out] of [[a,first1],[b,first0]]){let t=ss.findIndex(s=>s.has(i));if(t>=0)out[t]++;}
    }
    const sum=x=>x.reduce((a,b)=>a+b,0),u1=sum(first1),u0=sum(first0);
    return {snapshotHigh:counts1.map((v,t)=>fraction(pi1*v,pi1*v+pi0*counts0[t])),snapshotLow:counts1.map((v,t)=>fraction(pi1*(M-v),pi1*(M-v)+pi0*(M-counts0[t]))),firstTrue:first1,firstFalse:first0,firstPrecision:first1.map((v,t)=>fraction(pi1*v,pi1*v+pi0*first0[t])),everPrecision:fraction(pi1*u1,pi1*u1+pi0*u0)};
  }
  const rare=evaluate(100,Array(100).fill(81),Array(100).fill(1),false,true,1,9);
  assert(rare.everPrecision==="9/109","rare precision");assert(rare.snapshotHigh.every(x=>x==="9/10"),"rare high calibration");assert(rare.snapshotLow.every(x=>x==="19/910"),"rare low calibration");assert(rare.firstPrecision.slice(1).every(x=>x==="0/1"),"late alerts");
  const nested=evaluate(4,[3,3,3,3],[1,1,1,1],false,false,1,1);
  const spread=evaluate(4,[3,3,3,3],[1,1,1,1],false,true,1,1);
  assert(nested.everPrecision==="3/4" && spread.everPrecision==="3/7","four tick");
  // Conditional false path distributions: half mass at zero plus half
  // uniformly over parity class. Use integer counts, denominator 2^n.
  let projectionChecks=0;const parity=[];
  for(let n=2;n<=10;n++){
    const K=1<<n;
    const weights=p=>Array.from({length:K},(_,x)=>(pop(x)%2===p?1:0)+(x===0?K/2:0));
    const A=weights(0),B=weights(1);
    for(let mask=0;mask<K-1;mask++){
      const aa=new Int32Array(K),bb=new Int32Array(K);
      for(let x=0;x<K;x++){aa[x&mask]+=A[x];bb[x&mask]+=B[x]}
      for(let i=0;i<K;i++)if((i&mask)===i){assert(aa[i]===bb[i],"proper projection");projectionChecks++;}
    }
    const uA=K-A[0],uB=K-B[0];
    parity.push({n,falseUnionEven:fraction(uA,K),falseUnionOdd:fraction(uB,K),precisionEven:fraction(3*K,3*K+4*uA),precisionOdd:fraction(3*K,3*K+4*uB)});
  }
  // Genuine posterior coupling: P1=1/4 or 3/4, equiprobable;
  // P2=0,1/2,1. Rows use denominator 4; Y sampled at P2.
  const martingale=[];
  for(let c=0;c<=1;c++){
    const rows=[[2+c,2-2*c,c],[1-c,2*c,3-c]];
    assert(rows.every(row=>row.reduce((a,b)=>a+b,0)===4),"row mass");
    assert(rows[0][1]+2*rows[0][2]===2 && rows[1][1]+2*rows[1][2]===6,"martingale");
    assert([0,1,2].map(j=>rows[0][j]+rows[1][j]).join(",")==="3,2,3","terminal marginal");
    martingale.push({rows,hitProbability:fraction(4+c,8),hitPrecision:fraction(3+c,4+c)});
  }
  return {status:"PASS",schedules,profiles,extrema,endpointPairs,projectionChecks,nested,spread,rare:{...rare, snapshotHigh:rare.snapshotHigh[0],snapshotLow:rare.snapshotLow[0]},parity,martingale};
}
console.log(JSON.stringify(laboratory(), null, 2));
