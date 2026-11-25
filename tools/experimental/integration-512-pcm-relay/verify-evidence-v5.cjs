'use strict';
// Refs #512: independent exported PCM rescan and causal trace checks.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict'),{decode}=require('./stream-v4.cjs');
const dir=process.argv[2]||'evidence-v5-output',manifest=JSON.parse(fs.readFileSync(path.join(dir,'manifest.json')));let checks=0,terminal=0,accepted=0;const check=(v,m)=>{checks++;assert.ok(v,m);};
for(const r of manifest.rows){const stem=r.name+'-'+r.policy+'-g'+r.guard,b=fs.readFileSync(path.join(dir,stem+'.wav')),s=JSON.parse(fs.readFileSync(path.join(dir,stem+'.json')));
  check(crypto.createHash('sha256').update(b).digest('hex')===r.sha256,'hash');check(b.toString('ascii',0,4)==='RIFF'&&b.toString('ascii',8,12)==='WAVE'&&b.toString('ascii',36,40)==='data'&&b.readUInt16LE(20)===1&&b.readUInt16LE(22)===1&&b.readUInt32LE(24)===16000&&b.readUInt16LE(34)===16&&b.readUInt32LE(40)===640000&&b.length===640044,'format');
  const pcm=Int16Array.from({length:320000},(_,i)=>b.readInt16LE(44+i*2));check(pcm.reduce((a,x)=>Math.max(a,Math.abs(x)),0)===r.peak,'peak');const replay=decode(pcm,997).events;check(JSON.stringify(replay)===JSON.stringify(s.evidence),'independent capture replay');
  for(const e of replay)if(e.status==='ok'){accepted++;if(e.at===manifest.horizon)terminal++;}
  check(JSON.stringify(s.metrics)===JSON.stringify(r.metrics),'metric trace');
  for(const tx of s.trace.filter(x=>x.origin==='return')){const {packet,...rest}=tx;const data={...packet,kind:0};check(s.trace.some(e=>e.type==='return-enqueued'&&e.at===rest.evidenceAt&&JSON.stringify(e.packet)===JSON.stringify(data)&&e.ready<=tx.at&&tx.at<e.expires),'return has prior evidence and valid window');}
  if(r.name==='forged')check(r.metrics.invalid===1&&r.metrics.uniqueReceipts===0,'forgery retained');else check(r.metrics.invalid===0,'no unexpected false confirmation');
  if(r.name==='expiry')check(r.metrics.confirmations===0&&r.metrics.expiredAck>0,'expiry retained');
  if(r.name==='revision')check(r.metrics.refusedData===1&&r.metrics.genuineCurrentConfirmed===2,'revision boundary retained');
}
const report={rows:manifest.rows.length,checks,accepted,terminalAtHorizon:terminal};console.log(JSON.stringify(report));fs.writeFileSync(path.join(dir,'verify.json'),JSON.stringify(report,null,2)+'\n');
