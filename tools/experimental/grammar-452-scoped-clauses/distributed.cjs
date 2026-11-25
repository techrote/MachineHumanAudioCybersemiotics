"use strict";
// Grammars lane / Refs #452, Draft PR #453. Synthetic only.
// Pinned dependencies: fecc566ec781f47ddcb47e6818a578d79e197690; main 495a98ca12bae467a507031f04931aa4254b1866.
const R=require("./recursive.cjs"),I=require("./integrity.cjs"),A=require("./acquisition.cjs");
const Lab=(function laboratory(R,I,A){
 const RATE=16000,H=320,S=1280,B=10240,F=B+2*H,STEP=16,TH=.72,TOL=96;
 const modes=["prefix-pair","prefix-either","split-either"],conditions=["clean","first-marker","second-marker","prefix-burst","middle-burst","drift-minus","drift-plus","noise","noise-only","matched-mimic"];
 const offs=m=>m==="split-either"?[0,H+4*S]:[0,H];
 const join=(...a)=>{const p=new Int16Array(a.reduce((s,v)=>s+v.length,0));let k=0;for(const v of a){p.set(v,k);k+=v.length;}return p;};
 const z=n=>new Int16Array(n);
 const rng=s=>()=>{s=(Math.imul(s,1664525)+1013904223)>>>0;return s/4294967296;};
 const eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
 const catalog=R.catalog();
 function packet(tree,mode,phase=0){const h=A.preamble("ordered",phase),b=I.render(I.encode(tree,"protected"),phase);return mode==="split-either"?join(h.slice(0,H),b.slice(0,4*S),h.slice(H),b.slice(4*S)):join(h,b);}
 function stretch(p,scale){return Int16Array.from({length:Math.round(p.length*scale)},(_,i)=>{const x=i/scale,j=Math.floor(x),a=x-j;return Math.round((p[j]||0)*(1-a)+(p[j+1]||0)*a);});}
 const bank=[2300,2700].map(f=>[Float64Array.from({length:H},(_,i)=>Math.cos(2*Math.PI*f*i/RATE)),Float64Array.from({length:H},(_,i)=>Math.sin(2*Math.PI*f*i/RATE))]);
 function score(p,s,k){let x=0,y=0,e=0;const [c,t]=bank[k];for(let i=0;i<H;i++){const v=p[s+i];x+=v*c[i];y+=v*t[i];e+=v*v;}return e<H*250**2?0:2*(x*x+y*y)/(H*e);}
 function scan(p,mode){
  if(!(p instanceof Int16Array)||p.length>RATE*20||!modes.includes(mode))throw Error("input");
  const peaks=[[],[]],o=offs(mode);let windows=0;
  for(let k=0;k<2;k++){const all=[];for(let s=0;s+H<=p.length;s+=STEP){windows++;const q=score(p,s,k);if(q>=TH)all.push({at:s,q});}all.sort((a,b)=>b.q-a.q||a.at-b.at);for(const x of all)if(!peaks[k].some(y=>Math.abs(x.at-y.at)<H))peaks[k].push(x);}
  const proposed=[];
  for(let k=0;k<2;k++)for(const x of peaks[k]){const start=x.at-o[k];const other=peaks[1-k].filter(y=>Math.abs(y.at-o[1-k]-start)<=TOL).sort((a,b)=>b.q-a.q)[0];if(mode==="prefix-pair"&&!other)continue;proposed.push({start:other?Math.round((start+other.at-o[1-k])/2):start,support:other?2:1,q:other?Math.min(x.q,other.q):x.q});}
  proposed.sort((a,b)=>b.support-a.support||b.q-a.q||a.start-b.start);const keep=[];
  for(const x of proposed)if(!keep.some(y=>Math.abs(x.start-y.start)<=TOL))keep.push(x);
  const candidates=keep.sort((a,b)=>a.start-b.start).map(x=>{const s=x.start;if(s<0||s+F>p.length)return {...x,status:"truncated"};const b=mode==="split-either"?join(p.slice(s+H,s+H+4*S),p.slice(s+2*H+4*S,s+F)):p.slice(s+2*H,s+F);const tokens=I.receive(b);return {...x,tokens,...I.decode(tokens,"protected")};});
  return {windows,candidates,peaks};
 }
 function stimulus(mode,condition,seed){
  const rnd=rng(seed),tree=catalog[Math.floor(rnd()*catalog.length)],foreign=catalog[Math.floor(rnd()*catalog.length)],phase=rnd()*6.283185307179586,lead=801+Math.floor(rnd()*500),tail=1200,offset=offs(mode);
  let a=packet(tree,mode,phase),truth=[{start:lead,tree}],decoy=[];
  if(condition==="first-marker")a.fill(0,offset[0],offset[0]+H);
  if(condition==="second-marker")a.fill(0,offset[1],offset[1]+H);
  if(condition==="prefix-burst")a.fill(0,0,2*H);
  if(condition==="middle-burst")a.fill(0,H+4*S,H+4*S+2*H);
  if(condition==="drift-minus"||condition==="drift-plus")a=stretch(a,condition==="drift-minus"?.995:1.005);
  if(condition==="noise-only"){truth=[];a=z(F);}
  if(condition==="matched-mimic"){truth=[];decoy=[lead];a=packet(foreign,mode,phase);}
  const pcm=join(z(lead),a,z(tail));const sigma=condition==="noise"||condition==="noise-only"?900:0;
  if(sigma)for(let i=0;i<pcm.length;i++)pcm[i]=Math.round(pcm[i]+(rnd()*2-1)*Math.sqrt(3)*sigma);
  return {pcm,truth,decoy,mode,condition,seed};
 }
 function evaluate(s){const out=scan(s.pcm,s.mode),used=new Set(),m={truth:s.truth.length,correct:0,wrong:0,refused:0,missed:0,falseAcquisition:0,falseAccept:0,windows:out.windows,peak:0};for(const v of s.pcm)m.peak=Math.max(m.peak,Math.abs(v));
  for(const t of s.truth){const hit=out.candidates.map((c,i)=>({c,i})).filter(x=>!used.has(x.i)&&Math.abs(x.c.start-t.start)<=TOL).sort((a,b)=>Math.abs(a.c.start-t.start)-Math.abs(b.c.start-t.start))[0];if(!hit){m.missed++;continue;}used.add(hit.i);if(hit.c.status!=="ok")m.refused++;else if(eq(t.tree,hit.c.tree))m.correct++;else m.wrong++;}
  out.candidates.forEach((c,i)=>{if(!used.has(i)){m.falseAcquisition++;if(c.status==="ok")m.falseAccept++;}});return {m,candidates:out.candidates,peaks:out.peaks};
 }
 function qualify(){let assertions=0;const check=(v,msg)=>{assertions++;if(!v)throw Error(msg);};const seeds=Array.from({length:8},(_,i)=>0x71840000+104729*i),metrics={},witnesses={},energy={};
  for(const mode of modes){metrics[mode]={};energy[mode]=packet(["fault"],mode).reduce((a,v)=>a+v*v,0);for(const condition of conditions){const t={};for(const seed of seeds){const s=stimulus(mode,condition,seed),x=evaluate(s),m=x.m;check(m.truth===m.correct+m.wrong+m.refused+m.missed,"truth accounting");check(x.candidates.length===m.truth-m.missed+m.falseAcquisition,"candidate accounting");check(m.peak<32768,"peak");for(const [k,v] of Object.entries(m))t[k]=k==="peak"?Math.max(t[k]||0,v):(t[k]||0)+v;if(seed===seeds[0])witnesses[mode+"/"+condition]={seed,truth:s.truth,decoy:s.decoy,...x};}metrics[mode][condition]=t;}
   check(metrics[mode].clean.correct===seeds.length,"clean");
  }
  check(energy[modes[0]]===energy[modes[1]]&&energy[modes[0]]===energy[modes[2]],"equal energy");
  check(metrics["prefix-pair"]["first-marker"].missed===seeds.length,"strict header failure");
  check(metrics["split-either"]["prefix-burst"].correct===seeds.length,"split recovers prefix burst");
  check(metrics["prefix-either"]["prefix-burst"].correct===0,"prefix burst failure");
  return {schema:"mhac-grammar-distributed-v1",source:"fecc566ec781f47ddcb47e6818a578d79e197690",assertions,seeds,rate:RATE,frameSamples:F,threshold:TH,tolerance:TOL,metrics,energy,witnesses};
 }
 return {packet,scan,stimulus,evaluate,qualify,modes,conditions};
})(R,I,A);
module.exports=Lab;
if(require.main===module){const fs=require("node:fs"),path=require("node:path"),crypto=require("node:crypto");const dir=process.argv[2]||"output-distributed";fs.mkdirSync(dir,{recursive:true});const q=Lab.qualify(),manifest=[];for(const mode of Lab.modes)for(const condition of ["clean","prefix-burst","middle-burst","matched-mimic"]){const s=Lab.stimulus(mode,condition,q.seeds[0]),name=mode+"-"+condition+".wav",wav=R.wav(s.pcm);fs.writeFileSync(path.join(dir,name),wav);manifest.push({name,mode,condition,seed:s.seed,truth:s.truth,decoy:s.decoy,sha256:crypto.createHash("sha256").update(wav).digest("hex")});}fs.writeFileSync(path.join(dir,"distributed-qualification.json"),JSON.stringify(q,null,2)+"\n");fs.writeFileSync(path.join(dir,"distributed-stimuli.json"),JSON.stringify(manifest,null,2)+"\n");console.log(JSON.stringify({assertions:q.assertions,metrics:q.metrics,energy:q.energy},null,2));}

