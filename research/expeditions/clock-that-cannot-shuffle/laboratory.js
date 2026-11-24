function check(ok,msg){if(!ok)throw Error(msg)}

function* shuffles(lengths,prefix=[],used=lengths.map(()=>0)){
  if(prefix.length===lengths.reduce((a,b)=>a+b,0)){yield prefix;return}
  for(let i=0;i<lengths.length;i++)if(used[i]<lengths[i]){
    const u=used.slice();u[i]++;yield* shuffles(lengths,[...prefix,i],u)
  }
}

function events(times,word){
  check(times.length>=1&&times.length<=6&&times.every(t=>t.length>0&&t.every((v,i)=>Number.isSafeInteger(v)&&Math.abs(v)<=1000000&&(!i||v>t[i-1]))),"bad clocks");
  const used=times.map(()=>0);
  const out=word.map(c=>{check(Number.isInteger(c)&&c>=0&&c<times.length&&used[c]<times[c].length,"bad word");return [c,times[c][used[c]++]]});
  check(used.every((v,i)=>v===times[i].length),"incomplete word");return out
}

function witness(times,word){
  const es=events(times,word),k=times.length,d=Array(k).fill(0);
  const edges=es.slice(1).map(([v,b],i)=>{const [u,a]=es[i];return [v,u,k*(b-a)-1]});
  for(let pass=0;pass<k;pass++){
    let changed=false;
    for(const [v,u,w] of edges)if(d[u]>d[v]+w){d[u]=d[v]+w;changed=true}
    if(!changed){
      const numerators=d.map(x=>x-d[0]);
      const adjusted=es.map(([c,t])=>k*t+numerators[c]);
      check(adjusted.every((v,i)=>!i||v>adjusted[i-1]),"invalid offset witness");
      return {denominator:k,numerators,adjusted}
    }
  }return null
}

function differenceSet(a,b){return new Set(a.flatMap(x=>b.map(y=>x-y)))}

function regionCount(times){
  check(times.length===2||times.length===3,"region count: two or three clocks only");
  const X=differenceSet(times[0],times[1]);
  if(times.length===2)return X.size+1;
  const Y=differenceSet(times[0],times[2]),D=differenceSet(times[1],times[2]);
  let T=0;for(const x of X)for(const y of Y)if(D.has(y-x))T++;
  const p=X.size,q=Y.size,r=D.size;
  return 1+p+q+r+p*q+p*r+q*r-T
}

function pairwiseOK(times,word){
  for(let i=0;i<times.length;i++)for(let j=i+1;j<times.length;j++){
    if(!witness([times[i],times[j]],word.filter(v=>v===i||v===j).map(v=>v===i?0:1)))return false
  }return true
}

function upper(a,b,c){const p=a*b,q=a*c,r=b*c;return 1+p+q+r+p*q+p*r+q*r-a*b*c}

