'use strict';
// Interaction lane Refs #456, Draft/HOLD #457. Synthetic only, AI-assisted single agent.
// Derived from exact epistemic-ledger.cjs at 4e9f7120f137256fb8ba0736af51be7caacebc1f (blob ae2c8370191b0698263be6823a34df6e4a65bda0).
// All five policies tagged; same request cap, unequal realized airtime. Deadline estimate uses only shared offer/TTL context, not archive oracle.
const implementation=function implementation(parent){
 const RATE=16000,SLOT=3200,FRAME=1600,H=24;
 const policies=["stop","retry","rotate","cooldown","deadline"];
 const cases=["revision","churn","lost-data","lost-ack","late-archive","slow-reply","old-positive","old-negative","session-positive","session-negative"];
 const basis=Array.from({length:4},(_,n)=>Array.from({length:400},(_,i)=>[Math.cos(2*Math.PI*(400+80*n)*i/RATE),Math.sin(2*Math.PI*(400+80*n)*i/RATE)]));
 // New disjoint stand-in: 12 current + 36 historical control expressions; no legacy interoperability.
 function encode(p){const {kind,address,tag=0}=p;if(!Number.isInteger(address)||address<0||address>=6||!Number.isInteger(kind)||kind<0||kind>4||![0,1].includes(tag)||(kind<2&&tag!==0))throw Error("packet");return kind<2?2*address+kind:12+6*address+2*(kind-2)+tag;}
 function wave(n,seed,loss=false){return parent.render({kind:n%4,source:1+(n>>2)%4,version:1+(n>>4)},seed,loss);}
 function decode(w){if(w.length!==SLOT)throw Error("slot length");const s=[];for(let j=0;j<4;j++){const v=basis.map(b=>{let x=0,y=0;for(let i=0;i<400;i++){x+=w[j*400+i]*b[i][0];y+=w[j*400+i]*b[i][1];}return x*x+y*y;});const peak=Math.max(...v),n=v.indexOf(peak);v[n]=0;if(peak<1e10||peak<4*Math.max(...v))return null;s.push(n);}
 const n=s[0]+4*s[1]+16*s[2];if(n>=48||s[3]!==((s[0]+2*s[1]+3*s[2])%4))return null;return n<12?{address:n>>1,kind:n%2,tag:0}:{address:Math.floor((n-12)/6),kind:2+Math.floor((n-12)%6/2),tag:n%2};}
 const source=a=>Math.floor(a/3);
 function simulate({name,policy,ttl,seed,interest,requestLoss,replyLoss,cap}){
 if(!cases.includes(name)||!policies.includes(policy)||![2,4,6].includes(ttl)||!["all","source0"].includes(interest)||![2,4].includes(cap))throw Error("config");
 const offers=[[0,0],[0,3],[3,1],[6,4]];if(name==="churn")offers.push([5,2],[8,5]);
 if(name==="late-archive")offers.splice(1);
 const current=new Map(),records=new Map(),receiver=new Map(),currentReturns=[],staging=[],archive=new Map(),historicalReturns=[],trace=[],pcm=new Int16Array(H*SLOT);
 const metrics={data:0,currentAck:0,request:0,positive:0,negative:0,fixture:0,idle:0,erased:0,received:0,currentConfirmed:0,currentGenuineSamples:0,currentReceivedSamples:0,historicalGenuine:0,historicalFalse:0,historicalUnsupported:0,wrongCorrespondence:0,negativeAccepted:0,negativeWrong:0,negativeThenPositive:0,expired:0,evicted:0,archiveInserted:0,archiveHits:0,archiveMisses:0,rejected:0};
 let serial=0,lostReq=false,lostReply=false,fixtureSent=false;
 const log=(slot,type,fields={})=>trace.push({slot,atSample:slot*SLOT+(["rx","lookup","current-confirm","historical-admission","decode-refusal"].includes(type)?FRAME:0),type,...fields});
 const useful=(a,t)=>{const r=records.get(a);return !!r&&current.get(source(a))===a&&t<r.offer+ttl;};
 const wanted=a=>interest==="all"||source(a)===0;
 const tagged=true, negative=true, stop=policy==="stop";
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
  // No receiver archive, lookup result, or evaluator truth is consulted by scheduling.
  const eligible=[...records.values()].filter(r=>wanted(r.address)&&r.tries>0&&!r.currentConfirmed&&!r.historyConfirmed&&!r.historyStopped&&!useful(r.address,t)&&r.attempts.length<2&&!r.attempts.at(-1)?.open);
  const estimate=r=>Math.min(r.offer+ttl,records.get(current.get(source(r.address)))?.offer>r.offer?records.get(current.get(source(r.address))).offer:Infinity)+8;
  if(policy==="rotate"||policy==="cooldown")eligible.sort((a,b)=>a.attempts.length-b.attempts.length||a.offer-b.offer||a.address-b.address);
  if(policy==="deadline")eligible.sort((a,b)=>estimate(a)-estimate(b)||a.attempts.length-b.attempts.length||a.address-b.address);
  const target=metrics.request>=cap?null:eligible.find(r=>policy!=="cooldown"||!r.negatives.length||t>=r.negatives.at(-1).at+3);
  const old=[...records.values()].find(r=>r.attempts.at(-1)?.open&&r.attempts.length>=(name.startsWith("session")?1:2)&&!r.historyConfirmed&&!r.historyStopped);
  const hr=historicalReturns.findIndex(x=>x.ready<=t);
  let p=null,origin="",loss=false,meta=null;
  // Fixture owns a slot only when no current work competes. It is an externally supplied synthetic obsolete body.
  if(ret>=0){const x=currentReturns.splice(ret,1)[0];p={address:x.address,kind:1,tag:0};origin="currentAck";loss=(name==="lost-ack"||name==="late-archive"||name==="slow-reply")&&x.address===0;}
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
      if(d.kind===3){r.historyConfirmed=true;metrics[origin==="fixture"?"historicalFalse":"historicalGenuine"]++;if(!receiver.has(d.address))metrics.historicalUnsupported++;if(r.negatives.length)metrics.negativeThenPositive++;}
      else{r.negatives.push({at:t,tag:d.tag});metrics.negativeAccepted++;if(!matched)metrics.negativeWrong++;if(stop)r.historyStopped=true;}
     }
    }
   }else log(t,"decode-refusal");
  }
  // Sample-weighted availability after the body decode point; no historic reply updates current state.
  for(const [a,r] of records)if(useful(a,t)){const wasReceived=receiver.has(a),wasConfirmed=r.currentConfirmed;
   const newData=trace.some(e=>e.slot===t&&e.type==="rx"&&e.packet.kind===0&&e.packet.address===a)&&receiver.get(a)?.observed===t;
   const newAck=trace.some(e=>e.slot===t&&e.type==="current-confirm"&&e.address===a);
   if(wasReceived)metrics.currentReceivedSamples+=newData?SLOT-FRAME:SLOT;
   if(wasConfirmed&&wasReceived)metrics.currentGenuineSamples+=newAck?SLOT-FRAME:SLOT;
  }
 }
 for(const [a,r] of records){const q=r.attempts.at(-1);if(q?.open){q.open=false;r.history.push({kind:"unresolved-at-horizon",at:H,tag:q.tag});}}
 return {name,policy,ttl,seed,interest,requestLoss,replyLoss,cap,metrics,ledger:[...records.values()],trace,pcm};
 }
 return {simulate,encode,decode,wave,cases,policies};
};

