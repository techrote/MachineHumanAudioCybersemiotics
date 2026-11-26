'use strict';
// Exact synthetic witness for MHAC #740. Run: node laboratory.cjs
function laboratory(){
 const assert=(v,msg)=>{if(!v)throw Error(msg)};
 const parity=t=>t%2===0?1:-1;
 const R=(p,t)=>t%p===0?p-1:-1;
 const prod=a=>a.reduce((x,y)=>x*y,1);
 const coef=(p,a,b)=>{const n=new Set([0,a%p,b%p]).size;return n===1?(p-1)*(p-2):n===2?-(p-2):2};
 const pred=(ps,w,a,b)=>ps.reduce((v,p,i)=>v+w[i]*coef(p,a,b),0);
 const sample=(ps,A,s,t)=>ps.reduce((v,p,i)=>v+A[i]*s[i]*R(p,t),0);
 const full=(ps,A,s,a,b,shift=0,raw=false)=>{
  const N=2*prod(ps);let total=0;
  for(let t=0;t<N;t++){
   const x=k=>parity(k+shift)*sample(ps,A,s,k+shift)*(raw?1:parity(k));
   total+=x(t)*x(t+a)*x(t+b);
  }
  assert(Number.isSafeInteger(total),"integer overflow");return total/N;
 };
 const rank=rows=>{
  let M=rows.map(r=>r.map(BigInt)), k=0;
  for(let j=0;j<M[0].length;j++){
   let i=M.findIndex((r,i)=>i>=k&&r[j]!==0n);if(i<0)continue;
   [M[k],M[i]]=[M[i],M[k]];
   for(i=k+1;i<M.length;i++)if(M[i][j]!==0n){
    const a=M[k][j],b=M[i][j];for(let l=j;l<M[i].length;l++)M[i][l]=a*M[i][l]-b*M[k][l];
   }
   k++;
  }return k;
 };
 let local=0,literal=0,rankChecks=0,noise=0,rawChecks=0,negative=0;
 for(const p of [3,5,7,11,13,17,19,23])
 for(let a=0;a<2*p;a++)for(let b=a;b<2*p;b++){
  let v=0;for(let t=0;t<p;t++)v+=R(p,t)*R(p,t+a)*R(p,t+b);
  assert(v===p*coef(p,a,b),"private coefficient");local++;
 }
 for(const ps of [[3,5],[5,7],[3,5,7],[5,7,11]]){
  const A=ps.map((_,i)=>i+1);
  for(let mask=0;mask<2**ps.length;mask++){
   const s=ps.map((_,i)=>mask>>i&1?-1:1), w=A.map((v,i)=>s[i]*v**3);
   for(let shift=0;shift<3;shift++)for(const [a,b] of [[0,0],[0,1],[1,2],[0,ps[0]],[0,ps[1]],[2,7],[3,11],[5,10]]){
    assert(full(ps,A,s,a,b,shift)===parity(shift)*pred(ps,w,a,b),"literal third");
    assert(full(ps,A,s,a,b,shift,true)===0,"raw odd blind");
    literal++;rawChecks++;
   }
  }
 }
 const pool=[3,5,7,11,13,17];
 for(let mask=1;mask<2**pool.length;mask++){
  const ps=pool.filter((_,i)=>mask>>i&1);
  for(let B=0;B<=17;B++){
   const rows=[];for(let a=0;a<=B;a++)for(let b=a;b<=B;b++)rows.push(ps.map(p=>coef(p,a,b)));
   const k=ps.filter(p=>p<=B).length;
   assert(rank(rows)===(B<2?Math.min(B+1,ps.length):k+Math.min(3,ps.length-k)),"aperture rank");rankChecks++;
  }
 }
 const ps=[3,5,7],A=[1,2,1],s=[1,-1,1],w=A.map((v,i)=>s[i]*v**3),N=2*prod(ps);
 // Random phase of a fixed periodic sequence is strictly stationary in ensemble.
 // Enumerate the entire independent uniform phase law, not a sampled estimate.
 const patterns=[[0,0,9],[2,2,2,-7],[1,4,-2,8,8]];
 for(const pat of patterns)for(let shift=0;shift<2;shift++)for(let a=0;a<=9;a++)for(let b=a;b<=9;b++){
  let sum=0;
  for(let t=0;t<N;t++)for(let u=0;u<pat.length;u++){
   const z=k=>parity(shift)*sample(ps,A,s,k+shift)+parity(k)*pat[(k+u)%pat.length];
   sum+=z(t)*z(t+a)*z(t+b);
  }
  assert(Number.isSafeInteger(sum),"noise overflow");
  assert(sum===N*pat.length*parity(shift)*pred(ps,w,a,b),"stationary skew noise");noise++;
 }
 // Unit-gain fixed-amplitude collision with a shared small anchor.
 const cp=[3,5,7,37,41,71,73], ca=cp.map(p=>[5,41,71].includes(p)?-1:1),
 cb=ca.map((v,i)=>i===0?v:-v);
 for(let a=0;a<=4;a++)for(let b=a;b<=4;b++){
  assert(pred(cp,ca,a,b)===pred(cp,cb,a,b),"unit amplitude collision");negative++;
 }
 assert(pred(cp,ca,0,5)!==pred(cp,cb,0,5),"larger aperture separates");negative++;
 // Stationary ensemble interference whose single realization erases the component.
 // n_u(t)=-(-1)^(t+u) R_5(t+u), uniform u in [0,10).
 let ensemble=0;const perPhase=[];
 for(let u=0;u<10;u++){
  let sums=[0,0];
  for(let t=0;t<10;t++){
   const z=k=>R(5,k)-parity(u)*R(5,k+u);
   sums[0]+=z(t)**2*z(t+5);sums[1]+=z(t)**2*z(t+1);
  }
  perPhase.push((sums[0]-sums[1])/10);ensemble+=sums[0]-sums[1];
 }
 assert(ensemble===10*10*15&&perPhase[0]===0&&perPhase[5]===120,"ensemble versus record");negative++;
 // Explicit five-prime compiler: three baseline receipts plus two isolated low primes.
 const p5=[5,7,11,13,17],w5=[1,8,-27,1,-8];
 const baseline=[[0,0],[0,1],[1,2],[0,5],[0,7]].map(([a,b])=>pred(p5,w5,a,b));
 assert(baseline[3]-baseline[1]===15&&baseline[4]-baseline[1]===280,"individual receipts");
 const large=p5.slice(2), rem=baseline.slice(0,3).map((v,j)=>v-pred(p5.slice(0,2),w5.slice(0,2),...[ [0,0],[0,1],[1,2] ][j]));
 const matrix=[[0,0],[0,1],[1,2]].map(([a,b])=>large.map(p=>coef(p,a,b)));
 // Brute exact inverse via Cramer's rule, a separate recovery witness.
 const det=m=>m[0][0]*(m[1][1]*m[2][2]-m[1][2]*m[2][1])-m[0][1]*(m[1][0]*m[2][2]-m[1][2]*m[2][0])+m[0][2]*(m[1][0]*m[2][1]-m[1][1]*m[2][0]);
 const decoded=[0,1,2].map(i=>det(matrix.map((r,j)=>r.map((v,k)=>k===i?rem[j]:v)))/det(matrix));
 assert(JSON.stringify(decoded)===JSON.stringify(w5.slice(2)),"compiler inverse");
 return {local_moment_identities:local,literal_demodulated_triples:literal,raw_third_negative_controls:rawChecks,exact_rank_checks:rankChecks,exact_stationary_noise_profiles:noise,collision_and_coherence_negative_checks:negative,five_prime:{primes:p5,receipts:baseline,recovered:[1,8,...decoded],minimum_aperture:7},coherent_noise_per_phase:perPhase,coherent_noise_ensemble:ensemble/100,failures:0};
}
console.log(JSON.stringify(laboratory(), null, 2));
