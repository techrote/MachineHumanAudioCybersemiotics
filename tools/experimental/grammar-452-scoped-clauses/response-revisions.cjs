"use strict";
// Refs #452 / #453, Grammars lane. Synthetic aligned PCM, not authentication or human evidence.
// Parent b18e9fa1a5d5d2405245e3999125d12c5ac37c7c; accepted main 495a98ca12bae467a507031f04931aa4254b1866.
// One AI agent, no subagents. Revision 0 uses existing bodies; revision 1 is a new disjoint namespace.
// No wrap; a revision is ordering information, not proof of finality or truth.
const pins={"typed-negative.cjs":"9de937800542e9af3ea3ec3fe3c58e9a74b8e3b0","systematic-mds.cjs":"3e74ca6f76b0e9fdb267c5b4e5734828ca27ddf3","algebraic-binding.cjs":"7415235429fd86aa96bde3f69bcfe10cf5eb8fa2","recursive.cjs":"7d9e305857b59e029913432bb40f713ab84b5a90","integrity.cjs":"a58403f51806c17d89c7ebaf098d2e19b0995a02","injective-tags.cjs":"d91e0ed1e8700ff78b12e7732c07ddfcfc189e08","block-binding.cjs":"4c8be6987b345a5084dee16cf9e7053726c034c9","clock-hypotheses.cjs":"45a5fafb6506ba9211970c1cd58ac2840fbfc670","clock.cjs":"49a6849ae8a0094d30d499718ce21dd3029c0f8a","distributed.cjs":"c727fe13c7131e9a5eac9240fa909c34bcc5011c","acquisition.cjs":"70fb9823d596300112282a73386d6c6088b5d793","local-clock.cjs":"18e86536a85a7327499be1d5ff5719518d1a696a","epoch-fence.cjs":"311aa5e8d621238eec47d238861e8bec1bb02a94","transaction-clarification.cjs":"37bd277c96b08bff10465b17de246bb570c68d09","clarification-controls.cjs":"9434b7134f23c54e3870f78efcc84fa145a70d2d","sequential-clarification.cjs":"5a83020a1548ed2af7f15aa248e834105d449afd"};
const M=require("./systematic-mds.cjs"),E=require("./epoch-fence.cjs"),N=require("./typed-negative.cjs"),A=require("./algebraic-binding.cjs"),T=require("./transaction-clarification.cjs"),C=require("./clarification-controls.cjs"),I=require("./integrity.cjs"),R=require("./recursive.cjs");
const acts=20, addresses=192, total=acts*addresses, valid=(x,n)=>Number.isInteger(x)&&x>=0&&x<n;
const key=x=>x.reduce((s,v)=>s*17+v,0),eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const row=k=>[13,Math.floor(k/289),Math.floor(k/17)%17,k%17];
const codec=M.build(Array.from({length:total},(_,k)=>row(k)));
const identity=t=>t.epoch*16+t.side*8+t.slot;
function encode(t){
 if(!valid(t.epoch,12)||!valid(t.side,2)||!valid(t.slot,8)||!valid(t.revision,2)||!valid(t.act,acts))throw Error("invalid revision response");
 if(t.revision===0)return t.act<17?E.encode({type:"reply",epoch:t.epoch,side:t.side,slot:t.slot,value:t.act}):N.encode({kind:N.kinds[t.act-17],epoch:t.epoch,side:t.side,slot:t.slot});
 return M.encode(row(identity(t)*acts+t.act));
}
function parse(x){
 const k=M.decode(x,codec);
 if(k!==null){const [,b,c,d]=codec.map.get(k),r=b*289+c*17+d,a=Math.floor(r/acts);
 return {epoch:Math.floor(a/16),side:Math.floor(a%16/8),slot:a%8,revision:1,act:r%acts};}
 const p=E.parse(x),n=N.parse(x),v=n||p;
 if(!v||(!n&&p.type!=="reply"))return null;
 return {epoch:v.epoch,side:v.side,slot:v.slot,revision:0,act:n?17+N.kinds.indexOf(n.kind):p.value};
}
// Bounded per-request ledger. Caller owns live identity and persistent state.
// Equal revision with distinct payloads is a conflict, not a new update.
// Conflict remains latched until a strictly newer revision arrives; no finality inference.
function receiver(request,policy="ordered",snapshot=null){
 const q=E.parse(request);if(!q||q.type!=="request"||!["first","last","ordered"].includes(policy))throw Error("request/policy");
 let state=snapshot===null?null:{...snapshot};
 if(state!==null&&(!valid(state.revision,2)||!valid(state.act,acts)||typeof state.conflict!=="boolean"))throw Error("snapshot");
 return {
 ingest(body){const r=parse(body);if(!r)return "undecodable";if(identity(r)!==identity(q))return "mismatch";
 if(state===null){state={revision:r.revision,act:r.act,conflict:false};return "accepted";}
 if(policy==="first")return "ignored";
 if(policy==="last"){state={revision:r.revision,act:r.act,conflict:false};return "accepted";}
 if(r.revision<state.revision)return "stale";
 if(r.revision>state.revision){state={revision:r.revision,act:r.act,conflict:false};return "accepted";}
 if(r.act!==state.act){state.conflict=true;return "conflict";}
 return state.conflict?"conflict":"duplicate";
 },
 snapshot(){return state===null?null:{...state};},
 value(){return state===null||state.conflict?null:{revision:state.revision,act:state.act};}
 };
}
function qualify(){
 let assertions=0;const check=(v,msg)=>{assertions++;if(!v)throw Error(msg);};
 const semantic=M.build(A.versions.append), seen=new Set(), counts={clean:0,erasure:0,legacySeparation:0,substitution:0};
 const masks=Array.from({length:256},(_,m)=>Array.from({length:8},(_,j)=>j).filter(j=>m&(1<<j))).filter(x=>x.length<=4);
 const erase=(x,m)=>x.map((v,j)=>m.includes(j)?null:v);
 for(let a=0;a<addresses;a++)for(let act=0;act<acts;act++){
  const t={epoch:Math.floor(a/16),side:Math.floor(a%16/8),slot:a%8,revision:1,act},x=encode(t);
  check(eq(parse(x),t),"clean");counts.clean++;seen.add(x.join(","));
  check(M.decode(x,semantic)===null&&E.parse(x)===null&&N.parse(x)===null&&T.parse(x)===null&&C.parseControl(x)===null,"legacy exclusion");counts.legacySeparation++;
  for(const m of masks)if(m.length){check(eq(parse(erase(x,m)),t),"revision erasure");counts.erasure++;}
  // Full single-substitution values at every position on a deterministic stratified subset.
  if((a*acts+act)%37===0)for(let j=0;j<8;j++)for(let v=0;v<17;v++)if(v!==x[j]){let y=x.slice();y[j]=v;check(parse(y)===null,"substitution");counts.substitution++;}
  const old={...t,revision:0};check(eq(parse(encode(old)),old),"old response unchanged");
 }
 check(seen.size===total,"no collision");
 // Reverse exclusion in the same MDS namespace: semantic, all older controls and responses.
 for(const x of semantic.book)check(parse(x)===null,"semantic refused");
 for(let e=0;e<12;e++)for(let s=0;s<2;s++){
  for(const type of ["retire","retired"])check(parse(E.encode({type,epoch:e,side:s}))===null,"retire refused");
  for(let slot=0;slot<8;slot++)check(parse(E.encode({type:"request",epoch:e,side:s,slot,value:null}))===null,"request refused");
 }
 for(let s=0;s<2;s++)for(let slot=0;slot<8;slot++){
  check(parse(C.encodeRequest(s,slot))===null,"legacy request");
  for(let v=0;v<17;v++)check(parse(C.encodeReply(s,slot,v))===null,"legacy reply");
  for(let tag=0;tag<17;tag++){check(parse(T.encode("request",s,slot,tag))===null,"tagged request");
  for(let v=0;v<17;v++)check(parse(T.encode("reply",s,slot,tag,v))===null,"tagged reply");}
 }
 const qid={epoch:3,side:1,slot:5},q=E.encode({...qid,type:"request",value:null});
 // Every pair of semantic acts (including same act) and six distinct delivery permutations
 // of revision0, revision1 and a duplicate of revision0. Same bodies and airtime across policies.
 const permutations=[[0,1,2],[0,2,1],[1,0,2],[1,2,0],[2,0,1],[2,1,0]];
 const outcomes=Object.fromEntries(["first","last","ordered"].map(p=>[p,{correct:0,stale:0,refused:0}]));
 const cases=[];
 for(let a=0;a<acts;a++)for(let b=0;b<acts;b++){
  const old=encode({...qid,revision:0,act:a}),next=encode({...qid,revision:1,act:b});
  for(const order of permutations){
   const result={a,b,order};
   for(const policy of Object.keys(outcomes)){
    const r=receiver(q,policy);for(const i of order)r.ingest([old,next,old][i]);
    const v=r.value(),k=v===null?"refused":v.revision===1&&v.act===b?"correct":"stale";
    outcomes[policy][k]++;result[policy]=k;
    if(policy==="ordered")check(k==="correct","monotone under reorder");
   }cases.push(result);
  }
 }
 // Equal revision conflict, stale replay, wrong identity and rollback witnesses.
 const old=encode({...qid,revision:0,act:17}),next=encode({...qid,revision:1,act:7}),conflict=encode({...qid,revision:1,act:8});
 const r=receiver(q);r.ingest(old);const snap=r.snapshot();r.ingest(next);
 check(r.ingest(old)==="stale"&&r.value().act===7,"stale replay");
 const restored=receiver(q,"ordered",r.snapshot());check(restored.ingest(old)==="stale","persistent order");
 const rollback=receiver(q,"ordered",snap);check(rollback.ingest(old)==="duplicate"&&rollback.value().act===17,"rollback witness");
 check(r.ingest(conflict)==="conflict"&&r.value()===null,"equal-revision conflict");
 check(r.ingest(next)==="conflict"&&r.value()===null,"conflict sticky");
 check(r.ingest(encode({...qid,slot:6,revision:1,act:7}))==="mismatch","wrong address");
 const early=receiver(q);early.ingest(old);early.ingest(encode({...qid,revision:0,act:18}));check(early.value()===null,"early conflict");early.ingest(next);check(early.value().act===7,"new revision resolves conflict");
 // Loss of newest message cannot be inferred from old revision; matching forged newer
 // message is admissible. No sender authentication or completion claim.
 const lost=receiver(q);lost.ingest(old);check(lost.value().revision===0,"lost update witness");
 const forged=receiver(q);forged.ingest(conflict);check(forged.value().act===8,"forged revision witness");
 const specimens=[],pcmCases=[];let peak=0,pcmBodies=0;
 for(const phase of [.137,2.419,5.827])for(const missing of [0,4,5]){
  const rr=receiver(q);for(const [label,x] of [["initial",old],["revised",next],["delayed-initial",old]]){
   const tokens=erase(x,Array.from({length:missing},(_,i)=>i)),pcm=I.render(tokens,phase),y=I.receive(pcm);
   check(eq(tokens,y),"aligned PCM");const wav=R.wav(pcm),h=new DataView(wav.buffer,wav.byteOffset,wav.byteLength);
   check(h.getUint32(24,true)===16000&&h.getUint32(40,true)===pcm.length*2,"WAV");
   for(const v of pcm)peak=Math.max(peak,Math.abs(v));pcmBodies++;
   rr.ingest(y);if(phase===.137)specimens.push({name:label+"-"+missing+".wav",tokens,phase});
  }
  const v=rr.value();check(missing===5?v===null:v.revision===1&&v.act===7,"PCM revision");pcmCases.push({phase,missing,value:v});
 }
 check(peak<=4096,"digital peak");
 return {schema:"mhac-response-revisions-v1",parent:"b18e9fa1a5d5d2405245e3999125d12c5ac37c7c",pins,assertions,counts,outcomes,cases,pcmCases,pcmBodies,specimens,peak,bodyMs:640,revisionLimit:2,witnesses:{rollback:rollback.snapshot(),lost:lost.snapshot(),forged:forged.snapshot(),conflict:r.snapshot()}};
}
const summary=q=>({assertions:q.assertions,counts:q.counts,outcomes:q.outcomes,matchedSchedules:q.cases.length,pcmBodies:q.pcmBodies,pcmCases:q.pcmCases,specimens:q.specimens.length,peak:q.peak,witnesses:q.witnesses});
module.exports={encode,parse,receiver,qualify,summary};
if(require.main===module){
 const fs=require("node:fs"),path=require("node:path"),crypto=require("node:crypto");
 for(const [n,expected] of Object.entries(pins)){const b=fs.readFileSync(path.join(__dirname,n));if(crypto.createHash("sha1").update("blob "+b.length+"\0").update(b).digest("hex")!==expected)throw Error("dependency changed: "+n);}
 const q=qualify(),out=process.argv[2]||"output-revisions";fs.mkdirSync(out,{recursive:true});
 const manifest=q.specimens.map(s=>{const w=R.wav(I.render(s.tokens,s.phase));fs.writeFileSync(path.join(out,s.name),w);return {...s,sha256:crypto.createHash("sha256").update(w).digest("hex")};});
 fs.writeFileSync(path.join(out,"qualification.json"),JSON.stringify(q,null,2));fs.writeFileSync(path.join(out,"stimuli.json"),JSON.stringify(manifest,null,2));
 fs.writeFileSync(path.join(out,"index.html"),'<!doctype html><meta charset="utf-8"><title>Acoustic response revisions</title><h1>Acoustic response revisions</h1><p>Synthetic aligned frames; start at low volume, no autoplay. Revision indicates order, not finality or truth.</p><pre>'+JSON.stringify(summary(q),null,2)+'</pre>'+manifest.map(s=>'<h2>'+s.name+'</h2><audio controls preload="none" src="'+s.name+'"></audio>').join(""));
 console.log(JSON.stringify(summary(q),null,2));
}
