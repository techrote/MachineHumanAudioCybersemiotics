/* #456 Interaction lane, synthetic only */
(function(root){const build=function build(A){
const agents=A.agents,policies=["optimistic","confirmed","repair"],names=["light","overload","bursty","tight"];
function config(name){return {...A.config(name),horizon:40,loss:30,delay:2,seed:1105}}
function simulate(c,policy,until=c.horizon,manual=[]){
 A.simulate(c,"priority",0,manual.filter(e=>e.op==="offer").map(e=>({t:e.t,agent:e.agent})));
 if(!policies.includes(policy)||!Number.isInteger(until)||until<0||until>c.horizon||!Number.isInteger(c.seed)||!Number.isInteger(c.loss)||c.loss<0||c.loss>100||!Number.isInteger(c.delay)||c.delay<1||c.delay>20||manual.length>400||manual.some(e=>!["offer","drop"].includes(e.op)||!Number.isInteger(e.t)||e.t<0||e.t>=c.horizon))throw Error("input");
 const records=[],trace=[],segments=[],feedback=[],q=[null,null,null],cur=[null,null,null],debt=[0,0,0],seq=[0,0,0];let active=null;
 const log=(t,type,r,extra={})=>trace.push({t,type,id:r.id,agent:r.agent,...extra});
 function offer(t,i){const v=++seq[i],r={id:agents[i]+":"+v,agent:agents[i],i,version:v,arrived:t,deadline:t+c.deadlines[i],priority:c.priorities[i],attempts:0,received:null,claim:null};if(q[i])log(t,"coalesced",q[i]);if(cur[i])log(t,"superseded",cur[i],{by:r.id});cur[i]=q[i]=r;records.push(r);log(t,"offer",r);}
 function draw(r){let x=(c.seed^Math.imul(r.i+1,0x9e3779b1)^Math.imul(r.version,0x85ebca6b)^Math.imul(r.attempts,0xc2b2ae35))>>>0;x^=x>>>16;x=Math.imul(x,0x7feb352d);x^=x>>>15;x=Math.imul(x,0x846ca68b);x^=x>>>16;return (x>>>0)%100}
 for(let t=0;t<=until;t++){
  if(t<until){for(let i=0;i<3;i++)if(t>=c.phases[i]&&(t-c.phases[i])%c.periods[i]===0)offer(t,i);for(const e of manual)if(e.t===t&&e.op==="offer")offer(t,agents.indexOf(e.agent));}
  for(const f of feedback.filter(f=>f.due===t)){const r=f.r;log(t,"feedback",r,{ok:f.ok,attempt:f.attempt});if(cur[r.i]!==r||t>=r.deadline){log(t,"feedback-stale",r);continue}if(f.ok){r.claim=t;log(t,"confirmed",r)}else if(policy==="repair"&&r.attempts===1&&!q[r.i]&&r.deadline-t>=2){q[r.i]=r;log(t,"retry-queued",r)}else log(t,"repair-unavailable",r)}
  if(t===until)break;
  for(let i=0;i<3;i++){if(q[i]&&q[i].deadline-t<2){log(t,"queue-expired",q[i]);q[i]=null}if(!q[i]&&active?.r.i!==i)debt[i]=0}
  if(!active){const ids=[0,1,2].filter(i=>q[i]);ids.sort((i,j)=>(4*q[j].priority+debt[j])-(4*q[i].priority+debt[i])||q[i].arrived-q[j].arrived||i-j);if(ids.length){const i=ids[0],r=q[i];q[i]=null;r.attempts++;active={r,part:0};log(t,"start",r,{attempt:r.attempts})}}
  for(let i=0;i<3;i++)if(q[i]&&active?.r.i!==i)debt[i]++;
  if(!active){segments.push({t,id:null});continue}
  const {r,part}=active;segments.push({t,id:r.id,agent:r.agent,part,attempt:r.attempts});active.part++;
  if(active.part===2){const end=t+1,lost=manual.some(e=>e.op==="drop"&&e.t===t)||draw(r)<c.loss,ok=!lost&&cur[r.i]===r&&end<=r.deadline;
   log(end,"sent",r,{attempt:r.attempts,lost,ok});if(ok){r.received=end;log(end,"received",r)}
   if(policy==="optimistic"){r.claim=end;log(end,"assumed-delivery",r)}else feedback.push({r,attempt:r.attempts,ok,due:end+c.delay});debt[r.i]=0;active=null}
 }
 const metrics={};for(const a of agents){const rs=records.filter(r=>r.agent===a);metrics[a]={offered:rs.length,received:rs.filter(r=>r.received!==null).length,claimed:rs.filter(r=>r.claim!==null).length,falseClaims:rs.filter(r=>r.claim!==null&&r.received===null).length,unconfirmed:rs.filter(r=>r.received!==null&&r.claim===null).length,retries:rs.filter(r=>r.attempts===2).length}}
 return {schema:"mhac-situated-feedback-v1",config:c,policy,until,manual,metrics,records,trace,segments,pendingFeedback:feedback.filter(f=>f.due>until).map(f=>({id:f.r.id,due:f.due,ok:f.ok,attempt:f.attempt})),used:segments.filter(s=>s.id!==null).length}
}
function summary(r){return Object.fromEntries([...Object.keys(r.metrics.pump).map(k=>[k,agents.reduce((s,a)=>s+r.metrics[a][k],0)]),["used",r.used]])}
function qualify(){
 let assertions=0,runs=0;const check=(v,m)=>{assertions++;if(!v)throw Error(m)};
 function verify(r){runs++;check(r.segments.length===r.until,"timeline");check(r.used<=r.until,"budget");for(const x of r.records){check(x.attempts<=2,"attempts");check(x.received===null||x.received<=x.deadline,"deadline");check(x.claim===null||x.claim<=r.until,"horizon");if(r.policy!=="optimistic")check(x.claim===null||x.received!==null&&x.claim>=x.received,"receipt");if(x.attempts===2)check(r.policy==="repair"&&r.trace.some(e=>e.id===x.id&&e.type==="retry-queued"),"retry")}
 for(const e of r.trace.filter(e=>e.type==="sent")){check(r.segments.slice(e.t-2,e.t).every((s,i)=>s.id===e.id&&s.part===i),"contiguous");if(e.ok)check(!e.lost,"loss")}
 for(const e of r.trace.filter(e=>e.type==="confirmed"))check(!r.trace.some(s=>s.type==="superseded"&&s.id===e.id&&s.t<=e.t),"stale")}
 const named={},aggregate={};let peak=0;for(const n of names){named[n]={};for(const p of policies){const r=simulate(config(n),p);verify(r);check(JSON.stringify(r)===JSON.stringify(simulate(config(n),p)),"determinism");const a=A.render(r.segments);peak=Math.max(peak,a.peak);check(a.peak<=2622&&a.bytes.length===44+4000*r.until,"pcm");named[n][p]=summary(r);aggregate[p]=Object.fromEntries(Object.keys(summary(r)).map(k=>[k,0]))}}
 for(const n of names)for(const loss of [0,30,60])for(const delay of [1,2,4])for(const seed of [1105,2027,6011,8123])for(const p of policies){const r=simulate({...config(n),loss,delay,seed},p);verify(r);const s=summary(r);for(const k in s)aggregate[p][k]+=s[k]}
 const c={...config("light"),horizon:12,periods:[400,400,400],phases:[0,400,400],deadlines:[12,12,12],loss:0,delay:1},manual=[{op:"drop",t:1}],witness=Object.fromEntries(policies.map(p=>[p,simulate(c,p,12,manual)]));for(const r of Object.values(witness))verify(r);
 check(summary(witness.optimistic).falseClaims===1,"optimistic");check(summary(witness.confirmed).received===0,"no repair");check(summary(witness.repair).received===1&&summary(witness.repair).claimed===1,"repair");
 const stale=simulate({...c,delay:3},"repair",12,[{op:"offer",t:3,agent:"pump"}]);verify(stale);check(stale.trace.some(e=>e.id==="pump:1"&&e.type==="feedback-stale")&&stale.records[0].claim===null,"stale receipt");
 const end=simulate(c,"confirmed",2);verify(end);check(end.pendingFeedback.length===1&&end.records[0].received===2&&end.records[0].claim===null,"censor");
 return {schema:"mhac-feedback-qualification-v1",parent:"857b7e8a6db9032b38cfcd1458d3d515b658e656",assertions,runs,factorialScenarios:144,named,aggregate,peak,witnesses:{forcedLoss:witness,lateFeedback:stale,horizon:end},limits:"synthetic oracle and reliable out-of-band feedback; no human evidence"}
}
return {agents,policies,names,config,simulate,summary,qualify,render:A.render}
};if(typeof module==="object"&&module.exports){const F=module.exports=build(require("./attention.js"));if(require.main===module){const fs=require("node:fs"),path=require("node:path"),crypto=require("node:crypto"),out=process.argv[2]||"feedback-output";fs.mkdirSync(out,{recursive:true});const q=F.qualify(),manifest=[];for(const p of F.policies){const r=q.witnesses.forcedLoss[p],b=F.render(r.segments).bytes;fs.writeFileSync(path.join(out,p+".wav"),b);fs.writeFileSync(path.join(out,p+".json"),JSON.stringify(r,null,2)+"\n");manifest.push({policy:p,sha256:crypto.createHash("sha256").update(b).digest("hex")});}fs.writeFileSync(path.join(out,"feedback-qualification.json"),JSON.stringify(q,null,2)+"\n");fs.writeFileSync(path.join(out,"stimuli.json"),JSON.stringify(manifest,null,2)+"\n");console.log(JSON.stringify({assertions:q.assertions,runs:q.runs}));}}else root.FeedbackLab=build(root.AttentionLab);})(typeof globalThis!=="undefined"?globalThis:this);
