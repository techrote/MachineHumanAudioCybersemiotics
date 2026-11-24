'use strict';
// Synthetic mathematical experiment; no perceptual or semantic validation.
const abs=x=>x<0n?-x:x;
function gcd(a,b){a=abs(a);b=abs(b);while(b){[a,b]=[b,a%b]}return a}
const lcm=(a,b)=>abs(a/gcd(a,b)*b);
const sum=a=>a.reduce((s,x)=>s+x,0n);
function fraction(n,d){if(d<=0n)throw Error('bad denominator');const g=gcd(n,d);return [n/g,d/g]}
const str=([n,d])=>n+'/'+d;
const num=([n,d])=>Number(n)/Number(d);
const le=(a,b)=>a[0]*b[1]<=b[0]*a[1];
const eq=(a,b)=>le(a,b)&&le(b,a);
function check(x,msg){if(!x)throw Error(msg)}
function choose(n,k){if(k<0||k>n)return 0n;let c=1n;for(let i=1;i<=k;i++)c=c*BigInt(n-i+1)/BigInt(i);return c}
function* subsets(a,k,i=0,p=[]){if(!k){yield p;return}for(let j=i;j<=a.length-k;j++)yield* subsets(a,k-1,j+1,[...p,a[j]])}
function witness(xs,h=xs.map(x=>x>0?1:0)){
  check(xs.length>=2&&new Set(xs).size===xs.length,'distinct nodes');
  const x=xs.map(BigInt);
  const d=x.map((v,i)=>x.reduce((p,z,j)=>i===j?p:p*(v-z),1n));
  const L=d.reduce((p,v)=>lcm(p,v),1n);
  let w=d.map(v=>L/v);
  const g=w.reduce(gcd,0n);w=w.map(v=>v/g);
  const positive=sum(w.filter(v=>v>0n));
  check(positive===-sum(w.filter(v=>v<0n)),'total mass');
  for(let j=0;j<=x.length-2;j++)
    check(sum(w.map((v,i)=>v*x[i]**BigInt(j)))===0n,'matched moment');
  check(sum(w.map((v,i)=>v*x[i]**BigInt(x.length-1)))!==0n,'next moment negative control');
  const a=sum(w.map((v,i)=>v>0n?v*BigInt(h[i]):0n));
  const b=-sum(w.map((v,i)=>v<0n?v*BigInt(h[i]):0n));
  return {w,positive,a:fraction(a,positive),b:fraction(b,positive),gap:fraction(abs(a-b),positive)};
}
function optimum(grid,k){
  let best=[0n,1n], nodes=null, count=0;
  if(k>=grid.length-1)return {best,nodes,count};
  for(const xs of subsets(grid,k+2)){
    const q=witness(xs).gap;count++;
    if(!le(q,best)){best=q;nodes=xs}
  }
  check(BigInt(count)===choose(grid.length,k+2),'subset count');
  return {best,nodes,count};
}
// Upper bound from expectation of an odd-degree binomial majority polynomial.
function majorityBound(k,g,R){
  const m=k%2?k:k-1;
  if(m<1)return [1n,1n];
  const a=BigInt(R+g),b=BigInt(R-g),d=BigInt(2*R)**BigInt(m);
  let e=0n;
  for(let j=0;j<=(m-1)/2;j++)e+=choose(m,j)*a**BigInt(j)*b**BigInt(m-j);
  return 2n*e>=d?[1n,1n]:fraction(2n*e,d);
}
function pcm(xs,w,side,filtered=false){
  // xs are signed offsets in Hz, threshold = 1000 Hz. One full second.
  const fs=8000, scale=0.55/Math.sqrt(xs.length), n=fs;
  const a=w.w.map((v,i)=>Math.sign(Number(v))===side&&(!filtered||xs[i]>0)?
    scale*Math.sqrt(Number(abs(v))/Number(w.positive)):0);
  const data=new Uint8Array(44+2*n), d=new DataView(data.buffer);
  const chars=(o,s)=>{for(let i=0;i<s.length;i++)data[o+i]=s.charCodeAt(i)};
  chars(0,'RIFF');d.setUint32(4,data.length-8,true);chars(8,'WAVE');chars(12,'fmt ');
  d.setUint32(16,16,true);d.setUint16(20,1,true);d.setUint16(22,1,true);
  d.setUint32(24,fs,true);d.setUint32(28,2*fs,true);d.setUint16(32,2,true);d.setUint16(34,16,true);
  chars(36,'data');d.setUint32(40,2*n,true);
  let energy=0,max=0;
  for(let j=0;j<n;j++){
    const s=a.reduce((t,v,i)=>t+v*Math.sin(2*Math.PI*(1000+xs[i])*j/fs),0);
    const q=Math.round(s*32767);check(abs(BigInt(q))<32767n,'no clipping');
    d.setInt16(44+2*j,q,true);energy+=q*q;max=Math.max(max,Math.abs(q));
  }
  let hash=2166136261;
  for(const v of data)hash=Math.imul(hash^v,16777619)>>>0;
  return {data,summary:{bytes:data.length,fnv1a:hash.toString(16).padStart(8,'0'),integer_energy:energy,peak:max}};
}
function run(){
  let subsetChecks=0;
  const grids=[];
  for(const g of [1,2,3,4,5,6,7,8]){
    const grid=Array.from({length:17},(_,i)=>i-8).filter(x=>Math.abs(x)>=g);
    const rows=[];
    for(let k=0;k<=Math.min(8,grid.length);k++){
      const a=optimum(grid,k);subsetChecks+=a.count;
      check(le(a.best,[1n,1n]),'probability range');
      check(le(a.best,majorityBound(k,g,8)),'majority certificate');
      if(k===1||k===2)check(eq(a.best,fraction(BigInt(8-g),BigInt(8+g))),'sharp first/second moment');
      if(k>=1)check(le(a.best,rows[k-1].raw),'monotonicity');
      if(k>=2&&k%2===0)check(eq(a.best,rows[k-1].raw),'even degree plateau');
      rows.push({k,raw:a.best,gap:str(a.best),decimal:num(a.best),nodes:a.nodes,count:a.count,majority:str(majorityBound(k,g,8))});
    }
    grids.push({g,grid,rows:rows.map(({raw,...r})=>r)});
  }
  const uniform=[];
  for(let k=0;k<=20;k++){
    const x=Array.from({length:k+2},(_,i)=>i);
    for(let j=1;j<x.length;j++){
      const w=witness(x,x.map(t=>t>=j?1:0));
      check(eq(w.gap,fraction(choose(k,j-1),2n**BigInt(k))),'uniform partial binomial');
    }
    uniform.push({k,max:str(fraction(choose(k,Math.floor(k/2)),2n**BigInt(k)))});
  }
  const close=[];
  for(let k=0;k<=12;k++){
    let prev=[0n,1n];
    for(const M of [10,100,1000,10000]){
      const x=[-1,1,...Array.from({length:k},(_,i)=>(i+1)*M)].sort((a,b)=>a-b);
      const w=witness(x);
      check(le(prev,w.gap),'convergence in chosen family');prev=w.gap;
      close.push({k,M,gap:str(w.gap),decimal:num(w.gap)});
    }
  }
  const audio={}, audioData={};
  for(const [tag,x] of [['near',[-800,-400,-1,1,400,800]],['wide',[-800,-400,-100,100,400,800]]]){
    const w=witness(x);
    const details={offsets:x,weights:w.w.map(String),normalizer:String(w.positive),bandA:str(w.a),bandB:str(w.b),gap:str(w.gap),files:{}};
    for(const [side,name] of [[1,'A'],[-1,'B']])for(const filtered of [false,true]){
      const key=tag+'-'+name+(filtered?'-above':'')+'.wav';
      const p=pcm(x,w,side,filtered);
      details.files[key]=p.summary;audioData[key]=p.data;
    }
    const f=details.files;
    check(Math.abs(f[tag+'-A.wav'].integer_energy/f[tag+'-B.wav'].integer_energy-1)<0.001,'PCM equal energy tolerance');
    audio[tag]=details;
  }
  return {receipt:{subsetChecks,grids,uniform,close,audio},audioData};
}
module.exports={run,witness,optimum};
if(require.main===module){
  const fs=require('node:fs'),path=require('node:path'),out=process.argv[2]||'moment-output';
  fs.mkdirSync(out,{recursive:true});
  const {receipt,audioData}=run();
  fs.writeFileSync(path.join(out,'execution.json'),JSON.stringify(receipt,null,2)+'\n');
  for(const [name,data] of Object.entries(audioData))fs.writeFileSync(path.join(out,name),data);
  console.log('Completed '+receipt.subsetChecks+' exact subset checks.');
}
