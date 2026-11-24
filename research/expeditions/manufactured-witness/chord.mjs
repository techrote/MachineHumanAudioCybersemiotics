// Exact integer-grid analytic cubic model; no modulo-frequency folding.
export function analyze(input) {
  if (!Array.isArray(input) || input.length < 2 || input.length > 32 ||
      input.some(x=>!Number.isSafeInteger(x)||Math.abs(x)>1e9) ||
      new Set(input).size!==input.length) throw Error("invalid distinct integer grid");
  const f=[...input].sort((a,b)=>a-b), n=f.length, ix=new Map(f.map((x,i)=>[x,i]));
  const residual=Array(n).fill(0), silent=Array(n).fill(0), midpoint=Array(n).fill(0);
  const witness=[], masks=new Set();
  for(let i=0;i<n;i++) for(let j=i;j<n;j++) for(let k=0;k<n;k++){
    if(k===i||k===j) continue;
    const l=ix.get(f[i]+f[j]-f[k]); if(l===undefined) continue;
    const weight=i===j?1:2;
    residual[l]+=weight;
    if(k!==l) silent[l]+=weight;
    else midpoint[l]+=weight;
    const mask=(1<<i)^(1<<j)^(1<<k)^(1<<l);
    masks.add(mask>>>0);
    witness.push({i,j,k,l,weight});
  }
  return {f,residual,silent,midpoint,peak:Math.max(...silent),
    total:residual.reduce((a,b)=>a+b,0),sidon:!witness.length,
    apFree:!midpoint.some(Boolean),masks:[...masks].sort((a,b)=>a-b),witness};
}
function* combinations(xs,k,start=0,p=[]){
  if(k===0){yield p;return;}
  for(let j=start;j<=xs.length-k;j++) yield* combinations(xs,k-1,j+1,[...p,xs[j]]);
}
// Finite search. Complete frontiers only when all candidates inspected.
export function plan(allowed,n,required=[],budget=100000){
  if(!Array.isArray(allowed)||allowed.length>128||!Number.isInteger(n)||n<2||n>32||
    new Set(allowed).size!==allowed.length||allowed.some(x=>!Number.isSafeInteger(x)||Math.abs(x)>1e9)||
    !Array.isArray(required)||new Set(required).size!==required.length||required.some(x=>!allowed.includes(x))||
    required.length>n||n>allowed.length||!Number.isSafeInteger(budget)||budget<1) throw Error("invalid planner input");
  const free=allowed.filter(x=>!required.includes(x)).sort((a,b)=>a-b);
  let visited=0,sidon=0,apFree=0,apFalse=0,frontier=[],best=null;
  for(const c of combinations(free,n-required.length)){
    if(visited===budget)return {status:"BUDGET_EXHAUSTED",visited,sidon,apFree,apFalse,frontier,best};
    visited++;
    const a=analyze([...required,...c]), v={f:a.f,peak:a.peak,total:a.total};
    sidon+=Number(a.sidon);apFree+=Number(a.apFree);apFalse+=Number(a.apFree&&a.peak>0);
    if(!best||v.peak<best.peak||(v.peak===best.peak&&v.total<best.total))best=v;
    if(frontier.some(u=>u.peak<=v.peak&&u.total<=v.total))continue;
    frontier=frontier.filter(u=>!(v.peak<=u.peak&&v.total<=u.total));frontier.push(v);
  }
  frontier.sort((a,b)=>a.peak-b.peak||a.total-b.total);
  return {status:"COMPLETE",visited,sidon,apFree,apFalse,frontier,best};
}
// Each code label is a bit vector. Every nontrivial cubic monomial must have
// nonzero XOR of labels on its odd-multiplicity support.
export function phasePlan(f,maxBits=5,budget=1000000){
  if(!Number.isInteger(maxBits)||maxBits<0||maxBits>8||
     !Number.isSafeInteger(budget)||budget<1)throw Error("invalid phase budget");
  const a=analyze(f), n=a.f.length, masks=a.masks;
  let visited=0;
  const groups=Array.from({length:n},()=>[]);
  for(const m of masks)groups[31-Math.clz32(m)].push(m);
  const labels=Array(n).fill(0);
  function dfs(i,limit){
    if(i===n)return true;
    for(let v=0;v<limit;v++){
      if(++visited>budget)return null;
      labels[i]=v;
      if(groups[i].some(m=>{
        let x=0;for(let k=0;k<=i;k++)if((m>>>k)&1)x^=labels[k];return x===0;
      }))continue;
      const ans=dfs(i+1,limit);if(ans!==false)return ans;
    }return false;
  }
  // Global XOR translation does not alter even-cardinality constraints.
  for(let bits=0;bits<=maxBits;bits++){
    const ans=dfs(1,2**bits);
    if(ans===null)return {status:"BUDGET_EXHAUSTED",visited:visited-1,bitsProvenImpossibleBelow:bits};
    if(ans)return {status:"OPTIMAL",bits,frames:2**bits,labels:[...labels],visited};
  }
  return {status:"INFEASIBLE_WITHIN_BITS",visited,maxBits};
}
export function sign(label,frame){
  let v=(label&frame)>>>0,p=0;while(v){p^=1;v=(v&(v-1))>>>0;}return p?-1:1;
}
export function census(){
  const rows=[];
  for(let n=3;n<=6;n++)for(let span=n-1;span<=20;span++){
    const p=plan(Array.from({length:span+1},(_,i)=>i),n,[0,span]);
    rows.push({n,span,...p});
  }
  return {rows,phase:Array.from({length:9},(_,i)=>{
    const n=i+2,f=Array.from({length:n},(_,j)=>j);
    return {n,...phasePlan(f)};
  })};
}
