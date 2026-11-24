// Synthetic preset-layout laboratory; no empirical UX claim.
export function weight(x) { let k=0; for(;x;x&=x-1) k++; return k; }
function dim(n,max=16) {if(!Number.isInteger(n)||n<1||n>max) throw new RangeError("dimension");}
export function reflected(n) {dim(n);return Array.from({length:2**n},(_,i)=>i^(i>>>1));}
export function shifted(n) {
  dim(n);if(n===1)return [0,1];
  const g=reflected(n-1),m=g.length;
  return g.concat([g[m-1],...g.slice(0,-1)].map(v=>v+m));
}
export function hales(n) {
  dim(n);return Array.from({length:2**n},(_,i)=>i).sort((a,b)=>weight(a)-weight(b)||b-a);
}
export function metrics(order) {
  if(!Array.isArray(order)||order.length<2)throw new RangeError("order");
  const N=order.length,n=Math.log2(N);dim(n);
  const pos=new Int32Array(N).fill(-1);
  for(let i=0;i<N;i++){const v=order[i];if(!Number.isInteger(v)||v<0||v>=N||pos[v]!==-1)throw new RangeError("not bijective");pos[v]=i;}
  let jump=0,span=0,totalJump=0,totalSpan=0,worst=null;
  const histogram={};
  for(let i=1;i<N;i++){const d=weight(order[i]^order[i-1]);jump=Math.max(jump,d);totalJump+=d;}
  for(let u=0;u<N;u++)for(let bit=0;bit<n;bit++){
    const v=u^(1<<bit);if(u>v)continue;
    const d=Math.abs(pos[u]-pos[v]);totalSpan+=d;histogram[d]=(histogram[d]||0)+1;
    if(d>span){span=d;worst=[u,v,pos[u],pos[v]];}
  }
  return {jump,span,totalJump,totalSpan,histogram,worst};
}
export function harper(n){
  dim(n);let total=0;
  for(let m=0;m<n;m++){let c=1;for(let k=1;k<=Math.floor(m/2);k++)c=c*(m-k+1)/k;total+=c;}
  return total;
}
// Exact feasibility for a linear (not circular) dial, up to 32 vertices.
// At position i the vertex at i-span has its last opportunity to place any missing neighbour.
export function solve(n,jump,span,budget=30000000){
  dim(n,5);const N=2**n;
  if(!Number.isInteger(jump)||jump<1||jump>n||!Number.isInteger(span)||span<1||span>=N||!Number.isSafeInteger(budget)||budget<1)throw new RangeError("limits");
  const near=Array.from({length:N},(_,v)=>Array.from({length:n},(_,b)=>v^(1<<b)));
  const next=Array.from({length:N},(_,v)=>Array.from({length:N},(_,u)=>u).filter(u=>u!==v&&weight(u^v)<=jump));
  const path=[0],pos=new Int8Array(N).fill(-1);pos[0]=0;
  let nodes=0,exhausted=false;
  function visit(){
    if(nodes===budget){exhausted=true;return null;}
    nodes++;const i=path.length;
    if(i===N)return path.slice();
    let forced=-1;
    if(i>=span){
      for(const u of near[path[i-span]])if(pos[u]===-1){if(forced!==-1)return null;forced=u;}
    }
    const choices=forced===-1?next[path[i-1]]:[forced];
    for(const u of choices){
      if(pos[u]!==-1||weight(u^path[i-1])>jump)continue;
      // XOR translation sets first vertex 0. Coordinate permutation sets second to low w bits.
      if(i===1&&u!==(1<<weight(u))-1)continue;
      if(near[u].some(v=>pos[v]>=0&&i-pos[v]>span))continue;
      pos[u]=i;path.push(u);const result=visit();path.pop();pos[u]=-1;
      if(result||exhausted)return result;
    }
    return null;
  }
  const order=visit();
  return {status:order?"feasible":exhausted?"budget_exhausted":"infeasible",nodes,order};
}
export function censusGray(n){
  dim(n,4);const N=2**n,path=[0],histogram={};let count=0;
  function visit(mask){
    if(path.length===N){
      const {span}=metrics(path);histogram[span]=(histogram[span]||0)+1;count++;return;
    }
    for(let b=0;b<n;b++){const u=path.at(-1)^(1<<b);if(mask&(1<<u))continue;path.push(u);visit(mask|(1<<u));path.pop();}
  }
  visit(1);return {count,histogram}; // start fixed at zero; no second-vertex symmetry reduction.
}
export function experiment(){
  const assert=(x,m)=>{if(!x)throw new Error(m);};
  const families=[];
  for(let n=1;n<=12;n++){
    const a=metrics(reflected(n)),b=metrics(shifted(n)),c=metrics(hales(n));
    assert(a.jump===1&&a.span===2**n-1,"reflected");
    assert(b.jump===1&&b.span===(n===1?1:2**(n-1)+1),"shifted");
    assert(c.span===harper(n),"Hales");
    families.push({n,harper:harper(n),reflected:a.span,shifted:b.span,halesJump:c.jump});
  }
  const exact=[];
  for(let n=2;n<=5;n++){
    let cap=harper(n);if(cap%2===0)cap++;
    for(;cap<2**n;cap+=2){
      const a=solve(n,1,cap);assert(a.status!=="budget_exhausted","budget");
      if(a.order){const m=metrics(a.order);assert(m.jump===1&&m.span===cap,"witness");}
      exact.push({n,jump:1,cap,...a});
      if(a.order)break;
    }
  }
  const census=[2,3,4].map(n=>({n,...censusGray(n)}));
  for(const c of census){const a=exact.find(x=>x.n===c.n&&x.status==="feasible");assert(a.cap===Math.min(...Object.keys(c.histogram).map(Number)),"census");}
  const relaxed=[2,3,4].map(n=>({n,jump:2,cap:harper(n),...solve(n,2,harper(n))}));
  for(const a of relaxed)if(a.order){const m=metrics(a.order);assert(m.jump<=2&&m.span===a.cap,"relaxed");}
  assert(solve(4,1,7,1).status==="budget_exhausted","budget status");
  assert(solve(2,1,3,1).status==="budget_exhausted","budget positive control");
  let invalid=0;for(const p of [[0,0],[0,1,2],[0,2]])try{metrics(p);}catch{invalid++;}
  assert(invalid===3,"invalid input");
  return {scope:"synthetic linear bijective binary preset dial",families,exact,census,relaxed,negativeChecks:5};
}
