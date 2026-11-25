"use strict";
function laboratory(){
 const subsets=(n)=>Array.from({length:1<<n},(_,i)=>i);
 const pop=(x)=>{let n=0;for(;x;x&=x-1)n++;return n};
 const assert=(v,msg)=>{if(!v)throw Error(msg)};
 const pairs=a=>a.flatMap((x,i)=>a.slice(i+1).map(y=>[x,y]));
 const range=n=>Array.from({length:n},(_,i)=>i);
 let trees=0, faults=0, graphs=0, comparisons=0;
 function checkTree(E){
  const n=E.length+1, V=range(n), A=V.map(v=>E.flatMap(([a,b],k)=>a===v?[[b,k]]:b===v?[[a,k]]:[]));
  const leaves=V.filter(v=>A[v].length===1), I=V.filter(v=>A[v].length>1);
  if(I.some(v=>A[v].length===2))return;
  const delta=Math.min(...I.map(v=>A[v].length));
  function dfs(v,w,p=-1){if(v===w)return 0;for(const [u,k] of A[v])if(u!==p){const d=dfs(u,w,v);if(d>=0)return d|(1<<k)}return -1}
  const P=pairs(leaves).map(([v,w])=>dfs(v,w));
  const maps=[new Map(),new Map(),new Map()];
  for(const f of subsets(E.length)){
   const r=P.map(p=>pop(p&f));
   [r,r.map(x=>x%2),r.map(x=>+(x>0))].forEach((row,j)=>{const key=row.join(",");if(!maps[j].has(key))maps[j].set(key,[]);maps[j].get(key).push(pop(f))});
  }
  assert(maps[0].size===1<<E.length,"sum injection");
  assert(maps[1].size===1<<(leaves.length-1),"parity rank");
  assert([...maps[1].values()].every(a=>a.length===1<<I.length),"parity fibre");
  [Math.floor((delta-1)/2),delta-2].forEach((t,j)=>{
   const actual=Math.min(...[...maps[j+1].values()].filter(a=>a.length>1).map(a=>a.sort((a,b)=>a-b)[1]))-1;
   assert(actual===t,"sparse threshold");
  });
  trees++;faults+=1<<E.length;
 }
 for(let n=4;n<=6;n++){
  for(let s=0;s<n**(n-2);s++){
   let k=s,seq=range(n-2).map(()=>{let x=k%n;k=Math.floor(k/n);return x}),d=range(n).map(v=>1+seq.filter(x=>x===v).length),E=[];
   for(const v of seq){const u=d.indexOf(1);E.push([u,v]);d[u]--;d[v]--}
   E.push(range(n).filter(v=>d[v]===1));checkTree(E);
  }
 }
 for(let n=7;n<=10;n++)checkTree(range(n-1).map(i=>[0,i+1]));
 for(let n=3;n<=5;n++){
  const P=pairs(range(n)), best={};
  for(const g of subsets(P.length)){
   const chosen=P.filter((_,i)=>g>>i&1);
   const codes=subsets(n-1).map(x=>chosen.reduce((r,[a,b],i)=>r|((((x>>a)^(x>>b))&1)<<i),0));
   const d=Math.min(...codes.slice(1).map(pop));
   let direct=Infinity;
   for(const [a,b] of pairs(codes)){direct=Math.min(direct,pop(a^b));comparisons++}
   assert(d===direct,"cut distance");
   if(d)best[d]=Math.min(best[d]??Infinity,chosen.length);
   graphs++;
  }
  for(let d=1;d<n;d++)assert(best[d]===(d===1?n-1:Math.ceil(n*d/2)),"budget");
 }
 return {trees,faults,graphs,comparisons};
}
console.log(JSON.stringify(laboratory(), null, 2));
