'use strict';
// Interaction #456 / #457. Synthetic only, Draft/HOLD. AI-assisted.
// Derived from pinned conversational-economics.cjs; preserve original implementation and wire.
const implementation=function implementation(parent){
 const RATE=16000,SLOT=3200,FRAME=1600,H=24;
 const policies=["stop","rotate","cooldown1","cooldown","cooldown5","window"];
 const cases=["revision","churn","lost-data","lost-ack","late-archive","slow-reply","old-positive","old-negative","session-positive","session-negative"];
 const basis=Array.from({length:4},(_,n)=>Array.from({length:400},(_,i)=>[Math.cos(2*Math.PI*(400+80*n)*i/RATE),Math.sin(2*Math.PI*(400+80*n)*i/RATE)]));
 // New disjoint stand-in: 12 current + 36 historical control expressions; no legacy interoperability.
 function encode(p){const {kind,address,tag=0}=p;if(!Number.isInteger(address)||address<0||address>=6||!Number.isInteger(kind)||kind<0||kind>4||![0,1].includes(tag)||(kind<2&&tag!==0))throw Error("packet");return kind<2?2*address+kind:12+6*address+2*(kind-2)+tag;}
 function wave(n,seed,loss=false){return parent.render({kind:n%4,source:1+(n>>2)%4,version:1+(n>>4)},seed,loss);}
 function decode(w){if(w.length!==SLOT)throw Error("slot length");const s=[];for(let j=0;j<4;j++){const v=basis.map(b=>{let x=0,y=0;for(let i=0;i<400;i++){x+=w[j*400+i]*b[i][0];y+=w[j*400+i]*b[i][1];}return x*x+y*y;});const peak=Math.max(...v),n=v.indexOf(peak);v[n]=0;if(peak<1e10||peak<4*Math.max(...v))return null;s.push(n);}
 const n=s[0]+4*s[1]+16*s[2];if(n>=48||s[3]!==((s[0]+2*s[1]+3*s[2])%4))return null;return n<12?{address:n>>1,kind:n%2,tag:0}:{address:Math.floor((n-12)/6),kind:2+Math.floor((n-12)%6/2),tag:n%2};}
 const source=a=>Math.floor(a/3);
 function simulate({name,policy,ttl,seed,interest,requestLoss,replyLoss,cap,delay=3,retention=8}){
 if(!cases.includes(name)||!policies.includes(policy)||![2,4,6].includes(ttl)||!["all","source0"].includes(interest)||![2,4].includes(cap))throw Error("config");
 if(!Number.isInteger(delay)||delay<0||delay>8||!Number.isInteger(retention)||retention<2||retention>12)throw Error("archive config");
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
  for(const [a,r] of receiver)if(!useful(a,t)&&!r.staged){r.staged=true;staging.push({address:a,observed:r.observed,ready:t+(name==="late-archive"?delay:0)});log(t,"archive-stage",{address:a,observed:r.observed});}
  for(const [a,x] of archive)if(x.expires<=t){archive.delete(a);metrics.expired++;log(t,"archive-expire",{address:a});}
  for(let j=0;j<staging.length;){const x=staging[j];if(x.ready>t){j++;continue;}staging.splice(j,1);if(archive.size===3){const a=archive.keys().next().value;archive.delete(a);metrics.evicted++;log(t,"archive-evict",{address:a});}archive.set(x.address,{...x,expires:t+retention});metrics.archiveInserted++;log(t,"archive-insert",{address:x.address,observed:x.observed,expires:t+retention});}
  for(let j=currentReturns.length-1;j>=0;j--)if(!useful(currentReturns[j].address,t))currentReturns.splice(j,1);
  const ret=currentReturns.findIndex(x=>x.ready<=t);
  const data=[...records.values()].find(r=>useful(r.address,t)&&!r.currentConfirmed&&r.tries<2&&r.next<=t);
  // No receiver archive, lookup result, or evaluator truth is consulted by scheduling.
  const eligible=[...records.values()].filter(r=>wanted(r.address)&&r.tries>0&&!r.currentConfirmed&&!r.historyConfirmed&&!r.historyStopped&&!useful(r.address,t)&&r.attempts.length<2&&!r.attempts.at(-1)?.open);
  const estimate=r=>Math.min(r.offer+ttl,records.get(current.get(source(r.address)))?.offer>r.offer?records.get(current.get(source(r.address))).offer:Infinity)+8;
  if(policy!=="stop")eligible.sort((a,b)=>a.attempts.length-b.attempts.length||a.offer-b.offer||a.address-b.address);
  if(policy==="deadline")eligible.sort((a,b)=>estimate(a)-estimate(b)||a.attempts.length-b.attempts.length||a.address-b.address);
  const wait=r=>policy==="cooldown1"?1:policy==="cooldown"?3:policy==="cooldown5"?5:policy==="window"?Math.max(1,Math.min(5,Math.floor((estimate(r)-r.negatives.at(-1).at)/2))):0;
  const target=metrics.request>=cap?null:eligible.find(r=>!r.negatives.length||t>=r.negatives.at(-1).at+wait(r));
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
 return {name,policy,ttl,seed,interest,requestLoss,replyLoss,cap,delay,retention,metrics,ledger:[...records.values()],trace,pcm};
 }
 return {simulate,encode,decode,wave,cases,policies};
};

