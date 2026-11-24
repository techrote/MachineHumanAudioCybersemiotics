"use strict";
// Original finite model; no participant data.
function audit(){
  const gcd=(a,b)=>b?gcd(b,a%b):a;
  const bit=(m,p,t)=>Number(t%m===p);
  let pairs=0,classes=0,checks=0,global=[];
  const assert=(v)=>{checks++;if(!v)throw Error("assertion failed")};
  for(let m=2;m<=16;m++)for(let n=m;n<=16;n++){
    let longest=-1; classes++;
    for(let p=0;p<m;p++)for(let q=0;q<n;q++){
      if(m===n&&p===q)continue;
      pairs++;
      let i=0;const l=m*n/gcd(m,n);
      while(i<l&&bit(m,p,i)===bit(n,q,i))i++;
      assert(i<l);
      const bound=m===n?m-2:2*m-1;
      assert(i<=bound);
      longest=Math.max(longest,i);
    }
    assert(longest===(m===n?m-2:2*m-1));
  }
  for(let M=2;M<=16;M++){
    const hypotheses=Array.from({length:M-1},(_,j)=>j+2).flatMap(m=>Array.from({length:m},(_,p)=>[m,p]));
    const L=M===2?1:2*M-2;
    for(const k of [L-1,L]){
      const words=new Set(hypotheses.map(([m,p])=>Array.from({length:k},(_,t)=>bit(m,p,t)).join("")));
      assert((words.size===hypotheses.length)===(k===L));
    }
    global.push([M,hypotheses.length,L]);
  }
  return {periodPairs:classes,phasePairs:pairs,assertions:checks,global};
}
console.log(JSON.stringify(audit(),null,2));
