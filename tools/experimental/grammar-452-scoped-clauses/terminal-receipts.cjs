"use strict";
// Grammars lane, Refs #452 / Draft #453. Synthetic aligned PCM, no human evidence.
// Parent d0a7c818b1ec9070cb539422a04b01c5d0c63d64; accepted main 495a98ca12bae467a507031f04931aa4254b1866.
// One GPT-6.2 agent; no subagents. ACK asserts receipt of a specific terminal act,
// not truth, authentication, permanent closure, or common knowledge.
const parent="d0a7c818b1ec9070cb539422a04b01c5d0c63d64", pins={"terminal-responses.cjs":"4d79022bf88c07ad1dba8e7817b5e01d2c823a90","response-revisions.cjs":"9592ff3004db7763dceb3e3164b9455b102e1cef","typed-negative.cjs":"9de937800542e9af3ea3ec3fe3c58e9a74b8e3b0","systematic-mds.cjs":"3e74ca6f76b0e9fdb267c5b4e5734828ca27ddf3","algebraic-binding.cjs":"7415235429fd86aa96bde3f69bcfe10cf5eb8fa2","recursive.cjs":"7d9e305857b59e029913432bb40f713ab84b5a90","integrity.cjs":"a58403f51806c17d89c7ebaf098d2e19b0995a02","injective-tags.cjs":"d91e0ed1e8700ff78b12e7732c07ddfcfc189e08","block-binding.cjs":"4c8be6987b345a5084dee16cf9e7053726c034c9","clock-hypotheses.cjs":"45a5fafb6506ba9211970c1cd58ac2840fbfc670","clock.cjs":"49a6849ae8a0094d30d499718ce21dd3029c0f8a","distributed.cjs":"c727fe13c7131e9a5eac9240fa909c34bcc5011c","acquisition.cjs":"70fb9823d596300112282a73386d6c6088b5d793","local-clock.cjs":"18e86536a85a7327499be1d5ff5719518d1a696a","epoch-fence.cjs":"311aa5e8d621238eec47d238861e8bec1bb02a94","transaction-clarification.cjs":"37bd277c96b08bff10465b17de246bb570c68d09","clarification-controls.cjs":"9434b7134f23c54e3870f78efcc84fa145a70d2d","sequential-clarification.cjs":"5a83020a1548ed2af7f15aa248e834105d449afd"};
const M=require("./systematic-mds.cjs"),F=require("./terminal-responses.cjs"),E=require("./epoch-fence.cjs"),
 V=require("./response-revisions.cjs"),A=require("./algebraic-binding.cjs"),T=require("./transaction-clarification.cjs"),
 C=require("./clarification-controls.cjs"),I=require("./integrity.cjs"),R=require("./recursive.cjs");
