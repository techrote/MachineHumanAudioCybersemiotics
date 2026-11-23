// MHAC #228 — independent same-panel census and original stereo interval instrument.
// Node.js, standard library only. All samples computed with integer arithmetic.
// Run node panel_and_audio.js [output-directory] (optional WAV writing).
function permutations(xs){
 if(!xs.length)return [[]];
 return xs.flatMap((x,i)=>permutations(xs.filter((_,j)=>i!==j)).map(q=>[x,...q]));
}

function panelCensus(){
 const n=4,orders=permutations([0,1,2,3]),loops=[];
 for(const r of orders){
  if(r[0]===0)loops.push(r); // every four-cycle, both orientations
 }
 for(let omitted=0;omitted<n;omitted++){
  const vs=[0,1,2,3].filter(x=>x!==omitted);
  for(const r of permutations(vs))if(r[0]===vs[0])loops.push(r);
 }
 const matrices=orders.map(r=>Array.from({length:n},(_,u)=>Array.from({length:n},(_,v)=>u===v?0:r.indexOf(v)<r.indexOf(u)?1:-1)));
 const histogram={};let count=0,cycles=0,maxDebt=0,maxDebtNoCycle=0,maxDebtCycle=0,zeroDebt=0;
 for(let a=0;a<24;a++)for(let b=a;b<24;b++)for(let c=b;c<24;c++)for(let d=c;d<24;d++){
  const m=Array.from({length:n},(_,u)=>Array.from({length:n},(_,v)=>matrices[a][u][v]+matrices[b][u][v]+matrices[c][u][v]+matrices[d][u][v]));
  // Numerator on a common denominator 12 (LCM of 3 and 4), for raw count margins.
  let max=0,cyclic=false;
  for(const loop of loops){
   const weights=loop.map((u,i)=>m[u][loop[(i+1)%loop.length]]);
   max=Math.max(max,12*weights.reduce((s,x)=>s+x,0)/loop.length);
   if(weights.every(w=>w>0))cyclic=true;
  }
  if(max>24)throw Error("same-panel bound violated");
  count++;if(cyclic)cycles++;if(!max)zeroDebt++;
  if(max===24){maxDebt++;if(cyclic)maxDebtCycle++;else maxDebtNoCycle++}
  const key=String(max);
  if(!histogram[key])histogram[key]={acyclic:0,cyclic:0};
  histogram[key][cyclic?"cyclic":"acyclic"]++;
 }
 if(count!==17550)throw Error("unexpected count");
 return {count,cycles,maxDebt,maxDebtNoCycle,maxDebtCycle,zeroDebt,histogram,unit:"1/48 of normalized margin"};
}

function stereoWav(left,right){
 if(left.length!==right.length||left.some(f=>!Number.isInteger(f)||f<40||f>3000)||right.some(f=>!Number.isInteger(f)||f<40||f>3000))throw Error("invalid frequency path");
 const rate=16000,framesPerNote=3200,frames=left.length*framesPerNote,bytes=new Uint8Array(44+4*frames),dv=new DataView(bytes.buffer);
 function chars(at,s){for(let i=0;i<s.length;i++)bytes[at+i]=s.charCodeAt(i)}
 chars(0,"RIFF");dv.setUint32(4,bytes.length-8,true);chars(8,"WAVE");chars(12,"fmt ");dv.setUint32(16,16,true);dv.setUint16(20,1,true);dv.setUint16(22,2,true);dv.setUint32(24,rate,true);dv.setUint32(28,rate*4,true);dv.setUint16(32,4,true);dv.setUint16(34,16,true);chars(36,"data");dv.setUint32(40,frames*4,true);
 for(let k=0;k<left.length;k++)for(let j=0;j<framesPerNote;j++){
  const env=Math.min(j,framesPerNote-1-j,160);
  for(let ch=0;ch<2;ch++){
   const f=(ch?right:left)[k],phase=(j*f)%rate;
   const triangle=rate-4*Math.abs(phase-rate/2);
   const s=Math.trunc(triangle*8000*env/(rate*160));
   dv.setInt16(44+4*(k*framesPerNote+j)+2*ch,s,true);
  }
 }
 return bytes;
}

function checksum(bytes){let h=2166136261;for(const b of bytes){h=Math.imul(h^b,16777619)>>>0}return h.toString(16).padStart(8,"0")}

function instruments(){
 // Same raw count debt 2, two different profiles, common witness 0,3,2,1,0.
 // The local interval path sums edge weights; the global potential path is closed.
 // 20 Hz per raw vote-margin unit, reference 400 Hz.
 const cases={
  rotations:{left:[400,440,480,520,560],right:[400,400,400,400,400]},
  unanimous:{left:[400,320,400,480,560],right:[400,280,320,360,400]}
 };
 for(const [name,c] of Object.entries(cases)){
  const bytes=stereoWav(c.left,c.right);
  c.bytes=bytes.length;c.fnv1a32=checksum(bytes);
  if(c.left.at(-1)===c.left[0]||c.right.at(-1)!==c.right[0])throw Error(name+" failed closure check");
  if(c.bytes!==64044)throw Error("WAV size");
 }
 return cases;
}
const result={panels:panelCensus(),instruments:instruments()};
console.log(JSON.stringify(result,null,2));
if(process.argv[2]){
 const fs=require("node:fs"),path=require("node:path");
 fs.mkdirSync(process.argv[2],{recursive:true});
 for(const [name,c] of Object.entries(result.instruments))
  fs.writeFileSync(path.join(process.argv[2],name+".wav"),stereoWav(c.left,c.right));
}
