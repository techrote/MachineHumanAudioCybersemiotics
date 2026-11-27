"use strict";
// Refs #744. Exact primal-dual verification, no LP dependency.
const receipt = (function certificate(){
  const check=(ok,msg)=>{if(!ok)throw Error(msg)};
  const ps=[3,5,7,11],P=1155,D=674;
  // W0=(1+...+z^(P-1))/Phi_P(z); compute directly by formal
  // division using the square-free Mobius factorization of Phi_P.
  const L=Array(D+1).fill(1n);
  for(let mask=0;mask<16;mask++){
    let d=1,k=0;
    for(let i=0;i<4;i++)if(mask&(1<<i)){d*=ps[i];k++}
    const e=-((-1)**(4-k));
    if(e>0)for(let i=D;i>=d;i--)L[i]-=L[i-d];
    else for(let i=d;i<=D;i++)L[i]+=L[i-d];
  }
  check(L[0]===1n&&L[D]===1n&&L.reduce((a,b)=>a+b,0n)===BigInt(P),"least polynomial");
  // 3 times the floating-LP-discovered quotient, rationalized and checked exactly.
  const C=[1,-1,0,1,-1,1,0,0,0,0,1,-1,1,0,0,0,0,1,-1,1,0,-1,1].map(BigInt);
  const W=Array(D+C.length).fill(0n);
  for(let i=0;i<L.length;i++)for(let j=0;j<C.length;j++)W[i+j]+=L[i]*C[j];
  check(W.at(-1)===1n&&W.every(v=>v>=0n),"positive exact primal");
  const mass=W.reduce((a,b)=>a+b,0n);
  let marginChecks=0;
  for(const omit of ps){
    const q=P/omit,b=Array(q).fill(0n);
    for(let i=0;i<W.length;i++)b[i%q]+=W[i];
    for(const v of b){check(v*BigInt(q)===mass,"literal primal margin");marginChecks++}
  }
  // Twice the rational nonnegative dual weights. Certify every quotient
  // of degree <=21, not just those with nonnegative coefficients.
  const dual=[[19,1],[22,2],[25,3],[29,4],[30,2],[49,1],[51,1],[52,2],[53,4],[642,4],[643,2],[644,1],[646,1],[665,2],[666,4],[670,3],[673,2],[676,1]];
  const dot=Array.from({length:22},(_,j)=>dual.reduce((s,[i,v])=>s+BigInt(v)*(L[i-j]||0n),0n));
  check(dot.every(v=>v===-2n),"exact dual");
  return {primes:ps,least_signed_span:D,optimal_positive_span:W.length-1,weight_mass:String(mass),nonzero_weights:W.filter(x=>x>0n).length,largest_weight:String(W.reduce((a,b)=>a>b?a:b,0n)),quotient:C.map(String),dual_twice:dual,dual_dot_products:dot.map(String),literal_triple_margin_checks:marginChecks,assertion_failures:0};
})();
console.log(JSON.stringify(receipt, null, 2));