function census(){
  const words=[...shuffles([2,2,2])],pairWords=[...shuffles([2,2])];
  const hist={},examples={};let profiles=0,orders=0,feasible=0,locallyOnly=0,pairProfiles=0,pairOrders=0;
  for(let a=1;a<=8;a++)for(let b=1;b<=8;b++){
    const t=[[0,a],[0,b]],n=pairWords.filter(w=>witness(t,w)).length;
    check(n===regionCount(t),"2D oracle mismatch");pairProfiles++;pairOrders+=pairWords.length
  }
  for(let a=1;a<=8;a++)for(let b=1;b<=8;b++)for(let c=1;c<=8;c++){
    const t=[[0,a],[0,b],[0,c]];let n=0;
    for(const word of words){
      const v=witness(t,word),p=pairwiseOK(t,word);orders++;
      if(v){n++;check(p,"global implies pairwise")}else if(p){locallyOnly++;examples.pairwise??={times:t,word}}
    }
    check(n===regionCount(t),"3-clock oracle mismatch");
    check(n<=upper(2,2,2),"upper bound mismatch");
    profiles++;feasible+=n;hist[n]=(hist[n]??0)+1
  }
  const generic=[];
  for(let a=1;a<=3;a++)for(let b=1;b<=3;b++)for(let c=1;c<=3;c++){
    let i=0;const t=[a,b,c].map(n=>Array.from({length:n},()=>2**i++));
    const n=[...shuffles([a,b,c])].filter(w=>witness(t,w)).length;
    check(n===upper(a,b,c)&&n===regionCount(t),"generic bound mismatch");generic.push({lengths:[a,b,c],regions:n})
  }
  check(witness([[0,1],[0,2]],[0,1,1,0])===null,"nested duration negative");
  check(witness([[0,2],[0,1]],[0,1,1,0])!==null,"nested duration positive");
  let refused=0;for(const [t,w] of [[[[0,0]],[0,0]],[[[0],[0]],[0,0]],[[[0],[0]],[0]]]){
    try{witness(t,w)}catch(e){refused++}
  }check(refused===3,"bad input accepted");
  return {pairProfiles,pairOrders,profiles,orders,feasible,locallyOnly,hist,examples,generic,refused}
}

function audio(times,word){
  // Serial pitch score deliberately does NOT assert physical onset timing.
  const es=events(times,word),rate=8000,slot=800,len=es.length*slot;
  const buf=new Uint8Array(44+2*len),v=new DataView(buf.buffer);
  const tag=(i,s)=>{for(let j=0;j<s.length;j++)buf[i+j]=s.charCodeAt(j)};
  tag(0,"RIFF");v.setUint32(4,36+2*len,true);tag(8,"WAVE");tag(12,"fmt ");v.setUint32(16,16,true);v.setUint16(20,1,true);v.setUint16(22,1,true);v.setUint32(24,rate,true);v.setUint32(28,2*rate,true);v.setUint16(32,2,true);v.setUint16(34,16,true);tag(36,"data");v.setUint32(40,2*len,true);
  const used=times.map(()=>0);
  for(let j=0;j<es.length;j++){
    const [c]=es[j],period=40-5*c-2*used[c]++;
    for(let i=0;i<600;i++){
      const env=Math.min(i,599-i,40),sample=(i%period<period/2?1:-1)*env*150;
      v.setInt16(44+2*(j*slot+i),sample,true)
    }
  }return buf
}

function fingerprint(bytes){let h=2166136261;for(const b of bytes)h=Math.imul(h^b,16777619);return(h>>>0).toString(16).padStart(8,"0")}

function run(){
  const result=census(),example=result.examples.pairwise;
  check(!!example,"no pairwise-only witness found");
  const {times,word}=example;
  const pairs=[];
  for(let i=0;i<3;i++)for(let j=i+1;j<3;j++){
    const w=word.filter(x=>x===i||x===j).map(x=>x===i?0:1);
    pairs.push({clocks:[i,j],word:w,witness:witness([times[i],times[j]],w)})
  }
  const legal=[...shuffles(times.map(x=>x.length))].find(w=>witness(times,w));
  const a=audio(times,word),b=audio(times,legal);
  check(a.length===b.length&&a.some((x,i)=>x!==b[i]),"audio collision");
  return {result,negative:{times,word,pairs,legal,legalWitness:witness(times,legal)},audio:{bytes:a.length,impossible:fingerprint(a),possible:fingerprint(b)}}
}

const result=run();
console.log(JSON.stringify(result,null,2));
if(process.argv[2]){
 const fs=require('node:fs');const out=process.argv[2];fs.mkdirSync(out,{recursive:true});
 const {times,word,legal}=result.negative;
 fs.writeFileSync(out+'/impossible-splice.wav',audio(times,word));
 fs.writeFileSync(out+'/possible-order.wav',audio(times,legal));
 fs.writeFileSync(out+'/execution.json',JSON.stringify(result,null,2)+'\n');
}
