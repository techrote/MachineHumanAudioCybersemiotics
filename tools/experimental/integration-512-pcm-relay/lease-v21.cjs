'use strict';
// Refs #512. Original integration experiment; no imported upstream code.
const compact=require('./compact-v20.cjs'), {tag,render}=require('./bound-v2.cjs');
const {scan,STEP}=require('./clarify-v18.cjs'),{base,wav}=require('./relay.cjs');
const eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b), id=p=>JSON.stringify([p.source,p.version,p.actor,p.event,p.seq,p.tree]);
const C={...base,version:1,actor:9,event:6,seq:15},D={...base,version:2,actor:5,event:9,seq:16};
const integer=x=>Number.isSafeInteger(x)&&x>=0;
// Caller supplies monotone absolute sample time. Inclusive retirement horizon.
// A live entry cannot be evicted. A retired entry cannot be evicted before expiry.
function ledger(cap,life){
 if(!integer(cap)||cap<1||!integer(life))throw Error('configuration');
 let last=0;const entries=new Map();
 function advance(now){if(!integer(now)||now<last||!Number.isSafeInteger(now+life))throw Error('clock');last=now;for(const [k,v] of entries)if(v.until!==null&&now>v.until)entries.delete(k);}
 return {reserve(p,now){advance(now);const k=tag(p).join(',');if(entries.has(k))return 'tag-reserved';if(entries.size===cap)return 'capacity';entries.set(k,{id:id(p),until:null});return 'admitted';},retire(p,now){advance(now);const v=entries.get(tag(p).join(','));if(!v||v.id!==id(p)||v.until!==null)throw Error('retire');v.until=now+life;},snapshot(){return {last,entries:[...entries].map(([k,v])=>[k,{...v}])};}};
}
const scenarios=['bounded-replay','expired-replay','lost-history','honest-current','no-replay'];
function run(scenario,policy,seed=71,chunk=511){
 if(!scenarios.includes(scenario)||!['singleton','quarantine'].includes(policy))throw Error('case');
 const slots=19,pcm=new Int16Array(slots*STEP),gaps=[],events=[],controls=[],trace=[];
 const life=4*STEP;let store=ledger(2,life),slot=0,oldRequest=null,newRequest=null,current=C,record={p:C,attempts:0,ready:0,first:null},ack=null,retired=false,offered=false;
 const metrics={admitted:null,blocked:0,honored:0,wrongRepair:0,confirmed:{},reservation:0};
 const log=(type,at,extra={})=>trace.push({type,at,...extra});
 if(policy==='quarantine')store.reserve(C,0);
 function evidence(e){events.push(e);const p=e.packet;if(!p||id(p)!==id(current))return;
  if(e.authority===false&&e.status==='diagnostic-ok'&&p.kind===0){const signal=compact.render(p,seed*.013);if(current===C&&!oldRequest){oldRequest=signal;log('request-created',e.at,{packet:p});}else if(current===D&&!newRequest){newRequest=signal;log('request-created',e.at,{packet:p});}return;}
  if(e.status!=='ok'||e.authority===false)return;
  if(p.kind===0){ack={...p,kind:1};log('receipt',e.at,{packet:p});}
  else if(p.kind===1&&record&&record.attempts){metrics.confirmed[current===C?'C':'D']=e.at;log('confirmation',e.at,{packet:p});if(policy==='quarantine')store.retire(record.p,e.at);record=null;if(current===C)retired=true;}
 }
 const reader=scan(pcm,gaps,evidence,chunk);
 const offerAt=['expired-replay','honest-current'].includes(scenario)?12:8;
 for(slot=0;slot<slots;slot++){
  const at=slot*STEP,start=at+64,h=at+STEP;
  if(slot===offerAt){if(!retired)throw Error('previous not retired');current=D;offered=true;if(scenario==='lost-history')store=ledger(2,life);}
  if(offered&&metrics.admitted===null){const result=policy==='quarantine'?store.reserve(D,at):'admitted';log('admission',at,{result});if(result==='admitted'){record={p:D,attempts:0,ready:slot,first:null};metrics.admitted=at;}else metrics.blocked++;}
  let a=null,origin='idle',p=null;
  const replay=(['bounded-replay','lost-history'].includes(scenario)&&slot===9)||(scenario==='expired-replay'&&slot===13);
  if(replay){if(!oldRequest)throw Error('no old diagnostic request');a=oldRequest;origin='delayed-old-request';}
  else if(scenario==='honest-current'&&slot===13){if(!newRequest)throw Error('no current diagnostic request');a=newRequest;origin='current-request';}
  else if(ack){p=ack;ack=null;a=render(p,seed*.013+slot*.19);origin='ack';}
  else if(record&&record.ready<=slot&&record.attempts<2){p=record.p;a=render(p,seed*.013+slot*.19);origin='data';record.attempts++;if(record.first===null)record.first=slot;record.ready=slot+5;
   if(record.attempts===1){if(current===C||scenario==='honest-current'){for(const off of [1036,2316,3596])gaps.push([start+off,start+off+16]);}else a.fill(0);}}
  if(a){pcm.set(a,start);metrics.reservation+=a.length;for(const [l,r] of gaps)if(l>=at&&r<=h)pcm.fill(0,l,r);}
  log('tx',at,{origin,packet:p});reader.feed(h);
  const e=compact.acquire(pcm.subarray(at,h),gaps.filter(([l,r])=>l<h&&r>at).map(([l,r])=>[l-at,r-at]));
  if(e.status!=='no-onset'){controls.push({...e,slot,at:h-1});if(e.status==='ok'){
   const match=compact.resolve(e.token,record?[record.p]:[]);let reason=match.status;
   if(match.packet){reason=record.attempts===1&&record.ready>slot+1&&h-1>=(record.first+1)*STEP&&h-1<(record.first+4)*STEP?'honored':'inactive-or-expired';if(reason==='honored'){record.ready=slot+1;metrics.honored++;if(origin==='delayed-old-request'&&record.p===D)metrics.wrongRepair++;}}
   log('control-decision',h-1,{reason,token:e.token,packet:match.packet||null});}}
 }
 reader.finish();return {scenario,policy,seed,metrics,trace,gaps,events,controls,pcm};
}
module.exports={ledger,run,scenarios,C,D};
if(require.main===module){
 const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict');
 const out=process.argv[2]||'lease-v21-output';fs.mkdirSync(out,{recursive:true});let checks=0;const ck=(x,m)=>{checks++;assert.ok(x,m);};
 ck(eq(tag(C),tag(D))&&!eq(C,D),'known collision');
 for(let life=0;life<=32;life++){const l=ledger(1,life);ck(l.reserve(C,0)==='admitted','initial');ck(l.reserve(D,0)==='tag-reserved','live collision');ck(l.reserve(base,0)==='capacity','capacity');l.retire(C,1);ck(l.reserve(D,life+1)==='tag-reserved','inclusive expiry');ck(l.reserve(D,life+2)==='admitted','first legal reuse');let threw=false;try{l.reserve(C,0);}catch{threw=true;}ck(threw,'clock rollback');}
 const rows=[];for(const seed of [71])for(const scenario of scenarios)for(const policy of ['singleton','quarantine']){
  const {pcm,...r}=run(scenario,policy,seed),m=r.metrics;ck(!!m.confirmed.C&&!!m.confirmed.D,'both genuine DATA/ACK exchanges');
  ck(m.wrongRepair===Number(['expired-replay','lost-history'].includes(scenario)||(scenario==='bounded-replay'&&policy==='singleton')),'stale repair outcome');
  ck(m.honored===Number(scenario==='honest-current'||m.wrongRepair===1),'request outcome');
  const events=[],reader=scan(pcm,r.gaps,e=>events.push(e),127);reader.feed(pcm.length);reader.finish();ck(eq(events,r.events),'alternate PCM rescan');
  const controls=[];for(let l=0;l<pcm.length;l+=STEP){const h=l+STEP,e=compact.acquire(pcm.subarray(l,h),r.gaps.filter(([a,b])=>a<h&&b>l).map(([a,b])=>[a-l,b-l]));if(e.status!=='no-onset')controls.push({...e,slot:l/STEP,at:h-1});}ck(eq(controls,r.controls),'control rescan');
  const file=`${seed}-${scenario}-${policy}.wav`,bytes=wav(pcm);fs.writeFileSync(path.join(out,file),bytes);rows.push({...r,file,sha256:crypto.createHash('sha256').update(bytes).digest('hex'),samples:pcm.length});
 }
 fs.writeFileSync(path.join(out,'receipt.json'),JSON.stringify({schema:'mhac-lease-v21',rate:16000,step:STEP,checks,rows},null,2)+'\n');console.log(JSON.stringify({checks,rows:rows.map(({seed,scenario,policy,metrics})=>({seed,scenario,policy,metrics}))},null,2));
}
