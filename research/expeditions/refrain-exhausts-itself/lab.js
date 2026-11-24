"use strict";
// MHAC #302: synthetic finite trail census, no dependencies; node lab.js
function census(k,n){
  const V=k**(n-1), E=k**n;
  if(E>32)throw Error("bounded census only");
  const factorial=x=>x<2?1:x*factorial(x-1);
  const D=factorial(k)**V;
  const full=(1n<<BigInt(E))-1n;
  const used=(mask,e)=>Boolean(mask&(1n<<BigInt(e)));
  const options=(cur,mask)=>Array.from({length:k},(_,b)=>cur*k+b).filter(e=>!used(mask,e));
  // For a valid trail from 0 the residual degrees already satisfy the Euler-trail condition.
  // All non-isolated vertices must be weakly connected to the current vertex.
  function connected(cur,mask){
    if(mask===full)return cur===0;
    const adj=Array.from({length:V},()=>[]);
    const active=new Set();
    for(let e=0;e<E;e++)if(!used(mask,e)){
      const a=Math.floor(e/k),b=e%V;
      adj[a].push(b);adj[b].push(a);active.add(a);active.add(b);
    }
    const seen=new Set([cur]),stack=[cur];
    while(stack.length)for(const b of adj[stack.pop()])if(!seen.has(b)){seen.add(b);stack.push(b)}
    return [...active].every(x=>seen.has(x));
  }
  let prefixes=0, checks=0, goodMoves=0,badMoves=0, success=0, successWeight=0, witness=null, firstFull=null;
  const lengths={},weights={};
  const assert=(condition,message)=>{checks++;if(!condition)throw Error(message)};
  function visit(cur,mask,word,denom){
    prefixes++;
    const opts=options(cur,mask);
    let possible=false;
    if(!opts.length){
      const l=word.length;
      assert(D%denom===0,"exact weight");
      lengths[l]=(lengths[l]||0)+1;
      weights[l]=(weights[l]||0)+D/denom;
      if(mask===full){
        assert(cur===0,"closure");
        assert(denom===D,"full trail probability");
        success++;successWeight+=D/denom;possible=true;
        if(firstFull===null)firstFull=word;
        // Verify all lower-order cyclic window frequencies, independently from graph walk.
        for(let m=1;m<=n;m++){
          const counts=new Map();
          for(let i=0;i<E;i++){
            let s="";
            for(let j=0;j<m;j++)s+=word[(i+j)%E];
            counts.set(s,(counts.get(s)||0)+1);
          }
          assert(counts.size===k**m && [...counts.values()].every(x=>x===k**(n-m)),"cyclic multiplicities");
        }
      }else if(witness===null||word.length<witness.length)witness=word;
    }else{
      for(const e of opts){
        const good=visit(e%V,mask|(1n<<BigInt(e)),word+String(e%k),denom*opts.length);
        if(good)goodMoves++;else badMoves++;
        possible=possible||good;
      }
    }
    assert(connected(cur,mask)===possible,"residual guard vs exhaustive search");
    return possible;
  }
  assert(visit(0,0n,"",1),"initial completion");
  assert(Object.values(weights).reduce((a,b)=>a+b,0)===D,"probability mass");
  assert(successWeight*k**(n-1)===D,"closed-form success probability");
  return {k,n,V,E,prefixes,checks,goodMoves,badMoves,success,successWeight,D,terminalLengths:lengths,terminalProbabilityWeights:weights,shortestStall:witness,firstFull};
}
const cases = [[2,2],[2,3],[2,4],[2,5],[3,2]];
console.log(JSON.stringify(cases.map(([k,n])=>census(k,n)),null,2));
