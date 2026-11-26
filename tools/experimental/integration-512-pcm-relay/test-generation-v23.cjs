'use strict';
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const G=require('./generation-v23.cjs'),{C:P}=require('./lease-v21.cjs'),{wav}=require('./relay.cjs');
const eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b),{STEP,HEAD}=G;let checks=0;const ck=(x,m)=>{checks++;assert.ok(x,m);};
const out=process.argv[2]||'generation-v23-output';fs.mkdirSync(out,{recursive:true});
const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'mhac-v23-'));let serial=0;
function fresh(){const d=path.join(tmp,String(serial++));G.provision(d);return d;}
const ledger=fresh();for(let i=0;i<G.CAP;i++)ck(G.allocate(ledger)===i,'allocation across reopen');assert.throws(()=>G.allocate(ledger),/exhausted/);checks++;fs.unlinkSync(path.join(ledger,'001'));assert.throws(()=>G.allocate(ledger),/history/);checks++;assert.throws(()=>G.allocate(path.join(tmp,'missing')));checks++;
const rows=[],controls=[];function save(name,pcm){const file=name+'.wav',bytes=wav(pcm);fs.writeFileSync(path.join(out,file),bytes);return {file,samples:pcm.length,sha256:crypto.createHash('sha256').update(bytes).digest('hex')};}
function run(scenario,policy,seed){let d=fresh(),snapshot=path.join(tmp,String(serial++));fs.cpSync(d,snapshot,{recursive:true});let g=policy==='generation'?G.allocate(d):0,active='C',attempts=0,ready=0,ack=null,oldAck=null,oldRequest=null,newRequest=null,record=true,receipts=new Set(),trace=[],segments=[],metrics={wrongRepair:0,falseConfirmation:0,forgedHonored:0,confirmed:{},genuine:0,reservation:0};
 const ph=seed*.013,packet=P,reply={...packet,kind:1};
 for(let slot=0;slot<11;slot++){
  if(slot===5){ck(!record,'C completed');active='D';attempts=0;ready=5;record=true;g=policy==='generation'?G.allocate(scenario.startsWith('rollback')?snapshot:d):0;}
  let x=new Int16Array(STEP),gaps=[],origin='idle',role='idle';
  if(slot===6&&['stale-request','rollback'].includes(scenario)){x=oldRequest;origin='old-request';role='request';}
  else if(slot===6&&['stale-ack','rollback-ack'].includes(scenario)){x=oldAck;origin='old-ack';role='body';}
  else if(slot===6&&scenario==='forged-ack'){x=G.envelope(reply,g,ph);origin='forged-ack';role='body';}
  else if(slot===6&&scenario==='forged-request'){x=G.request(packet,g,ph);origin='forged-request';role='request';}
  else if(slot===6&&scenario==='honest-request'){x=newRequest;origin='honest-request';role='request';}
  else if(ack){x=G.envelope(ack.packet,ack.g,ph);origin='ack';role='body';if(active==='C')oldAck=x;ack=null;}
  else if(record&&ready<=slot&&attempts<2){x=G.envelope(packet,g,ph);origin='data';role='body';attempts++;ready=slot+3;if(attempts===1){if(active==='C'||scenario==='honest-request'){gaps=[1036,2316,3596].map(n=>[64+n,80+n]);for(const [l,r] of gaps)x.fill(0,l,r);}else if(scenario!=='clean')x.fill(0);}}
  if(role!=='idle')metrics.reservation+=role==='request'?7040:38400; // nominal tone-frame lengths, not slot occupancy
  const e=G.acquire(x,gaps);ck(eq(e,G.acquire(x,gaps,127)),'chunk invariance');segments.push(x);let decision='none';
  if(e.status==='diagnostic'&&e.packet.kind===0){const req=G.request(e.packet,e.generation,ph);if(active==='C')oldRequest=req;else newRequest=req;decision='diagnostic-request-created';}
  if(e.status==='receipt-candidate'&&e.packet.kind===0&&eq(e.packet,packet)){ack={g:e.generation,packet:{...e.packet,kind:1}};if(origin==='data')receipts.add(active);decision='receipt';}
  if(e.status==='receipt-candidate'&&e.packet.kind===1&&eq(e.packet,reply)&&record&&attempts&&e.generation===g){record=false;metrics.confirmed[active]=slot*STEP+e.at;const genuine=receipts.has(active)&&origin==='ack';metrics.genuine+=Number(genuine);metrics.falseConfirmation+=Number(!genuine);decision=genuine?'genuine-confirmation':'false-confirmation';}
  if(e.status==='request'&&record&&attempts===1&&ready>slot+1&&eq(e.token,G.token(packet,g,'request'))){ready=slot+1;decision='repair';metrics.wrongRepair+=Number(origin==='old-request'&&active==='D');metrics.forgedHonored+=Number(origin==='forged-request');}
  trace.push({slot,active,origin,gaps,at:slot*STEP+e.at,decision,e});
 }
 const pcm=new Int16Array(STEP*segments.length);segments.forEach((x,i)=>pcm.set(x,i*STEP));return {scenario,policy,seed,metrics,trace,pcm};}
try{
 for(const seed of process.env.SEED?[Number(process.env.SEED)]:[71,113])for(const scenario of ['stale-request','stale-ack','rollback','rollback-ack','honest-request','forged-request','forged-ack','clean'])for(const policy of ['reuse','generation']){const {pcm,...r}=run(scenario,policy,seed),m=r.metrics;ck(!!m.confirmed.C&&!!m.confirmed.D,'both confirmed');ck(m.wrongRepair===Number(scenario==='rollback'||(scenario==='stale-request'&&policy==='reuse')),'stale request');ck(m.falseConfirmation===Number(['forged-ack','rollback-ack'].includes(scenario)||(scenario==='stale-ack'&&policy==='reuse')),'stale/forged ack');ck(m.forgedHonored===Number(scenario==='forged-request'),'forged request');rows.push({...r,...save(`${seed}-${scenario}-${policy}`,pcm)});}
 for(const seed of process.env.SEED?[Number(process.env.SEED)]:[71,113]){const ph=seed*.013,x=G.envelope(P,17,ph),wrong=G.envelope({...P,seq:14},17,ph),splice=x.slice();splice.set(wrong.subarray(HEAD),HEAD);const tail=x.slice();tail.fill(0,HEAD);const hidden=x.slice();hidden.fill(0,STEP-8,STEP-4);const relabel=x.slice();relabel.set(G.envelope(P,18,ph).subarray(HEAD),HEAD);for(const [name,pcm,gaps,status,gen] of [['clean',x,[],'receipt-candidate',17],['wrong-body-suffix',splice,[],'refused'],['missing-suffix',tail,[],'refused'],['outside-gap',hidden,[[STEP-8,STEP-4]],'refused'],['relabel-same-body',relabel,[],'receipt-candidate',18]]){const e=G.acquire(pcm,gaps);ck(e.status===status,name+': '+e.status);if(gen!==undefined)ck(e.generation===gen,'generation from PCM');controls.push({seed,name,gaps,e,...save(`${seed}-control-${name}`,pcm)});}}
 fs.writeFileSync(path.join(out,'receipt.json'),JSON.stringify({schema:'mhac-generation-v23',rate:16000,step:STEP,checks,rows,controls},null,2)+'\n');console.log(JSON.stringify({checks,rows:rows.map(({scenario,policy,seed,metrics})=>({scenario,policy,seed,metrics})),controls:controls.length},null,2));
}finally{fs.rmSync(tmp,{recursive:true,force:true});}
