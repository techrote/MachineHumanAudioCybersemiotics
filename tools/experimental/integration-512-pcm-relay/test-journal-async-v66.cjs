'use strict';
const fs=require('node:fs'),os=require('node:os'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto'),{spawnSync}=require('node:child_process');
const J=require('./journal-async-v66.cjs'),R=require('./async-rx-v65.cjs'),F=require('./fresh-v45.cjs'),{wav}=require('./relay.cjs');
const p={kind:0,source:1,version:1,actor:9,event:7,seq:2,tree:['verify',['stopped']]},q={...p,source:2,event:8,tree:['pump-reports',['fault']]};
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
function read(file){const b=fs.readFileSync(file);return Int16Array.from({length:(b.length-44)/2},(_,i)=>b.readInt16LE(44+2*i));}
function feed(c,x,gap=null){for(let i=0;i<x.length;){if(gap&&i===gap[0]){c.gap(gap[1]-i);i=gap[1];continue;}const end=Math.min(x.length,i+511,gap&&i<gap[0]?gap[0]:Infinity);c.push(x.subarray(i,end));i=end;}return c;}
function place(...xs){const y=new Int16Array(13+xs.reduce((n,x)=>n+x.length,0)+1500);let i=13;for(const x of xs){y.set(x,i);i+=x.length;}return y;}
if(process.argv[2]==='child'){const [dir,w,cut,file]=process.argv.slice(3);feed(J.open(dir,w).continuous(()=>{},k=>{if(k===cut)process.exit(77);}),read(file)).finish();throw Error('cut not reached');}
const out=process.argv[2]||'journal66-results';fs.mkdirSync(out,{recursive:true});const root=fs.mkdtempSync(path.join(os.tmpdir(),'mhac66-'));let checks=0,serial=0;const rows=[],archive=[];
const ck=(a,b)=>{assert.deepEqual(a,b);checks++;};const throws=f=>{assert.throws(f);checks++;};
function pair(){const dir=path.join(root,String(serial++)),w=dir+'.w';J.provision(dir,w,'shared',1,6);const j=J.open(dir,w),id=j.register(p,1);j.allocate(id);return {dir,w,j,id,reopen:()=>J.open(dir,w)};}
function scan(a,x,gap=null,mid=null){const events=[],states=[];const c=a.j.continuous(e=>{events.push(e);states.push(a.reopen().snapshot());});if(mid){feed(c,x.subarray(0,40000));mid();feed(c,x.subarray(40000));}else feed(c,x,gap);c.finish();return {events,states};}
const count=z=>z.events.filter(e=>e.decision==='consumed').length;
function row(seed,name,x,a,before,z,expected,extra={}){ck(count(z),expected);const after=a.reopen().snapshot();ck(after.commit,before.commit+expected+(extra.otherCommits||0));const file=seed+'-'+name+'.wav',b=Buffer.from(wav(x));fs.writeFileSync(path.join(out,file),b);rows.push({seed,name,file,samples:x.length,sha256:sha(b),before,after,...z,...extra});}
try{
for(const dir of ['async64-results','async65-results']){const old=JSON.parse(fs.readFileSync(path.join(dir,'receipt.json')));for(const r of old.specimens){const a=pair(),before=a.j.snapshot(),file=path.join(dir,r.file);ck(sha(fs.readFileSync(file)),r.sha256);const z=scan(a,read(file),r.gap);const expected=r.name==='early-decoy-lock'?1:r.events.some(e=>e.decision.kind!=='unknown')?1:0;ck(count(z),expected);ck(a.reopen().snapshot().commit,before.commit+expected);archive.push({dir,name:r.name,seed:r.seed,staticAdmits:r.events.filter(e=>e.decision.kind!=='unknown').length,consumed:count(z)});}}
for(const seed of [71,113]){
 const reply=(packet,n,report={status:'applied',revision:2})=>F.reply(1,packet,1,n,report,seed*.013,true),pcm=reply(p,7),clean=place(pcm);
 {const a=pair(),id=a.j.register(q,1);ck(a.j.allocate(id),8);const before=a.j.snapshot(),x=place(pcm,reply(q,8)),z=scan(a,x);row(seed,'two-distinct',x,a,before,z,2);ck(z.states[0].offers[1].pending,8);ck(z.states[1].offers.map(o=>o.pending),[null,null]);}
 {const a=pair(),x=place(pcm,pcm),before=a.j.snapshot(),z=scan(a,x);row(seed,'duplicate-in-stream',x,a,before,z,1);ck(z.events.map(e=>e.decision),['consumed','refused']);ck(z.states[0],z.states[1]);}
 {const a=pair(),before=a.j.snapshot(),z=scan(a,clean,null,()=>ck(a.j.allocate(a.id),8));row(seed,'renew-during-capture',clean,a,before,z,0,{otherCommits:1});ck(a.j.snapshot().offers[0].pending,8);const b=a.j.snapshot(),abs=place(reply(p,8,null)),v=scan(a,abs);row(seed,'fresh-absent',abs,a,b,v,1);ck(v.events[0].evidence,{challenge:8,kind:'absent',status:'no-exact-retained-record',revision:null});}
 {const a=pair(),before=a.j.snapshot(),gap=[13+R.HORIZON+20,13+R.HORIZON+38],z=scan(a,clean,gap);row(seed,'guard-gap',clean,a,before,z,0,{gap});ck(a.j.snapshot(),before);}
 {const a=pair(),x=clean.subarray(0,13+pcm.length),before=a.j.snapshot(),z=scan(a,x);row(seed,'no-guard',x,a,before,z,0);ck(a.j.snapshot(),before);}
 {const a=pair(),before=a.j.snapshot(),z=scan(a,clean);row(seed,'clean',clean,a,before,z,1);}
 for(const cut of ['before-stage','after-stage','after-witness','after-publish']){const a=pair(),before=a.j.snapshot(),file=path.join(out,seed+'-clean.wav');const child=spawnSync(process.execPath,[__filename,'child',a.dir,a.w,cut,file],{encoding:'utf8'});ck(child.status,77);const committed=['after-witness','after-publish'].includes(cut),recovered=a.reopen().snapshot();ck(recovered.commit,before.commit+Number(committed));ck(recovered.offers[0].pending,committed?null:7);const v=scan(a,clean);row(seed,'cut-'+cut,clean,a,recovered,v,committed?0:1,{childExit:child.status});ck(a.j.snapshot().commit,before.commit+1);}
 {const a=pair(),before=a.j.snapshot(),s=fs.readFileSync(path.join(a.dir,'current')),w=fs.readFileSync(a.w);ck(count(scan(a,clean)),1);fs.writeFileSync(path.join(a.dir,'current'),s);fs.writeFileSync(a.w,w);const z=scan(a,clean);row(seed,'joint-rollback',clean,a,before,z,1,{previouslyConsumed:true});}
 {const a=pair(),before=a.j.snapshot(),c=a.j.continuous(()=>{throw Error('observer failed');});throws(()=>feed(c,clean));throws(()=>c.finish());ck(a.reopen().snapshot().commit,before.commit+1);const b=a.j.snapshot(),z=scan(a,clean);row(seed,'callback-failure-replay',clean,a,b,z,0,{previouslyConsumed:true});}
}
const receipt={schema:'mhac-journal-async-v66',parent:'3e70388c74b858b8d06afcef46cc1b37cd116d7a',node:process.version,checks,archive,rows};fs.writeFileSync(path.join(out,'receipt.json'),JSON.stringify(receipt,null,2)+'\n');console.log(JSON.stringify({checks,archive:archive.length,rows:rows.length}));
}finally{fs.rmSync(root,{recursive:true,force:true});}
