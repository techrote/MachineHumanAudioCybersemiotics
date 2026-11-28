/* MHAC Situated Relay continuation, synthetic only. */
(function(root){const api=(function build(){
"use strict";
const agents=["pump","fan","relay"], policies=["preempt","priority","aging"], tickMs=250, packet=2;
function config(name){
 const profiles={saturated:[80,2,80],bursty:[11,5,13],overload:[3,2,4],light:[17,11,19],tight:[80,2,80]};
 if(!Object.hasOwn(profiles,name))throw Error("scenario");
 return {name,horizon:80,periods:profiles[name],phases:[0,1,0],deadlines:name==="tight"?[12,2,12]:[20,6,20],priorities:[0,2,1]};
}
function validate(c){
 if(!c||!Number.isInteger(c.horizon)||c.horizon<1||c.horizon>400||typeof c.name!=="string")throw Error("config");
 for(const k of ["periods","phases","deadlines","priorities"])if(!Array.isArray(c[k])||c[k].length!==3||c[k].some(x=>!Number.isInteger(x)))throw Error(k);
 if(c.periods.some(x=>x<1||x>400)||c.phases.some(x=>x<0||x>400)||c.deadlines.some(x=>x<1||x>400)||c.priorities.some(x=>x<0||x>2))throw Error("range");
}
function simulate(c,policy,until=c.horizon,extra=[]){
 validate(c);if(!policies.includes(policy)||!Number.isInteger(until)||until<0||until>c.horizon||!Array.isArray(extra)||extra.length>400)throw Error("input");
 if(extra.some(x=>!x||!Number.isInteger(x.t)||x.t<0||x.t>=c.horizon||!agents.includes(x.agent)))throw Error("extra");
 const records=[],trace=[],segments=[],q=[];let active=null;const seq=[0,0,0];
 function log(t,type,r){trace.push({t,type,id:r.id,agent:r.agent});}
 function finish(t,r,outcome){if(r.outcome!=="pending")throw Error("double terminal");r.outcome=outcome;r.terminal=t;log(t,outcome,r);}
 function offer(t,i){
  const r={id:agents[i]+":"+ ++seq[i],agent:agents[i],priority:c.priorities[i],arrived:t,deadline:t+c.deadlines[i],remaining:packet,outcome:"pending",terminal:null,starts:0};
  records.push(r);log(t,"offer",r);
  const j=q.findIndex(x=>x.agent===r.agent);
  if(j>=0)finish(t,q.splice(j,1)[0],"coalesced");
  q.push(r);
 }
 const rank=(a,t)=>policy==="aging"?a.priority*4+(t-a.arrived):a.priority;
 const sort=(t)=>q.sort((a,b)=>rank(b,t)-rank(a,t)||a.arrived-b.arrived||a.deadline-b.deadline||a.id.localeCompare(b.id,"en"));
 for(let t=0;t<until;t++){
  // Expire before admissions and service. Deadline means latest completion boundary.
  for(let j=q.length-1;j>=0;j--)if(q[j].deadline-t<packet)finish(t,q.splice(j,1)[0],"expired");
  if(active&&active.deadline-t<active.remaining){finish(t,active,"expired");active=null;}
  agents.forEach((_,i)=>{if(t>=c.phases[i]&&(t-c.phases[i])%c.periods[i]===0)offer(t,i);});
  for(const e of extra)if(e.t===t)offer(t,agents.indexOf(e.agent));
  for(let j=q.length-1;j>=0;j--)if(q[j].deadline-t<packet)finish(t,q.splice(j,1)[0],"expired");
  sort(t);
  if(policy==="preempt"&&active&&q.length&&q[0].priority>active.priority){
   const r=active;active=null;log(t,"interrupted",r);r.remaining=packet;
   // A newer pending observation replaces an older interrupted packet, never a receipt.
   if(q.some(x=>x.agent===r.agent))finish(t,r,"coalesced");
   else q.push(r);
   sort(t);
  }
  if(!active&&q.length){active=q.shift();active.starts++;log(t,"start",active);}
  if(active){const r=active;segments.push({t,id:r.id,agent:r.agent,part:packet-r.remaining});r.remaining--;
   if(!r.remaining){finish(t+1,r,"complete");active=null;}
  }else segments.push({t,id:null});
  if(q.length>3)throw Error("queue bound");
 }
 const metrics={};
 for(const agent of agents){const rr=records.filter(r=>r.agent===agent),done=rr.filter(r=>r.outcome==="complete"),lat=done.map(r=>r.terminal-r.arrived);
  metrics[agent]={offered:rr.length,complete:done.length,expired:rr.filter(r=>r.outcome==="expired").length,coalesced:rr.filter(r=>r.outcome==="coalesced").length,pending:rr.filter(r=>r.outcome==="pending").length,maxCompletedLatency:lat.length?Math.max(...lat):null,meanCompletedLatency:lat.length?lat.reduce((a,b)=>a+b,0)/lat.length:null};
 }
 const used=segments.filter(s=>s.id!==null).length, useful=records.filter(r=>r.outcome==="complete").length*packet;
 return {schema:"mhac-attention-v1",config:c,policy,until,extra,metrics,used,useful,records,trace,segments};
}
function render(segments){
 const rate=8000,n=2000,b=new Uint8Array(44+segments.length*n*2),v=new DataView(b.buffer);
 const s=(o,x)=>{for(let i=0;i<x.length;i++)b[o+i]=x.charCodeAt(i);};
 s(0,"RIFF");v.setUint32(4,b.length-8,true);s(8,"WAVE");s(12,"fmt ");v.setUint32(16,16,true);v.setUint16(20,1,true);v.setUint16(22,1,true);v.setUint32(24,rate,true);v.setUint32(28,rate*2,true);v.setUint16(32,2,true);v.setUint16(34,16,true);s(36,"data");v.setUint32(40,b.length-44,true);
 let peak=0,j=44;
 for(const seg of segments)for(let i=0;i<n;i++){
  let z=0;if(seg.id!==null){const a=agents.indexOf(seg.agent),f=[400,600,800][a]+seg.part*100,h=[2,3,2][a],env=Math.min(1,i/80,(n-1-i)/80);
   z=Math.round(32767*.08*env*(Math.sin(2*Math.PI*f*i/rate)+.2*Math.sin(2*Math.PI*h*f*i/rate))/1.2);}
  peak=Math.max(peak,Math.abs(z));v.setInt16(j,z,true);j+=2;
 }return {bytes:b,peak};
}
function qualify(){
 let assertions=0;const check=(x,m)=>{assertions++;if(!x)throw Error(m);};const summary=[];
 function verify(r){
  check(r.segments.length===r.until,"timeline length");
  check(r.useful<=r.used&&r.used<=r.until,"budget");
  for(const a of agents){const m=r.metrics[a];check(m.offered===m.complete+m.expired+m.coalesced+m.pending,"outcome conservation");}
  for(const rec of r.records){const done=r.trace.filter(e=>e.id===rec.id&&["complete","expired","coalesced"].includes(e.type));
   check(done.length===(rec.outcome==="pending"?0:1),"terminal once");
   if(rec.outcome==="complete"){check(rec.terminal<=rec.deadline,"deadline");const last=r.segments.slice(rec.terminal-packet,rec.terminal);check(last.length===packet&&last.every((s,i)=>s.id===rec.id&&s.part===i),"complete consecutive packet");}
  }
 }
 for(const name of ["saturated","bursty","overload","light","tight"])for(const policy of policies){
  const r=simulate(config(name),policy);verify(r);check(JSON.stringify(r)===JSON.stringify(simulate(config(name),policy)),"deterministic");
  const audio=render(r.segments);check(audio.peak<=2622,"gain bound");check(audio.bytes.length===44+4000*r.until,"wav size");
  summary.push({name,policy,metrics:r.metrics,used:r.used,useful:r.useful,peak:audio.peak});
 }
 // Factorial stress of arrival periods, phase, and deadlines. Independent exact scenarios, not human samples.
 let cases=0;
 for(const p of [1,2,3,5,9])for(const phase of [0,1,2])for(const d of [2,4,8,20])for(const policy of policies){
  const c={...config("saturated"),horizon:30,periods:[7,p,9],phases:[0,phase,2],deadlines:[d,d,d]};verify(simulate(c,policy));cases++;
 }
 const strict=simulate(config("saturated"),"preempt"),non=simulate(config("saturated"),"priority"),age=simulate(config("saturated"),"aging");
 check(strict.metrics.pump.complete===0,"starvation witness");check(age.metrics.pump.complete===1,"aging rescues pump");
 check(age.metrics.relay.complete===1,"aging rescues relay");
 const extra=[{t:3,agent:"pump"},{t:3,agent:"pump"}];const edited=simulate(config("light"),"aging",10,extra);verify(edited);check(edited.metrics.pump.coalesced>0,"manual events coalesced");
 const prefix=simulate(config("bursty"),"aging",10),full=simulate(config("bursty"),"aging");check(JSON.stringify(prefix.segments)===JSON.stringify(full.segments.slice(0,10)),"prefix replay");
 const tight=simulate(config("tight"),"aging");check(tight.metrics.fan.expired>0,"urgency tradeoff");
 let bad=false;try{simulate({...config("light"),periods:[0,2,3]},"aging")}catch{bad=true}check(bad,"invalid input");
 return {schema:"mhac-attention-qualification-v1",assertions,cases,summary,witnesses:{strict:strict.trace,nonpreempt:non.trace,aging:age.trace,tight:tight.trace},limits:"synthetic arrivals; no waveform reception, perception, or safety claim"};
}
return {agents,policies,tickMs,config,simulate,render,qualify};
})();if(typeof module==="object"&&module.exports){module.exports=api;if(require.main===module){const fs=require("node:fs"),path=require("node:path"),out=process.argv[2]||"attention-output";fs.mkdirSync(out,{recursive:true});const q=api.qualify();fs.writeFileSync(path.join(out,"attention-qualification.json"),JSON.stringify(q,null,2)+"\n");for(const p of api.policies){const r=api.simulate(api.config("saturated"),p);fs.writeFileSync(path.join(out,p+".wav"),api.render(r.segments).bytes);fs.writeFileSync(path.join(out,p+".json"),JSON.stringify(r,null,2)+"\n");}console.log(JSON.stringify({assertions:q.assertions,cases:q.cases}));}}else root.AttentionLab=api;})(typeof globalThis!=="undefined"?globalThis:this);
