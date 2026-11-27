'use strict';
const fs=require('node:fs'),os=require('node:os'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const F=require('./fresh-v45.cjs'),A=require('./session-v40.cjs'),J=require('./journal-v42.cjs'),M=require('./multi-v47.cjs'),{wav}=require('./relay.cjs');
const seed=Number(process.env.SEED||71),phase=seed*.013,out=process.argv[2]||'multi-output',root=fs.mkdtempSync(path.join(os.tmpdir(),'mhac47-'));fs.mkdirSync(out,{recursive:true});let checks=0,rescans=0;const rows=[];
const ck=(a,b)=>{assert.deepEqual(a,b);checks++;},throws=(f,re)=>{assert.throws(f,re);checks++;},hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const packet=(source,event,seq,value)=>({kind:0,source,version:1,actor:9,event,seq,tree:[event===7?'verify':'pump-reports',[value]]});
const offers=[{p:packet(1,7,2,'stopped'),g:1},{p:packet(2,8,1,'fault'),g:0},{p:packet(1,7,1,'open'),g:0}];const id=o=>o.p.source+':'+o.g;
const base=offers.map(o=>F.wrap(A.encode(A.ctx(1),64,'data',o.p,o.g,null,0,A.nonce(o.p,o.g),phase)));
const zero=()=>new Int16Array(F.L);
try{for(const name of ['clean','loss','retire-replay'])for(const policy of ['isolated','shared']){
 const dir=path.join(root,name+'-'+policy),w=dir+'.w',qdir=dir+'-q',qw=qdir+'.w';J.provision(dir,w);let r=J.open(dir,w);M.provision(qdir,qw,policy);let d=M.open(qdir,qw);
 const old=[fs.readFileSync(path.join(dir,'state.json')),fs.readFileSync(w)],slots=[],trace=[];
 const rollback=()=>{fs.writeFileSync(path.join(dir,'state.json'),old[0]);fs.writeFileSync(w,old[1]);r=J.open(dir,w);};
 function slot(role,x,o,n,action){const decoded=role==='data'?A.decode(A.ctx(1),64,'data',x.subarray(0,F.BASE)):role==='query'?F.decodeQuery(1,x):F.decodeReply(1,o.p,o.g,n,x,true);const before=d.snapshot(),result=action?action(x):decoded;slots.push(x);trace.push({slot:slots.length-1,role,id:id(o),challenge:n,decoded,result,before,requester:d.snapshot()});return result;}
 for(const [i,o] of offers.entries()){d.register(o.p,o.g);ck(slot('data',base[i],o,0,x=>r.receive('data',x.subarray(0,F.BASE)).decision),'new');}
 const start=slots.length,queue=[],archives=new Map();
 // Bounded centralized half-duplex scheduler: queries first, returns in reverse order.
 function enqueue(o){const n=d.allocate(id(o)),q=d.query(id(o),phase);slot('query',q,o,n);const answer=F.answer(r,q,phase,true);ck(answer.decision,r.snapshot().epochs[0].records.length?'retained-report':'no-exact-retained-record');queue.push({o,n,x:answer.pcm});}
 for(const o of offers)enqueue(o);d=M.open(qdir,qw);ck(d.snapshot().offers.filter(o=>o.pending!==null).length,3);
 while(queue.length){const {o,n,x}=queue.pop();archives.set(id(o),x);const lost=name==='loss'&&id(o)===id(offers[1]);const a=slot('reply',lost?zero():x,o,n,y=>d.receive(y));ck(a.decision,lost?'refused':'consumed');if(!lost)ck(a.id,id(o));}
 if(name==='loss'){const o=offers[1];enqueue(o);const {n,x}=queue.pop();ck(slot('reply',x,o,n,y=>d.receive(y)).id,id(o));}
 if(name==='retire-replay'){
 const o=offers[1],k=id(o);d.retire(k);d=M.open(qdir,qw);d.register(o.p,o.g);rollback();enqueue(o);const {n}=queue.pop(),arch=archives.get(k);const a=slot('reply',arch,o,n,y=>d.receive(y));ck(a.decision,policy==='shared'?'refused':'consumed');if(policy==='shared'){enqueue(o);const {n,x}=queue.pop();ck(slot('reply',x,o,n,y=>d.receive(y)).evidence.kind,'absent');}}
 const s=d.snapshot(),records=r.snapshot().epochs[0].records.length;ck(s.offers.length,3);ck(s.offers.every(o=>o.pending===null),true);ck(s.offers.find(o=>id(o)===id(offers[1])).evidence.status,name==='retire-replay'&&policy==='shared'?'no-exact-retained-record':'applied');ck(records,name==='retire-replay'?0:3);ck(slots.length-start<=10,true);
 const pcm=new Int16Array(slots.length*F.L);slots.forEach((x,i)=>pcm.set(x,i*F.L));const file=`${seed}-${name}-${policy}.wav`,b=wav(pcm);fs.writeFileSync(path.join(out,file),b);const raw=fs.readFileSync(path.join(out,file));for(const t of trace){const x=Int16Array.from({length:F.L},(_,i)=>raw.readInt16LE(44+2*(t.slot*F.L+i))),o=offers.find(o=>id(o)===t.id);const a=t.role==='data'?A.decode(A.ctx(1),64,'data',x.subarray(0,F.BASE)):t.role==='query'?F.decodeQuery(1,x):F.decodeReply(1,o.p,o.g,t.challenge,x,true);ck(a,t.decoded);rescans++;}
 rows.push({name,policy,file,sha256:hash(raw),samples:pcm.length,repairSlots:slots.length-start,records,belief:s.offers,high:s.high,trace});
}
const faults=[];for(const cut of ['before-stage','after-stage','after-witness','after-publish']){const dir=path.join(root,cut),w=dir+'.w';M.provision(dir,w,'shared');let d=M.open(dir,w);for(const o of offers)d.register(o.p,o.g);const a=id(offers[0]),b=id(offers[1]);ck(d.allocate(a),1);throws(()=>d.allocate(b,x=>{if(x===cut)throw Error('cut');}),/cut/);d=M.open(dir,w);const committed=['after-witness','after-publish'].includes(cut);ck(d.snapshot().high,committed?2:1);ck(d.snapshot().offers[0].pending,1);if(!committed)ck(d.allocate(b),2);ck(d.allocate(id(offers[2])),3);faults.push({cut,committed,state:d.snapshot()});}
const dir=path.join(root,'exhaust'),w=dir+'.w';M.provision(dir,w,'shared',1,M.MAX-1);let d=M.open(dir,w);for(const o of offers)d.register(o.p,o.g);ck(d.allocate(id(offers[0])),M.MAX);ck(F.decodeQuery(1,d.query(id(offers[0]),phase)).queryChallenge,M.MAX);throws(()=>d.allocate(id(offers[1])),/exhausted/);throws(()=>d.retire(id(offers[0])),/pending/);ck(d.snapshot().high,M.MAX);fs.unlinkSync(w);throws(()=>M.open(dir,w),/ENOENT/);
fs.writeFileSync(path.join(out,'receipt.json'),JSON.stringify({schema:'mhac-multi-v47',parent:'609c5d940a9f5d143c9696cec0f948cf9bc9dc49',seed,rate:16000,step:F.L,checks,rescans,rows,faults},null,2)+'\n');console.log({seed,checks,rescans,sessions:rows.length,faults:faults.length});}finally{fs.rmSync(root,{recursive:true,force:true});}
