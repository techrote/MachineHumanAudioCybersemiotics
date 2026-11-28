"use strict";
// Refs #452 / Draft PR #453. Grammars Run 004; synthetic only.
// Source: 6686c10ecba7885d06a8e2b9a2773e1286deddbb. Accepted main 495a98ca12bae467a507031f04931aa4254b1866.
// Fixed 40-ms two-part preamble, 640-ms existing GF(17) body. No human claim.
// Original PCM, no external dependencies. Scan over integer samples at 1-ms steps.
// Both modes same duration, amplitude, pulse count; occupied header frequencies differ.
// Noise uniform independent samples at nominal RMS 1700 PCM counts, paired seeds.
// Carrier and spoof are deliberately 2300+2300; this is a specific nuisance, not general superiority.
// No acquisition under sample-clock drift, real room acoustics, or streaming latency established.
// Header erasure causes loss of frame; neither CRC nor preamble authenticates a source.
// 12 seeds per mode/scenario, finite deterministic fixtures, no tuning/test statistical independence claim.
// A scan candidate within +/-5 ms of one truth is matched once; duplicates counted as false.
// Interrupted packet acquisition counted separately; any partial acceptance is a failure.
// A single GPT-6.2 agent; prior code read at exact refs; no other branches edited.
// Execute: node acquisition.cjs output-acquisition
const R=require("./recursive.cjs"),I=require("./integrity.cjs");
const Lab=(function lab(R,I){
 const RATE=16000,HALF=320,HEADER=640,BODY=10240,FRAME=HEADER+BODY,AMP=4096,STEP=16,TOL=80;
 const modes=["repeat","ordered"],families=["clean","noise","carrier","interrupted","header-erasure","noise-only","spoof"];
 const freq={repeat:[2300,2300],ordered:[2300,2700]};
 const eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
 const rng=seed=>()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;};
 const join=(...parts)=>{let a=new Int16Array(parts.reduce((s,p)=>s+p.length,0)),i=0;for(const p of parts){a.set(p,i);i+=p.length;}return a;};
 const quiet=n=>new Int16Array(n);
 function tone(f,phase=0){return Int16Array.from({length:HALF},(_,i)=>Math.round(AMP*Math.min(1,i/32,(HALF-1-i)/32)*Math.sin(2*Math.PI*f*i/RATE+phase)));}
 function preamble(mode,phase=0){if(!freq[mode])throw Error("mode");return join(...freq[mode].map(f=>tone(f,phase)));}
 function packet(tree,mode,phase=0){return join(preamble(mode,phase),I.render(I.encode(tree,"protected"),phase));}
 // 20-ms window with exact integer cycles. Quadrature normalized to received energy.
 const bank={};for(const f of [2300,2700])bank[f]=[Float64Array.from({length:HALF},(_,i)=>Math.cos(2*Math.PI*f*i/RATE)),Float64Array.from({length:HALF},(_,i)=>Math.sin(2*Math.PI*f*i/RATE))];
 function score(p,s,f){let a=0,b=0,e=0;const [c,t]=bank[f];for(let i=0;i<HALF;i++){const v=p[s+i];a+=v*c[i];b+=v*t[i];e+=v*v;}return e<HALF*250**2?0:2*(a*a+b*b)/(HALF*e);}
 function scan(p,mode){
  if(!(p instanceof Int16Array)||p.length>RATE*20||!freq[mode])throw Error("input bound");
  const hits=[],[f,g]=freq[mode];let tested=0;
  for(let s=0;s+HEADER<=p.length;s+=STEP){tested++;const a=score(p,s,f);if(a<.72)continue;const b=score(p,s+HALF,g);if(b<.72)continue;hits.push({start:s,score:Math.min(a,b)});}
  hits.sort((a,b)=>b.score-a.score||a.start-b.start);const keep=[];
  for(const h of hits)if(!keep.some(k=>Math.abs(k.start-h.start)<HEADER))keep.push(h);
  return {tested,candidates:keep.sort((a,b)=>a.start-b.start).map(h=>{const at=h.start+HEADER;if(at+BODY>p.length)return {...h,status:"truncated"};const tokens=I.receive(p.slice(at,at+BODY)),d=I.decode(tokens,"protected");return {...h,tokens,...d};})};
 }
 function stimulus(mode,family,seed){
  const rnd=rng(seed),trees=R.catalog(),a=trees[Math.floor(rnd()*trees.length)],b=trees[Math.floor(rnd()*trees.length)],phase=rnd()*2*Math.PI;
  const lead=137+Math.floor(rnd()*500),gap=183+Math.floor(rnd()*800),tail=320;let p,truth=[],partial=[],decoy=[];
  const A=packet(a,mode,phase),B=packet(b,mode,phase+.73);
  if(family==="noise-only"){p=quiet(lead+FRAME+tail);}
  else if(family==="interrupted"){const frag=A.slice(0,HEADER+3*1280);const s=lead+frag.length+gap;partial=[lead];truth=[{start:s,tree:b}];p=join(quiet(lead),frag,quiet(gap),B,quiet(tail));}
  else if(family==="carrier"||family==="spoof"){
   // Same nuisance waveform in both modes; spoof attaches a real grammar body, not an authentic transmission.
   const nuisance=family==="carrier"?join(tone(2300,phase),tone(2300,phase),quiet(BODY)):join(preamble("repeat",phase),I.render(I.encode(a,"protected"),phase));
   const s=lead+nuisance.length+gap;decoy=[lead];truth=[{start:s,tree:b}];p=join(quiet(lead),nuisance,quiet(gap),B,quiet(tail));
  }else{const s=lead+FRAME+gap;truth=[{start:lead,tree:a},{start:s,tree:b}];if(family==="header-erasure")A.fill(0,0,HALF);p=join(quiet(lead),A,quiet(gap),B,quiet(tail));}
  const sigma=family==="noise"?1700:family==="noise-only"?1700:0;
  if(sigma)for(let i=0;i<p.length;i++)p[i]=Math.round(p[i]+(rnd()*2-1)*Math.sqrt(3)*sigma);
  return {p,truth,partial,decoy,seed,family,mode};
 }
 function evaluate(s){
  const x=scan(s.p,s.mode),m={truth:s.truth.length,acquired:0,correct:0,wrong:0,missed:0,refused:0,falseAcquisition:0,falseAccept:0,partialAcquisition:0,partialAccept:0,scanWindows:x.tested,peak:0,maxError:0},used=new Set();
  for(const v of s.p)m.peak=Math.max(m.peak,Math.abs(v));
  for(const t of s.truth){const hits=x.candidates.map((c,i)=>({c,i})).filter(z=>!used.has(z.i)&&Math.abs(z.c.start-t.start)<=TOL).sort((a,b)=>Math.abs(a.c.start-t.start)-Math.abs(b.c.start-t.start));
   if(!hits.length){m.missed++;continue;}const {c,i}=hits[0];used.add(i);m.acquired++;m.maxError=Math.max(m.maxError,Math.abs(c.start-t.start));if(c.status!=="ok")m.refused++;else if(eq(c.tree,t.tree))m.correct++;else m.wrong++;
  }
  x.candidates.forEach((c,i)=>{if(used.has(i))return;if(s.partial.some(t=>Math.abs(c.start-t)<=TOL)){m.partialAcquisition++;if(c.status==="ok")m.partialAccept++;}else{m.falseAcquisition++;if(c.status==="ok")m.falseAccept++;}});
  return {m,candidates:x.candidates};
 }
 function qualify(){
  let assertions=0;const check=(v,msg)=>{assertions++;if(!v)throw Error(msg);};
  const metrics={},witnesses={};let maxPeak=0;const seeds=Array.from({length:12},(_,i)=>0x61720000+7919*i);
  for(const mode of modes){metrics[mode]={};for(const family of families){const total={};for(const seed of seeds){const s=stimulus(mode,family,seed),{m,candidates}=evaluate(s);
   check(m.truth===m.correct+m.wrong+m.refused+m.missed,"truth conservation");check(m.acquired===m.correct+m.wrong+m.refused,"acquisition conservation");check(candidates.length===m.acquired+m.falseAcquisition+m.partialAcquisition,"candidate conservation");check(m.peak<32768,"no clipping");
   maxPeak=Math.max(maxPeak,m.peak);
   for(const [k,v] of Object.entries(m))total[k]=k==="peak"||k==="maxError"?Math.max(total[k]||0,v):(total[k]||0)+v;
   if(!witnesses[mode+"-"+family])witnesses[mode+"-"+family]={seed,truth:s.truth,partial:s.partial,decoy:s.decoy,candidates,metrics:m};
  }metrics[mode][family]=total;}}
  for(const mode of modes){check(metrics[mode].clean.correct===24,"clean round trips");check(metrics[mode].clean.falseAccept===0,"clean false accept");check(metrics[mode]["header-erasure"].missed===12,"lost header");check(metrics[mode]["noise-only"].truth===0,"noise-only truth");}
  check(metrics.ordered.carrier.falseAcquisition<metrics.repeat.carrier.falseAcquisition,"carrier discrimination");
  check(metrics.repeat.spoof.falseAccept===12,"baseline spoof witness");
  check(metrics.ordered.spoof.falseAccept===0,"ordered mismatch");
  // No claim of authentication: a correctly shaped ordered preamble with a valid foreign body also decodes.
  const spoof=join(quiet(213),packet(["fault"],"ordered"),quiet(320));const hit=scan(spoof,"ordered").candidates;check(hit.some(x=>x.status==="ok"&&eq(x.tree,["fault"])),"ordered spoof");
  const energy={};for(const mode of modes){energy[mode]=0;for(const v of preamble(mode))energy[mode]+=v*v;}
  return {schema:"mhac-grammar-acquisition-v1",source:"6686c10ecba7885d06a8e2b9a2773e1286deddbb",assertions,rate:RATE,headerSamples:HEADER,bodySamples:BODY,frameSamples:FRAME,scanStep:STEP,tolerance:TOL,threshold:.72,amplitude:AMP,seeds,metrics,witnesses,maxPeak,headerEnergy:energy};
 }
 return {packet,preamble,scan,stimulus,evaluate,qualify,modes,families};
})(R,I);
module.exports=Lab;
if(require.main===module){
 const fs=require("node:fs"),path=require("node:path"),crypto=require("node:crypto");
 const dir=process.argv[2]||"output-acquisition";fs.mkdirSync(dir,{recursive:true});
 const q=Lab.qualify(),manifest=[];
 for(const mode of Lab.modes)for(const family of Lab.families){
  const s=Lab.stimulus(mode,family,q.seeds[0]),name=mode+"-"+family+".wav",data=R.wav(s.p);
  fs.writeFileSync(path.join(dir,name),data);
  manifest.push({name,mode,family,seed:s.seed,truth:s.truth,partial:s.partial,decoy:s.decoy,sha256:crypto.createHash("sha256").update(data).digest("hex")});
 }
 fs.writeFileSync(path.join(dir,"acquisition-qualification.json"),JSON.stringify(q,null,2)+"\n");
 fs.writeFileSync(path.join(dir,"acquisition-stimuli.json"),JSON.stringify(manifest,null,2)+"\n");
 console.log(JSON.stringify({assertions:q.assertions,metrics:q.metrics,headerEnergy:q.headerEnergy,maxPeak:q.maxPeak},null,2));
}

