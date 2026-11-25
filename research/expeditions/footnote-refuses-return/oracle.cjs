"use strict";
// Original synthetic oracle; no empirical or auditory claims.
function laboratory() {
  const assert=(ok,msg)=>{if(!ok)throw Error(msg);checks++};
  let checks=0;
  const fact=n=>n<2?1:n*fact(n-1);
  function* words(n,s="",o=0,c=0) {
    if(o===n&&c===n){yield s;return}
    if(o<n)yield* words(n,s+"+",o+1,c);
    if(c<o)yield* words(n,s+"-",o,c+1);
  }
  function* permutations(xs) {
    if(!xs.length){yield [];return}
    for(let i=0;i<xs.length;i++)for(const p of permutations(xs.filter((_,j)=>j!==i)))yield [xs[i],...p];
  }
  function profile(word) {
    let d=0,peak=0,radices=[];
    for(const ch of word){
      if(ch==="+"){peak=Math.max(peak,++d)}
      else if(ch==="-"&&d>0){radices.push(d--)}
      else throw Error("invalid event skeleton");
    }
    if(d!==0)throw Error("unclosed event skeleton");
    return {peak,radices,count:radices.reduce((a,b)=>a*b,1)};
  }
  function encode(word,order) {
    const {count,radices}=profile(word);
    if(order.length!==radices.length)throw Error("wrong close count");
    let active=[],id=0,j=0,rank=0;
    for(const ch of word){
      if(ch==="+")active.push(id++);
      else {
        const k=active.indexOf(order[j++]);
        if(k<0)throw Error("invalid close address");
        rank=rank*active.length+k;active.splice(k,1);
      }
    }
    if(rank>=count)throw Error("rank overflow");
    return rank;
  }
  function decode(word,rank) {
    const {radices,count}=profile(word);
    if(!Number.isSafeInteger(rank)||rank<0||rank>=count)throw Error("invalid rank");
    let digits=[];
    for(let i=radices.length-1;i>=0;i--){digits[i]=rank%radices[i];rank=Math.floor(rank/radices[i])}
    let active=[],id=0,j=0,result=[];
    for(const ch of word){
      if(ch==="+")active.push(id++);
      else result.push(active.splice(digits[j++],1)[0]);
    }
    return result;
  }
  // Independent oracle: close-order permutations are filtered by position, not rank or stack.
  function valid(word,p) {
    let opens=0,closes=0;
    for(const ch of word)if(ch==="+")opens++;else if(p[closes++]>=opens)return false;
    return true;
  }
  let rows=[],skeletons=0,matchings=0;
  for(let n=0;n<=7;n++){
    let row={n,words:0,matchings:0,maxByPeak:{}};
    let perms=[...permutations(Array.from({length:n},(_,i)=>i))];
    for(const word of words(n)){
      const {peak,count}=profile(word);
      const compatible=perms.filter(p=>valid(word,p));
      assert(compatible.length===count,"matching product");
      const ranks=new Set();
      for(const p of compatible){
        const k=encode(word,p);
        assert(!ranks.has(k),"injective rank");
        ranks.add(k);
        assert(decode(word,k).join()===p.join(),"rank inverse");
      }
      assert(ranks.size===count&&[...ranks].every(k=>k>=0&&k<count),"surjective rank");
      row.maxByPeak[peak]=Math.max(row.maxByPeak[peak]||0,count);
      row.words++;row.matchings+=count;
    }
    const df=Array.from({length:n},(_,i)=>2*i+1).reduce((a,b)=>a*b,1);
    assert(row.matchings===df,"double factorial total");
    for(let h=1;h<=n;h++){
      const bound=fact(h)*h**(n-h);
      assert(row.maxByPeak[h]===bound,"sharp depth bound");
      assert(profile("+".repeat(h)+"-+".repeat(n-h)+"-".repeat(h)).count===bound,"bound witness");
    }
    rows.push(row);skeletons+=row.words;matchings+=row.matchings;
  }
  function rejects(fn){try{fn();return false}catch{return true}}
  assert(rejects(()=>profile("-+")),"underflow");
  assert(rejects(()=>profile("+")),"unclosed");
  assert(rejects(()=>profile("x")),"unknown token");
  assert(rejects(()=>encode("+-+-",[1,0])),"future close");
  assert(rejects(()=>encode("++--",[0,0])),"duplicate close");
  assert(rejects(()=>decode("++--",2)),"out of range");
  assert(rejects(()=>decode("++--",0.5)),"noninteger rank");
  assert(encode("++--",[0,1])!==encode("++--",[1,0]),"crossing vs nested");
  return {rows,skeletons,matchings,checks};
}
console.log(JSON.stringify(laboratory(), null, 2));
