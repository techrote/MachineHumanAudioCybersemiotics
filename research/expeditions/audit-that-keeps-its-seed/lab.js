'use strict';
// Exact finite missing-label audit. Node.js, no dependencies. Integer coefficient units.
const assert=(ok,msg='assertion failed')=>{if(!ok)throw Error(msg)};
const gcd=(a,b)=>b===0n?a:gcd(b,a%b);
const lcm=(a,b)=>a/gcd(a,b)*b;
const ratio=(a,b)=>{assert(b>0n);const g=gcd(a,b);return (a/g).toString()+'/'+(b/g).toString()};
function model(weights){
 if(!Array.isArray(weights)||weights.length<2||weights.length>64||weights.some(x=>!Number.isSafeInteger(x)))throw Error('2..64 safe integer weights required');
 const w=weights.map(BigInt),n=w.length,edges=[];let L=1n,zero=-1;
 for(let i=0;i<n;i++)for(let j=i+1;j<n;j++){
  const d=w[i]>w[j]?w[i]-w[j]:w[j]-w[i];if(d===0n)zero=edges.length;else L=lcm(L,d);
  edges.push({i,j,d});
 }
 return {n,w,edges,L,zero};
}
// x_e=u_e/2; objective F=sum x_e/d_e; score=2L F.
function primal(m){
 if(m.n>7)throw Error('exhaustive primal cap 7');
 if(m.zero>=0)return {zero:true};
 const {n,edges,L}=m,deg=Array(n).fill(0),u=Array(edges.length).fill(0);
 let best=-1n,witness=null,leaves=0;
 function walk(e,s){
  if(e===edges.length){leaves++;if(s>best){best=s;witness=u.slice()}return;}
  const {i,j,d}=edges[e],v=L/d;
  for(let q=0;q<=Math.min(2-deg[i],2-deg[j]);q++){
   u[e]=q;deg[i]+=q;deg[j]+=q;walk(e+1,s+BigInt(q)*v);deg[i]-=q;deg[j]-=q;
  }
  u[e]=0;
 }
 walk(0,0n);return {score:best,u:witness,leaves};
}
// Independent dual vertex enumeration. y_i in units 1/(2L).
// Solve active equations by exact integer elimination; nonsingular incidence
// systems have integral solutions at this scale (anchor or odd cycle).
function solve(rows,n){
 const a=rows.map(r=>r.slice());
 for(let i=0;i<n;i++){
  let k=i;while(k<n&&a[k][i]===0n)k++;if(k===n)return null;
  [a[i],a[k]]=[a[k],a[i]];
  for(let j=i+1;j<n;j++){
   const v=a[j][i],p=a[i][i];if(v===0n)continue;
   for(let t=i;t<=n;t++)a[j][t]=p*a[j][t]-v*a[i][t];
  }
 }
 const x=Array(n).fill(0n);
 for(let i=n-1;i>=0;i--){
  let b=a[i][n];for(let j=i+1;j<n;j++)b-=a[i][j]*x[j];
  assert(b%a[i][i]===0n,'nonintegral scaled dual vertex');
  x[i]=b/a[i][i];
 }
 return x;
}
function dual(m){
 if(m.n>5||m.zero>=0)throw Error('dual cap 5; distinct weights required');
 const {n,edges,L}=m,rows=[];
 for(let i=0;i<n;i++){let r=Array(n+1).fill(0n);r[i]=1n;rows.push(r)}
 for(const {i,j,d} of edges){let r=Array(n+1).fill(0n);r[i]=r[j]=1n;r[n]=2n*L/d;rows.push(r)}
 let best=null,y=null,vertices=0,systems=0;
 function walk(start,chosen){
  if(chosen.length===n){
   systems++;const x=solve(chosen,n);if(!x||x.some(v=>v<0n)||edges.some(({i,j,d})=>x[i]+x[j]<2n*L/d))return;
   vertices++;const s=x.reduce((a,b)=>a+b,0n);if(best===null||s<best){best=s;y=x;}return;
  }
  for(let i=start;i<=rows.length-(n-chosen.length);i++)walk(i+1,[...chosen,rows[i]]);
 }
 walk(0,[]);assert(best!==null);return {score:best,y,vertices,systems};
}
function checkCertificate(m,u,y){
 const {n,edges,L}=m;assert(m.zero<0&&u.length===edges.length&&y.length===n);
 const deg=Array(n).fill(0);let s=0n;
 edges.forEach(({i,j,d},e)=>{const q=u[e];assert(Number.isInteger(q)&&q>=0&&q<=2);deg[i]+=q;deg[j]+=q;s+=BigInt(q)*L/d;assert(y[i]+y[j]>=2n*L/d)});
 assert(deg.every(v=>v<=2)&&y.every(v=>typeof v==='bigint'&&v>=0n)&&s>0n);
 assert(s===y.reduce((a,b)=>a+b,0n),'primal/dual gap');
 // Direct expectation: pair probability is q*L/(d*s).
 // Loss on world j is d only when j remains in the retained pair.
 let numerator=Array(n).fill(0n),mass=0n,lower=null;
 edges.forEach(({i,j,d},e)=>{
  const p=BigInt(u[e])*L/d;mass+=p;
  for(let z=0;z<n;z++)if(z===i||z===j)numerator[z]+=p*d;
  const z=d*(y[i]+y[j]);if(lower===null||z<lower)lower=z;
 });
 assert(mass===s&&numerator.reduce((a,b)=>a>b?a:b)===2n*L&&lower===2n*L);
 return {width:ratio(2n*L,s),hardPrior:y.map(v=>ratio(v,s)),worldWidths:numerator.map(v=>ratio(v,s)),pairProbabilities:edges.flatMap(({i,j},e)=>u[e]?[{pair:[i,j],p:ratio(BigInt(u[e])*L/edges[e].d,s)}]:[])};
}
function regular(n,step=1){
 if(!Number.isInteger(n)||n<2||n>64||!Number.isSafeInteger(step)||step<1||!Number.isSafeInteger((n-1)*step))throw Error('invalid regular design');
 const m=model(Array.from({length:n},(_,i)=>i*step)),u=Array(m.edges.length).fill(0);
 const put=(i,j,q)=>{const e=m.edges.findIndex(e=>e.i===i&&e.j===j);assert(e>=0);u[e]=q};
 const end=n%2?n-3:n;
 for(let i=0;i<end;i+=2)put(i,i+1,2);
 if(n%2){put(n-3,n-2,1);put(n-2,n-1,1);put(n-3,n-1,1)}
 const D=BigInt(step);const y=Array.from({length:n},(_,i)=>n%2?BigInt(i%2?3:1)*m.L/(2n*D):m.L/D);
 assert(n%2===0||m.L%(2n*D)===0n);
 return {m,u,y,...checkCertificate(m,u,y)};
}
function* subsets(n,k,start=0,p=[]){
 if(k===0){yield p;return}
 for(let i=start;i<=n-k;i++)yield* subsets(n,k-1,i+1,[...p,i]);
}
function* compositions(total,slots,p=[]){
 if(slots===1){yield [...p,total];return}
 for(let i=0;i<=total;i++)yield* compositions(total-i,slots-1,[...p,i]);
}
// Direct reveal simulation; does not use pair-load or fractional matching formula.
function revealWidth(w,query,positive){
 let seen=false;const remaining=new Set(w.map((_,i)=>i));
 for(const i of query){remaining.delete(i);if(i===positive)seen=true}
 if(seen)return 0;
 const a=[...remaining].map(i=>w[i]);return Math.max(...a)-Math.min(...a);
}

