// MHAC #228 — exact cycle-mean scalar compression laboratory.
// Original research toy. Node.js (no external dependencies).
// Integer arithmetic exact under explicit n<=8 and |w|<=1e6 bounds.
// Edge (u,v,w), u<v: desired score[v]-score[u] = w. Missing edges are absent.
// Fractions returned as numerator/denominator, potential scaled by denominator.
function ensure(ok,msg){if(!ok)throw Error(msg)}

function graph(n,edges){
 ensure(Number.isInteger(n)&&n>=1&&n<=8,"n must be 1..8");
 const seen=new Set(),adj=Array.from({length:n},()=>[]);
 for(const e of edges){
  ensure(Array.isArray(e)&&e.length===3,"edge triple required");
  const [u,v,w]=e;
  ensure(Number.isInteger(u)&&Number.isInteger(v)&&u>=0&&u<n&&v>=0&&v<n&&u<v,"canonical edge u<v required");
  ensure(Number.isSafeInteger(w)&&Math.abs(w)<=1000000,"integer weight out of range");
  const key=u*n+v;ensure(!seen.has(key),"duplicate edge");seen.add(key);
  adj[u].push([v,w]);adj[v].push([u,-w]);
 }
 return adj;
}

function cycles(adj){
 const n=adj.length,out=[];
 for(let start=0;start<n;start++){
  function dfs(u,used,route,sum){
   for(const [v,w] of adj[u]){
    if(v===start&&route.length>=2)out.push({route:[...route,start],sum:sum+w,len:route.length});
    else if(v>start&&!used.has(v)){used.add(v);dfs(v,used,[...route,v],sum+w);used.delete(v)}
   }
  }
  dfs(start,new Set([start]),[start],0);
 }
 return out;
}

function gcd(a,b){a=Math.abs(a);while(b){const t=a%b;a=b;b=t}return a||1}

function debt(n,edges){
 const adj=graph(n,edges), cs=cycles(adj);
 let best={route:[],sum:0,len:1},tri={sum:0,len:1};
 for(const c of cs){
  if(c.sum*best.len>best.sum*c.len)best=c;
  if(c.len===3&&c.sum*tri.len>tri.sum*c.len)tri=c;
 }
 const g=gcd(best.sum,best.len),num=best.sum/g,den=best.len/g;
 const x=Array(n).fill(0);
 // Difference constraint x[v] >= x[u] + w*den - num.
 // Super-source permits zero-length paths at every vertex.
 for(let round=0;round<n-1;round++){
  const prev=x.slice();
  for(let u=0;u<n;u++)for(const [v,w] of adj[u])x[v]=Math.max(x[v],prev[u]+w*den-num);
 }
 const errors=edges.map(([u,v,w])=>Math.abs(x[v]-x[u]-w*den));
 const maxError=Math.max(0,...errors);
 ensure(maxError===num,"primal/dual mismatch");
 return {num,den,potential:x,witness:best.route,witnessSum:best.sum,witnessLength:best.route.length?best.len:0,triangleNum:tri.sum,triangleDen:tri.len,
  ordinalCycle:cs.some(c=>c.len>=3&&c.route.slice(0,-1).every((u,i)=>adj[u].find(([v])=>v===c.route[i+1])[1]>0))};
}

function feasible(n,edges,num,den){
 // Independent synchronous Bellman-Ford decision; no cycle enumeration.
 const arcs=edges.flatMap(([u,v,w])=>[[u,v,w*den-num],[v,u,-w*den-num]]);
 let d=Array(n).fill(0);
 for(let k=0;k<n;k++){
  const next=d.slice();
  for(const [u,v,w] of arcs)next[v]=Math.max(next[v],d[u]+w);
  if(next.every((v,i)=>v===d[i]))return true;
  if(k===n-1)return false;
  d=next;
 }
 return true;
}