/* Executed qualification and report:
# Acoustic frame acquisition — Grammars Run 004

Refs #452 / Draft PR #453. Synthetic-only, isolated continuation at 6686c10ecba7885d06a8e2b9a2773e1286deddbb, accepted main 495a98ca12bae467a507031f04931aa4254b1866. Prior exact-head CI 45546746963 success. Reconciled AGENTS, RAG, programme, runbook, research integrity, experiments/human gates, foundation, frozen protocol and amendment index, issue comments and live open lanes. One GPT-6.2 agent; no subagents, no human evidence or research acceptance.

## Method

Both transports add a 40 ms preamble to the existing 640 ms GF(17) grammar body. The comparator repeats 2300 Hz twice; proposed ordered preamble uses 2300 then 2700 Hz. Both use identical duration, amplitude and envelopes; the second uses an extra carrier. The receiver scans at 1 ms steps, uses phase-independent normalized 20 ms quadrature scores with minimum RMS 250 PCM counts and correlation threshold 0.72; greedily suppresses candidates within 40 ms, then decodes complete bodies using the existing aligned receiver. Match each acquisition once within 5 ms of annotated starts. A damaged first frame may be missed, never assumed delivered. The acquisition contract supplies sample rate and framing design, not start indices. Offline complete-buffer scan, not a real-time implementation.

Seven deterministic scenario families, twelve seeds each per mode. Noise is independent bounded uniform samples with nominal RMS 1700 PCM counts. Identical seeds drive both modes. Carrier and spoof nuisance are specifically repeated 2300 Hz; the ordered mode's rejection is conditional on that nuisance, not universal superiority. Spoof contains a valid grammar body but is not an intended transmission. A valid ordered preamble with foreign valid body is also accepted (explicit regression). No authentication, no human listening or perception evidence, no sample-clock drift, no adversarial optimization; finite fixtures only, no inferential uncertainty or population claim. No independent held-out calibration claimed.

## Executed results

```json
{
  "assertions": 684,
  "metrics": {
    "repeat": {
      "clean": {
        "truth": 24,
        "acquired": 24,
        "correct": 24,
        "wrong": 0,
        "missed": 0,
        "refused": 0,
        "falseAcquisition": 0,
        "falseAccept": 0,
        "partialAcquisition": 0,
        "partialAccept": 0,
        "scanWindows": 16800,
        "peak": 4096,
        "maxError": 8
      },
      "noise": {
        "truth": 24,
        "acquired": 0,
        "correct": 0,
        "wrong": 0,
        "missed": 24,
        "refused": 0,
        "falseAcquisition": 0,
        "falseAccept": 0,
        "partialAcquisition": 0,
        "partialAccept": 0,
        "scanWindows": 16800,
        "peak": 7039,
        "maxError": 0
      },
      "carrier": {
        "truth": 12,
        "acquired": 12,
        "correct": 12,
        "wrong": 0,
        "missed": 0,
        "refused": 0,
        "falseAcquisition": 12,
        "falseAccept": 0,
        "partialAcquisition": 0,
        "partialAccept": 0,
        "scanWindows": 16800,
        "peak": 4096,
        "maxError": 8
      },
      "interrupted": {
        "truth": 12,
        "acquired": 12,
        "correct": 12,
        "wrong": 0,
        "missed": 0,
        "refused": 0,
        "falseAcquisition": 0,
        "falseAccept": 0,
        "partialAcquisition": 12,
        "partialAccept": 0,
        "scanWindows": 12000,
        "peak": 4096,
        "maxError": 8
      },
      "header-erasure": {
        "truth": 24,
        "acquired": 12,
        "correct": 12,
        "wrong": 0,
        "missed": 12,
        "refused": 0,
        "falseAcquisition": 0,
        "falseAccept": 0,
        "partialAcquisition": 0,
        "partialAccept": 0,
        "scanWindows": 16800,
        "peak": 4096,
        "maxError": 8
      },
      "noise-only": {
        "truth": 0,
        "acquired": 0,
        "correct": 0,
        "wrong": 0,
        "missed": 0,
        "refused": 0,
        "falseAcquisition": 0,
        "falseAccept": 0,
        "partialAcquisition": 0,
        "partialAccept": 0,
        "scanWindows": 8232,
        "peak": 2944,
        "maxError": 0
      },
      "spoof": {
        "truth": 12,
        "acquired": 12,
        "correct": 12,
        "wrong": 0,
        "missed": 0,
        "refused": 0,
        "falseAcquisition": 12,
        "falseAccept": 12,
        "partialAcquisition": 0,
        "partialAccept": 0,
        "scanWindows": 16800,
        "peak": 4096,
        "maxError": 8
      }
    },
    "ordered": {
      "clean": {
        "truth": 24,
        "acquired": 24,
        "correct": 24,
        "wrong": 0,
        "missed": 0,
        "refused": 0,
        "falseAcquisition": 0,
        "falseAccept": 0,
        "partialAcquisition": 0,
        "partialAccept": 0,
        "scanWindows": 16800,
        "peak": 4096,
        "maxError": 8
      },
      "noise": {
        "truth": 24,
        "acquired": 0,
        "correct": 0,
        "wrong": 0,
        "missed": 24,
        "refused": 0,
        "falseAcquisition": 0,
        "falseAccept": 0,
        "partialAcquisition": 0,
        "partialAccept": 0,
        "scanWindows": 16800,
        "peak": 7039,
        "maxError": 0
      },
      "carrier": {
        "truth": 12,
        "acquired": 12,
        "correct": 12,
        "wrong": 0,
        "missed": 0,
        "refused": 0,
        "falseAcquisition": 0,
        "falseAccept": 0,
        "partialAcquisition": 0,
        "partialAccept": 0,
        "scanWindows": 16800,
        "peak": 4096,
        "maxError": 8
      },
      "interrupted": {
        "truth": 12,
        "acquired": 12,
        "correct": 12,
        "wrong": 0,
        "missed": 0,
        "refused": 0,
        "falseAcquisition": 0,
        "falseAccept": 0,
        "partialAcquisition": 12,
        "partialAccept": 0,
        "scanWindows": 12000,
        "peak": 4096,
        "maxError": 8
      },
      "header-erasure": {
        "truth": 24,
        "acquired": 12,
        "correct": 12,
        "wrong": 0,
        "missed": 12,
        "refused": 0,
        "falseAcquisition": 0,
        "falseAccept": 0,
        "partialAcquisition": 0,
        "partialAccept": 0,
        "scanWindows": 16800,
        "peak": 4096,
        "maxError": 8
      },
      "noise-only": {
        "truth": 0,
        "acquired": 0,
        "correct": 0,
        "wrong": 0,
        "missed": 0,
        "refused": 0,
        "falseAcquisition": 0,
        "falseAccept": 0,
        "partialAcquisition": 0,
        "partialAccept": 0,
        "scanWindows": 8232,
        "peak": 2944,
        "maxError": 0
      },
      "spoof": {
        "truth": 12,
        "acquired": 12,
        "correct": 12,
        "wrong": 0,
        "missed": 0,
        "refused": 0,
        "falseAcquisition": 0,
        "falseAccept": 0,
        "partialAcquisition": 0,
        "partialAccept": 0,
        "scanWindows": 16800,
        "peak": 4096,
        "maxError": 8
      }
    }
  },
  "headerEnergy": {
    "repeat": 4636836942,
    "ordered": 4636503072
  },
  "maxPeak": 7039
}
```

## Reproduction and interfaces

Node 18+: `node acquisition.cjs output-acquisition`. Generates 14 original PCM16 WAV recipes, SHA-256 manifest and JSON trace receipt. Exported packet, preamble, scan, stimulus, evaluate, qualify. Keep playback low; digital peak is not SPL. V8 executed qualification twice and serialized source replay once, all identical. Native Node filesystem/CLI, actual listening, whole repository validation and independent review outstanding. No new dependencies, no frozen/canonical edits. Next: incremental streaming acquisition, clock drift and preamble mimics including matched ordered nuisance; evaluate header erasure alternatives at matched budget before integration with Situated Relay.

*/
