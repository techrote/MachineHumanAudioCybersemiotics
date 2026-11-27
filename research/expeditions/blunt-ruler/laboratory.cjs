"use strict";
function laboratory(){
  "use strict";
  const check=(condition,message)=>{if(!condition)throw Error(message)};
  // Every grid value exists, including levels absent from a restricted word.
  function oriented(a,b,q,r,B,C,sign) {
    const p=Array.from({length:q+1},()=>Array(r+1).fill(0));
    for(let t=0;t<a.length;t++)p[a[t]+1][(sign===1?b[t]:r-1-b[t])+1]++;
    for(let i=1;i<=q;i++)for(let j=1;j<=r;j++)p[i][j]+=p[i-1][j]+p[i][j-1]-p[i-1][j-1];
    const dp=Array.from({length:q+1},()=>Array(r+1).fill(0));
    for(let i=1;i<=q;i++)for(let j=1;j<=r;j++){
      let v=Math.max(dp[i-1][j],dp[i][j-1]);
      for(let u=1;u<=Math.min(i,B);u++)for(let w=1;w<=Math.min(j,C);w++){
        const mass=p[i][j]-p[i-u][j]-p[i][j-w]+p[i-u][j-w];
        v=Math.max(v,dp[i-u][j-w]+mass);
      }
      dp[i][j]=v;
    }
    return dp[q][r];
  }
  const score=(a,b,q,r,B,C)=>Math.max(oriented(a,b,q,r,B,C,1),oriented(a,b,q,r,B,C,-1));
  const phases=(x,N,K)=>Array.from({length:K},(_,s)=>x.slice(s,s+N));
  function profile(x,N,K,q,B){
    let w=phases(x,N,K),pairs=[];
    for(let i=0;i<K;i++)for(let j=i+1;j<K;j++)pairs.push([i,j,oriented(w[i],w[j],q,q,B,B,1),oriented(w[i],w[j],q,q,B,B,-1)]);
    let L=Math.max(...pairs.map(p=>Math.max(p[2],p[3])));
    return {N,K,q,B,L,distance:N-L,required_survivors:L+1,pairs,pilot:x};
  }
  function partitions(q,B){
    let out=[];
    function rec(a,k){if(a.length===q){out.push(a);return;}for(let u=1;u<=Math.min(B,q-a.length);u++)rec(a.concat(Array(u).fill(k)),k+1)}
    rec([],0);return out;
  }
  // Independent oracle: enumerate legal channel partitions, then retained masks.
  function oracle(a,b,q,r,B,C){
    let best=0;const n=a.length;
    for(const f of partitions(q,B))for(const g of partitions(r,C)){
      const x=a.map(v=>f[v]),y=b.map(v=>g[v]);
      for(let mask=1;mask<(1<<n);mask++){
        let idx=[];for(let i=0;i<n;i++)if(mask&(1<<i))idx.push(i);
        if(idx.length<=best)continue;
        for(const s of [1,-1]){
          if(idx.every(i=>idx.every(j=>Math.sign(x[i]-x[j])===s*Math.sign(y[i]-y[j])))){best=idx.length;break;}
        }
      }
    }
    return best;
  }
  function decode(x,N,K,q,B,y,e){
    const keep=[];for(let i=0;i<N;i++)if(y[i]!==null)keep.push(i);
    if(keep.length===0)return Array.from({length:K},(_,s)=>s);
    const values=[...new Set(keep.map(i=>y[i]))].sort((a,b)=>a-b);
    const rank=keep.map(i=>values.indexOf(y[i]));
    return Array.from({length:K},(_,s)=>s).filter(s=>score(keep.map(t=>x[t+s]),rank,q,values.length,B,1)>=keep.length-e);
  }
  let state=796;
  const rnd=n=>{state=(Math.imul(state,1664525)+1013904223)>>>0;return Math.floor(state/4294967296*n)};
  const sample=(n,q)=>Array.from({length:n},()=>rnd(q));
  let oracleChecks=0,decodeChecks=0,reductionChecks=0;
  for(let k=0;k<400;k++){
    const n=1+rnd(7),q=1+rnd(6),r=1+rnd(6),B=1+rnd(q),C=1+rnd(r),a=sample(n,q),b=sample(n,r);
    check(score(a,b,q,r,B,C)===oracle(a,b,q,r,B,C),"partition oracle");
    oracleChecks++;
  }
  // Compare spaced embedding and adversarial binning for arbitrary reference pairs.
  for(let k=0;k<800;k++){
    let q=1+rnd(12),B=1+rnd(q),m=Math.ceil(q/B),n=1+rnd(14),a=sample(n,q),b=sample(n,q);
    let ca=a.map(x=>Math.floor(x/B)),cb=b.map(x=>Math.floor(x/B));
    let strict=score(ca,cb,m,m,1,1);
    check(score(a,b,q,q,B,B)>=strict,"binning bound");
    check(score(ca.map(x=>x*B),cb.map(x=>x*B),q,q,B,B)===strict,"spaced equality");
    reductionChecks++;
  }
  const old=[1,3,0,0,1,0,3,2,3,3];
  const cases=[profile(old,8,3,4,1),profile(old,8,3,4,2),profile(old.map(v=>2*v),8,3,7,2),profile(old.map(v=>3*v),8,3,10,3)];
  const ternary=[0,0,1,0,2,2,1,2,0,0];
  const binary=[0,0,0,0,1,0,0,1,0,0];
  cases.push(profile(binary.map(v=>2*v),8,3,4,2));
  for(let B=1;B<=8;B++){const p=profile(ternary.map(v=>B*v),8,3,2*B+1,B);check(p.L===2,"minimal grid ternary witness");cases.push(p);}
  for(let k=0;k<600;k++){
    const x=old.map(v=>2*v),N=8,K=3,q=7,B=2,s=rnd(K),p=partitions(q,B),f=p[rnd(p.length)],sign=rnd(2)?1:-1;
    const levels=Array.from({length:Math.max(...f)+1},(_,i)=>sign*(i*i+2*i+7));
    let y=x.slice(s,s+N).map(v=>levels[f[v]]);
    // Random distinct fault locations, two replacements and one erasure.
    const ids=Array.from({length:N},(_,i)=>i);
    for(let i=ids.length-1;i>0;i--){let j=rnd(i+1);[ids[i],ids[j]]=[ids[j],ids[i]]}
    y[ids[0]]=rnd(61)-30;y[ids[1]]=rnd(61)-30;y[ids[2]]=null;
    const actual=decode(x,N,K,q,B,y,2);
    check(JSON.stringify(actual)===JSON.stringify([s]),"spaced candidate list");
    const keep=ids.filter(i=>y[i]!==null);
    const ranks=[...new Set(keep.map(i=>y[i]))].sort((a,b)=>a-b);
    let expected=Array.from({length:K},(_,j)=>j).filter(j=>oracle(keep.map(t=>x[t+j]),keep.map(t=>ranks.indexOf(y[t])),q,ranks.length,B,1)>=keep.length-2);
    check(JSON.stringify(actual)===JSON.stringify(expected),"candidate list oracle");
    decodeChecks++;
  }
  // Exhaustively search finite strict alphabets. No quotient/symmetry pruning.
  const searches=[];
  function exhaustive(N,q,B){
    const K=3,x=Array(N+K-1).fill(0);let count=0,best=N+1,witness=null,histogram={};
    function rec(i){
      if(i<x.length){for(let v=0;v<q;v++){x[i]=v;rec(i+1)}return}
      count++;
      const a=x.slice(0,N),b=x.slice(1,N+1),c=x.slice(2,N+2);
      const L=Math.max(score(a,b,q,q,B,B),score(a,c,q,q,B,B),score(b,c,q,q,B,B));
      histogram[L]=(histogram[L]||0)+1;
      if(L<best){best=L;witness=x.slice()}
    }
    rec(0);check(count===q**x.length,"enumeration size");
    return {N,q,B,count,best_L:best,histogram,witness};
  }
  for(let N=3;N<=8;N++)for(const q of [2,3])searches.push(exhaustive(N,q,1));
  for(let N=3;N<=6;N++)for(const [q,B] of [[3,2],[4,2],[5,2]]){
    const v=exhaustive(N,q,B);const m=Math.ceil(q/B),w=searches.find(s=>s.N===N&&s.q===m&&s.B===1);
    check(v.best_L===w.best_L,"finite minimax reduction");searches.push(v);
  }
  // Find exact full-window ambiguity for the old pilot after clipping if possible,
  // and explicit common subset of maximum size from actual partitions.
  function ambiguity(x,N,K,q,B){
    let words=phases(x,N,K),best=-1,witness;
    for(let s=0;s<K;s++)for(let u=s+1;u<K;u++)for(const f of partitions(q,B))for(const g of partitions(q,B)){
      const a=words[s].map(v=>f[v]),b=words[u].map(v=>g[v]);
      for(let mask=1;mask<(1<<N);mask++){
        const idx=Array.from({length:N},(_,i)=>i).filter(i=>mask&(1<<i));if(idx.length<=best)continue;
        for(const sign of [1,-1])if(idx.every(i=>idx.every(j=>Math.sign(a[i]-a[j])===sign*Math.sign(b[i]-b[j])))){
          best=idx.length;witness={s,u,f,g,sign,indices:idx,a,b};break;
        }
      }
    }
    check(best===profile(x,N,K,q,B).L,"ambiguity witness");
    // Assign common outputs on retained blocks; extend with strict interpolation.
    const {s,u,f,g,sign,indices,a,b}=witness;
    const b2=b.map(v=>sign*v);
    const vals=[...new Set(indices.map(i=>a[i]))].sort((x,y)=>x-y);
    const anchorsA=vals.map(v=>[v,100*vals.indexOf(v)]);
    const anchorsB=vals.map(v=>[b2[indices.find(i=>a[i]===v)],100*vals.indexOf(v)]).sort((x,y)=>x[0]-y[0]);
    function extend(t,anchors){
      if(t<=anchors[0][0])return anchors[0][1]+t-anchors[0][0];
      for(let k=1;k<anchors.length;k++)if(t<=anchors[k][0]){
        let [a,v]=anchors[k-1],[b,w]=anchors[k];return v+(w-v)*(t-a)/(b-a)
      }
      let [a,v]=anchors[anchors.length-1];return v+t-a;
    }
    const A=a.map(v=>extend(v,anchorsA)),D=b2.map(v=>extend(v,anchorsB));
    check(indices.every(i=>A[i]===D[i]),"common calibrated outputs");
    const diff=Array.from({length:N},(_,i)=>i).filter(i=>A[i]!==D[i]);
    check(diff.length===N-best,"distance witness");
    const y=A.slice();for(let i=0;i<Math.floor(diff.length/2);i++)y[diff[i]]=D[diff[i]];
    const e=Math.floor(diff.length/2),fcount=diff.length%2;
    if(fcount)y[diff[e]]=null;
    const list=decode(x,N,K,q,B,y,e);
    check(list.includes(s)&&list.includes(u),"fault ambiguity");
    return {...witness,L:best,calibratedA:A,calibratedB:D,received:y,errors:e,erasures:fcount,candidates:list};
  }
  const negative=ambiguity(old,8,3,4,2);
  return {scope:"synthetic exact integer combinatorics; no physical or human evidence",seed:796,oracleChecks,decodeChecks,reductionChecks,cases,searches,enumerated_pilots:searches.reduce((s,x)=>s+x.count,0),negative,assertion_failures:0};
}
console.log(JSON.stringify(laboratory(), null, 2));
