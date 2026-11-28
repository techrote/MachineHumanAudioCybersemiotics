"use strict";
// Grammars / #452. Transaction labels, not authentication. Aligned synthetic bodies.
const M=require("./systematic-mds.cjs"), C=require("./clarification-controls.cjs"),
 S=require("./sequential-clarification.cjs"), A=require("./algebraic-binding.cjs"),
 I=require("./integrity.cjs"), R=require("./recursive.cjs");
const parent="09bba7545e3cfb5b469eca46b50ccb8e9da338f5", pinnedBlobs={"sequential-clarification.cjs":"5a83020a1548ed2af7f15aa248e834105d449afd","clarification-controls.cjs":"9434b7134f23c54e3870f78efcc84fa145a70d2d","systematic-mds.cjs":"3e74ca6f76b0e9fdb267c5b4e5734828ca27ddf3","algebraic-binding.cjs":"7415235429fd86aa96bde3f69bcfe10cf5eb8fa2","recursive.cjs":"7d9e305857b59e029913432bb40f713ab84b5a90","integrity.cjs":"a58403f51806c17d89c7ebaf098d2e19b0995a02","injective-tags.cjs":"d91e0ed1e8700ff78b12e7732c07ddfcfc189e08","block-binding.cjs":"4c8be6987b345a5084dee16cf9e7053726c034c9","clock-hypotheses.cjs":"45a5fafb6506ba9211970c1cd58ac2840fbfc670","clock.cjs":"49a6849ae8a0094d30d499718ce21dd3029c0f8a","distributed.cjs":"c727fe13c7131e9a5eac9240fa909c34bcc5011c","acquisition.cjs":"70fb9823d596300112282a73386d6c6088b5d793","local-clock.cjs":"18e86536a85a7327499be1d5ff5719518d1a696a"};
const key=x=>x.reduce((s,v)=>17*s+v,0), eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const valid=(x,n)=>Number.isInteger(x)&&x>=0&&x<n;
// 16 addresses x 18 speech acts (request or 17 values) x 17 labels.
// Reserve systematic first>=15 AND second>=2, disjoint from old controls and meanings.
function row(rank){return [15+Math.floor(rank/4335),2+Math.floor(rank/289)%15,Math.floor(rank/17)%17,rank%17];}
const codec=M.build(Array.from({length:4896},(_,i)=>row(i)));
function encode(type,side,slot,tag,value=null){
 if(!valid(side,2)||!valid(slot,8)||!valid(tag,17)||!(type==="request"?value===null:type==="reply"&&valid(value,17)))throw Error("invalid control");
 const rank=((side*8+slot)*18+(type==="request"?0:value+1))*17+tag;
 return M.encode(row(rank));
}
function parse(body){
 const k=M.decode(body,codec);if(k===null)return null;
 const [a,b,c,d]=codec.map.get(k),rank=(a-15)*4335+(b-2)*289+c*17+d;
 const address=Math.floor(rank/306),act=Math.floor(rank/17)%18;
 return {type:act===0?"request":"reply",side:Math.floor(address/8),slot:address%8,tag:d,value:act===0?null:act-1};
}
function matches(t,q,candidate){return !!t&&t.type==="reply"&&t.side===q.side&&t.slot===q.slot&&t.tag===q.tag&&t.value===candidate[q.slot];}
function allocator(start=0,wrap=false){
 if(!valid(start,17))throw Error("start");let count=0;
 return {next(){if(!wrap&&count>=17)return null;return (start+count++)%17;},used(){return count;}};
}
// Reuse previous candidate-selection logic; check new reply before adapting to old control.
// The transport gets a serialized acoustic request. It does not receive candidate truth.
function session(observation,semanticCodec,cap,labels,transport){
 const transactions=[];let exhausted=false;
 const result=S.session(observation,semanticCodec,cap,(_old,q)=>{
  const tag=labels.next();if(tag===null){exhausted=true;return nullBody();}
  const request=encode("request",q.side,q.slot,tag),response=transport(request);
  const t=parse(response),bound=!!t&&t.type==="reply"&&t.side===q.side&&t.slot===q.slot&&t.tag===tag;
  transactions.push({query:{...q,tag},request,response,parsed:t,bound});
  return bound?C.encodeReply(t.side,t.slot,t.value):nullBody();
 });
 return {...result,transactions,reason:exhausted?"label budget exhausted":result.reason};
}
const nullBody=()=>Array(8).fill(null);
function qualify(){
 let assertions=0;const check=(ok,msg)=>{assertions++;if(!ok)throw Error(msg);};
 const masks=Array.from({length:256},(_,i)=>Array.from({length:8},(_,j)=>j).filter(j=>i&(1<<j))).filter(m=>m.length<=4);
 const oldControls=[], counts={clean:0,erasure:0,legacyRefused:0,semanticRefused:0,wrongLabelRefused:0,matchingLabelAccepted:0};
 for(let side=0;side<2;side++)for(let slot=0;slot<8;slot++){
  oldControls.push(C.encodeRequest(side,slot));for(let v=0;v<17;v++)oldControls.push(C.encodeReply(side,slot,v));
  for(let tag=0;tag<17;tag++)for(let act=0;act<18;act++){
   const t={type:act===0?"request":"reply",side,slot,tag,value:act===0?null:act-1},body=encode(t.type,side,slot,tag,t.value);
   check(eq(parse(body),t),"clean");counts.clean++;
   check(C.parseControl(body)===null,"legacy namespace disjoint");
   for(const mask of masks){if(!mask.length)continue;
    check(eq(parse(body.map((v,j)=>mask.includes(j)?null:v)),t),"erasure");counts.erasure++;
   }
   if(act)for(let expected=0;expected<17;expected++){
    const accepted=matches(parse(body),{side,slot,tag:expected},Array(8).fill(act-1));
    check(accepted===(tag===expected),"label check");counts[accepted?"matchingLabelAccepted":"wrongLabelRefused"]++;
   }
  }
 }
 for(const x of oldControls){check(parse(x)===null,"legacy refused");counts.legacyRefused++;}
 const semantic=M.build(A.versions.append);
 for(const x of semantic.book){check(parse(x)===null,"semantic refused");counts.semanticRefused++;}
 const book=semantic.book,old=M.build(A.versions.original);
 check(eq(book.slice(0,old.book.length),old.book),"catalogue stable");
 const mask=[1,2,4,5], candidate=512;
 const spliced=[...book[62].slice(0,4),...book[214].slice(4)].map((v,j)=>mask.includes(j)?null:v);
 const genuine=book[candidate].map((v,j)=>mask.includes(j)?null:v);
 // Earlier genuine exchange, then the same query pattern in a mixed-source observation.
 const prior=S.session(genuine,old,4,(_,q)=>C.encodeReply(q.side,q.slot,book[candidate][q.slot]));
 check(prior.status==="certified","prior genuine");
 const replay=S.session(spliced,old,4,(_,q)=>C.encodeReply(q.side,q.slot,book[candidate][q.slot]));
 check(replay.status==="certified"&&replay.candidate===512,"unbound stale reply counterexample");
 const cases=[{name:"genuine",input:genuine,tag:4,kind:"truth"},{name:"honest-splice",input:spliced,tag:4,kind:"honest"},{name:"fresh-tag-stale",input:spliced,tag:4,kind:"stale"},{name:"reused-tag-stale",input:spliced,tag:0,kind:"stale"},{name:"missing",input:genuine,tag:4,kind:"missing"}];
 const traces=[],specimens=[];let peak=0,pcmBodies=0;
 for(const phase of [.137,2.419,5.827])for(const s of cases){
  let index=0;
  function pcm(tokens,label){const x=I.render(tokens,phase),w=R.wav(x),h=new DataView(w.buffer,w.byteOffset,w.byteLength);
   check(eq(I.receive(x),tokens),"PCM round trip");check(h.getUint32(24,true)===16000&&h.getUint32(40,true)===2*x.length,"WAV");
   for(const v of x)peak=Math.max(peak,Math.abs(v));pcmBodies++;
   if(phase===.137)specimens.push({name:s.name+"-"+label+".wav",tokens,phase});
   return I.receive(x);
  }
  const result=session(pcm(s.input,"body"),old,4,allocator(s.tag),request=>{
   const q=parse(pcm(request,"request-"+index));check(q?.type==="request","request decoded");
   if(s.kind==="missing")return nullBody();
   const tag=s.kind==="stale"?index:q.tag;
   const value=book[s.kind==="honest"?(q.side===0?62:214):candidate][q.slot];
   return pcm(encode("reply",q.side,q.slot,tag,value),"reply-"+index++);
  });
  check(result.candidate===512,"candidate");
  check(result.status===(["genuine","reused-tag-stale"].includes(s.name)?"certified":"refused"),"witness status");
  traces.push({scenario:s.name,phase,status:result.status,transactions:result.transactions,residual:result.residual});
 }
 const safe=allocator(0),wrap=allocator(0,true);const safeTags=Array.from({length:18},()=>safe.next()),wrapTags=Array.from({length:18},()=>wrap.next());
 check(safeTags[17]===null&&new Set(safeTags.slice(0,17)).size===17,"exhaustion");
 check(wrapTags[0]===wrapTags[17],"wrap alias");
 const exhausted=session(genuine,old,4,safe,()=>{throw Error("must not transmit");});
 check(exhausted.status==="refused"&&exhausted.reason==="label budget exhausted","exhaustion refusal");
 check(peak<=4096,"peak");
 return {schema:"mhac-transaction-clarification-v1",parent,pinnedBlobs,assertions,counts,bodyMs:640,exchangeMs:1280,legacyReplay:replay.status,trace:traces,specimens,peak,pcmBodies,safeTags,wrapTags};
}
module.exports={encode,parse,matches,allocator,session,qualify};
if(require.main===module){
 const fs=require("node:fs"),path=require("node:path"),crypto=require("node:crypto");
 for(const [n,expected] of Object.entries(pinnedBlobs)){const b=fs.readFileSync(path.join(__dirname,n));if(crypto.createHash("sha1").update("blob "+b.length+"\\0".replace("\\0","\0")).update(b).digest("hex")!==expected)throw Error("dependency changed: "+n);}
 const q=qualify(),out=process.argv[2]||"output-transaction";fs.mkdirSync(out,{recursive:true});
 const manifest=q.specimens.map(s=>{const b=R.wav(I.render(s.tokens,s.phase));fs.writeFileSync(path.join(out,s.name),b);return {...s,sha256:crypto.createHash("sha256").update(b).digest("hex")};});
 fs.writeFileSync(path.join(out,"qualification.json"),JSON.stringify(q,null,2));
 fs.writeFileSync(path.join(out,"stimuli.json"),JSON.stringify(manifest,null,2));
 fs.writeFileSync(path.join(out,"index.html"),'<!doctype html><meta charset="utf-8"><title>Transaction clarification</title><h1>Transaction clarification</h1><p>Synthetic aligned PCM. Start at low volume; no autoplay. Labels are not authentication.</p>'+manifest.map(s=>'<h2>'+s.name+'</h2><audio controls preload="none" src="'+s.name+'"></audio><pre>'+JSON.stringify(s.tokens)+'</pre>').join("")+'<h2>Traces</h2><pre>'+JSON.stringify(q.trace,null,2)+'</pre>');
 console.log(JSON.stringify({assertions:q.assertions,counts:q.counts,pcmBodies:q.pcmBodies,peak:q.peak},null,2));
}

