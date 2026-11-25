"use strict";
// Exact rational fractional-delay stencils. Synthetic, not a production filter.
function gcd(a,b){a=a<0n?-a:a;b=b<0n?-b:b;while(b){[a,b]=[b,a%b]}return a}
function Q(n,d=1n){n=BigInt(n);d=BigInt(d);if(!d)throw Error("zero denominator");if(d<0n){n=-n;d=-d}const g=gcd(n,d);return [n/g,d/g]}
const add=(a,b)=>Q(a[0]*b[1]+b[0]*a[1],a[1]*b[1]);
const neg=a=>Q(-a[0],a[1]);
const sub=(a,b)=>add(a,neg(b));
const mul=(a,b)=>Q(a[0]*b[0],a[1]*b[1]);
const div=(a,b)=>Q(a[0]*b[1],a[1]*b[0]);
const eq=(a,b)=>a[0]===b[0]&&a[1]===b[1];
const lt=(a,b)=>a[0]*b[1]<b[0]*a[1];
const sum=a=>a.reduce(add,Q(0));
const pow=(a,k)=>{let v=Q(1);while(k--)v=mul(v,a);return v};
const fmt=a=>a[0]+"/"+a[1];
const negativeMass=h=>sum(h.filter(x=>x[0]<0n).map(neg));
function grid(nodes){
 if(!Array.isArray(nodes)||nodes.length<3||nodes.length>257||
 nodes.some((k,i)=>!Number.isSafeInteger(k)||Math.abs(k)>10000||(i&&k<=nodes[i-1]))||
 !nodes.includes(0)||!nodes.includes(1))throw Error("strict sorted integer grid with 0,1 and an extra tap required");
}
// Polynomial interpolation functional at x on a chosen subset.
function lagrange(nodes,x){
 return nodes.map((v,i)=>nodes.reduce((w,u,j)=>j===i?w:mul(w,div(sub(x,Q(u)),Q(v-u))),Q(1)));
}
// General degree-two optimum, arbitrary rational alpha in (0,1).
function quadratic(nodes,alpha){
 grid(nodes);if(!Array.isArray(alpha)||alpha.length!==2||typeof alpha[0]!=="bigint"||typeof alpha[1]!=="bigint")throw Error("rational pair required");
 alpha=Q(...alpha);if(!lt(Q(0),alpha)||!lt(alpha,Q(1)))throw Error("fractional offset must lie in (0,1)");
 const K=nodes.reduce((a,k)=>k*(k-1)>a*(a-1)?k:a);
 const M=K*(K-1);
 const b=div(mul(alpha,sub(Q(1),alpha)),Q(M));
 const h=nodes.map(k=>k===K?neg(b):k===1?add(alpha,mul(Q(K),b)):k===0?add(sub(Q(1),alpha),mul(Q(1-K),b)):Q(0));
 return {h,b,K,M};
}
// Half-sample symmetric optimum through degree 3 or 5.
// Shell j consists of nodes -j and j+1; t=(2j+1)^2 (four times centered square).
function half(L,degree){
 if(!Number.isInteger(L)||L<1||L>128||![3,5].includes(degree)||degree===5&&L<2)throw Error("invalid half-grid or degree");
 const t=Array.from({length:L+1},(_,j)=>(2*j+1)**2);
 let chosen=[0,L],M=0;
 if(degree===5){
  let j=1;for(let i=1;i<L;i++){const p=(t[i]-1)*(t[L]-t[i]);if(p>M){M=p;j=i}}
  chosen=[0,j,L];
 }
 const w=lagrange(chosen.map(j=>t[j]),Q(0));
 const nodes=Array.from({length:2*L+2},(_,i)=>i-L);
 const h=nodes.map(k=>{const j=k<=0?-k:k-1;const i=chosen.indexOf(j);return i<0?Q(0):div(w[i],Q(2))});
 return {nodes,h,b:negativeMass(h),chosen,t,M};
}
function moment(nodes,h,degree,x=Q(0)){
 return sum(nodes.map((k,i)=>mul(h[i],pow(sub(Q(k),x),degree))));
}
function* subsets(a,k,start=0,p=[]){
 if(k===0){yield p;return}
 for(let i=start;i<=a.length-k;i++)yield* subsets(a,k-1,i+1,[...p,a[i]]);
}
function verify(){
 const assert=(v,m)=>{if(!v)throw Error(m)};
 let quadraticCases=0,quadraticCandidates=0,halfCases=0,halfCandidates=0,dualChecks=0;
 // Independently enumerate all 3-node interpolation bases on each irregular grid.
 const pool=[-4,-3,-2,-1,2,3,4,5];
 for(let mask=1;mask<2**pool.length;mask++){
  const nodes=[0,1,...pool.filter((_,i)=>mask&(1<<i))].sort((a,b)=>a-b);
  for(let d=2;d<=7;d++)for(let p=1;p<d;p++){
   const x=Q(p,d),z=quadratic(nodes,x);quadraticCases++;
   for(let k=0;k<=2;k++)assert(eq(moment(nodes,z.h,k),pow(x,k)),"quadratic moment");
   assert(eq(negativeMass(z.h),z.b),"mass");
   let best=null;
   for(const a of subsets(nodes,3)){const b=negativeMass(lagrange(a,x));if(best===null||lt(b,best))best=b;quadraticCandidates++}
   assert(eq(best,z.b),"quadratic enumeration");
   for(const k of nodes){const q=Q(k*(k-1),z.M);assert(!lt(q,Q(0))&&!lt(Q(1),q),"dual");dualChecks++}
  }
 }
 for(const degree of [3,5])for(let L=degree===3?1:2;L<=128;L++){
  const z=half(L,degree);halfCases++;
  for(let k=0;k<=degree;k++)assert(eq(moment(z.nodes,z.h,k,Q(1,2)),Q(k===0?1:0)),"half moment");
  const R=Q(2*L+1,2);
  if(degree===3){
   assert(eq(z.b,Q(1,4*L*(L+1))),"cubic mass");
   assert(eq(moment(z.nodes,z.h,4,Q(1,2)),neg(div(pow(R,2),Q(4)))),"fourth moment");
  }else{
   assert(eq(z.b,Q(z.t[L],z.M)),"quintic mass");
   const a=z.chosen.map(j=>Q(z.t[j],4));
   assert(eq(moment(z.nodes,z.h,6,Q(1,2)),a.reduce(mul,Q(1))),"sixth moment");
   for(const t of z.t){const q=Q((t-1)*(z.t[L]-t),z.M);assert(!lt(q,Q(0))&&!lt(Q(1),q),"quartic dual");dualChecks++}
  }
  if(L<=24){
   let best=null;
   for(const a of subsets(z.t,(degree+1)/2)){const b=negativeMass(lagrange(a,Q(0)));if(best===null||lt(b,best))best=b;halfCandidates++}
   assert(eq(best,z.b),"half enumeration");
  }
  // Exact bounded-input overshoot witness.
  const y=sum(z.h.filter(v=>v[0]>0n));assert(eq(y,add(Q(1),z.b)),"peak witness");
 }
 let refused=0;for(const f of [()=>quadratic([0,1],Q(1,2)),()=>quadratic([0,1,2],Q(1)),()=>half(1,5),()=>half(0,3),()=>half(129,3)]){try{f()}catch(e){refused++}}
 assert(refused===5,"refusals");
 return {quadraticCases,quadraticCandidates,halfCases,halfCandidates,dualChecks,refused,examples:[1,2,4,8,16,32,64,128].map(L=>({L,cubic:fmt(half(L,3).b),quintic:L>1?fmt(half(L,5).b):null}))};
}
if(typeof module!=="undefined")module.exports={Q,quadratic,half,moment,negativeMass,verify,fmt};
if(typeof require!=="undefined"&&require.main===module)console.log(JSON.stringify(verify(),null,2));
