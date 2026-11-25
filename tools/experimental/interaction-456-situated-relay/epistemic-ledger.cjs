'use strict';
// Interaction lane, Refs #456 / Draft #457. AI-assisted, synthetic only.
// Parent 809489feb21ba23662fe5bd2b113cb3d2752e15a; grammar handoff b18e9fa1a5d5d2405245e3999125d12c5ac37c7c read, not a runtime dependency.
// New 48-code stand-in; no interoperation or authentication. Shared scripted world/deadline context; no durable epoch allocation.
// Receiver records actual decoded DATA. History records local receipt time, not untransmitted lookup time. Current eligibility is evaluated separately.
// 24 slots, 200 ms each, 100 ms body; archive capacity 3, retention 8 slots, at most two requests per address. Equal horizon, unequal realized airtime.
const implementation=function implementation(parent){
 const RATE=16000,SLOT=3200,FRAME=1600,H=24;
 const policies=["silent-tag","negative-stop","negative-retry","negative-untagged"];
 const cases=["revision","churn","lost-data","lost-ack","late-archive","slow-reply","old-positive","old-negative","session-positive","session-negative"];
 const basis=Array.from({length:4},(_,n)=>Array.from({length:400},(_,i)=>[Math.cos(2*Math.PI*(400+80*n)*i/RATE),Math.sin(2*Math.PI*(400+80*n)*i/RATE)]));
 // New disjoint stand-in: 12 current + 36 historical control expressions; no legacy interoperability.
 function encode(p){const {kind,address,tag=0}=p;if(!Number.isInteger(address)||address<0||address>=6||!Number.isInteger(kind)||kind<0||kind>4||![0,1].includes(tag)||(kind<2&&tag!==0))throw Error("packet");return kind<2?2*address+kind:12+6*address+2*(kind-2)+tag;}
 function wave(n,seed,loss=false){return parent.render({kind:n%4,source:1+(n>>2)%4,version:1+(n>>4)},seed,loss);}
 function decode(w){if(w.length!==SLOT)throw Error("slot length");const s=[];for(let j=0;j<4;j++){const v=basis.map(b=>{let x=0,y=0;for(let i=0;i<400;i++){x+=w[j*400+i]*b[i][0];y+=w[j*400+i]*b[i][1];}return x*x+y*y;});const peak=Math.max(...v),n=v.indexOf(peak);v[n]=0;if(peak<1e10||peak<4*Math.max(...v))return null;s.push(n);}
 const n=s[0]+4*s[1]+16*s[2];if(n>=48||s[3]!==((s[0]+2*s[1]+3*s[2])%4))return null;return n<12?{address:n>>1,kind:n%2,tag:0}:{address:Math.floor((n-12)/6),kind:2+Math.floor((n-12)%6/2),tag:n%2};}
 const source=a=>Math.floor(a/3);
 function simulate({name,policy,ttl,seed,interest,requestLoss,replyLoss}){
 if(!cases.includes(name)||!policies.includes(policy)||![2,4,6].includes(ttl)||!["all","source0"].includes(interest))throw Error("config");
 const offers=[[0,0],[0,3],[3,1],[6,4]];if(name==="churn")offers.push([5,2],[8,5]);
 if(name==="late-archive")offers.splice(1);
 const current=new Map(),records=new Map(),receiver=new Map(),currentReturns=[],staging=[],archive=new Map(),historicalReturns=[],trace=[],pcm=new Int16Array(H*SLOT);
 const metrics={data:0,currentAck:0,request:0,positive:0,negative:0,fixture:0,idle:0,erased:0,received:0,currentConfirmed:0,currentGenuineSamples:0,currentReceivedSamples:0,historicalGenuine:0,historicalFalse:0,wrongCorrespondence:0,negativeAccepted:0,negativeWrong:0,negativeThenPositive:0,expired:0,evicted:0,archiveInserted:0,archiveHits:0,archiveMisses:0,rejected:0};
 let serial=0,lostReq=false,lostReply=false,fixtureSent=false;
 const log=(slot,type,fields={})=>trace.push({slot,atSample:slot*SLOT+(type==="rx"?FRAME:0),type,...fields});
 const useful=(a,t)=>{const r=records.get(a);return !!r&&current.get(source(a))===a&&t<r.offer+ttl;};
 const wanted=a=>interest==="all"||source(a)===0;
 const tagged=policy!=="negative-untagged", negative=policy!=="silent-tag", stop=policy==="negative-stop";
 for(let t=0;t<H;t++){
  for(const [when,a] of offers)if(when===t){records.set(a,{address:a,offer:t,tries:0,next:t,currentConfirmed:false,historyConfirmed:false,historyStopped:false,attempts:[],negatives:[],history:[]});current.set(source(a),a);log(t,"offer",{address:a});}
  for(const [a,r] of records){const q=r.attempts.at(-1);if(q&&q.open&&t>q.until){q.open=false;r.history.push({kind:"unanswered",at:t,tag:q.tag});log(t,"timeout",{address:a,tag:q.tag});}}
  // Receiver retains only evidence from actually decoded current DATA. No sender acknowledgement oracle.
  for(const [a,r] of receiver)if(!useful(a,t)&&!r.staged){r.staged=true;staging.push({address:a,observed:r.observed,ready:t+(name==="late-archive"?3:0)});log(t,"archive-stage",{address:a,observed:r.observed});}
  for(const [a,x] of archive)if(x.expires<=t){archive.delete(a);metrics.expired++;log(t,"archive-expire",{address:a});}
  for(let j=0;j<staging.length;){const x=staging[j];if(x.ready>t){j++;continue;}staging.splice(j,1);if(archive.size===3){const a=archive.keys().next().value;archive.delete(a);metrics.evicted++;log(t,"archive-evict",{address:a});}archive.set(x.address,{...x,expires:t+8});metrics.archiveInserted++;log(t,"archive-insert",{address:x.address,observed:x.observed,expires:t+8});}
  for(let j=currentReturns.length-1;j>=0;j--)if(!useful(currentReturns[j].address,t))currentReturns.splice(j,1);
  const ret=currentReturns.findIndex(x=>x.ready<=t);
  const data=[...records.values()].find(r=>useful(r.address,t)&&!r.currentConfirmed&&r.tries<2&&r.next<=t);
  const target=[...records.values()].find(r=>wanted(r.address)&&r.tries>0&&!r.currentConfirmed&&!r.historyConfirmed&&!r.historyStopped&&!useful(r.address,t)&&r.attempts.length<2&&!r.attempts.at(-1)?.open);
  const old=[...records.values()].find(r=>r.attempts.at(-1)?.open&&r.attempts.length>=(name.startsWith("session")?1:2)&&!r.historyConfirmed&&!r.historyStopped);
  const hr=historicalReturns.findIndex(x=>x.ready<=t);
  let p=null,origin="",loss=false,meta=null;
  // Fixture owns a slot only when no current work competes. It is an externally supplied synthetic obsolete body.
  if(ret>=0){const x=currentReturns.splice(ret,1)[0];p={address:x.address,kind:1,tag:0};origin="currentAck";loss=(name==="lost-ack"||name==="late-archive")&&x.address===0;}
  else if(data){p={address:data.address,kind:0,tag:0};origin="data";data.tries++;data.next=t+3;loss=(name==="lost-data"||name.includes("positive")||name.includes("negative"))&&data.address===0;}
  else if(old&&!fixtureSent&&(name.startsWith("old-")||name.startsWith("session-"))){p={address:old.address,kind:name.endsWith("positive")?3:4,tag:0};origin="fixture";fixtureSent=true;}
  else if(hr>=0){meta=historicalReturns.splice(hr,1)[0];p=meta.packet;origin=p.kind===3?"positive":"negative";loss=replyLoss&&!lostReply;lostReply=true;}
  else if(target){const tag=tagged?target.attempts.length:0;meta={id:++serial,tag,at:t,until:t+4,open:true};target.attempts.push(meta);p={address:target.address,kind:2,tag};origin="request";loss=requestLoss&&!lostReq;lostReq=true;}
  if(!p){metrics.idle++;log(t,"idle");}
  else {
   metrics[origin]++;if(loss)metrics.erased++;log(t,"tx",{packet:p,origin,loss,attemptId:meta?.id??null,lookupSlot:meta?.lookupSlot??null});
   const w=wave(encode(p),seed+t*997,loss);pcm.set(w,t*SLOT);const d=decode(w);
   if(d){const r=records.get(d.address);log(t,"rx",{packet:d,origin});
    if(d.kind===0){if(useful(d.address,t)){if(!receiver.has(d.address)){receiver.set(d.address,{observed:t,staged:false});metrics.received++;}if(!currentReturns.some(x=>x.address===d.address))currentReturns.push({address:d.address,ready:t+1});}}
    else if(d.kind===1){if(useful(d.address,t)&&r.tries>0&&!r.currentConfirmed){r.currentConfirmed=true;metrics.currentConfirmed++;log(t,"current-confirm",{address:d.address});}}
    else if(d.kind===2){const a=archive.get(d.address);metrics[a?"archiveHits":"archiveMisses"]++;log(t,"lookup",{address:d.address,tag:d.tag,found:!!a,id:meta.id,observed:a?.observed??null});
     if(a||negative)historicalReturns.push({id:meta.id,lookupSlot:t,observed:a?.observed??null,packet:{address:d.address,kind:a?3:4,tag:d.tag},ready:t+(name==="slow-reply"?6:1)});
    }else{const q=r?.attempts.at(-1);const admissible=!!q&&q.open&&t<=q.until&&q.tag===d.tag&&!useful(d.address,t)&&!r.currentConfirmed&&!r.historyConfirmed&&!r.historyStopped;
     const matched=origin!=="fixture"&&meta?.id===q?.id;log(t,"historical-admission",{address:d.address,tag:d.tag,kind:d.kind,admissible,evaluatorMatched:matched,evaluatorLookupSlot:meta?.lookupSlot??null});
     if(!admissible)metrics.rejected++;
     else{q.open=false;if(!matched)metrics.wrongCorrespondence++;
      // Receiver timestamps and evaluator attempt IDs are not exposed to the requester. Only receipt time is known.
      r.history.push({kind:d.kind===3?"reported-received":"reported-unavailable",at:t,tag:d.tag});
      if(d.kind===3){r.historyConfirmed=true;metrics[origin==="fixture"?"historicalFalse":"historicalGenuine"]++;if(r.negatives.length)metrics.negativeThenPositive++;}
      else{r.negatives.push({at:t,tag:d.tag});metrics.negativeAccepted++;if(!matched)metrics.negativeWrong++;if(stop)r.historyStopped=true;}
     }
    }
   }else log(t,"decode-refusal");
  }
  // Sample-weighted availability after the body decode point; no historic reply updates current state.
  for(const [a,r] of records)if(useful(a,t)){const wasReceived=receiver.has(a),wasConfirmed=r.currentConfirmed;
   const rx=trace.at(-1); // use explicit events, not future state
   const newData=trace.some(e=>e.slot===t&&e.type==="rx"&&e.packet.kind===0&&e.packet.address===a)&&receiver.get(a)?.observed===t;
   const newAck=trace.some(e=>e.slot===t&&e.type==="current-confirm"&&e.address===a);
   if(wasReceived)metrics.currentReceivedSamples+=newData?SLOT-FRAME:SLOT;
   if(wasConfirmed&&wasReceived)metrics.currentGenuineSamples+=newAck?SLOT-FRAME:SLOT;
  }
 }
 for(const [a,r] of records){const q=r.attempts.at(-1);if(q?.open){q.open=false;r.history.push({kind:"unresolved-at-horizon",at:H,tag:q.tag});}}
 return {name,policy,ttl,seed,interest,requestLoss,replyLoss,metrics,ledger:[...records.values()],trace,pcm};
 }
 function qualify(){let checks=0;const ck=(v,m)=>{checks++;if(!v)throw Error(m);};for(let a=0;a<6;a++)for(let k=0;k<5;k++)for(let tag=0;tag<(k<2?1:2);tag++){const p={address:a,kind:k,tag};ck(JSON.stringify(decode(wave(encode(p),31)))===JSON.stringify(p),"roundtrip");ck(decode(wave(encode(p),31,true))===null,"erasure");}for(let n=48;n<64;n++)ck(decode(wave(n,31))===null,"unused code");
 const rows=[],specimens=[],aggregate={};const fields=["data","currentAck","request","positive","negative","fixture","idle"];
 for(const seed of [4421,93199])for(const name of cases)for(const ttl of [2,4,6])for(const interest of ["all","source0"])for(const requestLoss of [false,true])for(const replyLoss of [false,true])for(const policy of policies){
 const s=simulate({name,policy,ttl,seed,interest,requestLoss,replyLoss}),m=s.metrics;ck(fields.reduce((a,k)=>a+m[k],0)===H,"slot partition");ck(s.pcm.every(x=>Math.abs(x)<=3080),"peak");
 ck(s.ledger.every(r=>r.attempts.length<=2&&r.tries<=2),"bounded attempts");
 ck(s.trace.filter(e=>e.type==="archive-insert").every(e=>s.trace.some(x=>x.type==="rx"&&x.packet.kind===0&&x.packet.address===e.address&&x.slot===e.observed&&x.slot<=e.slot)),"archive provenance");
 ck(s.trace.filter(e=>e.type==="tx"&&(e.origin==="positive"||e.origin==="negative")).every(e=>s.trace.some(x=>x.type==="lookup"&&x.id===e.attemptId&&x.slot===e.lookupSlot&&x.found===(e.origin==="positive")&&x.slot<e.slot)),"reply provenance");
 ck(s.trace.filter(e=>e.type==="historical-admission"&&e.admissible).every(e=>s.trace.some(x=>x.type==="tx"&&x.origin==="request"&&x.packet.address===e.address&&x.packet.tag===e.tag&&x.slot<e.slot&&e.slot<=x.slot+4)),"window");
 ck(m.currentGenuineSamples<=m.currentReceivedSamples,"genuine subset");
 ck(s.ledger.every(r=>!r.historyConfirmed||!r.currentConfirmed),"separate historical and current ledger");
 ck(m.historicalGenuine+m.historicalFalse===s.ledger.filter(r=>r.historyConfirmed).length,"confirmation partition");
 const {pcm,trace,ledger,...row}=s;rows.push(row);const a=aggregate[policy]??(aggregate[policy]={runs:0});a.runs++;for(const k of Object.keys(m))a[k]=(a[k]??0)+m[k];
 if(seed===4421&&ttl===2&&interest==="all"&&!requestLoss&&!replyLoss&&["late-archive","old-positive","session-negative"].includes(name))specimens.push(s);
 }
 let currentDifferences=0;const index=new Map(rows.map(x=>[[x.seed,x.name,x.ttl,x.interest,x.requestLoss,x.replyLoss,x.policy].join("/"),x]));for(const r of rows.filter(x=>x.policy==="silent-tag"))for(const p of policies.slice(1)){const b=index.get([r.seed,r.name,r.ttl,r.interest,r.requestLoss,r.replyLoss,p].join("/"));if(b.metrics.currentGenuineSamples!==r.metrics.currentGenuineSamples||b.metrics.currentReceivedSamples!==r.metrics.currentReceivedSamples)currentDifferences++;}
 return {receipt:{schema:"mhac-interaction-epistemic-ledger-v1",rate:RATE,slotSamples:SLOT,bodySamples:FRAME,checks,rows,aggregate,currentDifferences},specimens};
 }
 return {simulate,qualify,encode,decode,wave,cases,policies};
};
const api=implementation(require('./narrow-deadline-relay.cjs')); module.exports=api;
if(require.main===module){
 const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
 const b=fs.readFileSync(path.join(__dirname,'narrow-deadline-relay.cjs'));
 const pin='10ed127dd84aee591f1addfa02fd1e2931114d67';
 if(crypto.createHash('sha1').update('blob '+b.length+'\0').update(b).digest('hex')!==pin)throw Error('parent mismatch');
 const out=process.argv[2]||'epistemic-ledger-output';fs.mkdirSync(out,{recursive:true});
 const {receipt,specimens}=api.qualify();receipt.parentRef='809489feb21ba23662fe5bd2b113cb3d2752e15a';receipt.parentBlob=pin;receipt.stimuli=[];
 for(const s of specimens){const stem=s.name+'-'+s.policy,buf=Buffer.alloc(44+2*s.pcm.length);buf.write('RIFF');buf.writeUInt32LE(buf.length-8,4);buf.write('WAVEfmt ',8);buf.writeUInt32LE(16,16);buf.writeUInt16LE(1,20);buf.writeUInt16LE(1,22);buf.writeUInt32LE(16000,24);buf.writeUInt32LE(32000,28);buf.writeUInt16LE(2,32);buf.writeUInt16LE(16,34);buf.write('data',36);buf.writeUInt32LE(buf.length-44,40);s.pcm.forEach((x,i)=>buf.writeInt16LE(Math.round(x/2),44+2*i));fs.writeFileSync(path.join(out,stem+'.wav'),buf);const {pcm,...trace}=s;fs.writeFileSync(path.join(out,stem+'.json'),JSON.stringify(trace,null,2));receipt.stimuli.push({stem,gain:.5,sha256:crypto.createHash('sha256').update(buf).digest('hex')});}
 fs.writeFileSync(path.join(out,'receipt.json'),JSON.stringify(receipt,null,2));
 const html='<!doctype html><meta charset=utf-8><title>Epistemic ledger</title><style>body{font:16px system-ui;max-width:1100px;margin:2em auto;padding:1em}td,th{padding:.4em;border:1px solid #aaa}table{border-collapse:collapse}</style><h1>Situated epistemic ledger</h1><p>Synthetic historical reports are not current confirmations. No autoplay; begin at low volume. Tags are not authentication.</p><label>Scenario <select id="case">'+api.cases.map(x=>'<option>'+x+'</option>').join('')+'</select></label> <label>TTL <select id="ttl"><option>2</option><option>4</option><option>6</option></select></label> <label>Interest <select id="interest"><option>all</option><option>source0</option></select></label> <label><input id="loss" type="checkbox"> First request erased</label> <label><input id="reply" type="checkbox"> First history reply erased</label><div id="v"></div><h2>Original half-gain specimens</h2>'+receipt.stimuli.map(x=>'<p>'+x.stem+' <audio controls preload=none src="'+x.stem+'.wav"></audio> <a href="'+x.stem+'.json">ledger and trace</a></p>').join('')+'<script>const rows='+JSON.stringify(receipt.rows.filter(x=>x.seed===4421))+';const c=document.getElementById("case"),t=document.getElementById("ttl"),i=document.getElementById("interest"),l=document.getElementById("loss"),r=document.getElementById("reply"),v=document.getElementById("v");function draw(){v.innerHTML="<table><tr><th>Policy</th><th>Current genuine ms</th><th>Historical genuine</th><th>Historical false</th><th>Wrong correspondence</th><th>Negatives</th><th>Negative then positive</th><th>Requests</th></tr>"+rows.filter(x=>x.name===c.value&&x.ttl===+t.value&&x.interest===i.value&&x.requestLoss===l.checked&&x.replyLoss===r.checked).map(x=>"<tr>"+[x.policy,x.metrics.currentGenuineSamples/16,x.metrics.historicalGenuine,x.metrics.historicalFalse,x.metrics.wrongCorrespondence,x.metrics.negativeAccepted,x.metrics.negativeThenPositive,x.metrics.request].map(y=>"<td>"+y+"</td>").join("")+"</tr>").join("")+"</table>"}c.onchange=t.onchange=i.onchange=l.onchange=r.onchange=draw;draw()</script>';fs.writeFileSync(path.join(out,'index.html'),html);
 console.log(JSON.stringify({checks:receipt.checks,rows:receipt.rows.length,aggregate:receipt.aggregate,currentDifferences:receipt.currentDifferences,stimuli:receipt.stimuli.length}));
}