/*
Run 015 / 2026-11-25 / Refs #452. Main 495a98ca12bae467a507031f04931aa4254b1866. One GPT-6.2 agent, no subagents. Actual pinned dependency files executed in V8 CommonJS compatibility adapter. Native git ls-remote failed DNS; native filesystem export, browser, physical audition, independent review untested. Synthetic, aligned body only; no authentication, no human evidence. Label nonreuse scoped to allocator lifetime; reset/wrap permits stale replies. No matched-energy claim, same body time and nominal tone bank. Results:
{
  "assertions": 885196,
  "counts": {
    "clean": 4896,
    "erasure": 793152,
    "legacyRefused": 288,
    "semanticRefused": 3100,
    "wrongLabelRefused": 73984,
    "matchingLabelAccepted": 4624
  },
  "pcmBodies": 90,
  "peak": 4096,
  "specimens": 30,
  "legacyReplay": "certified",
  "trace": [
    {
      "scenario": "genuine",
      "status": "certified",
      "transactions": [
        {
          "query": {
            "side": 0,
            "slot": 1,
            "tag": 4
          },
          "parsed": {
            "type": "reply",
            "side": 0,
            "slot": 1,
            "tag": 4,
            "value": 4
          },
          "bound": true
        },
        {
          "query": {
            "side": 1,
            "slot": 2,
            "tag": 5
          },
          "parsed": {
            "type": "reply",
            "side": 1,
            "slot": 2,
            "tag": 5,
            "value": 16
          },
          "bound": true
        },
        {
          "query": {
            "side": 0,
            "slot": 2,
            "tag": 6
          },
          "parsed": {
            "type": "reply",
            "side": 0,
            "slot": 2,
            "tag": 6,
            "value": 16
          },
          "bound": true
        },
        {
          "query": {
            "side": 1,
            "slot": 0,
            "tag": 7
          },
          "parsed": {
            "type": "reply",
            "side": 1,
            "slot": 0,
            "tag": 7,
            "value": 5
          },
          "bound": true
        }
      ]
    },
    {
      "scenario": "honest-splice",
      "status": "refused",
      "transactions": [
        {
          "query": {
            "side": 0,
            "slot": 1,
            "tag": 4
          },
          "parsed": {
            "type": "reply",
            "side": 0,
            "slot": 1,
            "tag": 4,
            "value": 4
          },
          "bound": true
        },
        {
          "query": {
            "side": 1,
            "slot": 2,
            "tag": 5
          },
          "parsed": {
            "type": "reply",
            "side": 1,
            "slot": 2,
            "tag": 5,
            "value": 16
          },
          "bound": true
        },
        {
          "query": {
            "side": 0,
            "slot": 2,
            "tag": 6
          },
          "parsed": {
            "type": "reply",
            "side": 0,
            "slot": 2,
            "tag": 6,
            "value": 6
          },
          "bound": true
        }
      ]
    },
    {
      "scenario": "fresh-tag-stale",
      "status": "refused",
      "transactions": [
        {
          "query": {
            "side": 0,
            "slot": 1,
            "tag": 4
          },
          "parsed": {
            "type": "reply",
            "side": 0,
            "slot": 1,
            "tag": 0,
            "value": 4
          },
          "bound": false
        }
      ]
    },
    {
      "scenario": "reused-tag-stale",
      "status": "certified",
      "transactions": [
        {
          "query": {
            "side": 0,
            "slot": 1,
            "tag": 0
          },
          "parsed": {
            "type": "reply",
            "side": 0,
            "slot": 1,
            "tag": 0,
            "value": 4
          },
          "bound": true
        },
        {
          "query": {
            "side": 1,
            "slot": 2,
            "tag": 1
          },
          "parsed": {
            "type": "reply",
            "side": 1,
            "slot": 2,
            "tag": 1,
            "value": 16
          },
          "bound": true
        },
        {
          "query": {
            "side": 0,
            "slot": 2,
            "tag": 2
          },
          "parsed": {
            "type": "reply",
            "side": 0,
            "slot": 2,
            "tag": 2,
            "value": 16
          },
          "bound": true
        },
        {
          "query": {
            "side": 1,
            "slot": 0,
            "tag": 3
          },
          "parsed": {
            "type": "reply",
            "side": 1,
            "slot": 0,
            "tag": 3,
            "value": 5
          },
          "bound": true
        }
      ]
    },
    {
      "scenario": "missing",
      "status": "refused",
      "transactions": [
        {
          "query": {
            "side": 0,
            "slot": 1,
            "tag": 4
          },
          "parsed": null,
          "bound": false
        }
      ]
    }
  ],
  "safeTags": [
    0,
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    9,
    10,
    11,
    12,
    13,
    14,
    15,
    16,
    null
  ],
  "wrapTags": [
    0,
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    9,
    10,
    11,
    12,
    13,
    14,
    15,
    16,
    0
  ]
}
*/
