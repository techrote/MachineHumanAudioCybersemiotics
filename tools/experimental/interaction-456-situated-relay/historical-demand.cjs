'use strict';
// Interaction lane, Refs #456, Draft/HOLD, AI-assisted synthetic-only.
// Historical demand, not Integration or Grammars wire. Request window is not authentication.
// 20 shared 200 ms slots; identical 100 ms waveform body; interest is requester-local.
// Archive cap 3; retention 8 slots; 2 requests max, 4-slot response window. No negative reply.
// Run: node historical-demand.cjs historical-demand-output. Original half-gain WAV and traces.
const pins={"narrow-deadline-relay.cjs":"10ed127dd84aee591f1addfa02fd1e2931114d67","evidence-freshness.cjs":"c459c6edd8446440adee6f4ee54ee405863d5b43","archive-recovery.cjs":"83f9905636ef5c0bfadd72cbe5cc3178ced2cd15"};
const implementation=function implementation(parent,freshness,archiveParent){
const RATE=16000,SLOT=3200,FRAME=1600,H=20;
const key=p=>JSON.stringify([p.source,p.version,p.actor,p.event,p.seq,p.tree]);
const packet=(source,version,kind=0)=>({source,version,kind,actor:source+1,event:source,seq:version,tree:[['open','hold','close'][version-1]]});
const modes=['bilateral','push','pull'],cases=['clean','revision','delayed','data-loss','ack-loss','forged','churn'];
// Request uses previously unused kind 2, same tone bank, checksum, frame and peak.
const basis=Array.from({length:4},(_,n)=>Array.from({length:400},(_,i)=>[Math.cos(2*Math.PI*(400+80*n)*i/RATE),Math.sin(2*Math.PI*(400+80*n)*i/RATE)]));
function decode(w){
 const d=parent.decode(w);if(d)return d;const s=[];
 for(let j=0;j<4;j++){const power=basis.map(b=>{let x=0,y=0;for(let i=0;i<400;i++){const v=w[j*400+i];x+=v*b[i][0];y+=v*b[i][1];}return x*x+y*y;});const m=Math.max(...power),n=power.indexOf(m);power[n]=0;if(m<1e10||m<4*Math.max(...power))return null;s.push(n);}
 return s[0]===2&&s[1]<2&&s[2]<3&&s[3]===(s[0]+2*s[1]+3*s[2])%4?packet(s[1]+1,s[2]+1,2):null;
}
function simulate(name,mode,ttl,seed,interest='all',requestLoss=false,lateFixture=false){
 if(!cases.includes(name)||!modes.includes(mode)||![2,3,4,6].includes(ttl)||!['all','source1','none'].includes(interest))throw Error('config');
 const offers=[[0,packet(1,1)],[0,packet(2,1)]];
 if(name==='revision')offers.push([2,packet(1,2)],[5,packet(2,2)]);
 if(name==='churn')offers.push([2,packet(1,2)],[3,packet(2,2)],[5,packet(1,3)],[6,packet(2,3)]);
 const trace=[],pcm=new Int16Array(H*SLOT),records=new Map(),current=new Map(),received=new Set(),queue=[],archive=[];
 const log=(at,type,x={})=>trace.push({at,type,...x});
 const m={data:0,ack:0,request:0,idle:0,invalid:0,archived:0,evicted:0,expired:0,archiveTx:0,requestDecoded:0,requestMiss:0,requestLoss:0,rejectedHistorical:0,unsolicited:0};
 const useful=(r,t)=>t*SLOT+FRAME<r.at+ttl*SLOT;
 const wanted=r=>interest==='all'||interest==='source1'&&r.p.source===1;
 for(let t=0;t<H;t++){
  const at=t*SLOT,end=at+FRAME;
  for(const [when,p] of offers)if(when===t){const k=key(p);records.set(k,{p,at,ready:t,attempts:0,confirmed:false,requests:0,until:-1});current.set(p.source,k);log(at,'offer',{packet:p});}
  for(let j=archive.length-1;j>=0;j--)if(archive[j].expires<=t){const a=archive.splice(j,1)[0];m.expired++;log(at,'archive-expired',{packet:a.p});}
  for(let j=queue.length-1;j>=0;j--){const a=queue[j],r=records.get(key(a.p));if(!useful(r,t)||current.get(a.p.source)!==key(a.p)){
   queue.splice(j,1);if(mode!=='bilateral'){archive.push({...a,expires:t+8,requestedAt:null});m.archived++;log(at,'archive-enqueued',{packet:a.p,expires:t+8});if(archive.length>3){const q=archive.shift();m.evicted++;log(at,'archive-evicted',{packet:q.p});}}else log(at,'return-abandoned',{packet:a.p});
  }}
  const ret=queue.findIndex(a=>a.ready<=t),old=archive.findIndex(a=>a.ready<=t&&(mode==='push'||mode==='pull'&&a.requestedAt!==null&&a.requestedAt<t&&t<=a.requestedAt+4));
  const data=[...records.values()].find(r=>!r.confirmed&&r.attempts<2&&r.ready<=t&&current.get(r.p.source)===key(r.p)&&useful(r,t));
  // No archive or receiver receipt oracle at the requester.
  const req=mode==='pull'&&[...records.values()].find(r=>wanted(r)&&r.attempts>0&&!r.confirmed&&(!useful(r,t)||current.get(r.p.source)!==key(r.p))&&r.requests<2&&t>r.until);
  let p=null,loss=false,origin='idle';
  if(name==='forged'&&t===1){p=packet(1,1,1);origin='fixture';}
  else if(lateFixture&&t===4){p=packet(1,1,1);origin='late-fixture';}
  else if(ret>=0){p=queue.splice(ret,1)[0].p;origin='return';}
  else if(data){p=data.p;origin='data';data.attempts++;data.ready=t+3;loss=(name==='data-loss'||name==='forged')&&p.source===1&&data.attempts===1;}
  else if(old>=0){p=archive.splice(old,1)[0].p;origin='archive';m.archiveTx++;log(at,'archive-service',{packet:p});}
  else if(req){p={...req.p,kind:2};origin='request';req.requests++;req.until=t+4;loss=requestLoss&&req.requests===1;if(loss)m.requestLoss++;}
  if(!p){m.idle++;log(at,'idle');continue;}
  const r=records.get(key(p));
  if(origin==='return'||origin==='archive'){loss=name==='ack-loss'&&p.source===1&&!r.ackLost;if(loss)r.ackLost=true;}
  m[['data','ack','request'][p.kind]]++;log(at,'tx',{packet:p,origin,loss});
  const wave=parent.render(p,seed+t*997,loss);pcm.set(wave,at);const d=decode(wave);
  if(!d){log(end,'refusal');continue;}
  const k=key(d);
  if(d.kind===2){m.requestDecoded++;const a=archive.find(a=>key(a.p)===k);
   if(a)a.requestedAt=t;else m.requestMiss++;
   log(end,'historical-request',{packet:d,available:!!a});continue;
  }
  if(d.kind===0){const accepted=current.get(d.source)===k;log(end,'data-receipt',{packet:d,accepted});if(!accepted)continue;received.add(k);if(!queue.some(a=>key(a.p)===k))queue.push({p:{...d,kind:1},ready:t+(name==='delayed'?4:1)});}
  else{const rec=records.get(k),historical=!rec||!useful(rec,t)||current.get(d.source)!==k,within=!!rec&&rec.requests>0&&t<=rec.until;
   const eligible=!!rec&&rec.attempts>0&&!rec.confirmed;
   const accepted=eligible&&(mode!=='pull'||!historical||within),genuine=received.has(k);
   if(eligible&&historical&&!within){m.unsolicited++;if(mode==='pull')m.rejectedHistorical++;}
   if(accepted){rec.confirmed=true;if(!genuine)m.invalid++;}
   log(end,'ack-receipt',{packet:d,accepted,evaluatorGenuine:genuine,historical,within});
  }
 }
 m.archivePending=archive.length;
 const f=freshness(trace,pcm.length,ttl*SLOT/RATE),historical=f.records.filter(x=>x.confirmed&&x.genuine),target=f.records.filter(x=>wanted({p:x.packet}));
 return {name,mode,ttl,seed,interest,requestLoss,lateFixture,trace,pcm,metrics:{...m,...f.totals,allGenuine:historical.length,wantedGenuine:target.filter(x=>x.confirmed&&x.genuine).length,wantedOffers:target.length,unwantedGenuine:historical.filter(x=>!wanted({p:x.packet})).length},intervals:f.timeline};
}
function qualify(){
 let checks=0;const check=(v,m)=>{checks++;if(!v)throw Error(m);};const rows=[],aggregate={},specimens=[];let parentMatches=0;
 for(let s=1;s<=2;s++)for(let v=1;v<=3;v++)for(let kind=0;kind<=2;kind++){const p=packet(s,v,kind);check(JSON.stringify(decode(parent.render(p,317)))===JSON.stringify(p),'roundtrip');check(decode(parent.render(p,317,true))===null,'loss');if(kind===2)check(parent.decode(parent.render(p,317))===null,'legacy request refusal');}
 function run(name,mode,ttl,seed,interest,loss=false,fixture=false){
 const s=simulate(name,mode,ttl,seed,interest,loss,fixture),m=s.metrics;
 check(m.data+m.ack+m.request+m.idle===H,'slot accounting');check(m.archived===m.archiveTx+m.evicted+m.expired+m.archivePending,'archive conservation');check(s.pcm.every(x=>Math.abs(x)<=3080),'PCM peak');check(m.genuine+m.falseBelief===m.believed,'belief partition');
 check(s.trace.filter(e=>e.type==='archive-service').every(e=>s.trace.some(q=>q.type==='archive-enqueued'&&key(q.packet)===key(e.packet)&&q.at<=e.at)),'archive causality');
 if(mode==='pull')check(s.trace.filter(e=>e.type==='ack-receipt'&&e.accepted&&e.historical).every(e=>e.within),'historical gate');
 if(!fixture&&mode!=='pull'&&interest==='all'&&!loss){const b=archiveParent.simulate(name,mode==='push'?'idle-archive':'bilateral',ttl,seed),f=freshness(b.trace,b.samples,ttl*SLOT/RATE);check(s.pcm.every((x,i)=>x===b.pcm[i]),'parent pcm');check(['genuine','received','falseBelief'].every(k=>m[k]===f.totals[k]),'parent metric');parentMatches++;}
 const row={name,mode,ttl,seed,interest,loss,fixture,...m};rows.push(row);return {s,row};
 }
 for(const seed of [30133,59149])for(const name of cases)for(const ttl of [2,3,4,6])for(const interest of ['all','source1','none'])for(const mode of modes){
 const {s,row}=run(name,mode,ttl,seed,interest);const k=ttl+'/'+interest+'/'+mode,a=aggregate[k]??(aggregate[k]={runs:0,genuine:0,received:0,allGenuine:0,wantedGenuine:0,unwantedGenuine:0,ack:0,data:0,request:0,requestMiss:0,invalid:0});a.runs++;for(const f of Object.keys(a))if(f!=='runs')a[f]+=row[f];
 if(seed===30133&&ttl===3&&interest==='source1'&&['churn','delayed'].includes(name))specimens.push({row,trace:s.trace,pcm:s.pcm,intervals:s.intervals});
 }
 const controls=[];for(const seed of [7013,8851])for(const name of ['data-loss','delayed','churn'])for(const loss of [false,true])for(const fixture of [false,true]){const {s,row}=run(name,'pull',3,seed,'all',loss,fixture);controls.push(row);if(seed===7013&&name==='data-loss')specimens.push({row,trace:s.trace,pcm:s.pcm,intervals:s.intervals});}
 check(controls.filter(x=>x.name==='data-loss'&&x.fixture).every(x=>x.invalid===1),'preserved late false witness');
 check(controls.filter(x=>x.name==='data-loss'&&!x.fixture).every(x=>x.invalid===0),'no late fixture control');
 const paired={currentLoss:0,receivedLoss:0,wantedLoss:0,pairs:0};
 for(const b of rows.filter(x=>!x.fixture&&!x.loss&&x.mode==='push')){const q=rows.find(x=>x.mode==='pull'&&!x.fixture&&!x.loss&&x.name===b.name&&x.ttl===b.ttl&&x.seed===b.seed&&x.interest===b.interest);paired.pairs++;if(q.genuine<b.genuine)paired.currentLoss++;if(q.received<b.received)paired.receivedLoss++;if(q.wantedGenuine<b.wantedGenuine)paired.wantedLoss++;}
 return {receipt:{schema:'mhac-interaction-historical-demand-v1',parentRef:'077e36808c7911575b88251172c9a3ce37fa3831',rate:RATE,slotSamples:SLOT,frameSamples:FRAME,checks,parentMatches,rows,aggregate,controls,paired},specimens};
}
return {simulate,qualify,decode};
};
const api=implementation(require('./narrow-deadline-relay.cjs'),require('./evidence-freshness.cjs').freshness,require('./archive-recovery.cjs'));
module.exports=api;
if(require.main===module){(function cli(api,pins){
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
for(const [name,expected] of Object.entries(pins)){const b=fs.readFileSync(path.join(__dirname,name));if(crypto.createHash('sha1').update('blob '+b.length+'\0').update(b).digest('hex')!==expected)throw Error('parent mismatch '+name);}
const out=process.argv[2]||'historical-demand-output';fs.mkdirSync(out,{recursive:true});
const {receipt,specimens}=api.qualify();receipt.pins=pins;receipt.stimuli=[];
for(const {row,trace,pcm,intervals} of specimens){
 const stem=[row.name,row.mode,row.interest,row.loss?'lost':'clean',row.fixture?'fixture':'normal'].join('-'),b=Buffer.alloc(44+pcm.length*2);b.write('RIFF');b.writeUInt32LE(b.length-8,4);b.write('WAVEfmt ',8);b.writeUInt32LE(16,16);b.writeUInt16LE(1,20);b.writeUInt16LE(1,22);b.writeUInt32LE(16000,24);b.writeUInt32LE(32000,28);b.writeUInt16LE(2,32);b.writeUInt16LE(16,34);b.write('data',36);b.writeUInt32LE(pcm.length*2,40);pcm.forEach((v,i)=>b.writeInt16LE(Math.round(v/2),44+2*i));fs.writeFileSync(path.join(out,stem+'.wav'),b);fs.writeFileSync(path.join(out,stem+'.json'),JSON.stringify({row,trace,intervals},null,2));receipt.stimuli.push({row,stem,gain:.5,sha256:crypto.createHash('sha256').update(b).digest('hex')});
}
fs.writeFileSync(path.join(out,'receipt.json'),JSON.stringify(receipt,null,2));
const html='<!doctype html><meta charset=utf-8><title>Historical evidence on demand</title><style>body{font:16px system-ui;max-width:1050px;margin:2em auto;padding:1em}td,th{padding:.5em;border:1px solid #999}table{border-collapse:collapse}</style><h1>Historical evidence on demand</h1><p>Synthetic, fixed-slot FSK. Start at low device volume. No autoplay. Historical request windows do not authenticate ACKs.</p><label>Deadline slots <select id="d"><option>2</option><option selected>3</option><option>4</option><option>6</option></select></label> <label>Interest <select id="i"><option>all</option><option>source1</option><option>none</option></select></label><div id="v"></div><h2>Original half-gain replays</h2>'+receipt.stimuli.map(x=>'<p>'+x.stem+' <audio controls preload=none src="'+x.stem+'.wav"></audio> <a href="'+x.stem+'.json">trace</a></p>').join('')+'<script>const a='+JSON.stringify(receipt.aggregate)+';const d=document.getElementById("d"),i=document.getElementById("i"),v=document.getElementById("v");function draw(){v.innerHTML="<table><tr><th>Policy</th><th>Current confirmed agent-s</th><th>Wanted confirmations</th><th>All confirmations</th><th>ACK/request frames</th><th>False accepts</th></tr>"+["bilateral","push","pull"].map(m=>{const x=a[d.value+"/"+i.value+"/"+m];return "<tr><td>"+m+"</td><td>"+(x.genuine/16000).toFixed(3)+"</td><td>"+x.wantedGenuine+"</td><td>"+x.allGenuine+"</td><td>"+x.ack+"/"+x.request+"</td><td>"+x.invalid+"</td></tr>"}).join("")+"</table>"}d.onchange=i.onchange=draw;draw()</script>';fs.writeFileSync(path.join(out,'index.html'),html);console.log(JSON.stringify({checks:receipt.checks,paired:receipt.paired,aggregate:receipt.aggregate,stimuli:receipt.stimuli.length}));
})(api,pins);}

