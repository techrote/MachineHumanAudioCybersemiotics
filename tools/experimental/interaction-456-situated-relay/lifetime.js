/* Interaction lane #456 Run 007. Additive fork of return-window.js at cc4aad9db4862af40709d3272bc3c915e3224325. Synthetic receipt oracle; no human evidence. */
const Lab=(function makeLab(){
"use strict";
const lifetimes=["fixed","ready-ttl","timing-only","combined","renew"];const agents=["pump","fan","relay"],policies=["free","data-first","ack-first","alternate","reserve","fresh-first"],names=["light","overload","bursty","tight"],tickMs=250,cap=6,ttl=8;
function config(name){const profiles={light:[17,11,19],overload:[3,2,4],bursty:[11,5,13],tight:[40,2,40]};if(!Object.hasOwn(profiles,name))throw Error("scenario");return {name,horizon:40,periods:profiles[name].slice(),phases:[0,1,0],deadlines:name==="tight"?[12,2,12]:[20,6,20],priorities:[0,2,1],dataLoss:20,ackLoss:30,timeout:4,delay:2,batch:4,seed:1105}}
function validate(c,p,until,manual){if(!c||!Number.isInteger(c.delay)||c.delay<0||c.delay>12||!Number.isInteger(c.batch)||c.batch<1||c.batch>8)throw Error("return timing");if(!c||!policies.includes(p)||!Number.isInteger(c.horizon)||c.horizon<1||c.horizon>400||!Number.isInteger(until)||until<0||until>c.horizon||!Number.isInteger(c.seed)||c.seed<0||c.seed>0xffffffff||!Number.isInteger(c.timeout)||c.timeout<2||c.timeout>40)throw Error("configuration");for(const [k,lo,hi] of [["periods",1,400],["phases",0,400],["deadlines",1,400],["priorities",0,2]])if(!Array.isArray(c[k])||c[k].length!==3||c[k].some(x=>!Number.isInteger(x)||x<lo||x>hi))throw Error(k);for(const k of ["dataLoss","ackLoss"])if(!Number.isInteger(c[k])||c[k]<0||c[k]>100)throw Error(k);if(!Array.isArray(manual)||manual.length>400||manual.some(e=>!e||!Number.isInteger(e.t)||e.t<0||e.t>=c.horizon||!["offer","drop-data","drop-ack"].includes(e.op)||(e.op==="offer"&&!agents.includes(e.agent))))throw Error("manual")}
function simulate(c,p,until=c.horizon,manual=[]){
 validate(c,p,until,manual);const mode=c.lifetime??"fixed";if(!lifetimes.includes(mode))throw Error("lifetime");const readyTTL=["ready-ttl","combined","renew"].includes(mode),timing=["timing-only","combined","renew"].includes(mode);
 const records=[],trace=[],segments=[],q=[null,null,null],cur=[null,null,null],debt=[0,0,0],seq=[0,0,0],acks=[],free=[];
 let active=null,last="ack";
 const log=(t,type,r,extra={})=>trace.push({t,type,id:r.id,agent:r.agent,...extra});
 function offer(t,i){const r={id:agents[i]+":"+ ++seq[i],i,agent:agents[i],version:seq[i],arrived:t,deadline:t+c.deadlines[i],priority:c.priorities[i],attempts:0,received:null,confirmed:null,timeout:null};if(q[i])log(t,"coalesced",q[i]);if(cur[i])log(t,"superseded",cur[i],{by:r.id});cur[i]=q[i]=r;records.push(r);log(t,"offer",r)}
 function lost(r,kind,attempt,t){if(manual.some(e=>e.t===t&&e.op==="drop-"+kind))return true;let x=(c.seed^Math.imul(r.i+1,0x9e3779b1)^Math.imul(r.version,0x85ebca6b)^Math.imul(attempt,0xc2b2ae35)^(kind==="ack"?0x52da9a31:0))>>>0;x^=x>>>16;x=Math.imul(x,0x7feb352d);x^=x>>>15;x=Math.imul(x,0x846ca68b);x^=x>>>16;return (x>>>0)%100<c[kind+"Loss"]}
 function enqueueAck(t,r){const due=Math.ceil((t+c.delay)/c.batch)*c.batch;const a={r,attempt:r.attempts,created:t,ready:due,expires:(readyTTL?due:t)+ttl};if(p==="free"){free.push({...a,due:Math.max(t+1,due)});log(t,"ack-queued",r,{attempt:a.attempt,ready:a.due??Math.max(t+1,due)});return}const existing=acks.find(x=>x.r===r);if(existing){log(t,"ack-coalesced",r);if(mode==="renew"){existing.expires=Math.max(existing.expires,a.expires);existing.attempt=a.attempt;log(t,"ack-queued",r,{attempt:existing.attempt,ready:existing.ready,expires:existing.expires,renewed:true})}return}if(acks.length===cap){const old=acks.shift();log(t,"ack-overflow",old.r)}acks.push(a);log(t,"ack-queued",r,{attempt:a.attempt,ready:a.ready,expires:a.expires})}
 function receiveAck(t,a){const r=a.r,drop=lost(r,"ack",a.attempt,t-1);log(t,"ack-complete",r,{attempt:a.attempt,lost:drop,free:p==="free"});if(drop)return;if(r.confirmed!==null){log(t,"ack-duplicate",r);return}r.confirmed=t;r.timeout=null;if(q[r.i]===r){q[r.i]=null;log(t,"retry-cancelled",r)}log(t,"confirmed",r,{current:cur[r.i]===r&&t<=r.deadline})}
 function finishData(t,r){const drop=lost(r,"data",r.attempts,t-1),ok=!drop&&cur[r.i]===r&&t<=r.deadline;log(t,"data-complete",r,{attempt:r.attempts,lost:drop,ok});if(ok){if(r.received===null){r.received=t;log(t,"received",r)}else log(t,"data-duplicate",r);enqueueAck(t,r)}if(r.confirmed===null&&r.attempts===1)r.timeout=timing?Math.max(t+c.timeout,Math.ceil((t+c.delay)/c.batch)*c.batch+2):t+c.timeout;debt[r.i]=0}
 for(let t=0;t<=until;t++){
  for(let j=free.length-1;j>=0;j--)if(free[j].due===t)receiveAck(t,free.splice(j,1)[0]);
  if(t===until)break;
  for(let i=0;i<3;i++)if(t>=c.phases[i]&&(t-c.phases[i])%c.periods[i]===0)offer(t,i);
  for(const e of manual)if(e.t===t&&e.op==="offer")offer(t,agents.indexOf(e.agent));
  for(const r of records)if(r.timeout===t){r.timeout=null;log(t,"timeout",r);if(r.confirmed===null&&r.attempts===1&&cur[r.i]===r&&!q[r.i]&&r.deadline-t>=2){q[r.i]=r;log(t,"retry-queued",r)}else log(t,"retry-unavailable",r)}
  for(let j=acks.length-1;j>=0;j--)if(acks[j].expires-t<1){log(t,"ack-expired",acks[j].r);acks.splice(j,1)}
  for(let i=0;i<3;i++){if(q[i]&&q[i].deadline-t<2){log(t,"data-expired",q[i]);q[i]=null}if(!q[i]&&active?.r.i!==i)debt[i]=0}
  if(!active){
    const ids=[0,1,2].filter(i=>q[i]).sort((i,j)=>(4*q[j].priority+debt[j])-(4*q[i].priority+debt[i])||q[i].arrived-q[j].arrived||i-j);
    const ready=acks.filter(a=>a.ready<=t);const fresh=a=>cur[a.r.i]===a.r&&a.r.deadline>=t+1;if(p==="fresh-first")ready.sort((a,b)=>Number(fresh(b))-Number(fresh(a))||a.created-b.created);const takeAck=ready.length&&(ids.length===0||p==="ack-first"||p==="fresh-first"||(p==="alternate"&&last==="data")||(p==="reserve"&&(t%4===0||t%4===3)));
    if(takeAck){const a=ready[0];acks.splice(acks.indexOf(a),1);active={kind:"ack",r:a.r,a,part:0};log(t,"ack-start",a.r,{attempt:a.attempt})}
    else if(ids.length){const i=ids[0],r=q[i];q[i]=null;r.attempts++;active={kind:"data",r,part:0};log(t,"data-start",r,{attempt:r.attempts})}
  }
  for(let i=0;i<3;i++)if(q[i]&&!(active?.kind==="data"&&active.r.i===i))debt[i]++;
  if(!active){segments.push({t,kind:"idle",id:null});continue}
  const {r,kind,part,a}=active;segments.push({t,kind,id:r.id,agent:r.agent,attempt:kind==="ack"?a.attempt:r.attempts,part});active.part++;
  if(active.part===(kind==="ack"?1:2)){last=kind;active=null;if(kind==="ack")receiveAck(t+1,a);else finishData(t+1,r)}
 }
 const metrics={offered:records.length,received:records.filter(r=>r.received!==null).length,confirmed:records.filter(r=>r.confirmed!==null).length,currentConfirmed:cur.filter(r=>r&&r.confirmed!==null&&until<=r.deadline).length,freshAtAck:trace.filter(e=>e.type==="confirmed"&&e.current).length,unconfirmed:records.filter(r=>r.received!==null&&r.confirmed===null).length,retries:records.filter(r=>r.attempts===2).length,duplicates:trace.filter(e=>e.type==="data-duplicate").length,ackLost:trace.filter(e=>e.type==="ack-complete"&&e.lost).length,ackDiscarded:trace.filter(e=>["ack-overflow","ack-expired"].includes(e.type)).length,dataTicks:segments.filter(s=>s.kind==="data").length,ackTicks:segments.filter(s=>s.kind==="ack").length,freeAcks:trace.filter(e=>e.type==="ack-complete"&&e.free).length,byAgent:agents.map(a=>records.filter(r=>r.agent===a&&r.received!==null).length)};
 return {schema:"mhac-return-window-v1",config:c,policy:p,until,manual,records,trace,segments,metrics,pending:{data:q.map(r=>r?.id??null),ack:acks.map(a=>({id:a.r.id,ready:a.ready,expires:a.expires,attempt:a.attempt})),free:free.map(a=>({id:a.r.id,due:a.due,attempt:a.attempt})),active:active?{kind:active.kind,id:active.r.id,part:active.part}:null}}
}
function render(segments){const rate=8000,n=2000,bytes=new Uint8Array(44+segments.length*n*2),d=new DataView(bytes.buffer);function ascii(at,s){for(let i=0;i<s.length;i++)bytes[at+i]=s.charCodeAt(i)}ascii(0,"RIFF");d.setUint32(4,bytes.length-8,true);ascii(8,"WAVEfmt ");d.setUint32(16,16,true);d.setUint16(20,1,true);d.setUint16(22,1,true);d.setUint32(24,rate,true);d.setUint32(28,rate*2,true);d.setUint16(32,2,true);d.setUint16(34,16,true);ascii(36,"data");d.setUint32(40,bytes.length-44,true);let peak=0;for(const s of segments){if(s.kind==="idle")continue;const i=agents.indexOf(s.agent),f=s.kind==="ack"?1000+150*i:360+120*i+90*s.part;for(let j=0;j<n;j++){const env=Math.min(1,j/100,(n-1-j)/100),v=Math.round(32767*.065*env*Math.sin(2*Math.PI*f*j/rate));peak=Math.max(peak,Math.abs(v));d.setInt16(44+2*(s.t*n+j),v,true)}}return {bytes,peak,rate}}


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
 let assertions=0,runs=0;const check=(x,m)=>{assertions++;if(!x)throw Error(m)};
 function verify(r){runs++;let m=r.metrics,f=freshness(r);
 check(r.segments.length===r.until,"timeline");check(m.dataTicks+m.ackTicks<=r.until,"channel budget");
 check(m.confirmed+m.unconfirmed===m.received,"accounting");check(m.freshAtAck<=m.confirmed,"fresh subset");
 check(r.pending.ack.length<=cap,"queue cap");check(f.ticks<=f.available&&f.ticks===f.perAgent.reduce((a,b)=>a+b,0),"fresh ticks");
 for(const x of r.records){check(x.attempts<=2,"retry bound");check(x.received===null||x.received<=x.deadline,"receipt deadline");check(x.confirmed===null||x.received!==null&&x.confirmed>=x.received&&x.confirmed<=r.until,"receipt provenance");check(r.trace.filter(e=>e.id===x.id&&e.type==="received").length<=1,"dedup")}
 for(const e of r.trace.filter(e=>e.type==="ack-start"))check(r.trace.some(a=>a.type==="ack-queued"&&a.id===e.id&&a.attempt===e.attempt&&a.t<=e.t&&a.ready<=e.t&&a.expires>e.t),"ready ACK");
 for(const e of r.trace.filter(e=>e.type==="confirmed"))check(r.trace.some(a=>a.type==="ack-complete"&&a.id===e.id&&a.t===e.t&&!a.lost),"ACK provenance");
 for(const e of r.trace.filter(e=>e.type==="ack-complete"&&!e.free))check(r.segments[e.t-1]?.kind==="ack"&&r.segments[e.t-1].id===e.id,"in band");
 for(const e of r.trace.filter(e=>e.type==="data-complete"))check(r.segments.slice(e.t-2,e.t).every((s,j)=>s.kind==="data"&&s.id===e.id&&s.part===j),"contiguous data");
 return f}
 const keys=["offered","received","confirmed","freshAtAck","currentConfirmed","retries","ackDiscarded","dataTicks","ackTicks","freshTicks","availableTicks"];
 const groups={},byHorizon={};let scenarios=0;
 for(const [delay,batch] of [[2,4],[5,4],[12,4]]){
  const group=groups[delay]={};for(const p of ["ack-first","reserve"])group[p]=Object.fromEntries(lifetimes.map(l=>[l,Object.fromEntries(keys.map(k=>[k,0]))]));
  for(const name of names)for(const dataLoss of [0,30])for(const ackLoss of [0,30,60])for(const timeout of [3,6])for(const seed of [1105,2027,6011,8123]){
   scenarios++;const c={...config(name),delay,batch,dataLoss,ackLoss,timeout,seed};
   for(const p of Object.keys(group))for(const l of lifetimes){const r=simulate({...c,lifetime:l},p),f=verify(r),m={...r.metrics,freshTicks:f.ticks,availableTicks:f.available};for(const k of keys)group[p][l][k]+=m[k]}
  }
 }
 for(const horizon of [20,40,80,160]){
  byHorizon[horizon]={};for(const l of lifetimes){let ticks=0,available=0,current=0;for(const name of names){const r=simulate({...config(name),horizon,lifetime:l,delay:5},"reserve"),f=verify(r);ticks+=f.ticks;available+=f.available;current+=r.metrics.currentConfirmed}byHorizon[horizon][l]={ticks,available,current}}
 }
 const single={...config("light"),horizon:40,periods:[400,400,400],phases:[0,400,400],deadlines:[40,40,40],dataLoss:0,ackLoss:0,timeout:3,delay:12,batch:4};
 const witnesses={};for(const l of lifetimes){const r=simulate({...single,lifetime:l},"ack-first");verify(r);witnesses[l]=r}
 check(witnesses.fixed.metrics.confirmed===0,"original expiry-before-readiness");check(witnesses["ready-ttl"].metrics.confirmed===1,"ready lifetime recovers");check(witnesses.combined.metrics.confirmed===1&&witnesses.combined.metrics.retries===0,"combined avoids premature retry");
 const loss=simulate({...single,lifetime:"combined",ackLoss:100},"ack-first");verify(loss);witnesses.loss=loss;check(loss.metrics.confirmed===0&&loss.metrics.retries===1,"bounded failure");
 const stale=simulate({...single,lifetime:"combined"},"ack-first",40,[{op:"offer",t:3,agent:"pump"}]);verify(stale);witnesses.stale=stale;check(stale.trace.some(e=>e.type==="confirmed"&&e.id==="pump:1"&&!e.current),"stale history not current");
 const busy=simulate({...config("overload"),lifetime:"combined",delay:12},"reserve");verify(busy);witnesses.busy=busy;
 const cut=simulate({...config("overload"),lifetime:"combined",delay:12},"reserve",17);verify(cut);check(JSON.stringify(cut.segments)===JSON.stringify(busy.segments.slice(0,17)),"prefix replay");
 let peak=0;for(const r of Object.values(witnesses)){const a=render(r.segments);peak=Math.max(peak,a.peak);check(a.peak<=2130&&a.bytes.length===44+4000*r.until,"PCM");check(JSON.stringify(r)===JSON.stringify(simulate(r.config,r.policy,r.until,r.manual)),"deterministic witness")}
 return {schema:"mhac-negotiated-lifetime-v1",parent:"cc4aad9db4862af40709d3272bc3c915e3224325",assertions,runs,scenarios,groups,byHorizon,peak,witnesses,limits:"Synthetic shared channel; both endpoints configured with same known delay/batch, no actual negotiation protocol or acoustic identity decoding. Timing allowance not a guaranteed service reservation. Freshness retrospective."}
}
return {agents,policies,names,lifetimes,tickMs,config,simulate,render,freshness,qualify}
})();
if(typeof module==="object"&&module.exports){module.exports=Lab;if(require.main===module){const fs=require("node:fs"),path=require("node:path"),crypto=require("node:crypto"),out=process.argv[2]||"lifetime-output";fs.mkdirSync(out,{recursive:true});const q=Lab.qualify(),manifest=[];for(const [name,r] of Object.entries(q.witnesses)){const b=Lab.render(r.segments).bytes;fs.writeFileSync(path.join(out,name+".wav"),b);fs.writeFileSync(path.join(out,name+".json"),JSON.stringify(r,null,2)+"\n");manifest.push({name,sha256:crypto.createHash("sha256").update(b).digest("hex")})}fs.writeFileSync(path.join(out,"lifetime-qualification.json"),JSON.stringify(q,null,2)+"\n");fs.writeFileSync(path.join(out,"stimuli.json"),JSON.stringify(manifest,null,2)+"\n");console.log(JSON.stringify({assertions:q.assertions,runs:q.runs,scenarios:q.scenarios}));}}else globalThis.LifetimeLab=Lab;