function qualify(api, legacy){
 const rows=[],specimens=[],aggregate={},grid={},pairs={};let checks=0;
 const ck=(v,m)=>{checks++;if(!v)throw Error(m)};
 const fields=["data","currentAck","request","positive","negative","fixture","idle"];
 // Regression of unchanged policies against the exact parent, with both positive and adverse scenarios.
 for(const name of legacy.cases)for(const policy of ["stop","rotate","cooldown"]){
  const c={name,policy,ttl:2,seed:4421,interest:"all",requestLoss:false,replyLoss:false,cap:2};
  const a=api.simulate(c),b=legacy.simulate(c);
  ck(JSON.stringify(a.metrics)===JSON.stringify(b.metrics),"legacy metrics");
  ck(JSON.stringify(a.trace)===JSON.stringify(b.trace),"legacy trace");
  ck(a.pcm.every((v,i)=>v===b.pcm[i]),"legacy PCM");
 }
 // Fixed held-out grid; no fitting. Delay and retention are not visible to scheduler.
 for(const seed of [211019,211021])for(const ttl of [2,6])for(const delay of [0,1,2,3,4,5,6,7,8])for(const retention of [2,4,8,12])for(const loss of ["none","first-request","first-reply"]){
  let base;
  for(const policy of api.policies){
   const c={name:"late-archive",policy,ttl,seed,interest:"all",requestLoss:loss==="first-request",replyLoss:loss==="first-reply",cap:2,delay,retention};
   const a=api.simulate(c),m=a.metrics,air=m.request+m.positive+m.negative;
   ck(fields.reduce((n,k)=>n+m[k],0)===24,"slots");
   ck(m.request<=2&&air<=4,"matched ceiling: two request/reply pairs");
   ck(a.trace.every((e,i)=>!i||e.atSample>=a.trace[i-1].atSample),"trace order");
   ck(a.trace.filter(e=>e.type==="lookup"&&e.found).every(e=>a.trace.some(x=>x.type==="archive-insert"&&x.address===e.address&&x.slot<=e.slot&&x.expires>e.slot)),"archive support");
   ck(m.historicalFalse===0&&m.wrongCorrespondence===0,"fixture-free scenarios");
   ck(a.pcm.every(v=>Math.abs(v)<=3080),"peak");
   if(!base)base=m;
   ck(base.currentReceivedSamples===m.currentReceivedSamples&&base.currentGenuineSamples===m.currentGenuineSamples,"current invariant");
   rows.push({...c,loss,air,genuine:m.historicalGenuine,current:m.currentGenuineSamples});
   const z=aggregate[policy]??(aggregate[policy]={runs:0,genuine:0,air:0});z.runs++;z.genuine+=m.historicalGenuine;z.air+=air;
   const k=delay+"/"+retention+"/"+policy;const q=grid[k]??(grid[k]={runs:0,genuine:0,air:0});q.runs++;q.genuine+=m.historicalGenuine;q.air+=air;
   if(seed===211019&&ttl===2&&loss==="none"&&[[1,2],[3,8],[6,8],[8,12]].some(([d,r])=>delay===d&&retention===r)&&["rotate","cooldown","cooldown5"].includes(policy))specimens.push(a);
  }
 }
 // Strict equal-realized-airtime subset of rotate vs fixed cooldowns; report coverage of subset.
 for(let i=0;i<rows.length;i+=api.policies.length){const group=rows.slice(i,i+api.policies.length),a=group.find(x=>x.policy==="rotate");for(const b of group.filter(x=>["cooldown","cooldown5","window"].includes(x.policy))){const z=pairs[b.policy]??(pairs[b.policy]={all:0,matched:0,win:0,tie:0,loss:0});z.all++;if(a.air===b.air){z.matched++;z[b.genuine>a.genuine?"win":b.genuine<a.genuine?"loss":"tie"]++;}}}
 return {receipt:{schema:"mhac-patience-sensitivity-v1",parentRef:"b44f11b425a0e42d2ed245057c8afbb42d4e0cec",parentBlob:"96291467cf542f1700ba6dee7d15f7a73122672e",rendererBlob:"10ed127dd84aee591f1addfa02fd1e2931114d67",checks,rows,aggregate,grid,pairs},specimens};
}
module.exports={implementation,qualify};
if(require.main===module){
 const fs=require("node:fs"),path=require("node:path"),crypto=require("node:crypto");
 const pin=(name,sha)=>{const p=path.join(__dirname,name),b=fs.readFileSync(p);if(crypto.createHash("sha1").update("blob "+b.length+"\0").update(b).digest("hex")!==sha)throw Error("pin mismatch "+name);return require(p);};
 const legacy=pin("conversational-economics.cjs","96291467cf542f1700ba6dee7d15f7a73122672e"),renderer=pin("narrow-deadline-relay.cjs","10ed127dd84aee591f1addfa02fd1e2931114d67");
 const api=implementation(renderer),{receipt,specimens}=qualify(api,legacy.implementation(renderer)),out=process.argv[2]||"patience-output";fs.mkdirSync(out,{recursive:true});
 receipt.stimuli=[];for(const s of specimens){const stem="delay-"+s.delay+"-retention-"+s.retention+"-"+s.policy,b=legacy.wavBytes(s.pcm);fs.writeFileSync(path.join(out,stem+".wav"),b);const {pcm,...trace}=s;fs.writeFileSync(path.join(out,stem+".json"),JSON.stringify(trace,null,2));receipt.stimuli.push({stem,gain:.5,sha256:crypto.createHash("sha256").update(b).digest("hex")});}
 fs.writeFileSync(path.join(out,"receipt.json"),JSON.stringify(receipt,null,2));
 const html='<!doctype html><meta charset=utf-8><title>Conversational patience</title><style>body{font:16px system-ui;max-width:1000px;margin:2em auto;padding:1em}td,th{border:1px solid #aaa;padding:.4em}table{border-collapse:collapse}</style><h1>Conversational patience</h1><p>Aligned synthetic FSK, not authenticated. Begin at low volume; no autoplay. Delay and retention are evaluator parameters, not requester observations.</p><label>Archive delay (200 ms slots) <select id="delay">'+Array.from({length:9},(_,i)=>'<option>'+i+'</option>').join('')+'</select></label> <label>Retention <select id="retention">'+[2,4,8,12].map(i=>'<option>'+i+'</option>').join('')+'</select></label><div id="result"></div><h2>Half-gain original replays</h2>'+receipt.stimuli.map(x=>'<p>'+x.stem+' <audio controls preload="none" src="'+x.stem+'.wav"></audio> <a href="'+x.stem+'.json">trace</a></p>').join('')+'<script>const grid='+JSON.stringify(receipt.grid)+',policies='+JSON.stringify(api.policies)+';const d=document.getElementById("delay"),r=document.getElementById("retention"),v=document.getElementById("result");function draw(){v.innerHTML="<table><tr><th>Policy</th><th>Confirmations</th><th>Historical bodies</th><th>Runs</th></tr>"+policies.map(p=>{const x=grid[d.value+"/"+r.value+"/"+p];return "<tr><td>"+p+"</td><td>"+x.genuine+"</td><td>"+x.air+"</td><td>"+x.runs+"</td></tr>"}).join("")+"</table>"}d.onchange=r.onchange=draw;draw()</script>';fs.writeFileSync(path.join(out,"index.html"),html);
 console.log(JSON.stringify({checks:receipt.checks,rows:receipt.rows.length,aggregate:receipt.aggregate,pairs:receipt.pairs,stimuli:receipt.stimuli.length}));
}

// Executed V8 summary: {"checks":18234,"rows":2592,"aggregate":{"stop":{"runs":432,"genuine":160,"air":1296},"rotate":{"runs":432,"genuine":192,"air":1552},"cooldown1":{"runs":432,"genuine":192,"air":1552},"cooldown":{"runs":432,"genuine":216,"air":1552},"cooldown5":{"runs":432,"genuine":232,"air":1552},"window":{"runs":432,"genuine":216,"air":1552}},"pairs":{"cooldown":{"all":432,"matched":432,"win":32,"tie":392,"loss":8},"cooldown5":{"all":432,"matched":432,"win":56,"tie":360,"loss":16},"window":{"all":432,"matched":432,"win":32,"tie":392,"loss":8}},"stimuli":12}