function ballotMargins(ballots){
 ensure(ballots.length>0,"empty panel");
 const n=ballots[0].length;ensure(n>=1&&n<=8,"invalid n");
 for(const b of ballots)ensure(b.length===n&&b.every(v=>Number.isInteger(v)&&v>=0&&v<n)&&new Set(b).size===n,"not a permutation");
 const edges=[];
 for(let u=0;u<n;u++)for(let v=u+1;v<n;v++){
  // positive means v is preferred to u, matching ascending potential.
  const w=ballots.reduce((s,b)=>s+(b.indexOf(v)<b.indexOf(u)?1:-1),0);
  edges.push([u,v,w]);
 }
 return edges;
}

function census(){
 const pairs=[];for(let u=0;u<4;u++)for(let v=u+1;v<4;v++)pairs.push([u,v]);
 const fresh=()=>({cases:0,positiveDebt:0,ordinalCycle:0,positiveWithoutOrdinalCycle:0,triangleUnderstates:0,triangleZeroButDebt:0,debtHistogram:{}});
 const result={all:fresh(),complete:fresh(),checks:0};
 for(let mask=0;mask<4**6;mask++){
  let code=mask,edges=[];
  for(const [u,v] of pairs){const q=code%4;code=Math.floor(code/4);if(q)edges.push([u,v,q-2])}
  const d=debt(4,edges);
  // Candidate fractions with numerator 0..length, denominator <=4.
  // Independent threshold search using Bellman-Ford; exact rational comparison.
  let best={num:1,den:1};
  for(let den=1;den<=4;den++)for(let num=0;num<=den;num++){
   if(num*best.den<best.num*den&&feasible(4,edges,num,den))best={num,den}
  }
  ensure(best.num*d.den===d.num*best.den,"independent feasibility mismatch");
  result.checks++;
  for(const s of (edges.length===6?[result.all,result.complete]:[result.all])){
   s.cases++;if(d.num)s.positiveDebt++;
   if(d.ordinalCycle)s.ordinalCycle++;
   if(d.num&&!d.ordinalCycle)s.positiveWithoutOrdinalCycle++;
   if(d.triangleNum*d.den<d.num*d.triangleDen)s.triangleUnderstates++;
   if(!d.triangleNum&&d.num)s.triangleZeroButDebt++;
   const key=d.num+"/"+d.den;s.debtHistogram[key]=(s.debtHistogram[key]||0)+1;
  }
 }
 return result;
}

function controls(){
 const square=[[0,1,1],[1,2,1],[2,3,1],[0,3,-1]];
 const sparse=debt(4,square);
 ensure(sparse.num===1&&sparse.den===1&&sparse.triangleNum===0,"square");
 const tree=debt(4,[[0,1,5],[1,2,-7],[2,3,2]]);
 ensure(tree.num===0,"tree");
 const disconnected=debt(5,[[0,1,2],[1,2,2],[0,2,-2],[3,4,99]]);
 ensure(disconnected.num===2&&disconnected.den===1,"disconnected");
 const exact=debt(3,[[0,1,2],[1,2,3],[0,2,5]]);
 ensure(exact.num===0,"gradient");
 const examples=[];
 for(let n=3;n<=8;n++){
  const base=Array.from({length:n},(_,i)=>i);
  const unanimous=Array.from({length:n},()=>base);
  const rotations=base.map(i=>base.slice(i).concat(base.slice(0,i)));
  const u=debt(n,ballotMargins(unanimous)),r=debt(n,ballotMargins(rotations));
  ensure(u.num/u.den===n-2&&r.num/r.den===n-2,"sharp same-panel bound");
  ensure(!u.ordinalCycle&&r.ordinalCycle,"same debt, different ordinal structure");
  examples.push({n,unanimous:u,rotations:r});
 }
 for(const bad of [[[1,0,1]],[[0,1,1],[0,1,2]],[[0,1,0.5]],[[0,4,0]]]){
  let rejected=false;try{debt(4,bad)}catch(e){rejected=true}ensure(rejected,"invalid graph accepted");
 }
 return {square:sparse,tree,disconnected,exact,examples};
}
console.log(JSON.stringify({census:census(),controls:controls()},null,2));
