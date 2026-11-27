'use strict';
// Refs #607. Linux process termination at completed filesystem-call boundaries.
// Does not simulate kernel crash, loss of page cache, or power failure.
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),assert=require('node:assert/strict'),crypto=require('node:crypto'),{spawnSync}=require('node:child_process');
const J=require('./source/journal-v42.cjs'),A=require('./source/session-v40.cjs');
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const packet={kind:0,source:2,version:1,actor:9,event:8,seq:1,tree:['pump-reports',['fault']]};
const cuts=['before-stage','after-stage','after-witness','after-publish'];
const encode=seed=>A.encode(A.ctx(1),64,'data',packet,0,null,0,A.nonce(packet,0),seed*.013);
function child(dir,w,seed,cut){
 const pcm=encode(seed),stage=path.join(dir,'stage');
 const r=J.open(dir,w),open=fs.openSync,sync=fs.fsyncSync;
 let witnessAdvanced=false,stageSyncs=0;
 const stop=()=>{fs.writeSync(1,`cut:${cut}\n`);process.kill(process.pid,'SIGKILL');throw Error('SIGKILL returned');};
 fs.openSync=function(f,...args){if(cut==='before-stage'&&f===path.join(stage,'state.json.write'))stop();return open.call(this,f,...args);};
 fs.fsyncSync=function(fd){const target=fs.readlinkSync(`/proc/self/fd/${fd}`);const ret=sync.call(this,fd);
  if(target===stage){stageSyncs++;if(cut==='after-stage'&&stageSyncs===2)stop();}
  if(target===path.dirname(w)){witnessAdvanced=true;if(cut==='after-witness')stop();}
  if(target===dir&&witnessAdvanced&&cut==='after-publish')stop();
  return ret;
 };
 r.receive('data',pcm);throw Error('target boundary not reached');
}
function parent(){assert.equal(process.platform,'linux');const rows=[];const root=fs.mkdtempSync(path.join(os.tmpdir(),'mhac-process-cut-'));
 try{for(const seed of [71,113]){const pcm=encode(seed);for(const cut of cuts){const dir=path.join(root,`${seed}-${cut}`),w=dir+'.witness',f=path.join(dir,'state.json'),stage=path.join(dir,'stage','state.json');J.provision(dir,w);
  const c=spawnSync(process.execPath,[__filename,'--child',dir,w,String(seed),cut],{encoding:'utf8',timeout:60000});assert.ifError(c.error);assert.equal(c.signal,'SIGKILL',c.stderr);assert.equal(c.status,null);assert.equal(c.stdout,`cut:${cut}\n`);assert.equal(c.stderr,'');
  const read=file=>JSON.parse(fs.readFileSync(file));const before={local:read(f).s.commit,witness:read(w).commit,stage:fs.existsSync(stage)?read(stage).s.commit:null};const committed=cut==='after-witness'||cut==='after-publish';
  assert.deepEqual(before,{local:cut==='after-publish'?1:0,witness:committed?1:0,stage:cut==='before-stage'?null:1});
  const witnessedFile=cut==='after-witness'?stage:f;assert.equal(read(w).sha256,hash(fs.readFileSync(witnessedFile)));
  const r=J.open(dir,w);assert.equal(r.initial,cut==='after-witness'?'candidate':'current');assert.equal(r.snapshot().commit,committed?1:0);const retry=r.receive('data',pcm).decision;assert.equal(retry,committed?'duplicate':'new');
  const s=r.snapshot();assert.equal(s.commit,1);assert.equal(s.epochs[0].records.length,1);assert.equal(s.epochs[0].semantic.world.events.length,1);assert.deepEqual(read(w),{commit:1,sha256:hash(fs.readFileSync(f))});
  rows.push({seed,cut,termination:c.signal,before,recovery:r.initial,retry,finalCommit:s.commit,retainedEffects:1});
 }} }finally{fs.rmSync(root,{recursive:true,force:true});}
 console.log(JSON.stringify({schema:'mhac-journal-process-cut-v1',source:'3637529f313949d31e55d66d04bb119547c1e29a',node:process.version,platform:process.platform,rows,limits:'Actual child SIGKILL at instrumented filesystem-call boundaries. Original modules unmodified. Single writer; same running kernel and filesystem; not power-loss, kernel crash, or external witness qualification.'},null,2));
}
if(process.argv[2]==='--child')child(process.argv[3],process.argv[4],Number(process.argv[5]),process.argv[6]);else parent();
