'use strict';
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),assert=require('node:assert/strict'),crypto=require('node:crypto'),{spawnSync}=require('node:child_process');
const Q=require('./requester-v43.cjs'),J=require('./journal-v42.cjs'),A=require('./session-v40.cjs'),{wav}=require('./relay.cjs');
const L=Q.L,p={kind:0,source:2,version:1,actor:9,event:8,seq:1,tree:['pump-reports',['fault']]},b={kind:0,source:1,version:1,actor:9,event:7,seq:2,tree:['verify',['stopped']]};
const pcm=f=>{const x=fs.readFileSync(f);return Int16Array.from({length:x.length/2},(_,i)=>x.readInt16LE(2*i));};
const encode=(p,g,role,s,v,phase)=>{const q={...p,kind:role==='data'?0:1};return A.encode(A.ctx(1),64,role,q,g,s,v,A.nonce(q,g),phase);};
if(process.argv[2]==='child'){
 const [dir,w,input,cut,output,phase]=process.argv.slice(3),x=pcm(input);let c;
 if(cut==='volatile'){const d=A.decode(A.ctx(1),64,'outcome',x);assert.equal(d.authenticated,true);c=encode(p,0,'confirm',d.outcome,d.revision,+phase);}
 else{const q=Q.open(dir,w);q.receive(x,k=>{if(k===cut)process.kill(process.pid,'SIGKILL');});c=q.confirmation(+phase);}
 if(c)fs.writeFileSync(output,Buffer.from(c.buffer));process.kill(process.pid,'SIGKILL');
}else{
 const seed=Number(process.env.SEED||71),phase=seed*.013,out=process.argv[2]||'output',root=fs.mkdtempSync(path.join(os.tmpdir(),'mhac43-'));fs.mkdirSync(out,{recursive:true});let checks=0,rescans=0;const rows=[];
 const ck=(x,y)=>{assert.deepEqual(x,y);checks++;};
 try{for(const name of ['volatile','durable','before-stage','after-stage','after-witness','after-publish','rollback-local','rollback-both','authorized-lie','wrong-offer','witness-unavailable']){
  const base=path.join(root,name);fs.mkdirSync(base);const rd=path.join(base,'reporter'),rw=rd+'.witness',qd=path.join(base,'requester'),qw=qd+'.witness',input=path.join(base,'input'),output=path.join(base,'confirm'),target=name==='authorized-lie'?b:p,g=target===b?1:0,trace=[],slots=[];
  J.provision(rd,rw);Q.provision(qd,qw,target,g);const r=J.open(rd,rw);let q=Q.open(qd,qw);const initial=fs.readFileSync(path.join(qd,'current')),initialW=fs.readFileSync(qw);
  function audio(role,x,fn){const d=A.decode(A.ctx(1),64,role,x,127);let result;try{result=fn(x);}catch(e){result=e.message;}trace.push({role,slot:slots.length,decoded:d,result});slots.push(x);return result;}
  ck(audio('data',encode(target,g,'data',null,0,phase),x=>r.receive('data',x).decision),'new');const report=r.outcome(0,target,g,phase);let emitted=false,recovered=null;
  if(name==='authorized-lie'||name==='wrong-offer'){
   const x=name==='authorized-lie'?encode(b,1,'outcome','applied',2,phase):encode({...p,tree:['pump-reports',['open']]},0,'outcome','applied',1,phase);
   ck(audio('outcome',x,x=>q.receive(x)),name==='authorized-lie'?'retained':'refused');const c=q.confirmation(phase);if(name==='authorized-lie'){ck(audio('confirm',c,x=>r.receive('confirm',x).decision),'confirmation-refused');ck(q.snapshot().belief.outcome,'applied');ck(r.snapshot().epochs[0].reports['1:1'].status,'buffered');}else ck(c,null);
  }else if(name.startsWith('rollback')||name==='witness-unavailable'){
   ck(audio('outcome',report,x=>q.receive(x)),'retained');const c=q.confirmation(phase);ck(audio('confirm',c,x=>r.receive('confirm',x).decision),'confirmed');fs.writeFileSync(path.join(qd,'current'),initial);
   if(name==='rollback-both')fs.writeFileSync(qw,initialW);if(name==='witness-unavailable')fs.unlinkSync(qw);
   try{q=Q.open(qd,qw);recovered=q.snapshot().belief;}catch(e){recovered=e.code||e.message;q=null;}ck(recovered,name==='rollback-local'?{outcome:'applied',revision:1}:name==='rollback-both'?null:'ENOENT');
  }else{
   fs.writeFileSync(input,Buffer.from(report.buffer));const child=audio('outcome',report,()=>{const c=spawnSync(process.execPath,[__filename,'child',qd,qw,input,name,output,String(phase)],{encoding:'utf8',timeout:15000});if(c.signal!=='SIGKILL')throw Error(JSON.stringify(c));return c.signal;});ck(child,'SIGKILL');
   emitted=fs.existsSync(output);ck(emitted,['volatile','durable'].includes(name));if(emitted)ck(audio('confirm',pcm(output),x=>r.receive('confirm',x).decision),'confirmed');q=Q.open(qd,qw);recovered=q.snapshot().belief;ck(recovered,['volatile','before-stage','after-stage'].includes(name)?null:{outcome:'applied',revision:1});
   if(name!=='volatile'&&!emitted){if(!recovered)ck(audio('outcome',report,x=>q.receive(x)),'retained');ck(audio('confirm',q.confirmation(phase),x=>r.receive('confirm',x).decision),'confirmed');}
  }
  const final=q?q.snapshot():null,reporter=r.snapshot(),x=new Int16Array(L*slots.length);slots.forEach((s,i)=>x.set(s,i*L));const file=`${seed}-${name}.wav`,raw=wav(x);fs.writeFileSync(path.join(out,file),raw);const saved=fs.readFileSync(path.join(out,file));for(const t of trace){const s=Int16Array.from({length:L},(_,i)=>saved.readInt16LE(44+2*(t.slot*L+i)));ck(A.decode(A.ctx(1),64,t.role,s,511),t.decoded);rescans++;}rows.push({name,file,sha256:crypto.createHash('sha256').update(saved).digest('hex'),samples:x.length,trace,emitted,recovered,final,reporter});
 }fs.writeFileSync(path.join(out,'receipt.json'),JSON.stringify({schema:'mhac-requester-v43',parent:'3637529f313949d31e55d66d04bb119547c1e29a',seed,rate:16000,step:L,checks,rescans,rows},null,2)+'\n');console.log({seed,checks,rescans,sessions:rows.length});}finally{fs.rmSync(root,{recursive:true,force:true});}
}
