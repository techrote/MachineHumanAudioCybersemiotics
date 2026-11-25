/* Interaction #456 Run 010: opportunistic metacommunication. Additive fork of timing-advert.js at 52b72a2a6c76ba084dab6291cbeb5f97c7ac45b1, blob c75a726e5f3a4ec525087a7b1009f3db3620fe41. Synthetic event oracle; illustrative PCM only. */
const Lab=(function makeLab(){
"use strict";
const lifetimes=["fixed","static","learned","learned-cap","matched","advert","advert-sticky","advert-cap","advert-event","advert-idle","advert-opportunistic","advert-hybrid"];const agents=["pump","fan","relay"],policies=["free","data-first","ack-first","alternate","reserve","fresh-first"],names=["light","overload","bursty","tight"],tickMs=250,cap=6,ttl=8;
function config(name){const profiles={light:[17,11,19],overload:[3,2,4],bursty:[11,5,13],tight:[40,2,40]};if(!Object.hasOwn(profiles,name))throw Error("scenario");return {name,horizon:40,periods:profiles[name].slice(),phases:[0,1,0],deadlines:name==="tight"?[12,2,12]:[20,6,20],priorities:[0,2,1],dataLoss:20,ackLoss:30,timeout:4,delay:2,batch:4,seed:1105}}
function validate(c,p,until,manual){if(!c||!Number.isInteger(c.delay)||c.delay<0||c.delay>12||!Number.isInteger(c.batch)||c.batch<1||c.batch>8)throw Error("return timing");if(!c||!policies.includes(p)||!Number.isInteger(c.horizon)||c.horizon<1||c.horizon>400||!Number.isInteger(until)||until<0||until>c.horizon||!Number.isInteger(c.seed)||c.seed<0||c.seed>0xffffffff||!Number.isInteger(c.timeout)||c.timeout<2||c.timeout>40)throw Error("configuration");for(const [k,lo,hi] of [["periods",1,400],["phases",0,400],["deadlines",1,400],["priorities",0,2]])if(!Array.isArray(c[k])||c[k].length!==3||c[k].some(x=>!Number.isInteger(x)||x<lo||x>hi))throw Error(k);for(const k of ["dataLoss","ackLoss"])if(!Number.isInteger(c[k])||c[k]<0||c[k]>100)throw Error(k);if(!Array.isArray(manual)||manual.length>400||manual.some(e=>!e||!Number.isInteger(e.t)||e.t<0||e.t>=c.horizon||!["offer","drop-data","drop-ack","drop-advert"].includes(e.op)||(e.op==="offer"&&!agents.includes(e.agent))))throw Error("manual")}
function simulate(c,p,until=c.horizon,manual=[]){
 validate(c,p,until,manual);const mode=c.lifetime??"fixed";if(!lifetimes.includes(mode))throw Error("lifetime");const guess=c.guess??2,senderBatch=c.senderBatch??4,change=c.change??null;
 if(!Number.isInteger(guess)||guess<0||guess>12||!Number.isInteger(senderBatch)||senderBatch<1||senderBatch>8||change!==null&&(!Number.isInteger(change.tick)||change.tick<0||change.tick>c.horizon||!Number.isInteger(change.delay)||change.delay<0||change.delay>12))throw Error("endpoint timing");
 const actualDelay=t=>change&&t>=change.tick?change.delay:c.delay;
 const readyTTL=true;let estimate=guess+senderBatch;
 const advertise=mode.startsWith("advert"),period=c.advertPeriod??16,validity=c.advertTTL??24,adLoss=c.advertLoss??0;
 if(!Number.isInteger(period)||period<1||period>400||!Number.isInteger(validity)||validity<1||validity>400||!Number.isInteger(adLoss)||adLoss<0||adLoss>100||advertise&&p==="free")throw Error("advert configuration");
 const passive=mode.startsWith("learned")||mode==="advert-hybrid";
 const opportunistic=mode==="advert-opportunistic"||mode==="advert-hybrid";
 let pendingAd=null,cache=null,adSeq=0,epoch=0;
 const records=[],trace=[],segments=[],q=[null,null,null],cur=[null,null,null],debt=[0,0,0],seq=[0,0,0],acks=[],free=[];
 let active=null,last="ack";
 const log=(t,type,r,extra={})=>trace.push({t,type,id:r.id,agent:r.agent,...extra});
 function queueAd(t){const urgent=t===0||!!(change&&t===change.tick);if(change&&t===change.tick)epoch++;
 if(opportunistic&&pendingAd&&pendingAd.urgent&&!urgent&&pendingAd.expires>=t+1)return;
 const a={id:"timing:"+ ++adSeq,agent:"relay",i:-1,epoch,seq:adSeq,created:t,expires:t+validity,delay:actualDelay(t),batch:c.batch,...(opportunistic?{urgent}:{})};if(pendingAd)log(t,"advert-replaced",pendingAd);pendingAd=a;log(t,"advert-queued",a,{epoch:a.epoch,seq:a.seq,delay:a.delay,batch:a.batch,expires:a.expires})}
 function finishAd(t,a){let x=(c.seed^Math.imul(a.seq,0x7feb352d)^0x6ad17)>>>0;x^=x>>>16;x=Math.imul(x,0x846ca68b);x^=x>>>16;const drop=manual.some(e=>e.t===t-1&&e.op==="drop-advert")||(x>>>0)%100<adLoss;log(t,"advert-complete",a,{lost:drop,epoch:a.epoch,seq:a.seq});if(!drop&&t<=a.expires&&(!cache||a.seq>cache.seq)){cache=a;log(t,"advert-accepted",a,{epoch:a.epoch,seq:a.seq,delay:a.delay,batch:a.batch,expires:a.expires})}}
 function offer(t,i){const r={id:agents[i]+":"+ ++seq[i],i,agent:agents[i],version:seq[i],arrived:t,deadline:t+c.deadlines[i],priority:c.priorities[i],attempts:0,received:null,confirmed:null,timeout:null};if(q[i])log(t,"coalesced",q[i]);if(cur[i])log(t,"superseded",cur[i],{by:r.id});cur[i]=q[i]=r;records.push(r);log(t,"offer",r)}
 function lost(r,kind,attempt,t){if(manual.some(e=>e.t===t&&e.op==="drop-"+kind))return true;let x=(c.seed^Math.imul(r.i+1,0x9e3779b1)^Math.imul(r.version,0x85ebca6b)^Math.imul(attempt,0xc2b2ae35)^(kind==="ack"?0x52da9a31:0))>>>0;x^=x>>>16;x=Math.imul(x,0x7feb352d);x^=x>>>15;x=Math.imul(x,0x846ca68b);x^=x>>>16;return (x>>>0)%100<c[kind+"Loss"]}
 function enqueueAck(t,r){const due=Math.ceil((t+actualDelay(t))/c.batch)*c.batch;const a={r,attempt:r.attempts,created:t,ready:due,expires:(readyTTL?due:t)+ttl};if(p==="free"){free.push({...a,due:Math.max(t+1,due)});log(t,"ack-queued",r,{attempt:a.attempt,ready:a.due??Math.max(t+1,due)});return}const existing=acks.find(x=>x.r===r);if(existing){log(t,"ack-coalesced",r);if(mode==="renew"){existing.expires=Math.max(existing.expires,a.expires);existing.attempt=a.attempt;log(t,"ack-queued",r,{attempt:existing.attempt,ready:existing.ready,expires:existing.expires,renewed:true})}return}if(acks.length===cap){const old=acks.shift();log(t,"ack-overflow",old.r)}acks.push(a);log(t,"ack-queued",r,{attempt:a.attempt,ready:a.ready,expires:a.expires})}
 function receiveAck(t,a){const r=a.r,drop=lost(r,"ack",a.attempt,t-1);log(t,"ack-complete",r,{attempt:a.attempt,lost:drop,free:p==="free"});if(drop)return;if(r.confirmed!==null){log(t,"ack-duplicate",r);return}r.confirmed=t;r.timeout=null;if(passive&&r.attempts===1&&a.attempt===1){const sample=t-r.firstFinish,before=estimate;estimate=Math.min(40,Math.max(1,Math.ceil((estimate+sample)/2)));log(t,"timing-learned",r,{sample,before,after:estimate});}if(q[r.i]===r){q[r.i]=null;log(t,"retry-cancelled",r)}log(t,"confirmed",r,{current:cur[r.i]===r&&t<=r.deadline})}
 function finishData(t,r){const drop=lost(r,"data",r.attempts,t-1),ok=!drop&&cur[r.i]===r&&t<=r.deadline;log(t,"data-complete",r,{attempt:r.attempts,lost:drop,ok});if(ok){if(r.received===null){r.received=t;log(t,"received",r)}else log(t,"data-duplicate",r);enqueueAck(t,r)}if(r.confirmed===null&&r.attempts===1){r.firstFinish=t;let due=t+c.timeout;if(mode==="static")due=Math.max(due,Math.ceil((t+guess)/senderBatch)*senderBatch+2);if(mode==="matched")due=Math.max(due,Math.ceil((t+actualDelay(t))/c.batch)*c.batch+2);if(mode.startsWith("learned"))due=Math.max(due,t+estimate+1);if(mode==="learned-cap")due=Math.max(t+1,Math.min(due,r.deadline-2));if(advertise){const usable=cache&&(mode==="advert-sticky"||t<=cache.expires);const d=usable?cache.delay:guess,b=usable?cache.batch:senderBatch;due=mode==="advert-hybrid"&&!usable?Math.max(t+c.timeout,t+estimate+1):Math.max(t+c.timeout,Math.ceil((t+d)/b)*b+2);if(mode==="advert-cap")due=Math.max(t+1,Math.min(due,r.deadline-2));log(t,"timing-used",r,{from:usable?cache.id:"fallback",epoch:usable?cache.epoch:null,stale:!!usable&&cache.epoch!==(change&&t>=change.tick?1:0),expired:!!usable&&t>cache.expires,delay:d,batch:b,...(mode==="advert-hybrid"&&!usable?{learnedFallback:estimate}:{})});}r.timeout=due;log(t,"timeout-set",r,{due,estimate:mode.startsWith("learned")?estimate:null});}debt[r.i]=0}
 for(let t=0;t<=until;t++){
  for(let j=free.length-1;j>=0;j--)if(free[j].due===t)receiveAck(t,free.splice(j,1)[0]);
  if(t===until)break;
  if(advertise){if(t===0||change&&t===change.tick||mode!=="advert-event"&&t%period===0)queueAd(t);if(pendingAd&&pendingAd.expires<t+1){log(t,"advert-expired",pendingAd);pendingAd=null}}
  for(let i=0;i<3;i++)if(t>=c.phases[i]&&(t-c.phases[i])%c.periods[i]===0)offer(t,i);
  for(const e of manual)if(e.t===t&&e.op==="offer")offer(t,agents.indexOf(e.agent));
  for(const r of records)if(r.timeout===t){r.timeout=null;log(t,"timeout",r);if(r.confirmed===null&&r.attempts===1&&cur[r.i]===r&&!q[r.i]&&r.deadline-t>=2){q[r.i]=r;log(t,"retry-queued",r)}else log(t,"retry-unavailable",r)}
  for(let j=acks.length-1;j>=0;j--)if(acks[j].expires-t<1){log(t,"ack-expired",acks[j].r);acks.splice(j,1)}
  for(let i=0;i<3;i++){if(q[i]&&q[i].deadline-t<2){log(t,"data-expired",q[i]);q[i]=null}if(!q[i]&&active?.r.i!==i)debt[i]=0}
  if(!active){
    const ids=[0,1,2].filter(i=>q[i]).sort((i,j)=>(4*q[j].priority+debt[j])-(4*q[i].priority+debt[i])||q[i].arrived-q[j].arrived||i-j);
    const ready=acks.filter(a=>a.ready<=t);const fresh=a=>cur[a.r.i]===a.r&&a.r.deadline>=t+1;if(p==="fresh-first")ready.sort((a,b)=>Number(fresh(b))-Number(fresh(a))||a.created-b.created);const takeAck=ready.length&&(ids.length===0||p==="ack-first"||p==="fresh-first"||(p==="alternate"&&last==="data")||(p==="reserve"&&(t%4===0||t%4===3)));
    if(takeAck){const a=ready[0];acks.splice(acks.indexOf(a),1);active={kind:"ack",r:a.r,a,part:0};log(t,"ack-start",a.r,{attempt:a.attempt})}
    else if(pendingAd&&(ids.length===0||(mode!=="advert-idle"&&(!opportunistic||pendingAd.urgent)&&(p==="ack-first"||p==="fresh-first"||p==="reserve"&&(t%4===0||t%4===3)||p==="alternate"&&last==="data")))){const a=pendingAd;pendingAd=null;active={kind:"advert",r:a,a,part:0};log(t,"advert-start",a,{epoch:a.epoch,seq:a.seq})}
    else if(ids.length){const i=ids[0],r=q[i];q[i]=null;r.attempts++;active={kind:"data",r,part:0};log(t,"data-start",r,{attempt:r.attempts})}
  }
  for(let i=0;i<3;i++)if(q[i]&&!(active?.kind==="data"&&active.r.i===i))debt[i]++;
  if(!active){segments.push({t,kind:"idle",id:null});continue}
  const {r,kind,part,a}=active;segments.push({t,kind,id:r.id,agent:r.agent,attempt:kind==="advert"?1:kind==="ack"?a.attempt:r.attempts,part,...(kind==="advert"?{epoch:a.epoch,delay:a.delay,batch:a.batch}:{})});active.part++;
  if(active.part===(kind==="data"?2:1)){last=kind;active=null;if(kind==="ack")receiveAck(t+1,a);else if(kind==="advert")finishAd(t+1,a);else finishData(t+1,r)}
 }
 const metrics={offered:records.length,received:records.filter(r=>r.received!==null).length,confirmed:records.filter(r=>r.confirmed!==null).length,currentConfirmed:cur.filter(r=>r&&r.confirmed!==null&&until<=r.deadline).length,freshAtAck:trace.filter(e=>e.type==="confirmed"&&e.current).length,unconfirmed:records.filter(r=>r.received!==null&&r.confirmed===null).length,retries:records.filter(r=>r.attempts===2).length,duplicates:trace.filter(e=>e.type==="data-duplicate").length,ackLost:trace.filter(e=>e.type==="ack-complete"&&e.lost).length,ackDiscarded:trace.filter(e=>["ack-overflow","ack-expired"].includes(e.type)).length,dataTicks:segments.filter(s=>s.kind==="data").length,ackTicks:segments.filter(s=>s.kind==="ack").length,advertTicks:segments.filter(s=>s.kind==="advert").length,advertAccepted:trace.filter(e=>e.type==="advert-accepted").length,staleUses:trace.filter(e=>e.type==="timing-used"&&e.stale).length,expiredUses:trace.filter(e=>e.type==="timing-used"&&e.expired).length,freeAcks:trace.filter(e=>e.type==="ack-complete"&&e.free).length,byAgent:agents.map(a=>records.filter(r=>r.agent===a&&r.received!==null).length)};
 return {schema:"mhac-opportunistic-timing-v1",config:c,policy:p,until,manual,records,trace,segments,metrics,pending:{advert:pendingAd,cache,data:q.map(r=>r?.id??null),ack:acks.map(a=>({id:a.r.id,ready:a.ready,expires:a.expires,attempt:a.attempt})),free:free.map(a=>({id:a.r.id,due:a.due,attempt:a.attempt})),active:active?{kind:active.kind,id:active.r.id,part:active.part}:null}}
}
function render(segments){const rate=8000,n=2000,bytes=new Uint8Array(44+segments.length*n*2),d=new DataView(bytes.buffer);function ascii(at,s){for(let i=0;i<s.length;i++)bytes[at+i]=s.charCodeAt(i)}ascii(0,"RIFF");d.setUint32(4,bytes.length-8,true);ascii(8,"WAVEfmt ");d.setUint32(16,16,true);d.setUint16(20,1,true);d.setUint16(22,1,true);d.setUint32(24,rate,true);d.setUint32(28,rate*2,true);d.setUint16(32,2,true);d.setUint16(34,16,true);ascii(36,"data");d.setUint32(40,bytes.length-44,true);let peak=0;for(const s of segments){if(s.kind==="idle")continue;const i=agents.indexOf(s.agent),f=s.kind==="advert"?700+25*s.delay:s.kind==="ack"?1000+150*i:360+120*i+90*s.part;for(let j=0;j<n;j++){const env=Math.min(1,j/100,(n-1-j)/100),v=Math.round(32767*.065*env*Math.sin(2*Math.PI*f*j/rate));peak=Math.max(peak,Math.abs(v));d.setInt16(44+2*(s.t*n+j),v,true)}}return {bytes,peak,rate}}


/* At each integer tick after offers, a confirmation counts only while the exact
 * version is current and within its inclusive deadline. No lookahead in policy:
 * this retrospective metric uses the full trace for evaluation only. */
function freshness(r){
 let ticks=0,available=0,perAgent=[0,0,0],last=[null,null,null];
 for(let t=0;t<r.until;t++){
  for(let i=0;i<3;i++){for(const x of r.records)if(x.i===i&&x.arrived===t)last[i]=x;
   const x=last[i];if(x&&x.deadline>=t){available++;if(x.confirmed!==null&&x.confirmed<=t){ticks++;perAgent[i]++}}
  }
 }return {ticks,available,perAgent};
}

function qualify(){
 const modes=["static","learned","advert","advert-event","advert-idle","advert-opportunistic","advert-hybrid"],groups={},witnesses={};
 const keys=["offered","received","confirmed","retries","dataTicks","ackTicks","advertTicks","advertAccepted","staleUses","expiredUses","freshTicks","available"];
 let assertions=0,runs=0;const check=(v,msg)=>{assertions++;if(!v)throw Error(msg)};
 function verify(r){runs++;const m=r.metrics,f=freshness(r),starts=r.trace.filter(e=>e.type==="advert-start"),accepts=r.trace.filter(e=>e.type==="advert-accepted");
 check(r.segments.length===r.until&&r.segments.every((s,i)=>s.t===i),"timeline");
 check(m.dataTicks+m.ackTicks+m.advertTicks<=r.until,"half duplex");check(m.confirmed+m.unconfirmed===m.received,"receipt accounting");check(f.ticks<=f.available,"freshness");check(r.pending.ack.length<=cap,"bounded ACK queue");
 check(starts.length===m.advertTicks,"control airtime");
 for(const x of r.records){check(x.attempts<=2,"bounded attempts");check(x.received===null||x.received<=x.deadline,"deadline");check(x.confirmed===null||x.received!==null&&x.confirmed>=x.received&&x.confirmed<=r.until,"confirmation provenance")}
 for(let i=0;i<accepts.length;i++){const e=accepts[i];check(i===0||e.seq>accepts[i-1].seq,"monotonic cache");check(e.t<=e.expires&&r.trace.some(x=>x.type==="advert-complete"&&x.id===e.id&&x.t===e.t&&!x.lost),"accepted control provenance")}
 for(const e of r.trace.filter(e=>e.type==="timing-used"&&e.from!=="fallback"))check(!e.expired&&accepts.some(x=>x.id===e.from&&x.t<=e.t),"causal unexpired cache");
 if(r.config.lifetime==="advert-event")check(r.trace.filter(e=>e.type==="advert-queued").length<=2,"event only");
 const queued=new Set();
 for(const e of r.trace){if(e.type==="offer"||e.type==="retry-queued")queued.add(e.id);if(["coalesced","data-start","data-expired","retry-cancelled"].includes(e.type))queued.delete(e.id);
 if(e.type==="advert-start"){const source=r.trace.find(x=>x.type==="advert-queued"&&x.id===e.id);const urgent=source.t===0||source.t===r.config.change?.tick;
 if(r.config.lifetime==="advert-idle"||(["advert-opportunistic","advert-hybrid"].includes(r.config.lifetime)&&!urgent))check(queued.size===0,"idle-only did not displace queued DATA");}}
 return {...m,freshTicks:f.ticks,available:f.available};
 }
 const regimes=[["slow",12,0,null],["fast",0,12,null],["slowdown",2,2,{tick:40,delay:12}],["speedup",12,12,{tick:40,delay:2}]];
 for(const [name,delay,guess,change] of regimes){groups[name]={};for(const loss of [0,60])for(const p of ["ack-first","reserve"]){const g=groups[name][loss+"-"+p]=Object.fromEntries(modes.map(m=>[m,Object.fromEntries(keys.map(k=>[k,0]))]));
 for(const world of names)for(const dataLoss of [0,30])for(const ackLoss of [0,60])for(const seed of [63809,78191])for(const lifetime of modes){const m=verify(simulate({...config(world),horizon:80,delay,guess,change,dataLoss,ackLoss,seed,lifetime,advertLoss:loss},p));for(const k of keys)g[lifetime][k]+=m[k]}}}
 const single={...config("light"),horizon:48,periods:[400,400,400],phases:[0,400,400],deadlines:[48,48,48],dataLoss:0,ackLoss:0,timeout:3,delay:12,guess:0,advertPeriod:8,advertTTL:24};
 for(const lifetime of modes){const q=simulate({...single,lifetime},"ack-first",48,[{t:0,op:"drop-advert"},{t:8,op:"offer",agent:"relay"},{t:24,op:"offer",agent:"pump"}]);verify(q);witnesses[lifetime]=q}
 check(witnesses["advert-event"].metrics.advertAccepted===0,"lost sole event remains lost");
 check(witnesses["advert-opportunistic"].metrics.advertAccepted>0,"idle refresh repairs initial loss");
 const step={...config("overload"),horizon:80,delay:2,guess:2,change:{tick:40,delay:12},dataLoss:0,ackLoss:0};
 for(const lifetime of ["advert","advert-event","advert-idle","advert-opportunistic","advert-hybrid"]){const q=simulate({...step,lifetime},"reserve");verify(q);witnesses["overload-"+lifetime]=q}
 let peak=0;for(const q of Object.values(witnesses)){const w=render(q.segments);peak=Math.max(peak,w.peak);check(w.peak<=2130&&w.bytes.length===44+4000*q.until,"WAV bounds");check(JSON.stringify(q)===JSON.stringify(simulate(q.config,q.policy,q.until,q.manual)),"deterministic replay");const prefix=simulate(q.config,q.policy,Math.floor(q.until/2),q.manual);check(JSON.stringify(prefix.segments)===JSON.stringify(q.segments.slice(0,prefix.until)),"causal prefix")}
 return {schema:"mhac-opportunistic-timing-evaluation-v1",parent:"52b72a2a6c76ba084dab6291cbeb5f97c7ac45b1",seeds:[63809,78191],assertions,runs,groups,peak,witnesses,limits:"Synthetic trusted symbolic delivery, shared clock, fixed slot sizes. Idle-only refers to absence of queued DATA after ACK arbitration. No piggybacking, waveform decoding, human evidence, authentication or physical device control."};
}
return {agents,policies,names,lifetimes,tickMs,config,simulate,render,freshness,qualify}
})();
if(typeof module==="object"&&module.exports){
 module.exports=Lab;
 if(require.main===module){
 const fs=require("node:fs"),path=require("node:path"),crypto=require("node:crypto"),out=process.argv[2]||"opportunistic-output";fs.mkdirSync(out,{recursive:true});
 const q=Lab.qualify(),manifest=[];for(const [name,r] of Object.entries(q.witnesses)){const w=Lab.render(r.segments);fs.writeFileSync(path.join(out,name+".wav"),w.bytes);fs.writeFileSync(path.join(out,name+".json"),JSON.stringify(r,null,2)+"\n");manifest.push({name,sha256:crypto.createHash("sha256").update(w.bytes).digest("hex"),peak:w.peak,rate:w.rate})}
 fs.writeFileSync(path.join(out,"qualification.json"),JSON.stringify(q,null,2)+"\n");fs.writeFileSync(path.join(out,"stimuli.json"),JSON.stringify(manifest,null,2)+"\n");
 fs.copyFileSync(__filename,path.join(out,"opportunistic.js"));fs.writeFileSync(path.join(out,"index.html"),gallery());
 console.log(JSON.stringify({assertions:q.assertions,runs:q.runs,peak:q.peak,stimuli:manifest.length}));
 }
}else globalThis.OpportunisticLab=Lab;
function gallery(){return '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Situated Relay — Opportunistic Timing</title><style>body{font:16px system-ui;max-width:850px;margin:2em auto;padding:0 1em;color:#172334;background:#f4f6f8}label{display:block;margin:.5em 0}button,select,input{font:inherit}pre{white-space:pre-wrap;background:white;padding:1em}audio{width:100%}</style><h1>Situated Relay: opportunistic timing</h1><p>Synthetic event reception; audio illustrates occupied slots, not decoded fields. No autoplay. Start with low playback volume.</p><label>World <select id="world"><option>light</option><option>overload</option><option>bursty</option><option>tight</option></select></label><label>Policy <select id="policy"><option>reserve</option><option>ack-first</option></select></label><label>Timing <select id="mode"><option>static</option><option>learned</option><option>advert</option><option>advert-event</option><option>advert-idle</option><option>advert-opportunistic</option><option selected>advert-hybrid</option></select></label><label>Announcement loss % <input id="loss" type="number" min="0" max="100" value="60"></label><label>Receiver step <select id="step"><option value="slowdown">2 → 12 ticks</option><option value="speedup">12 → 2 ticks</option></select></label><button id="run">Simulate / render</button> <a id="trace">Export trace</a><p id="status"></p><audio controls id="audio"></audio><pre id="metrics"></pre><pre id="timeline"></pre><script src="opportunistic.js"></script><script>const $=id=>document.getElementById(id);let urls=[];function run(){try{$("audio").pause();urls.forEach(URL.revokeObjectURL);urls=[];const L=OpportunisticLab,slow=$("step").value==="slowdown",delay=slow?2:12,c={...L.config($("world").value),horizon:80,delay,guess:delay,change:{tick:40,delay:slow?12:2},seed:63809,lifetime:$("mode").value,advertLoss:Number($("loss").value)};const r=L.simulate(c,$("policy").value);const w=L.render(r.segments),url=URL.createObjectURL(new Blob([w.bytes],{type:"audio/wav"})),tr=URL.createObjectURL(new Blob([JSON.stringify(r,null,2)],{type:"application/json"}));urls=[url,tr];$("audio").src=url;$("audio").volume=.2;$("trace").href=tr;$("trace").download="trace.json";$("metrics").textContent=JSON.stringify({...r.metrics,freshness:L.freshness(r)},null,2);$("timeline").textContent=r.segments.map(s=>s.t+" "+s.kind+" "+(s.id||"")).join("\\n");$("status").textContent="Rendered "+r.until+" ticks; digital peak "+w.peak+"/32768."}catch(e){$("status").textContent=e.message}}$("run").onclick=run;run();</script></html>'}
