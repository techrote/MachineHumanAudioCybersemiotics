"use strict";
const FootingLab = (function laboratory() {
  function choose(n,k) {
    if(k<0||k>n)return 0;
    let c=1;
    for(let i=1;i<=Math.min(k,n-k);i++)c=c*(n-i+1)/i;
    return c;
  }
  function boundaries(bits) {
    if(bits.length>16||bits.some(b=>b!==0&&b!==1))throw Error("invalid score");
    const out=[];
    let prev=0;
    for(let i=0;i<=bits.length;i++){
      const next=i===bits.length?0:bits[i];
      if(next!==prev)out.push(i);
      prev=next;
    }
    return out;
  }
  function rank(bits) {
    const n=bits.length,b=boundaries(bits);
    let index=0,lo=0;
    for(let i=0;i<b.length;i++){
      for(let j=lo;j<b[i];j++)index+=choose(n-j,b.length-i-1);
      lo=b[i]+1;
    }
    return {n,runs:b.length/2,index};
  }
  function unrank(n,runs,index) {
    if(!Number.isInteger(n)||n<0||n>16||!Number.isInteger(runs)||runs<0||
       !Number.isInteger(index)||index<0||index>=choose(n+1,2*runs))throw Error("invalid code");
    let remaining=2*runs,lo=0;
    const cuts=[];
    while(remaining){
      const block=choose(n-lo,remaining-1);
      if(index<block){cuts.push(lo);remaining--;}
      else index-=block;
      lo++;
    }
    return Array.from({length:n},(_,i)=>cuts.filter(c=>c<=i).length%2);
  }
  function scopeEffect(frames) {
    if(!Array.isArray(frames)||frames.some(f=>!["LIVE","QUOTE","REHEARSE"].includes(f)))throw Error("unknown frame");
    return frames.every(f=>f==="LIVE")?1:0;
  }
  function footerEffect(events,footer) {
    if(footer!==undefined&&footer!=="LIVE"&&footer!=="QUOTE")throw Error("unknown footer");
    return events.map(()=>footer==="LIVE"?1:0);
  }
  function selftest() {
    let checks=0,patterns=0,frames=0;
    function eq(a,b){checks++;if(JSON.stringify(a)!==JSON.stringify(b))throw Error("mismatch "+JSON.stringify({a,b}));}
    for(let n=0;n<=12;n++){
      const counts=Array(n+1).fill(0),seen=new Set();
      for(let m=0;m<2**n;m++){
        const bits=Array.from({length:n},(_,i)=>(m>>i)&1);
        const x=rank(bits);patterns++;
        counts[x.runs]++;
        eq(unrank(n,x.runs,x.index),bits);
        eq(seen.has(x.runs+":"+x.index),false);
        seen.add(x.runs+":"+x.index);
        const direct=bits.filter((v,i)=>v===1&&(i===0||bits[i-1]===0)).length;
        eq(x.runs,direct);
      }
      for(let k=0;k<=n;k++)eq(counts[k],choose(n+1,2*k));
      eq(seen.size,2**n);
    }
    function walk(path,depth){
      frames++;eq(scopeEffect(path),Number(!path.includes("QUOTE")&&!path.includes("REHEARSE")));
      if(depth)for(const f of ["LIVE","QUOTE","REHEARSE"])walk([...path,f],depth-1);
    }
    walk([],6);
    const events=[220,330,275,440];
    eq(footerEffect(events),[0,0,0,0]);
    eq(footerEffect(events,"QUOTE"),[0,0,0,0]);
    eq(footerEffect(events,"LIVE"),[1,1,1,1]);
    for(const f of [()=>unrank(4,2,5),()=>scopeEffect(["UNKNOWN"]),()=>rank([2]),()=>footerEffect(events,"MAYBE")]){
      let threw=false;try{f();}catch(e){threw=true;}eq(threw,true);
    }
    return {checks,patterns,frames};
  }
  return {choose,boundaries,rank,unrank,scopeEffect,footerEffect,selftest};
})();
if (typeof module !== "undefined") {
  module.exports = FootingLab;
  if (require.main === module) console.log(JSON.stringify(FootingLab.selftest()));
}
