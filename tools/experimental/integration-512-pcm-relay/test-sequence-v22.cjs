'use strict';
// Refs #512. Additive scheduler fork of lease-v21.cjs, no upstream imports.
const legacy=require('./compact-v20.cjs'),qualified=require('./sequence-v22.cjs'),{tag,render}=require('./bound-v2.cjs');
const {scan,STEP}=require('./clarify-v18.cjs'),{wav}=require('./relay.cjs'),{C,D:collisionD}=require('./lease-v21.cjs');
const eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b), id=p=>JSON.stringify([p.source,p.version,p.actor,p.event,p.seq,p.tree]);
const scenarios=['bounded-replay','expired-replay','honest-current','no-replay','reused-sequence','forged-current'];
function run(scenario,policy,seed=71,chunk=511){
 const D=scenario==='reused-sequence'?{...C}:collisionD,compact=policy==='qualified'?qualified:legacy;
 if(!scenarios.includes(scenario)||!['legacy','qualified'].includes(policy))throw Error('case');
 const slots=19,pcm=new Int16Array(slots*STEP),gaps=[],events=[],controls=[],trace=[];
 let slot=0,oldRequest=null,newRequest=null,current=C,record={p:C,attempts:0,ready:0,first:null},ack=null,retired=false,offered=false;
 const metrics={admitted:null,blocked:0,honored:0,wrongRepair:0,forgedHonored:0,confirmed:{},reservation:0};
 const log=(type,at,extra={})=>trace.push({type,at,...extra});
 function evidence(e){events.push(e);const p=e.packet;if(!p||id(p)!==id(current))return;
  if(e.authority===false&&e.status==='diagnostic-ok'&&p.kind===0){const signal=compact.render(p,seed*.013);if(current===C&&!oldRequest){oldRequest=signal;log('request-created',e.at,{packet:p});}else if(current===D&&!newRequest){newRequest=signal;log('request-created',e.at,{packet:p});}return;}
  if(e.status!=='ok'||e.authority===false)return;
  if(p.kind===0){ack={...p,kind:1};log('receipt',e.at,{packet:p});}
  else if(p.kind===1&&record&&record.attempts){metrics.confirmed[current===C?'C':'D']=e.at;log('confirmation',e.at,{packet:p});record=null;if(current===C)retired=true;}
 }
 const reader=scan(pcm,gaps,evidence,chunk);
 const offerAt=['expired-replay','honest-current'].includes(scenario)?12:8;
 for(slot=0;slot<slots;slot++){
  const at=slot*STEP,start=at+64,h=at+STEP;
  if(slot===offerAt){if(!retired)throw Error('previous not retired');current=D;offered=true;}
  if(offered&&metrics.admitted===null){log('admission',at,{result:'admitted'});record={p:D,attempts:0,ready:slot,first:null};metrics.admitted=at;}
  let a=null,origin='idle',p=null;
  const replay=(['bounded-replay','lost-history','reused-sequence'].includes(scenario)&&slot===9)||(scenario==='expired-replay'&&slot===13);
  if(replay){if(!oldRequest)throw Error('no old diagnostic request');a=oldRequest;origin='delayed-old-request';}
  else if(scenario==='forged-current'&&slot===9){a=compact.render(D,seed*.013);origin='forged-current-request';}
  else if(scenario==='honest-current'&&slot===13){if(!newRequest)throw Error('no current diagnostic request');a=newRequest;origin='current-request';}
  else if(ack){p=ack;ack=null;a=render(p,seed*.013+slot*.19);origin='ack';}
  else if(record&&record.ready<=slot&&record.attempts<2){p=record.p;a=render(p,seed*.013+slot*.19);origin='data';record.attempts++;if(record.first===null)record.first=slot;record.ready=slot+5;
   if(record.attempts===1){if(current===C||scenario==='honest-current'){for(const off of [1036,2316,3596])gaps.push([start+off,start+off+16]);}else a.fill(0);}}
  if(a){pcm.set(a,start);metrics.reservation+=a.length;for(const [l,r] of gaps)if(l>=at&&r<=h)pcm.fill(0,l,r);}
  log('tx',at,{origin,packet:p});reader.feed(h);
  const e=compact.acquire(pcm.subarray(at,h),gaps.filter(([l,r])=>l<h&&r>at).map(([l,r])=>[l-at,r-at]));
  if(e.status!=='no-onset'){controls.push({...e,slot,at:h-1});if(e.status==='ok'){
   const match=compact.resolve(e.token,record?[record.p]:[]);let reason=match.status;
   if(match.packet){reason=record.attempts===1&&record.ready>slot+1&&h-1>=(record.first+1)*STEP&&h-1<(record.first+4)*STEP?'honored':'inactive-or-expired';if(reason==='honored'){record.ready=slot+1;metrics.honored++;if(origin==='delayed-old-request'&&record.p===D)metrics.wrongRepair++;if(origin==='forged-current-request')metrics.forgedHonored++;}}
   log('control-decision',h-1,{reason,token:e.token,packet:match.packet||null});}}
 }
 reader.finish();return {scenario,policy,seed,metrics,trace,gaps,events,controls,pcm};
}
module.exports={run,scenarios};
if(require.main===module){
 const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict');
 const out=process.argv[2]||'sequence-v22-output';fs.mkdirSync(out,{recursive:true});let checks=0;const ck=(x,m)=>{checks++;assert.ok(x,m);};
 ck(eq(tag(C),tag(collisionD))&&!eq(C,collisionD),'known collision');ck(!eq(qualified.token(C),qualified.token(collisionD)),'distinct labels');
 for(const p of [C,collisionD]){const t=qualified.token(p),w=qualified.protect(t);for(let i=0;i<w.length;i++){for(let j=i+1;j<w.length;j++){const z=w.slice();z[i]=z[j]=null;ck(eq(qualified.recover(z),t),'two erasures');}for(let d=1;d<17;d++){const z=w.slice();z[i]=(z[i]+d)%17;ck(qualified.recover(z)===null,'single substitution');}}}
 const rows=[],controls=[];for(const seed of [71,113]){
  const phase=seed*.013,clean=qualified.render(C,phase);for(const [name,pcm,gaps,expect] of [['clean',clean,[],'ok'],['two-erasures',qualified.render(C,phase,w=>w.map((v,i)=>[6,7].includes(i)?null:v)),[],'ok'],['three-erasures',qualified.render(C,phase,w=>w.map((v,i)=>[5,6,7].includes(i)?null:v)),[],'parity-or-domain-refused'],['substitution',qualified.render(C,phase,w=>w.map((v,i)=>i===7?(v+1)%17:v)),[],'parity-or-domain-refused'],['outside-gap',require('./relay.cjs').join(clean,new Int16Array(320)),[[clean.length,clean.length+1]],'capture-incomplete'],['truncated',clean.slice(0,-1),[],'truncated'],['old-namespace',legacy.render(C,phase),[],'no-onset'],['full-data',render(C,phase),[],'no-onset'],['double-onset',require('./relay.cjs').join(clean,new Int16Array(640),clean),[],'ambiguous-onset']]){
   const e=qualified.acquire(pcm,gaps);ck(e.status===expect,`${name}: ${e.status}`);if(e.status==='ok')ck(eq(e.token,qualified.token(C)),'PCM token');const file=`${seed}-control-${name}.wav`,bytes=wav(pcm);fs.writeFileSync(path.join(out,file),bytes);controls.push({seed,name,file,gaps,e,samples:pcm.length,sha256:crypto.createHash('sha256').update(bytes).digest('hex')});}
 }
 for(const scenario of scenarios)for(const policy of ['legacy','qualified']){
  const {pcm,...r}=run(scenario,policy,71),m=r.metrics;ck(!!m.confirmed.C&&!!m.confirmed.D,'both exchanges');
  ck(m.wrongRepair===Number(scenario==='reused-sequence'||(policy==='legacy'&&['bounded-replay','expired-replay'].includes(scenario))),'stale repair');ck(m.forgedHonored===Number(scenario==='forged-current'),'forgery');ck(m.honored===Number(scenario==='honest-current'||m.wrongRepair||m.forgedHonored),'request outcome');
  const events=[],reader=scan(pcm,r.gaps,e=>events.push(e),127);reader.feed(pcm.length);reader.finish();ck(eq(events,r.events),'alternate PCM rescan');
  const c=[],codec=policy==='qualified'?qualified:legacy;for(let l=0;l<pcm.length;l+=STEP){const h=l+STEP,e=codec.acquire(pcm.subarray(l,h),r.gaps.filter(([a,b])=>a<h&&b>l).map(([a,b])=>[a-l,b-l]));if(e.status!=='no-onset')c.push({...e,slot:l/STEP,at:h-1});}ck(eq(c,r.controls),'control rescan');
  for(const n of ['C','D']){const t=m.confirmed[n],p=n==='C'?C:scenario==='reused-sequence'?C:collisionD;ck(r.trace.some(e=>e.type==='receipt'&&e.at<t&&id(e.packet)===id(p)&&(n==='C'||e.at>=m.admitted)),'receipt precedes confirmation');}
  const file=`71-${scenario}-${policy}.wav`,bytes=wav(pcm);fs.writeFileSync(path.join(out,file),bytes);rows.push({...r,file,sha256:crypto.createHash('sha256').update(bytes).digest('hex'),samples:pcm.length});
 }
 fs.writeFileSync(path.join(out,'receipt.json'),JSON.stringify({schema:'mhac-sequence-v22',rate:16000,step:STEP,checks,rows,controls},null,2)+'\n');console.log(JSON.stringify({checks,rows:rows.map(({scenario,policy,metrics})=>({scenario,policy,metrics})),controls:controls.length},null,2));
}
