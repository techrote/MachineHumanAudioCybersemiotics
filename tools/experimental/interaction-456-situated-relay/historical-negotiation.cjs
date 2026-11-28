'use strict';
// Interaction lane Refs #456, Draft/HOLD; synthetic only, AI-assisted single agent.
// Narrow experiment after ab30661ed840795f0bff100fbdbe1d2e16470ccd; parent waveform blob 10ed127dd84aee591f1addfa02fd1e2931114d67.
// Grammar handoff be40e7795877599a02a151359f07adfa34036514 read only; this is an independent stand-in, not its wire.
// 200 ms fixed slots, 100 ms bodies; separate slot ownership assumed. Archive availability is a scripted exogenous interval.
// Budget is a matched maximum, not equal realized airtime. A negative reports absence at lookup time, not permanent absence.
// No authentication, persistence, human benefit, or real device control. Same tag reused across sessions by design (negative witness).
const implementation=function implementation(parent){
 const RATE=16000,SLOT=3200,FRAME=1600,H=12;
 const policies=["silent","silent-tag","negative-stop","negative-tag-stop","negative-tag-retry"];
 const cases=[
 {name:"retained",from:0,to:12,busy:[],delay:1},
 {name:"absent",from:12,to:12,busy:[],delay:1},
 {name:"late-entry",from:3,to:12,busy:[],delay:1},
 {name:"expires",from:0,to:1,busy:[],delay:2},
 {name:"busy",from:0,to:12,busy:[1,2,3,5],delay:1},
 {name:"delayed",from:0,to:12,busy:[],delay:5},
 {name:"old-reply",from:12,to:12,busy:[],delay:1,replay:5},
 {name:"cross-session",from:12,to:12,busy:[],delay:1,replay:1}
 ];
 const basis=Array.from({length:4},(_,n)=>Array.from({length:400},(_,i)=>[Math.cos(2*Math.PI*(400+80*n)*i/RATE),Math.sin(2*Math.PI*(400+80*n)*i/RATE)]));
 // Disjoint adapter semantics, NOT wire-compatible with parent: 36 legal bodies, checksum inherited.
 function render(p,seed,loss=false){
  if(!Number.isInteger(p.address)||p.address<0||p.address>5||![0,1,2].includes(p.kind)||![0,1].includes(p.tag))throw Error("packet");
  const n=p.address*6+p.kind*2+p.tag;
  return parent.render({kind:n%4,source:1+(n>>2)%4,version:1+(n>>4)},seed,loss);
 }
 function decode(w){
  if(w.length!==SLOT)throw Error("length");
  const s=[];
  for(let j=0;j<4;j++){
   const v=basis.map(b=>{let x=0,y=0;for(let i=0;i<400;i++){x+=w[j*400+i]*b[i][0];y+=w[j*400+i]*b[i][1];}return x*x+y*y;});
   const peak=Math.max(...v),n=v.indexOf(peak);v[n]=0;if(peak<1e10||peak<4*Math.max(...v))return null;s.push(n);
  }
  const n=s[0]+4*s[1]+16*s[2];if(n>=36||s[3]!==((s[0]+2*s[1]+3*s[2])%4))return null;
  return {address:Math.floor(n/6),kind:Math.floor(n/2)%3,tag:n%2};
 }
 function simulate({name,policy,budget,seed,requestLoss=false,replyLoss=false,address=0}){
  const c=cases.find(x=>x.name===name);if(!c||!policies.includes(policy)||![2,4].includes(budget))throw Error("config");
  const tagged=policy.includes("tag"),negative=policy.startsWith("negative"),stop=policy.endsWith("stop");
  const pcm=new Int16Array(H*SLOT),trace=[],pending=[];
  let attempts=0,window=-1,tag=-1,state="unknown",spent=0,firstReply=true,complete=false;
  const m={requests:0,replies:0,positive:0,negative:0,misses:0,requestErased:0,replyErased:0,staleRejected:0,falseCorrespondence:0,falseConfirmation:0,genuine:0,negativeAccepted:0,negativeAfterChange:0,busy:0,idle:0,fixture:0,expiredPending:0};
  const log=(slot,type,x={})=>trace.push({slot,atSample:slot*SLOT,type,...x});
  const available=t=>t>=c.from&&t<c.to;
  for(let t=0;t<H;t++){
   if(t>window&&window>=0){log(t,"window-ended",{tag,state});window=-1;}
   // Current traffic has strict priority and is independently scheduled; no historical decoding in those slots.
   if(c.busy.includes(t)){m.busy++;pcm.set(parent.render({kind:0,source:1,version:1},seed+t*997),t*SLOT);log(t,"current-slot");continue;}
   let p=null,origin="",loss=false,corresponding=false,observedAt=null,requestId=null;
   if(c.replay===t){p={address,kind:1,tag:0};origin="old-session-fixture";m.fixture++;}
   else if(!complete&&window<0&&attempts<2&&spent<budget){
    tag=tagged?attempts:0;attempts++;window=t+3;state="waiting";p={address,kind:0,tag};origin="request";requestId=attempts;
    loss=requestLoss&&attempts===1;m.requests++;spent++;if(loss)m.requestErased++;
   }else if(spent<budget){
    const j=pending.findIndex(q=>q.ready<=t);
    if(j>=0){const q=pending.splice(j,1)[0];p=q.p;origin="reply";observedAt=q.observedAt;requestId=q.requestId;corresponding=true;
     loss=replyLoss&&firstReply;firstReply=false;m.replies++;spent++;if(loss)m.replyErased++;m[p.kind===1?"positive":"negative"]++;
    }
   }
   if(!p){m.idle++;log(t,"idle");continue;}
   log(t,"tx",{packet:p,origin,loss,requestId,observedAt});
   const w=render(p,seed+t*997,loss);pcm.set(w,t*SLOT);const d=decode(w);
   if(!d){log(t,"decode-refusal");continue;}
   if(d.kind===0){
    const found=available(t);if(!found)m.misses++;
    log(t,"lookup",{packet:d,found,requestId});
    if(found||negative)pending.push({p:{...d,kind:found?1:2},ready:t+c.delay,observedAt:t,requestId});
   }else{
    const eligible=!complete&&window>=t&&d.address===address&&d.tag===tag;
    const matched=corresponding&&requestId===attempts;
    log(t,"reply-receipt",{packet:d,eligible,evaluatorCorresponding:matched,observedAt,availableNow:available(t)});
    if(!eligible){m.staleRejected++;continue;}
    if(!matched)m.falseCorrespondence++;
    if(d.kind===1){if(corresponding)m.genuine++;else m.falseConfirmation++;state="confirmed";complete=true;}
    else{m.negativeAccepted++;if(available(t))m.negativeAfterChange++;state="reported-absent";if(stop)complete=true;}
   }
  }
  m.expiredPending=pending.length;
  if(state==="waiting")state="unanswered";
  return {name,policy,budget,seed,address,requestLoss,replyLoss,state,spent,metrics:m,trace,pcm};
 }
 function qualify(){
  let checks=0;const ck=(x,msg)=>{checks++;if(!x)throw Error(msg);};
  for(let a=0;a<6;a++)for(let k=0;k<3;k++)for(let t=0;t<2;t++){const p={address:a,kind:k,tag:t};ck(JSON.stringify(decode(render(p,31)))===JSON.stringify(p),"roundtrip");ck(decode(render(p,31,true))===null,"erasure");}
  const rows=[],specimens=[],aggregate={};
  for(const seed of [21611,84977])for(const c of cases)for(const budget of [2,4])for(const requestLoss of [false,true])for(const replyLoss of [false,true])for(const policy of policies){
   const s=simulate({name:c.name,policy,budget,seed,requestLoss,replyLoss,address:2}),m=s.metrics;
   ck(s.spent<=budget&&s.spent===m.requests+m.replies,"budget");ck(m.requests<=2,"attempt bound");ck(m.busy+m.idle+m.fixture+s.spent===H,"slot partition");ck(s.pcm.every(x=>Math.abs(x)<=3080),"peak");
   ck(m.genuine+m.falseConfirmation<=1,"one positive acceptance");ck(m.negativeAccepted<=2,"negative bound");
   ck(s.trace.filter(e=>e.type==="tx"&&e.origin==="reply").every(e=>s.trace.some(q=>q.type==="lookup"&&q.requestId===e.requestId&&q.slot===e.observedAt&&q.slot<e.slot&&q.found===(e.packet.kind===1))),"causal lookup");
   ck(s.trace.filter(e=>e.type==="reply-receipt"&&e.eligible).every(e=>s.trace.some(q=>q.type==="tx"&&q.origin==="request"&&q.packet.tag===e.packet.tag&&q.slot<e.slot&&e.slot<=q.slot+3)),"window");
   const row={name:s.name,policy,budget,seed,requestLoss,replyLoss,state:s.state,spent:s.spent,...m};rows.push(row);
   const k=budget+"/"+policy,a=aggregate[k]??(aggregate[k]={runs:0,spent:0,genuine:0,falseConfirmation:0,falseCorrespondence:0,negativeAccepted:0,negativeAfterChange:0,requests:0,replies:0,unanswered:0});a.runs++;for(const f of ["spent","genuine","falseConfirmation","falseCorrespondence","negativeAccepted","negativeAfterChange","requests","replies"])a[f]+=row[f];a.unanswered+=Number(s.state==="unanswered");
   if(seed===21611&&budget===4&&!replyLoss&&((c.name==="old-reply"&&requestLoss)||(c.name==="late-entry"&&!requestLoss)||(c.name==="cross-session"&&!requestLoss)))specimens.push(s);
  }
  const witness=(n,p,loss=false)=>rows.find(x=>x.name===n&&x.policy===p&&x.budget===4&&x.seed===21611&&x.requestLoss===loss&&!x.replyLoss);
  ck(witness("old-reply","silent",true).falseConfirmation===1,"old replay legacy");
  ck(witness("old-reply","silent-tag",true).falseConfirmation===0,"old replay tagged");
  ck(witness("cross-session","silent-tag").falseConfirmation===1,"session reuse negative");
  ck(witness("late-entry","negative-tag-stop").genuine===0,"premature finality");
  ck(witness("late-entry","negative-tag-retry").genuine===1,"retry recovery");
  ck(witness("late-entry","silent-tag").genuine===1,"silence retry recovery");
  return {receipt:{schema:"mhac-interaction-historical-negotiation-v1",rate:RATE,slotSamples:SLOT,bodySamples:FRAME,checks,rows,aggregate},specimens};
 }
 return {simulate,qualify,render,decode,policies,cases};
};
const api=implementation(require('./narrow-deadline-relay.cjs')); module.exports=api;
if(require.main===module){
 const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
 const b=fs.readFileSync(path.join(__dirname,'narrow-deadline-relay.cjs'));
 if(crypto.createHash('sha1').update('blob '+b.length+'\0').update(b).digest('hex')!=='10ed127dd84aee591f1addfa02fd1e2931114d67')throw Error('parent mismatch');
 const out=process.argv[2]||'historical-negotiation-output';fs.mkdirSync(out,{recursive:true});
 const {receipt,specimens}=api.qualify();receipt.parentRef='ab30661ed840795f0bff100fbdbe1d2e16470ccd';receipt.parentBlob='10ed127dd84aee591f1addfa02fd1e2931114d67';receipt.stimuli=[];
 for(const s of specimens){const stem=s.name+'-'+s.policy,buf=Buffer.alloc(44+2*s.pcm.length);buf.write('RIFF');buf.writeUInt32LE(buf.length-8,4);buf.write('WAVEfmt ',8);buf.writeUInt32LE(16,16);buf.writeUInt16LE(1,20);buf.writeUInt16LE(1,22);buf.writeUInt32LE(16000,24);buf.writeUInt32LE(32000,28);buf.writeUInt16LE(2,32);buf.writeUInt16LE(16,34);buf.write('data',36);buf.writeUInt32LE(buf.length-44,40);s.pcm.forEach((x,i)=>buf.writeInt16LE(Math.round(x/2),44+2*i));fs.writeFileSync(path.join(out,stem+'.wav'),buf);const {pcm,...trace}=s;fs.writeFileSync(path.join(out,stem+'.json'),JSON.stringify(trace,null,2));receipt.stimuli.push({stem,gain:.5,sha256:crypto.createHash('sha256').update(buf).digest('hex')});}
 fs.writeFileSync(path.join(out,'receipt.json'),JSON.stringify(receipt,null,2));
 const html='<!doctype html><meta charset=utf-8><title>Historical negotiation</title><style>body{font:16px system-ui;max-width:1000px;margin:2em auto;padding:1em}td,th{padding:.4em;border:1px solid #aaa}table{border-collapse:collapse}</style><h1>Historical negotiation</h1><p>Synthetic lookup dialogue. Low device volume; no autoplay. Negative reports absence at lookup time. Tags are not authentication.</p><label>Scenario <select id="case">'+api.cases.map(c=>'<option>'+c.name+'</option>').join('')+'</select></label> <label>Body budget <select id="budget"><option>2</option><option selected>4</option></select></label> <label><input id="loss" type="checkbox"> First request erased</label> <label><input id="reply" type="checkbox"> First reply erased</label><div id="v"></div><h2>Original half-gain specimens</h2>'+receipt.stimuli.map(x=>'<p>'+x.stem+' <audio controls preload=none src="'+x.stem+'.wav"></audio> <a href="'+x.stem+'.json">trace</a></p>').join('')+'<script>const rows='+JSON.stringify(receipt.rows.filter(x=>x.seed===21611))+';const c=document.getElementById("case"),b=document.getElementById("budget"),l=document.getElementById("loss"),r=document.getElementById("reply"),v=document.getElementById("v");function draw(){v.innerHTML="<table><tr><th>Policy</th><th>State</th><th>Genuine</th><th>False confirmation</th><th>Wrong correspondence</th><th>Negative accepted</th><th>Bodies</th></tr>"+rows.filter(x=>x.name===c.value&&x.budget===+b.value&&x.requestLoss===l.checked&&x.replyLoss===r.checked).map(x=>"<tr>"+[x.policy,x.state,x.genuine,x.falseConfirmation,x.falseCorrespondence,x.negativeAccepted,x.spent].map(y=>"<td>"+y+"</td>").join("")+"</tr>").join("")+"</table>"}c.onchange=b.onchange=l.onchange=r.onchange=draw;draw()</script>';fs.writeFileSync(path.join(out,'index.html'),html);
 console.log(JSON.stringify({checks:receipt.checks,rows:receipt.rows.length,aggregate:receipt.aggregate,stimuli:receipt.stimuli.length}));
}

