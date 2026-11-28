"use strict";
const original=[[0,1,4,13],[0,1,5,6],[0,1,10,17],[0,1,11,12],[0,1,14,18],[0,1,15,16],[0,2,7,18],[0,2,11,13],[0,2,15,17],[0,3,5,9],[0,3,7,10],[0,3,8,17],[0,3,11,14],[0,3,13,16],[0,4,6,9],[0,4,11,15],[0,4,17,18],[0,5,12,17],[0,5,13,18],[0,6,7,13],[0,6,11,17],[0,7,8,15],[0,7,16,17],[0,9,12,13],[0,9,14,17],[0,11,16,18]];
function experiment(original){
  "use strict";
  const s0=.6, rate=8000, levels=[0,.0005,.002,.005,.01], seeds=[101,307,901], repeats=24;
  let checks=0;
  const assert=(x,m)=>{checks++;if(!x)throw Error(m)};
  const gcd=(a,b)=>b?gcd(b,a%b):a;
  function rng(seed){return ()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296}}
  const words=[];for(let L=3;L<=18;L++)for(let a=1;a<L;a++)for(let b=a+1;b<L;b++)if(gcd(gcd(a,b),L)===1)words.push([0,a,b,L]);
  assert(words.length===712,"primitive census");
  const triples=w=>w.map((_,d)=>{const t=w.filter((_,i)=>i!==d);return {d,t:t.map(x=>x/w[3]),span:(t[2]-t[0])/w[3],r:(t[1]-t[0])/(t[2]-t[0])}});
  const ts=words.map(triples);
  const ids=original.map(w=>words.findIndex(x=>String(x)===String(w)));assert(ids.length===26&&ids.every(i=>i>=0),"source words");
  const n=words.length, distances=new Float64Array(n*n);
  function pair(i,j){let best={margin:Infinity};for(const a of ts[i])for(const b of ts[j]){const margin=s0*Math.max(a.span,b.span)*Math.abs(a.r-b.r)/4;if(margin<best.margin)best={i,j,a,b,margin}}return best}
  for(let i=0;i<n;i++)for(let j=i+1;j<n;j++)distances[i*n+j]=distances[j*n+i]=pair(i,j).margin;
  const dist=(i,j)=>distances[i*n+j];
  function quality(set){let v=Infinity;for(let i=0;i<set.length;i++)for(let j=i+1;j<set.length;j++)v=Math.min(v,dist(set[i],set[j]));return v}
  function weakest(set){let w={margin:Infinity};for(let i=0;i<set.length;i++)for(let j=i+1;j<set.length;j++){const p=pair(set[i],set[j]);if(p.margin<w.margin)w=p}return w}
  assert(quality(ids)>0,"noiseless source packing");
  // Deterministic farthest-first + bounded single replacement. No evaluation seed used.
  function search(pool,starts){let best=[],score=-1;for(const start of starts){let set=[start];while(set.length<8){let pick=-1,v=-1;for(const x of pool){if(set.includes(x))continue;const q=Math.min(...set.map(y=>dist(x,y)));if(q>v+1e-14){pick=x;v=q}}set.push(pick)}
    for(let sweep=0;sweep<3;sweep++){let changed=false;for(let k=0;k<8;k++){let winner=set[k],v=quality(set);for(const x of pool){if(set.includes(x))continue;const trial=set.slice();trial[k]=x;const q=quality(trial);if(q>v+1e-14){winner=x;v=q}}if(winner!==set[k]){set[k]=winner;changed=true}}if(!changed)break}
    const q=quality(set);if(q>score+1e-14){best=set;score=q}
  }return best}
  const all=words.map((_,i)=>i), sr=rng(448),starts=[...new Set([...ids,...Array.from({length:32},()=>Math.floor(sr()*n))])];
  const baseline=ids.slice(0,8), subset=search(ids,ids), optimized=search(all,starts);
  assert(quality(subset)>=quality(baseline)-1e-14,"source search baseline");
  assert(quality(optimized)>=quality(subset)-1e-14,"larger pool search");
  // A candidate is feasible iff some a >= s0 makes all pairwise
  // differences of y-a*t <= 2*eps; translation then exists.
  function compatible(t,y,eps){let lo=s0,hi=Infinity;for(let i=0;i<3;i++)for(let j=i+1;j<3;j++){const d=t[j]-t[i],q=y[j]-y[i];lo=Math.max(lo,(q-2*eps)/d);hi=Math.min(hi,(q+2*eps)/d)}return lo<=hi+1e-12}
  function membership(set,y,eps){return set.filter(i=>ts[i].some(a=>compatible(a.t,y,eps)))}
  function nearest(set,y){const ratio=(y[1]-y[0])/(y[2]-y[0]);let v=Infinity, picks=[];for(const i of set){const q=Math.min(...ts[i].map(a=>Math.abs(a.r-ratio)));if(q<v-1e-12){v=q;picks=[i]}else if(Math.abs(q-v)<=1e-12)picks.push(i)}return picks}
  function classify(picks,id,c){if(picks.length!==1)c.abstain++;else if(picks[0]===id)c.correct++;else c.wrong++}
  function evaluate(set){const results=[];for(const eps of levels){for(const mode of ["uniform","endpoint"]){let near={correct:0,wrong:0,abstain:0},bounded={correct:0,wrong:0,abstain:0},invalid=0,total=0;for(const seed of seeds){const r=rng(seed);for(const id of set)for(const a of ts[id])for(let k=0;k<repeats;k++){const scale=s0+.4*r(), offset=.1+.1*r();const y=a.t.map(t=>Math.round(rate*(offset+scale*t+eps*(mode==="uniform"?2*r()-1:r()<.5?-1:1)))/rate);total++;if(y[0]>=y[1]||y[1]>=y[2]){invalid++;continue}const m=membership(set,y,eps+.5/rate);assert(m.includes(id),"bounded receiver lost true word");classify(m,id,bounded);classify(nearest(set,y),id,near)}}assert(total===near.correct+near.wrong+near.abstain+invalid,"near count");assert(total===bounded.correct+bounded.wrong+bounded.abstain+invalid,"bound count");assert(bounded.wrong===0,"bounded decoder wrong");results.push({eps_ms:eps*1000,mode,total,invalid,near,bounded})}}return results}
  function witness(set){const w=weakest(set),{a,b,margin,i,j}=w;const span=s0*Math.max(a.span,b.span),sa=span/a.span,sb=span/b.span;const A=a.t.map(t=>sa*t),B=b.t.map(t=>sb*t),d=A.map((x,k)=>x-B[k]);const shift=(Math.max(...d)+Math.min(...d))/2;const BB=B.map(x=>x+shift),off=.1-Math.min(A[0],BB[0]),y=A.map((x,k)=>(x+BB[k])/2+off);const ea=y.map((x,k)=>x-A[k]-off),eb=y.map((x,k)=>x-BB[k]-off);assert(Math.abs(Math.max(...ea.map(Math.abs),...eb.map(Math.abs))-margin)<1e-12,"midpoint radius");
    assert(compatible(a.t,y,margin)&&compatible(b.t,y,margin),"literal witness");
    assert(!compatible(a.t,y,0)||!compatible(b.t,y,0),"not exact alias");
    const samples=y.map(t=>Math.round(t*rate)), q=samples.map(t=>t/rate);
    assert(compatible(a.t,q,margin+.5/rate)&&compatible(b.t,q,margin+.5/rate),"quantized witness");
    return {words:[words[i],words[j]],deleted_zero_based:[a.d,b.d],margin_ms:1000*margin,scales_s:[sa,sb],observed_s:y,errors_ms:[ea.map(x=>1000*x),eb.map(x=>1000*x)],samples,quantized_radius_ms:1000*(margin+.5/rate)}
  }
  function wav(samples){const length=samples.at(-1)+240, data=new Int16Array(length);for(const start of samples)for(let k=0;k<80;k++)data[start+k]+=Math.round(7000*Math.sin(2*Math.PI*500*k/rate)*Math.sin(Math.PI*k/79)**2);const buf=new Uint8Array(44+2*length),v=new DataView(buf.buffer),tag=(o,s)=>{for(let k=0;k<s.length;k++)buf[o+k]=s.charCodeAt(k)};tag(0,"RIFF");v.setUint32(4,buf.length-8,true);tag(8,"WAVE");tag(12,"fmt ");v.setUint32(16,16,true);v.setUint16(20,1,true);v.setUint16(22,1,true);v.setUint32(24,rate,true);v.setUint32(28,rate*2,true);v.setUint16(32,2,true);v.setUint16(34,16,true);tag(36,"data");v.setUint32(40,2*length,true);for(let k=0;k<length;k++)v.setInt16(44+2*k,data[k],true);assert(data.every(x=>Math.abs(x)<=7000),"PCM peak");return buf}
  const groups={source26:ids,source8:baseline,source8_searched:subset,robust8:optimized}, results={}, audio={};
  for(const [name,set] of Object.entries(groups)){const w=witness(set), a=wav(w.samples),b=wav(w.samples);assert(a.length===b.length&&a.every((x,i)=>x===b[i]),"literal identical waveform");audio[name]=a;results[name]={words:set.map(i=>words[i]),margin_ms:quality(set)*1000,witness:w,wav_bytes:a.length, trials:evaluate(set)}}
  return {receipt:{source_ref:"07fb2f67a5a2cf26312699410f00152033cae843",base:"495a98ca12bae467a507031f04931aa4254b1866",model:{rate,s0,scale_trial_range:[.6,1],levels_ms:levels.map(x=>x*1000),seeds,repeats,search_seed:448,search_starts:starts.length,source_search_starts:ids.length,max_replacement_sweeps:3,candidate_count:n},checks,results},audio};
}
if(require.main===module){const fs=require("node:fs"),path=require("node:path"),crypto=require("node:crypto");const out=process.argv[2];if(!out)throw Error("usage: node lab.cjs OUTPUT_DIRECTORY");fs.mkdirSync(out,{recursive:true});const {receipt,audio}=experiment(original);fs.writeFileSync(path.join(out,"qualification.json"),JSON.stringify(receipt,null,2)+"\n");for(const [name,bytes] of Object.entries(audio)){fs.writeFileSync(path.join(out,name+".wav"),bytes);console.log(name,crypto.createHash("sha256").update(bytes).digest("hex"));}console.log("assertions",receipt.checks);}
module.exports={experiment,original};
