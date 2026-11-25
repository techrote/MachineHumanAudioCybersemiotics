"use strict";
// Grammars lane, Refs #452 / Draft #453. Synthetic aligned PCM; no truth/authentication claim.
// Parent 915baf07d49e22d01bd651579a00f41f0071bc82; accepted main 495a98ca12bae467a507031f04931aa4254b1866.
// One AI agent, no subagents. Terminal means respondent declares this enquiry closed, not permanent truth.
const pins={"response-revisions.cjs":"9592ff3004db7763dceb3e3164b9455b102e1cef","typed-negative.cjs":"9de937800542e9af3ea3ec3fe3c58e9a74b8e3b0","systematic-mds.cjs":"3e74ca6f76b0e9fdb267c5b4e5734828ca27ddf3","algebraic-binding.cjs":"7415235429fd86aa96bde3f69bcfe10cf5eb8fa2","recursive.cjs":"7d9e305857b59e029913432bb40f713ab84b5a90","integrity.cjs":"a58403f51806c17d89c7ebaf098d2e19b0995a02","injective-tags.cjs":"d91e0ed1e8700ff78b12e7732c07ddfcfc189e08","block-binding.cjs":"4c8be6987b345a5084dee16cf9e7053726c034c9","clock-hypotheses.cjs":"45a5fafb6506ba9211970c1cd58ac2840fbfc670","clock.cjs":"49a6849ae8a0094d30d499718ce21dd3029c0f8a","distributed.cjs":"c727fe13c7131e9a5eac9240fa909c34bcc5011c","acquisition.cjs":"70fb9823d596300112282a73386d6c6088b5d793","local-clock.cjs":"18e86536a85a7327499be1d5ff5719518d1a696a","epoch-fence.cjs":"311aa5e8d621238eec47d238861e8bec1bb02a94","transaction-clarification.cjs":"37bd277c96b08bff10465b17de246bb570c68d09","clarification-controls.cjs":"9434b7134f23c54e3870f78efcc84fa145a70d2d","sequential-clarification.cjs":"5a83020a1548ed2af7f15aa248e834105d449afd"};