function qualify(api){
 let checks=0;const ck=(v,m)=>{checks++;if(!v)throw Error(m)};
 const rows=[],specimens=[],aggregate={},comparisons={};let peak=0;
 const fields=["data","currentAck","request","positive","negative","fixture","idle"];
 for(const seed of [4421,170021])for(const name of api.cases)for(const ttl of [2,6])for(const interest of ["all","source0"])for(const requestLoss of [false,true])for(const replyLoss of [false,true])for(const cap of [2,4]){
  let base;
  for(const policy of api.policies){
   const s=api.simulate({name,policy,ttl,seed,interest,requestLoss,replyLoss,cap}),m=s.metrics;
   ck(fields.reduce((a,k)=>a+m[k],0)===24,"slot partition");
   ck(m.request<=cap,"request budget");
   ck(s.ledger.every(r=>r.attempts.length<=2&&r.tries<=2),"bounded attempts");
   ck(s.trace.every((e,i)=>!i||e.atSample>=s.trace[i-1].atSample),"trace time");
   ck(s.trace.filter(e=>e.type==="archive-insert").every(e=>s.trace.some(x=>x.type==="rx"&&x.packet.kind===0&&x.packet.address===e.address&&x.slot===e.observed&&x.slot<=e.slot)),"archive provenance");
   ck(s.trace.filter(e=>e.type==="tx"&&(e.origin==="positive"||e.origin==="negative")).every(e=>s.trace.some(x=>x.type==="lookup"&&x.id===e.attemptId&&x.slot===e.lookupSlot&&x.found===(e.origin==="positive")&&x.slot<e.slot)),"reply provenance");
   ck(m.historicalUnsupported<=m.historicalFalse,"unsupported subset");
   ck(s.ledger.every(r=>!r.historyConfirmed||!r.currentConfirmed),"ledger separation");
   ck(m.historicalGenuine+m.historicalFalse===s.ledger.filter(r=>r.historyConfirmed).length,"confirmation partition");
   let max=0;for(const v of s.pcm)max=Math.max(max,Math.abs(v));peak=Math.max(peak,max);ck(max<=3080,"peak");
   if(!base)base=m;
   ck(base.currentGenuineSamples===m.currentGenuineSamples&&base.currentReceivedSamples===m.currentReceivedSamples,"current invariant");
   const {pcm,trace,ledger,...row}=s;rows.push(row);
   const k=cap+"/"+policy;const a=aggregate[k]??(aggregate[k]={runs:0});a.runs++;
   for(const f of ["historicalGenuine","historicalFalse","historicalUnsupported","wrongCorrespondence","request","positive","negative","negativeThenPositive","negativeAccepted"])a[f]=(a[f]??0)+m[f];
   const c=comparisons[k]??(comparisons[k]={wins:0,ties:0,losses:0});c[m.historicalGenuine>base.historicalGenuine?"wins":m.historicalGenuine<base.historicalGenuine?"losses":"ties"]++;
   if(seed===4421&&ttl===2&&interest==="all"&&!requestLoss&&!replyLoss&&cap===4&&["lost-data","late-archive","session-negative"].includes(name))specimens.push(s);
  }
 }
 return {receipt:{schema:"mhac-interaction-conversational-economics-v1",parentRef:"4e9f7120f137256fb8ba0736af51be7caacebc1f",parentBlob:"ae2c8370191b0698263be6823a34df6e4a65bda0",renderBlob:"10ed127dd84aee591f1addfa02fd1e2931114d67",checks,peak,rows,aggregate,comparisons},specimens};
}
function wavBytes(pcm){
 const b=new Uint8Array(44+2*pcm.length),d=new DataView(b.buffer);
 function ascii(s,i){for(let j=0;j<s.length;j++)b[i+j]=s.charCodeAt(j)}
 ascii("RIFF",0);d.setUint32(4,b.length-8,true);ascii("WAVEfmt ",8);d.setUint32(16,16,true);d.setUint16(20,1,true);d.setUint16(22,1,true);d.setUint32(24,16000,true);d.setUint32(28,32000,true);d.setUint16(32,2,true);d.setUint16(34,16,true);ascii("data",36);d.setUint32(40,b.length-44,true);pcm.forEach((x,i)=>d.setInt16(44+2*i,Math.round(x/2),true));return b;
}
module.exports={implementation,qualify,wavBytes};
if(require.main===module){
 const fs=require("node:fs"),path=require("node:path"),crypto=require("node:crypto");
 const pin="10ed127dd84aee591f1addfa02fd1e2931114d67",file=path.join(__dirname,"narrow-deadline-relay.cjs"),b=fs.readFileSync(file);
 if(crypto.createHash("sha1").update("blob "+b.length+"\0").update(b).digest("hex")!==pin)throw Error("render pin mismatch");
 const api=implementation(require(file)),{receipt,specimens}=qualify(api),out=process.argv[2]||"conversational-economics-output";
 fs.mkdirSync(out,{recursive:true});receipt.stimuli=[];
 for(const s of specimens){const stem=s.name+"-"+s.policy,bytes=wavBytes(s.pcm);fs.writeFileSync(path.join(out,stem+".wav"),bytes);const {pcm,...trace}=s;fs.writeFileSync(path.join(out,stem+".json"),JSON.stringify(trace,null,2));receipt.stimuli.push({stem,gain:.5,sha256:crypto.createHash("sha256").update(bytes).digest("hex")});}
 fs.writeFileSync(path.join(out,"receipt.json"),JSON.stringify(receipt,null,2));
 const html='<!doctype html><meta charset=utf-8><title>Conversational economics</title><style>body{font:16px system-ui;max-width:1100px;margin:2em auto;padding:1em}td,th{border:1px solid #aaa;padding:.4em}table{border-collapse:collapse}</style><h1>Conversational economics</h1><p>Synthetic shared-channel comparison. Begin at low volume. No autoplay. Request cap is matched; realized airtime is not. Not an authenticated protocol.</p><label>Scenario <select id="case">'+api.cases.map(x=>'<option>'+x+'</option>').join('')+'</select></label> <label>TTL <select id="ttl"><option>2</option><option>6</option></select></label> <label>Request cap <select id="cap"><option>2</option><option>4</option></select></label><div id="v"></div><h2>Original half-gain specimens (cap 4, TTL 2)</h2>'+receipt.stimuli.map(x=>'<p>'+x.stem+' <audio controls preload=none src="'+x.stem+'.wav"></audio> <a href="'+x.stem+'.json">trace</a></p>').join('')+'<script>const rows='+JSON.stringify(receipt.rows.filter(x=>x.seed===4421&&x.interest==="all"&&!x.requestLoss&&!x.replyLoss))+';const c=document.getElementById("case"),t=document.getElementById("ttl"),b=document.getElementById("cap"),v=document.getElementById("v");function draw(){v.innerHTML="<table><tr><th>Policy</th><th>Archive-origin positives</th><th>Replay positives</th><th>Wrong correspondence</th><th>Requests</th><th>Historical body ms</th></tr>"+rows.filter(x=>x.name===c.value&&x.ttl===+t.value&&x.cap===+b.value).map(x=>"<tr>"+[x.policy,x.metrics.historicalGenuine,x.metrics.historicalFalse,x.metrics.wrongCorrespondence,x.metrics.request,100*(x.metrics.request+x.metrics.positive+x.metrics.negative)].map(y=>"<td>"+y+"</td>").join("")+"</tr>").join("")+"</table>"}c.onchange=t.onchange=b.onchange=draw;draw()</script>';fs.writeFileSync(path.join(out,"index.html"),html);
 console.log(JSON.stringify({checks:receipt.checks,rows:receipt.rows.length,aggregate:receipt.aggregate,comparisons:receipt.comparisons,peak:receipt.peak,stimuli:receipt.stimuli.length}));
}

