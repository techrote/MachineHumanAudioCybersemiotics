"use strict";
function laboratory(){
 const check=(v,m)=>{if(!v)throw Error(m)};
 const types="ABC", pairs=["AB","AC","BC"];
 function words(counts,p=""){if(counts.every(x=>!x))return [p];return counts.flatMap((n,i)=>n?words(counts.map((v,j)=>v-(i===j)),p+types[i]):[])}
 const W=words([2,2,2]), M=["AB","AB","AC","AC","BC","BC"], proj=(w,s)=>[...w].filter(x=>s.includes(x)).join("");
 const pop=x=>{let n=0;while(x){x&=x-1;n++}return n};
 function lev(a,b){let v=Array.from({length:b.length+1},(_,i)=>i);for(let i=0;i<a.length;i++){let z=[i+1];for(let j=0;j<b.length;j++)z.push(Math.min(v[j+1]+1,z[j]+1,v[j]+ +(a[i]!==b[j])));v=z}return v[b.length]}
 function dag(w,m,mask){const v=Array.from({length:w.length},()=>0);for(let i=w.length-1;i>=0;i--)for(let j=i+1;j<w.length;j++)if(w[i]===w[j]||m.some((s,k)=>!(mask>>k&1)&&s.includes(w[i])&&s.includes(w[j])))v[i]|=(1<<j)|v[j];return v}
 function changedPossible(w,m,mask,g){const v=dag(w,m,mask);for(let i=0;i<w.length;i++)for(let j=i+1;j<w.length;j++)if(w[i]!==w[j]&&g.some(s=>s.includes(w[i])&&s.includes(w[j]))&&!(v[i]>>j&1))return true;return false}
 function rank(w,g){return g.map(s=>proj(w,s)).join("|")}
 const graphs=Array.from({length:7},(_,i)=>pairs.filter((_,j)=>(i+1)>>j&1));
 let pairChecks=0,traceChecks=0,localChecks=0,maskChecks=0,fullLocalChecks=0;const minima=[];
 const signatures=W.map(w=>M.map(s=>proj(w,s)));
 const distances=W.map((w,i)=>W.map((u,j)=>{const h=signatures[i].reduce((n,s,k)=>n+ +(s!==signatures[j][k]),0), d=signatures[i].reduce((n,s,k)=>n+lev(s,signatures[j][k]),0);if(i<j){check(d>=2*h,"equal-count per report edit bound");pairChecks++}return [h,d]}));
 for(const g of graphs){
  const t=W.map(w=>rank(w,g));let minH=Infinity,minE=Infinity;
  for(let i=0;i<W.length;i++){
   let h=Infinity,d=Infinity;
   for(let j=0;j<W.length;j++)if(t[i]!==t[j]){h=Math.min(h,distances[i][j][0]);d=Math.min(d,distances[i][j][1]);traceChecks++}
   minH=Math.min(minH,h);minE=Math.min(minE,d);
   let local=Infinity;
   for(let mask=0;mask<1<<M.length;mask++){
    const possible=changedPossible(W[i],M,mask,g);
    const brute=W.some((_,j)=>t[i]!==t[j]&&M.every((_,k)=>(mask>>k&1)||signatures[i][k]===signatures[j][k]));
    check(possible===brute,"DAG vs enumerated candidate");maskChecks++;
    if(possible)local=Math.min(local,pop(mask));
   }
   check(h===local,"local report distance");localChecks++;
   if(g.length===3){let c=Infinity;for(let k=1;k<W[i].length;k++)if(W[i][k-1]!==W[i][k])c=Math.min(c,M.filter(s=>s.includes(W[i][k-1])&&s.includes(W[i][k])).length);check(c===h&&d===2*h,"local full word formula");fullLocalChecks++}
  }
  check(minH===2&&minE===4,"global trace distance");minima.push({graph:g,hamming:minH,edit:minE});
 }
 const bridge=["AB","AB","BC","BC"], p="AABBCC", target=["AC"];let local=Infinity;
 for(let mask=0;mask<16;mask++)if(changedPossible(p,bridge,mask,target))local=Math.min(local,pop(mask));
 check(local===2,"indirect certificate");
 const EMon=pairs.flatMap(s=>Array(5).fill(s));
 const decode=(y,e,E,g=pairs)=>[...new Set(W.filter(w=>{const costs=y.flatMap((r,i)=>r===null?[]:[lev(proj(w,EMon[i]),r)]).sort((a,b)=>b-a);return costs.slice(e).reduce((a,b)=>a+b,0)<=E}).map(w=>rank(w,g)))].sort();
 const brute=(w,y,e,E)=>{const c=y.flatMap((r,i)=>r===null?[]:[lev(proj(w,EMon[i]),r)]);for(let mask=0;mask<1<<c.length;mask++)if(pop(mask)<=e&&c.reduce((n,x,j)=>n+((mask>>j&1)?0:x),0)<=E)return true;return false};
 let seed=813, rnd=n=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed%n};
 let strict=0,trimChecks=0;
 for(let i=0;i<180;i++){
  const w=W[rnd(W.length)], y=EMon.map(s=>proj(w,s));const coords=[...EMon.keys()];for(let j=coords.length-1;j>0;j--){const k=rnd(j+1);[coords[j],coords[k]]=[coords[k],coords[j]]}
  y[coords[0]]=null;y[coords[1]]="ZZZZ";const k=coords[2],s=y[k],j=rnd(s.length);y[k]=s.slice(0,j)+s.slice(j+1);
  const a=decode(y,1,1);check(a.length===1&&a[0]===rank(w,pairs),"strict mixed faults");strict++;
  if(i<12)for(const u of W){check(brute(u,y,1,1)===decode(y,1,1).includes(rank(u,pairs)),"trimmed decoder brute mask");trimChecks++}
 }
 const a="AABBCC", b="ABABCC", y=EMon.map(s=>proj(a,s));y[0]=null;y[1]=proj(a,"AB");y[2]=proj(b,"AB");y[3]=y[4]="ABB";
 const boundary=decode(y,1,2);check(boundary.includes(rank(a,pairs))&&boundary.includes(rank(b,pairs)),"boundary collision");
 // Shared deletion: the full surviving word is stronger than any set of its projections.
 const census={},twoCensus={};let deletionChecks=0,twoDeletionChecks=0;
 for(const w of W)for(let i=0;i<w.length;i++){
  const x=w[i],v=w.slice(0,i)+w.slice(i+1);
  const orig=W.filter(u=>[...u].some((z,j)=>z===x&&u.slice(0,j)+u.slice(j+1)===v));
  check(orig.length===5,"single shared deletion count");census[orig.length]=(census[orig.length]||0)+1;deletionChecks++;
 }
 for(const w of W)for(const x of types){
  const v=[...w].filter(c=>c!==x).join("");
  const n=W.filter(u=>[...u].filter(c=>c!==x).join("")===v).length;
  check(n===15,"two shared same-type deletions");twoCensus[n]=(twoCensus[n]||0)+1;twoDeletionChecks++;
 }
 return {status:"PASS",wordCount:W.length,monitors:M,minima,pairChecks,traceChecks,localChecks,maskChecks,fullLocalChecks,indirect:{word:p,monitors:bridge,target,local_distance:local,universal_distance:0},strict,trimChecks,boundary:{a,b,reports:y,traceCandidates:boundary,e:1,f:1,E:2},sharedDeletion:{deletionChecks,census,twoDeletionChecks,twoCensus},scope:"synthetic fixed multiplicity type-word reconstruction; no empirical validation"};
}
if(typeof module!=="undefined"&&require.main===module) console.log(JSON.stringify(laboratory(),null,2));
