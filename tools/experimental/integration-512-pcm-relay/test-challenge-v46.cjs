'use strict';
const fs=require('node:fs'),os=require('node:os'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const F=require('./fresh-v45.cjs'),A=require('./session-v40.cjs'),J=require('./journal-v42.cjs'),D=require('./challenge-v46.cjs'),{wav}=require('./relay.cjs');
const seed=Number(process.env.SEED||71),phase=seed*.013,out=process.argv[2]||'challenge-output',root=fs.mkdtempSync(path.join(os.tmpdir(),'mhac46-'));fs.mkdirSync(out,{recursive:true});let checks=0,rescans=0;const rows=[];
const ck=(a,b)=>{assert.deepEqual(a,b);checks++;},throws=(f,re)=>{assert.throws(f,re);checks++;},hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const p={kind:0,source:2,version:1,actor:9,event:8,seq:1,tree:['pump-reports',['fault']]},g=0;
const data=A.encode(A.ctx(1),64,'data',p,g,null,0,A.nonce(p,g),phase),zero=()=>new Int16Array(F.L);
const cutAt=k=>x=>{if(x===k)throw Error('cut:'+k);};
try{for(const name of ['reboot-archive','joint-rollback','duplicate','supersede','response-loss','delayed','authorized-lie'])for(const policy of ['volatile','durable']){
 const dir=path.join(root,name+'-'+policy),w=dir+'.w',qdir=dir+'-q',qw=qdir+'.w';J.provision(dir,w);let r=J.open(dir,w);D.provision(qdir,qw,p,g);let d=D.open(qdir,qw),high=0,pending=null,evidence=null;
 const durable=policy==='durable',slots=[],trace=[];const state=()=>durable?d.snapshot():{high,pending,evidence};
 function allocate(){if(durable)return d.allocate();pending=++high;return pending;}
 function reboot(){if(durable)d=D.open(qdir,qw);else{high=0;pending=null;evidence=null;}}
 function query(){return durable?d.query(phase):F.query(1,p,g,pending,phase);}
 function accept(x){if(durable)return d.receive(x);if(pending===null)return {decision:'no-pending-challenge'};const a=F.decodeReply(1,p,g,pending,x,true);if(a.kind==='unknown')return {decision:'refused'};evidence={challenge:pending,kind:a.kind,status:a.status,revision:a.revision??null};pending=null;return {decision:'consumed',evidence};}
 const old=[fs.readFileSync(path.join(dir,'state.json')),fs.readFileSync(w)],qold=[fs.readFileSync(path.join(qdir,'current')),fs.readFileSync(qw)];
 const rollback=()=>{fs.writeFileSync(path.join(dir,'state.json'),old[0]);fs.writeFileSync(w,old[1]);r=J.open(dir,w);};
 function slot(role,x,n,action){const decoded=role==='data'?A.decode(A.ctx(1),64,'data',x.subarray(0,F.BASE)):role==='query'?F.decodeQuery(1,x):F.decodeReply(1,p,g,n,x,true);const result=action?action(x):decoded;slots.push(x);trace.push({slot:slots.length-1,role,n,decoded,result,requester:state()});return result;}
 ck(slot('data',F.wrap(data),0,x=>r.receive('data',x.subarray(0,F.BASE)).decision),'new');let n=allocate(),q=query();slot('query',q,n);const archive=F.answer(r,q,phase,true).pcm;ck(slot('reply',archive,n,accept).decision,'consumed');
 const start=slots.length;let result;
 if(name==='duplicate'){result=slot('reply',archive,n,accept);ck(result.decision,'no-pending-challenge');}
 else{
 if(['reboot-archive','joint-rollback','authorized-lie'].includes(name))rollback();
 if(name==='joint-rollback'){fs.writeFileSync(path.join(qdir,'current'),qold[0]);fs.writeFileSync(qw,qold[1]);}
 if(['reboot-archive','joint-rollback'].includes(name))reboot();
 n=allocate();q=query();slot('query',q,n);const a=F.answer(r,q,phase,true);
 if(name==='supersede'){const oldN=n;n=allocate();q=query();slot('query',q,n);ck(slot('reply',a.pcm,oldN,accept).decision,'refused');result=slot('reply',F.answer(r,q,phase,true).pcm,n,accept);}
 else{let reply=a.pcm;if(['reboot-archive','joint-rollback'].includes(name))reply=archive;if(name==='response-loss')reply=zero();if(name==='delayed')rollback();if(name==='authorized-lie')reply=F.reply(1,p,g,n,{status:'applied',revision:1},phase,true);result=slot('reply',reply,n,accept);if(result.decision==='refused'){n=allocate();q=query();slot('query',q,n);result=slot('reply',F.answer(r,q,phase,true).pcm,n,accept);}}
 }
 const decision=name==='duplicate'?'no-pending-challenge':'consumed';ck(result.decision,decision);const s=state(),expected=name==='reboot-archive'&&durable?'no-exact-retained-record':'applied';ck(s.evidence.status,expected);ck(s.pending,null);const records=r.snapshot().epochs[0].records.length;ck(records,['reboot-archive','joint-rollback','authorized-lie','delayed'].includes(name)?0:1);
 const pcm=new Int16Array(slots.length*F.L);slots.forEach((x,i)=>pcm.set(x,i*F.L));const file=`${seed}-${name}-${policy}.wav`,b=wav(pcm);fs.writeFileSync(path.join(out,file),b);const raw=fs.readFileSync(path.join(out,file));for(const t of trace){const x=Int16Array.from({length:F.L},(_,i)=>raw.readInt16LE(44+2*(t.slot*F.L+i)));const a=t.role==='data'?A.decode(A.ctx(1),64,'data',x.subarray(0,F.BASE)):t.role==='query'?F.decodeQuery(1,x):F.decodeReply(1,p,g,t.n,x,true);ck(a,t.decoded);rescans++;}
 rows.push({name,policy,file,sha256:hash(raw),samples:pcm.length,repairSlots:slots.length-start,decision:result.decision,belief:s.evidence,records,newAdmission:false,trace});
}
const faults=[];for(const operation of ['allocate','consume'])for(const cut of ['before-stage','after-stage','after-witness','after-publish']){const dir=path.join(root,operation+cut),w=dir+'.w';D.provision(dir,w,p,g);let d=D.open(dir,w);if(operation==='consume')d.allocate();const response=F.reply(1,p,g,1,{status:'applied',revision:1},phase,true);throws(()=>operation==='allocate'?d.allocate(cutAt(cut)):d.receive(response,cutAt(cut)),/cut:/);d=D.open(dir,w);const after=cut==='after-witness'||cut==='after-publish',s=d.snapshot();ck(s.high,operation==='allocate'&&!after?0:1);ck(s.pending,operation==='allocate'?(after?1:null):(after?null:1));ck(s.evidence?.status??null,operation==='consume'&&after?'applied':null);if(operation==='allocate'){if(!after)ck(d.allocate(),1);ck(F.decodeQuery(1,d.query(phase)).queryChallenge,1);}else ck(d.receive(response).decision,after?'no-pending-challenge':'consumed');faults.push({operation,cut,after,snapshot:s});}
const dir=path.join(root,'exhaust'),w=dir+'.w';D.provision(dir,w,p,g,1,D.MAX-1);let d=D.open(dir,w);ck(d.allocate(),D.MAX);ck(F.decodeQuery(1,d.query(phase)).queryChallenge,D.MAX);throws(()=>d.allocate(),/exhausted/);ck(d.snapshot().pending,D.MAX);fs.unlinkSync(w);throws(()=>D.open(dir,w),/ENOENT/);
fs.writeFileSync(path.join(out,'receipt.json'),JSON.stringify({schema:'mhac-challenge-v46',parent:'b27dc2329b7841f11664b1db21fd7f8f0454289f',seed,rate:16000,step:F.L,checks,rescans,rows,faults},null,2)+'\n');console.log({seed,checks,rescans,sessions:rows.length,faults:faults.length});}finally{fs.rmSync(root,{recursive:true,force:true});}
