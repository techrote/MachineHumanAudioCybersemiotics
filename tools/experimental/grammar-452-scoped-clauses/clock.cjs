"use strict";
// Refs #452 / Draft #453; Grammars lane. Synthetic only.
// Exact source f5cce85de1f8d0be5962043ce65671d2dd27298b; accepted main 495a98ca12bae467a507031f04931aa4254b1866.
const R=require("./recursive.cjs"), I=require("./integrity.cjs"), D=require("./distributed.cjs");
const RATE=16000,H=320,S=1280,SEP=5440,F=10880,TOL=96;
const eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const join=(...p)=>{const a=new Int16Array(p.reduce((n,x)=>n+x.length,0));let i=0;for(const x of p){a.set(x,i);i+=x.length;}return a;};
const interp=(p,t)=>{const j=Math.floor(t),u=t-j;return Math.round((p[j]||0)*(1-u)+(p[j+1]||0)*u);};
const stretch=(p,s)=>Int16Array.from({length:Math.round(p.length*s)},(_,i)=>interp(p,i/s));
const rng=seed=>()=>{seed^=seed<<13;seed^=seed>>>17;seed^=seed<<5;return (seed>>>0)/4294967296;};
// Tapered quadrature energy refines each existing coarse peak within +/-24 samples.
const bank=[2300,2700].map(f=>[Float64Array.from({length:H},(_,i)=>Math.min(1,i/32,(H-1-i)/32)*Math.cos(2*Math.PI*f*i/RATE)),Float64Array.from({length:H},(_,i)=>Math.min(1,i/32,(H-1-i)/32)*Math.sin(2*Math.PI*f*i/RATE))]);
function refine(p,at,k){let best={at,score:-1};const [c,s]=bank[k];for(let j=Math.max(0,at-24);j<=Math.min(p.length-H,at+24);j++){let x=0,y=0;for(let i=0;i<H;i++){x+=p[j+i]*c[i];y+=p[j+i]*s[i];}const score=x*x+y*y;if(score>best.score)best={at:j,score};}return best.at;}
function frame(p,start,scale){
 if(!Number.isFinite(start)||!Number.isFinite(scale)||scale<=0||start<0||start+(F-1)*scale>=p.length)return {status:"truncated"};
 const a=Int16Array.from({length:F},(_,i)=>interp(p,start+i*scale));
 const tokens=I.receive(join(a.slice(H,SEP),a.slice(SEP+H,F)));
 return {tokens,...I.decode(tokens,"protected")};
}
function receive(p){
 const coarse=D.scan(p,"split-either"),out=[];
 for(const c of coarse.candidates){
  const marks=[0,SEP].map((o,k)=>{
   const x=coarse.peaks[k].filter(x=>Math.abs(x.at-o-c.start)<=TOL).sort((a,b)=>Math.abs(a.at-o-c.start)-Math.abs(b.at-o-c.start))[0];
   return x?refine(p,x.at,k):null;
  });
  const [a,b]=marks;let scale=1,source="single",start=a??(b===null?c.start:b-SEP);
  if(a!==null&&b!==null){const s=(b-a)/SEP;if(s>=.98&&s<=1.02){scale=s;source="pair";start=a;}else source="inconsistent";}
  const refinedStart=a!==null&&b!==null?(a+b-SEP)/2:start;
  out.push({coarseStart:c.start,marks,source,scale,start,baseline:c,nominal:{start:refinedStart,...frame(p,refinedStart,1)},affine:{start,...frame(p,start,scale)}});
 }
 return {candidates:out,windows:coarse.windows};
}
const conditions=[
 ["clean",1,0,"none"],["minus025",.9975,0,"none"],["plus025",1.0025,0,"none"],
 ["minus05",.995,0,"none"],["plus05",1.005,0,"none"],["minus10",.99,0,"none"],["plus10",1.01,0,"none"],
 ["minus05-noise",.995,900,"none"],["plus05-noise",1.005,900,"none"],
 ["minus05-first-erased",.995,0,"first"],["plus05-second-erased",1.005,0,"second"],
 ["prefix-erased-clean",1,0,"prefix"],["noise-only",1,900,"noise"],["foreign",1.005,0,"foreign"],
 ["shifted-marker",1,0,"shift"],["plus20",1.02,0,"none"]
];
const catalog=R.catalog();
function stimulus(name,seed){
 const row=conditions.find(x=>x[0]===name);if(!row)throw Error("condition");const [,scale,sigma,fault]=row,r=rng(seed);
 const tree=catalog[Math.floor(r()*catalog.length)],phase=r()*2*Math.PI,lead=800+Math.floor(r()*512);
 let a=D.packet(tree,"split-either",phase);
 if(fault==="first"||fault==="prefix")a.fill(0,0,fault==="prefix"?2*H:H);
 if(fault==="second")a.fill(0,SEP,SEP+H);
 if(fault==="shift"){const b=a.slice(SEP,SEP+H);a.fill(0,SEP,SEP+H);a.set(b,SEP+48);}
 if(fault==="noise")a.fill(0);
 const pcm=join(new Int16Array(lead),stretch(a,scale),new Int16Array(1200));
 if(sigma)for(let i=0;i<pcm.length;i++)pcm[i]=Math.round(pcm[i]+(r()*2-1)*Math.sqrt(3)*sigma);
 return {name,seed,scale,pcm,truth:["foreign","noise"].includes(fault)?null:{start:lead,tree},fault,tree};
}
function evaluate(s){
 const out=receive(s.pcm),metrics={};let peak=0;for(const v of s.pcm)peak=Math.max(peak,Math.abs(v));
 for(const mode of ["baseline","nominal","affine"]){
  const a=out.candidates.map(x=>x[mode]),m={correct:0,wrong:0,refused:0,missed:0,falseAcquire:0,falseAccept:0};
  const matches=s.truth?a.map((c,i)=>({c,i})).filter(x=>Math.abs(x.c.start-s.truth.start)<=TOL).sort((a,b)=>Math.abs(a.c.start-s.truth.start)-Math.abs(b.c.start-s.truth.start)):[];
  const hit=matches[0];if(s.truth){if(!hit)m.missed++;else if(hit.c.status!=="ok")m.refused++;else if(eq(hit.c.tree,s.truth.tree))m.correct++;else m.wrong++;}
  a.forEach((c,i)=>{if(i!==hit?.i){m.falseAcquire++;if(c.status==="ok")m.falseAccept++;}});metrics[mode]=m;
 }
 const oracle=s.truth?frame(s.pcm,s.truth.start,s.scale):null;
 const m=out.candidates.filter(x=>s.truth&&Math.abs(x.start-s.truth.start)<=TOL).sort((a,b)=>Math.abs(a.start-s.truth.start)-Math.abs(b.start-s.truth.start))[0];
 return {metrics,oracle:oracle?oracle.status!=="ok"?"refused":eq(oracle.tree,s.truth.tree)?"correct":"wrong":null,fit:m?{source:m.source,scale:m.scale,start:m.start,scaleErrorPpm:Math.round((m.scale-s.scale)*1e6),startErrorSamples:m.start-s.truth.start}:null,peak,...out};
}
function qualify(){
 let assertions=0;const check=(v,m)=>{assertions++;if(!v)throw Error(m);};
 const seeds=Array.from({length:12},(_,i)=>(0x935761b1+Math.imul(i,2654435761))>>>0),metrics={},traces=[];
 for(const [name] of conditions){
  const sum={baseline:{},nominal:{},affine:{},oracle:{},pairFits:0,maxPairErrorPpm:0,sumAbsPairErrorPpm:0,peak:0};
  for(const seed of seeds){const s=stimulus(name,seed),e=evaluate(s);
   for(const [mode,m] of Object.entries(e.metrics)){check(m.correct+m.wrong+m.refused+m.missed===(s.truth?1:0),"truth accounting");check(e.candidates.length===m.correct+m.wrong+m.refused+m.falseAcquire,"candidate accounting");for(const [k,v] of Object.entries(m))sum[mode][k]=(sum[mode][k]||0)+v;}
   if(e.oracle)sum.oracle[e.oracle]=(sum.oracle[e.oracle]||0)+1;
   if(e.fit?.source==="pair"){sum.pairFits++;sum.maxPairErrorPpm=Math.max(sum.maxPairErrorPpm,Math.abs(e.fit.scaleErrorPpm));sum.sumAbsPairErrorPpm+=Math.abs(e.fit.scaleErrorPpm);}
   check(e.peak<32768,"digital peak");sum.peak=Math.max(sum.peak,e.peak);traces.push({name,seed,scale:s.scale,truth:s.truth,...e});
  }metrics[name]=sum;
 }
 check(metrics.clean.affine.correct===seeds.length,"clean");
 check(metrics["noise-only"].affine.falseAccept===0,"noise-only");
 check(metrics.foreign.affine.falseAccept>0,"foreign counterexample");
 return {schema:"mhac-grammar-clock-v1",source:"f5cce85de1f8d0be5962043ce65671d2dd27298b",assertions,seeds,conditions,metrics,traces};
}
module.exports={stimulus,receive,evaluate,qualify,frame,conditions};
if(require.main===module){
 const fs=require("node:fs"),path=require("node:path"),crypto=require("node:crypto"),dir=process.argv[2]||"output-clock";
 fs.mkdirSync(dir,{recursive:true});const q=qualify(),manifest=[];
 for(const [name] of conditions){const s=stimulus(name,q.seeds[0]),bytes=R.wav(s.pcm),file=name+".wav";fs.writeFileSync(path.join(dir,file),bytes);manifest.push({file,seed:s.seed,truth:s.truth,scale:s.scale,sha256:crypto.createHash("sha256").update(bytes).digest("hex")});}
 fs.writeFileSync(path.join(dir,"clock-qualification.json"),JSON.stringify(q,null,2)+"\n");fs.writeFileSync(path.join(dir,"clock-stimuli.json"),JSON.stringify(manifest,null,2)+"\n");console.log(JSON.stringify({assertions:q.assertions,metrics:q.metrics},null,2));
}

