"use strict";
// #452 Grammars / Run 016. Synthetic bounded reply lifetime; not authentication.
// One GPT-6.2 agent, no subagents. Main 495a98ca12bae467a507031f04931aa4254b1866.
// Parent a0e65f96676cb8bd02e9fddf09e8a625a1a10ccf. Pinned dependency blob IDs verified at export.
const pins={"transaction-clarification.cjs":"37bd277c96b08bff10465b17de246bb570c68d09","systematic-mds.cjs":"3e74ca6f76b0e9fdb267c5b4e5734828ca27ddf3","clarification-controls.cjs":"9434b7134f23c54e3870f78efcc84fa145a70d2d","sequential-clarification.cjs":"5a83020a1548ed2af7f15aa248e834105d449afd","algebraic-binding.cjs":"7415235429fd86aa96bde3f69bcfe10cf5eb8fa2","integrity.cjs":"a58403f51806c17d89c7ebaf098d2e19b0995a02","recursive.cjs":"7d9e305857b59e029913432bb40f713ab84b5a90","injective-tags.cjs":"d91e0ed1e8700ff78b12e7732c07ddfcfc189e08","block-binding.cjs":"4c8be6987b345a5084dee16cf9e7053726c034c9","clock-hypotheses.cjs":"45a5fafb6506ba9211970c1cd58ac2840fbfc670","clock.cjs":"49a6849ae8a0094d30d499718ce21dd3029c0f8a","distributed.cjs":"c727fe13c7131e9a5eac9240fa909c34bcc5011c","acquisition.cjs":"70fb9823d596300112282a73386d6c6088b5d793","local-clock.cjs":"18e86536a85a7327499be1d5ff5719518d1a696a"};
const T=require("./transaction-clarification.cjs"), S=require("./sequential-clarification.cjs"),
 C=require("./clarification-controls.cjs"), M=require("./systematic-mds.cjs"),
 A=require("./algebraic-binding.cjs"), I=require("./integrity.cjs"), R=require("./recursive.cjs");
