/* #456 Interaction lane: persistent source service debt. Synthetic only. */
(function(root,factory){
 if(typeof module==="object"&&module.exports){module.exports=factory(require("./attention.js"));if(require.main===module){
 const fs=require("node:fs"),path=require("node:path"),crypto=require("node:crypto"),D=module.exports,out=process.argv[2]||"debt-output";fs.mkdirSync(out,{recursive:true});
 const q=D.qualify(),manifest=[];for(const policy of D.policies){const r=D.simulate(D.config("overload"),policy),audio=D.render(r.segments).bytes;
 fs.writeFileSync(path.join(out,policy+".wav"),audio);fs.writeFileSync(path.join(out,policy+".json"),JSON.stringify(r,null,2)+"\n");manifest.push({policy,sha256:crypto.createHash("sha256").update(audio).digest("hex")});}
 fs.writeFileSync(path.join(out,"debt-qualification.json"),JSON.stringify(q,null,2)+"\n");fs.writeFileSync(path.join(out,"stimuli.json"),JSON.stringify(manifest,null,2)+"\n");console.log(JSON.stringify({assertions:q.assertions,runs:q.runs}));}}
 else root.DebtLab=factory(root.AttentionLab);
})(typeof globalThis!=="undefined"?globalThis:this,function(A){
"use strict";
const agents=A.agents,policies=[...A.policies,"edf","debt","debt-guard"],names=["saturated","bursty","overload","light","tight"];
const config=A.config,render=A.render,packet=2;
function simulate(c,policy,until=c.horizon,extra=[]){
 if(A.policies.includes(policy))return A.simulate(c,policy,until,extra);
 if(!policies.includes(policy))throw Error("policy");
 // Reuse existing validation, without executing an old timeline.
 A.simulate(c,"priority",0,extra);
 if(!Number.isInteger(until)||until<0||until>c.horizon)throw Error("until");
 const records=[],trace=[],segments=[],debtHistory=[],debt=[0,0,0],seq=[0,0,0],q=[null,null,null];let active=null;
 function log(t,type,r){trace.push({t,type,id:r.id,agent:r.agent});}
 function finish(t,r,outcome){if(r.outcome!=="pending")throw Error("double terminal");r.outcome=outcome;r.terminal=t;log(t,outcome,r);}
 function offer(t,i){const r={id:agents[i]+":"+(++seq[i]),agent:agents[i],priority:c.priorities[i],arrived:t,deadline:t+c.deadlines[i],remaining:packet,outcome:"pending",terminal:null,starts:0};
 records.push(r);log(t,"offer",r);if(q[i])finish(t,q[i],"coalesced");q[i]=r;}
 function expire(t){for(let i=0;i<3;i++)if(q[i]&&q[i].deadline-t<packet){finish(t,q[i],"expired");q[i]=null;}}
 for(let t=0;t<until;t++){
 expire(t);
 agents.forEach((_,i)=>{if(t>=c.phases[i]&&(t-c.phases[i])%c.periods[i]===0)offer(t,i);});
 for(const e of extra)if(e.t===t)offer(t,agents.indexOf(e.agent));
 expire(t);
 // No debt for an absent source; coalescence itself does not clear it.
 for(let i=0;i<3;i++)if(!q[i]&&active?.agent!==agents[i])debt[i]=0;
 if(!active){
 const ids=[0,1,2].filter(i=>q[i]);const urgent=i=>q[i].priority===2&&q[i].deadline-t<2*packet;
 ids.sort((i,j)=>{
 if(policy==="edf")return q[i].deadline-q[j].deadline||q[j].priority-q[i].priority||q[i].arrived-q[j].arrived||i-j;
 if(policy==="debt-guard"&&urgent(i)!==urgent(j))return Number(urgent(j))-Number(urgent(i));
 if(policy==="debt-guard"&&urgent(i)&&urgent(j))return q[i].deadline-q[j].deadline||i-j;
 return (4*q[j].priority+debt[j])-(4*q[i].priority+debt[i])||q[i].arrived-q[j].arrived||q[i].deadline-q[j].deadline||i-j;
 });
 if(ids.length){const i=ids[0];active=q[i];q[i]=null;active.starts++;log(t,"start",active);}
 }
 const serving=active?agents.indexOf(active.agent):-1;
 debtHistory.push({t,debt:debt.slice(),queued:q.map(x=>x?.id??null),serving:active?.id??null});
 for(let i=0;i<3;i++)if(q[i]&&i!==serving)debt[i]++;
 if(active){const r=active;segments.push({t,id:r.id,agent:r.agent,part:packet-r.remaining});r.remaining--;if(!r.remaining){finish(t+1,r,"complete");debt[serving]=0;active=null;}}
 else segments.push({t,id:null});
 }
 const metrics={};
 for(const agent of agents){const rr=records.filter(r=>r.agent===agent),done=rr.filter(r=>r.outcome==="complete"),lat=done.map(r=>r.terminal-r.arrived);
 metrics[agent]={offered:rr.length,complete:done.length,expired:rr.filter(r=>r.outcome==="expired").length,coalesced:rr.filter(r=>r.outcome==="coalesced").length,pending:rr.filter(r=>r.outcome==="pending").length,maxCompletedLatency:lat.length?Math.max(...lat):null,meanCompletedLatency:lat.length?lat.reduce((a,b)=>a+b,0)/lat.length:null};}
 return {schema:"mhac-attention-debt-v1",config:c,policy,until,extra,metrics,used:segments.filter(s=>s.id!==null).length,useful:records.filter(r=>r.outcome==="complete").length*packet,records,trace,segments,debtHistory};
}
function gaps(r){return agents.map(a=>{const served=r.records.filter(x=>x.agent===a&&x.outcome==="complete").map(x=>x.terminal).sort((a,b)=>a-b),offered=r.records.filter(x=>x.agent===a);if(!offered.length)return null;const times=[offered[0].arrived,...served,r.until];return Math.max(...times.slice(1).map((x,i)=>x-times[i]));});}
function compact(r){return {complete:agents.map(a=>r.metrics[a].complete),expired:agents.map(a=>r.metrics[a].expired),coalesced:agents.map(a=>r.metrics[a].coalesced),pending:agents.map(a=>r.metrics[a].pending),gap:gaps(r),used:r.used,useful:r.useful};}
function qualify(){
 let assertions=0,runs=0;const check=(v,m)=>{assertions++;if(!v)throw Error(m);};
 function verify(r){runs++;check(r.segments.length===r.until,"timeline");check(r.useful<=r.used&&r.used<=r.until,"budget");
 for(const a of agents){const m=r.metrics[a];check(m.offered===m.complete+m.expired+m.coalesced+m.pending,"conservation");}
 for(const rec of r.records){const end=r.trace.filter(e=>e.id===rec.id&&["complete","expired","coalesced"].includes(e.type));check(end.length===(rec.outcome==="pending"?0:1),"terminal once");if(rec.outcome==="complete"){check(rec.terminal<=rec.deadline,"deadline");check(r.segments.slice(rec.terminal-2,rec.terminal).every((s,i)=>s.id===rec.id&&s.part===i),"contiguous");}}
 if(r.debtHistory)for(const d of r.debtHistory){check(d.debt.every(x=>Number.isInteger(x)&&x>=0&&x<=r.until),"debt bound");check(d.queued.filter(Boolean).length<=3,"queue");}
 }
 const named={};let peak=0;
 for(const name of names){named[name]={};for(const p of policies){const c=config(name),r=simulate(c,p);verify(r);check(JSON.stringify(r)===JSON.stringify(simulate(c,p)),"determinism");check(JSON.stringify(simulate(c,p,11).segments)===JSON.stringify(r.segments.slice(0,11)),"prefix");const a=render(r.segments);peak=Math.max(peak,a.peak);check(a.peak<=2622&&a.bytes.length===44+4000*r.until,"PCM");named[name][p]=compact(r);}}
 const aggregate=Object.fromEntries(policies.map(p=>[p,{zeroPump:0,zeroRelay:0,complete:[0,0,0],expired:[0,0,0],coalesced:[0,0,0],pending:[0,0,0]}]));
 // Complete predeclared finite factorial, not random or tuned on outcomes.
 for(const pump of [1,3,7])for(const fan of [1,2,5])for(const relay of [2,4,9])for(const phase of [0,1])for(const dl of [2,4,8])for(const p of policies){
 const c={...config("overload"),horizon:40,periods:[pump,fan,relay],phases:[0,phase,0],deadlines:[12,dl,12]},r=simulate(c,p),s=compact(r),a=aggregate[p];verify(r);a.zeroPump+=Number(!s.complete[0]);a.zeroRelay+=Number(!s.complete[2]);for(const k of ["complete","expired","coalesced","pending"])for(let i=0;i<3;i++)a[k][i]+=s[k][i];
 }
 const witness=simulate(config("overload"),"debt"),guard=simulate(config("tight"),"debt-guard");
 check(named.overload.aging.complete[0]===0,"old starvation");check(named.overload.debt.complete[0]>0,"debt witness");
 check(witness.trace.some(e=>e.type==="coalesced"&&e.agent==="pump"&&witness.debtHistory[e.t].debt[0]>0),"debt survives replacement");
 const manual=simulate(config("light"),"debt",12,[{t:3,agent:"pump"},{t:3,agent:"pump"}]);verify(manual);check(manual.metrics.pump.coalesced>0,"manual coalescence");
 return {schema:"mhac-debt-qualification-v1",parent:"85ca2185a0481512c903b08d55c4e5dd6ed738e9",assertions,runs,factorialScenarios:162,named,aggregate,peak,witnesses:{overload:witness,tightGuard:guard},limits:"synthetic finite scheduling; gap includes idle time and right-censored tail, not waiting-time estimate"};
}
return {agents,policies,names,config,simulate,render,qualify,compact};
});
