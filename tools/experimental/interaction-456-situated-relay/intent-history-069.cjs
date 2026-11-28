'use strict';
// Refs #456. Synthetic-only bounded retired history variant; no canonical wire change.
const fs=require('node:fs'),p=require('node:path'),c=require('node:crypto'),a=require('node:assert/strict');
const parent='7784d3d8d401e3f340e777d822651cd569f7cce3', HISTORY=2;
const {C,D}=require('./intent-continuity-065.cjs').load(__dirname);
const eq=(x,y)=>JSON.stringify(x)===JSON.stringify(y),hash=x=>c.createHash('sha256').update(JSON.stringify(x)).digest('hex');
const write=(f,x)=>{fs.writeFileSync(f+'.tmp',JSON.stringify(x));fs.renameSync(f+'.tmp',f);};
const read=f=>JSON.parse(fs.readFileSync(f,'utf8'));
function init(d,role,policy='terminal'){
 if(!['requester','reporter'].includes(role)||!['terminal','completed-only'].includes(policy))throw Error('configuration');
 fs.mkdirSync(d);const s=role==='requester'?{role,policy,gen:0,nonce:0,pending:null,observations:{},knowledge:null}:{role,policy,gen:0,nonce:0,tick:0,rev:2,value:'open',floor:22,entries:{},effects:0};
 s.schema=69;if(role==='reporter')s.retired=[];write(p.join(d,'state'),s);write(p.join(d,'witness'),{gen:0,hash:hash(s)});
}
function recover(d){const w=read(p.join(d,'witness'));for(const n of ['state','stage']){try{const s=read(p.join(d,n));if(s.gen===w.gen&&hash(s)===w.hash){if(s.schema!==69)throw Error('schema');return s;}}catch{}}throw Error('continuity unavailable');}
function commit(d,s,cut){const old=recover(d);a.equal(old.gen,s.gen);write(p.join(d,'state'),old);s.gen++;a.ok(Buffer.byteLength(JSON.stringify(s))<=4096);write(p.join(d,'stage'),s);if(cut==='stage')process.exit(77);write(p.join(d,'witness'),{gen:s.gen,hash:hash(s)});if(cut==='witness')process.exit(77);write(p.join(d,'state'),s);}
const req={observe:[1,['question',['open']],2],replace:[7,['question',['open']],2],apply:[3,['stopped'],4],query:[5,['question',['stopped']],6],cancel:[8,['not',['stopped']],10],skip:[9,['quote',['open']],11]};
const outcomes={applied:['verify',['stopped']],refused:['not',['stopped']],unseen:['question',['stopped']],unknown:['uncertain',['stopped']],duplicate:['quote',['stopped']],cancelled:['not',['open']],skipped:['quote',['open']],retired:['uncertain',['open']],window:['overload'],allocated:['verify',['open']],unsupported:['fault']};
const key=(id,seq)=>id+':'+seq;
function message(kind,event,id,seq,prev,nonce,version,tree){return {p:{kind,source:kind+1,version,actor:3,event,seq,tree},intent:id,prev,nonce};}
function begin(d,op,id,seq=1,prev=0,cut){const s=recover(d),k=key(id,seq);a.equal(s.role,'requester');if(s.pending||s.nonce===0xffffffff)throw Error('pending or exhausted');if(!req[op]||!Number.isInteger(id)||id<1||id>65535||!Number.isInteger(seq)||seq<1||seq>16||!Number.isInteger(prev)||prev<0||prev>16)throw Error('domain');
 let version=1;
 if(op==='replace'){const old=s.observations[key(id,prev)];if(!prev||!old||!s.knowledge||s.knowledge.id!==id||s.knowledge.seq!==prev||s.knowledge.op!=='query'||s.knowledge.result!=='unseen')throw Error('fresh execution not authorized');}
 else if(op==='observe'||op==='skip'){if(prev)throw Error('unexpected predecessor');}
 else {const o=s.observations[k];if(!o||o.prev!==prev)throw Error('no correlated observation');version=o.version;}
 if((op==='observe'||op==='replace')&&!s.observations[k]&&Object.keys(s.observations).length>=4)throw Error('requester capacity');
 const [event,tree]=req[op],m=message(0,event,id,seq,prev,++s.nonce,version,tree);s.pending={op,m};commit(d,s,cut);return m;}
