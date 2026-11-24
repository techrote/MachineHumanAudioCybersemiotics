"use strict";
// Standalone synthetic oracle. Run: node lab.js
console.log(JSON.stringify((function lab(){
"use strict";
const assert=(x,m)=>{if(!x)throw Error(m||"assertion");};
const X=[0,1,2,3,4], C=[0,1,2];
const adjacent=(x,y)=>[1,4].includes((x-y+5)%5);
const near=(x,y)=>x===y||adjacent(x,y);
const words=(alphabet,n)=>n===0?[[]]:words(alphabet,n-1).flatMap(p=>alphabet.map(x=>[...p,x]));
const type=S=>S.length===0?0:S.length===5?3:S.some(x=>S.some(y=>adjacent(x,y)))?2:1;
function vectors(S){
  const edges=S.flatMap((x,i)=>S.flatMap((y,j)=>adjacent(x,y)?[[i,j]]:[]));
  const cols=words(C,S.length).filter(v=>edges.every(([i,j])=>v[i]!==v[j]));
  const compatible=(a,b)=>edges.every(([i,j])=>a[i]!==b[j]);
  const next=cols.map(a=>cols.map((b,j)=>compatible(a,b)?j:-1).filter(j=>j>=0));
  const seen=new Set();let cycles=0;
  function visit(path){
    if(path.length===5){
      if(!next[path[4]].includes(path[0]))return;
      cycles++;
      const v=C.map(c=>Math.max(...S.map((x,i)=>type(X.filter(y=>cols[path[y]][i]===c)))));
      seen.add(v.sort((a,b)=>a-b).join(""));return;
    }
    for(const j of next[path[path.length-1]])visit([...path,j]);
  }
  cols.forEach((_,i)=>visit([i]));
  const all=[...seen].map(s=>[...s].map(Number));
  const pareto=all.filter(v=>!all.some(u=>u.some((x,i)=>x<v[i])&&u.every((x,i)=>x<=v[i]))).sort((a,b)=>a.join("").localeCompare(b.join("")));
  return {columns:cols.length,cycles,all:all.map(v=>v.join("")).sort(),pareto};
}
const V=[null,vectors([0]),vectors([0,1]),vectors(X)];
const P=[null,[[0,0,3],[0,1,2],[1,1,1]],[[0,3,3],[1,2,2]],[[3,3,3]]];
for(let i=1;i<=3;i++)assert(JSON.stringify(V[i].pareto)===JSON.stringify(P[i]),"local frontier");
const fib=[0n,1n];for(let i=2;i<=105;i++)fib.push(fib[i-1]+fib[i-2]);
const dp=[[0n,1n,1n,1n]], choice=[];
for(let n=1;n<=50;n++){
 const prev=dp[n-1],best=[0n],ch=[null];
 for(let k=1;k<=3;k++){
  const options=P[k].map(v=>v.reduce((a,x)=>a+prev[x],0n));
  let i=options.reduce((j,x,i)=>x<options[j]?i:j,0);
  best[k]=options[i];ch[k]=P[k][i];
 }
 dp.push(best);choice[n]=ch;
 assert(best[1]===fib[2*n]&&best[2]===fib[2*n+1]&&best[3]===3n**BigInt(n),"Fibonacci frontier");
}
const rows1={"003":[2,2,2,2,2],"012":[2,2,2,2,1],"111":[2,1,2,1,0]};
const rows2={"033":[[2,2,2,2,2],[1,1,1,1,1]],"122":[[2,2,2,2,0],[1,0,1,1,1]]};
const scalar=[0,1,0,1,2];
function bip(S){
 const color=new Map();
 for(const x of S)if(!color.has(x)){
  color.set(x,0);const q=[x];
  for(let i=0;i<q.length;i++)for(const y of S)if(adjacent(q[i],y)){
   if(!color.has(y)){color.set(y,1-color.get(q[i]));q.push(y);}
   else assert(color.get(y)!==color.get(q[i]),"non-bipartite subset");
  }
 }
 return color;
}
function groupBy(a,key){const m=new Map();for(const x of a){const k=key(x);if(!m.has(k))m.set(k,[]);m.get(k).push(x);}return m;}
function step(entries,remaining,stationary){
 const byTag=groupBy(entries,e=>e.tags.join(""));
 const out=[];
 for(const bucket of byTag.values()){
  const root=bucket[0].x.length===0;
  const gs=groupBy(bucket,e=>e.x.slice(0,-1).join(""));
  const k=root?1:Math.max(...[...gs.values()].map(g=>type(g.map(e=>e.x[e.x.length-1]))));
  const plan=stationary?(k===1?"012":k===2?"122":"333"):choice[remaining][k].join("");
  for(const g of gs.values()){
   const S=root?[]:g.map(e=>e.x[e.x.length-1]);
   const b=k===2?bip(S):null;
   for(const e of g){
    const x=e.x[e.x.length-1];
    const row=k===1?rows1[plan]:k===2?rows2[plan][b.get(x)]:Array(5).fill(scalar[x]);
    for(const y of X)out.push({x:[...e.x,y],tags:[...e.tags,row[y]]});
   }
  }
 }
 return out;
}
const observe=(x,a)=>x===(a+1)%5?a:x;
let decoderChecks=0,pairChecks=0,stopWitnesses=0,causalityChecks=0;
function check(entries,n,direct){
 const byTag=groupBy(entries,e=>e.tags.join(""));
 let debt=false;
 for(const b of byTag.values()){
  for(let i=0;i<b.length;i++)for(let j=i+1;j<b.length;j++){
   const x=b[i].x,y=b[j].x;pairChecks++;
   if(x.every((v,k)=>near(v,y[k]))){
    assert(x.slice(0,-1).join("")===y.slice(0,-1).join(""),"late reconstruction");debt=true;
   }
  }
 }
 if(debt)stopWitnesses++;
 if(direct){
  const obs=new Map(), actions=words(X,n);
  for(const e of entries)for(const a of actions){
   const key=e.tags.join("")+"|"+a.join("")+"|"+e.x.map((x,i)=>observe(x,a[i])).join("");
   const target=e.x.slice(0,-1).join("");decoderChecks++;
   if(obs.has(key))assert(obs.get(key)===target,"direct intervention decoder");
   else obs.set(key,target);
  }
 }
 return byTag.size;
}
function run(n,stationary){
 let entries=[{x:[],tags:[]}],counts=[];
 for(let t=1;t<=n;t++){
  const old=new Map(entries.map(e=>[e.x.join(""),e.tags.join("")]));
  entries=step(entries,n-t+1,stationary);
  for(const e of entries){assert(old.get(e.x.slice(0,-1).join(""))===e.tags.slice(0,-1).join(""),"causality");causalityChecks++;}
  counts.push(check(entries,t,t<=4));
 }
 return counts;
}
const stationary=run(6,true);
for(let n=1;n<=6;n++)assert(BigInt(stationary[n-1])===fib[2*n+1],"stationary count");
const finite=[];
for(let n=1;n<=6;n++){const c=run(n,false);assert(BigInt(c[n-1])===fib[2*n],"finite optimum witness");finite.push(c[n-1]);}
assert(stopWitnesses>0,"must not confuse deadline with stop");
return {local:V.slice(1),stationary,finite,decoderChecks,pairChecks,causalityChecks,stopWitnesses,dpHorizons:50};
})()));
