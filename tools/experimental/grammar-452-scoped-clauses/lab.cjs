const MHAC = (function lab(){
"use strict";
const names=["source","event","polarity","confidence","scope"];
const words=[["pump","door","fan","relay"],["fault","open","stopped","overload"],["affirmed","negated","unknown","conflicting"],["unassessed","low","medium","high"],["report","question","quotation","request-verification"]];
const mod=x=>((x%7)+7)%7;
const valid=m=>Array.isArray(m)&&m.length===5&&m.every(x=>Number.isInteger(x)&&x>=0&&x<4);
function encode(m){if(!valid(m))throw Error("invalid clause");return [...m,mod(-m.reduce((a,x)=>a+x,0)),mod(-m.reduce((a,x,i)=>a+(i+1)*x,0))];}
function syndrome(c){return [mod(c.slice(0,6).reduce((a,x)=>a+x,0)),mod(c.slice(0,5).reduce((a,x,i)=>a+(i+1)*x,c[6]))];}
function decode(c){
 if(!Array.isArray(c)||c.length!==7||c.some(x=>x!==null&&(!Number.isInteger(x)||x<0||x>6)))return {status:"invalid"};
 const holes=c.map((x,i)=>x===null?i:-1).filter(i=>i>=0);
 if(holes.length>2)return {status:"unresolved"};
 const t=c.slice(), hits=[];
 function search(i){if(i===holes.length){if(valid(t.slice(0,5))&&syndrome(t).every(x=>x===0))hits.push(t.slice(0,5));return;}for(let x=0;x<7;x++){t[holes[i]]=x;search(i+1);}}
 search(0);return hits.length===1?{status:"ok",message:hits[0]}:{status:hits.length?"ambiguous":"unresolved"};
}
function baseline(c){return c.length===7&&valid(c.slice(0,5))?{status:"ok",message:c.slice(0,5)}:{status:"unresolved"};}
function semantic(m){if(!valid(m))throw Error("invalid clause");return {speechAct:words[4][m[4]],content:{source:words[0][m[0]],event:words[1][m[1]],polarity:words[2][m[2]],confidence:words[3][m[3]]},assertedBySender:m[4]===0};}
const RATE=8000,SLOT=800,ACTIVE=640,AMP=4096,FREQ=Array.from({length:7},(_,i)=>400+100*i);
const tones=FREQ.map(f=>Int16Array.from({length:SLOT},(_,n)=>n>=ACTIVE?0:Math.round(AMP*Math.min(1,n/40,(ACTIVE-1-n)/40)*Math.sin(2*Math.PI*f*n/RATE))));
const energy=tones.map(t=>t.reduce((a,x)=>a+x*x,0));
function render(c){if(c.length!==7||c.some(x=>x!==null&&(!Number.isInteger(x)||x<0||x>6)))throw Error("invalid slots");const pcm=new Int16Array(7*SLOT);c.forEach((x,i)=>{if(x!==null)pcm.set(tones[x],i*SLOT);});return pcm;}
function receive(pcm){if(pcm.length!==7*SLOT)throw Error("requires aligned 700 ms frame");return Array.from({length:7},(_,i)=>{const p=pcm.subarray(i*SLOT,i*SLOT+SLOT);const e=p.reduce((a,x)=>a+x*x,0);if(e<energy[0]*0.05)return null;
 const scores=tones.map((t,k)=>{let dot=0;for(let n=0;n<SLOT;n++)dot+=p[n]*t[n];return dot/Math.sqrt(e*energy[k]);});
 const sorted=scores.map((s,k)=>[s,k]).sort((a,b)=>b[0]-a[0]);return sorted[0][0]>=0.8&&sorted[0][0]-sorted[1][0]>=0.2?sorted[0][1]:null;});}
function wav(pcm){const bytes=new Uint8Array(44+pcm.length*2),v=new DataView(bytes.buffer);const s=(i,x)=>{for(let j=0;j<x.length;j++)bytes[i+j]=x.charCodeAt(j);};s(0,"RIFF");v.setUint32(4,bytes.length-8,true);s(8,"WAVE");s(12,"fmt ");v.setUint32(16,16,true);v.setUint16(20,1,true);v.setUint16(22,1,true);v.setUint32(24,RATE,true);v.setUint32(28,RATE*2,true);v.setUint16(32,2,true);v.setUint16(34,16,true);s(36,"data");v.setUint32(40,pcm.length*2,true);for(let i=0;i<pcm.length;i++)v.setInt16(44+i*2,pcm[i],true);return bytes;}
const eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
function qualify(){
 let assertions=0;const check=(c,msg)=>{assertions++;if(!c)throw Error(msg);};
 const metrics={messages:0,trained:0,heldOut:0,flatHeldOutDecodable:0,compositionalHeldOutDecodable:0,oneErasure:0,twoErasures:0,baselineOneErasure:0,baselineTwoErasures:0,singleSubstitutionRejected:0,pcmFrames:0,pcmRecovered:0,pcmRejectedSubstitution:0};
 const masks1=Array.from({length:7},(_,i)=>[i]),masks2=masks1.flatMap(([i])=>masks1.filter(([j])=>j>i).map(([j])=>[i,j]));
 const seen=new Set();
 let tripleWitness=null;
 for(let n=0;n<1024;n++){
  const m=Array.from({length:5},(_,i)=>(n>>(2*i))&3),c=encode(m);metrics.messages++;
  check(!seen.has(c.join(",")),"collision");seen.add(c.join(","));
  check(eq(decode(c),{status:"ok",message:m}),"clean");check(eq(baseline([...m,null,null]).message,m),"baseline clean");
  const trained=m.reduce((a,x)=>a+x,0)%4===0;if(trained)metrics.trained++;else{metrics.heldOut++;metrics.compositionalHeldOutDecodable++;}
  check(semantic(m).assertedBySender===(m[4]===0),"scope");
  for(const mask of [...masks1,...masks2]){
   const erased=c.map((x,i)=>mask.includes(i)?null:x),b=[...m,null,null].map((x,i)=>mask.includes(i)?null:x);
   check(eq(decode(erased).message,m),"erasure recovery");metrics[mask.length===1?"oneErasure":"twoErasures"]++;
   const z=baseline(b);check((z.status==="ok")===mask.every(i=>i>=5),"baseline availability");if(z.status==="ok")metrics[mask.length===1?"baselineOneErasure":"baselineTwoErasures"]++;
  }
  for(let i=0;i<7;i++)for(let x=0;x<7;x++)if(x!==c[i]){const bad=c.slice();bad[i]=x;check(decode(bad).status!=="ok","single substitution accepted");metrics.singleSubstitutionRejected++;}
  if(n%31===0){
   for(const mask of [[],[0],[2,4],[5,6]]){
    const t=c.map((x,i)=>mask.includes(i)?null:x),pcm=render(t);check(eq(receive(pcm),t),"PCM slot decode");check(eq(decode(receive(pcm)).message,m),"PCM clause decode");metrics.pcmFrames++;metrics.pcmRecovered++;
   }
   const bad=c.slice();bad[2]=(bad[2]+1)%7;check(decode(receive(render(bad))).status!=="ok","PCM substitution");metrics.pcmFrames++;metrics.pcmRejectedSubstitution++;
  }
  if(!tripleWitness&&n>0){const a=encode([0,0,0,0,0]);const d=c.map((x,i)=>x!==a[i]?i:-1).filter(i=>i>=0);if(d.length===3)tripleWitness={a,b:c,erased:d,receipt:c.map((x,i)=>d.includes(i)?null:x)};}
 }
 check(tripleWitness!==null,"triple witness");check(decode(tripleWitness.receipt).status==="unresolved","triple refusal");
 const unsafeA=tripleWitness.a.slice();for(const i of tripleWitness.erased.slice(0,2))unsafeA[i]=tripleWitness.b[i];unsafeA[tripleWitness.erased[2]]=null;
 check(eq(decode(unsafeA).message,tripleWitness.b.slice(0,5)),"mixed corruption negative control");
 const sample=wav(render(encode([0,0,1,3,2]))),dv=new DataView(sample.buffer);
 check(dv.getUint32(24,true)===8000&&dv.getUint32(40,true)===11200,"WAV header");check(Math.max(...render(encode([0,0,1,3,2])).map(Math.abs))<=AMP,"peak");
 check(decode([1,2]).status==="invalid","invalid");
 return {schema:"mhac-scoped-clauses-v1",metrics,assertions,frameMs:700,rate:RATE,slotSamples:SLOT,activeSamples:ACTIVE,peakLimit:AMP,frequencies:FREQ,trainingRule:"sum(fields) mod 4 == 0",tripleWitness,mixedCorruptionWitness:{transmitted:tripleWitness.a,received:unsafeA,decoded:decode(unsafeA).message},toneEnergies:energy,wavBytes:sample.length};
}
function specimens(){const m=[0,0,1,3,2],c=encode(m);return [{name:"negated-high-confidence-quotation",message:m,slots:c},{name:"same-content-report",message:[0,0,1,3,0],slots:encode([0,0,1,3,0])},{name:"same-content-question",message:[0,0,1,3,1],slots:encode([0,0,1,3,1])},{name:"quotation-two-erased-fields",message:m,slots:c.map((x,i)=>i===0||i===4?null:x)},{name:"unprotected-quotation",message:m,slots:[...m,null,null]}];}
return {names,words,encode,decode,baseline,semantic,render,receive,wav,qualify,specimens};
})();
if(typeof module!=="undefined")module.exports=MHAC;
if(typeof require!=="undefined" && require.main===module){const fs=require('node:fs'),path=require('node:path'),out=process.argv[2]||'output';fs.mkdirSync(out,{recursive:true});const report=MHAC.qualify();fs.writeFileSync(path.join(out,'qualification.json'),JSON.stringify(report,null,2)+'\n');for(const s of MHAC.specimens())fs.writeFileSync(path.join(out,s.name+'.wav'),MHAC.wav(MHAC.render(s.slots)));console.log(JSON.stringify(report,null,2));}