// Executed V8 receipt summary: {"schema":"mhac-interaction-conversational-economics-v1","parentRef":"4e9f7120f137256fb8ba0736af51be7caacebc1f","parentBlob":"ae2c8370191b0698263be6823a34df6e4a65bda0","renderBlob":"10ed127dd84aee591f1addfa02fd1e2931114d67","checks":35200,"peak":3080,"aggregate":{"2/stop":{"runs":320,"historicalGenuine":72,"historicalFalse":32,"historicalUnsupported":32,"wrongCorrespondence":64,"request":474,"positive":144,"negative":190,"negativeThenPositive":0,"negativeAccepted":118},"2/retry":{"runs":320,"historicalGenuine":60,"historicalFalse":32,"historicalUnsupported":32,"wrongCorrespondence":64,"request":524,"positive":130,"negative":254,"negativeThenPositive":0,"negativeAccepted":174},"2/rotate":{"runs":320,"historicalGenuine":78,"historicalFalse":32,"historicalUnsupported":32,"wrongCorrespondence":64,"request":524,"positive":150,"negative":234,"negativeThenPositive":0,"negativeAccepted":156},"2/cooldown":{"runs":320,"historicalGenuine":86,"historicalFalse":32,"historicalUnsupported":32,"wrongCorrespondence":64,"request":524,"positive":158,"negative":226,"negativeThenPositive":8,"negativeAccepted":148},"2/deadline":{"runs":320,"historicalGenuine":78,"historicalFalse":32,"historicalUnsupported":32,"wrongCorrespondence":64,"request":524,"positive":150,"negative":234,"negativeThenPositive":0,"negativeAccepted":156},"4/stop":{"runs":320,"historicalGenuine":72,"historicalFalse":32,"historicalUnsupported":32,"wrongCorrespondence":64,"request":510,"positive":144,"negative":226,"negativeThenPositive":0,"negativeAccepted":154},"4/retry":{"runs":320,"historicalGenuine":60,"historicalFalse":32,"historicalUnsupported":32,"wrongCorrespondence":64,"request":592,"positive":130,"negative":322,"negativeThenPositive":0,"negativeAccepted":242},"4/rotate":{"runs":320,"historicalGenuine":78,"historicalFalse":32,"historicalUnsupported":32,"wrongCorrespondence":64,"request":574,"positive":150,"negative":284,"negativeThenPositive":0,"negativeAccepted":206},"4/cooldown":{"runs":320,"historicalGenuine":86,"historicalFalse":32,"historicalUnsupported":32,"wrongCorrespondence":64,"request":574,"positive":158,"negative":276,"negativeThenPositive":8,"negativeAccepted":198},"4/deadline":{"runs":320,"historicalGenuine":78,"historicalFalse":32,"historicalUnsupported":32,"wrongCorrespondence":64,"request":574,"positive":150,"negative":284,"negativeThenPositive":0,"negativeAccepted":206}},"comparisons":{"2/stop":{"wins":0,"ties":320,"losses":0},"2/retry":{"wins":0,"ties":308,"losses":12},"2/rotate":{"wins":6,"ties":314,"losses":0},"2/cooldown":{"wins":14,"ties":306,"losses":0},"2/deadline":{"wins":6,"ties":314,"losses":0},"4/stop":{"wins":0,"ties":320,"losses":0},"4/retry":{"wins":0,"ties":308,"losses":12},"4/rotate":{"wins":6,"ties":314,"losses":0},"4/cooldown":{"wins":14,"ties":306,"losses":0},"4/deadline":{"wins":6,"ties":314,"losses":0}},"rows":3200,"specimens":15}
