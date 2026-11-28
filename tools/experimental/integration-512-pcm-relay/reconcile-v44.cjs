'use strict';
// Refs #512. Synthetic read-only reconciliation; public fixture keys, no fresh challenge.
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const A=require('./session-v40.cjs'),Q=require('./requester-v43.cjs'),J=require('./journal-v42.cjs'),{wav}=require('./relay.cjs');
const L=Q.L,hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const queryContext=s=>({...A.ctx(s),session:crypto.createHash('sha256').update('MHAC-v44/read-only-query\0').update(A.ctx(s).session).digest().subarray(0,16)});
function query(s,p,g,phase){return A.encode(queryContext(s),64,'data',p,g,null,0,A.nonce(p,g),phase);}
function answer(r,x,phase){const before=r.snapshot(),hits=[];for(const e of before.epochs){const d=A.decode(queryContext(e.session),64,'data',x);if(d.authenticated)hits.push({e,d});}if(hits.length!==1)return {decision:'refused',pcm:null};const {e,d}=hits[0],pcm=r.outcome(e.id,d.packet,d.generation,phase);assert.deepEqual(r.snapshot(),before);return {decision:pcm?'retained-report':'no-retained-report',pcm};}
module.exports={query,answer,queryContext};
if(require.main===module){
 const seed=Number(process.env.SEED||71),phase=seed*.013,out=process.argv[2]||'output',root=fs.mkdtempSync(path.join(os.tmpdir(),'mhac44-'));fs.mkdirSync(out,{recursive:true});let checks=0,rescans=0;const rows=[];
 const ck=(x,y)=>{assert.deepEqual(x,y);checks++;};
 const p={kind:0,source:2,version:1,actor:9,event:8,seq:1,tree:['pump-reports',['fault']]},g=0;
 const data=s=>A.encode(A.ctx(s),64,'data',p,g,null,0,A.nonce(p,g),phase);
 const save=(d,w,f)=>[fs.readFileSync(path.join(d,f)),fs.readFileSync(w)];
 const restore=(d,w,f,b)=>{fs.writeFileSync(path.join(d,f),b[0]);fs.writeFileSync(w,b[1]);};
 try{for(const name of ['clean','requester-rollback','reporter-rollback','asymmetric-rekey','query-loss','replayed-outcome'])for(const policy of ['repeat-data','read-only']){
  const base=path.join(root,name+'-'+policy);fs.mkdirSync(base);const rd=path.join(base,'r'),rw=rd+'.w',qd=path.join(base,'q'),qw=qd+'.w';J.provision(rd,rw);Q.provision(qd,qw,p,g);let r=J.open(rd,rw),q=Q.open(qd,qw);
  const ri=save(rd,rw,'state.json'),qi=save(qd,qw,'current'),trace=[],slots=[];
  function audio(role,session,x,fn){const c=role==='query'?queryContext(session):A.ctx(session),wire=role==='query'?'data':role,d=A.decode(c,64,wire,x,127),result=fn(x);trace.push({role,session,slot:slots.length,decoded:d,result});slots.push(x);return result;}
  ck(audio('data',1,data(1),x=>r.receive('data',x).decision),'new');const old=r.outcome(0,p,g,phase);ck(audio('outcome',1,old,x=>q.receive(x)),'retained');ck(audio('confirm',1,q.confirmation(phase),x=>r.receive('confirm',x).decision),'confirmed');
  // Faults are explicit evaluator actions, never received through PCM.
  if(['requester-rollback','replayed-outcome'].includes(name))restore(qd,qw,'current',qi);
  if(['reporter-rollback','replayed-outcome'].includes(name))restore(rd,rw,'state.json',ri);
  if(name==='asymmetric-rekey')ck(r.transition(0,2),'transitioned');
  r=J.open(rd,rw);q=Q.open(qd,qw);const start=trace.length,before=r.snapshot(),s=before.epochs[0].session;
  let response=null,decision=null,generatedResponse=false;
  for(let attempt=0;attempt<2;attempt++){
   let x=policy==='read-only'?query(1,p,g,phase):data(1);if(name==='query-loss'&&attempt===0)x=new Int16Array(L);
   if(policy==='read-only'){
    decision=audio('query',s,x,z=>{const a=answer(r,z,phase);response=a.pcm;return a.decision;});
   }else{
    decision=audio('data',s,x,z=>{const a=r.receive('data',z);if(['new','duplicate'].includes(a.decision))response=r.outcome(a.epoch,a.decoded.packet,a.decoded.generation,phase);return a.decision;});
   }
   if(response){generatedResponse=true;break;}if(name==='replayed-outcome'){response=old;break;}
  }
  if(response){audio('outcome',1,response,x=>q.receive(x));const c=q.confirmation(phase);if(c)audio('confirm',s,c,x=>r.receive('confirm',x).decision);}
  const final=r.snapshot(),belief=q.snapshot().belief,report=final.epochs[0].reports['2:0']??null,records=final.epochs[0].records.length;
  if(policy==='read-only'){ck(records,before.epochs[0].records.length);ck(A.decode(A.ctx(1),64,'data',query(1,p,g,phase)).authenticated,undefined);ck(A.decode(queryContext(1),64,'data',data(1)).authenticated,undefined);}
  if(name==='asymmetric-rekey'){ck(response,null);ck(final,before);}
  else if(['reporter-rollback','replayed-outcome'].includes(name)&&policy==='read-only'){ck(records,0);ck(report,null);ck(generatedResponse,false);if(name==='replayed-outcome'){ck(belief.outcome,'applied');ck(trace.at(-1).result,'confirmation-refused');}}
  else{ck(records,1);ck(report.confirmed,true);ck(belief.outcome,'applied');ck(generatedResponse,true);}
  const pcm=new Int16Array(L*slots.length);slots.forEach((x,i)=>pcm.set(x,L*i));const raw=wav(pcm),file=seed+"-"+name+"-"+policy+".wav";fs.writeFileSync(path.join(out,file),raw);const b=fs.readFileSync(path.join(out,file));for(const t of trace){const x=Int16Array.from({length:L},(_,i)=>b.readInt16LE(44+2*(t.slot*L+i)));ck(A.decode(t.role==='query'?queryContext(t.session):A.ctx(t.session),64,t.role==='query'?'data':t.role,x,511),t.decoded);rescans++;}
  rows.push({name,policy,file,sha256:hash(b),samples:pcm.length,repairSlots:trace.length-start,decision,generatedResponse,belief,report,records,newAdmission:trace.slice(start).some(t=>t.role==='data'&&t.result==='new'),trace});
 }fs.writeFileSync(path.join(out,'receipt.json'),JSON.stringify({schema:'mhac-reconcile-v44',parent:'60f7f1d08e7bfb4392108bee017723d679b016d9',seed,rate:16000,step:L,checks,rescans,rows},null,2)+'\n');console.log({seed,checks,rescans,sessions:rows.length});}finally{fs.rmSync(root,{recursive:true,force:true});}
}
