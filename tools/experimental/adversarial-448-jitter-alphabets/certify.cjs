"use strict";
function certify(q){
  const gcd=(a,b)=>b===0n?a:gcd(b,a%b), abs=x=>x<0n?-x:x;
  function triples(w){return w.map((_,d)=>{const t=w.filter((_,i)=>i!==d).map(BigInt);return {d,a:t[1]-t[0],b:t[2]-t[0],L:BigInt(w[3])}})}
  const result={};let comparisons=0;
  for(const [name,set] of Object.entries(q.results)){
    let best=null;
    for(let i=0;i<set.words.length;i++)for(let j=i+1;j<set.words.length;j++)for(const u of triples(set.words[i]))for(const v of triples(set.words[j])){
      // margin in ms = (600/4)*max(b/L)*abs(a/b-c/d)
      const m=u.b*v.L>=v.b*u.L?u:v;
      let n=150n*m.b*abs(u.a*v.b-v.a*u.b),d=m.L*u.b*v.b;
      const g=gcd(n,d);n/=g;d/=g;comparisons++;
      if(best===null||n*best.d<best.n*d)best={n,d,words:[set.words[i],set.words[j]],deleted:[u.d,v.d]};
    }
    if(Math.abs(Number(best.n)/Number(best.d)-set.margin_ms)>1e-10)throw Error("margin mismatch "+name);
    result[name]={exact_margin_ms:best.n.toString()+"/"+best.d.toString(),words:best.words,deleted_zero_based:best.deleted};
  }
  return {comparisons,result};
}
if(require.main===module){const fs=require("node:fs");const input=process.argv[2]||require("node:path").join(__dirname,"qualification.json");console.log(JSON.stringify(certify(JSON.parse(fs.readFileSync(input,"utf8"))),null,2));}
module.exports={certify};
