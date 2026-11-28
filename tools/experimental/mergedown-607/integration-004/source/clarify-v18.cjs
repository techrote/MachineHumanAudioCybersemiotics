'use strict';
// Refs #512. Isolated experimental slot scheduler; source 16 is reserved here only.
const {PartialReceiver}=require('./partial-v15.cjs'),{render}=require('./bound-v2.cjs'),{base}=require('./relay.cjs');
const STEP=33600, SLOTS=9, A={...base}, B={...A,source:2,actor:3,event:2,seq:4,tree:['quote',['open']]}, A3={...A,version:3,seq:5};
const key=p=>JSON.stringify([p.source,p.version,p.actor,p.event,p.seq,p.tree]);
const request=p=>({...p,kind:0,source:16,actor:p.source});
const cases=['clean','gap','request-loss','persistent-gap','revision','forged-request','wrong-request','forged-ack','competition','noise','drift'];
function scan(pcm,gaps,emit,chunk=511){const r=new PartialReceiver(emit);let at=0,j=0;return {feed(end){while(at<end){const g=gaps[j];if(g&&at===g[0]){if(g[1]>end)throw Error('gap crosses feed boundary');r.gap(g[1]-g[0]);at=g[1];j++;}else{const n=Math.min(end,at+chunk,g?.[0]??end);if(n<=at)throw Error('unordered gap');r.push(pcm.subarray(at,n));at=n;}}},finish(){r.finish();}};}
function run(scenario,policy,seed=71,chunk=511){if(!cases.includes(scenario)||!['timeout','clarify'].includes(policy))throw Error('case');
 const pcm=new Int16Array(STEP*SLOTS),gaps=[],events=[],trace=[],records=new Map(),received=new Set(),ack=new Map(),hints=new Map(),current=new Map([[1,2],[2,2]]);
 let spent=0,slot=0,now=0;const m={data:0,ack:0,request:0,fixture:0,retries:0,unique:0,confirmed:0,genuine:0,false:0,requestsDecoded:0,requestsHonored:0,requestsRefused:0,hints:0,firstGenuine:null,occupancy:0};
 const log=(type,extra={})=>trace.push({at:now,type,...extra});
 function offer(p){records.set(key(p),{p,attempts:0,ready:slot,confirmed:false});log('offer',{packet:p});}
 const valid=p=>p.version===current.get(p.source)&&((p.source===1&&p.actor===2&&p.event===1)||(p.source===2&&p.actor===3&&p.event===2));
 function evidence(e){events.push(e);now=e.at;const p=e.packet;if(!p)return;const k=key(p);
   if(e.authority===false){if(e.status==='diagnostic-ok'&&p.kind===0&&valid(p)&&!received.has(k)){m.hints++;log('hint',{packet:p,authority:false});if(policy==='clarify'&&spent===0&&!hints.has(k))hints.set(k,p);}return;}
   if(e.status!=='ok')return;
   if(p.kind===0&&p.source===16){m.requestsDecoded++;const r=[...records.values()].find(r=>key(request(r.p))===k);const ok=!!r&&valid(r.p)&&r.attempts===1&&!r.confirmed&&r.ready>slot&&policy==='clarify';if(ok){r.ready=slot+1;m.requestsHonored++;}else m.requestsRefused++;log('request-receipt',{packet:p,honored:ok});return;}
   if(p.kind===0&&valid(p)){if(!received.has(k)){received.add(k);m.unique++;}hints.delete(k);ack.set(k,{...p,kind:1});log('receipt',{packet:p});return;}
   if(p.kind===1){const r=records.get(k);if(r&&r.attempts&&!r.confirmed&&valid(r.p)){r.confirmed=true;m.confirmed++;const genuine=received.has(k);if(genuine){m.genuine++;if(m.firstGenuine===null)m.firstGenuine=e.at;}else m.false++;log('confirmation',{packet:p,evaluatorGenuine:genuine});}}
 }
 const s=scan(pcm,gaps,evidence,chunk);offer(A);if(scenario==='competition')offer(B);
 for(slot=0;slot<SLOTS;slot++){now=slot*STEP;if(scenario==='revision'&&slot===1){current.set(1,3);offer(A3);}for(const [k,p] of hints)if(!valid(p)||received.has(k))hints.delete(k);for(const [k,p] of ack)if(!valid(p))ack.delete(k);
  let p=null,origin='idle',fault='clean';
  if(slot===1&&['forged-request','wrong-request','forged-ack'].includes(scenario)){p=scenario==='forged-ack'?{...A,kind:1}:request({...A,seq:scenario==='wrong-request'?7:A.seq});origin='fixture';m.fixture++;}
  else if(ack.size){const [k,a]=ack.entries().next().value;ack.delete(k);p=a;origin='ack';m.ack++;}
  else if(policy==='clarify'&&spent===0&&hints.size){const [k,h]=hints.entries().next().value;hints.delete(k);p=request(h);origin='request';spent++;m.request++;if(scenario==='request-loss')fault='lost';}
  else {const r=[...records.values()].find(r=>valid(r.p)&&!r.confirmed&&r.attempts<2&&r.ready<=slot);if(r){p=r.p;origin='data';r.attempts++;r.ready=slot+5;m.data++;if(r.attempts>1)m.retries++;if(['forged-ack','forged-request','wrong-request'].includes(scenario)&&r.attempts===1)fault='lost';if(scenario==='drift'&&r.attempts===1)fault='drift';if(scenario==='noise'&&r.attempts===1)fault='noise';}}
  const start=slot*STEP+64;if(p){m.occupancy+=31360;let a=render(p,(seed%997)*.013+slot*.19);if(fault==='lost')a.fill(0);if(fault==='drift'){const b=a;a=Int16Array.from({length:Math.round(b.length*1.009)},(_,i)=>b[Math.floor(i/1.009)]);m.occupancy+=a.length-31360;}if(fault==='noise'){let z=seed;for(let i=0;i<a.length;i++){z=(Math.imul(z,1664525)+1013904223)>>>0;a[i]+=Math.round((z/4294967296*2-1)*900);}}pcm.set(a,start);
   if(origin==='data'&&p.source===1&&p.version===2&&(['gap','request-loss','revision','competition'].includes(scenario)&&slot===0||scenario==='persistent-gap'))for(const off of [1036,2316,3596]){const l=start+off;gaps.push([l,l+16]);pcm.fill(0,l,l+16);}}
  log('tx',{packet:p,origin,fault,slot});s.feed((slot+1)*STEP);
 }s.finish();return {scenario,policy,seed,step:STEP,samples:pcm.length,gaps,events,trace,metrics:m,pcm};
}
module.exports={run,scan,cases,request,STEP,SLOTS};
