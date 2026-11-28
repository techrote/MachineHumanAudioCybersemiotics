"use strict";
// #452 Grammars lane / Draft HOLD. Synthetic, aligned PCM; no human or authentication claims.
// Parent be40e7795877599a02a151359f07adfa34036514; main 495a98ca12bae467a507031f04931aa4254b1866.
// Interaction #457 at 809489feb21ba23662fe5bd2b113cb3d2752e15a motivates typed negative responses;
// its independent stand-in is not wire-compatible. One GPT-6.2 agent; no subagents.
const pins={"epoch-fence.cjs":"311aa5e8d621238eec47d238861e8bec1bb02a94","transaction-leases.cjs":"cb2b2922bd4649dc9a1200bbffd2c11a501b8c7d","transaction-clarification.cjs":"37bd277c96b08bff10465b17de246bb570c68d09","systematic-mds.cjs":"3e74ca6f76b0e9fdb267c5b4e5734828ca27ddf3","clarification-controls.cjs":"9434b7134f23c54e3870f78efcc84fa145a70d2d","sequential-clarification.cjs":"5a83020a1548ed2af7f15aa248e834105d449afd","algebraic-binding.cjs":"7415235429fd86aa96bde3f69bcfe10cf5eb8fa2","integrity.cjs":"a58403f51806c17d89c7ebaf098d2e19b0995a02","recursive.cjs":"7d9e305857b59e029913432bb40f713ab84b5a90","injective-tags.cjs":"d91e0ed1e8700ff78b12e7732c07ddfcfc189e08","block-binding.cjs":"4c8be6987b345a5084dee16cf9e7053726c034c9","clock-hypotheses.cjs":"45a5fafb6506ba9211970c1cd58ac2840fbfc670","clock.cjs":"49a6849ae8a0094d30d499718ce21dd3029c0f8a","distributed.cjs":"c727fe13c7131e9a5eac9240fa909c34bcc5011c","acquisition.cjs":"70fb9823d596300112282a73386d6c6088b5d793","local-clock.cjs":"18e86536a85a7327499be1d5ff5719518d1a696a"};
const M=require("./systematic-mds.cjs"), E=require("./epoch-fence.cjs"),
 T=require("./transaction-clarification.cjs"), C=require("./clarification-controls.cjs"),
 A=require("./algebraic-binding.cjs"), I=require("./integrity.cjs"), R=require("./recursive.cjs");