const N=17, STEP=1280, eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const integer=x=>Number.isSafeInteger(x)&&x>=0;
function validAddress(q){return q&&Number.isInteger(q.side)&&q.side>=0&&q.side<2&&Number.isInteger(q.slot)&&q.slot>=0&&q.slot<8;}
function leases(scope,lifetime,snapshot){
 if(!["global","address"].includes(scope)||!integer(lifetime))throw Error("configuration");
 const size=scope==="global"?N:16*N;
 let last=0, until=Array(size).fill(-1);
 if(snapshot!==undefined){
  if(!snapshot||snapshot.version!==1||snapshot.scope!==scope||snapshot.lifetime!==lifetime||!integer(snapshot.last)||!Array.isArray(snapshot.until)||snapshot.until.length!==size||!snapshot.until.every(v=>v===-1||integer(v)&&v<=snapshot.last+lifetime)||!Number.isSafeInteger(snapshot.last+lifetime))throw Error("invalid snapshot");
  last=snapshot.last;until=snapshot.until.slice();
 }
 return {
  reserve(q,now){
   if(!validAddress(q)||!integer(now)||now<last||!Number.isSafeInteger(now+lifetime))throw Error("clock/address");
   last=now;
   const offset=scope==="address"?(8*q.side+q.slot)*N:0;
   for(let tag=0;tag<N;tag++)if(now>until[offset+tag]){until[offset+tag]=now+lifetime;return tag;}
   return null;
  },
  snapshot(){return {version:1,scope,lifetime,last,until:until.slice()};}
 };
}
// Timestamp is request issue time, not reply time. The assumed lifetime bounds the
// last possible evidence RELEASE of any reply derived from that request (including delay).
// Before sending a request, caller must durably save the reservation; no rollback/clock reset.
function session(observation,codec,cap,allocate,transport){
 const transactions=[];
 const result=S.session(observation,codec,cap,(_old,q)=>{
  const tag=allocate(q);
  if(tag===null)return Array(8).fill(null);
  const request=T.encode("request",q.side,q.slot,tag),response=transport(request,q);
  const t=T.parse(response),bound=!!t&&t.type==="reply"&&t.side===q.side&&t.slot===q.slot&&t.tag===tag;
  transactions.push({q:{...q,tag},request,response,parsed:t,bound});
  return bound?C.encodeReply(t.side,t.slot,t.value):Array(8).fill(null);
 });
 return {...result,transactions};
}
function workload(kind,i){
 const address=kind==="hotspot"?0:kind==="alternating"?i%2:kind==="round-robin"?i%16:(i%5===0?1+i%15:0);
 return {side:Math.floor(address/8),slot:address%8};
}
function simulate(kind,bound,actual,policy,count=96){
 let store=policy.endsWith("lease")?leases(policy==="address-lease"?"address":"global",bound):null;
 let counter=0;const prior=[],trace=[];let accepted=0,refused=0,exposed=0,aliases=0,restores=0;
 for(let i=0;i<count;i++){
  const now=i*STEP,q=workload(kind,i);
  // Simulate orderly restart at fixed points, round-trip persistent state; not disk durability.
  if(store&&i>0&&i%11===0){store=leases(policy==="address-lease"?"address":"global",bound,JSON.parse(JSON.stringify(store.snapshot())));restores++;}
  const tag=store?store.reserve(q,now):policy==="nonreuse"&&counter>=N?null:counter++%N;
  if(tag===null){refused++;trace.push({i,now,q,tag});continue;}
  accepted++;
  const same=prior.filter(x=>x.tag===tag&&x.q.side===q.side&&x.q.slot===q.slot);
  if(same.length)aliases++;
  const stale=same.filter(x=>now-x.now<=actual);
  if(stale.length)exposed++;
  trace.push({i,now,q,tag,eligibleStaleRequests:stale.map(x=>x.i)});
  prior.push({i,now,q,tag});
 }
 return {kind,bound,actual,policy,accepted,refused,aliases,exposed,restores,trace};
}
function qualify(){
 let assertions=0;const check=(x,m)=>{assertions++;if(!x)throw Error(m);};
 const policies=["cyclic","nonreuse","global-lease","address-lease"],rows=[];
 for(const kind of ["hotspot","alternating","round-robin","skewed"])
 for(const slots of [4,16,17,32,64])
 for(const extra of [0,1,16])
 for(const policy of policies){
  const x=simulate(kind,slots*STEP,(slots+extra)*STEP,policy);
  check(x.accepted+x.refused===96,"conservation");
  if(extra===0&&policy.endsWith("lease"))check(x.exposed===0,"bounded stale exposure");
  if(policy==="nonreuse")check(x.exposed===0&&x.accepted===17,"nonreuse");
  rows.push(x);
 }
 // Exhaustive small history boundary checks: same address+tag is the matching key.
 for(const scope of ["global","address"])for(let life=0;life<=34;life++){
  const q={side:0,slot:0},s=leases(scope,life*STEP),history=[];
  for(let i=0;i<80;i++){const now=i*STEP,tag=s.reserve(q,now);
   if(tag!==null){check(!history.some(x=>x.tag===tag&&now-x.now<=life*STEP),"inclusive boundary");history.push({now,tag});}
  }
 }
 const q={side:0,slot:0},a=leases("address",STEP*32);
 for(let i=0;i<17;i++)check(a.reserve(q,0)===i,"fill");
 check(a.reserve(q,32*STEP)===null,"inclusive expiry");
 check(a.reserve({side:1,slot:0},32*STEP)===0,"independent address");
 const restored=leases("address",STEP*32,JSON.parse(JSON.stringify(a.snapshot())));
 check(restored.reserve(q,32*STEP)===null,"restart at expiry");
 check(restored.reserve(q,32*STEP+1)===0,"first legal reuse");
 let invalid=0;for(const f of [()=>restored.reserve(q,0),()=>leases("address",1,{version:1}),()=>leases("global",STEP*32,a.snapshot())]){try{f();}catch{invalid++;}}
 check(invalid===3,"invalid/rollback refusal");
 // Exact inherited mixed-source witness, with real aligned PCM request/reply demodulation.
 const codec=M.build(A.versions.original),book=codec.book,mask=[1,2,4,5],target=512;
 const genuine=book[target].map((v,j)=>mask.includes(j)?null:v);
 const splice=[...book[62].slice(0,4),...book[214].slice(4)].map((v,j)=>mask.includes(j)?null:v);
 const scenarios=[],specimens=[];let peak=0,pcmBodies=0;
 for(const phase of [.137,2.419,5.827]){
  const life=32*STEP;
  function pcm(tokens,name){const x=I.render(tokens,phase),decoded=I.receive(x),w=R.wav(x);
   check(eq(decoded,tokens),"PCM");const h=new DataView(w.buffer,w.byteOffset,w.byteLength);check(h.getUint32(24,true)===16000&&h.getUint32(40,true)===x.length*2,"WAV");
   for(const v of x)peak=Math.max(peak,Math.abs(v));pcmBodies++;
   if(phase===.137)specimens.push({name:name+".wav",tokens,phase});
   return decoded;
  }
  for(const mode of ["persistent-inbound","expired-replay","lost-state","honest-current"]){
   let s=leases("address",life),i=0;const old=[];
   const prior=session(pcm(genuine,mode+"-old-body"),codec,4,q=>s.reserve(q,i*STEP),request=>{
    const q=T.parse(pcm(request,mode+"-old-request-"+i));
    const reply=pcm(T.encode("reply",q.side,q.slot,q.tag,book[target][q.slot]),mode+"-old-reply-"+i);
    old.push(reply);i++;return reply;
   });
   check(prior.status==="certified"&&i===4,"prior");
   const snap=JSON.parse(JSON.stringify(s.snapshot()));
   s=mode==="lost-state"?leases("address",life):leases("address",life,snap);
   i=0;const start=mode==="expired-replay"?life+4*STEP:4*STEP;
   const current=session(pcm(splice,mode+"-new-body"),codec,4,q=>s.reserve(q,start+i*STEP),request=>{
    const q=T.parse(pcm(request,mode+"-new-request-"+i));
    const reply=mode==="honest-current"?T.encode("reply",q.side,q.slot,q.tag,book[q.side===0?62:214][q.slot]):old[i];
    return pcm(reply,mode+"-new-reply-"+i++);
   });
   check(current.candidate===target,"candidate");
   check(current.status===(mode==="expired-replay"||mode==="lost-state"?"certified":"refused"),"replay outcome");
   scenarios.push({mode,phase,start,lifetime:life,status:current.status,transactions:current.transactions});
  }
 }
 check(peak<=4096,"peak");
 return {schema:"mhac-grammar-lease-v1",parent:"a0e65f96676cb8bd02e9fddf09e8a625a1a10ccf",pins,stepMs:STEP,assertions,rows,scenarios,specimens,pcmBodies,peak};
}
function summary(q){return {assertions:q.assertions,rows:q.rows.length,pcmBodies:q.pcmBodies,peak:q.peak,specimens:q.specimens.length,
 bounded:q.rows.filter(x=>x.bound===x.actual&&x.policy.endsWith("lease")).reduce((a,x)=>a+x.exposed,0),
 table:q.rows.filter(x=>x.bound===32*STEP&&x.actual===x.bound).map(({kind,policy,accepted,exposed})=>({kind,policy,accepted,exposed})),
 violation:q.rows.filter(x=>x.kind==="hotspot"&&x.bound===16*STEP).map(({policy,actual,accepted,exposed})=>({policy,actual,accepted,exposed})),
 witness:q.scenarios.filter(x=>x.phase===.137).map(x=>({mode:x.mode,status:x.status,labels:x.transactions.map(t=>[t.q.tag,t.parsed?.tag])}))};}