const M=require("./systematic-mds.cjs"),V=require("./response-revisions.cjs"),E=require("./epoch-fence.cjs"),A=require("./algebraic-binding.cjs"),T=require("./transaction-clarification.cjs"),C=require("./clarification-controls.cjs"),I=require("./integrity.cjs"),R=require("./recursive.cjs");
const valid=(x,n)=>Number.isInteger(x)&&x>=0&&x<n,eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const identity=t=>t.epoch*16+t.side*8+t.slot;
const row=k=>[14,Math.floor(k/289),Math.floor(k/17)%17,k%17];
const codec=M.build(Array.from({length:3840},(_,k)=>row(k)));
function encode(t){
 if(!valid(t.epoch,12)||!valid(t.side,2)||!valid(t.slot,8)||!valid(t.revision,2)||!valid(t.act,20)||typeof t.terminal!=="boolean"||(t.terminal&&t.revision!==1))throw Error("response");
 return t.terminal?M.encode(row(identity(t)*20+t.act)):V.encode(t);
}
function parse(x){
 const k=M.decode(x,codec);
 if(k===null){const t=V.parse(x);return t?{...t,terminal:false}:null;}
 const [,b,c,d]=codec.map.get(k),n=b*289+c*17+d,a=Math.floor(n/20);
 return {epoch:Math.floor(a/16),side:Math.floor(a%16/8),slot:a%8,revision:1,act:n%20,terminal:true};
}
// Snapshot binds the canonical request codeword. This detects accidental cross-request restore,
// not rollback within that identity, tampering, or epoch reuse. Caller owns durable storage.
function receiver(request,snapshot=null){
 const q=E.parse(request);if(!q||q.type!=="request")throw Error("request");
 const bound=E.encode(q);
 let s=null;
 if(snapshot!==null){
  if(snapshot.schema!=="mhac-finality-v1"||!eq(snapshot.request,bound))throw Error("snapshot identity");
  if(snapshot.state!==null){
   const t=snapshot.state;
   if(!t||!valid(t.revision,2)||!valid(t.act,20)||typeof t.terminal!=="boolean"||typeof t.conflict!=="boolean"||(t.terminal&&t.revision!==1))throw Error("snapshot state");
   s={revision:t.revision,act:t.act,terminal:t.terminal,conflict:t.conflict};
  }
 }
 return {
  ingest(body){
   const t=parse(body);if(!t)return "undecodable";if(identity(t)!==identity(q))return "mismatch";
   if(s&&t.revision<s.revision)return "stale";
   if(!s||t.revision>s.revision){s={revision:t.revision,act:t.act,terminal:t.terminal,conflict:false};return "accepted";}
   if(t.act!==s.act){s.conflict=true;return "conflict";}
   if(s.conflict)return "conflict";
   if(t.terminal&&!s.terminal){s.terminal=true;return "closed";}
   return "duplicate";
  },
  snapshot(){return {schema:"mhac-finality-v1",request:bound.slice(),state:s?{...s}:null};},
  value(){return !s||s.conflict?null:{revision:s.revision,act:s.act,terminal:s.terminal};}
 };
}
function qualify(){
 let assertions=0;const check=(ok,m)=>{assertions++;if(!ok)throw Error(m);};
 const masks=Array.from({length:256},(_,m)=>Array.from({length:8},(_,i)=>i).filter(i=>m&(1<<i))).filter(m=>m.length&&m.length<=4);
 const erase=(x,m)=>x.map((v,i)=>m.includes(i)?null:v);
 const semantic=M.build(A.versions.append),counts={clean:0,erasure:0,substitution:0,legacyRefusal:0,snapshotMismatch:0};
 const seen=new Set(),requests=[];
 for(let a=0;a<192;a++){
  const q={epoch:Math.floor(a/16),side:Math.floor(a%16/8),slot:a%8};
  requests.push(E.encode({...q,type:"request",value:null}));
  for(let act=0;act<20;act++){
   const t={...q,revision:1,act,terminal:true},x=encode(t);
   check(eq(parse(x),t),"terminal clean");counts.clean++;seen.add(x.join(","));
   check(V.parse(x)===null&&E.parse(x)===null&&T.parse(x)===null&&C.parseControl(x)===null&&M.decode(x,semantic)===null,"old namespace refusal");
   for(const mask of masks)if(mask.length<=2||(a*20+act)%37===0){check(eq(parse(erase(x,mask)),t),"erasure");counts.erasure++;}
   if((a*20+act)%37===0)for(let j=0;j<8;j++)for(let v=0;v<17;v++)if(v!==x[j]){
    const y=x.slice();y[j]=v;check(parse(y)===null,"single substitution");counts.substitution++;
   }
   for(const revision of [0,1]){
    const old={...t,revision,terminal:false},body=V.encode(old);
    check(eq(encode(old),body)&&eq(parse(body),old),"old body unchanged");counts.legacyRefusal++;
   }
  }
 }
 check(seen.size===3840,"no collision");
 for(const x of semantic.book){check(parse(x)===null,"semantic refusal");counts.legacyRefusal++;}
 for(let e=0;e<12;e++)for(let side=0;side<2;side++){
  for(const type of ["retire","retired"]){check(parse(E.encode({type,epoch:e,side}))===null,"retirement refusal");counts.legacyRefusal++;}
  for(let slot=0;slot<8;slot++){check(parse(E.encode({type:"request",epoch:e,side,slot,value:null}))===null,"request refusal");counts.legacyRefusal++;}
 }
 for(let side=0;side<2;side++)for(let slot=0;slot<8;slot++){
  check(parse(C.encodeRequest(side,slot))===null,"legacy request");counts.legacyRefusal++;
  for(let v=0;v<17;v++){check(parse(C.encodeReply(side,slot,v))===null,"legacy reply");counts.legacyRefusal++;}
  for(let tag=0;tag<17;tag++){
   check(parse(T.encode("request",side,slot,tag))===null,"tag request");counts.legacyRefusal++;
   for(let v=0;v<17;v++){check(parse(T.encode("reply",side,slot,tag,v))===null,"tag reply");counts.legacyRefusal++;}
  }
 }
 // Compare implicit closure at revision 1 versus explicit terminal declaration.
 // Identical three transmission opportunities, loss masks and delivery orders.
 // Baseline sees ordinary revision 1 with the same act, never an oracle finality bit.
 const id={epoch:3,side:1,slot:5},q=E.encode({...id,type:"request",value:null});
 const perms=[[0,1,2],[0,2,1],[1,0,2],[1,2,0],[2,0,1],[2,1,0]];
 const stats=Object.fromEntries(["implicit","explicit"].map(p=>[p,{correctClosure:0,falseClosure:0,missedClosure:0,correctOpen:0,newestValue:0}]));
 const conditions=[];
 for(let a=0;a<20;a++)for(let b=0;b<20;b++)for(const terminal of [false,true]){
  const old=encode({...id,revision:0,act:a,terminal:false}),next=encode({...id,revision:1,act:b,terminal}),legacy=V.encode({...id,revision:1,act:b});
  for(const order of perms)for(let loss=0;loss<8;loss++){
   const er=receiver(q),ir=V.receiver(q),delivered=order.filter(i=>!(loss&(1<<i)));
   for(const i of delivered){er.ingest([old,next,old][i]);ir.ingest([old,legacy,old][i]);}
   const x=er.value(),y=ir.value(),record={a,b,terminal,order,loss,delivered:delivered.length};
   for(const [p,v,closed] of [["implicit",y,!!y&&y.revision===1],["explicit",x,!!x&&x.terminal]]){
    const k=terminal?(closed?"correctClosure":"missedClosure"):(closed?"falseClosure":"correctOpen");
    stats[p][k]++;stats[p].newestValue+=+(!!v&&v.revision===1&&v.act===b);record[p]=k;
   }
   check(!x||x.terminal===(terminal&&delivered.includes(1)),"explicit closure semantics");
   conditions.push(record);
  }
 }
 // All distinct request-pair restore attempts, no durable storage or authenticity claim.
 for(let i=0;i<requests.length;i++){
  const r=receiver(requests[i]),t=E.parse(requests[i]);r.ingest(encode({...t,revision:1,act:7,terminal:true}));
  const snap=JSON.parse(JSON.stringify(r.snapshot()));
  check(eq(receiver(requests[i],snap).value(),r.value()),"same identity restore");
  for(let j=0;j<requests.length;j++)if(j!==i){
   let rejected=false;try{receiver(requests[j],snap);}catch(e){rejected=e.message==="snapshot identity";}
   check(rejected,"cross request snapshot");counts.snapshotMismatch++;
  }
 }
 const provisional=encode({...id,revision:1,act:7,terminal:false}),final=encode({...id,revision:1,act:7,terminal:true}),different=encode({...id,revision:1,act:8,terminal:true}),old=encode({...id,revision:0,act:17,terminal:false});
 const r=receiver(q);r.ingest(old);const stale=r.snapshot();r.ingest(provisional);
 check(r.ingest(final)==="closed"&&r.value().terminal,"explicit upgrade");
 check(r.ingest(provisional)==="duplicate"&&r.value().terminal,"delayed provisional does not reopen");
 check(r.ingest(different)==="conflict"&&r.value()===null,"terminal equivocation");
 check(r.ingest(final)==="conflict"&&r.value()===null,"conflict sticky");
 const rolled=receiver(q,stale);check(rolled.value().terminal===false,"rollback witness");
 const forged=receiver(q);forged.ingest(different);check(forged.value().terminal&&forged.value().act===8,"forgery witness");
 const specimens=[],pcmCases=[];let peak=0,pcmBodies=0;
 for(const phase of [.137,2.419,5.827])for(const missing of [0,4,5]){
  const r=receiver(q);
  for(const [name,x] of [["provisional",provisional],["terminal",final],["delayed-provisional",provisional]]){
   const tokens=erase(x,Array.from({length:missing},(_,i)=>i)),pcm=I.render(tokens,phase),y=I.receive(pcm);
   check(eq(tokens,y),"aligned PCM");r.ingest(y);pcmBodies++;
   for(const v of pcm)peak=Math.max(peak,Math.abs(v));
   if(phase===.137)specimens.push({name:name+"-"+missing+".wav",tokens,phase});
  }
  const value=r.value();check(missing===5?value===null:value.terminal&&value.act===7,"PCM closure");pcmCases.push({phase,missing,value});
 }
 check(peak<=4096,"digital peak");
 return {schema:"mhac-terminal-responses-v1",parent:"915baf07d49e22d01bd651579a00f41f0071bc82",pins,assertions,counts,stats,conditions,pcmBodies,pcmCases,specimens,peak,bodyMs:640,witnesses:{rollback:rolled.value(),forged:forged.value(),conflict:r.snapshot()}};
}
const summary=q=>({assertions:q.assertions,counts:q.counts,stats:q.stats,matched:q.conditions.length,pcmBodies:q.pcmBodies,pcmCases:q.pcmCases,peak:q.peak,specimens:q.specimens.length,witnesses:q.witnesses});
module.exports={encode,parse,receiver,qualify,summary};
if(require.main===module){
 const fs=require("node:fs"),path=require("node:path"),crypto=require("node:crypto");
 for(const [name,expected] of Object.entries(pins)){const bytes=fs.readFileSync(path.join(__dirname,name));if(crypto.createHash("sha1").update("blob "+bytes.length+"\0").update(bytes).digest("hex")!==expected)throw Error("dependency changed: "+name);}
 const q=qualify(),out=process.argv[2]||"output-finality";fs.mkdirSync(out,{recursive:true});
 const manifest=q.specimens.map(s=>{const w=R.wav(I.render(s.tokens,s.phase));fs.writeFileSync(path.join(out,s.name),w);return {...s,sha256:crypto.createHash("sha256").update(w).digest("hex")};});
 fs.writeFileSync(path.join(out,"qualification.json"),JSON.stringify(q,null,2));fs.writeFileSync(path.join(out,"stimuli.json"),JSON.stringify(manifest,null,2));
 fs.writeFileSync(path.join(out,"index.html"),'<!doctype html><meta charset="utf-8"><title>Terminal acoustic responses</title><h1>Terminal acoustic responses</h1><p>Synthetic aligned PCM. Start at low volume. Terminal is a closure declaration, not truth or authentication.</p><pre>'+JSON.stringify(summary(q),null,2)+'</pre>'+manifest.map(s=>'<h2>'+s.name+'</h2><audio controls preload="none" src="'+s.name+'"></audio>').join(""));
 console.log(JSON.stringify(summary(q),null,2));
}
