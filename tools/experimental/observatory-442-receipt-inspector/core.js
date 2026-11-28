"use strict";
function apparatus(){
const source="07fb2f67a5a2cf26312699410f00152033cae843";
const gcd=(a,b)=>b?gcd(b,a%b):a;
const ratio=(a,b)=>{let g=gcd(a,b);return `${a/g}/${b/g}`};
const round=(n,d)=>Math.floor((2*n+d)/(2*d));
const rates=[8000,16000,48000], spans=[200,800,1600];
function condition(p,q,rate,ms,frame){
 if(!Number.isInteger(p)||!Number.isInteger(q)||p<1||q<1||p>10000||q>10000||!rates.includes(rate)||!spans.includes(ms)||!["fixed","receipt"].includes(frame))throw Error("Unsupported condition");
 const nominal=[0,p,p+q,2*p+q], duration=rate*ms/1000, pad=rate/10;
 const rows=nominal.map((_,i)=>{
   const r=nominal.filter((_,j)=>i!==j), lo=frame==="fixed"?0:r[0], den=frame==="fixed"?nominal[3]:r[2]-r[0];
   return {deleted:i+1,shape:ratio(r[1]-r[0],r[2]-r[0]),samples:r.map(t=>pad+round((t-lo)*duration,den))};
 });
 const groups={}; for(const r of rows)(groups[r.samples.join(",")]??=[]).push(r.deleted);
 const sizes=Object.values(groups).map(g=>g.length), exactShapes=new Set(rows.map(r=>r.shape)).size;
 return {p,q,rate,ms,frame,rows,groups,exactShapes,distinctReceipts:sizes.length,optimalIndexAccuracy:sizes.length/4,conditionalEntropyBits:sizes.reduce((s,n)=>s+n/4*Math.log2(n),0)};
}
function wav(c,row){
 const count=c.rate*(c.ms+200)/1000,pcm=new Int32Array(count), pulse=c.rate/50;
 for(const onset of row.samples) for(let j=0;j<pulse&&onset+j<count;j++){
   // Integer triangular carrier at 500 Hz, integer tapered envelope; no platform-dependent trigonometry.
   const period=c.rate/500,k=j%period,carrier=period-4*Math.abs(k-period/2);
   const env=Math.min(j,pulse-1-j);
   pcm[onset+j]+=Math.trunc(3000*carrier*env/(period*Math.floor(pulse/2)));
 }
 const out=new Uint8Array(44+count*2),v=new DataView(out.buffer);
 const str=(i,s)=>{for(let j=0;j<s.length;j++)out[i+j]=s.charCodeAt(j)};
 str(0,"RIFF");v.setUint32(4,out.length-8,true);str(8,"WAVE");str(12,"fmt ");v.setUint32(16,16,true);v.setUint16(20,1,true);v.setUint16(22,1,true);v.setUint32(24,c.rate,true);v.setUint32(28,c.rate*2,true);v.setUint16(32,2,true);v.setUint16(34,16,true);str(36,"data");v.setUint32(40,count*2,true);
 for(let i=0;i<count;i++)v.setInt16(44+2*i,pcm[i],true);
 return out;
}
function sha256(bytes){
 const K=[0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2];
 const h=[0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19],len=Math.ceil((bytes.length+9)/64)*64,b=new Uint8Array(len);b.set(bytes);b[bytes.length]=128;const dv=new DataView(b.buffer);dv.setUint32(len-4,bytes.length*8);dv.setUint32(len-8,Math.floor(bytes.length/0x20000000));const rr=(x,n)=>(x>>>n)|(x<<(32-n)),w=new Uint32Array(64);
 for(let o=0;o<len;o+=64){for(let j=0;j<16;j++)w[j]=dv.getUint32(o+j*4);for(let j=16;j<64;j++){const a=w[j-15],z=w[j-2];w[j]=(w[j-16]+(rr(a,7)^rr(a,18)^(a>>>3))+w[j-7]+(rr(z,17)^rr(z,19)^(z>>>10)))>>>0;}let [a,c,d,e,f,g,i,j]=h;for(let k=0;k<64;k++){let t=(j+(rr(f,6)^rr(f,11)^rr(f,25))+((f&g)^(~f&i))+K[k]+w[k])>>>0,u=((rr(a,2)^rr(a,13)^rr(a,22))+((a&c)^(a&d)^(c&d)))>>>0;[a,c,d,e,f,g,i,j]=[(t+u)>>>0,a,c,d,(e+t)>>>0,f,g,i];} [a,c,d,e,f,g,i,j].forEach((x,k)=>h[k]=(h[k]+x)>>>0);}
 return h.map(x=>x.toString(16).padStart(8,"0")).join("");
}
function specimen(c){return c.rows.map(r=>({deleted:r.deleted,sha256:sha256(wav(c,r))}));}
function run(){
 const pairs=[[1,1],[2,1],[3,2],[5,3],[8,5],[13,8],[21,13],[34,21],[55,34],[89,55],[144,89],[233,144],[377,233],[610,377],[987,610],[1597,987]];
 const rows=[];for(const [p,q] of pairs)for(const rate of rates)for(const ms of spans)for(const frame of ["receipt","fixed"])rows.push(condition(p,q,rate,ms,frame));
 const summary={};for(const frame of ["receipt","fixed"]){const a=rows.filter(r=>r.frame===frame);summary[frame]={conditions:a.length,ambiguous:a.filter(r=>r.distinctReceipts<4).length,oneBitAmbiguity:a.filter(r=>r.conditionalEntropyBits===1).length,meanAccuracy:a.reduce((s,r)=>s+r.optimalIndexAccuracy,0)/a.length};}
 const witness=condition(144,89,8000,800,"receipt"),fixed=condition(144,89,8000,800,"fixed");
 return {schema:"mhac-receipt-inspector-v1",claimClass:"synthetic deterministic measurement",sourceRef:source,seed:null,seedReason:"exhaustive declared finite factorial, no RNG",ratesHz:rates,spanMs:spans,pairs,summary,witness:{...witness,stimuli:specimen(witness)},fixedWitness:{...fixed,stimuli:specimen(fixed)},rows};
}
function tests(){
 let count=0;const ok=(x,m)=>{if(!x)throw Error(m);count++};
 ok(sha256(new Uint8Array())==="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855","sha empty");
 ok(sha256(Uint8Array.of(97,98,99))==="ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad","sha abc");
 const r=run(),w=r.witness,f=r.fixedWitness;
 ok(w.rows[1].samples.join(",")==="800,4755,7200","source onset witness");
 ok(w.rows[3].samples.join(",")==="800,4755,7200","source pair");
 ok(w.rows[1].shape!==w.rows[3].shape,"exact ratios differ");
 ok(w.stimuli[1].sha256===w.stimuli[3].sha256,"WAV equality");
 ok(wav(w,w.rows[1]).every((x,i)=>x===wav(w,w.rows[3])[i]),"literal bytes"); // small witness
 ok(f.distinctReceipts===4,"anchored baseline");
 ok(f.stimuli[1].sha256!==f.stimuli[3].sha256,"anchored WAV differs");
 ok(condition(1,1,8000,800,"receipt").exactShapes===3,"equal gaps");
 ok(r.rows.length===288,"factorial count");
 for(const c of r.rows){ok(c.rows.length===4,"deletion count");ok(c.optimalIndexAccuracy===Object.keys(c.groups).length/4,"accuracy");ok(Object.values(c.groups).flat().sort().join(",")==="1,2,3,4","partition");if(c.frame==="fixed")ok(c.distinctReceipts===4,"fixed baseline");}
 for(const c of [w,f])for(const row of c.rows){const b=wav(c,row),v=new DataView(b.buffer);ok(v.getUint32(24,true)===c.rate&&v.getUint32(40,true)===b.length-44,"WAV header");let peak=0;for(let i=44;i<b.length;i+=2)peak=Math.max(peak,Math.abs(v.getInt16(i,true)));ok(peak<=9000,"bounded peak");}
 let threw=false;try{condition(0,1,8000,800,"fixed")}catch{threw=true}ok(threw,"reject invalid");
 return {assertions:count,status:"PASS"};
}
return {condition,wav,sha256,specimen,run,tests,rates,spans};
}
const MHAC=apparatus();
if(typeof module!=='undefined' && module.exports){module.exports=MHAC;if(require.main===module){const fs=require('node:fs');console.log(JSON.stringify(MHAC.tests()));fs.writeFileSync('receipt.json',JSON.stringify(MHAC.run(),null,2)+'\n');}}
