'use strict';
// Synthetic artistic apparatus; no participant data.
function laboratory(){
 const supports=[3,5,9,6,10,12], cls=s=>Math.min(s,15^s);
 const crossing=(a,b)=>!!(a&b)&&!!(a&(~b)&15)&&!!(b&(~a)&15);
 const rows=cols=>Array.from({length:4},(_,i)=>cols.map(s=>(s>>i)&1));
 const four=(rr,i,j)=>new Set(rr.map(a=>2*a[i]+a[j])).size===4;
 let configs=0, checks=0, max=0, histogram={}, repairHistogram={}, balancedRows=0;
 function check(x){checks++;if(!x)throw Error("assertion "+checks)}
 for(let code=0;code<6**6;code++){
  let k=code;const cols=Array.from({length:6},()=>{let s=supports[k%6];k=Math.floor(k/6);return s});
  const rr=rows(cols), counts=[3,5,6].map(c=>cols.filter(s=>cls(s)===c).length);
  let pairs=0;for(let i=0;i<6;i++)for(let j=i+1;j<6;j++){
   const c=crossing(cols[i],cols[j]);check(c===four(rr,i,j));if(c)pairs++;
  }
  check(pairs===counts[0]*counts[1]+counts[0]*counts[2]+counts[1]*counts[2]);
  let keep=0;
  for(let mask=0;mask<64;mask++){
   const selected=cols.filter((_,i)=>mask&(1<<i));
   if(selected.every((a,i)=>selected.slice(i+1).every(b=>!crossing(a,b))))keep=Math.max(keep,selected.length);
  }
  check(keep===Math.max(...counts));
  check(pairs<=12); max=Math.max(max,pairs);
  histogram[pairs]=(histogram[pairs]||0)+1;
  repairHistogram[6-keep]=(repairHistogram[6-keep]||0)+1;
  if(rr.every(a=>a.reduce((x,y)=>x+y,0)===3))balancedRows++;
  configs++;
 }
 const nested=[3,3,3,12,12,12], crossed=[3,5,9,12,10,6];
 for(const cols of [nested,crossed]){
  check(rows(cols).every(a=>a.reduce((x,y)=>x+y,0)===3));
  check(cols.every(s=>rows([s]).flat().reduce((x,y)=>x+y,0)===2));
 }
 const rate=16000, slot=4000, base=[0,4,7,2,5,0];
 const voice=(j,v)=>Array.from({length:slot},(_,i)=>{
  const t=i/rate, f=220*2**((base[j]+v*2)/12), env=Math.sin(Math.PI*i/(slot-1))**2;
  return Math.round(1800*env*(Math.sin(2*Math.PI*f*t)+0.2*Math.sin(4*Math.PI*f*t)));
 });
 const tones=base.map((_,j)=>[voice(j,0),voice(j,1)]);
 const render=cols=>rows(cols).map(row=>row.flatMap((v,j)=>tones[j][v]));
 const mix=stems=>stems[0].map((_,i)=>stems.reduce((s,a)=>s+a[i],0));
 const a=render(nested),b=render(crossed), am=mix(a),bm=mix(b);
 check(am.every((v,i)=>v===bm[i]));check(a.some((s,j)=>s.some((v,i)=>v!==b[j][i])));
 check([...am,...bm].every(v=>Number.isInteger(v)&&Math.abs(v)<=32767));
 check(max===12);check(histogram[0]===192); // 3 split classes, two orientations at six positions
 return {summary:{configs,checks,max,histogram,repairHistogram,balancedRows,frames:am.length,rate},audio:{nested:a,crossed:b,mix:am}};
}
const result = laboratory();
console.log(JSON.stringify(result.summary,null,2));
if(process.argv.includes('--wav')) {
 const fs=require('node:fs'); const dir='choir-audio'; fs.mkdirSync(dir,{recursive:true});
 function wav(name, samples) {const b=Buffer.alloc(44+samples.length*2);b.write('RIFF');b.writeUInt32LE(b.length-8,4);b.write('WAVEfmt ',8);b.writeUInt32LE(16,16);b.writeUInt16LE(1,20);b.writeUInt16LE(1,22);b.writeUInt32LE(result.summary.rate,24);b.writeUInt32LE(result.summary.rate*2,28);b.writeUInt16LE(2,32);b.writeUInt16LE(16,34);b.write('data',36);b.writeUInt32LE(samples.length*2,40);samples.forEach((v,i)=>b.writeInt16LE(v,44+i*2));fs.writeFileSync(dir+'/'+name+'.wav',b);if(!fs.readFileSync(dir+'/'+name+'.wav').equals(b))throw Error('readback');}
 for(const name of ['nested','crossed']) result.audio[name].forEach((s,i)=>wav(name+'-'+(i+1),s));wav('invariant-mix',result.audio.mix);
}
