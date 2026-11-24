import {certificate,choose,search,robustFloor,primes} from "./lanes.mjs";
import assert from "node:assert/strict";
let sets=0,rankChecks=0,failures=0;
for(let q=2;q<=12;q++){
  const all=Array.from({length:q},(_,i)=>i);
  for(let m=1;m<=q;m++){
    let optimum=-2;
    for(const C of choose(all,m)){
      sets++;const w=certificate(q,C);let maxBad=0;
      // Independent finite-character oracle: largest equality class for each gap.
      for(let d=1;d<q;d++){
        const bins=Array(q).fill(0);
        for(const c of C)bins[(c*d)%q]++;
        maxBad=Math.max(maxBad,...bins);rankChecks++;
      }
      assert.equal(w.size,maxBad);
      assert.equal(new Set(w.keep.map(c=>(c*w.failGap)%q)).size,1);
      assert.equal(w.erase.length,w.guaranteedErasures+1);
      optimum=Math.max(optimum,w.guaranteedErasures);
      if(w.guaranteedErasures<0)failures++;
    }
    const p=primes(q)[0];
    assert.equal(optimum,m-Math.ceil(m/p)-1);
    assert.equal(certificate(q,all.slice(0,m)).guaranteedErasures,optimum);
  }
}
const results=[];
for(let q=4;q<=12;q++)for(let m=3;m<=Math.min(6,q);m++)for(const e of [0,1])results.push(search(q,m,e));
assert.equal(robustFloor(12,[0,3,6,1],1).sigma,0);
assert.ok(robustFloor(12,[0,1,2,3],1).sigma>0);
assert.throws(()=>certificate(12,[0,0]));
assert.throws(()=>search(17,4,1));
assert.throws(()=>robustFloor(12,[0,1],2));
console.log(JSON.stringify({sets,rankChecks,failures,results},null,2));
