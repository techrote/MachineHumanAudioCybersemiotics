import {mod,probePlan,probeNumerator,decodeProbe,combineResidues} from "./probe.mjs";

function verifyProbes(){
  const assert=(c,m)=>{if(!c)throw Error(m);};let plans=0,observations=0,systems=0;
  for(let width=1;width<=100;width++)for(let mask=0;mask<128;mask++){
    const qs=Array.from({length:7},(_,i)=>i+2).filter((_,i)=>mask&(1<<i));
    let best=Infinity;
    for(let s=0;s<(1<<qs.length);s++){
      const subset=qs.filter((_,i)=>s&(1<<i));
      const keys=new Set(Array.from({length:width},(_,k)=>subset.map(q=>k%q).join(",")));
      if(keys.size===width)best=Math.min(best,subset.length);
    }
    const a=probePlan(width,qs);
    assert(best===Infinity?a.status==="impossible":a.status==="optimal"&&a.denominators.length===best,"plan mismatch");
    plans++;
  }
  for(let M=2;M<=20;M++)for(let q=2;q<=12;q++)for(let k=-q;k<=q;k++){
    const start=M-1,residue=Math.floor(M/2),e=Math.floor((M-1)/2);
    for(let error=-e;error<=e;error++){
      const o=mod(probeNumerator(M,start,residue,k,q)+error,q*M);
      const d=decodeProbe(M,start,residue,q,o,e);
      assert(d.status==="decoded_residue"&&d.residue===mod(k,q),"probe error");observations++;
    }
  }
  for(let width=1;width<=80;width++)for(let k=-20;k<-20+width;k++){
    const p=probePlan(width,[2,3,4,5,6,7,8]);
    if(p.status!=="optimal")continue;
    const d=combineResidues(-20,-21+width,p.denominators.map(q=>({q,residue:mod(k,q)})));
    assert(d.status==="unique"&&d.first===k,"combine error");systems++;
  }
  assert(probePlan(41,[2,3,4,5,6]).denominators.length===3,"example 3");
  assert(probePlan(41,[2,3,4,5,6,7,8]).denominators.length===2,"example 2");
  assert(probePlan(100,[2,4,8]).status==="impossible","negative control");
  assert(probePlan(100,[2,3,4,5,6],1).status==="budget_exhausted","budget status");
  assert(combineResidues(0,10,[{q:2,residue:0},{q:4,residue:1}]).status==="inconsistent","inconsistent");
  return {plans,observations,systems,example41cap6:probePlan(41,[2,3,4,5,6]),example41cap8:probePlan(41,[2,3,4,5,6,7,8]),exampleNested:probePlan(100,[2,4,8])};
}

console.log(JSON.stringify(verifyProbes(),null,2));