/*
Grammars Run 006: affine clock reconstruction. Refs #452 / #453. One GPT-6.2 agent, no subagents. Accepted main 495a98ca12bae467a507031f04931aa4254b1866; prior CI 45560512074 success. Reconciled main instructions, programme, runbook, integrity, validation, experiments/human gates, foundations, protocol index, issue/comments and current lane inventory. Existing distributed frame unchanged. Fixed sample-clock model; no additional energy, bandwidth or packet duration. Existing scan candidates and nominal-frequency gate inherited; refine each peak +/-24 samples with tapered quadrature, estimate scale from 5440-sample separation and linearly resample; one marker falls back to nominal rate. Compare prior baseline, refined nominal, affine and privileged oracle with exact start and scale (truth packets only; not a deployable detector). Match within 96 samples; unmatched hypotheses counted as false acquisitions. 12 fresh deterministic xorshift seeds per 16 conditions, paired across conditions/receivers, no parameter search or population estimates. Uniform bounded nominal RMS 900 noise. Shifted marker moves B 48 samples, overwrites overlapping body samples; a deliberate model violation. Foreign valid message not authentication. Observed clean +/-0.5% drift recovery improves 1/24 to 24/24, but drift+noise and +/-1% lose marker acquisition; shifted marker causes 12 new refusals despite nominal success; foreign accepts rise 1/12 to 12/12. No human evidence. V8 qualification repeated identically; 16 WAV byte arrays generated. Native CLI/filesystem/hash exports and audition not executed. Node 18+: node clock.cjs output-clock; writes full traces, original WAVs and SHA-256 manifest. Digital peak not calibrated SPL. No canonical changes, no extra CI fan-out, no merge or self-certification. Next: scale-tolerant marker detector with separate development/evaluation and multi-marker consistency checks, source attribution remains separate. Executed compact aggregate and all conditions below.
{
  "assertions": 1347,
  "seeds": [
    2471977393,
    831445858,
    3485881619,
    1845350084,
    204818549,
    2859254310,
    1218722775,
    3873158536,
    2232627001,
    592095466,
    3246531227,
    1605999692
  ],
  "conditions": [
    [
      "clean",
      1,
      0,
      "none"
    ],
    [
      "minus025",
      0.9975,
      0,
      "none"
    ],
    [
      "plus025",
      1.0025,
      0,
      "none"
    ],
    [
      "minus05",
      0.995,
      0,
      "none"
    ],
    [
      "plus05",
      1.005,
      0,
      "none"
    ],
    [
      "minus10",
      0.99,
      0,
      "none"
    ],
    [
      "plus10",
      1.01,
      0,
      "none"
    ],
    [
      "minus05-noise",
      0.995,
      900,
      "none"
    ],
    [
      "plus05-noise",
      1.005,
      900,
      "none"
    ],
    [
      "minus05-first-erased",
      0.995,
      0,
      "first"
    ],
    [
      "plus05-second-erased",
      1.005,
      0,
      "second"
    ],
    [
      "prefix-erased-clean",
      1,
      0,
      "prefix"
    ],
    [
      "noise-only",
      1,
      900,
      "noise"
    ],
    [
      "foreign",
      1.005,
      0,
      "foreign"
    ],
    [
      "shifted-marker",
      1,
      0,
      "shift"
    ],
    [
      "plus20",
      1.02,
      0,
      "none"
    ]
  ],
  "metrics": {
    "clean": {
      "baseline": {
        "correct": 12,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "nominal": {
        "correct": 12,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "affine": {
        "correct": 12,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "oracle": {
        "correct": 12
      },
      "pairFits": 12,
      "maxPairErrorPpm": 184,
      "sumAbsPairErrorPpm": 736,
      "peak": 4096
    },
    "minus025": {
      "baseline": {
        "correct": 12,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "nominal": {
        "correct": 12,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "affine": {
        "correct": 12,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "oracle": {
        "correct": 12
      },
      "pairFits": 12,
      "maxPairErrorPpm": 294,
      "sumAbsPairErrorPpm": 1432,
      "peak": 4096
    },
    "plus025": {
      "baseline": {
        "correct": 12,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "nominal": {
        "correct": 12,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "affine": {
        "correct": 12,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "oracle": {
        "correct": 12
      },
      "pairFits": 12,
      "maxPairErrorPpm": 257,
      "sumAbsPairErrorPpm": 1947,
      "peak": 4096
    },
    "minus05": {
      "baseline": {
        "correct": 0,
        "wrong": 0,
        "refused": 12,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "nominal": {
        "correct": 0,
        "wrong": 0,
        "refused": 12,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "affine": {
        "correct": 12,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "oracle": {
        "correct": 12
      },
      "pairFits": 12,
      "maxPairErrorPpm": 147,
      "sumAbsPairErrorPpm": 554,
      "peak": 4096
    },
    "plus05": {
      "baseline": {
        "correct": 1,
        "wrong": 0,
        "refused": 11,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "nominal": {
        "correct": 1,
        "wrong": 0,
        "refused": 11,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "affine": {
        "correct": 12,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "oracle": {
        "correct": 12
      },
      "pairFits": 12,
      "maxPairErrorPpm": 331,
      "sumAbsPairErrorPpm": 2244,
      "peak": 4096
    },
    "minus10": {
      "baseline": {
        "correct": 0,
        "wrong": 0,
        "refused": 0,
        "missed": 12,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "nominal": {
        "correct": 0,
        "wrong": 0,
        "refused": 0,
        "missed": 12,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "affine": {
        "correct": 0,
        "wrong": 0,
        "refused": 0,
        "missed": 12,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "oracle": {
        "correct": 12
      },
      "pairFits": 0,
      "maxPairErrorPpm": 0,
      "sumAbsPairErrorPpm": 0,
      "peak": 4096
    },
    "plus10": {
      "baseline": {
        "correct": 0,
        "wrong": 0,
        "refused": 0,
        "missed": 12,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "nominal": {
        "correct": 0,
        "wrong": 0,
        "refused": 0,
        "missed": 12,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "affine": {
        "correct": 0,
        "wrong": 0,
        "refused": 0,
        "missed": 12,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "oracle": {
        "correct": 12
      },
      "pairFits": 0,
      "maxPairErrorPpm": 0,
      "sumAbsPairErrorPpm": 0,
      "peak": 4096
    },
    "minus05-noise": {
      "baseline": {
        "correct": 0,
        "wrong": 0,
        "refused": 5,
        "missed": 7,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "nominal": {
        "correct": 0,
        "wrong": 0,
        "refused": 5,
        "missed": 7,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "affine": {
        "correct": 0,
        "wrong": 0,
        "refused": 5,
        "missed": 7,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "oracle": {
        "correct": 12
      },
      "pairFits": 0,
      "maxPairErrorPpm": 0,
      "sumAbsPairErrorPpm": 0,
      "peak": 5648
    },
    "plus05-noise": {
      "baseline": {
        "correct": 0,
        "wrong": 0,
        "refused": 7,
        "missed": 5,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "nominal": {
        "correct": 0,
        "wrong": 0,
        "refused": 7,
        "missed": 5,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "affine": {
        "correct": 0,
        "wrong": 0,
        "refused": 7,
        "missed": 5,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "oracle": {
        "correct": 12
      },
      "pairFits": 0,
      "maxPairErrorPpm": 0,
      "sumAbsPairErrorPpm": 0,
      "peak": 5648
    },
    "minus05-first-erased": {
      "baseline": {
        "correct": 0,
        "wrong": 0,
        "refused": 12,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "nominal": {
        "correct": 0,
        "wrong": 0,
        "refused": 12,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "affine": {
        "correct": 0,
        "wrong": 0,
        "refused": 12,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "oracle": {
        "correct": 12
      },
      "pairFits": 0,
      "maxPairErrorPpm": 0,
      "sumAbsPairErrorPpm": 0,
      "peak": 4096
    },
    "plus05-second-erased": {
      "baseline": {
        "correct": 1,
        "wrong": 0,
        "refused": 11,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "nominal": {
        "correct": 1,
        "wrong": 0,
        "refused": 11,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "affine": {
        "correct": 1,
        "wrong": 0,
        "refused": 11,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "oracle": {
        "correct": 12
      },
      "pairFits": 0,
      "maxPairErrorPpm": 0,
      "sumAbsPairErrorPpm": 0,
      "peak": 4096
    },
    "prefix-erased-clean": {
      "baseline": {
        "correct": 12,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "nominal": {
        "correct": 12,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "affine": {
        "correct": 12,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "oracle": {
        "correct": 12
      },
      "pairFits": 0,
      "maxPairErrorPpm": 0,
      "sumAbsPairErrorPpm": 0,
      "peak": 4096
    },
    "noise-only": {
      "baseline": {
        "correct": 0,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "nominal": {
        "correct": 0,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "affine": {
        "correct": 0,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "oracle": {},
      "pairFits": 0,
      "maxPairErrorPpm": 0,
      "sumAbsPairErrorPpm": 0,
      "peak": 1559
    },
    "foreign": {
      "baseline": {
        "correct": 0,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquire": 12,
        "falseAccept": 1
      },
      "nominal": {
        "correct": 0,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquire": 12,
        "falseAccept": 1
      },
      "affine": {
        "correct": 0,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquire": 12,
        "falseAccept": 12
      },
      "oracle": {},
      "pairFits": 0,
      "maxPairErrorPpm": 0,
      "sumAbsPairErrorPpm": 0,
      "peak": 4096
    },
    "shifted-marker": {
      "baseline": {
        "correct": 12,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "nominal": {
        "correct": 12,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "affine": {
        "correct": 0,
        "wrong": 0,
        "refused": 12,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "oracle": {
        "correct": 12
      },
      "pairFits": 12,
      "maxPairErrorPpm": 9007,
      "sumAbsPairErrorPpm": 105519,
      "peak": 4096
    },
    "plus20": {
      "baseline": {
        "correct": 0,
        "wrong": 0,
        "refused": 0,
        "missed": 12,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "nominal": {
        "correct": 0,
        "wrong": 0,
        "refused": 0,
        "missed": 12,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "affine": {
        "correct": 0,
        "wrong": 0,
        "refused": 0,
        "missed": 12,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "oracle": {
        "correct": 12
      },
      "pairFits": 0,
      "maxPairErrorPpm": 0,
      "sumAbsPairErrorPpm": 0,
      "peak": 4096
    }
  },
  "specimens": [
    {
      "name": "clean",
      "bytes": 25850
    },
    {
      "name": "minus025",
      "bytes": 25796
    },
    {
      "name": "plus025",
      "bytes": 25904
    },
    {
      "name": "minus05",
      "bytes": 25742
    },
    {
      "name": "plus05",
      "bytes": 25958
    },
    {
      "name": "minus10",
      "bytes": 25632
    },
    {
      "name": "plus10",
      "bytes": 26068
    },
    {
      "name": "minus05-noise",
      "bytes": 25742
    },
    {
      "name": "plus05-noise",
      "bytes": 25958
    },
    {
      "name": "minus05-first-erased",
      "bytes": 25742
    },
    {
      "name": "plus05-second-erased",
      "bytes": 25958
    },
    {
      "name": "prefix-erased-clean",
      "bytes": 25850
    },
    {
      "name": "noise-only",
      "bytes": 25850
    },
    {
      "name": "foreign",
      "bytes": 25958
    },
    {
      "name": "shifted-marker",
      "bytes": 25850
    },
    {
      "name": "plus20",
      "bytes": 26286
    }
  ]
}
*/