/* Run 005 executed report. Refs #452, #453. Synthetic only. One GPT-6.2 agent; no subagents. Previous exact head CI 45553437450 passed. Reconciled main AGENTS/RAG and topic authorities, issue/PR/branch inventory. Same 40 ms marker duration and 640 ms body in all modes; prefix-pair requires both markers, prefix-either permits either, split-either moves second to halfway. Nominal timing reconstruction (no drift compensation), 1 ms scan grid, 6 ms matching/pair tolerance, 0.72 normalized score inherited from prior run, 250 count minimum RMS. Candidate pairing and suppression are offline and not streaming. Eight new deterministic seeds per mode/condition, no threshold tuning; finite fixture results, not population or human estimates. Noise bounded uniform nominal RMS 900 PCM counts, drift linear resampling +/-0.5%, same seeds and phase across modes. Middle burst is fixed absolute packet offset 5440 samples; it can erase different structural roles. Matching mimic is a valid foreign frame, not authentication. No real listening. Code and generated bytes executed in V8; native CLI and hash export not executed. Reproduce node distributed.cjs output-distributed. 12 original WAV byte arrays generated in V8. Metrics include wrong intended, missed, refused, false accept and false acquisition separately; false acquisitions can include alternate shifted hypotheses of true frames. No canonical/shared records edited. Exact executed aggregate: 
{
  "assertions": 727,
  "seeds": [
    1904476160,
    1904580889,
    1904685618,
    1904790347,
    1904895076,
    1904999805,
    1905104534,
    1905209263
  ],
  "metrics": {
    "prefix-pair": {
      "clean": {
        "truth": 8,
        "correct": 8,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquisition": 0,
        "falseAccept": 0,
        "windows": 12808,
        "peak": 4096
      },
      "first-marker": {
        "truth": 8,
        "correct": 0,
        "wrong": 0,
        "refused": 0,
        "missed": 8,
        "falseAcquisition": 0,
        "falseAccept": 0,
        "windows": 12808,
        "peak": 4096
      },
      "second-marker": {
        "truth": 8,
        "correct": 0,
        "wrong": 0,
        "refused": 0,
        "missed": 8,
        "falseAcquisition": 0,
        "falseAccept": 0,
        "windows": 12808,
        "peak": 4096
      },
      "prefix-burst": {
        "truth": 8,
        "correct": 0,
        "wrong": 0,
        "refused": 0,
        "missed": 8,
        "falseAcquisition": 0,
        "falseAccept": 0,
        "windows": 12808,
        "peak": 4096
      },
      "middle-burst": {
        "truth": 8,
        "correct": 8,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquisition": 0,
        "falseAccept": 0,
        "windows": 12808,
        "peak": 4096
      },
      "drift-minus": {
        "truth": 8,
        "correct": 0,
        "wrong": 0,
        "refused": 8,
        "missed": 0,
        "falseAcquisition": 0,
        "falseAccept": 0,
        "windows": 12752,
        "peak": 4095
      },
      "drift-plus": {
        "truth": 8,
        "correct": 0,
        "wrong": 0,
        "refused": 8,
        "missed": 0,
        "falseAcquisition": 0,
        "falseAccept": 0,
        "windows": 12864,
        "peak": 4095
      },
      "noise": {
        "truth": 8,
        "correct": 8,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquisition": 0,
        "falseAccept": 0,
        "windows": 12808,
        "peak": 5652
      },
      "noise-only": {
        "truth": 0,
        "correct": 0,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquisition": 0,
        "falseAccept": 0,
        "windows": 12808,
        "peak": 1559
      },
      "matched-mimic": {
        "truth": 0,
        "correct": 0,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquisition": 8,
        "falseAccept": 8,
        "windows": 12808,
        "peak": 4096
      }
    },
    "prefix-either": {
      "clean": {
        "truth": 8,
        "correct": 8,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquisition": 0,
        "falseAccept": 0,
        "windows": 12808,
        "peak": 4096
      },
      "first-marker": {
        "truth": 8,
        "correct": 8,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquisition": 0,
        "falseAccept": 0,
        "windows": 12808,
        "peak": 4096
      },
      "second-marker": {
        "truth": 8,
        "correct": 8,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquisition": 0,
        "falseAccept": 0,
        "windows": 12808,
        "peak": 4096
      },
      "prefix-burst": {
        "truth": 8,
        "correct": 0,
        "wrong": 0,
        "refused": 0,
        "missed": 8,
        "falseAcquisition": 0,
        "falseAccept": 0,
        "windows": 12808,
        "peak": 4096
      },
      "middle-burst": {
        "truth": 8,
        "correct": 8,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquisition": 0,
        "falseAccept": 0,
        "windows": 12808,
        "peak": 4096
      },
      "drift-minus": {
        "truth": 8,
        "correct": 0,
        "wrong": 0,
        "refused": 8,
        "missed": 0,
        "falseAcquisition": 0,
        "falseAccept": 0,
        "windows": 12752,
        "peak": 4095
      },
      "drift-plus": {
        "truth": 8,
        "correct": 0,
        "wrong": 0,
        "refused": 8,
        "missed": 0,
        "falseAcquisition": 0,
        "falseAccept": 0,
        "windows": 12864,
        "peak": 4095
      },
      "noise": {
        "truth": 8,
        "correct": 8,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquisition": 0,
        "falseAccept": 0,
        "windows": 12808,
        "peak": 5652
      },
      "noise-only": {
        "truth": 0,
        "correct": 0,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquisition": 0,
        "falseAccept": 0,
        "windows": 12808,
        "peak": 1559
      },
      "matched-mimic": {
        "truth": 0,
        "correct": 0,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquisition": 8,
        "falseAccept": 8,
        "windows": 12808,
        "peak": 4096
      }
    },
    "split-either": {
      "clean": {
        "truth": 8,
        "correct": 8,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquisition": 0,
        "falseAccept": 0,
        "windows": 12808,
        "peak": 4096
      },
      "first-marker": {
        "truth": 8,
        "correct": 8,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquisition": 0,
        "falseAccept": 0,
        "windows": 12808,
        "peak": 4096
      },
      "second-marker": {
        "truth": 8,
        "correct": 8,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquisition": 0,
        "falseAccept": 0,
        "windows": 12808,
        "peak": 4096
      },
      "prefix-burst": {
        "truth": 8,
        "correct": 8,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquisition": 0,
        "falseAccept": 0,
        "windows": 12808,
        "peak": 4096
      },
      "middle-burst": {
        "truth": 8,
        "correct": 8,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquisition": 0,
        "falseAccept": 0,
        "windows": 12808,
        "peak": 4096
      },
      "drift-minus": {
        "truth": 8,
        "correct": 0,
        "wrong": 0,
        "refused": 8,
        "missed": 0,
        "falseAcquisition": 0,
        "falseAccept": 0,
        "windows": 12752,
        "peak": 4095
      },
      "drift-plus": {
        "truth": 8,
        "correct": 0,
        "wrong": 0,
        "refused": 8,
        "missed": 0,
        "falseAcquisition": 0,
        "falseAccept": 0,
        "windows": 12864,
        "peak": 4095
      },
      "noise": {
        "truth": 8,
        "correct": 8,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquisition": 0,
        "falseAccept": 0,
        "windows": 12808,
        "peak": 5652
      },
      "noise-only": {
        "truth": 0,
        "correct": 0,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquisition": 0,
        "falseAccept": 0,
        "windows": 12808,
        "peak": 1559
      },
      "matched-mimic": {
        "truth": 0,
        "correct": 0,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquisition": 8,
        "falseAccept": 8,
        "windows": 12808,
        "peak": 4096
      }
    }
  },
  "energy": {
    "prefix-pair": 61829799097,
    "prefix-either": 61829799097,
    "split-either": 61829799097
  },
  "specimens": [
    {
      "mode": "prefix-pair",
      "condition": "clean",
      "bytes": 25878,
      "peak": 4096
    },
    {
      "mode": "prefix-pair",
      "condition": "prefix-burst",
      "bytes": 25878,
      "peak": 4096
    },
    {
      "mode": "prefix-pair",
      "condition": "middle-burst",
      "bytes": 25878,
      "peak": 4096
    },
    {
      "mode": "prefix-pair",
      "condition": "matched-mimic",
      "bytes": 25878,
      "peak": 4096
    },
    {
      "mode": "prefix-either",
      "condition": "clean",
      "bytes": 25878,
      "peak": 4096
    },
    {
      "mode": "prefix-either",
      "condition": "prefix-burst",
      "bytes": 25878,
      "peak": 4096
    },
    {
      "mode": "prefix-either",
      "condition": "middle-burst",
      "bytes": 25878,
      "peak": 4096
    },
    {
      "mode": "prefix-either",
      "condition": "matched-mimic",
      "bytes": 25878,
      "peak": 4096
    },
    {
      "mode": "split-either",
      "condition": "clean",
      "bytes": 25878,
      "peak": 4096
    },
    {
      "mode": "split-either",
      "condition": "prefix-burst",
      "bytes": 25878,
      "peak": 4096
    },
    {
      "mode": "split-either",
      "condition": "middle-burst",
      "bytes": 25878,
      "peak": 4096
    },
    {
      "mode": "split-either",
      "condition": "matched-mimic",
      "bytes": 25878,
      "peak": 4096
    }
  ]
}
*/
