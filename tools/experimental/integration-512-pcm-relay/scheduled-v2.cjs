'use strict';
// Refs #512. Finite synthetic half-duplex scheduler; real PCM in both directions.
const v1=require('./relay.cjs'), v2=require('./bound-v2.cjs');
const RATE=16000, STEP=32000, FRAME=31360, HORIZON=10, MAX_ATTEMPTS=2, TIMEOUT=3, CAP=4;
const A={...v1.base}, B={...A,source:2,actor:3,event:2,seq:4,tree:['quote',['open']]};
const A3={...A,version:3,seq:5,tree:['question',['overload']]}, B3={...B,version:3,seq:6};
const policies=['data-first','ack-first','reserve'];
const cases=['clean','data-loss','ack-loss','persistent-loss','interference','drift','interrupt','splice','noise','delayed','expiry','revision','forged','wrong-actor','replay'];
const key=p=>JSON.stringify([p.source,p.version,p.actor,p.event,p.seq,p.tree]);
const eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b), packetHits=h=>h.filter(x=>x.status==='ok').map(x=>x.packet);
function config(name){
  if(!cases.includes(name))throw Error('scenario');
  const isolated=['forged','wrong-actor','replay'].includes(name);
  return {offers:isolated?[[0,A]]:name==='revision'?[[0,A],[0,B],[1,A3],[4,B3]]:[[0,A],[0,B]],delay:name==='delayed'?3:name==='revision'?2:1,ttl:name==='expiry'?1:5};
}
// The fault is a declared fixture selected by packet identity/attempt, not by decoder result.
function channel(p,fault,slot){
  let pcm=v2.render(p,slot*.19);
  if(fault==='lost')pcm.fill(0);
  if(fault==='interrupt')pcm=pcm.slice(0,10000);
  if(fault==='drift'){const a=pcm;pcm=Int16Array.from({length:Math.round(a.length*1.012)},(_,i)=>a[Math.min(a.length-1,Math.floor(i/1.012))]);}
  if(fault==='splice'){const alt=v2.render({...p,tree:['quote',['stopped']]},slot*.19);pcm=v1.join(pcm.slice(0,10880),alt.slice(10880,21120),pcm.slice(21120));}
  if(fault==='noise'){let seed=71+p.source*101+p.seq*17;pcm=Int16Array.from(pcm,v=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return v+Math.round((seed/4294967296*2-1)*600);});}
  if(fault==='overlap'){const a=v2.render({...B,tree:['question',['stopped']]},slot*.19);pcm=Int16Array.from(pcm,(v,i)=>v+a[i]);}
  // Deterministic varying lead, always <= 160 samples so the drift fixture fits.
  const lead=64+16*(slot%5);
  if(lead+pcm.length>STEP)throw Error('slot overrun');
  const out=new Int16Array(STEP);out.set(pcm,lead);return out;
}
// Fixed capture windows independent of scheduled slot boundaries. 2.5 s overlap > 1.96 s frame.
function rescan(pcm){const hop=88000, win=128000, hits=[];for(let start=0;start<pcm.length;start+=hop){for(const h of v2.acquire(pcm.slice(start,Math.min(start+win,pcm.length))))if(h.start<hop&&h.status==='ok')hits.push({...h,start:start+h.start});}return hits;}
function simulate(name,policy){
  if(!policies.includes(policy))throw Error('policy');
  const cfg=config(name), current=new Map(), records=new Map(), queue=[], received=new Set(), returns=new Map();
  const trace=[], audio=[];const metrics={offered:0,dataAttempts:0,retries:0,acks:0,uniqueReceipts:0,duplicates:0,confirmations:0,genuineConfirmations:0,invalid:0,freshAtAck:0,genuineFreshAtAck:0,staleAtAck:0,unmatchedAck:0,replayAck:0,expiredAck:0,droppedAck:0,refusedData:0,noDecodedPacket:0,currentConfirmed:0,genuineCurrentConfirmed:0,idleSlots:0};
  for(let slot=0;slot<HORIZON;slot++){
    const events=[];for(const [at,p] of cfg.offers)if(at===slot){current.set(p.source,p.version);records.set(key(p),{packet:p,attempts:0,ready:slot,confirmed:false});metrics.offered++;events.push({type:'offer',packet:p});}
    for(let i=queue.length-1;i>=0;i--)if(slot>=queue[i].expires){events.push({type:'return-expired',packet:queue[i].packet});queue.splice(i,1);metrics.expiredAck++;}
    const data=[...records.values()].filter(r=>!r.confirmed&&r.attempts<MAX_ATTEMPTS&&r.ready<=slot&&current.get(r.packet.source)===r.packet.version);
    const ret=queue.filter(r=>r.ready<=slot);const preferReturn=policy==='ack-first'||(policy==='reserve'&&slot%3===2);
    let p=null,fault='clean',origin='idle';
    // Independent fixture return transmissions occupy the same finite channel as legitimate traffic.
    if((name==='forged'||name==='wrong-actor')&&slot===1){p={...A,kind:1,...(name==='wrong-actor'?{actor:4}:{})};origin='fixture-return';}
    else if(name==='replay'&&slot===4){p={...A,kind:1};origin='fixture-return';}
    else if(ret.length&&(preferReturn||!data.length)){const r=ret[0];queue.splice(queue.indexOf(r),1);p=r.packet;origin='return';}
    else if(data.length){const r=data[0];p=r.packet;origin='data';r.attempts++;r.ready=slot+TIMEOUT;metrics.dataAttempts++;if(r.attempts>1)metrics.retries++;
      if(r.attempts===1&&p.source===1&&p.version===2){if(name==='data-loss'||name==='forged')fault='lost';if(name==='drift')fault='drift';if(name==='interrupt')fault='interrupt';if(name==='splice')fault='splice';if(name==='noise')fault='noise';}
      if(name==='persistent-loss'&&p.source===1)fault='lost';
      if(r.attempts===1&&p.source===2&&name==='interference')fault='overlap';
    }
    if(p&&p.kind===1){metrics.acks++;const k=key(p),n=(returns.get(k)||0)+1;returns.set(k,n);if(name==='ack-loss'&&p.source===1&&n===1)fault='lost';}
    const pcm=p?channel(p,fault,slot):new Int16Array(STEP);audio.push(pcm);if(!p)metrics.idleSlots++;
    const hits=v2.acquire(pcm);if(p&&!packetHits(hits).length)metrics.noDecodedPacket++;
    for(const r of packetHits(hits)){
      const k=key(r);
      if(r.kind===0){const route=r.source===1?[2,1]:r.source===2?[3,2]:null;const accepted=route&&r.actor===route[0]&&r.event===route[1]&&r.version===current.get(r.source);
        events.push({type:'data-receipt',accepted:!!accepted,packet:r});if(!accepted){metrics.refusedData++;continue;}
        if(received.has(k))metrics.duplicates++;else{received.add(k);metrics.uniqueReceipts++;}
        if(!queue.some(a=>key(a.packet)===k)){if(queue.length>=CAP){metrics.droppedAck++;events.push({type:'return-overflow',packet:r});}else queue.push({packet:{...r,kind:1},ready:slot+cfg.delay,expires:slot+cfg.ttl});}
      }else{
        // Sender is allowed to consult only its own sent-record ledger and configured current version.
        // Receiver's receipt set is used solely by the evaluator *after* acceptance.
        const record=records.get(k),accepted=!!record&&record.attempts>0&&!record.confirmed;
        const fresh=r.version===current.get(r.source);
        if(accepted){record.confirmed=true;metrics.confirmations++;if(fresh)metrics.freshAtAck++;else metrics.staleAtAck++;}
        else if(record?.confirmed)metrics.replayAck++;else metrics.unmatchedAck++;
        const evaluatorGenuine=received.has(k);if(accepted){if(evaluatorGenuine){metrics.genuineConfirmations++;if(fresh)metrics.genuineFreshAtAck++;}else metrics.invalid++;}
        events.push({type:'ack-receipt',accepted,fresh,evaluatorGenuine,packet:r});
      }
    }
    trace.push({slot,atSamples:slot*STEP,tx:p,origin,fault,hits,events,returnQueue:queue.map(x=>({...x})),current:Object.fromEntries(current)});
  }
  metrics.currentConfirmed=[...records.values()].filter(r=>r.confirmed&&current.get(r.packet.source)===r.packet.version).length;
  metrics.genuineCurrentConfirmed=[...records.entries()].filter(([k,r])=>received.has(k)&&r.confirmed&&current.get(r.packet.source)===r.packet.version).length;
  metrics.unconfirmed=[...records.values()].filter(r=>!r.confirmed).length;metrics.returnBacklog=queue.length;
  const pcm=v1.join(...audio), scanned=rescan(pcm), expected=trace.flatMap(t=>packetHits(t.hits));
  const continuousMatch=eq(packetHits(scanned),expected);return {name,policy,config:cfg,metrics,continuousMatch,samples:pcm.length,trace,continuous:scanned,pcm};
}
function qualify(){let assertions=0;const check=(v,m)=>{assertions++;if(!v)throw Error(m);};const sessions=[];
  for(const name of cases)for(const policy of policies){const s=simulate(name,policy),m=s.metrics;check(s.samples===HORIZON*STEP,'budget');check(s.continuousMatch,'continuous '+name+' '+policy);check(m.dataAttempts<=MAX_ATTEMPTS*m.offered,'retry cap');check(m.confirmations<=m.offered,'confirmation cap');check(m.freshAtAck+m.staleAtAck===m.confirmations,'fresh partition');check(m.genuineConfirmations+m.invalid===m.confirmations,'genuineness partition');check(m.uniqueReceipts<=m.dataAttempts,'receipt count');check(s.trace.every(t=>t.returnQueue.length<=CAP),'queue cap');check(s.pcm.every(x=>Math.abs(x)<=8192),'peak');
    if(name==='forged')check(m.invalid===1&&m.uniqueReceipts===0&&m.confirmations===1,'forgery retained');else check(m.invalid===0,'unexpected invalid');
    if(name==='wrong-actor')check(m.unmatchedAck===1&&m.confirmations===1,'wrong actor rejected');if(name==='replay')check(m.replayAck===1&&m.confirmations===1,'replay ignored');if(name==='expiry')check(m.confirmations===0&&m.expiredAck>0,'expiry');if(name==='data-loss'||name==='ack-loss'||name==='interference'||name==='interrupt'||name==='splice'||name==='drift')check(m.retries>0&&m.confirmations===2,'repair '+name+' '+policy);if(name==='persistent-loss')check(m.confirmations===1&&m.unconfirmed===1,'persistent loss');if(name==='revision')check(m.staleAtAck>0,'historical confirmation');sessions.push(s);
  }return {assertions,sessions};
}
module.exports={simulate,qualify,rescan};
if(require.main===module){const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),dir=process.argv[2]||'scheduled-v2-output';fs.mkdirSync(dir,{recursive:true});const {assertions,sessions}=qualify(),rows=[];
  for(const {pcm,...s} of sessions){const stem=s.name+'-'+s.policy,bytes=v1.wav(pcm);fs.writeFileSync(path.join(dir,stem+'.wav'),bytes);fs.writeFileSync(path.join(dir,stem+'.json'),JSON.stringify(s,null,2)+'\n');rows.push({name:s.name,policy:s.policy,metrics:s.metrics,samples:s.samples,continuousMatch:s.continuousMatch,peak:pcm.reduce((a,b)=>Math.max(a,Math.abs(b)),0),sha256:crypto.createHash('sha256').update(bytes).digest('hex')});}
  fs.writeFileSync(path.join(dir,'manifest.json'),JSON.stringify({schema:'mhac-scheduled-v2',assertions,rate:RATE,slotSamples:STEP,rows},null,2)+'\n');console.log(JSON.stringify({assertions,rows:rows.map(({name,policy,metrics})=>({name,policy,metrics}))}));
}
