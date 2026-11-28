'use strict';
// Refs #607: independent bounded native witness-state audit; not a crash simulation.
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const J=require('./source/journal-v42.cjs'),A=require('./source/session-v40.cjs');
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const p={kind:0,source:2,version:1,actor:9,event:8,seq:1,tree:['pump-reports',['fault']]};
const results=[];
for(const seed of [71,113]){
 const pcm=A.encode(A.ctx(1),64,'data',p,0,null,0,A.nonce(p,0),seed*.013);
 const root=fs.mkdtempSync(path.join(os.tmpdir(),'mhac-independent-'));
 try{
  function scenario(name,fn){const dir=path.join(root,name),w=dir+'.witness',f=path.join(dir,'state.json'),stage=path.join(dir,'stage','state.json');J.provision(dir,w); const first=fs.readFileSync(f),anchor=fs.readFileSync(w);const read=()=>JSON.parse(fs.readFileSync(f)).s; const seal=()=>JSON.parse(fs.readFileSync(w)); const exact=()=>{const b=fs.readFileSync(f);assert.equal(seal().sha256,hash(b));assert.equal(seal().commit,read().commit);};const row=fn({dir,w,f,stage,first,anchor,read,seal,exact});results.push({seed,name,...row});}
  for(const cut of ['before-stage','after-stage','after-witness','after-publish'])scenario(cut,({dir,w,f,stage,read,seal,exact})=>{
   assert.throws(()=>J.open(dir,w).receive('data',pcm,cut),new RegExp('cut:'+cut));
   const committed=['after-witness','after-publish'].includes(cut), before={local:read().commit,witness:seal().commit,stage:fs.existsSync(stage)?JSON.parse(fs.readFileSync(stage)).s.commit:null};
   assert.equal(before.local,cut==='after-publish'?1:0);assert.equal(before.witness,committed?1:0);assert.equal(before.stage,cut==='before-stage'?null:1);
   const r=J.open(dir,w);assert.equal(r.initial,cut==='after-witness'?'candidate':'current');exact();assert.equal(r.snapshot().commit,committed?1:0);
   const retry=r.receive('data',pcm).decision;assert.equal(retry,committed?'duplicate':'new');exact();const after=r.snapshot();assert.equal(after.commit,1);assert.equal(after.epochs[0].records.length,1);assert.equal(after.epochs[0].semantic.world.events.length,1);
   return {before,recovery:r.initial,retry,finalCommit:after.commit,retainedEffects:1};
  });
  for(const name of ['missing-witness','malformed-witness','witness-only-rollback','joint-rollback','local-rollback-recover','local-rollback-no-candidate'])scenario(name,({dir,w,f,stage,first,anchor,read,exact})=>{
   const r=J.open(dir,w);assert.equal(r.receive('data',pcm).decision,'new');exact();const advanced=fs.readFileSync(f);
   if(name==='missing-witness')fs.unlinkSync(w);
   if(name==='malformed-witness')fs.writeFileSync(w,'{}');
   if(name==='witness-only-rollback'||name==='joint-rollback')fs.writeFileSync(w,anchor);
   if(name==='joint-rollback'||name.startsWith('local-rollback'))fs.writeFileSync(f,first);
   if(name==='local-rollback-no-candidate')fs.unlinkSync(stage);
   if(name==='joint-rollback'||name==='local-rollback-recover'){
    const rr=J.open(dir,w);assert.equal(rr.initial,name==='joint-rollback'?'current':'candidate');const retry=rr.receive('data',pcm).decision;assert.equal(retry,name==='joint-rollback'?'new':'duplicate');exact();assert.deepEqual(fs.readFileSync(f),advanced);return {recovery:rr.initial,retry,finalCommit:read().commit};
   }
   let error;try{J.open(dir,w)}catch(e){error=e.message;}assert.ok(error);assert.match(error,name==='missing-witness'?/ENOENT/:/no-witness-matching-state/);assert.equal(read().commit,name==='local-rollback-no-candidate'?0:1);return {refused:true,error:name==='missing-witness'?'ENOENT':error,localCommit:read().commit};
  });
 }finally{fs.rmSync(root,{recursive:true,force:true});}
}
console.log(JSON.stringify({schema:'mhac-independent-journal-boundary-v1',node:process.version,platform:process.platform,source:'3637529f313949d31e55d66d04bb119547c1e29a',results,limits:'Logical cuts are injected exceptions, not crash/power-loss. Public synthetic keys; one writer; actual aligned PCM and native filesystem calls. No external witness or physical device.'},null,2));
