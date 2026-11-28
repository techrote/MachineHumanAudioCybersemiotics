'use strict';
// Independently rescan response windows from filesystem WAV bytes, using prior persistent challenge contexts.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),F=require('./fresh-v45.cjs');
let checks=0,windows=0;const ck=(a,b)=>{assert.deepEqual(a,b);checks++;};
const offer=(source,g,value)=>({g,p:{kind:0,source,version:1,actor:9,event:8,seq:g+1,tree:['pump-reports',[value]]}});
const offers=[offer(1,0,'open'),offer(2,0,'fault'),offer(1,1,'stopped')];
for(const dir of process.argv.slice(2)){const r=JSON.parse(fs.readFileSync(path.join(dir,'receipt.json')));for(const row of r.rows){const b=fs.readFileSync(path.join(dir,row.file));const read=(t,start)=>Int16Array.from({length:F.L},(_,k)=>b.readInt16LE(44+2*(t*r.L+start+k)));for(let t=1;t<r.H;t++){const x=row.trace[t],prev=row.trace[t-1];if(x.role==='REPLY'){const pcm=read(t,r.G),hits=[];for(let i=0;i<offers.length;i++){const o=offers[i],n=prev.pending[i].challenge;if(n===null)continue;const z=F.decodeReply(1,o.p,o.g,n,pcm,true);if(z.kind!=='unknown')hits.push(z);windows++;}ck(hits.length===1?'consumed':'refused',x.decision);}if(x.recv?.length){for(const e of x.recv){const o=offers[e.endpoint],n=prev.pending[e.endpoint];const z=n===null?{kind:'unknown'}:F.decodeReply(e.endpoint+1,o.p,o.g,n,read(t,e.start),true);ck(z.kind==='unknown'?'refused':'consumed',e.decision);windows++;}}}}}
console.log(JSON.stringify({checks,windows}));