const kinds=["unavailable-now","obsolete-epoch","refuse-certification"];
const valid=(x,n)=>Number.isInteger(x)&&x>=0&&x<n;
const eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const key=x=>x.reduce((s,v)=>17*s+v,0);
// 12 epochs x 16 addresses x 3 typed negative acts = 576 of 578 rows.
// First symbol 14 was introduced as an atom, but never followed by 15 or 16
// in the pinned semantic catalogue. Namespace compatibility is checked, not assumed.
const row=k=>[14,15+Math.floor(k/289),Math.floor(k/17)%17,k%17];
const codec=M.build(Array.from({length:576},(_,k)=>row(k)));
function encode(t){
 const kind=kinds.indexOf(t.kind);
 if(!valid(kind,3)||!valid(t.epoch,12)||!valid(t.side,2)||!valid(t.slot,8))throw Error("negative control");
 return M.encode(row((t.epoch*16+t.side*8+t.slot)*3+kind));
}
function parse(body){
 const k=M.decode(body,codec);if(k===null)return null;
 const [,b,c,d]=codec.map.get(k),n=(b-15)*289+c*17+d,addr=Math.floor(n/3)%16;
 return {kind:kinds[n%3],epoch:Math.floor(n/48),side:Math.floor(addr/8),slot:addr%8};
}
// A negative is neither a value nor a proof of permanent absence. "obsolete"
// is the respondent's assertion about the request epoch, not a retirement ACK.
// The caller must supply its current outstanding request and whether it is live.
// State/retirement/timeout policies belong to Interaction.
function classify(request,body,live=true){
 const q=E.parse(request);
 if(!q||q.type!=="request"||!live)return {status:"no-live-request"};
 const n=parse(body),p=E.parse(body),v=n||p;
 if(!v)return {status:"no-decoded-response"};
 if(v.epoch!==q.epoch||v.side!==q.side||v.slot!==q.slot)return {status:"mismatch"};
 if(n)return {status:"negative",kind:n.kind};
 if(p.type==="reply")return {status:"value",value:p.value};
 return {status:"not-a-reply"};
}
function qualify(){
 let assertions=0;const check=(v,msg)=>{assertions++;if(!v)throw Error(msg);};
 const masks=Array.from({length:256},(_,m)=>Array.from({length:8},(_,i)=>i).filter(i=>m&(1<<i))).filter(m=>m.length<=4);
 const erase=(x,m)=>x.map((v,i)=>m.includes(i)?null:v);
 let clean=0,erasures=0,wrongAddress=0,expired=0,legacyRefusal=0;
 const semantic=M.build(A.versions.append),seen=new Set(),negatives=[];
 const request=(epoch,side,slot)=>E.encode({type:"request",epoch,side,slot,value:null});
 const requests=[];
 for(let e=0;e<12;e++)for(let s=0;s<2;s++)for(let j=0;j<8;j++)requests.push(request(e,s,j));
 for(let n=0;n<576;n++){
  const x=M.encode(row(n)),t=parse(x);negatives.push(x);
  check(!!t&&eq(encode(t),x),"negative roundtrip");clean++;seen.add(key(row(n)));
  check(M.decode(x,semantic)===null&&E.parse(x)===null&&T.parse(x)===null&&C.parseControl(x)===null,"old parser separation");
  for(const m of masks)if(m.length){check(eq(parse(erase(x,m)),t),"erasure");erasures++;}
  for(let i=0;i<requests.length;i++){
   const got=classify(requests[i],x);
   if(i===Math.floor(n/3))check(eq(got,{status:"negative",kind:t.kind}),"typed matching");
   else {check(got.status==="mismatch","negative must not cross address/epoch");wrongAddress++;}
  }
  check(classify(requests[Math.floor(n/3)],x,false).status==="no-live-request","retired request");expired++;
 }
 check(seen.size===576,"unique");
 // Exhaustive reverse namespace refusal at clean full body.
 for(const x of semantic.book){check(parse(x)===null,"semantic excluded");legacyRefusal++;}
 for(let e=0;e<12;e++)for(let s=0;s<2;s++){
  for(const type of ["retire","retired"]){check(parse(E.encode({type,epoch:e,side:s}))===null,"retire excluded");legacyRefusal++;}
  for(let j=0;j<8;j++){
   check(parse(request(e,s,j))===null,"request excluded");legacyRefusal++;
   for(let v=0;v<17;v++){const x=E.encode({type:"reply",epoch:e,side:s,slot:j,value:v});
    check(parse(x)===null,"reply excluded");legacyRefusal++;
    check(eq(classify(request(e,s,j),x),{status:"value",value:v}),"positive unchanged");
   }
  }
 }
 for(let s=0;s<2;s++)for(let j=0;j<8;j++){
  check(parse(C.encodeRequest(s,j))===null,"legacy request excluded");legacyRefusal++;
  for(let v=0;v<17;v++){check(parse(C.encodeReply(s,j,v))===null,"legacy reply excluded");legacyRefusal++;}
  for(let tag=0;tag<17;tag++){
   check(parse(T.encode("request",s,j,tag))===null,"tagged request excluded");legacyRefusal++;
   for(let v=0;v<17;v++){check(parse(T.encode("reply",s,j,tag,v))===null,"tagged reply excluded");legacyRefusal++;}
  }
 }
 // Two unused rows must not be interpreted as negatives.
 for(let n=576;n<578;n++)check(parse(M.encode(row(n)))===null,"reserved row");
 // Exhaustive single-symbol substitution on all negatives, strict parser.
 let substitutions=0;
 for(const x of negatives)for(let i=0;i<8;i++)for(let v=0;v<17;v++)if(v!==x[i]){
  const y=x.slice();y[i]=v;check(parse(y)===null,"single substitution");substitutions++;
 }
 // Equal-duration comparison: collapse every negative to one generic negative;
 // silence emits no body. Compare intended act recoverability, not human interpretation.
 // Clean and four-erasure conditions preserve the code. Five erasures refuse it.
 const cases=[],specimens=[];let peak=0,pcmBodies=0;
 function pcm(tokens,phase,name){
  const p=I.render(tokens,phase),got=I.receive(p),w=R.wav(p),h=new DataView(w.buffer,w.byteOffset,w.byteLength);
  check(eq(got,tokens),"aligned PCM");check(h.getUint32(24,true)===16000&&h.getUint32(40,true)===2*p.length,"WAV header");
  for(const v of p)peak=Math.max(peak,Math.abs(v));pcmBodies++;
  if(phase===.137)specimens.push({name:name+".wav",tokens,phase});
  return got;
 }
 for(const phase of [.137,2.419,5.827])for(const kind of kinds)for(const policy of ["silence","generic","typed"])for(const missing of [0,4,5]){
  const q=request(3,1,5),t={kind,epoch:3,side:1,slot:5};
  const wire=policy==="silence"?Array(8).fill(null):erase(encode({...t,kind:policy==="generic"?kinds[0]:kind}),Array.from({length:missing},(_,i)=>i));
  const got=classify(q,pcm(wire,phase,kind+"-"+policy+"-"+missing));
  const exact=got.status==="negative"&&got.kind===kind;
  check(got.status===(policy==="silence"||missing===5?"no-decoded-response":"negative"),"policy outcome");
  cases.push({phase,kind,policy,missing,got,exact,bodies:policy==="silence"?0:1});
 }
 // Replay/rollback controls; same message is valid again if local request identity is reused.
 const witnesses=[];
 for(const phase of [.137,2.419,5.827])for(const kind of kinds){
  const old=request(0,0,2),now=request(1,0,2),wire=pcm(encode({kind,epoch:0,side:0,slot:2}),phase,"replay-"+kind);
  const fresh=classify(now,wire),rollback=classify(old,wire);
  check(fresh.status==="mismatch"&&rollback.status==="negative","rollback witness");
  const fake=pcm(encode({kind,epoch:1,side:0,slot:2}),phase,"forged-"+kind);
  check(classify(now,fake).status==="negative","no authentication");
  witnesses.push({phase,kind,fresh,rollback,forged:classify(now,fake)});
 }
 // A matched negative must never become positive certification; a later positive
 // on the same identifier is still structurally admissible if caller keeps it live.
 const q=request(4,0,0),negative=encode({kind:kinds[0],epoch:4,side:0,slot:0});
 const positive=E.encode({type:"reply",epoch:4,side:0,slot:0,value:0});
 check(classify(q,negative).status==="negative","zero not absence");
 check(eq(classify(q,positive),{status:"value",value:0}),"zero is a value");
 check(classify(q,positive,false).status==="no-live-request","caller closed");
 check(peak<=4096,"peak");
 return {schema:"mhac-typed-negative-v1",parent:"be40e7795877599a02a151359f07adfa34036514",pins,assertions,clean,erasures,substitutions,wrongAddress,expired,legacyRefusal,cases,witnesses,specimens,peak,pcmBodies,bodyMs:640};
}
function summary(q){
 return {assertions:q.assertions,clean:q.clean,erasures:q.erasures,substitutions:q.substitutions,wrongAddress:q.wrongAddress,expired:q.expired,legacyRefusal:q.legacyRefusal,peak:q.peak,pcmBodies:q.pcmBodies,specimens:q.specimens.length,comparison:["silence","generic","typed"].map(policy=>({policy,byErasure:[0,4,5].map(missing=>{const c=q.cases.filter(x=>x.policy===policy&&x.missing===missing);return {missing,n:c.length,exact:c.filter(x=>x.exact).length,negative:c.filter(x=>x.got.status==="negative").length,bodies:c.reduce((s,x)=>s+x.bodies,0)};})})),witnesses:q.witnesses.length};
}
module.exports={encode,parse,classify,qualify,summary,kinds};
if(require.main===module){
 const fs=require("node:fs"),path=require("node:path"),crypto=require("node:crypto");
 for(const [n,expected] of Object.entries(pins)){
  const b=fs.readFileSync(path.join(__dirname,n));
  if(crypto.createHash("sha1").update("blob "+b.length+"\0").update(b).digest("hex")!==expected)throw Error("dependency changed: "+n);
 }
 const q=qualify(),out=process.argv[2]||"output-negative";
 fs.mkdirSync(out,{recursive:true});
 const manifest=q.specimens.map(s=>{const b=R.wav(I.render(s.tokens,s.phase));fs.writeFileSync(path.join(out,s.name),b);return {...s,sha256:crypto.createHash("sha256").update(b).digest("hex")};});
 fs.writeFileSync(path.join(out,"qualification.json"),JSON.stringify(q,null,2));
 fs.writeFileSync(path.join(out,"stimuli.json"),JSON.stringify(manifest,null,2));
 fs.writeFileSync(path.join(out,"index.html"),'<!doctype html><meta charset="utf-8"><title>Typed negative controls</title><h1>Typed negative controls</h1><p>Synthetic aligned PCM; no autoplay. Start at low volume. A negative is not a proof of permanent absence or sender identity. Generic codes collapse all negative intents to one convention.</p><pre>'+JSON.stringify(summary(q),null,2)+'</pre>'+manifest.map(s=>'<h2>'+s.name+'</h2><audio controls preload="none" src="'+s.name+'"></audio>').join(""));
 console.log(JSON.stringify(summary(q),null,2));
}

