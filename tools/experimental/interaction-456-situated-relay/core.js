/* Situated Relay, synthetic-only. No external dependencies. */
(function(root){
const api=(function build(){
"use strict";
const actors=["operator","relay"],sources=["pump","fan"],scopes=["report","question","quotation","request"];
const key=m=>`${m.id}@${m.version}`;
const clone=x=>JSON.parse(JSON.stringify(x));
function world(policy="bound"){
 if(!["bound","latest"].includes(policy))throw Error("policy");
 return {schema:"situated-relay-v1",policy,t:0,seq:0,records:{},queue:[],playing:null,receipts:[],log:[],segments:[],latest:null};
}
function event(w,type,data={}){w.log.push({seq:++w.seq,t:w.t,type,...clone(data)});}
function current(w,m){return w.records[m.id]?.version===m.version;}
function live(w,m){return current(w,m)&&w.t<m.deadline;}
function schedule(w,m,repair=false){
 if(w.queue.length>=16){event(w,"queue-full",{key:key(m)});return false;}
 w.queue.push({message:clone(m),repair,remaining:2});return true;
}
function publish(w,m){
 if(!m||!["P","F"].includes(m.id)||!sources.includes(m.source)||!actors.includes(m.actor)||!scopes.includes(m.scope)||!["fault","clear"].includes(m.content)||!Number.isInteger(m.version)||m.version<1||!Number.isInteger(m.priority)||m.priority<0||m.priority>2||!Number.isInteger(m.deadline)||m.deadline<=w.t||m.source!==(m.id==="P"?"pump":"fan"))throw Error("message");
 const old=w.records[m.id];if(m.version!==(old?old.version+1:1))throw Error("version");
 w.records[m.id]={...clone(m),ack:false,repairUsed:false,action:"unknown",resolved:false};
 if(old){event(w,"superseded",{key:key(old),replacement:key(m)});w.queue=w.queue.filter(q=>current(w,q.message));if(w.playing&&!current(w,w.playing.message)){event(w,"interrupted",{key:key(w.playing.message),reason:"revision"});w.playing=null;}}
 schedule(w,m);event(w,"publish",{message:m});
}
function tick(w){
 w.queue=w.queue.filter(q=>{if(live(w,q.message))return true;event(w,"discard",{key:key(q.message),reason:"expired"});return false;});
 if(w.playing&&!live(w,w.playing.message)){event(w,"interrupted",{key:key(w.playing.message),reason:"expired"});w.playing=null;}
 w.queue.sort((a,b)=>b.message.priority-a.message.priority||a.message.deadline-b.message.deadline);
 if(w.playing&&w.queue.length&&w.queue[0].message.priority>w.playing.message.priority){const q=w.playing;event(w,"interrupted",{key:key(q.message),reason:"priority"});w.playing=null;if(w.queue.length<16)w.queue.push({...q,remaining:2});else event(w,"queue-full",{key:key(q.message)});}
 if(!w.playing&&w.queue.length){w.playing=w.queue.shift();event(w,"start",{key:key(w.playing.message),repair:w.playing.repair});}
 const q=w.playing;
 if(q){const m=q.message;w.segments.push({t:w.t,key:key(m),source:m.source,scope:m.scope,content:m.content,part:2-q.remaining,repair:q.repair});q.remaining--;if(!q.remaining){const receipt={id:"r"+(w.receipts.length+1),key:key(m),message:clone(m),completed:w.t+1,repair:q.repair};w.receipts.push(receipt);w.latest=receipt.id;event(w,"complete",{receipt});w.playing=null;}}
 else w.segments.push({t:w.t,key:null});
 w.t++;
}
function respond(w,kind,actor,receiptId){
 if(!actors.includes(actor)||!["ack","repair","action"].includes(kind))throw Error("response");
 const sent=w.receipts.find(x=>x.id===receiptId);
 const chosen=w.policy==="latest"&&kind==="ack"?w.receipts.find(x=>x.id===w.latest):sent;
 const m=chosen&&w.records[chosen.message.id];
 const valid=!!(chosen&&m&&key(m)===chosen.key&&m.actor===actor&&w.t<m.deadline&&chosen.completed<=w.t);
 let accepted=false,reason="unbound-or-stale";
 if(kind==="ack"&&w.policy==="latest"&&m){m.ack=true;accepted=true;reason="latest-id-only";}
 else if(valid){
  if(kind==="ack"){m.ack=true;accepted=true;reason="bound-receipt";}
  if(kind==="repair"){if(!m.repairUsed&&w.t+2<m.deadline&&schedule(w,m,true)){m.repairUsed=true;accepted=true;reason="bounded-repair";}else reason="budget-or-deadline";}
  if(kind==="action"){if(m.scope==="request"&&m.ack){m.action="reported";accepted=true;reason="explicit-fictional-action";}else reason="scope-or-ack";}
 }
 event(w,"response",{kind,actor,requested:receiptId??null,target:chosen?.key??null,accepted,reason});
 return accepted;
}
function resolve(w,id,version,evidence){
 const m=w.records[id];if(!m||m.version!==version||evidence!=="synthetic-world-clear")return false;
 m.resolved=true;event(w,"resolution",{key:key(m),evidence});return true;
}
function msg(id,version=1,actor="operator",priority=0,scope="request",deadline=20,content="fault"){return {id,version,actor,priority,scope,deadline,content,source:id==="P"?"pump":"fan"};}
function apply(w,e){
 if(e.op==="publish")publish(w,e.message);
 else if(e.op==="tick")tick(w);
 else if(e.op==="respond")return respond(w,e.kind,e.actor,e.receipt);
 else if(e.op==="resolve")return resolve(w,e.id,e.version,e.evidence);
 else throw Error("op");
}
function replay(policy,inputs){const w=world(policy);for(const e of inputs)apply(w,e);return w;}
function render(segment,rate=8000){
 if(rate!==8000)throw Error("rate");
 const n=rate/4,a=new Int16Array(n);if(!segment?.key)return a;
 const base=segment.source==="pump"?400:600, f=segment.part===0?base:base+100*scopes.indexOf(segment.scope)+50*(segment.content==="clear");
 for(let i=0;i<n;i++){const t=i/rate,env=Math.min(1,i/80,(n-1-i)/80);const amp=segment.repair?0.075:0.1;a[i]=Math.round(32767*amp*env*(Math.sin(2*Math.PI*f*t)+0.2*Math.sin(2*Math.PI*(segment.source==="pump"?2:3)*f*t))/1.2);}
 return a;
}
function wav(segments){
 const n=segments.length*2000,b=new Uint8Array(44+2*n),v=new DataView(b.buffer);
 const s=(o,x)=>{for(let i=0;i<x.length;i++)b[o+i]=x.charCodeAt(i);};
 s(0,"RIFF");v.setUint32(4,b.length-8,true);s(8,"WAVE");s(12,"fmt ");v.setUint32(16,16,true);v.setUint16(20,1,true);v.setUint16(22,1,true);v.setUint32(24,8000,true);v.setUint32(28,16000,true);v.setUint16(32,2,true);v.setUint16(34,16,true);s(36,"data");v.setUint32(40,n*2,true);
 let j=44;for(const seg of segments)for(const z of render(seg)){v.setInt16(j,z,true);j+=2;}return b;
}
function scenario({interrupt=true,revision=true,handover=true,wrongActor=false,expired=false,missing=false}={}){
 const e=[],p=m=>e.push({op:"publish",message:m}),t=(n=1)=>{for(let i=0;i<n;i++)e.push({op:"tick"});};
 p(msg("P",1,"operator",0,"request",12));t(2);
 if(interrupt){p(msg("F",1,"relay",2,"question",12));t(2);}
 if(revision){p(msg("P",2,handover?"relay":"operator",0,"quotation",12));t(2);}
 if(expired)t(12);
 e.push({op:"respond",kind:"ack",actor:wrongActor?"relay":"operator",receipt:missing?"missing":"r1"});return e;
}
function qualify(){
 let assertions=0;const check=(x,label)=>{assertions++;if(!x)throw Error(label);};
 const totals={cases:0,bound:{accepted:0,wrong:0,rejectedValid:0},latest:{accepted:0,wrong:0,rejectedValid:0}};let witness=null;
 for(let mask=0;mask<64;mask++){
  const [interrupt,revision,handover,wrongActor,expired,missing]=Array.from({length:6},(_,i)=>!!(mask&(1<<i)));
  const inputs=scenario({interrupt,revision,handover,wrongActor,expired,missing});
  const truth=!revision&&!wrongActor&&!expired&&!missing;
  totals.cases++;
  for(const policy of ["bound","latest"]){const w=replay(policy,inputs),last=w.log.at(-1),valid=truth&&last.target==="P@1";check(last.type==="response","last");
   if(last.accepted){totals[policy].accepted++;if(!valid){totals[policy].wrong++;if(policy==="latest"&&!witness)witness={mask,inputs,trace:w.log};}}
   if(truth&&(!last.accepted||last.target!=="P@1"))totals[policy].rejectedValid++;
   if(policy==="bound")check(last.accepted===truth,"bound truth");
   check(Object.values(w.records).every(m=>m.action==="unknown"&&!m.resolved),"ack not action");
   check(JSON.stringify(w)===JSON.stringify(replay(policy,inputs)),"replay deterministic");
  }
 }
 const w=world();publish(w,msg("P"));tick(w);publish(w,msg("F",1,"relay",2,"question"));tick(w);check(w.receipts.length===0,"partial no receipt");tick(w);check(w.receipts[0].key==="F@1","priority");tick(w);tick(w);check(w.receipts[1].key==="P@1","restart");check(w.segments.map(s=>s.key).join(",")==="P@1,F@1,F@1,P@1,P@1","timeline");
 check(!respond(w,"ack","relay","r2"),"wrong actor");check(respond(w,"repair","operator","r2"),"repair");check(!respond(w,"repair","operator","r2"),"bounded repair");tick(w);tick(w);check(w.receipts[2].repair,"repair receipt");check(respond(w,"ack","operator","r3"),"ack");check(respond(w,"action","operator","r3"),"explicit action");check(!w.records.P.resolved,"action not resolution");check(!resolve(w,"P",1,"ack"),"invalid evidence");check(resolve(w,"P",1,"synthetic-world-clear"),"independent resolution");check(respond(w,"ack","relay","r1"),"question ack");check(!respond(w,"action","relay","r1"),"question not action");
 publish(w,msg("P",2,"relay",0,"quotation",20));check(!respond(w,"ack","operator","r3"),"stale");check(!w.records.P.ack&&!w.records.P.resolved,"reset");
 tick(w);publish(w,msg("P",3,"relay",0,"report",20));tick(w);tick(w);check(!w.receipts.some(r=>r.key==="P@2"),"revision interrupted");
 const b=wav(w.segments);check(b.length===44+w.segments.length*4000,"wav length");let peak=0;for(const seg of w.segments){const a=render(seg);check(a[0]===0&&a.at(-1)===0,"taper");for(const x of a)peak=Math.max(peak,Math.abs(x));}check(peak<=3277,"peak");
 const short=world();publish(short,msg("P",1,"operator",0,"request",1));tick(short);tick(short);check(short.receipts.length===0,"deadline partial");
 return {schema:"situated-relay-qualification-v1",assertions,totals,peak,witness,interruptionTrace:w.log,segments:w.segments,limits:"scripted events, perfect symbolic receipts, no human or waveform decoding"};
}
return {world,publish,tick,respond,resolve,msg,apply,replay,render,wav,scenario,qualify};
})();
if(typeof module==="object"&&module.exports){module.exports=api;if(require.main===module){const fs=require("node:fs"),path=require("node:path"),out=process.argv[2]||"output";fs.mkdirSync(out,{recursive:true});const q=api.qualify();fs.writeFileSync(path.join(out,"qualification.json"),JSON.stringify(q,null,2)+"\n");fs.writeFileSync(path.join(out,"interruption.wav"),api.wav(q.segments));console.log(JSON.stringify({assertions:q.assertions,totals:q.totals,peak:q.peak}));}}else root.SituatedRelay=api;
})(typeof globalThis!=="undefined"?globalThis:this);
