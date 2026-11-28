'use strict';
// Refs #512. Independent replay of exported critical slots with provisioned context.
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const F=require('./fresh-v45.cjs'),M=require('./status-v49.cjs'),{wav}=require('./relay.cjs');
const q={kind:0,source:2,version:1,actor:9,event:8,seq:1,tree:['pump-reports',['fault']]};
const root=process.argv[2]||'.',hash=b=>crypto.createHash('sha256').update(b).digest('hex');let checks=0,rescans=0;
function ck(a,b){assert.deepEqual(a,b);checks++;}
const expected={clear:[5,5,5],deferred:[10,7,7],delayed:[10,10,8],latejam:[9,9,9],hidden:[10,7,7]},results=[];
for(const seed of [71,113])for(const [scenario,slots] of Object.entries(expected)){
 const folder=path.join(root,`${seed}-${scenario}`),receipt=JSON.parse(fs.readFileSync(path.join(folder,'receipt.json')));
 ck(receipt.rows.map(r=>r.urgent),slots);ck(receipt.rows.map(r=>r.policy),['eager','commit','journal']);
 for(const row of receipt.rows){const bytes=fs.readFileSync(path.join(folder,row.file));ck(hash(bytes),row.sha256);ck(bytes.length,44+2*receipt.H*receipt.L);ck(row.records,1);ck(row.transition,2);ck(row.deadline,true);
  for(const t of row.trace){const pcm=Int16Array.from({length:receipt.L},(_,k)=>bytes.readInt16LE(44+2*((t.slot-1)*receipt.L+k)));ck(hash(wav(pcm)),t.sha256);
   for(const e of t.received.filter(e=>e.i===2&&['ignored-valid-report','consumed'].includes(e.result))){ck(t.before.pending!==null,true);const decoded=F.decodeReply(10,q,0,t.before.pending,pcm.subarray(e.start,e.start+F.L),true);ck(decoded.kind,'report');ck(decoded.status,'applied');ck(t.after.pending,e.result==='consumed'?null:t.before.pending);rescans++;results.push({seed,scenario,policy:row.policy,slot:t.slot,challenge:t.before.pending,result:e.result});}
  }
 }
}
// A scheduling state must not override the actual journal's one-shot binding.
const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'mhac54-controls-'));
try{const dir=path.join(tmp,'requester'),w=dir+'.w';M.provision(dir,w,'shared',10,0);let d=M.open(dir,w),id=d.register(q,0),n=d.allocate(id);const old=F.reply(10,q,0,n,{status:'applied',revision:1},.923,true);ck(n,1);ck(d.allocate(id),2);d=M.open(dir,w);ck(d.receive(old).decision,'refused');ck(d.snapshot().offers[0].pending,2);const fresh=F.reply(10,q,0,2,{status:'applied',revision:1},.923,true);ck(d.receive(fresh).decision,'consumed');d=M.open(dir,w);ck(d.receive(fresh).decision,'refused');ck(d.snapshot().offers[0].pending,null);}finally{fs.rmSync(tmp,{recursive:true,force:true});}
const out={checks,rescans,results,controls:'superseded and consumed response refused after reopening'};fs.writeFileSync(path.join(root,'verification-v54.json'),JSON.stringify(out,null,2)+'\n');console.log({checks,rescans});
