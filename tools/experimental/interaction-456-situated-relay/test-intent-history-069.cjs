'use strict';
// Refs #456: bounded terminal history acoustic controls, actual filesystem/process boundaries.
const fs=require('node:fs'),p=require('node:path'),os=require('node:os'),c=require('node:crypto'),a=require('node:assert/strict'),cp=require('node:child_process');
const variants={baseline:require('./intent-retry-068.cjs'),retry:require('./intent-history-069.cjs')};
const raw=x=>Buffer.from(x.buffer,x.byteOffset,x.byteLength),hash=b=>c.createHash('sha256').update(b).digest('hex');
if(process.argv[2]==='child'){const [variant,d,f,cut]=process.argv.slice(3),b=fs.readFileSync(f);variants[variant].receive(d,Int16Array.from({length:b.length/2},(_,i)=>b.readInt16LE(i*2)),cut);process.exit(0);}
const out=p.resolve(process.argv[2]||'results069');fs.mkdirSync(out,{recursive:true});const root=fs.mkdtempSync(p.join(os.tmpdir(),'mhac069-'));let checks=0,exits=0,peak=0;const rows=[];
const ck=(x,y)=>{checks++;a.deepEqual(x,y);};
try{for(const seed of [71,113])for(const [variant,P] of Object.entries(variants))for(const scenario of ['lost-apply','lost-cancel','eviction','binding','refused-then-cancel','replacement','restart-stage','restart-witness']){
 const q=p.join(root,'q'),r=p.join(root,'r'),retry=variant==='retry';for(const d of [q,r])fs.rmSync(d,{recursive:true,force:true});P.init(q,'requester');P.init(r,'reporter');const clips=[],events=[];
 const snap=()=>({q:P.recover(q),r:P.recover(r)}),sample=(id=24,seq=1)=>P.recover(r).entries[id]?.samples[seq];
 const hear=(label,m,x)=>{x=x||P.encode(m,seed*.013+clips.length*.071);clips.push(x);events.push({label,sha256:hash(raw(x)),decoded:P.decode(x)});return x;};
 const state=(label,result)=>{const s=snap();for(const v of Object.values(s))peak=Math.max(peak,Buffer.byteLength(JSON.stringify(v)));events.push({label,result,state:s});};
 const send=(op,id=24,seq=1,prev=0,opt={})=>{const m=P.begin(q,op,id,seq,prev),x=hear(op,m);if(opt.cut){const f=p.join(root,'pcm');fs.writeFileSync(f,raw(x));const z=cp.spawnSync(process.execPath,[__filename,'child',variant,r,f,opt.cut],{encoding:'utf8'});ck(z.status,77);exits++;P.abandon(q);state(op,'exit');return {m,x};}if(opt.dropRequest){P.abandon(q);state(op,'request-lost');return {m,x};}const rr=P.receive(r,x);a.ok(rr.reply);const y=hear('reply '+op,rr.reply);if(opt.dropReply){P.abandon(q);state(op,'reply-lost');return {...rr,m,x,y};}const accepted=P.accept(q,y);state(op,accepted);return {...rr,accepted,m,x,y};};
 const expect=(op,w,id=24,seq=1,prev=0,opt={})=>{const z=send(op,id,seq,prev,opt);ck(z.accepted,w);return z;};
 if(scenario==='lost-apply'||scenario==='lost-cancel'){
  const op=scenario==='lost-apply'?'apply':'cancel',outcome=op==='apply'?'applied':'cancelled';
  expect('observe','observed',23);const lost=send(op,23,1,0,{dropReply:true});ck(lost.result,outcome);ck(P.recover(r).floor,23);ck(P.recover(r).effects,op==='apply'?1:0);
  const first=expect('query',retry?outcome:'retired',23);ck(P.accept(q,hear('old terminal reply',null,lost.y)),'unmatched');
  expect(op,'retired',23);expect('query',retry?outcome:'retired',23);ck(P.recover(r).effects,op==='apply'?1:0);ck(P.recover(r).floor,23);
 }
 if(scenario==='eviction'){
  expect('observe','observed',23);send('cancel',23,1,0,{dropReply:true});expect('skip','skipped',24);expect('query',retry?'cancelled':'retired',23);
  expect('skip','skipped',25);expect('query','retired',23);ck(P.recover(r).floor,25);if(retry)ck(P.recover(r).retired.map(h=>h.id),[24,25]);expect('apply','retired',23);ck(P.recover(r).effects,0);
 }
 if(scenario==='binding'){
  expect('observe','observed',23);expect('apply','applied',23);const m=P.begin(q,'query',23),bad={...m,p:{...m.p,version:3}};const rr=P.receive(r,hear('wrong version query',bad));ck(rr.result,'retired');ck(P.accept(q,hear('wrong version reply',rr.reply)),'unmatched');P.abandon(q);
  expect('query',retry?'applied':'retired',23);ck(P.recover(r).effects,1);
 }
 if(scenario==='refused-then-cancel'){
  expect('observe','observed',23);P.reopen(r);expect('apply','refused',23);send('cancel',23,1,0,{dropReply:true});expect('query',retry?'refused':'retired',23);ck(P.recover(r).effects,0);ck(P.recover(r).floor,23);
 }
 if(scenario==='replacement'){
  expect('observe','observed',23);send('apply',23,1,0,{dropRequest:true});expect('query','unseen',23);expect('replace','observed',23,2,1);send('apply',23,2,1,{dropReply:true});expect('query',retry?'applied':'retired',23,2,1);expect('query',retry?'duplicate':'retired',23);ck(P.recover(r).effects,1);
 }
 if(scenario==='restart-stage'||scenario==='restart-witness'){
  const cut=scenario.slice(8);expect('observe','observed',23);send('apply',23,1,0,{cut});ck(P.recover(r).floor,cut==='witness'?23:22);ck(P.recover(r).effects,cut==='witness'?1:0);
  if(cut==='stage'){expect('query','unseen',23);expect('apply','applied',23);}expect('query',retry?'applied':'retired',23);ck(P.recover(r).effects,1);
 }
 const wav=P.D.R.wav(P.D.R.join(...clips)),file=`${seed}-${variant}-${scenario}.wav`;fs.writeFileSync(p.join(out,file),wav);rows.push({seed,variant,scenario,file,sha256:hash(wav),events,final:snap()});
}const receipt={parent:variants.retry.parent,rate:16000,frame:variants.retry.C.F,node:process.version,checks,exits,peak,rows};fs.writeFileSync(p.join(out,'receipt.json'),JSON.stringify(receipt)+'\n');console.log(JSON.stringify({checks,exits,peak,sessions:rows.length,slots:rows.reduce((n,r)=>n+r.events.filter(e=>e.decoded).length,0)}));}finally{fs.rmSync(root,{recursive:true,force:true});}