module.exports={leases,session,simulate,qualify,summary};
if(require.main===module){
 const fs=require("node:fs"),path=require("node:path"),crypto=require("node:crypto");
 for(const [n,expected] of Object.entries(pins)){const b=fs.readFileSync(path.join(__dirname,n));if(crypto.createHash("sha1").update("blob "+b.length+"\0").update(b).digest("hex")!==expected)throw Error("dependency changed: "+n);}
 const q=qualify(),out=process.argv[2]||"output-leases";fs.mkdirSync(out,{recursive:true});
 const manifest=q.specimens.map(s=>{const b=R.wav(I.render(s.tokens,s.phase));fs.writeFileSync(path.join(out,s.name),b);return {...s,sha256:crypto.createHash("sha256").update(b).digest("hex")};});
 fs.writeFileSync(path.join(out,"qualification.json"),JSON.stringify(q,null,2));
 fs.writeFileSync(path.join(out,"stimuli.json"),JSON.stringify(manifest,null,2));
 fs.writeFileSync(path.join(out,"index.html"),'<!doctype html><meta charset="utf-8"><title>Clarification leases</title><h1>Clarification leases</h1><p>Aligned synthetic PCM, no autoplay. Start at low volume. Leases assume a real bound on reply release; they are not authentication.</p><pre>'+JSON.stringify(summary(q),null,2)+'</pre>'+manifest.map(s=>'<h2>'+s.name+'</h2><audio controls preload="none" src="'+s.name+'"></audio>').join(""));
 console.log(JSON.stringify(summary(q),null,2));
}

