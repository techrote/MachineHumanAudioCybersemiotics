"use strict";
// Synthetic finite model; no participant data. Node: node laboratory.cjs
function laboratory(){
  const pc=x=>{let n=0;while(x){n+=x&1;x>>=1}return n};
  const dist=(x,y)=>pc(x^y);
  const check=(condition,msg)=>{if(!condition)throw Error(msg)};
  const totals={cases:0,worlds:0,policyChecks:0}, rows=[];
  for(let n=1;n<=7;n++)for(let d=1;d<=n;d++)for(let t=0;t<=Math.min(2,n);t++){
    const a=0,b=(1<<d)-1,words=Array.from({length:1<<n},(_,i)=>i);
    const A=words.filter(w=>dist(a,w)<=t),B=words.filter(w=>dist(b,w)<=t);
    const I=A.filter(w=>B.includes(w)).length,V=A.length;
    const policies=["exact","nearest","bounded","joint"];
    const c=Object.fromEntries(policies.map(p=>[p,{correct:0,wrong:0,abstain:0}]));
    for(const x of A)for(const y of B)for(const swap of [false,true]){
      const obs=swap?[y,x]:[x,y],truth=swap?1:0;
      const ds=obs.map(w=>dist(a,w));
      const uniq=indices=>indices.length===1?indices[0]:-1;
      const indices=[0,1];
      const decisions={
        exact:uniq(indices.filter(i=>ds[i]===0)),
        nearest:uniq(indices.filter(i=>ds[i]===Math.min(...ds))),
        bounded:uniq(indices.filter(i=>ds[i]<=t)),
        joint:uniq(indices.filter(i=>ds[i]<=t&&dist(b,obs[1-i])<=t))
      };
      for(const p of policies){let j=decisions[p];c[p][j===-1?"abstain":j===truth?"correct":"wrong"]++;totals.policyChecks++}
      totals.worlds++;
    }
    const W=2*V*V;
    check(c.bounded.wrong===0&&c.joint.wrong===0,"soundness");
    check(c.bounded.abstain===2*V*I&&c.joint.abstain===2*I*I,"intersection identities");
    check((I===0)===(d>2*t),"separation");
    check(c.exact.wrong===2*(d<=t?V-1:0),"false exact");
    check(policies.every(p=>Object.values(c[p]).reduce((s,v)=>s+v,0)===W),"counts");
    totals.cases++;
    if(n===5)rows.push({n,d,t,V,I,W,...c});
  }
  // Negative control: violated edit bound; even bounded unique match can be false.
  const observation=[7,0], t=1;
  check(observation.filter(w=>dist(0,w)<=t).length===1&&dist(0,observation[0])>t,"out-of-model control");
  // Two distinct histories give same ordered observations; even full prior context cannot decide.
  check(dist(0,1)<=1&&dist(3,2)<=1&&dist(0,2)<=1&&dist(3,1)<=1,"swapped histories");
  return {totals,rows,negativeControl:{original:[0,7],observed:observation,targetSlot:0,assumedBudget:1,actualTargetEdits:3}};
}
console.log(JSON.stringify(laboratory(),null,2));
