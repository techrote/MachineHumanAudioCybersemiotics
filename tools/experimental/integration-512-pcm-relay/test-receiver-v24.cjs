'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const G=require('./generation-v23.cjs'),{C:P}=require('./lease-v21.cjs'),{wav,frame}=require('./relay.cjs'),{receiver}=require('./receiver-v24.cjs');
const out=process.argv[2]||'receiver-v24-output';fs.mkdirSync(out,{recursive:true});let checks=0;const ck=(x,m)=>{checks++;assert.ok(x,m);};
const {STEP}=G,Q={...P,tree:['quote',['fault']]},other={...P,source:2};
// Logical identity and restart are fixture metadata. Neither is passed to receive().
const cases={duplicate:[[0,P,'A'],[0,P,'A'],[1,P,'B']],stale:[[0,P,'A'],[1,P,'B'],[0,P,'A']],conflict:[[0,P,'A'],[0,Q,'forged']],reorder:[[1,P,'B'],[0,P,'A']],restart:[[0,P,'A'],[1,P,'B'],[0,P,'A','restart']],wrap:[[255,P,'A'],[0,P,'B']],wrapReplay:[[255,P,'A'],[0,P,'old']],sources:[[0,P,'A'],[0,other,'B'],[0,P,'A']],diagnostic:[[0,P,'A','gap'],[0,P,'A']],context:[[0,{...P,version:2},'wrong-context'],[0,P,'A']],jump:[[0,P,'A'],[255,P,'forged'],[1,P,'B']]};
const expected={duplicate:['new','duplicate','new'],stale:['new','new','stale'],conflict:['new','conflict'],reorder:['new','stale'],restart:['new','new','new'],wrap:['new','stale'],wrapReplay:['new','stale'],sources:['new','new','duplicate'],diagnostic:['no-receipt','new'],context:['context-refused','new'],jump:['new','new','stale']};
const rows=[];const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
for(const seed of [71,113]){
 const cache=new Map(),ph=seed*.013;
 function acquire(x,gaps=[]){const k=sha(Buffer.from(x.buffer,x.byteOffset,x.byteLength))+JSON.stringify(gaps);if(!cache.has(k)){const e=G.acquire(x,gaps);ck(JSON.stringify(e)===JSON.stringify(G.acquire(x,gaps,127)),'chunk invariance');cache.set(k,e);}return cache.get(k);}
 for(const [name,offers] of Object.entries(cases))for(const policy of ['baseline','highwater']){
  let r=receiver(policy),segments=[],trace=[],seen=new Set(),metrics={applies:0,duplicateApplies:0,forgedApplies:0,acks:0,matchingAcks:0};
  for(const [g,p,id,fault] of offers){if(fault==='restart')r=receiver(policy);const x=G.envelope(p,g,ph),gaps=fault==='gap'?[1036,2316,3596].map(n=>[64+n,80+n]):[];for(const [l,h] of gaps)x.fill(0,l,h);const e=acquire(x,gaps),d=r.receive(e);segments.push(x);let a=new Int16Array(STEP);if(d.apply){metrics.applies++;metrics.duplicateApplies+=Number(seen.has(id)||id==='old');metrics.forgedApplies+=Number(id==='forged');seen.add(id);}if(d.ack){metrics.acks++;a=G.envelope({...e.packet,kind:1},e.generation,ph);}const ae=acquire(a);segments.push(a);const match=ae.status==='receipt-candidate'&&ae.generation===g&&JSON.stringify(frame(ae.packet))===JSON.stringify(frame({...p,kind:1}));metrics.matchingAcks+=Number(match);ck(match===d.ack,'ACK PCM match');trace.push({g,p,id,fault:fault||null,gaps,decoded:{status:e.status,packet:e.packet,generation:e.generation},decision:d,ack:{status:ae.status,packet:ae.packet,generation:ae.generation},match});}
  if(policy==='highwater')ck(JSON.stringify(trace.map(t=>t.decision.decision))===JSON.stringify(expected[name]),name);
  const pcm=new Int16Array(segments.length*STEP);segments.forEach((x,i)=>pcm.set(x,i*STEP));const b=wav(pcm),file=`${seed}-${name}-${policy}.wav`;fs.writeFileSync(path.join(out,file),b);rows.push({seed,name,policy,metrics,trace,file,samples:pcm.length,sha256:sha(b)});
 }
}
// Abstract workload: no wrap is permitted under the intact namespace contract.
const r=receiver(),ev=g=>({status:'receipt-candidate',packet:P,generation:g});for(let g=0;g<256;g++){ck(r.receive(ev(g)).apply,'fresh sequential');ck(!r.receive(ev(g)).apply,'retry idempotent');}ck(r.receive(ev(0)).decision==='stale','wrap refused');
const tmp=fs.mkdtempSync(path.join(require('node:os').tmpdir(),'mhac-v24-')),ns=path.join(tmp,'ns');const workload=[];try{G.provision(ns);let admitted=0,refused=0;for(let offered=1;offered<=1024;offered++){try{const g=G.allocate(ns);ck(g===admitted,'allocated sequentially');admitted++;}catch(e){if(e.message!=='generation exhausted')throw e;refused++;}if([1,4,16,256,257,1024].includes(offered))workload.push({offered,admitted,refused});}}finally{fs.rmSync(tmp,{recursive:true,force:true});}
for(const seed of [71,113])for(const policy of ['baseline','highwater']){const get=n=>rows.find(r=>r.seed===seed&&r.policy===policy&&r.name===n);ck(get('wrap').sha256===get('wrapReplay').sha256,'indistinguishable wrap/replay PCM');}
const receipt={schema:'mhac-receiver-v24',rate:16000,step:STEP,checks,rows,workload};fs.writeFileSync(path.join(out,'receipt.json'),JSON.stringify(receipt,null,2)+'\n');console.log(JSON.stringify({checks,sessions:rows.length,workload,seed71:rows.filter(x=>x.seed===71).map(({name,policy,metrics})=>({name,policy,...metrics}))},null,2));
