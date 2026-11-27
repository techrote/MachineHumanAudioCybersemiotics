'use strict';
// Synthetic exact finite oracle, no dependencies. Run node laboratory.cjs.
function laboratory(){
 const assert=(x,m)=>{if(!x)throw Error(m)};
 const pop=x=>{let n=0;for(;x;x&=x-1)n++;return n};
 const seq=(w,m)=>Array.from(w).filter((_,i)=>m&(1<<i)).join("");
 const range=n=>Array.from({length:n},(_,i)=>i);
 const words=(abc,n)=>n===0?[""]:words(abc,n-1).flatMap(w=>Array.from(abc,a=>w+a));
 const counts=(w,abc)=>Array.from(abc,a=>Array.from(w).filter(b=>a===b).length);
 const sum=a=>a.reduce((x,y)=>x+y,0);
 const histKey=h=>JSON.stringify(h.map(String));
 function embeddings(w,scope){
  const map=new Map();
  for(let m=0;m<2**w.length;m++){
   const v=seq(w,m);if(Array.from(v).some(a=>!scope.includes(a)))continue;
   if(!map.has(v))map.set(v,[]);map.get(v).push(m);
  }
  return map;
 }
 // Exact coefficient counts of labeled embedding tuples, by number of invisible positions.
 function polynomial(w,vs,scopes){
  assert(vs.length===scopes.length&&vs.length<20,"scope shape");
  assert(vs.every((v,i)=>Array.from(v).every(a=>scopes[i].includes(a))),"out of scope");
  const memo=new Map(),h=vs.length,N=w.length;
  function rec(t,p){
   const key=t+":"+p.join(",");
   if(memo.has(key))return memo.get(key);
   const out=Array(N-t+1).fill(0n);
   if(t===N){out[0]=p.every((x,i)=>x===vs[i].length)?1n:0n;return out}
   let ready=0;
   for(let i=0;i<h;i++)if(scopes[i].includes(w[t])&&vs[i][p[i]]===w[t])ready|=1<<i;
   for(let m=ready;;m=(m-1)&ready){
    const next=rec(t+1,p.map((x,i)=>x+((m>>i)&1))),shift=m===0?1:0;
    for(let j=0;j<next.length;j++)out[j+shift]+=next[j];
    if(!m)break;
   }
   memo.set(key,out);return out;
  }
  return rec(0,Array(h).fill(0));
 }
 function brute(w,lists){
  const out=Array(w.length+1).fill(0n);
  function go(i,mask){if(i===lists.length){out[w.length-pop(mask)]++;return}for(const m of lists[i])go(i+1,mask|m)}
  go(0,0);return out;
 }
 function support(h){return range(h.length).filter(i=>h[i]>0n)}
 function interval(s){return s.length===0||s[s.length-1]-s[0]+1===s.length}
 function quotaLCS(u,v,abc,quota){
  const memo=new Map();
  function rec(i,j,q){
   if(i===u.length||j===v.length)return sum(q)===0?0:-Infinity;
   const key=i+":"+j+":"+q.join(",");
   if(memo.has(key))return memo.get(key);
   let best=Math.max(rec(i+1,j,q),rec(i,j+1,q));
   if(u[i]===v[j]){const k=abc.indexOf(u[i]),r=q.slice();r[k]=Math.max(0,r[k]-1);best=Math.max(best,1+rec(i+1,j+1,r))}
   memo.set(key,best);return best;
  }
  return rec(0,0,quota);
 }
 function unknown(u,v,abc,c){
  const a=counts(u,abc),b=counts(v,abc);
  if(Array.from(u+v).some(x=>!abc.includes(x))||a.some((x,i)=>x>c[i]||b[i]>c[i]))return [];
  const q=a.map((x,i)=>Math.max(0,x+b[i]-c[i])),M=quotaLCS(u,v,abc,q);
  if(M===-Infinity)return [];
  const base=sum(c)-u.length-v.length;
  return range(M-sum(q)+1).map(i=>base+sum(q)+i);
 }
 let two=0,three=0,tupleMass=0n,unknownCases=0,inconsistent=0,strictQuota=0,nontrivial=0;
 const agg=new Map();
 function fixed(w,scopes,collect){
  const em=scopes.map(s=>embeddings(w,s));
  function visit(i,vs,ls){
   if(i<em.length){for(const [v,l] of em[i])visit(i+1,[...vs,v],[...ls,l]);return}
   const b=brute(w,ls),d=polynomial(w,vs,scopes),s=support(b);
   assert(histKey(b)===histKey(d),"polynomial vs masks "+w+" "+vs);
   assert(interval(s),"fixed interval");
   assert(b.reduce((a,x)=>a+x,0n)===ls.reduce((a,x)=>a*BigInt(x.length),1n),"tuple mass");
   tupleMass+=b.reduce((a,x)=>a+x,0n);
   if(s.length>1)nontrivial++;
   if(scopes.length===2)two++;else three++;
   if(collect){
    const c=counts(w,"AB").join(","),key=JSON.stringify(vs);
    if(!agg.has(c))agg.set(c,new Map());const m=agg.get(c);
    if(!m.has(key))m.set(key,new Set());for(const x of s)m.get(key).add(x);
   }
  }
  visit(0,[],[]);
 }
 for(let n=0;n<=6;n++)for(const w of words("AB",n))fixed(w,["AB","AB"],true);
 for(let n=0;n<=4;n++)for(const w of words("ABC",n))fixed(w,["AB","BC","AC"],false);
 for(const [key,tab] of agg){
  const c=key.split(",").map(Number),abc="AB",N=sum(c);
  const vs=range(N+1).flatMap(n=>words(abc,n)).filter(w=>counts(w,abc).every((x,i)=>x<=c[i]));
  for(const u of vs)for(const v of vs){
   const want=[...(tab.get(JSON.stringify([u,v]))||[])].sort((a,b)=>a-b),got=unknown(u,v,abc,c);
   assert(JSON.stringify(want)===JSON.stringify(got),"unknown quota "+key+" "+u+" "+v);
   unknownCases++;if(!got.length)inconsistent++;
   else if(got[got.length-1]<N-u.length-v.length+quotaLCS(u,v,abc,[0,0]))strictQuota++;
  }
 }
 const fixedExample=(w,vs,scopes)=>({w,vs,scopes,polynomial:polynomial(w,vs,scopes).map(String),invisible:support(polynomial(w,vs,scopes))});
 const examples=[
  fixedExample("ABA",["A","BA"],["AB","AB"]),
  fixedExample("ABA",["AB","AB"],["AB","AB"]),
  fixedExample("AABBCC",["AB","BC","AC"],["AB","BC","AC"]),
  fixedExample("ABC",["AB","BC","CA"],["AB","BC","AC"])
 ];
 assert(JSON.stringify(examples[0].invisible)==="[0,1]","greedy counterexample");
 assert(JSON.stringify(examples[1].invisible)==="[1]","fixed source count obstruction");
 const quotaExample={u:"AAAB",v:"BAAA",composition:[6,1],alphabet:"AB",ordinaryLCS:quotaLCS("AAAB","BAAA","AB",[0,0]),quotaLCS:quotaLCS("AAAB","BAAA","AB",[0,1]),invisible:unknown("AAAB","BAAA","AB",[6,1])};
 assert(quotaExample.ordinaryLCS===3&&quotaExample.quotaLCS===1&&JSON.stringify(quotaExample.invisible)==="[0]","quota witness");
 const cycle={reports:["AB","BC","CA"],composition:[1,1,1],pairs:[],jointHistories:[]};
 for(let i=0;i<3;i++)for(let j=i+1;j<3;j++)cycle.pairs.push({views:[cycle.reports[i],cycle.reports[j]],invisible:unknown(cycle.reports[i],cycle.reports[j],"ABC",cycle.composition)});
 for(const w of words("ABC",3).filter(w=>counts(w,"ABC").every(x=>x===1)))if(support(polynomial(w,cycle.reports,["AB","BC","AC"])).length)cycle.jointHistories.push(w);
 assert(cycle.pairs.every(p=>p.invisible.length>0)&&cycle.jointHistories.length===0,"cycle witness");
 return {fixedTwoStreamCases:two,fixedThreePartialStreamCases:three,embeddingTuples:String(tupleMass),nontrivialFixedIntervals:nontrivial,unknownCompositionCases:unknownCases,inconsistentUnknownCases:inconsistent,strictQuotaCases:strictQuota,examples,quotaExample,cycle,assertionFailures:0};
}
console.log(JSON.stringify(laboratory(),null,2));