// Executed twice in V8; identical computational receipts. Native CLI/export/browser not yet qualified.
// {"checks":5198,"rows":640,"aggregate":{"2/silent":{"runs":64,"spent":120,"genuine":4,"falseConfirmation":16,"falseCorrespondence":16,"negativeAccepted":0,"negativeAfterChange":0,"requests":112,"replies":8,"unanswered":44},"2/silent-tag":{"runs":64,"spent":120,"genuine":4,"falseConfirmation":8,"falseCorrespondence":8,"negativeAccepted":0,"negativeAfterChange":0,"requests":112,"replies":8,"unanswered":52},"2/negative-stop":{"runs":64,"spent":124,"genuine":4,"falseConfirmation":12,"falseCorrespondence":12,"negativeAccepted":6,"negativeAfterChange":0,"requests":100,"replies":24,"unanswered":42},"2/negative-tag-stop":{"runs":64,"spent":124,"genuine":4,"falseConfirmation":8,"falseCorrespondence":8,"negativeAccepted":6,"negativeAfterChange":0,"requests":100,"replies":24,"unanswered":46},"2/negative-tag-retry":{"runs":64,"spent":124,"genuine":4,"falseConfirmation":8,"falseCorrespondence":8,"negativeAccepted":6,"negativeAfterChange":0,"requests":100,"replies":24,"unanswered":46},"4/silent":{"runs":64,"spent":162,"genuine":20,"falseConfirmation":16,"falseCorrespondence":20,"negativeAccepted":0,"negativeAfterChange":0,"requests":116,"replies":46,"unanswered":28},"4/silent-tag":{"runs":64,"spent":162,"genuine":18,"falseConfirmation":8,"falseCorrespondence":8,"negativeAccepted":0,"negativeAfterChange":0,"requests":116,"replies":46,"unanswered":38},"4/negative-stop":{"runs":64,"spent":188,"genuine":20,"falseConfirmation":14,"falseCorrespondence":18,"negativeAccepted":14,"negativeAfterChange":0,"requests":110,"replies":78,"unanswered":16},"4/negative-tag-stop":{"runs":64,"spent":188,"genuine":18,"falseConfirmation":8,"falseCorrespondence":8,"negativeAccepted":18,"negativeAfterChange":0,"requests":110,"replies":78,"unanswered":20},"4/negative-tag-retry":{"runs":64,"spent":200,"genuine":20,"falseConfirmation":8,"falseCorrespondence":8,"negativeAccepted":22,"negativeAfterChange":0,"requests":116,"replies":84,"unanswered":20}},"specimens":15}
