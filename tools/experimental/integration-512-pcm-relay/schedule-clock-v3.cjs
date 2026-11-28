'use strict';
// Refs #512. Same scheduler, fault definitions, wire format and slot budget as v2.
const v1=require('./relay.cjs'), clock=require('./clock-v3.cjs'), sched=require('./scheduled-v2.cjs');
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict');
function receive(p){const h=clock.acquire(p);return h.evidence.length?[{...h,start:h.evidence[0].s,score:Math.max(...h.evidence.map(e=>e.q))}]:[];}
const cases=['clean','data-loss','ack-loss','persistent-loss','interference','drift','interrupt','splice','noise','delayed','expiry','revision','forged','wrong-actor','replay'];
const policies=['data-first','ack-first','reserve'];
function run(dir){fs.mkdirSync(dir,{recursive:true});let assertions=0;const check=(v,m)=>{assertions++;assert.ok(v,m);};const rows=[];
 for(const name of cases)for(const policy of policies){
  const old=sched.simulate(name,policy),s=sched.simulate(name,policy,receive),m=s.metrics;
  check(s.samples===old.samples&&s.samples===320000,'equal channel horizon');check(m.offered===old.metrics.offered,'same offered messages');check(m.dataAttempts<=2*m.offered,'retry bound');check(s.trace.every(t=>t.returnQueue.length<=4),'queue bound');check(m.genuineConfirmations+m.invalid===m.confirmations,'evaluation partition');check(m.invalid===(name==='forged'?1:0),'forgery retained');
  if(name==='drift')check(m.retries<old.metrics.retries&&m.genuineConfirmations===2,'clock repair affects schedule');
  const {pcm,...trace}=s,stem=name+'-'+policy,bytes=v1.wav(pcm);fs.writeFileSync(path.join(dir,stem+'.wav'),bytes);fs.writeFileSync(path.join(dir,stem+'.json'),JSON.stringify(trace,null,2)+'\n');
  rows.push({name,policy,metrics:m,baseline:old.metrics,samples:s.samples,continuousMatch:null,peak:pcm.reduce((a,b)=>Math.max(a,Math.abs(b)),0),sha256:crypto.createHash('sha256').update(bytes).digest('hex')});
 }
 const report={schema:'mhac-scheduled-clock-v3',assertions,rate:16000,slotSamples:32000,rows};fs.writeFileSync(path.join(dir,'manifest.json'),JSON.stringify(report,null,2)+'\n');return report;
}
if(require.main===module){const r=run(process.argv[2]||'scheduled-clock-v3-output');console.log(JSON.stringify({assertions:r.assertions,sessions:r.rows.length,drift:r.rows.filter(x=>x.name==='drift').map(x=>({policy:x.policy,old:x.baseline.retries,new:x.metrics.retries,confirmed:x.metrics.genuineConfirmations}))}));}
module.exports={receive,run};
