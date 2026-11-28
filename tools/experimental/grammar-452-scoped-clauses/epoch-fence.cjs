"use strict";
// #452 Grammars lane. Synthetic aligned PCM; no human evidence or authentication.
// Parent e9f96d82bc0fdac196313411390c59d1645dec2b; accepted main 495a98ca12bae467a507031f04931aa4254b1866.
// One GPT-6.2 agent; no subagents. New namespace uses previously unused systematic rows.
const pins={"transaction-leases.cjs":"cb2b2922bd4649dc9a1200bbffd2c11a501b8c7d","transaction-clarification.cjs":"37bd277c96b08bff10465b17de246bb570c68d09","systematic-mds.cjs":"3e74ca6f76b0e9fdb267c5b4e5734828ca27ddf3","clarification-controls.cjs":"9434b7134f23c54e3870f78efcc84fa145a70d2d","sequential-clarification.cjs":"5a83020a1548ed2af7f15aa248e834105d449afd","algebraic-binding.cjs":"7415235429fd86aa96bde3f69bcfe10cf5eb8fa2","integrity.cjs":"a58403f51806c17d89c7ebaf098d2e19b0995a02","recursive.cjs":"7d9e305857b59e029913432bb40f713ab84b5a90","injective-tags.cjs":"d91e0ed1e8700ff78b12e7732c07ddfcfc189e08","block-binding.cjs":"4c8be6987b345a5084dee16cf9e7053726c034c9","clock-hypotheses.cjs":"45a5fafb6506ba9211970c1cd58ac2840fbfc670","clock.cjs":"49a6849ae8a0094d30d499718ce21dd3029c0f8a","distributed.cjs":"c727fe13c7131e9a5eac9240fa909c34bcc5011c","acquisition.cjs":"70fb9823d596300112282a73386d6c6088b5d793","local-clock.cjs":"18e86536a85a7327499be1d5ff5719518d1a696a"};

const M=require("./systematic-mds.cjs"),T=require("./transaction-clarification.cjs"),
 C=require("./clarification-controls.cjs"),S=require("./sequential-clarification.cjs"),
 A=require("./algebraic-binding.cjs"),I=require("./integrity.cjs"),R=require("./recursive.cjs");
const E=12, DATA=E*288, TOTAL=DATA+E*4;
const eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const valid=(x,n)=>Number.isInteger(x)&&x>=0&&x<n;
function row(k){return [16,4+Math.floor(k/289),Math.floor(k/17)%17,k%17];}
const codec=M.build(Array.from({length:TOTAL},(_,k)=>row(k)));
function encode(t){
 if(!valid(t.epoch,E)||!valid(t.side,2))throw Error("epoch/side");
 let k;
 if(t.type==="retire"||t.type==="retired")k=DATA+4*t.epoch+2*t.side+(t.type==="retired"?1:0);
 else{
  if(!valid(t.slot,8)||!(t.type==="request"?t.value===null:t.type==="reply"&&valid(t.value,17)))throw Error("control");
  k=t.epoch*288+(t.side*8+t.slot)*18+(t.type==="request"?0:t.value+1);
 }
 return M.encode(row(k));
}
function parse(body){
 const key=M.decode(body,codec);if(key===null)return null;
 const [,b,c,d]=codec.map.get(key),k=(b-4)*289+c*17+d;
 if(k>=DATA){const z=k-DATA;return {type:z%2?"retired":"retire",epoch:Math.floor(z/4),side:Math.floor(z/2)%2};}
 const act=k%18,address=Math.floor(k/18)%16;
 return {type:act?"reply":"request",epoch:Math.floor(k/288),side:Math.floor(address/8),slot:address%8,value:act?act-1:null};
}
// Snapshot is caller-owned. Persist reservation/transition before transmission.
// No rollback protection; epoch is not wrapped. Refuse malformed snapshots.
function requester(snapshot={epoch:0,used:0,retiring:false,acks:0}){
 let s={...snapshot};
 if(!valid(s.epoch,E+1)||!valid(s.used,65536)||typeof s.retiring!=="boolean"||!valid(s.acks,4)||
 (!s.retiring&&s.acks!==0)||(s.retiring&&s.epoch===E)||s.acks===3)throw Error("requester state");
 return {
  reserve(side,slot){if(!valid(side,2)||!valid(slot,8))throw Error("address");
   const bit=1<<(8*side+slot);if(s.epoch===E||s.retiring||(s.used&bit))return null;
   s.used|=bit;return encode({type:"request",epoch:s.epoch,side,slot,value:null});},
  retire(){if(s.epoch===E)return [];s.retiring=true;
   return [0,1].filter(side=>!(s.acks&(1<<side))).map(side=>encode({type:"retire",epoch:s.epoch,side}));},
  accept(body){const t=parse(body);if(!s.retiring||!t||t.type!=="retired"||t.epoch!==s.epoch)return false;
   s.acks|=1<<t.side;if(s.acks===3)s={epoch:s.epoch+1,used:0,retiring:false,acks:0};return true;},
  snapshot(){return {...s};}
 };
}
function responder(side,epoch=0){
 if(!valid(side,2)||!valid(epoch,E+1))throw Error("responder state");
 let current=epoch;
 return {
  receive(body,value){
   const t=parse(body);if(!t||t.side!==side)return null;
   if(t.type==="retire"){
    // Idempotent ACK for immediately previous epoch, never advance on an old/future command.
    if(t.epoch===current)current++;
    else if(t.epoch!==current-1)return null;
    return encode({type:"retired",epoch:t.epoch,side});
   }
   if(t.type!=="request"||t.epoch!==current||!valid(value,17))return null;
   return encode({...t,type:"reply",value});
  },epoch(){return current;}
 };
}
function match(request,reply){const a=parse(request),b=parse(reply);return !!a&&!!b&&a.type==="request"&&b.type==="reply"&&
 a.epoch===b.epoch&&a.side===b.side&&a.slot===b.slot;}