// Executed V8 twice, identical full receipts; native CLI not qualified at publication.
// {"checks":3100,"rows":528,"parentMatches":112,"paired":{"currentLoss":0,"receivedLoss":0,"wantedLoss":4,"pairs":168},"aggregate":{"3/all/bilateral":{"runs":14,"genuine":38400,"received":153600,"allGenuine":16,"wantedGenuine":16,"unwantedGenuine":0,"ack":20,"data":40,"request":0,"requestMiss":0,"invalid":2},"3/all/push":{"runs":14,"genuine":38400,"received":153600,"allGenuine":34,"wantedGenuine":34,"unwantedGenuine":0,"ack":38,"data":40,"request":0,"requestMiss":0,"invalid":2},"3/all/pull":{"runs":14,"genuine":38400,"received":153600,"allGenuine":34,"wantedGenuine":34,"unwantedGenuine":0,"ack":38,"data":40,"request":26,"requestMiss":8,"invalid":2},"3/source1/bilateral":{"runs":14,"genuine":38400,"received":153600,"allGenuine":16,"wantedGenuine":12,"unwantedGenuine":4,"ack":20,"data":40,"request":0,"requestMiss":0,"invalid":2},"3/source1/push":{"runs":14,"genuine":38400,"received":153600,"allGenuine":34,"wantedGenuine":14,"unwantedGenuine":20,"ack":38,"data":40,"request":0,"requestMiss":0,"invalid":2},"3/source1/pull":{"runs":14,"genuine":38400,"received":153600,"allGenuine":18,"wantedGenuine":14,"unwantedGenuine":4,"ack":22,"data":40,"request":10,"requestMiss":8,"invalid":2},"3/none/bilateral":{"runs":14,"genuine":38400,"received":153600,"allGenuine":16,"wantedGenuine":0,"unwantedGenuine":16,"ack":20,"data":40,"request":0,"requestMiss":0,"invalid":2},"3/none/push":{"runs":14,"genuine":38400,"received":153600,"allGenuine":34,"wantedGenuine":0,"unwantedGenuine":34,"ack":38,"data":40,"request":0,"requestMiss":0,"invalid":2},"3/none/pull":{"runs":14,"genuine":38400,"received":153600,"allGenuine":16,"wantedGenuine":0,"unwantedGenuine":16,"ack":20,"data":40,"request":0,"requestMiss":0,"invalid":2}},"controls":[{"seed":7013,"loss":false,"fixture":false,"invalid":0,"req":2,"miss":2,"rejected":0,"all":1},{"seed":7013,"loss":false,"fixture":true,"invalid":1,"req":1,"miss":1,"rejected":0,"all":1},{"seed":7013,"loss":true,"fixture":false,"invalid":0,"req":2,"miss":1,"rejected":0,"all":1},{"seed":7013,"loss":true,"fixture":true,"invalid":1,"req":1,"miss":0,"rejected":0,"all":1},{"seed":8851,"loss":false,"fixture":false,"invalid":0,"req":2,"miss":2,"rejected":0,"all":1},{"seed":8851,"loss":false,"fixture":true,"invalid":1,"req":1,"miss":1,"rejected":0,"all":1},{"seed":8851,"loss":true,"fixture":false,"invalid":0,"req":2,"miss":1,"rejected":0,"all":1},{"seed":8851,"loss":true,"fixture":true,"invalid":1,"req":1,"miss":0,"rejected":0,"all":1}],"specimens":10,"peak":3080}
