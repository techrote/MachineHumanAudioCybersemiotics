'use strict';
const {EpochReceiver}=require('./epoch-v7.cjs'),v1=require('./relay.cjs'),v2=require('./bound-v2.cjs');
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const Z=n=>new Int16Array(n),eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b),hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const STEP=32640,H=8*STEP,base=v1.base,key=p=>JSON.stringify({...p,kind:0}),modes=['sticky','peak512','cooldown'];
let checks=0;const check=(b,m)=>{checks++;assert.ok(b,m);};
function run(seed,scenario,mode,chunk=511){
  const A={...base,seq:1+seed%16},B={...A,version:3,seq:1+(seed+1)%16,tree:['question',['open']]};
  const raw=v2.render(A,seed/997),flood=v1.join(...Array.from({length:10},()=>v1.join(raw.slice(0,640),Z(640))));
  const pcm=Z(H),events=[],trace=[],ledger=new Set(),confirmed=new Set(),sent=new Set();let now=0,version=2,queue=null;
  let duplicates=0,stale=0,attempts=0,overflows=0;
  const r=new EpochReceiver(e=>{
    events.push(e);if(e.status==='overflow')overflows++;if(e.status!=='ok')return;
    const p=e.packet,k=key(p);if(p.kind===0){
      if(p.version!==version){stale++;trace.push({at:e.at,type:'stale',packet:p});return;}
      if(ledger.has(k))duplicates++;else ledger.add(k);
      queue={packet:{...p,kind:1},at:e.at};trace.push({at:e.at,type:'receipt',packet:p});
    }else if(sent.has(k)&&p.version===version){confirmed.add(k);trace.push({at:e.at,type:'confirmation',packet:p});}
  },mode);
  function feed(end){while(now<end){let n=Math.min(end,now+chunk);r.push(pcm.subarray(now,n));now=n;}}
  for(let slot=0;slot<8;slot++){
    const at=slot*STEP;feed(at);if(slot===2&&scenario==='revision')version=3;
    let p=null,signal=null,origin='idle';
    if(slot===0||slot===3||slot===5&&scenario==='revision'){
      p=slot===5?B:A;sent.add(key(p));attempts++;origin='data';signal=v2.render(p,seed/997+slot*.2);
      if(slot===3&&scenario==='weak')signal=Int16Array.from(signal,x=>Math.round(x/8));
    }else if(slot===1){ // lost return + onset overload, identical offered interference
      check(!queue||queue.at<=at,'causal lost return');queue=null;origin='lost-return-plus-overload';signal=flood;
      if(scenario==='tone')signal=v1.join(flood,Int16Array.from({length:STEP-128-flood.length},(_,i)=>Math.round(220*Math.sin(2*Math.PI*2300*i/16000))));
      if(scenario==='impulses'){signal=v1.join(flood,Z(STEP-128-flood.length));for(let i=flood.length+2000;i<signal.length;i+=6000)signal[i]=256;}
    }else if(queue){check(queue.at<=at,'causal return');p=queue.packet;queue=null;origin='return';signal=v2.render(p,seed/997+slot*.2);}
    if(signal)pcm.set(signal,at+64);trace.push({at,type:'tx',origin,packet:p,readiness:r.readiness()});
    feed(at+STEP);
  }
  const readiness=r.finish();return {seed,scenario,mode,pcm,events,trace,readiness,metrics:{receipts:ledger.size,duplicates,stale,attempts,overflows,confirmations:confirmed.size,genuine:[...confirmed].filter(k=>ledger.has(k)).length,rearms:events.filter(e=>e.status==='rearm').length}};
}
function main(out){fs.mkdirSync(out,{recursive:true});const rows=[];
  for(const seed of [34019,78233])for(const scenario of ['clean','weak','tone','impulses','revision'])for(const mode of modes){
    const {pcm,...r}=run(seed,scenario,mode);const again=run(seed,scenario,mode,127);
    check(eq(r.events,again.events)&&eq(r.trace,again.trace)&&eq(r.metrics,again.metrics),'partition invariance');
    check(r.metrics.overflows>=1,'overflow exercised');check(r.metrics.genuine===r.metrics.confirmations,'fixture confirmation provenance');
    check(r.events.every((e,i)=>e.at<=H&&(!i||e.at>=r.events[i-1].at)),'monotone time');
    check(r.events.filter(e=>e.status==='rearm').every(e=>e.discardedFrom<e.at&&e.possibleUnresolvedFrom<=e.discardedFrom),'loss interval');
    check(r.metrics.receipts>=1,'pre-overload receipt retained');
    if(mode==='cooldown'){check(r.metrics.genuine===1,'recovered return');check(scenario==='revision'?r.metrics.stale===1&&r.metrics.receipts===2:r.metrics.duplicates===1&&r.metrics.receipts===1,'semantic ledger survives epoch');}
    const file=`${scenario}-${seed}-${mode}.wav`,bytes=v1.wav(pcm);fs.writeFileSync(path.join(out,file),bytes);
    const read=fs.readFileSync(path.join(out,file));check(hash(read)===hash(bytes)&&read.length===44+H*2,'filesystem');
    const replay=new EpochReceiver(e=>events.push(e),mode),events=[];const x=new Int16Array(1);for(let i=44;i<read.length;i+=2){x[0]=read.readInt16LE(i);replay.push(x);}replay.finish();check(eq(events,r.events),'PCM rescan');
    rows.push({...r,file,sha256:hash(bytes),samples:H});
  }
  const summary=modes.map(mode=>{const a=rows.filter(r=>r.mode===mode);return {mode,sessions:a.length,...Object.fromEntries(Object.keys(a[0].metrics).map(k=>[k,a.reduce((s,r)=>s+r.metrics[k],0)]))};});
  // Held-out close-arrival and repeated-overload controls, no scheduled boundaries.
  const stress=[];
  for(const seed of [34019,78233]){
    const A={...base,seq:1+seed%16},B={...A,seq:1+(seed+1)%16,tree:['question',['open']]};
    const a=v2.render(A,seed/997),b=v2.render(B,seed/991),weak=Int16Array.from(a,x=>Math.round(x/8));
    const flood=n=>v1.join(...Array.from({length:n},()=>v1.join(a.slice(0,640),Z(640))));
    for(const [scenario,signal] of [['early-weak',v1.join(flood(10),Z(4000),weak,Z(24000),b,Z(2400))],['continued-overload',v1.join(flood(70),Z(24000),b,Z(2400))]]){
      const file=`stress-${scenario}-${seed}.wav`,bytes=v1.wav(signal);fs.writeFileSync(path.join(out,file),bytes);
      for(const mode of modes){const events=[],r=new EpochReceiver(e=>events.push(e),mode,scenario==='continued-overload'?1:4);
        r.push(signal);const final=r.finish(),ok=events.filter(e=>e.status==='ok').map(e=>e.packet);
        check(ok.every(p=>eq(p,A)||eq(p,B)),'no novel identity in stress');check(final.epoch<=(scenario==='continued-overload'?1:4),'reset budget');
        if(scenario==='continued-overload'&&mode==='cooldown')check(final.acquisition==='overloaded'&&ok.length===0,'bounded fail closed');
        if(scenario==='early-weak'&&mode==='cooldown')check(eq(ok,[A,B]),'close weak recovery');
        if(scenario==='early-weak'&&mode==='peak512')check(eq(ok,[B]),'quiet reset loses weak packet');
        stress.push({seed,scenario,mode,file,sha256:hash(bytes),samples:signal.length,ok,final,events});
      }
    }
  }
  const receipt={schema:'mhac-epoch-v7',node:process.version,rate:16000,checks,summary,rows,stress};fs.writeFileSync(path.join(out,'receipt.json'),JSON.stringify(receipt,null,2)+'\n');console.log(JSON.stringify({checks,summary,stress:stress.map(({seed,scenario,mode,ok,final})=>({seed,scenario,mode,accepted:ok.length,final:final.acquisition}))}));
}
if(require.main===module)main(process.argv[2]||'epoch-v7-output');
module.exports={run};