/*
Executed V8 receipt (two identical full runs). Native Git DNS unavailable; native CLI export, browser, physical audition, streaming, independent review and whole-repo validation untested. Bounded lifetime is an assumption, not a measured channel property. Snapshot persistence is simulated, not crash-safe storage. No human claims. Results:
{
  "assertions": 5547,
  "rows": 240,
  "pcmBodies": 192,
  "peak": 4096,
  "specimens": 64,
  "bounded": 0,
  "table": [
    {
      "kind": "hotspot",
      "policy": "cyclic",
      "accepted": 96,
      "exposed": 79
    },
    {
      "kind": "hotspot",
      "policy": "nonreuse",
      "accepted": 17,
      "exposed": 0
    },
    {
      "kind": "hotspot",
      "policy": "global-lease",
      "accepted": 51,
      "exposed": 0
    },
    {
      "kind": "hotspot",
      "policy": "address-lease",
      "accepted": 51,
      "exposed": 0
    },
    {
      "kind": "alternating",
      "policy": "cyclic",
      "accepted": 96,
      "exposed": 0
    },
    {
      "kind": "alternating",
      "policy": "nonreuse",
      "accepted": 17,
      "exposed": 0
    },
    {
      "kind": "alternating",
      "policy": "global-lease",
      "accepted": 51,
      "exposed": 0
    },
    {
      "kind": "alternating",
      "policy": "address-lease",
      "accepted": 96,
      "exposed": 0
    },
    {
      "kind": "round-robin",
      "policy": "cyclic",
      "accepted": 96,
      "exposed": 0
    },
    {
      "kind": "round-robin",
      "policy": "nonreuse",
      "accepted": 17,
      "exposed": 0
    },
    {
      "kind": "round-robin",
      "policy": "global-lease",
      "accepted": 51,
      "exposed": 0
    },
    {
      "kind": "round-robin",
      "policy": "address-lease",
      "accepted": 96,
      "exposed": 0
    },
    {
      "kind": "skewed",
      "policy": "cyclic",
      "accepted": 96,
      "exposed": 47
    },
    {
      "kind": "skewed",
      "policy": "nonreuse",
      "accepted": 17,
      "exposed": 0
    },
    {
      "kind": "skewed",
      "policy": "global-lease",
      "accepted": 51,
      "exposed": 0
    },
    {
      "kind": "skewed",
      "policy": "address-lease",
      "accepted": 71,
      "exposed": 0
    }
  ],
  "violation": [
    {
      "policy": "cyclic",
      "actual": 20480,
      "accepted": 96,
      "exposed": 0
    },
    {
      "policy": "nonreuse",
      "actual": 20480,
      "accepted": 17,
      "exposed": 0
    },
    {
      "policy": "global-lease",
      "actual": 20480,
      "accepted": 96,
      "exposed": 0
    },
    {
      "policy": "address-lease",
      "actual": 20480,
      "accepted": 96,
      "exposed": 0
    },
    {
      "policy": "cyclic",
      "actual": 21760,
      "accepted": 96,
      "exposed": 79
    },
    {
      "policy": "nonreuse",
      "actual": 21760,
      "accepted": 17,
      "exposed": 0
    },
    {
      "policy": "global-lease",
      "actual": 21760,
      "accepted": 96,
      "exposed": 79
    },
    {
      "policy": "address-lease",
      "actual": 21760,
      "accepted": 96,
      "exposed": 79
    },
    {
      "policy": "cyclic",
      "actual": 40960,
      "accepted": 96,
      "exposed": 79
    },
    {
      "policy": "nonreuse",
      "actual": 40960,
      "accepted": 17,
      "exposed": 0
    },
    {
      "policy": "global-lease",
      "actual": 40960,
      "accepted": 96,
      "exposed": 79
    },
    {
      "policy": "address-lease",
      "actual": 40960,
      "accepted": 96,
      "exposed": 79
    }
  ],
  "witness": [
    {
      "mode": "persistent-inbound",
      "status": "refused",
      "labels": [
        [
          1,
          0
        ]
      ]
    },
    {
      "mode": "expired-replay",
      "status": "certified",
      "labels": [
        [
          0,
          0
        ],
        [
          0,
          0
        ],
        [
          0,
          0
        ],
        [
          0,
          0
        ]
      ]
    },
    {
      "mode": "lost-state",
      "status": "certified",
      "labels": [
        [
          0,
          0
        ],
        [
          0,
          0
        ],
        [
          0,
          0
        ],
        [
          0,
          0
        ]
      ]
    },
    {
      "mode": "honest-current",
      "status": "refused",
      "labels": [
        [
          1,
          1
        ],
        [
          1,
          1
        ],
        [
          1,
          1
        ]
      ]
    }
  ]
}
*/