/* Executed twice in V8 using exact connector-fetched dependency blobs; identical complete receipts.
No native CLI/filesystem/hash export, browser, physical audition, streaming or independent review.
Generic negative is a collapsed alphabet baseline at identical body duration; silence uses no body.
No matched-energy or human inference. Same-identity replay and forged matching negatives remain valid.
No claim of permanence, retirement, authentication, or protection against requester rollback.
{
  "assertions": 294716,
  "clean": 576,
  "erasures": 93312,
  "substitutions": 73728,
  "wrongAddress": 110016,
  "expired": 576,
  "legacyRefusal": 11788,
  "peak": 4096,
  "pcmBodies": 99,
  "specimens": 33,
  "comparison": [
    {
      "policy": "silence",
      "byErasure": [
        {
          "missing": 0,
          "n": 9,
          "exact": 0,
          "negative": 0,
          "bodies": 0
        },
        {
          "missing": 4,
          "n": 9,
          "exact": 0,
          "negative": 0,
          "bodies": 0
        },
        {
          "missing": 5,
          "n": 9,
          "exact": 0,
          "negative": 0,
          "bodies": 0
        }
      ]
    },
    {
      "policy": "generic",
      "byErasure": [
        {
          "missing": 0,
          "n": 9,
          "exact": 3,
          "negative": 9,
          "bodies": 9
        },
        {
          "missing": 4,
          "n": 9,
          "exact": 3,
          "negative": 9,
          "bodies": 9
        },
        {
          "missing": 5,
          "n": 9,
          "exact": 0,
          "negative": 0,
          "bodies": 9
        }
      ]
    },
    {
      "policy": "typed",
      "byErasure": [
        {
          "missing": 0,
          "n": 9,
          "exact": 9,
          "negative": 9,
          "bodies": 9
        },
        {
          "missing": 4,
          "n": 9,
          "exact": 9,
          "negative": 9,
          "bodies": 9
        },
        {
          "missing": 5,
          "n": 9,
          "exact": 0,
          "negative": 0,
          "bodies": 9
        }
      ]
    }
  ],
  "witnesses": 9
}
*/
