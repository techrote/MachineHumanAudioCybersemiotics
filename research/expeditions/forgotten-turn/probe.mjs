function gcd(a,b){while(b){const t=a%b;a=b;b=t;}return a;}

function lcm(a,b){return a/gcd(a,b)*b;}

function mod(a,b){return ((a%b)+b)%b;}

function probePlan(width,denominators,stateBudget=100000){
  if(!Number.isInteger(width)||width<1||width>1000000||!Array.isArray(denominators)||Array.from(denominators).some(q=>!Number.isInteger(q)||q<2||q>64)||!Number.isSafeInteger(stateBudget)||stateBudget<1)throw RangeError("invalid probe domain");
  if(width===1)return {status:"optimal",denominators:[],period:1,visited:1};
  const qs=[...new Set(denominators)].sort((a,b)=>a-b);
  const queue=[{period:1,path:[]}],seen=new Set([1]);
  for(let i=0;i<queue.length;i++){
    const {period,path}=queue[i];
    for(const q of qs){
      const next=lcm(period,q);
      if(seen.has(next))continue;
      if(next>=width)return {status:"optimal",denominators:[...path,q],period:next,visited:seen.size};
      if(seen.size>=stateBudget)return {status:"budget_exhausted",visited:seen.size};
      seen.add(next);queue.push({period:next,path:[...path,q]});
    }
  }
  return {status:"impossible",visited:seen.size};
}

function probeNumerator(M,start,residue,k,q){
  if(!Number.isInteger(M)||M<2||M>1000000||!Number.isInteger(start)||start<0||start>=M||!Number.isInteger(residue)||residue<0||residue>=M||!Number.isInteger(k)||Math.abs(k)>1000000000||!Number.isInteger(q)||q<2||q>64)throw RangeError("invalid probe");
  return mod(q*start+residue+M*k,q*M);
}

function decodeProbe(M,start,residue,q,observedNumerator,errorNumerator){
  probeNumerator(M,start,residue,0,q);
  const period=q*M;
  if(!Number.isInteger(observedNumerator)||observedNumerator<0||observedNumerator>=period||!Number.isInteger(errorNumerator)||errorNumerator<0||2*errorNumerator>=M)throw RangeError("unsupported observation/error");
  const matches=[];
  for(let k=0;k<q;k++){
    const expected=probeNumerator(M,start,residue,k,q);
    const d=Math.abs(expected-observedNumerator);
    if(Math.min(d,period-d)<=errorNumerator)matches.push(k);
  }
  return matches.length===1?{status:"decoded_residue",residue:matches[0]}:{status:"inconsistent_observation"};
}

function combineResidues(lo,hi,observations){
  if(!Number.isInteger(lo)||!Number.isInteger(hi)||lo>hi||hi-lo>=1000000||Math.abs(lo)>1000000000||Math.abs(hi)>1000000000||!Array.isArray(observations)||Array.from(observations).some(o=>!o||!Number.isInteger(o.q)||o.q<2||o.q>64||!Number.isInteger(o.residue)||o.residue<0||o.residue>=o.q))throw RangeError("invalid residue system");
  let count=0,first=null,last=null;
  for(let k=lo;k<=hi;k++)if(observations.every(o=>mod(k,o.q)===o.residue)){count++;if(first===null)first=k;last=k;}
  return {status:count===0?"inconsistent":count===1?"unique":"ambiguous",count,first,last};
}

export {mod,probePlan,probeNumerator,decodeProbe,combineResidues};