// Two identical V8 computational receipts; native export/browser/audition not executed.
// {"checks":17392,"rows":1920,"aggregate":{"silent-tag":{"runs":480,"data":1840,"currentAck":1424,"request":762,"positive":166,"negative":0,"fixture":192,"idle":7136,"erased":616,"received":1568,"currentConfirmed":1312,"currentGenuineSamples":9062400,"currentReceivedSamples":14387200,"historicalGenuine":90,"historicalFalse":48,"wrongCorrespondence":96,"negativeAccepted":48,"negativeWrong":48,"negativeThenPositive":0,"expired":1408,"evicted":160,"archiveInserted":1568,"archiveHits":166,"archiveMisses":408,"rejected":96},"negative-stop":{"runs":480,"data":1840,"currentAck":1424,"request":656,"positive":148,"negative":320,"fixture":168,"idle":6964,"erased":708,"received":1568,"currentConfirmed":1312,"currentGenuineSamples":9062400,"currentReceivedSamples":14387200,"historicalGenuine":94,"historicalFalse":48,"wrongCorrespondence":96,"negativeAccepted":230,"negativeWrong":48,"negativeThenPositive":0,"expired":1408,"evicted":160,"archiveInserted":1568,"archiveHits":148,"archiveMisses":320,"rejected":96},"negative-retry":{"runs":480,"data":1840,"currentAck":1424,"request":770,"positive":134,"negative":448,"fixture":192,"idle":6712,"erased":718,"received":1568,"currentConfirmed":1312,"currentGenuineSamples":9062400,"currentReceivedSamples":14387200,"historicalGenuine":82,"historicalFalse":48,"wrongCorrespondence":96,"negativeAccepted":346,"negativeWrong":48,"negativeThenPositive":0,"expired":1408,"evicted":160,"archiveInserted":1568,"archiveHits":134,"archiveMisses":448,"rejected":120},"negative-untagged":{"runs":480,"data":1840,"currentAck":1424,"request":770,"positive":134,"negative":448,"fixture":192,"idle":6712,"erased":718,"received":1568,"currentConfirmed":1312,"currentGenuineSamples":9062400,"currentReceivedSamples":14387200,"historicalGenuine":82,"historicalFalse":96,"wrongCorrespondence":192,"negativeAccepted":318,"negativeWrong":96,"negativeThenPositive":12,"expired":1408,"evicted":160,"archiveInserted":1568,"archiveHits":134,"archiveMisses":448,"rejected":100}},"currentDifferences":0,"comparisons":1440,"specimens":12}