function abandon(d){const s=recover(d);a.equal(s.role,'requester');if(s.pending){s.pending=null;commit(d,s);}}
function forget(d,id){const s=recover(d);a.equal(s.role,'requester');if(s.pending)throw Error('pending');for(const k of Object.keys(s.observations))if(k.startsWith(id+':'))delete s.observations[k];if(s.knowledge?.id===id)s.knowledge=null;commit(d,s);}
function encode(m,phase=.92,session=1,bad=false){return C.encode(D,m,phase,session,bad);}
function decode(x){return C.decode(D,x,1);}
function receive(d,x,cut){const s=recover(d);a.equal(s.role,'reporter');const z=decode(x),m=z.m;const op=z.authenticated&&m&&m.p.kind===0&&m.p.source===1&&m.p.actor===3&&Object.keys(req).find(k=>m.p.event===req[k][0]&&eq(m.p.tree,req[k][1]));
 if(!op||m.nonce<=s.nonce)return {result:'invalid-or-stale',reply:null};
 const id=m.intent,seq=m.p.seq,prev=m.prev,e=s.entries[id],v=e?.samples[seq];let result='unknown',version=m.p.version,tree=null;s.nonce=m.nonce;s.tick++;
 const match=!!v&&v.prev===prev&&v.version===version;
 if(id<=s.floor){
  result='retired';
  // Retain the exact historical QUERY semantics, not an inferred intent-wide outcome.
  // Only QUERY can inspect a retired record; no retired operation may execute again.
  if(op==='query'){const t=s.retired.find(h=>h.id===id),u=t?.entry.samples[seq];
   if(u&&u.prev===prev&&u.version===version)result=u.outcome||(t.entry.status==='applied'?'duplicate':t.entry.status==='cancelled'?'cancelled':'unseen');}
 }else if(id>s.floor+2)result='window';
 else if(op==='observe'||op==='replace'){
  const predecessor=e?.samples[prev],valid=version===1&&(op==='observe'?!prev&&!e:prev&&e?.status==='open'&&predecessor&&!predecessor.outcome&&!v);
  // A fresh nonce authenticates a new enquiry, not a new observation. Never refresh v.at.
  const retry=version===1&&e?.status==='open'&&v&&!v.outcome&&v.prev===prev&&(op==='observe'?!prev:!!prev);
  if(retry){version=v.version;tree=[v.value];result='observed';}
  else if(valid&&Object.keys(e?.samples||{}).length<2){const t=e||{status:'open',samples:{}};t.samples[seq]={prev,version:s.rev,value:s.value,at:s.tick,outcome:null};s.entries[id]=t;version=s.rev;tree=[s.value];result='observed';}else result='refused';
 }else if(op==='skip'){if(version!==1||prev)result='refused';else if(s.policy!=='terminal')result='unsupported';else if(e)result='allocated';else {s.entries[id]={status:'skipped',samples:{}};result='skipped';}}
 else if(!match)result='unknown';
 else if(op==='query')result=v.outcome||(e.status==='applied'?'duplicate':e.status==='cancelled'?'cancelled':'unseen');
 else if(op==='cancel'){if(s.policy!=='terminal')result='unsupported';else if(e.status==='applied')result='applied';else if(e.status==='open'){e.status='cancelled';result='cancelled';}else result=e.status;}
 else if(e.status==='cancelled')result='cancelled';else if(v.outcome)result=v.outcome;else if(e.status==='applied')result='duplicate';
 else if(v.value==='open'&&s.value==='open'&&s.rev===version&&s.rev<16&&s.tick-v.at<=3){v.outcome='applied';e.status='applied';s.effects++;s.rev++;s.value='stopped';result='applied';}else {v.outcome='refused';result='refused';}
 while(['applied','cancelled','skipped'].includes(s.entries[s.floor+1]?.status)){
  const id=++s.floor;s.retired.push({id,entry:s.entries[id]});delete s.entries[id];
  if(s.retired.length>HISTORY)s.retired.shift();
 }
 a.ok(s.retired.length<=HISTORY);
 a.ok(Object.keys(s.entries).length<=2);commit(d,s,cut);return {result,reply:message(1,req[op][2],id,seq,prev,m.nonce,version,tree||outcomes[result])};}
function accept(d,x,cut){const s=recover(d);a.equal(s.role,'requester');const z=decode(x),m=z.m,q=s.pending?.m,op=s.pending?.op;if(!z.authenticated||!m||!q||m.p.kind!==1||m.p.source!==2||m.p.actor!==3||m.p.event!==req[op][2]||m.intent!==q.intent||m.prev!==q.prev||m.nonce!==q.nonce||m.p.seq!==q.p.seq)return 'unmatched';
 const observation=['observe','replace'].includes(op)&&['open','stopped','fault'].some(v=>eq(m.p.tree,[v]));let result=observation?'observed':Object.keys(outcomes).find(k=>eq(m.p.tree,outcomes[k]));if(!result||(!observation&&m.p.version!==q.p.version))return 'unmatched';
 if(observation){const k=key(m.intent,m.p.seq),next={version:m.p.version,prev:m.prev,value:m.p.tree[0]},old=s.observations[k];if(old&&!eq(old,next))return 'unmatched';s.observations[k]=next;}s.knowledge={op,id:m.intent,seq:m.p.seq,result};s.pending=null;commit(d,s,cut);return result;}
function reopen(d){const s=recover(d);a.equal(s.role,'reporter');if(s.rev>=16)throw Error('revision exhausted');s.rev++;s.value='open';commit(d,s);}
module.exports={parent,HISTORY,C,D,init,recover,begin,abandon,forget,encode,decode,receive,accept,reopen};