// Restrict all seed/world widths to at most one lattice step.
// Matching construction + cover certificate for the path graph.
function capped(n,step=1){
 const m=regular(n,step).m;
 const k=Math.floor(n/2),D=BigInt(step);
 const pairs=Array.from({length:k},(_,i)=>[2*i,2*i+1]);
 const cover=Array.from({length:n},(_,i)=>i%2===1?1:0);
 for(const {i,j,d} of m.edges)if(d===D)assert(cover[i]+cover[j]===1);
 assert(cover.reduce((a,b)=>a+b,0)===k);
 const w=m.w.map(Number);
 for(let z=0;z<n;z++){
  let sum=0;for(const [i,j] of pairs)sum+=revealWidth(w,w.map((_,t)=>t).filter(t=>t!==i&&t!==j),z);
  assert(sum<=step);
 }
 return ratio(D,BigInt(k));
}

function tests(){
 let general=0,systems=0,leaves=0,regularChecks=0,gridChecks=0,revealChecks=0,capChecks=0;
 for(let n=2;n<=5;n++)for(const w of subsets(6,n)){
  const m=model(w),p=primal(m),d=dual(m);
  assert(p.score===d.score);checkCertificate(m,p.u,d.y);general++;systems+=d.systems;leaves+=p.leaves;
 }
 for(let n=2;n<=64;n++)for(const step of [1,2,7]){
  const r=regular(n,step);
  assert(r.width===(n%2?ratio(4n*BigInt(step),BigInt(2*n-1)):ratio(2n*BigInt(step),BigInt(n))));
  if(n<=7){let p=primal(r.m);assert(p.score===r.y.reduce((a,b)=>a+b,0n));leaves+=p.leaves}
  assert(capped(n,step)===ratio(BigInt(step),BigInt(Math.floor(n/2))));capChecks++;regularChecks++;
 }
 for(const n of [3,4]){
  const w=Array.from({length:n},(_,i)=>i),r=regular(n),D=10;
  const pairs=r.m.edges.map(({i,j})=>w.map((_,k)=>k).filter(k=>k!==i&&k!==j));
  let best=Infinity;
  for(const p of compositions(D,pairs.length)){
   let worst=0;
   for(let z=0;z<n;z++){let s=0;for(let e=0;e<p.length;e++){s+=p[e]*revealWidth(w,pairs[e],z);revealChecks++}worst=Math.max(worst,s)}
   best=Math.min(best,worst);gridChecks++;
  }
  assert(best===(n===3?8:5),'grid optimum');
 }
 for(let n=2;n<=8;n++){
  const w=Array.from({length:n},(_,i)=>i*i);
  for(const {i,j} of model(w).edges){
   const q=w.map((_,k)=>k).filter(k=>k!==i&&k!==j);
   for(let z=0;z<n;z++){
    assert(revealWidth(w,q,z)===(z===i||z===j?w[j]-w[i]:0));
    assert(revealWidth(w,q.slice().reverse(),z)===revealWidth(w,q,z));revealChecks+=2;
   }
  }
 }
 assert(primal(model([2,2,9])).zero);
 assert(regular(2).width==='1/1'&&regular(3).width==='4/5');
 assert(regular(4).width==='1/2'&&regular(5).width==='4/9');
 assert(regular(3).hardPrior.join(',')==='1/5,3/5,1/5');
 let refusals=0;
 for(const bad of [[],[1],[1,1.5],[NaN,2],null]){
  try{model(bad)}catch{refusals++;continue}throw Error('invalid input accepted');
 }
 return {general,systems,leaves,regularChecks,capChecks,gridChecks,revealChecks,refusals,three:(({width,hardPrior,worldWidths,pairProbabilities})=>({width,hardPrior,worldWidths,pairProbabilities}))(regular(3))};
}
if(typeof module!=='undefined'){module.exports={model,primal,dual,checkCertificate,regular,tests};if(require.main===module)console.log(JSON.stringify(tests(),null,2))}
