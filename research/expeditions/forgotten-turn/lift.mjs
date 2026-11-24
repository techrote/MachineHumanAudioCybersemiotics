function validate(M,phases,budgets){
  if(!Number.isInteger(M)||M<2||M>1000000||!Array.isArray(phases)||phases.length<2||phases.length>4096||phases.some(p=>!Number.isInteger(p)||p<0||p>=M)) throw new RangeError("invalid phase grid");
  if(!Array.isArray(budgets)||budgets.length!==phases.length||budgets.some(b=>!Number.isInteger(b)||b<0||b>1000000000)) throw new RangeError("invalid slew budget");
}

function ranges(M,phases,budgets){
  validate(M,phases,budgets);
  const edges=phases.map((p,i)=>{
    const residue=(phases[(i+1)%phases.length]-p+M)%M;
    return {residue,lo:Math.ceil((-budgets[i]-residue)/M),hi:Math.floor((budgets[i]-residue)/M)};
  });
  if(edges.some(e=>e.lo>e.hi))return {status:"infeasible",edges};
  const baseline=edges.reduce((s,e)=>s+e.residue,0)/M;
  return {status:"feasible",edges,baseline,min:baseline+edges.reduce((s,e)=>s+e.lo,0),max:baseline+edges.reduce((s,e)=>s+e.hi,0)};
}

function witness(M,phases,budgets,target){
  if(!Number.isSafeInteger(target))throw new RangeError("invalid winding");
  const a=ranges(M,phases,budgets);
  if(a.status!=="feasible"||target<a.min||target>a.max)return null;
  let remaining=target-a.min;
  return a.edges.map(e=>{const add=Math.min(remaining,e.hi-e.lo);remaining-=add;return e.residue+M*(e.lo+add);});
}

function histogram(M,phases,budgets,cellBudget=1000000){
  if(!Number.isSafeInteger(cellBudget)||cellBudget<1)throw new RangeError("invalid cell budget");
  const a=ranges(M,phases,budgets);
  if(a.status!=="feasible")return {status:"infeasible"};
  let cells=1;
  let width=1;
  for(const e of a.edges){width+=e.hi-e.lo;cells+=width;if(cells>cellBudget)return {status:"budget_exhausted",min:a.min,max:a.max};}
  let counts=[1n];
  for(const e of a.edges){
    const span=e.hi-e.lo;
    const next=[];let sum=0n;
    for(let j=0;j<counts.length+span;j++){
      if(j<counts.length)sum+=counts[j];
      if(j-span-1>=0&&j-span-1<counts.length)sum-=counts[j-span-1];
      next.push(sum);
    }
    counts=next;
  }
  return {status:"complete",min:a.min,max:a.max,counts:counts.map(String),total:String(counts.reduce((s,x)=>s+x,0n)),cells};
}

function minimax(M,phases,target){
  if(!Number.isSafeInteger(target))throw new RangeError("invalid winding");
  validate(M,phases,phases.map(()=>0));
  const possible=b=>{const a=ranges(M,phases,phases.map(()=>b));return a.status==="feasible"&&a.min<=target&&target<=a.max;};
  if(!possible(1000000000))return {status:"outside_supported_budget"};
  let lo=0,hi=1000000000;
  while(lo<hi){const mid=Math.floor((lo+hi)/2);if(possible(mid))hi=mid;else lo=mid+1;}
  return {status:"optimal",budget:lo,steps:witness(M,phases,phases.map(()=>lo),target)};
}

export {ranges,witness,histogram,minimax};
