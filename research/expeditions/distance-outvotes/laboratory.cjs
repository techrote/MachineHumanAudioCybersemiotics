'use strict';
function run(){
 const assert=(x,m)=>{if(!x)throw Error(m)};
 const ps=[3,5,7], P=105, D=13, Q=1009;
 const times=[1,2,9,11,22,25,26,27,33,47,52,56,63,64,70,72,76,80,83,94,95,98];
 const h=[1,-1,0,-1,-1,-1,-1,1,0,1,0,0,0];
 const row=(t,pr=ps)=>[1,...pr.flatMap(p=>Array.from({length:p-1},(_,i)=>+(t%p===i+1)))];
 const dot=(a,b)=>a.reduce((s,x,i)=>s+x*b[i],0);
 const mod=x=>((x%Q)+Q)%Q;
 function inv(x){let a=1,b=x,n=Q-2;while(n){if(n%2)a=mod(a*b);b=mod(b*b);n=Math.floor(n/2)}return a}
 function rank(A){
   let a=A.map(r=>r.map(mod)), k=0;
   for(let j=0;j<a[0].length&&k<a.length;j++){
     let i=k;while(i<a.length&&!a[i][j])i++;if(i===a.length)continue;
     [a[k],a[i]]=[a[i],a[k]];let c=inv(a[k][j]);a[k]=a[k].map(x=>mod(x*c));
     for(let i=k+1;i<a.length;i++){c=a[i][j];if(c)for(let l=j;l<a[i].length;l++)a[i][l]=mod(a[i][l]-c*a[k][l])}k++;
   }return k;
 }
 const A=times.map(t=>row(t)), w=A.map(r=>dot(r,h));
 assert(JSON.stringify(w.map((v,i)=>[times[i],v]).filter(x=>x[1]))===JSON.stringify([[76,-1],[80,2],[95,1]]),'witness');
 let deletions=0;
 for(let i=0;i<A.length;i++)for(let j=i+1;j<A.length;j++){
   assert(rank(A.filter((_,k)=>k!==i&&k!==j))===D,'rank deletion');deletions++;
 }
 // Any full-rank minor mod prime is a nonzero integer minor over R.
 let family=[];
 for(let k=1;k<=20;k++){
   const ts=Array.from({length:k},(_,i)=>times.filter(t=>i===0||t!==76).map(t=>t+i*P)).flat();
   assert(new Set(ts).size===ts.length,'distinct timestamps');
   const v=ts.map(t=>dot(row(t),h));
   const z=v.map(x=>x===2?2:0);
   const dist=v.filter(Boolean).length, truth=z.reduce((s,x)=>s+Math.abs(x),0), alternative=z.reduce((s,x,i)=>s+Math.abs(x-v[i]),0);
   assert(dist===2*k+1&&truth===2*k&&alternative===k+1,'family identity');
   family.push({k,observations:ts.length,distance:dist,errors:k,trueLAD:truth,alternativeLAD:alternative});
 }
 // Full Cartesian decoder via disjoint paired contrasts, plus a median intercept.
 const median=a=>{assert(a.length>0,'no votes');a=a.slice().sort((a,b)=>a-b);return a[Math.floor(a.length/2)]};
 function decode(pr,z){
   const n=pr.reduce((a,b)=>a*b,1), t=Array.from({length:n},(_,i)=>i);
   const diffs=pr.map((p,i)=>{
     // Pair on all other residues. CRT means this key identifies a unique sample at each private residue.
     const key=j=>pr.filter((_,k)=>k!==i).map(q=>j%q).join(',');
     const anchor=new Map(t.filter(j=>j%p===0).map(j=>[key(j),j]));
     return Array.from({length:p},(_,r)=>r===0?0:median(t.filter(j=>j%p===r).flatMap(j=>{
       const a=anchor.get(key(j));return z[j]===null||z[a]===null?[]:[z[j]-z[a]];
     })));
   });
   const offset=median(t.flatMap(j=>z[j]===null?[]:[z[j]-diffs.reduce((s,a,i)=>s+a[j%pr[i]],0)]));
   return {diffs,offset};
 }
 let seed=20261127;
 const rand=n=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed%n};
 let cases=0,bounded=0,sharp=0;
 for(const pr of [[2,3,5],[3,5,7],[3,5,11],[2,3,5,7]]){
   const n=pr.reduce((a,b)=>a*b,1), d=n/Math.max(...pr);
   for(let e=0;2*e<d;e++){
     const f=d-1-2*e;
     for(let rep=0;rep<12;rep++){
       const diffs=pr.map(p=>Array.from({length:p},(_,r)=>r?rand(81)-40:0)), offset=rand(81)-40;
       const clean=Array.from({length:n},(_,t)=>offset+diffs.reduce((s,a,i)=>s+a[t%pr[i]],0));
       let order=Array.from({length:n},(_,i)=>i);
       for(let i=n-1;i>0;i--){let j=rand(i+1);[order[i],order[j]]=[order[j],order[i]]}
       let z=clean.slice(), noisy=clean.map(x=>x+rand(3)-1);
       for(let i=0;i<e;i++){const k=order[i];z[k]+=10000+rand(90000);noisy[k]=z[k]}
       for(let i=e;i<e+f;i++){const k=order[i];z[k]=null;noisy[k]=null}
       const a=decode(pr,z), b=decode(pr,noisy);
       assert(JSON.stringify(a)===JSON.stringify({diffs,offset}),'median exact');cases++;
       assert(b.diffs.every((x,i)=>x.every((v,j)=>Math.abs(v-diffs[i][j])<=2))&&Math.abs(b.offset-offset)<=2*pr.length+1,'bounded');bounded++;
     }
   }
   // Sharp distance witness: change one residue of largest period.
   const v=Array.from({length:n},(_,t)=>+(t%Math.max(...pr)===0));
   assert(v.filter(Boolean).length===d,'sharp full grid');sharp++;
 }
 // Counterexample to pure connectivity: schedule touches all residues, connected 2-section, but rank can still fail.
 // On the (2,3,5) grid use all tuples with x mod 2 = 1_{y mod 3 = 0}.
 const bad=Array.from({length:30},(_,t)=>t).filter(t=>t%2===+(t%3===0));
 const badA=bad.map(t=>row(t,[2,3,5]));
 assert(rank(badA)<8,'rank obstruction');
 const residues=[2,3,5].map(p=>new Set(bad.map(t=>t%p)).size);
 assert(residues.join(',')==='2,3,5','all vertices present');
 const edges=new Map();
 for(const t of bad){const ids=[2,3,5].map((p,i)=>i+':'+t%p);for(const a of ids){if(!edges.has(a))edges.set(a,new Set());for(const b of ids)edges.get(a).add(b)}}
 const seen=new Set(['0:0']), todo=['0:0'];while(todo.length)for(const b of edges.get(todo.pop()))if(!seen.has(b)){seen.add(b);todo.push(b)}
 assert(seen.size===10,'connected 2-section');
 return {prime:Q,base:{periods:ps,dimension:D,times,witness:h,nonzero:w.map((v,i)=>[times[i],v]).filter(x=>x[1]),rank_deletion_checks:deletions,distance:3},family,full_grid:{exact_decodes:cases,bounded_noise_decodes:bounded,sharp_distance_witnesses:sharp},connected_rank_failure:{times:bad,rank_mod_1009:rank(badA),full_dimension:8,vertices:seen.size},assertion_failures:0};
}
if(typeof module!=='undefined')module.exports={run};
if(typeof require!=='undefined'&&require.main===module)console.log(JSON.stringify(run(),null,2));
