// Exact bounded-size rank-one switching laboratory. Node >=18, no dependencies.
// Mode i is u_i v_i^T / denominator. Edges are in chronological order i -> j.
const abs=x=>x<0n?-x:x;
const sum=a=>a.reduce((s,x)=>s+x,0n);
const dot=(a,b)=>sum(a.map((x,i)=>x*b[i]));
const pow=(x,n)=>x**BigInt(n);
const norm1=a=>sum(a.map(abs));
const normInf=a=>a.reduce((m,x)=>abs(x)>m?abs(x):m,0n);
const key=(i,j)=>i+":"+j;
const cmp=(a,b)=>a.num*b.den>b.num*a.den?1:a.num*b.den<b.num*a.den?-1:0;
export function model(modes,denominator=1){
 if(!Number.isSafeInteger(denominator)||denominator<=0||!Array.isArray(modes)||!modes.length||modes.length>12)throw Error("require 1..12 modes and positive safe-integer denominator");
 const d=modes[0].u.length;
 if(!d||modes.some(m=>!Array.isArray(m.u)||!Array.isArray(m.v)||m.u.length!==d||m.v.length!==d||[...m.u,...m.v].some(x=>!Number.isSafeInteger(x))||!m.u.some(Boolean)||!m.v.some(Boolean)))throw Error("nonzero equal-dimension integer factors required");
 const ms=modes.map(m=>({u:m.u.map(BigInt),v:m.v.map(BigInt)}));
 return {ms,den:BigInt(denominator),n:ms.length,weights:ms.map(a=>ms.map(b=>abs(dot(b.v,a.u))))};
}
export function cycles(g,blocked=new Set()){
 const out=[];
 function walk(start,path,prod){
  const last=path.at(-1);
  for(let j=start;j<g.n;j++){
   const w=g.weights[last][j];if(!w||blocked.has(key(last,j)))continue;
   if(j===start){out.push({path:[...path],num:prod*w,den:pow(g.den,path.length),edges:path.map((i,k)=>key(i,path[(k+1)%path.length]))});}
   else if(!path.includes(j))walk(start,[...path,j],prod*w);
  }
 }
 for(let i=0;i<g.n;i++)walk(i,[i],1n);
 return out;
}
export function rate(g,blocked=new Set()){
 let best={num:0n,den:1n,path:[],edges:[]};
 for(const c of cycles(g,blocked)){
  const l=c.path.length,k=best.path.length||1;
  if(pow(c.num,k)*pow(best.den,l)>pow(best.num,l)*pow(c.den,k))best=c;
 }
 return {...best,root:best.path.length||1,status:best.num<best.den?"strictly-decaying":best.num===best.den?"bounded-neutral":"growing"};
}
// Maximum induced l1 norm over ALL nonempty allowed products, if cycle gains <=1.
// A repeated mode can be removed with its intervening cycle, without reducing gain.
// Dynamic program of lengths 1..n, fixed initial and current mode.
export function peak(g,blocked=new Set()){
 if(rate(g,blocked).status==="growing")return {unbounded:true};
 let best={num:0n,den:1n,path:[]};
 for(let i=0;i<g.n;i++){
  let dp=new Map([[i,{num:normInf(g.ms[i].v),path:[i]}]]);
  for(let len=1;len<=g.n;len++){
   const next=new Map();
   for(const [j,row] of dp){
    const value={num:row.num*norm1(g.ms[j].u),den:pow(g.den,len),path:row.path};
    if(cmp(value,best)>0)best=value;
    for(let k=0;k<g.n;k++){
     const w=g.weights[j][k];if(!w||blocked.has(key(j,k)))continue;
     const num=row.num*w,prev=next.get(k);
     if(!prev||num>prev.num)next.set(k,{num,path:[...row.path,k]});
    }
   }
   dp=next;
  }
 }
 return {...best,unbounded:false};
}
// Minimum positive integer cost of forbidding transitions. By default all nonzero
// transitions are removable at cost 1. Locked edges are never removed.
// strict=true forbids neutral cycles too. cap optional positive rational {num,den}.
// Exact exhaustive witness branching; cap counts visited search nodes.
export function guards(g,{strict=true,cap=null,costs={},locked=[],budget=100000}={}){
 if(!Number.isSafeInteger(budget)||budget<1)throw Error("positive integer budget required");
 if(cap&&(typeof cap.num!=="bigint"||typeof cap.den!=="bigint"||cap.num<0n||cap.den<=0n))throw Error("nonnegative rational cap required");
 const locks=new Set(locked);for(const e of Object.keys(costs))if(!Number.isSafeInteger(costs[e])||costs[e]<1)throw Error("positive integer costs required");
 let best=Infinity,visited=0,exhausted=false;const seen=new Set(),solutions=[];
 function visit(blocked,cost){
  if(cost>best||exhausted)return;
  const id=[...blocked].sort().join(",");
  if(seen.has(id))return;
  if(visited>=budget){exhausted=true;return;}visited++;seen.add(id);
  const bad=cycles(g,blocked).find(c=>strict?c.num>=c.den:c.num>c.den);
  let edges=bad?.edges;
  if(!edges&&cap){
   const p=peak(g,blocked);
   if(p.unbounded)throw Error("internal cycle check disagreement");
   if(cmp(p,cap)>0)edges=p.path.slice(1).map((j,k)=>key(p.path[k],j));
  }
  if(!edges){
   if(cost<best){best=cost;solutions.length=0;}
   solutions.push([...blocked].sort());return;
  }
  for(const e of edges)if(!locks.has(e)){
   const next=new Set(blocked);next.add(e);visit(next,cost+(costs[e]??1));
  }
 }
 visit(new Set(),0);
 return {status:exhausted?"budget-exhausted":solutions.length?"optimal":"impossible",cost:Number.isFinite(best)?best:null,solutions:solutions.sort((a,b)=>a.join(",").localeCompare(b.join(","))),visited};
}
export function fromWeights(w,den=1){
 const n=w.length;
 return model(w.map((_,i)=>({u:w.map((_,j)=>i===j?1:0),v:w.map(row=>row[i])})),den);
}
export function stringify(x){return JSON.stringify(x,(_,v)=>typeof v==="bigint"?v.toString():v,2)+"\n";}