const valid=(v,n)=>Number.isInteger(v)&&v>=0&&v<n,eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const id=t=>t.epoch*16+t.side*8+t.slot;
const row=k=>[0,Math.floor(k/289),Math.floor(k/17)%17,k%17];
// An atomic semantic row [0,13,13,13] is outside ranks 0..3839.
const codec=M.build(Array.from({length:3840},(_,k)=>row(k)));
function encode(t){
 if(!t||!valid(t.epoch,12)||!valid(t.side,2)||!valid(t.slot,8)||!valid(t.act,20)||t.revision!==1||t.terminal!==true)throw Error("terminal ACK");
 return M.encode(row(id(t)*20+t.act));
}
function parse(body){
 const k=M.decode(body,codec);if(k===null)return null;
 const [,b,c,d]=codec.map.get(k),n=b*289+c*17+d,a=Math.floor(n/20);
 return {epoch:Math.floor(a/16),side:Math.floor(a%16/8),slot:a%8,revision:1,act:n%20,terminal:true};
}
// Sender releases its retained terminal body ONLY on a matching receipt.
// No address reuse, authentication, durable storage or rollback protection here.
function sender(body){
 const t=F.parse(body);if(!t||!t.terminal)throw Error("terminal body required");
 const canonical=F.encode(t);let acknowledged=false;
 return {pending:()=>!acknowledged,body:()=>acknowledged?null:canonical.slice(),
  ingest(ack){const a=parse(ack);if(!a||id(a)!==id(t)||a.act!==t.act)return false;acknowledged=true;return true;}};
}
function requester(request){
 const q=E.parse(request),r=F.receiver(request);
 return {receive(body){
  const status=r.ingest(body),t=F.parse(body),v=r.value();
  // Do not ACK provisional, foreign, or contradictory bodies. Duplicate matching
  // terminal bodies are ACKed again, since the previous receipt could be lost.
  const ack=t&&t.terminal&&id(t)===id(q)&&v&&v.terminal&&v.act===t.act?encode(t):null;
  return {status,ack};
 },value:()=>r.value(),snapshot:()=>r.snapshot()};
}
// Two scheduled forward/return opportunities. A mask bit erases an entire body.
// Policies receive the same exogenous loss schedule, but actual transmissions differ.
function trial(t,loss,policy,pcm=null){
 if(!["eager","once","retry"].includes(policy)||!valid(loss,16))throw Error("trial");
 const q=E.encode({...t,type:"request",value:null}),terminal=F.encode(t),s=sender(terminal),r=requester(q);
 let sent=0,acks=0,trace=[],release=policy==="eager",confirmed=false;
 for(let round=0;round<2;round++){
  if(round===1&&(policy!=="retry"||release))break;
  sent++;const f=!(loss&(1<<(2*round))),a=!(loss&(1<<(2*round+1)));
  let received=null;
  if(f)received=r.receive(pcm?pcm(terminal):terminal);
  let accepted=false;
  if(received?.ack){acks++;if(a){accepted=s.ingest(pcm?pcm(received.ack):received.ack);confirmed||=accepted;if(accepted)release=true;}}
  trace.push({round,forwardDelivered:f,ackEmitted:!!received?.ack,ackDelivered:!!received?.ack&&a,accepted});
 }
 const closed=!!r.value()?.terminal;
 return {policy,loss,sent,acks,bodyMs:640*(sent+acks),closed,release,confirmed,falseRelease:release&&!closed,trace};
}
function qualify(){
 let assertions=0;const check=(v,m)=>{assertions++;if(!v)throw Error(m);};
 const erase=(x,m)=>x.map((v,i)=>m&(1<<i)?null:v),masks=Array.from({length:256},(_,m)=>m).filter(m=>m.toString(2).replace(/0/g,"").length<=4);
 const semantic=M.build(A.versions.append),counts={clean:0,erasure:0,substitution:0,priorRefusal:0,wrongAct:0,wrongAddress:0},seen=new Set(),conditions=[];
 for(let n=0;n<3840;n++){
  const a=Math.floor(n/20),t={epoch:Math.floor(a/16),side:Math.floor(a%16/8),slot:a%8,revision:1,act:n%20,terminal:true},x=encode(t);
  check(eq(parse(x),t),"ACK clean");counts.clean++;seen.add(x.join(","));
  check(F.parse(x)===null&&E.parse(x)===null&&T.parse(x)===null&&C.parseControl(x)===null&&M.decode(x,semantic)===null,"old namespace");counts.priorRefusal++;
  for(const m of masks)if(m&&(m.toString(2).replace(/0/g,"").length<=2||n%37===0)){check(eq(parse(erase(x,m)),t),"erasure");counts.erasure++;}
  if(n%37===0)for(let j=0;j<8;j++)for(let v=0;v<17;v++)if(v!==x[j]){let y=x.slice();y[j]=v;check(parse(y)===null,"substitution");counts.substitution++;}
  for(const revision of [0,1]){check(parse(V.encode({...t,revision}))===null,"provisional not ACK");counts.priorRefusal++;}
  check(parse(F.encode(t))===null,"terminal not ACK");counts.priorRefusal++;
  const s=sender(F.encode(t));
  for(let act=0;act<20;act++)if(act!==t.act){check(!s.ingest(encode({...t,act}))&&s.pending(),"wrong act");counts.wrongAct++;}
  const other=(a+1)%192;check(!s.ingest(encode({...t,epoch:Math.floor(other/16),side:Math.floor(other%16/8),slot:other%8})),"wrong address");counts.wrongAddress++;
  check(s.ingest(x)&&!s.pending()&&s.body()===null,"matched ACK");check(s.ingest(x),"duplicate ACK");
 }
 check(seen.size===3840,"unique");
 for(const x of semantic.book){check(parse(x)===null,"semantic refusal");counts.priorRefusal++;}
 for(let e=0;e<12;e++)for(let side=0;side<2;side++){
  for(const type of ["retire","retired"]){check(parse(E.encode({type,epoch:e,side}))===null,"retire refusal");counts.priorRefusal++;}
  for(let slot=0;slot<8;slot++){check(parse(E.encode({type:"request",epoch:e,side,slot,value:null}))===null,"request refusal");counts.priorRefusal++;}
 }
 for(let side=0;side<2;side++)for(let slot=0;slot<8;slot++){
  check(parse(C.encodeRequest(side,slot))===null,"legacy request");counts.priorRefusal++;
  for(let v=0;v<17;v++){check(parse(C.encodeReply(side,slot,v))===null,"legacy reply");counts.priorRefusal++;}
  for(let tag=0;tag<17;tag++){check(parse(T.encode("request",side,slot,tag))===null,"tag request");counts.priorRefusal++;for(let v=0;v<17;v++){check(parse(T.encode("reply",side,slot,tag,v))===null,"tag reply");counts.priorRefusal++;}}
 }
 const policies=["eager","once","retry"],stats=Object.fromEntries(policies.map(p=>[p,{closed:0,released:0,confirmed:0,falseRelease:0,unconfirmedClosed:0,bodies:0}]));
 for(let act=0;act<20;act++)for(let loss=0;loss<16;loss++)for(const p of policies){
  const t={epoch:3,side:1,slot:5,revision:1,act,terminal:true},z=trial(t,loss,p),s=stats[p];
  s.closed+=+z.closed;s.released+=+z.release;s.confirmed+=+z.confirmed;s.falseRelease+=+z.falseRelease;s.unconfirmedClosed+=+(z.closed&&!z.confirmed);s.bodies+=z.sent+z.acks;
  if(p!=="eager")check(!z.falseRelease,"honest channel no premature release");
  check(z.sent<=2&&z.acks<=2&&(!z.confirmed||z.closed),"bounded causal receipt");
  conditions.push({act,...z});
 }
 const t={epoch:3,side:1,slot:5,revision:1,act:7,terminal:true},q=E.encode({...t,type:"request",value:null}),body=F.encode(t),r=requester(q);
 check(!r.receive(F.encode({...t,terminal:false})).ack,"provisional no ACK");
 check(!!r.receive(body).ack&&!!r.receive(body).ack,"duplicate ACK");
 check(!r.receive(F.encode({...t,act:8})).ack&&!r.receive(body).ack,"conflict refuses");
 const forged=sender(body);check(forged.ingest(encode(t)),"forged ACK witness");
 const lostAck=trial(t,10,"retry");check(lostAck.closed&&!lostAck.confirmed,"ACK loss witness");
 const pcmCases=[],specimens=[];let peak=0,pcmBodies=0;
 for(const phase of [.137,2.419,5.827])for(const missing of [0,4,5]){
  const pass=body=>{const tokens=erase(body,(1<<missing)-1),pcm=I.render(tokens,phase),got=I.receive(pcm);check(eq(tokens,got),"PCM token recovery");for(const v of pcm)peak=Math.max(peak,Math.abs(v));pcmBodies++;if(phase===.137)specimens.push({name:"body-"+missing+"-"+pcmBodies+".wav",tokens,phase});return got;};
  const z=trial(t,2,"retry",pass);check(missing===5?!z.closed&&!z.release:z.closed&&z.confirmed,"PCM receipt retry");pcmCases.push({phase,missing,...z});
 }
 check(peak<=4096,"peak");
 return {schema:"mhac-terminal-receipt-v1",parent,pins,assertions,counts,stats,conditions,pcmCases,pcmBodies,specimens,peak,witnesses:{lostAck,forgedRelease:!forged.pending(),conflictingRequester:r.snapshot()}};
}
const summary=q=>({assertions:q.assertions,counts:q.counts,stats:q.stats,conditions:q.conditions.length,pcmBodies:q.pcmBodies,pcmCases:q.pcmCases.map(({phase,missing,closed,confirmed,sent,acks})=>({phase,missing,closed,confirmed,sent,acks})),specimens:q.specimens.length,peak:q.peak,witnesses:q.witnesses});
module.exports={encode,parse,sender,requester,trial,qualify,summary};
if(require.main===module){
 const fs=require("node:fs"),path=require("node:path"),crypto=require("node:crypto");
 for(const [name,h] of Object.entries(pins)){const b=fs.readFileSync(path.join(__dirname,name));if(crypto.createHash("sha1").update("blob "+b.length+"\0").update(b).digest("hex")!==h)throw Error("dependency changed: "+name);}
 const q=qualify(),out=process.argv[2]||"output-receipts";fs.mkdirSync(out,{recursive:true});
 const manifest=q.specimens.map(s=>{const w=R.wav(I.render(s.tokens,s.phase));fs.writeFileSync(path.join(out,s.name),w);return {...s,sha256:crypto.createHash("sha256").update(w).digest("hex")};});
 fs.writeFileSync(path.join(out,"qualification.json"),JSON.stringify(q,null,2));fs.writeFileSync(path.join(out,"stimuli.json"),JSON.stringify(manifest,null,2));
 fs.writeFileSync(path.join(out,"index.html"),'<!doctype html><meta charset="utf-8"><title>Terminal receipt lab</title><h1>Terminal receipt lab</h1><p>Aligned synthetic PCM. Start at low volume. No autoplay. Receipt is not truth or authentication.</p><pre>'+JSON.stringify(summary(q),null,2)+'</pre>'+manifest.map(s=>'<h2>'+s.name+'</h2><audio controls preload="none" src="'+s.name+'"></audio>').join(""));
 console.log(JSON.stringify(summary(q),null,2));
}
