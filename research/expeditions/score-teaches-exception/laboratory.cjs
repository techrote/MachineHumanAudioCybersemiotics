"use strict";
// Original synthetic score and affine-code oracle. No listener model.
function lab(){
 const assert=(c,m)=>{if(!c)throw Error(m)};
 const par=x=>{let p=0;while(x){p^=x&1;x>>=1}return p};
 const y=(h,x)=>par(h&(8|x));
 const rules=Array.from({length:16},(_,i)=>i);
 const cube=Array.from({length:8},(_,i)=>i);
 const target=1, rival=7;
 const consistent=(xs,ys)=>rules.filter(h=>xs.every((x,i)=>ys[i]===null||y(h,x)===ys[i]));
 const span=xs=>{let s=new Set([0]);for(const x of xs)for(const v of [...s])s.add(v^(8|x));return s};
 const d=cs=>Math.min(...rules.slice(1).map(h=>cube.reduce((n,x)=>n+cs[x]*y(h,x),0)));
 const formula=n=>4*Math.floor(n/8)+[0,0,0,0,1,1,2,3][n%8];
 let rankChecks=0,predictionChecks=0;
 for(let mask=0;mask<256;mask++){const xs=cube.filter(x=>(mask>>x)&1);const sp=span(xs);
 for(const h of rules){const cs=consistent(xs,xs.map(x=>y(h,x)));assert(cs.length===16/sp.size,"rank");rankChecks++;
 for(const x of cube){assert(new Set(cs.map(k=>y(k,x))).size===(sp.has(8|x)?1:2),"span");predictionChecks++}}}
 let profiles=[],designs=0;
 for(let n=1;n<=12;n++){const c=Array(8).fill(0);let best=-1,count=0,optimal=0,witness;
 function visit(i,left){if(i===7){c[i]=left;count++;let v=d(c);if(v>best){best=v;optimal=0;witness=c.slice()}if(v===best)optimal++;return}for(let j=0;j<=left;j++){c[i]=j;visit(i+1,left-j)}}
 visit(0,n);assert(best===formula(n),"distance formula");designs+=count;profiles.push({n,best,count,optimal,witness})}
 let constructionChecks=0;
 const residual=[[],[0],[0,1],[0,1,2],[0,1,2,4],[0,1,2,4,7],[0,1,2,3,4,5],[0,1,2,3,4,5,6]];
 for(let n=1;n<=512;n++){const c=Array(8).fill(Math.floor(n/8));for(const x of residual[n%8])c[x]++;assert(d(c)===formula(n),"constructive");constructionChecks++}
 let strictDecodes=0;
 for(const h of rules){for(let er=0;er<256;er++){let f=parCount(er);if(f>=4)continue;for(let bad=0;bad<256;bad++){if(er&bad)continue;let e=parCount(bad);if(2*e+f>=4)continue;const received=cube.map(x=>er>>x&1?null:y(h,x)^(bad>>x&1));const cand=rules.filter(k=>received.reduce((a,v,x)=>a+(v!==null&&v!==y(k,x)?1:0),0)<=e);assert(cand.length===1&&cand[0]===h,"decode");strictDecodes++}}}
 function parCount(x){let n=0;while(x){n+=x&1;x>>=1}return n}
 const boundary=cube.map(x=>x===0||x===2?null:y(target,x));
 // h=1 and h=3 disagree on x=2,3,6,7; erase two of them, flip one.
 const mid=cube.map(x=>[2,3].includes(x)?null:x===6?y(3,x):y(target,x));
 const tie=rules.filter(h=>mid.reduce((a,v,x)=>a+(v!==null&&v!==y(h,x)?1:0),0)<=1);
 assert(tie.includes(1)&&tie.includes(3),"boundary");
 const prefix=[0,1,6,7,0,1,6,7];
 const choices=consistent(prefix,prefix.map(x=>y(target,x)));assert(JSON.stringify(choices)==="[1,7]","two laws");
 assert(y(target,2)!==y(rival,2),"diagnostic");
 const score={lawA:[...prefix,2].map(x=>[x,y(target,x)]),lawB:[...prefix,2].map(x=>[x,y(rival,x)]),counterexamples:cube.map(x=>[x,y(target,x)])};
 const rate=16000,slot=3200,tone=2400,fade=160;
 function pcm(rows){const a=new Uint8Array(rows.length*4*slot*2);let i=0;for(const [x,v] of rows){const periods=[0,1,2].map(k=>(x>>k)&1?40:80).concat(v?32:50);for(const period of periods)for(let t=0;t<slot;t++){let s=0;if(t<tone){const p=t%period,tri=8000-Math.floor(32000*Math.abs(p-period/2)/period);s=Math.floor(tri*Math.min(t,tone-1-t,fade)/fade)}a[i++]=s&255;a[i++]=(s>>8)&255}}return a}
 function hash(a){let h=2166136261;for(const b of a)h=Math.imul(h^b,16777619)>>>0;return h.toString(16).padStart(8,"0")}
 const audio=Object.fromEntries(Object.entries(score).map(([k,v])=>[k,pcm(v)]));
 const a=audio.lawA,b=audio.lawB,prefixBytes=(prefix.length*4+3)*slot*2;
 assert(a.slice(0,prefixBytes).every((v,i)=>v===b[i]),"audio common prefix");
 assert(a.some((v,i)=>v!==b[i]),"audio divergence");
 const receipt={rankChecks,predictionChecks,designs,profiles,constructionChecks,strictDecodes,boundary:{received:mid,candidates:tie},rehearsal:{prefix,choices,probe:2,predictions:choices.map(h=>y(h,2))},audio:{rate,slot,tone,fade,commonPrefixSamples:prefixBytes/2,files:Object.fromEntries(Object.entries(audio).map(([k,v])=>[k,{samples:v.length/2,fnv1a32:hash(v)}]))}};
 return {receipt,audio};
}
const {receipt,audio}=lab();
if(typeof process!=="undefined" && process.argv[2]){
 const fs=require("node:fs"),path=require("node:path"),out=process.argv[2];fs.mkdirSync(out,{recursive:true});
 for(const [name,pcm] of Object.entries(audio)){const h=Buffer.alloc(44);h.write("RIFF",0);h.writeUInt32LE(36+pcm.length,4);h.write("WAVEfmt ",8);h.writeUInt32LE(16,16);h.writeUInt16LE(1,20);h.writeUInt16LE(1,22);h.writeUInt32LE(16000,24);h.writeUInt32LE(32000,28);h.writeUInt16LE(2,32);h.writeUInt16LE(16,34);h.write("data",36);h.writeUInt32LE(pcm.length,40);fs.writeFileSync(path.join(out,name+".wav"),Buffer.concat([h,Buffer.from(pcm)]));}
}
console.log(JSON.stringify(receipt,null,2));
