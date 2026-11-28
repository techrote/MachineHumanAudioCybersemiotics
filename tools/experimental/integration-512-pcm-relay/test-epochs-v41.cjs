'use strict';
// Refs #512. Native aligned PCM lifecycle experiments, not hardware/security qualification.
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const V=require('./epochs-v41.cjs'),A=require('./session-v40.cjs'),O=require('./outcome-v34.cjs'),{wav}=require('./relay.cjs');
const L=V.L,rate=16000,hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const packet=(source,event,seq,value)=>({kind:0,source,version:1,actor:9,event,seq,tree:[event===7?'verify':'pump-reports',[value]]});
const a=packet(1,7,1,'open'),b=packet(1,7,2,'stopped'),c=packet(2,8,1,'fault'),changed=packet(2,8,1,'open');
const cases=['continuity','namespace','rollback-data','rollback-session','rollback-both','split-write','authorized-lie'];
function run(root,out,name,policy,seed,check){const dir=path.join(root,`${seed}-${name}-${policy}`),file=path.join(dir,'state.json'),w=policy==='anchored'?dir+'.witness':null,phase=seed*.013,trace=[],samples=[],beliefs={};let rescans=0,maxState=0;
 V.provision(dir,w);let r=V.open(dir,w);
 const ck=(x,y,m)=>{check();assert.deepEqual(x,y,m);};
 const capture=()=>{try{const s=r.snapshot();maxState=Math.max(maxState,fs.statSync(file).size);return s;}catch(e){return {blocked:e.message};}};
 const event=(action,fn)=>{let result;try{result=fn();}catch(e){result=e.message;}trace.push({action,result,state:capture(),beliefs:structuredClone(beliefs)});return result;};
 const send=(session,role,p,g,status=null,revision=0)=>{const q={...p,kind:role==='data'?0:1};return A.encode(A.ctx(session),V.BITS,role,q,g,status,revision,A.nonce(q,g),phase);};
 function audio(label,role,x,session,process){const i=samples.length;samples.push(x);const decoded=A.decode(A.ctx(session),V.BITS,role,x);let result;try{result=process(x);}catch(e){result=e.message;}trace.push({action:label,role,session,slot:i,decoded,result,state:capture(),beliefs:structuredClone(beliefs)});return result;}
 const data=(label,session,p,g,x=send(session,'data',p,g))=>audio(label,'data',x,session,x=>r.receive('data',x));
 const confirm=(label,session,p,g,status,rev)=>audio(label,'confirm',send(session,'confirm',p,g,status,rev),session,x=>r.receive('confirm',x));
 const outcome=(label,session,epoch,p,g,x=r.outcome(epoch,p,g,phase))=>audio(label,'outcome',x,session,x=>{const d=A.decode(A.ctx(session),V.BITS,'outcome',x);const k=epoch+':'+p.source+':'+g;beliefs[k]=O.observe(beliefs[k],d,p,g,'outcome');return beliefs[k]??null;});
 const reopen=()=>event('reopen',()=>{r=V.open(dir,w);return 'opened';});
 const rotate=(epoch,session,fresh=false,cut=false)=>event(fresh?'new namespace':'rekey',()=>r.transition(epoch,session,fresh,cut));
 const backup=()=>({state:fs.readFileSync(file),anchor:w&&fs.readFileSync(w)});
 const restore=(s,both=false)=>event(both?'restore both stores':'restore local state',()=>{fs.writeFileSync(file,s.state);if(w&&both)fs.writeFileSync(w,s.anchor);return 'restored';});
 if(name==='continuity'){
  ck(data('B buffered',1,b,1).decision,'new');ck(outcome('B provisional report',1,0,b,1).outcome,'buffered');const old=r.outcome(0,b,1,phase);
  ck(rotate(0,2),'transitioned');ck(reopen(),'opened');ck(data('old B replay',1,b,1).decision,'refused');ck(data('new-session B duplicate',2,b,1).decision,'duplicate');
  ck(data('missing A',2,a,0).decision,'new');ck(r.snapshot().epochs[0].reports['1:1'].status,'applied');ck(reopen(),'opened');
  // The requester is provisioned with new context by the fixture; old report fails under new context.
  ck(outcome('old B report replay',2,0,b,1,old).outcome,'buffered');ck(outcome('B applied report',2,0,b,1).outcome,'applied');ck(confirm('B stale revision confirmation',2,b,1,'applied',1).decision,'confirmation-refused');ck(confirm('B exact confirmation',2,b,1,'applied',2).decision,'confirmed');ck(reopen(),'opened');ck(r.snapshot().epochs[0].reports['1:1'].confirmed,true);
 }else if(name==='namespace'){
  ck(data('namespace 0 event',1,c,0).decision,'new');ck(rotate(0,2),'transitioned');ck(data('rekey same occurrence',2,c,0).decision,'duplicate');ck(data('rekey changed occurrence',2,changed,0).decision,'occurrence-conflict');
  ck(rotate(0,3,true),'transitioned');ck(data('namespace 1 same address new payload',3,changed,0).decision,'new');ck(data('namespace 0 old-session replay',1,c,0).decision,'refused');ck(data('namespace 0 live duplicate',2,c,0).decision,'duplicate');ck(outcome('namespace 0 outstanding report',2,0,c,0).outcome,'applied');ck(confirm('namespace 0 delivery',2,c,0,'applied',1).decision,'confirmed');ck(outcome('namespace 1 report',3,1,changed,0).outcome,'applied');ck(confirm('namespace 1 delivery',3,changed,0,'applied',1).decision,'confirmed');ck(rotate(0,4,true),'namespace-capacity');ck(rotate(0,2),'session-refused');ck(reopen(),'opened');ck(r.snapshot().epochs.map(e=>e.semantic.world.events[0].value),['fault','open']);
 }else if(name==='rollback-data'||name==='rollback-session'||name==='rollback-both'){
  const old=backup();const x=send(1,'data',c,0);ck(data('first event',1,c,0,x).decision,'new');ck(data('exact replay before rollback',1,c,0,x).decision,'duplicate');if(name==='rollback-session'){ck(rotate(0,2),'transitioned');ck(data('retired session replay',1,c,0,x).decision,'refused');}
  restore(old,name==='rollback-both');const blocked=policy==='anchored'&&name!=='rollback-both';ck(reopen(),blocked?'witness-mismatch':'opened');const z=data('exact replay after rollback',1,c,0,x);ck(blocked?z:z.decision,blocked?'witness-mismatch':'new');
 }else if(name==='split-write'){
  ck(data('first event',1,c,0).decision,'new');ck(rotate(0,2,false,true),'injected-between-writes');ck(reopen(),policy==='anchored'?'witness-mismatch':'opened');const z=data('new session data after interrupted rotation',2,c,0);ck(policy==='anchored'?z:z.decision,policy==='anchored'?'witness-mismatch':'duplicate');
 }else if(name==='authorized-lie'){
  ck(data('B buffered',1,b,1).decision,'new');ck(outcome('authorized false applied claim',1,0,b,1,send(1,'outcome',b,1,'applied',2)).outcome,'applied');ck(r.snapshot().epochs[0].reports['1:1'].status,'buffered');ck(confirm('false claim confirmation',1,b,1,'applied',2).decision,'confirmation-refused');ck(data('A later arrives',1,a,0).decision,'new');ck(outcome('genuine applied claim',1,0,b,1).outcome,'applied');
 }
 const pcm=new Int16Array(samples.length*L);samples.forEach((x,i)=>pcm.set(x,i*L));const filename=`${seed}-${name}-${policy}.wav`,raw=wav(pcm);fs.writeFileSync(path.join(out,filename),raw);const raw2=fs.readFileSync(path.join(out,filename));for(const t of trace.filter(t=>t.role)){const x=Int16Array.from({length:L},(_,i)=>raw2.readInt16LE(44+2*(t.slot*L+i)));assert.deepEqual(A.decode(A.ctx(t.session),V.BITS,t.role,x,127),t.decoded);rescans++;}
 return {name,policy,seed,file:filename,sha256:hash(raw2),samples:pcm.length,maxState,rescans,trace,final:capture()};}
function main(out){fs.mkdirSync(out,{recursive:true});const root=fs.mkdtempSync(path.join(os.tmpdir(),'mhac-v41-')),rows=[];let checks=0;try{for(const seed of [Number(process.env.SEED||71)])for(const name of (process.env.CASES||cases.join(',')).split(','))for(const policy of ['local','anchored'])rows.push(run(root,out,name,policy,seed,()=>checks++));fs.writeFileSync(path.join(out,'receipt.json'),JSON.stringify({schema:'mhac-epochs-v41',parent:'32eca4f1e1fe16d53422971c7663ae7fd73cca34',rate,step:L,checks,rescans:rows.reduce((a,r)=>a+r.rescans,0),rows},null,2)+'\n');console.log({checks,rescans:rows.reduce((a,r)=>a+r.rescans,0),sessions:rows.length});}finally{fs.rmSync(root,{recursive:true,force:true});}}
if(require.main===module)main(process.argv[2]||'epochs-v41-output');