function qualify(){
 let assertions=0;const check=(v,m)=>{assertions++;if(!v)throw Error(m);};
 const masks=Array.from({length:256},(_,m)=>Array.from({length:8},(_,i)=>i).filter(i=>m&(1<<i))).filter(m=>m.length<=4);
 let bodies=0,erasures=0;const distinct=new Set();
 for(let k=0;k<TOTAL;k++){
  const x=M.encode(row(k)),t=parse(x);
  check(!!t&&eq(encode(t),x),"roundtrip");
  check(T.parse(x)===null&&C.parseControl(x)===null,"legacy separation");
  distinct.add(x.join(","));
  for(const mask of masks){if(!mask.length)continue;check(eq(parse(x.map((v,i)=>mask.includes(i)?null:v)),t),"erasure");erasures++;}
  bodies++;
 }
 check(distinct.size===TOTAL,"collision");
 for(const x of M.build(A.versions.append).book)check(parse(x)===null,"semantic separation");
 for(let e=0;e<E;e++)for(let side=0;side<2;side++)for(let slot=0;slot<8;slot++)for(let old=0;old<E;old++){
  const a=encode({type:"request",epoch:e,side,slot,value:null}),b=encode({type:"reply",epoch:old,side,slot,value:0});
  check(match(a,b)===(e===old),"epoch matching");
 }
 // All combinations of first-round request and ACK loss at the two respondents.
 // A second loss-free round retries only unacknowledged sides. No timeout forces advancement.
 const lossRuns=[];
 for(let loss=0;loss<16;loss++){
  let q=requester(),rs=[responder(0),responder(1)],sent=0,delivered=0,trace=[];
  const old=q.reserve(0,0);check(old!==null&&q.reserve(0,0)===null,"one use/address");
  const oldReply=rs[0].receive(old,7);
  for(let round=0;round<2;round++){
   const frames=q.retire();sent+=frames.length;
   check(q.reserve(1,0)===null||frames.length===0,"frozen while retiring");
   for(const x of frames){
    const side=parse(x).side;
    if(round===0&&(loss&(1<<side))){trace.push({round,side,event:"request lost"});continue;}
    const y=rs[side].receive(x,0);check(!!y,"idempotent retirement");sent++;
    if(round===0&&(loss&(4<<side))){trace.push({round,side,event:"ACK lost"});continue;}
    check(q.accept(y),"ACK");delivered++;trace.push({round,side,event:"ACK"});
   }
   q=requester(JSON.parse(JSON.stringify(q.snapshot())));
   rs=rs.map((r,i)=>responder(i,r.epoch()));
   if(q.snapshot().epoch===1)break;
  }
  check(q.snapshot().epoch===1&&rs.every(r=>r.epoch()===1),"converged");
  const next=q.reserve(0,0);check(next!==null&&!match(next,oldReply),"stale epoch");
  check(rs[0].receive(old,0)===null,"old request rejected");
  lossRuns.push({loss,sent,delivered,trace});
 }
 // Exhaustion: retire only after both ACK, even if every address consumed.
 const q=requester(),rs=[responder(0),responder(1)];
 let admitted=0,retirementBodies=0;
 for(let e=0;e<E;e++){
  for(let side=0;side<2;side++)for(let slot=0;slot<8;slot++){
   const x=q.reserve(side,slot);check(!!x&&parse(x).epoch===e,"admit");admitted++;
   check(q.reserve(side,slot)===null,"duplicate refusal");
  }
  for(const x of q.retire()){retirementBodies++;const y=rs[parse(x).side].receive(x,0);retirementBodies++;check(q.accept(y),"retirement");}
 }
 check(q.snapshot().epoch===E&&q.reserve(0,0)===null&&q.retire().length===0,"finite exhaustion");
 // Inherited genuine and splice bodies: preserve false certification if local state rolls back.
 const semantic=M.build(A.versions.original),book=semantic.book,mask=[1,2,4,5];
 const genuine=book[512].map((v,i)=>mask.includes(i)?null:v);
 const splice=[...book[62].slice(0,4),...book[214].slice(4)].map((v,i)=>mask.includes(i)?null:v);
 const witnesses=[],specimens=[];let pcmBodies=0,peak=0;
 for(const phase of [.137,2.419,5.827])for(const mode of ["new-epoch","rollback","truthful","genuine"]){
  let rq=requester(),responders=[responder(0),responder(1)],oldReplies=[],index=0;
  function pcm(tokens,label){const x=I.render(tokens,phase),y=I.receive(x),w=R.wav(x),h=new DataView(w.buffer,w.byteOffset,w.byteLength);
   check(eq(y,tokens),"aligned PCM");check(h.getUint32(24,true)===16000&&h.getUint32(40,true)===2*x.length,"WAV header");
   for(const v of x)peak=Math.max(peak,Math.abs(v));pcmBodies++;
   if(phase===.137)specimens.push({name:mode+"-"+label+".wav",tokens,phase});return y;
  }
  const snap=rq.snapshot();
  const prior=S.session(pcm(genuine,"old-body"),semantic,4,(_,query)=>{
   const x=pcm(rq.reserve(query.side,query.slot),"old-request-"+index);
   const y=pcm(responders[query.side].receive(x,book[512][query.slot]),"old-reply-"+index++);
   oldReplies.push(y);const t=parse(y);return C.encodeReply(t.side,t.slot,t.value);
  });
  check(prior.status==="certified"&&oldReplies.length===4,"prior");
  for(const x of rq.retire()){const a=pcm(x,"retire-"+parse(x).side);const b=pcm(responders[parse(a).side].receive(a,0),"retired-"+parse(a).side);check(rq.accept(b),"acoustic retirement");}
  if(mode==="rollback")rq=requester(snap);
  index=0;const transactions=[];
  const result=S.session(pcm(mode==="genuine"?genuine:splice,"current-body"),semantic,4,(_,query)=>{
   const req=rq.reserve(query.side,query.slot);check(!!req,"unique address");
   const x=pcm(req,"current-request-"+index);
   const v=book[mode==="truthful"?(query.side===0?62:214):512][query.slot];
   const raw=mode==="new-epoch"||mode==="rollback"?oldReplies[index]:responders[query.side].receive(x,v);
   const y=pcm(raw,"current-reply-"+index++),ok=match(x,y),t=parse(y);
   transactions.push({request:parse(x),reply:t,matched:ok});
   return ok?C.encodeReply(t.side,t.slot,t.value):Array(8).fill(null);
  });
  check(result.candidate===512&&result.status===(mode==="rollback"||mode==="genuine"?"certified":"refused"),"witness");
  witnesses.push({mode,phase,status:result.status,transactions});
 }
 check(peak<=4096,"digital peak");
 return {schema:"mhac-epoch-fence-v1",parent:"e9f96d82bc0fdac196313411390c59d1645dec2b",pins,assertions,bodies,erasures,lossRuns,admitted,retirementBodies,witnesses,specimens,pcmBodies,peak,bodyMs:640};
}
function summary(q){return {assertions:q.assertions,bodies:q.bodies,erasures:q.erasures,lossRuns:q.lossRuns.map(x=>({loss:x.loss,sent:x.sent})),admitted:q.admitted,retirementBodies:q.retirementBodies,pcmBodies:q.pcmBodies,specimens:q.specimens.length,peak:q.peak,witnesses:q.witnesses.filter(x=>x.phase===.137).map(x=>({mode:x.mode,status:x.status,transactions:x.transactions.length}))};}
module.exports={encode,parse,requester,responder,match,qualify,summary};
if(require.main===module){
 const fs=require("node:fs"),path=require("node:path"),crypto=require("node:crypto");
 for(const [n,expected] of Object.entries(pins)){const b=fs.readFileSync(path.join(__dirname,n));if(crypto.createHash("sha1").update("blob "+b.length+"\0").update(b).digest("hex")!==expected)throw Error("dependency changed: "+n);}
 const q=qualify(),out=process.argv[2]||"output-epoch";fs.mkdirSync(out,{recursive:true});
 const manifest=q.specimens.map(s=>{const b=R.wav(I.render(s.tokens,s.phase));fs.writeFileSync(path.join(out,s.name),b);return {...s,sha256:crypto.createHash("sha256").update(b).digest("hex")};});
 fs.writeFileSync(path.join(out,"qualification.json"),JSON.stringify(q,null,2));
 fs.writeFileSync(path.join(out,"stimuli.json"),JSON.stringify(manifest,null,2));
 fs.writeFileSync(path.join(out,"index.html"),'<!doctype html><meta charset="utf-8"><title>Epoch fence</title><h1>Epoch fence — synthetic aligned PCM</h1><p>No autoplay. Start at low volume. Retirement is not authentication or proof of durable persistence.</p><pre>'+JSON.stringify(summary(q),null,2)+'</pre>'+manifest.map(s=>'<h2>'+s.name+'</h2><audio controls preload="none" src="'+s.name+'"></audio>').join(""));
 console.log(JSON.stringify(summary(q),null,2));
}

