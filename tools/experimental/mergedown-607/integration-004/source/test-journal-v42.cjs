'use strict';
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const J=require('./journal-v42.cjs'),V=require('./epochs-v41.cjs'),A=require('./session-v40.cjs'),{wav}=require('./relay.cjs');
const L=V.L,seed=Number(process.env.SEED||71),out=process.argv[2]||'output',root=fs.mkdtempSync(path.join(os.tmpdir(),'mhac42-'));fs.mkdirSync(out,{recursive:true});let checks=0,rescans=0;const rows=[];
const p={kind:0,source:2,version:1,actor:9,event:8,seq:1,tree:['pump-reports',['fault']]};
const send=(s,role,status=null,rev=0)=>{const q={...p,kind:role==='data'?0:1};return A.encode(A.ctx(s),64,role,q,0,status,rev,A.nonce(q,0),seed*.013);};
const ck=(a,b)=>{assert.deepEqual(a,b);checks++;};
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
function run(name,policy){const dir=path.join(root,name+'-'+policy),w=dir+'.witness',f=path.join(dir,'state.json'),stage=path.join(dir,'stage','state.json'),M=policy==='journal'?J:V;M.provision(dir,w);let r=M.open(dir,w);const trace=[],slots=[];
 const snapshot=()=>{try{return r.snapshot();}catch(e){return {blocked:e.message};}};
 function event(label,fn){let result;try{result=fn();}catch(e){result=e.message;}trace.push({label,result,local:JSON.parse(fs.readFileSync(f)).s,witness:JSON.parse(fs.readFileSync(w))});return result;}
 function audio(label,session,role,x,fn){const decoded=A.decode(A.ctx(session),64,role,x,127);ck(decoded.authenticated,true);const result=event(label,()=>fn(x));Object.assign(trace.at(-1),{session,role,slot:slots.length,decoded});slots.push(x);return result;}
 const data=(s,cut)=>audio('DATA',s,'data',send(s,'data'),x=>r.receive('data',x, ...(policy==='journal'?[cut]:[])).decision);
 const reopen=()=>event('reopen',()=>{r=M.open(dir,w);return r.initial||'current';});
 const first=fs.readFileSync(f),anchor0=fs.readFileSync(w);
 if(name==='rekey-cut'){
  ck(data(1),'new');ck(event('interrupted rekey',()=>policy==='journal'?r.transition(0,2,false,'after-witness'):r.transition(0,2,false,true)),policy==='journal'?'cut:after-witness':'injected-between-writes');ck(reopen(),policy==='journal'?'candidate':'witness-mismatch');ck(data(2),policy==='journal'?'duplicate':'witness-mismatch');
 }else if(name.startsWith('data-')){
  const cut=name.slice(5),committed=['after-witness','after-publish'].includes(cut);ck(data(1,cut),'cut:'+cut);ck(reopen(),cut==='after-witness'?'candidate':'current');ck(data(1),committed?'duplicate':'new');ck(r.snapshot().epochs[0].semantic.world.events.length,1);ck(r.snapshot().commit,1);
 }else if(name==='missing-candidate'||name==='stale-candidate'||name==='tampered-candidate'){
  // Do not call snapshot between the fault and corruption: recovery itself publishes the candidate.
  ck(data(1,'after-witness'),'cut:after-witness');
  if(name==='missing-candidate')fs.unlinkSync(stage);else if(name==='stale-candidate')fs.writeFileSync(stage,first);else{const b=fs.readFileSync(stage);b[b.length-2]^=1;fs.writeFileSync(stage,b);}
  ck(reopen(),'no-witness-matching-state');ck(data(1),'no-witness-matching-state');
 }else if(name==='rollback-local'||name==='rollback-both'||name==='rollback-local-recover'){
  ck(data(1),'new');fs.writeFileSync(f,first);if(name==='rollback-both')fs.writeFileSync(w,anchor0);else if(name==='rollback-local')fs.unlinkSync(stage);ck(reopen(),name==='rollback-both'?'current':name==='rollback-local-recover'?'candidate':'no-witness-matching-state');ck(data(1),name==='rollback-both'?'new':name==='rollback-local-recover'?'duplicate':'no-witness-matching-state');
 }else if(name==='confirm-cut'||name==='confirm-uncommitted'){
  ck(data(1),'new');const x=r.outcome(0,p,0,seed*.013);const d=audio('OUTCOME',1,'outcome',x,x=>A.decode(A.ctx(1),64,'outcome',x));ck(d.outcome,'applied');const k=send(1,'confirm','applied',1);const cut=name==='confirm-cut'?'after-witness':'after-stage';ck(audio('CONFIRM interrupted',1,'confirm',k,x=>r.receive('confirm',x,cut).decision),'cut:'+cut);ck(reopen(),name==='confirm-cut'?'candidate':'current');ck(r.snapshot().epochs[0].reports['2:0'].confirmed,name==='confirm-cut');ck(audio('CONFIRM replay',1,'confirm',k,x=>r.receive('confirm',x).decision),name==='confirm-cut'?'duplicate-confirmation':'confirmed');ck(r.snapshot().epochs[0].reports['2:0'].confirmed,true);ck(r.snapshot().commit,2);
 }
 const pcm=new Int16Array(slots.length*L);slots.forEach((x,i)=>pcm.set(x,i*L));const file=seed+'-'+name+'-'+policy+'.wav',b=wav(pcm);fs.writeFileSync(path.join(out,file),b);const raw=fs.readFileSync(path.join(out,file));for(const t of trace.filter(t=>t.role)){const x=Int16Array.from({length:L},(_,i)=>raw.readInt16LE(44+2*(t.slot*L+i)));ck(A.decode(A.ctx(t.session),64,t.role,x,511),t.decoded);rescans++;}rows.push({name,policy,file,sha256:hash(raw),samples:pcm.length,trace,final:snapshot()});}
try{run('rekey-cut','baseline');for(const name of ['rekey-cut','data-before-stage','data-after-stage','data-after-witness','data-after-publish','missing-candidate','stale-candidate','tampered-candidate','rollback-local','rollback-local-recover','rollback-both','confirm-cut','confirm-uncommitted'])run(name,'journal');fs.writeFileSync(path.join(out,'receipt.json'),JSON.stringify({schema:'mhac-journal-v42',parent:'198bf5ad72801cf2969a6bd432c88af0aa9a52fb',seed,rate:16000,step:L,checks,rescans,rows},null,2)+'\n');console.log({seed,checks,rescans,sessions:rows.length});}finally{fs.rmSync(root,{recursive:true,force:true});}
