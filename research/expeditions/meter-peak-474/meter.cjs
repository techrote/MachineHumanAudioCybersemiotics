"use strict";
// Exact integer circular window inverse; no dependencies. See README for domain.
const gcd=(a,b)=>b?gcd(b,a%b):a;
function choose(n,k){
  let b=1n;
  for(let i=1;i<=k;i++) b=b*BigInt(n-k+i)/BigInt(i);
  return b;
}
function windows(x,w){
  const n=x.length, a=[x.slice(0,w).reduce((s,v)=>s+v,0)];
  for(let i=1;i<n;i++) a.push(a[i-1]-x[i-1]+x[(i-1+w)%n]);
  return a;
}
function solve(n, streams){
  if(!Number.isInteger(n)||n<1||n>256||!Array.isArray(streams)||!streams.length||streams.length>n)
    throw new RangeError("n=1..256; one or more distinct width streams required");
  const widths=new Set();
  for(const s of streams){
    if(!s||!Number.isInteger(s.width)||s.width<1||s.width>n||widths.has(s.width)||
       !Array.isArray(s.sums)||s.sums.length!==n||
       Array.from(s.sums).some(v=>!Number.isInteger(v)||v<0||v>1e9))
      throw new RangeError("invalid width or reading (integer 0..1e9)");
    widths.add(s.width);
  }
  const g=[...widths].reduce(gcd,n), adj=Array.from({length:n},()=>[]);
  const fail=reason=>({status:"inconsistent",reason});
  for(const {width:w,sums:a} of streams){
    for(let i=0;i<n;i++){
      const j=(i+w)%n, d=a[(i+1)%n]-a[i];
      adj[i].push([j,d]); adj[j].push([i,-d]);
    }
  }
  const base=Array(n).fill(null), range=[];
  for(let r=0;r<g;r++){
    base[r]=0;
    const q=[r];
    for(let k=0;k<q.length;k++){
      const i=q[k];
      for(const [j,d] of adj[i]){
        const t=base[i]+d;
        if(base[j]===null){base[j]=t;q.push(j);}
        else if(base[j]!==t)return fail("contradictory differences");
      }
    }
    const lo=Math.min(...q.map(i=>base[i]));
    for(const i of q)base[i]-=lo;
    range.push(Math.max(...q.map(i=>base[i])));
  }
  let S=null;
  for(const {width:w,sums:a} of streams){
    const b=windows(base,w), factor=w/g, delta=a[0]-b[0];
    if(delta<0||delta%factor!==0||a.some((v,i)=>v-b[i]!==delta))
      return fail("negative, nonintegral or varying residue budget");
    const s=delta/factor;
    if(S!==null&&S!==s)return fail("incompatible width budgets");
    S=s;
  }
  const maximumRange=Math.max(...range);
  const minPeak=Math.max(maximumRange,Math.ceil((S+range.reduce((a,b)=>a+b,0))/g));
  const maxPeak=maximumRange+S;
  let left=S;
  const lowOffsets=range.map(v=>{const a=Math.min(left,minPeak-v);left-=a;return a;});
  if(left!==0)throw Error("internal allocation");
  const highOffsets=range.map((_,r)=>r===range.indexOf(maximumRange)?S:0);
  const trace=z=>base.map((v,i)=>v+z[i%g]);
  return {status:S===0||g===1?"unique":"ambiguous",g,base,range,budget:S,
    count:choose(S+g-1,g-1).toString(),minPeak,maxPeak,
    lowWitness:trace(lowOffsets),highWitness:trace(highOffsets)};
}
function classify(result,threshold){
  if(!Number.isInteger(threshold)||threshold<0)throw new RangeError("nonnegative integer threshold");
  if(result.status==="inconsistent")return "inconsistent";
  if(result.minPeak>=threshold)return "certain-at-or-above";
  if(result.maxPeak<threshold)return "certain-below";
  return "undetermined";
}
module.exports={solve,windows,classify};
