'use strict';
// Exact bounded integer witness; all products stay within Number safe-integer range.
function lab(){
  "use strict";
  const assert=(v,m="assertion")=>{if(!v)throw Error(m)};
  const sum=a=>a.reduce((x,y)=>x+y,0);
  const pop=x=>{let n=0;for(;x;x&=x-1)n++;return n};
  const compositions=function*(n,k){if(k===1){yield [n];return}for(let i=0;i<=n;i++)for(const tail of compositions(n-i,k-1))yield [i,...tail]};
  const less=(a,b)=>a[0]*b[1]<b[0]*a[1];
  const le=(a,b)=>a[0]*b[1]<=b[0]*a[1];
  const eq=(a,b)=>le(a,b)&&le(b,a);
  const min=(a,b)=>less(a,b)?a:b;
  const f=(t,q0,q1)=>[sum(q0.map((v,i)=>Math.abs(t[0]*v-t[1]*q1[i]))),t[1]]; // in row-mass units
  function optimal(q0,q1,L){
    assert(q0.length===q1.length&&q0.length>0&&q0.every(x=>Number.isSafeInteger(x)&&x>=0)&&q1.every(x=>Number.isSafeInteger(x)&&x>=0)&&sum(q0)===sum(q1)&&sum(q0)>0,"invalid channel");
    assert(L.length===2&&Number.isSafeInteger(L[0])&&Number.isSafeInteger(L[1])&&L[0]>=0&&L[1]>0,"invalid cap");
    const candidates=[[0,1],L,...q0.flatMap((v,i)=>v&&le([q1[i],v],L)?[[q1[i],v]]:[])];
    let t=candidates[0],loss=f(t,q0,q1);
    for(const s of candidates){const v=f(s,q0,q1);if(less(v,loss)){t=s;loss=v}}
    return {t,loss};
  }
  let channelChecks=0,midpointChecks=0,gridChecks=0,asymChecks=0,symChecks=0,dominanceChecks=0,negative=0,refusals=0;
  for(const G of [3,5,7,9])for(let p=1;p<=8;p++){
    const L=[(G-1)*(8-p),p], m=min([1,1],L), mid=[m[0],2*m[1]];
    for(const k of [1,2,3]){
      const rows=[...compositions(6,k)];
      for(const q0 of rows)for(const q1 of rows){
        const o=optimal(q0,q1,L);channelChecks++;
        // Direct uniform grid of feasible t values, rather than using ratio breakpoints.
        for(let j=0;j<=48;j++){
          const s=[j*L[0],48*L[1]];
          assert(le(o.loss,f(s,q0,q1)),"breakpoint vs grid");gridChecks++;
        }
        const loss=f(mid,q0,q1);
        assert((loss[0]*o.loss[1]-o.loss[0]*loss[1])*mid[1]<=6*mid[0]*loss[1]*o.loss[1],"robust midpoint");
        midpointChecks++;
      }
    }
    const pooled=optimal([6],[6],L),full=optimal([6,0],[0,6],L);
    assert(eq(full.loss,[6,1]));
    assert(eq(pooled.loss,[6*(m[1]-m[0]),m[1]]));
    for(const [q0,q1,o] of [[[6],[6],pooled],[[6,0],[0,6],full]]){
      const v=f(mid,q0,q1);
      assert((v[0]*o.loss[1]-o.loss[0]*v[1])*mid[1]===6*mid[0]*v[1]*o.loss[1],"endpoint sharpness");
    }
  }
  // Enumerate six independently chosen local probabilities for G=3.
  // This does not assume recipient symmetry.
  const views=[[[6],[6]],[[6,0],[0,6]],[[4,2],[2,4]],[[3,2,1],[1,1,4]],[[3,2],[5,0]]];
  const words=[0,3,5,6],K=4;
  for(const [q0,q1] of views){
    const D=sum(q0),opt=optimal(q0,q1,[2,1]).loss;
    for(let index=0;index<5**6;index++){
      let c=index;
      const enc=Array.from({length:3},()=>[0,1].map(()=>{const a=c%5;c=Math.floor(c/5);return [a,K-a]}));
      const laws=enc.map((row,g)=>{
        const out=Array(words.length*q0.length).fill(0);
        for(let b=0;b<2;b++){
          const allowed=words.filter(w=>((w>>g)&1)===b),q=b?q1:q0;
          allowed.forEach((w,j)=>q.forEach((v,z)=>out[z*4+words.indexOf(w)]+=v*row[b][j]));
        }
        assert(sum(out)===2*K*D);return out;
      });
      let raw=0;
      for(let g=0;g<3;g++)for(let h=0;h<g;h++)raw=Math.max(raw,sum(laws[g].map((v,i)=>Math.abs(v-laws[h][i]))));
      assert(raw*2*opt[1]>=2*K*opt[0],"asymmetric beats optimum");
      asymChecks++;
    }
  }
  // Direct word probabilities for arbitrary symmetric weight mixtures.
  // Multiply each probability by a common integer M to avoid rounding.
  const gcd=(a,b)=>b?gcd(b,a%b):a;
  const lcm=(a,b)=>a/gcd(a,b)*b;
  for(const G of [3,5,7]){
    const W=Array.from({length:2**G},(_,i)=>i).filter(w=>pop(w)%2===0);
    const weights0=Array.from({length:(G+1)/2},(_,i)=>2*i),weights1=weights0.slice(1);
    const count=(b,w)=>W.filter(x=>(x&1)===b&&pop(x)===w).length;
    const M=[...weights0.map(w=>count(0,w)),...weights1.map(w=>count(1,w))].reduce(lcm,1);
    for(const a of compositions(3,weights0.length))for(const b of compositions(3,weights1.length)){
      const Aw=sum(a.map((v,i)=>v*weights0[i])),Bw=sum(b.map((v,i)=>v*(G-weights1[i])));
      for(const [q0,q1] of views){
        const D=sum(q0);
        const law=g=>q0.flatMap((_,z)=>W.map(w=>{
          const bit=(w>>g)&1,weights=bit?weights1:weights0,counts=bit?b:a,weight=pop(w);
          return (bit?q1[z]:q0[z])*counts[weights.indexOf(weight)]*M/count(bit,weight);
        }));
        const u=law(0),v=law(1),raw=sum(u.map((x,i)=>Math.abs(x-v[i])));
        assert(sum(u)===6*D*M&&sum(v)===6*D*M);
        let formula=0;
        for(let z=0;z<q0.length;z++)for(let i=1;i<weights0.length;i++){
          const w=weights0[i];formula+=Math.abs(q0[z]*a[i]*w-q1[z]*b[i-1]*(G-w));
        }
        assert(raw*(G-1)===2*M*formula,"weight TV formula");symChecks++;
        // Replacement t=Aw/Bw, with B reduced to its lower bound; feasible cap G-1.
        assert(Aw<=Bw*(G-1));
        const replacement=f([Aw,Bw],q0,q1);
        assert(3*replacement[0]<=formula*replacement[1],"universal dominance");dominanceChecks++;
      }
    }
  }
  // Unusual cue: optimum exceeds pooled t=1.
  assert(eq(optimal([3,2],[5,0],[2,1]).t,[5,3]));negative++;
  // Fair cue tied to private encoder coin: same cue marginal for all g but disjoint (word,cue) laws.
  const supports=Array.from({length:3},(_,g)=>[0,1].map(z=>`${(1<<g)|(1<<((g+1+z)%3))}:${z}`));
  for(let g=0;g<3;g++)for(let h=0;h<g;h++)assert(supports[g].every(x=>!supports[h].includes(x)));
  negative++;
  // Even G: all zero/all one both legal, independent of recipient.
  for(const G of [2,4,6,8])assert(pop(2**G-1)%2===0);
  negative++;
  for(const bad of [[[],[],[1,1]],[[1],[2],[1,1]],[[1],[-1],[1,1]],[[1],[1],[1,0]],[[1,0],[1],[1,1]]]){
    let caught=false;try{optimal(...bad)}catch{caught=true}assert(caught,"invalid accepted");refusals++;
  }
  return {channelChecks,midpointChecks,gridChecks,asymChecks,symChecks,dominanceChecks,negative,refusals};
}
const counts = lab();
console.log(JSON.stringify(counts,null,2));