/*
Synthetic V8 qualification repeated identically, exact parent dependency blobs fetched.
No native CLI/filesystem export, browser, streaming, physical audition or independent review here.
Epoch fence costs two retirement requests and two ACKs (2.56 s body airtime without loss),
versus zero separate retirement bodies for parent leases. Finite 192 address reservations
if each address used once in every epoch; not a replacement for the parent 272 address-label
combinations. No guaranteed convergence under permanent loss. Snapshot rollback can alias
an old epoch even after both responders advance. No authentication, no human claim.
{
  "assertions": 581202,
  "bodies": 3504,
  "erasures": 567648,
  "lossRuns": [
    {
      "loss": 0,
      "sent": 4
    },
    {
      "loss": 1,
      "sent": 5
    },
    {
      "loss": 2,
      "sent": 5
    },
    {
      "loss": 3,
      "sent": 6
    },
    {
      "loss": 4,
      "sent": 6
    },
    {
      "loss": 5,
      "sent": 5
    },
    {
      "loss": 6,
      "sent": 7
    },
    {
      "loss": 7,
      "sent": 6
    },
    {
      "loss": 8,
      "sent": 6
    },
    {
      "loss": 9,
      "sent": 7
    },
    {
      "loss": 10,
      "sent": 5
    },
    {
      "loss": 11,
      "sent": 6
    },
    {
      "loss": 12,
      "sent": 8
    },
    {
      "loss": 13,
      "sent": 7
    },
    {
      "loss": 14,
      "sent": 7
    },
    {
      "loss": 15,
      "sent": 6
    }
  ],
  "admitted": 192,
  "retirementBodies": 48,
  "pcmBodies": 240,
  "specimens": 80,
  "peak": 4096,
  "witnesses": [
    {
      "mode": "new-epoch",
      "status": "refused",
      "transactions": 1
    },
    {
      "mode": "rollback",
      "status": "certified",
      "transactions": 4
    },
    {
      "mode": "truthful",
      "status": "refused",
      "transactions": 3
    },
    {
      "mode": "genuine",
      "status": "certified",
      "transactions": 4
    }
  ]
}
*/
