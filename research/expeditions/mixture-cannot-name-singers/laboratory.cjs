// Standard Node.js, no dependencies. Synthetic exact arithmetic only.
"use strict";
const assert = require("node:assert/strict");
function choose(n,k) {
  let v=1n;
  for(let j=1;j<=k;j++) v=v*BigInt(n-j+1)/BigInt(j);
  return v;
}
function subsets(n,k,start=0,acc=[]) {
  if(k===0) return [acc];
  let out=[];
  for(let j=start;j<=n-k;j++) out.push(...subsets(n,k-1,j+1,[...acc,j]));
  return out;
}
function dictionary(B,N,L=N+1) {
  return Array.from({length:B},(_,j)=>Array.from({length:N},(_,i)=>
    choose(B-1,j)*BigInt(i+1)**BigInt(j)*BigInt(L-i-1)**BigInt(B-1-j)));
}
function determinant(a) {
  const n=a.length;
  if(n===0) return 1n;
  a=a.map(r=>r.slice());
  let prev=1n,sign=1n;
  for(let k=0;k<n-1;k++){
    let p=k;
    while(p<n && a[p][k]===0n) p++;
    if(p===n) return 0n;
    if(p!==k){[a[p],a[k]]=[a[k],a[p]];sign=-sign;}
    const pivot=a[k][k];
    for(let i=k+1;i<n;i++) for(let j=k+1;j<n;j++){
      const x=a[i][j]*pivot-a[i][k]*a[k][j];
      assert.equal(x%prev,0n);
      a[i][j]=x/prev;
    }
    for(let i=k+1;i<n;i++) a[i][k]=0n;
    prev=pivot;
  }
  return sign*a[n-1][n-1];
}
function mul(A,c) {return A.map(r=>r.reduce((s,v,i)=>s+v*c[i],0n));}
function run(){
  let minorChecks=0, witnessChecks=0, rowChecks=0, errorErasureChecks=0, profiles=[];
  const idx=n=>Array.from({length:n},(_,i)=>i);
  for(let B=2;B<=8;B++){
    const N=9, A=dictionary(B,N);
    for(let s=1;s<=B;s++)
      for(const R of subsets(B,s)) for(const C of subsets(N,s)){
        assert(determinant(R.map(j=>C.map(i=>A[j][i])))>0n);
        minorChecks++;
      }
    for(let s=1;s<B;s++){
      for(const R of subsets(B,s)) for(const C of subsets(N,s+1)){
        const V=R.map(j=>C.map(i=>A[j][i]));
        const c=C.map((_,l)=>(l%2?-1n:1n)*determinant(V.map(r=>r.filter((_,j)=>j!==l))));
        assert(c.every((v,j)=>j%2?v<0n:v>0n));
        const P=mul(A.map(r=>C.map(i=>r[i])),c.map(v=>v>0n?v:0n));
        const Q=mul(A.map(r=>C.map(i=>r[i])),c.map(v=>v<0n?-v:0n));
        const diff=idx(B).filter(j=>P[j]!==Q[j]);
        assert.deepEqual(diff,idx(B).filter(j=>!R.includes(j)));
        witnessChecks++;rowChecks+=B;
        // Exact same received record with e erasures and at most t errors in each world.
        // Erase e of the differing rows, split the remaining ones evenly.
        for(let e=0;e<=diff.length;e++){
          const live=diff.slice(e),t=Math.ceil(live.length/2);
          const erase=new Set(diff.slice(0,e)), takeQ=new Set(live.slice(0,t));
          let ep=0,eq=0;
          for(let j=0;j<B;j++) if(!erase.has(j)){
            const y=takeQ.has(j)?Q[j]:P[j];
            if(y!==P[j]) ep++;
            if(y!==Q[j]) eq++;
          }
          assert(ep<=t&&eq<=t);
          errorErasureChecks++;
        }
      }
    }
    profiles.push({B,N});
  }
  const collisions=[];
  for(const [B,s] of [[3,3],[4,4],[5,4]]){
    const A=dictionary(B,5,6), C=idx(s+1);
    const c=C.map((_,i)=>(i%2?-1n:1n)*choose(s,i));
    const P=mul(A.map(r=>C.map(i=>r[i])),c.map(v=>v>0n?v:0n));
    const Q=mul(A.map(r=>C.map(i=>r[i])),c.map(v=>v<0n?-v:0n));
    assert.equal(P.every((v,j)=>v===Q[j]),B<=s);
    collisions.push({B,positive:c.map(v=>String(v>0n?v:0n)),negative:c.map(v=>String(v<0n?-v:0n)),
      denominator:String(2n**BigInt(s-1)*6n**BigInt(B-1)),P:P.map(String),Q:Q.map(String)});
  }
  let conditioning=[];
  for(let k=1;k<=5;k++) for(const L of [20,100,1000]){
    const m=2*k-1,B=m+1,A=dictionary(B,B,L);
    const c=idx(B).map(i=>(i%2?-1n:1n)*choose(m,i));
    const delta=mul(A,c),abs=x=>x<0n?-x:x;
    const fac=idx(m).reduce((a,b)=>a*BigInt(b+1),1n);
    assert.equal(delta.reduce((a,b)=>a+abs(b),0n),2n**BigInt(m)*fac);
    conditioning.push({k,L,TV_numerator:String(fac),TV_denominator:String(BigInt(L)**BigInt(m))});
  }
  return {minorChecks,witnessChecks,rowChecks,errorErasureChecks,profiles,collisions,conditioning,assertions:"PASS"};
}
module.exports={run};
if(require.main===module) console.log(JSON.stringify(run(),null,2)+"\n");
