import {ranges,witness,histogram,minimax} from "./lift.mjs";

function brute(M,p,b){
  const counts=new Map();
  function rec(i,sum){
    if(i===p.length){if(sum%M!==0)throw Error("nonclosing");const w=sum/M;counts.set(w,(counts.get(w)||0)+1);return;}
    for(let delta=-b[i];delta<=b[i];delta++)if(((p[i]+delta)%M+M)%M===p[(i+1)%p.length])rec(i+1,sum+delta);
  }
  rec(0,0);return counts;
}

function run(){
  const assert=(v,msg)=>{if(!v)throw Error(msg);};
  let cases=0,feasible=0,ambiguous=0,infeasible=0,targets=0,minimaxChecks=0,nonuniform=0;
  const byModulus=[];
  function check(M,p,b){
    cases++;const a=ranges(M,p,b),h=histogram(M,p,b),oracle=brute(M,p,b);
    if(!oracle.size){infeasible++;assert(a.status==="infeasible"&&h.status==="infeasible","infeasible disagreement");return;}
    feasible++;const ws=[...oracle.keys()].sort((a,b)=>a-b);
    if(ws.length>1)ambiguous++;
    assert(a.min===ws[0]&&a.max===ws.at(-1)&&ws.length===a.max-a.min+1,"range mismatch");
    assert(h.status==="complete"&&h.counts.length===ws.length,"histogram size");
    for(const w of ws){
      targets++;assert(h.counts[w-a.min]===String(oracle.get(w)),"count mismatch");
      const d=witness(M,p,b,w);
      assert(d.reduce((s,x)=>s+x,0)===w*M&&d.every((x,i)=>Math.abs(x)<=b[i]&&((p[i]+x)%M+M)%M===p[(i+1)%p.length]),"bad witness");
    }
    assert(witness(M,p,b,a.min-1)===null&&witness(M,p,b,a.max+1)===null,"outside interval");
  }
  for(let M=2;M<=6;M++){
    const before=[cases,feasible,ambiguous,infeasible];
    for(let n=2;n<=4;n++){
      for(let code=0;code<M**(n-1);code++){
        let q=code;const p=[0];for(let i=1;i<n;i++){p.push(q%M);q=Math.floor(q/M);}
        for(let B=0;B<=M+1;B++)check(M,p,p.map(()=>B));
        for(let w=-2;w<=2;w++){
          const z=minimax(M,p,w);assert(z.status==="optimal","minimax status");
          const lower=z.budget===0?new Map():brute(M,p,p.map(()=>z.budget-1));
          assert(!lower.has(w)&&brute(M,p,p.map(()=>z.budget)).has(w),"nonminimal budget");minimaxChecks++;
        }
        const budgets=p.map((x,i)=>(x+2*i+code)%(M+2));check(M,p,budgets);nonuniform++;
      }
    }
    byModulus.push({M,cases:cases-before[0],feasible:feasible-before[1],ambiguous:ambiguous-before[2],infeasible:infeasible-before[3]});
  }
  const p=[0,6,12,2,8,14,4,10];
  const uniform=histogram(16,p,p.map(()=>22));
  const mixed=histogram(16,p,[22,6,6,6,22,6,6,6]);
  assert(uniform.min===-5&&uniform.max===11&&uniform.total==="6561","alias family");
  assert(mixed.min===1&&mixed.max===5&&mixed.counts.join(",")==="1,2,3,2,1","mixed case");
  assert(histogram(16,p,p.map(()=>22),1).status==="budget_exhausted","budget distinction");
  assert(ranges(16,p,p.map(()=>7)).min===3&&ranges(16,p,p.map(()=>7)).max===3,"unique control");
  assert(histogram(16,[0,8],[8,8]).counts.join(",")==="1,2,1","antipodal tie");
  assert(histogram(2,Array(80).fill(0),Array(80).fill(2)).total===String(3n**80n),"bigint counts");
  let familyChecks=0;
  for(let n=2;n<=32;n++)for(let k=0;k<=4;k++){
    const a=histogram(12,Array(n).fill(0),Array(n).fill(k*12));
    assert(a.min===-n*k&&a.max===n*k&&a.total===String(BigInt(2*k+1)**BigInt(n)),"flat family");familyChecks++;
  }
  return {population:"synthetic quantized cyclic observations, first phase zero; no participant data",cases,feasible,ambiguous,infeasible,targets,minimaxChecks,nonuniform,byModulus,familyChecks,alias:{phases:p,uniform,mixed,minimax:Array.from({length:17},(_,i)=>({winding:i-5,...minimax(16,p,i-5)}))}};
}

console.log(JSON.stringify(run(),null,2));
