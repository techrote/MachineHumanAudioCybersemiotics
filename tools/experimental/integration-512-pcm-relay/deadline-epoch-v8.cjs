'use strict';
// Refs #512: absolute-deadline factorial and bounded adaptive turnaround; unchanged wire/receiver.
const v1=require('./relay.cjs'),v2=require('./bound-v2.cjs'),{Stream}=require('./stream-v4.cjs');
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const STEP=32000,HORIZON=320000,RATE=16000;
const A={...v1.base},B={...A,source:2,actor:3,event:2,seq:4,tree:['quote',['open']]},A3={...A,version:3,seq:5,tree:['question',['overload']]};
const cases=['clean','data-loss','ack-loss','persistent-loss','drift','delayed','expiry','revision','forged','wrong-actor','replay'];
const policies=['data-first','ack-first','reserve'];
const key=p=>JSON.stringify([p.source,p.version,p.actor,p.event,p.seq,p.tree]);
function config(name){return {offers:['forged','wrong-actor','replay'].includes(name)?[[0,A]]:name==='revision'?[[0,A],[0,B],[STEP,A3]]:[[0,A],[0,B]],delay:name==='delayed'?3:1,ttl:name==='expiry'?1:5};}
function channel(p,fault,slot){let pcm=v2.render(p,slot*.19);if(fault==='lost')pcm.fill(0);if(fault==='drift'){const a=pcm;pcm=Int16Array.from({length:Math.round(a.length*1.012)},(_,i)=>a[Math.min(a.length-1,Math.floor(i/1.012))]);}const out=new Int16Array(STEP);out.set(pcm,64+16*(slot%5));return out;}
function simulate(name,policy,guard=0,chunk=511,timer="absolute",hooks={}){
  assert.ok(cases.includes(name)&&policies.includes(policy)&&[0,640,"adaptive"].includes(guard)&&["absolute","scaled"].includes(timer)&&!(guard==="adaptive"&&timer==="scaled")&&Number.isInteger(chunk)&&chunk>0);
  const cfg=config(name),period=STEP+(typeof guard==="number"?guard:0),timerStep=timer==="scaled"?period:STEP,epochs=[],pcm=new Int16Array(HORIZON),current=new Map(),records=new Map(),queue=[],received=new Set(),returns=new Map(),trace=[],evidence=[];
  let now=0,oi=0;const m={offered:0,dataAttempts:0,retries:0,acks:0,uniqueReceipts:0,duplicates:0,confirmations:0,genuineConfirmations:0,invalid:0,freshAtAck:0,staleAtAck:0,unmatchedAck:0,replayAck:0,expiredAck:0,droppedAck:0,refusedData:0,opportunities:0,idleSlots:0,lateEvidence:0,overflow:0};
  const log=(at,type,extra={})=>trace.push({at,type,...extra});
  function offers(at){while(oi<cfg.offers.length&&cfg.offers[oi][0]<=at){const [t,p]=cfg.offers[oi++];current.set(p.source,p.version);records.set(key(p),{packet:p,attempts:0,ready:t,confirmed:false});m.offered++;log(t,'offer',{packet:p});}}
  function expire(at){for(let i=queue.length-1;i>=0;i--)if(at>=queue[i].expires){const [r]=queue.splice(i,1);m.expiredAck++;log(at,'return-expired',{packet:r.packet,expires:r.expires});}}
  const stream=(hooks.receiver||(emit=>new Stream(emit)))(e=>{
    offers(e.at);expire(e.at);evidence.push(e);log(e.at,'evidence',{status:e.status,start:e.start,end:e.end});if(e.status==='overflow')m.overflow++;if(e.status!=='ok')return;
    const r=e.packet,k=key(r),epoch=epochs.findLast(t=>t<=e.start);
    // Shared transmit epoch grid is known; onset and packet identity are recovered from PCM.
    assert.ok(epoch!==undefined);if(e.at>epoch+STEP)m.lateEvidence++;
    if(r.kind===0){const route=r.source===1?[2,1]:r.source===2?[3,2]:null,accepted=!!route&&r.actor===route[0]&&r.event===route[1]&&r.version===current.get(r.source);log(e.at,'data-receipt',{packet:r,accepted});if(!accepted){m.refusedData++;return;}
      if(received.has(k))m.duplicates++;else{received.add(k);m.uniqueReceipts++;}
      const ready=Math.max(e.at,epoch+cfg.delay*timerStep),expires=epoch+cfg.ttl*timerStep;
      if(expires<=e.at){m.expiredAck++;log(e.at,'return-expired',{packet:r,expires});}
      else if(!queue.some(a=>key(a.packet)===k)){if(queue.length>=4){m.droppedAck++;log(e.at,'return-overflow',{packet:r});}else{queue.push({packet:{...r,kind:1},ready,expires,evidenceAt:e.at});log(e.at,'return-enqueued',{packet:r,ready,expires});}}
    }else{const rec=records.get(k),accepted=!!rec&&rec.attempts>0&&!rec.confirmed,fresh=r.version===current.get(r.source);
      if(accepted){rec.confirmed=true;m.confirmations++;if(fresh)m.freshAtAck++;else m.staleAtAck++;}else if(rec?.confirmed)m.replayAck++;else m.unmatchedAck++;
      const genuine=received.has(k);if(accepted){if(genuine)m.genuineConfirmations++;else m.invalid++;}log(e.at,'ack-receipt',{packet:r,accepted,fresh,evaluatorGenuine:genuine});
    }
  });
  function feed(until){while(now<until){offers(now);const next=Math.min(until,now+chunk,oi<cfg.offers.length?cfg.offers[oi][0]:Infinity);stream.push(pcm.subarray(now,next));now=next;}offers(now);expire(now);}
  for(let slot=0,at=0;at+STEP<=HORIZON;slot++){feed(at);epochs.push(at);m.opportunities++;
    const data=[...records.values()].filter(r=>!r.confirmed&&r.attempts<2&&r.ready<=at&&current.get(r.packet.source)===r.packet.version),ret=queue.filter(r=>r.ready<=at&&at<r.expires);
    let p=null,fault='clean',origin='idle',evidenceAt=null;
    if((name==='forged'||name==='wrong-actor')&&slot===1){p={...A,kind:1,...(name==='wrong-actor'?{actor:4}:{})};origin='fixture-return';}
    else if(name==='replay'&&slot===4){p={...A,kind:1};origin='fixture-return';}
    else if(ret.length&&(policy==='ack-first'||(policy==='reserve'&&slot%3===2)||!data.length)){const r=ret[0];queue.splice(queue.indexOf(r),1);p=r.packet;evidenceAt=r.evidenceAt;origin='return';assert.ok(evidenceAt<=at);}
    else if(data.length){const r=data[0];p=r.packet;origin='data';r.attempts++;r.ready=at+3*timerStep;m.dataAttempts++;if(r.attempts>1)m.retries++;
      if(r.attempts===1&&p.source===1&&p.version===2){if(name==='data-loss'||name==='forged')fault='lost';if(name==='drift')fault='drift';}if(name==='persistent-loss'&&p.source===1)fault='lost';}
    if(p?.kind===1){m.acks++;const k=key(p),n=(returns.get(k)||0)+1;returns.set(k,n);if(name==='ack-loss'&&p.source===1&&n===1)fault='lost';}
    if(p)pcm.set(channel(p,fault,slot),at);else m.idleSlots++;if(hooks.interference)hooks.interference(pcm,at,slot,p,origin);log(at,'tx',{slot,packet:p,origin,fault,evidenceAt});feed(at+STEP);const nominal=at+STEP;let next=at+period;if(guard==="adaptive"){next=nominal;while(next<Math.min(HORIZON,nominal+640)&&(stream.readiness?stream.readiness().acquisition==='pending':(stream.cluster||stream.pending.length)&&!stream.overflow)){next=Math.min(HORIZON,nominal+640,next+16);feed(next);}}log(now,'turnaround',{nominal,next,wait:next-nominal});at=next;
  }
  feed(HORIZON);stream.finish();
  m.genuineCurrentConfirmed=[...records.entries()].filter(([k,r])=>received.has(k)&&r.confirmed&&current.get(r.packet.source)===r.packet.version).length;
  m.unconfirmed=[...records.values()].filter(r=>!r.confirmed).length;m.returnBacklog=queue.length;
  m.missedNextBoundary=evidence.filter(e=>e.status==='ok'&&epochs.some((t,i)=>i+1<epochs.length&&t<=e.start&&e.start<epochs[i+1]&&e.at>epochs[i+1])).length;
  m.totalWaitSamples=trace.filter(e=>e.type==='turnaround').reduce((a,e)=>a+e.wait,0);
  return {name,policy,guard,timer,timerStep,period,samples:HORIZON,metrics:m,trace,evidence,stats:stream.stats,pcm};
}
module.exports={simulate,cases,policies,config};
