'use strict';
// Refs #512. Compact control experiment; fixed slot arbitration retained.
const compact=require('./compact-v20.cjs');
const {scan,request,STEP,SLOTS}=require('./clarify-v18.cjs');
const {render}=require('./bound-v2.cjs'),{base}=require('./relay.cjs');
const A={...base},B={...A,source:2,actor:3,event:2,seq:4,tree:['quote',['open']]};
const key=p=>JSON.stringify([p.source,p.version,p.actor,p.event,p.seq,p.tree]);
const scenarios=['gap','competition','late-forgery','early-forgery','replay','request-loss','persistent-gap'];
const policies=['compact'];
function run(scenario,policy,seed=71,chunk=511){
 if(!scenarios.includes(scenario)||!policies.includes(policy))throw Error('case');
 const pcm=new Int16Array(STEP*SLOTS),gaps=[],events=[],controlEvents=[],trace=[],records=new Map(),received=new Set(),acks=new Map(),hints=new Map();
 const m={data:0,ack:0,request:0,fixture:0,retries:0,genuine:0,false:0,honored:0,refused:0,first:{},occupancy:0};
 let slot=0,now=0,spent=false,bypasses=0;
 const log=(type,extra={})=>trace.push({at:now,slot,type,...extra});
 const offer=p=>records.set(key(p),{p,attempts:0,ready:slot,first:null,confirmed:false,accelerated:false});
 const valid=p=>p.version===2&&((p.source===1&&p.actor===2&&p.event===1)||(p.source===2&&p.actor===3&&p.event===2));
 function control(e){controlEvents.push(e);if(e.status!=='ok')return;now=e.at;const match=compact.resolve(e.token,[...records.values()].map(r=>r.p));const r=match.packet&&records.get(key(match.packet));let reason=match.status;if(r){reason='eligible';if(r.confirmed||r.attempts!==1||r.ready<=slot)reason='inactive';else if(r.accelerated)reason='duplicate';else if(e.at<(r.first+1)*STEP||e.at>=(r.first+4)*STEP)reason='expired';}if(reason==='eligible'){r.ready=slot+1;r.accelerated=true;m.honored++;}else m.refused++;log('compact-receipt',{token:e.token,reason,reference:match.packet||null});}
 function evidence(e){events.push(e);now=e.at;const p=e.packet;if(!p)return;const k=key(p);
  if(e.authority===false){if(e.status==='diagnostic-ok'&&p.kind===0&&valid(p)&&!received.has(k)&&!spent&&policy!=='timeout')hints.set(k,p);return;}
  if(e.status!=='ok')return;
  if(p.kind===0&&p.source===16){return;}
  if(p.kind===0&&valid(p)){received.add(k);hints.delete(k);acks.set(k,{...p,kind:1});log('receipt',{packet:p});return;}
  if(p.kind===1){const r=records.get(k);if(r&&r.attempts&&!r.confirmed){r.confirmed=true;if(received.has(k)){m.genuine++;m.first[p.source]=e.at;}else m.false++;log('confirmation',{packet:p,genuine:received.has(k)});}}
 }
 const reader=scan(pcm,gaps,evidence,chunk);offer(A);if(scenario==='competition')offer(B);
 for(slot=0;slot<SLOTS;slot++){now=slot*STEP;let p=null,controlTarget=null,origin='idle',fault='clean';
  const ready=[...records.values()].filter(r=>!r.confirmed&&r.attempts<2&&r.ready<=slot),fresh=ready.find(r=>r.attempts===0);
  const forged=(scenario==='early-forgery'&&slot===1)||(scenario==='late-forgery'&&slot===4)||(scenario==='replay'&&(slot===1||slot===2));
  if(forged){p=request(A);controlTarget=A;origin='fixture';m.fixture++;}
  else if(acks.size){const [k,a]=acks.entries().next().value;acks.delete(k);p=a;origin='ack';m.ack++;}
  else if(policy!=='timeout'&&!spent&&hints.size&&!(policy==='compact'&&fresh&&bypasses<1)){const [k,h]=hints.entries().next().value;hints.delete(k);p=request(h);controlTarget=h;origin='request';spent=true;m.request++;if(scenario==='request-loss')fault='lost';}
  else {const r=policy==='compact'?(fresh||ready[0]):ready[0];if(r){if(fresh===r&&hints.size&&!spent)bypasses++;p=r.p;origin='data';r.attempts++;if(r.first===null)r.first=slot;r.ready=slot+5;m.data++;if(r.attempts>1)m.retries++;if(['early-forgery','late-forgery','replay'].includes(scenario)&&r.attempts===1)fault='lost';}}
  const start=slot*STEP+64;if(p){let a=(controlTarget?compact.render(controlTarget,(seed%997)*.013+slot*.19):render(p,(seed%997)*.013+slot*.19));m.occupancy+=a.length;if(fault==='lost')a.fill(0);pcm.set(a,start);
   if(origin==='data'&&p.source===1&&((slot===0&&['gap','competition','request-loss'].includes(scenario))||scenario==='persistent-gap'))for(const off of [1036,2316,3596]){const l=start+off;gaps.push([l,l+16]);pcm.fill(0,l,l+16);}}
  log('tx',{packet:p,origin,fault,controlTarget});reader.feed((slot+1)*STEP);const l=slot*STEP,h=(slot+1)*STEP;const e=compact.acquire(pcm.subarray(l,h),gaps.filter(([a,b])=>a<h&&b>l).map(([a,b])=>[a-l,b-l]));if(e.status!=='no-onset')control({...e,slot,at:h-1});
 }reader.finish();return {scenario,policy,seed,step:STEP,samples:pcm.length,gaps,events,controlEvents,trace,metrics:m,pcm};
}
module.exports={run,scenarios,policies};
