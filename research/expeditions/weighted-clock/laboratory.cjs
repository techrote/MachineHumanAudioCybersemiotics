"use strict";
// Refs #744. Exact integer arithmetic; no dependencies.
const receipt = (function laboratory() {
  const check=(ok,msg)=>{if(!ok)throw Error(msg)};
  const prod=a=>a.reduce((x,y)=>x*y,1);
  const subsets=(a,k)=>k===0?[[]]:a.flatMap((p,i)=>subsets(a.slice(i+1),k-1).map(s=>[p,...s]));
  const small=a=>[1,2,3].flatMap(k=>subsets(a,k));
  const sum=a=>a.reduce((s,v)=>s+v,0n);
  const mod=(x,p)=>((x%p)+p)%p;
  const degree=ps=>small(ps).reduce((s,a)=>s+prod(a.map(p=>p-1)),0);
  let checks=0, literal=0, ensemble=0, negative=0;
  function leastPolynomial(ps) {
    const D=degree(ps), ex=new Map();
    for(const a of small(ps))for(let k=0;k<=a.length;k++)for(const b of subsets(a,k)){
      const q=prod(b);ex.set(q,(ex.get(q)||0)+((-1)**(a.length-k)));
    }
    // Formal power series expansion of product (1-z^q)^e, truncated at known degree.
    const w=Array(D+1).fill(0n);w[0]=1n;
    for(const [q,e] of ex) {
      for(let j=0;j<e;j++)for(let t=D;t>=q;t--)w[t]-=w[t-q];
      for(let j=0;j< -e;j++)for(let t=q;t<=D;t++)w[t]+=w[t-q];
    }
    check(w[D]===1n && sum(w)===BigInt(prod(ps)),"monic or mass");
    return w;
  }
  function positivePolynomial(ps) {
    let w=[1n], factors=[];
    for(let i=0;i<ps.length;i++){
      const p=ps[i], later=ps.slice(i+1);
      for(const a of subsets(later,Math.min(2,later.length))){
        const stride=prod(a), v=Array(w.length+(p-1)*stride).fill(0n);
        for(let t=0;t<v.length;t++)v[t]=(t>=stride?v[t-stride]:0n)+(w[t]||0n)-(t>=p*stride?(w[t-p*stride]||0n):0n);
        w=v;factors.push([p,stride]);
      }
    }
    check(w[0]===1n&&w.at(-1)===1n&&w.every(a=>a>=0n),"nonnegative factor compiler");
    return {w,factors};
  }
  function verifyMargins(w,ps) {
    const mass=sum(w);
    for(const a of small(ps)){
      const q=prod(a), b=Array(q).fill(0n);
      for(let t=0;t<w.length;t++)b[t%q]+=w[t];
      for(const v of b){check(v*BigInt(q)===mass,"margin "+q);checks++}
    }
  }
  function moment(ps,amps,r,a,b) {
    return BigInt(ps.reduce((s,p,i)=>{
      const n=new Set([0,mod(a,p),mod(b,p)]).size;
      return s+amps[i]**3*(n===1?(p-1)*(p-2):n===2?-(p-2):2);
    },0)*((-1)**mod(r,2)));
  }
  function actual(w,ps,amps,r,a,b,noise=[0],phase=0) {
    const u=Array.from({length:w.length+Math.max(a,b)},(_,t)=>
      ((-1)**mod(r,2))*ps.reduce((s,p,i)=>s+amps[i]*(mod(t+r,p)===0?p-1:-1),0)
      +((-1)**(t%2))*noise[mod(t+phase,noise.length)]);
    return w.reduce((s,v,t)=>s+v*BigInt(u[t]*u[t+a]*u[t+b]),0n);
  }
  const profiles=[];
  const fixtures=[[3,5,7,11],[2,3,5,7,11],[5,7,11,13,17],[2,5,7,11,13,17],[2,5,7,11,13,17,19]];
  for(const ps of fixtures){
    const l=leastPolynomial(ps),{w,factors}=positivePolynomial(ps);
    verifyMargins(l,ps);verifyMargins(w,ps);
    const P=prod(ps), mass=sum(w), ss=w.reduce((a,b)=>a+b*b,0n);
    const ni=l.findIndex(v=>v<0n);
    const privatePs=ps.filter(p=>p!==2);
    const amps=privatePs.map((_,i)=>[1,2,-3,1,-2,3][i]);
    for(const window of [l,w])for(const r of [0,1,19])for(const [a,b] of [[0,0],[0,1],[1,2],[0,5],[0,7],[2,9]]){
      check(actual(window,privatePs,amps,r,a,b)===sum(window)*moment(privatePs,amps,r,a,b),"literal clean");literal++;
    }
    if(ps[0]===2){
      for(const window of [l,w])for(const r of [0,1])for(const [a,b] of [[0,0],[0,1],[1,2],[0,7]])for(const noise of [[9],[0,0,9],[2,2,2,-7],[1,4,-2,8,8]]){
        let v=0n;for(let phase=0;phase<noise.length;phase++)v+=actual(window,privatePs,amps,r,a,b,noise,phase);
        check(v===BigInt(noise.length)*sum(window)*moment(privatePs,amps,r,a,b),"literal ensemble");ensemble++;
      }
    }
    profiles.push({primes:ps,equal_weight_minimum:P,least_signed_span:l.length-1,first_negative_index:ni,first_negative_coefficient:ni<0?null:String(l[ni]),negative_coefficients:l.filter(v=>v<0n).length,positive_span:w.length-1,nonzero_positive_weights:w.filter(v=>v>0n).length,weight_mass:String(mass),max_weight:String(w.reduce((a,b)=>a>b?a:b,0n)),weight_effective_count:Number(mass*mass)/Number(ss),factors});
  }
  // Pairwise-uniform but not triple-uniform: all pair margins exact.
  function pairwiseControl(ps,privatePs,bias){
    const f=(t,p)=>t%p===0?1:t%p===1?-1:0;
    const w=Array.from({length:prod(ps)},(_,t)=>BigInt(1+ps.reduce((a,p)=>a*f(t,p),1)));
    for(const a of [1,2].flatMap(k=>subsets(ps,k))){
      const q=prod(a), buckets=Array(q).fill(0n);
      for(let t=0;t<w.length;t++)buckets[t%q]+=w[t];
      check(buckets.every(v=>v*BigInt(q)===sum(w)),"pairwise control");negative++;
    }
    const amps=privatePs.map(()=>1);
    const v=actual(w,privatePs,amps,0,0,0,[bias]);
    const clean=moment(privatePs,amps,0,0,0);
    check(v-sum(w)*clean===sum(w)*6n*BigInt(bias||1),"third-order defect");negative++;
    return {primes:ps,bias,expected:String(clean),observed:String(v/sum(w))};
  }
  const controls=[pairwiseControl([3,5,7],[3,5,7],0),pairwiseControl([2,3,5],[3,5],1)];
  const ps=[2,5,7,11,13,17], n=positivePolynomial(ps).w.length;
  const uniform=Array(n).fill(1n);
  // Odd-length uniform acquisition cannot remove even a constant offset on a silent input.
  check(actual(uniform,[],[],0,0,0,[1])===1n,"uniform parity defect");negative++;
  // One-record coherent noise is not the ensemble: exact cancellation for any weights.
  const p5=Array.from({length:10},(_,t)=>-((-1)**t)*(t%5===0?4:-1));
  const w=positivePolynomial(ps).w;
  check(actual(w,[5],[1],0,0,5,p5,0)===0n,"coherent cancellation");
  check(moment([5],[1],0,0,5)!==0n,"clean nonzero");negative+=2;
  return {profiles,checks:{exact_residue_buckets:checks,literal_clean:literal,literal_stationary_ensemble:ensemble,negative_controls:negative,assertion_failures:0},controls,uniform_window_bias_defect:"1/"+n,coherent_cancellation:true};
})();
console.log(JSON.stringify(receipt, null, 2));
