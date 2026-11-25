"use strict";
// Grammar lane, Refs #452 / #453. Synthetic exploratory code, not a protocol or human evidence.
// Exact dependency head 5a84700b34e4b54ecba908946848b1d552456d47; accepted main 495a98ca12bae467a507031f04931aa4254b1866.
const C=require("./clock.cjs"),R=require("./recursive.cjs");
const RATE=16000,H=320,SEP=5440,F=10880,STEP=16,TOL=96,MAXPEAKS=16;
const eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const taper=Float64Array.from({length:H},(_,i)=>Math.min(1,i/32,(H-1-i)/32));
const norm=taper.reduce((s,v)=>s+v*v,0);
const freqs=[2300,2700],scales=Array.from({length:5},(_,i)=>.98+.01*i);
function template(f,scale){return {scale,c:Float64Array.from({length:H},(_,i)=>taper[i]*Math.cos(2*Math.PI*f*i/(RATE*scale))),s:Float64Array.from({length:H},(_,i)=>taper[i]*Math.sin(2*Math.PI*f*i/(RATE*scale)))};}
const coarse=freqs.map(f=>scales.map(s=>template(f,s)));
const fine=freqs.map(f=>Array.from({length:41},(_,i)=>template(f,.98+.001*i)));
function energy(p,at){let e=0;for(let i=0;i<H;i++)e+=p[at+i]**2;return e;}
function power(p,at,t){let a=0,b=0;const c=t.c,s=t.s;for(let i=0;i<H;i++){const v=p[at+i];a+=v*c[i];b+=v*s[i];}return a*a+b*b;}
function bestBank(p,at,bank){let best=-1,t=null;for(const v of bank){const q=power(p,at,v);if(q>best){best=q;t=v;}}return {power:best,t};}
function refine(p,x,k){let at=x.at,b=bestBank(p,at,fine[k]),best=-1;
 for(let i=Math.max(0,at-24);i<=Math.min(p.length-H,at+24);i++){const v=power(p,i,b.t);if(v>best){best=v;x={at:i};}}
 at=x.at;b=bestBank(p,at,fine[k]);
 const j=fine[k].indexOf(b.t);let scale=b.t.scale;
 if(j>0&&j<fine[k].length-1){const l=power(p,at,fine[k][j-1]),r=power(p,at,fine[k][j+1]),den=l-2*b.power+r;if(den<0)scale+=.001*Math.max(-.5,Math.min(.5,.5*(l-r)/den));}
 return {at,scale,q:2*b.power/(norm*energy(p,at))};
}
function acquire(p){
 if(!(p instanceof Int16Array)||p.length>RATE*20)throw Error("input bound");
 let windows=0;const peaks=[[],[]];
 for(let k=0;k<2;k++){const all=[];for(let at=0;at+H<=p.length;at+=STEP){windows++;const e=energy(p,at);if(e<H*250**2)continue;const b=bestBank(p,at,coarse[k]),q=2*b.power/(norm*e);if(q>=.52)all.push({at,q});}
 all.sort((a,b)=>b.q-a.q||a.at-b.at);for(const x of all){if(!peaks[k].some(y=>Math.abs(x.at-y.at)<H)){peaks[k].push(refine(p,x,k));if(peaks[k].length>MAXPEAKS)return {peaks,windows,overflow:true};}}}
 return {peaks,windows,overflow:false};
}
function receive(p){
 const a=acquire(p),groups=[],used=new Set();
 if(a.overflow)return {...a,groups};
 for(const x of a.peaks[0]){
  const b=a.peaks[1].map((y,i)=>({y,i,delta:Math.abs((y.at-x.at)-SEP*(x.scale+y.scale)/2)})).filter(v=>!used.has(v.i)&&Math.abs(v.y.at-x.at-SEP)<=130).sort((x,y)=>x.delta-y.delta)[0];
  if(b)used.add(b.i);groups.push([x,b?.y??null]);
 }
 a.peaks[1].forEach((y,i)=>{if(!used.has(i))groups.push([null,y]);});
 const out=groups.map(([x,y])=>{
  const anchor=x?x.at:y.at-SEP*y.scale;
  const hypotheses=[];
  function add(name,start,scale){const d=C.frame(p,start,scale);hypotheses.push({name,start,scale,...d});return d;}
  const pair=x&&y?(y.at-x.at)/SEP:null;
  const pairResult=pair!==null?add("pair",x.at,pair):add("single-nominal",x?x.at:y.at-SEP,1);
  if(x){add("A-nominal",x.at,1);add("A-spectral",x.at,x.scale);}
  if(y){add("B-nominal",y.at-SEP,1);add("B-spectral",y.at-SEP*y.scale,y.scale);}
  if(x&&y)add("nominal-average",(x.at+y.at-SEP)/2,1);
  const distinct=new Map();for(const h of hypotheses)if(h.status==="ok")distinct.set(JSON.stringify(h.tree),h.tree);
  const union=distinct.size===1?{status:"ok",tree:[...distinct.values()][0]}:{status:"refused",reason:distinct.size?"semantic-disagreement":"no-valid-interpretation"};
  return {anchor,marks:[x,y],pairScale:pair,pairResult,union,hypotheses};
 });
 return {...a,groups:out};
}
function classify(s,groups,key){
 const m={correct:0,wrong:0,refused:0,missed:0,falseAcquire:0,falseAccept:0};
 const hit=s.truth?groups.map((g,i)=>({g,i})).filter(v=>Math.abs(v.g.anchor-s.truth.start)<=TOL).sort((a,b)=>Math.abs(a.g.anchor-s.truth.start)-Math.abs(b.g.anchor-s.truth.start))[0]:null;
 if(s.truth){if(!hit)m.missed++;else{const d=hit.g[key];m[d.status!=="ok"?"refused":eq(d.tree,s.truth.tree)?"correct":"wrong"]++;}}
 groups.forEach((g,i)=>{if(i!==hit?.i){m.falseAcquire++;if(g[key].status==="ok")m.falseAccept++;}});return m;
}
function qualify(){
 let assertions=0;const check=(v,msg)=>{assertions++;if(!v)throw Error(msg);};
 // Fixed design constants, no calibration or tuning against these fixtures.
 const seeds=Array.from({length:8},(_,i)=>(0x6ca82971+Math.imul(i,2246822519))>>>0);
 const metrics={},traces=[],specimens=[];
 for(const [name] of C.conditions){const row={old:{},bankPair:{},union:{},oracle:{},overflow:0,disagreements:0,windows:0,peak:0};
  for(const seed of seeds){const s=C.stimulus(name,seed),prior=C.evaluate(s),o=receive(s.pcm),pair=classify(s,o.groups,"pairResult"),union=classify(s,o.groups,"union");
   for(const [key,m] of [["old",prior.metrics.affine],["bankPair",pair],["union",union]]){check(m.correct+m.wrong+m.refused+m.missed===(s.truth?1:0),"accounting");for(const [k,v] of Object.entries(m))row[key][k]=(row[key][k]||0)+v;}
   for(const g of o.groups){const valid=g.hypotheses.filter(h=>h.status==="ok");const count=new Set(valid.map(h=>JSON.stringify(h.tree))).size;check((g.union.status==="ok")===(count===1),"union acceptance invariant");if(count>1)row.disagreements++;}
   if(prior.oracle)row.oracle[prior.oracle]=(row.oracle[prior.oracle]||0)+1;
   row.overflow+=Number(o.overflow);row.windows+=o.windows;row.peak=Math.max(row.peak,prior.peak);
   check(prior.peak<32768,"peak");
   traces.push({name,seed,truth:s.truth,scale:s.scale,old:prior.metrics.affine,oracle:prior.oracle,pair,union,...o});
   if(seed===seeds[0]){const b=R.wav(s.pcm);const v=new DataView(b.buffer);check(v.getUint32(24,true)===RATE&&v.getUint32(40,true)===s.pcm.length*2,"WAV header");specimens.push({name,bytes:b.length,seed});}
  }metrics[name]=row;
 }
 check(metrics.clean.union.correct===seeds.length,"clean union");
 return {schema:"mhac-grammar-clock-hypotheses-v1",dependency:"5a84700b34e4b54ecba908946848b1d552456d47",assertions,seeds,conditions:C.conditions,metrics,traces,specimens};
}
module.exports={acquire,receive,classify,qualify};
if(require.main===module){
 const fs=require("node:fs"),path=require("node:path"),crypto=require("node:crypto"),dir=process.argv[2]||"output-clock-hypotheses";fs.mkdirSync(dir,{recursive:true});const q=qualify(),manifest=[];
 for(const {name,seed} of q.specimens){const s=C.stimulus(name,seed),wav=R.wav(s.pcm),file=name+".wav";fs.writeFileSync(path.join(dir,file),wav);manifest.push({file,name,seed,truth:s.truth,scale:s.scale,sha256:crypto.createHash("sha256").update(wav).digest("hex")});}
 fs.writeFileSync(path.join(dir,"qualification.json"),JSON.stringify(q,null,2)+"\n");fs.writeFileSync(path.join(dir,"stimuli.json"),JSON.stringify(manifest,null,2)+"\n");
 console.log(JSON.stringify({assertions:q.assertions,metrics:q.metrics},null,2));
}

/*
Grammars Run 007. One GPT-6.2 agent, no subagents. Live main and #452 issue/comments reconciled, previous exact-head CI 45568108965 passed. Additive experimental apparatus; no shared changes. Coarse five-rate tapered quadrature bank, 41-rate refinement (0.001 scale grid with local parabolic interpolation), fixed 0.52 approximate projection score and 250-count RMS floor. At most 16 peaks per carrier, overflow abstention. Frame length/energy unchanged, same protected GF(17) decoder. Pair matching bounded to +/-130 samples of nominal separation. Union tests nominal, spectral and separation-derived timing and accepts only a unique distinct grammar tree; not a source identity check. Same finite 16 conditions as clock.cjs but eight fresh paired seeds. No threshold calibration or population generalization claimed. Prior affine receiver evaluated on identical waveforms; privileged oracle only on intended frames. V8 two identical executions, 16 original WAV byte arrays and headers checked; native CLI, file hashes and audition not executed. Run node clock-hypotheses.cjs output-clock-hypotheses for full traces, WAVs and SHA-256 manifest. Dot products approximate quadrature energy; no wall-clock or embedded runtime claims, no overlapping multi-frame qualification. Taper normalization uses approximate orthogonality. Distinct valid trees cause refusal; a single wrong valid tree may pass. No human evidence. Draft/HOLD independent review. Executed summary:
{
  "schema": "mhac-grammar-clock-hypotheses-v1",
  "dependency": "5a84700b34e4b54ecba908946848b1d552456d47",
  "assertions": 649,
  "seeds": [
    1822959985,
    4069782504,
    2021637727,
    4268460246,
    2220315469,
    172170692,
    2418993211,
    370848434
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
      "old": {
        "correct": 8,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "bankPair": {
        "correct": 8,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "union": {
        "correct": 8,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "oracle": {
        "correct": 8
      },
      "overflow": 0,
      "disagreements": 0,
      "windows": 12834,
      "peak": 4096
    },
    "minus025": {
      "old": {
        "correct": 8,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "bankPair": {
        "correct": 8,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "union": {
        "correct": 8,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "oracle": {
        "correct": 8
      },
      "overflow": 0,
      "disagreements": 0,
      "windows": 12812,
      "peak": 4095
    },
    "plus025": {
      "old": {
        "correct": 8,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "bankPair": {
        "correct": 8,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "union": {
        "correct": 8,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "oracle": {
        "correct": 8
      },
      "overflow": 0,
      "disagreements": 0,
      "windows": 12864,
      "peak": 4095
    },
    "minus05": {
      "old": {
        "correct": 8,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "bankPair": {
        "correct": 8,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "union": {
        "correct": 8,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "oracle": {
        "correct": 8
      },
      "overflow": 0,
      "disagreements": 0,
      "windows": 12782,
      "peak": 4094
    },
    "plus05": {
      "old": {
        "correct": 8,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "bankPair": {
        "correct": 8,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "union": {
        "correct": 8,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "oracle": {
        "correct": 8
      },
      "overflow": 0,
      "disagreements": 0,
      "windows": 12892,
      "peak": 4094
    },
    "minus10": {
      "old": {
        "correct": 0,
        "wrong": 0,
        "refused": 0,
        "missed": 8,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "bankPair": {
        "correct": 8,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "union": {
        "correct": 8,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "oracle": {
        "correct": 8
      },
      "overflow": 0,
      "disagreements": 0,
      "windows": 12726,
      "peak": 4095
    },
    "plus10": {
      "old": {
        "correct": 0,
        "wrong": 0,
        "refused": 0,
        "missed": 8,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "bankPair": {
        "correct": 8,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "union": {
        "correct": 8,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "oracle": {
        "correct": 8
      },
      "overflow": 0,
      "disagreements": 0,
      "windows": 12946,
      "peak": 4095
    },
    "minus05-noise": {
      "old": {
        "correct": 0,
        "wrong": 0,
        "refused": 5,
        "missed": 3,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "bankPair": {
        "correct": 8,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "union": {
        "correct": 8,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "oracle": {
        "correct": 8
      },
      "overflow": 0,
      "disagreements": 0,
      "windows": 12782,
      "peak": 5640
    },
    "plus05-noise": {
      "old": {
        "correct": 0,
        "wrong": 0,
        "refused": 4,
        "missed": 4,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "bankPair": {
        "correct": 8,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "union": {
        "correct": 8,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "oracle": {
        "correct": 8
      },
      "overflow": 0,
      "disagreements": 0,
      "windows": 12892,
      "peak": 5642
    },
    "minus05-first-erased": {
      "old": {
        "correct": 1,
        "wrong": 0,
        "refused": 7,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "bankPair": {
        "correct": 1,
        "wrong": 0,
        "refused": 7,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "union": {
        "correct": 8,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "oracle": {
        "correct": 8
      },
      "overflow": 0,
      "disagreements": 0,
      "windows": 12782,
      "peak": 4094
    },
    "plus05-second-erased": {
      "old": {
        "correct": 2,
        "wrong": 0,
        "refused": 6,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "bankPair": {
        "correct": 2,
        "wrong": 0,
        "refused": 6,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "union": {
        "correct": 8,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "oracle": {
        "correct": 8
      },
      "overflow": 0,
      "disagreements": 0,
      "windows": 12892,
      "peak": 4094
    },
    "prefix-erased-clean": {
      "old": {
        "correct": 8,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "bankPair": {
        "correct": 8,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "union": {
        "correct": 8,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "oracle": {
        "correct": 8
      },
      "overflow": 0,
      "disagreements": 0,
      "windows": 12834,
      "peak": 4096
    },
    "noise-only": {
      "old": {
        "correct": 0,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "bankPair": {
        "correct": 0,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "union": {
        "correct": 0,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "oracle": {},
      "overflow": 0,
      "disagreements": 0,
      "windows": 12834,
      "peak": 1559
    },
    "foreign": {
      "old": {
        "correct": 0,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquire": 8,
        "falseAccept": 8
      },
      "bankPair": {
        "correct": 0,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquire": 8,
        "falseAccept": 8
      },
      "union": {
        "correct": 0,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquire": 8,
        "falseAccept": 8
      },
      "oracle": {},
      "overflow": 0,
      "disagreements": 0,
      "windows": 12892,
      "peak": 4094
    },
    "shifted-marker": {
      "old": {
        "correct": 0,
        "wrong": 0,
        "refused": 8,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "bankPair": {
        "correct": 0,
        "wrong": 0,
        "refused": 8,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "union": {
        "correct": 8,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "oracle": {
        "correct": 8
      },
      "overflow": 0,
      "disagreements": 0,
      "windows": 12834,
      "peak": 4096
    },
    "plus20": {
      "old": {
        "correct": 0,
        "wrong": 0,
        "refused": 0,
        "missed": 8,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "bankPair": {
        "correct": 8,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "union": {
        "correct": 8,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAcquire": 0,
        "falseAccept": 0
      },
      "oracle": {
        "correct": 8
      },
      "overflow": 0,
      "disagreements": 0,
      "windows": 13054,
      "peak": 4096
    }
  },
  "specimens": [
    {
      "name": "clean",
      "bytes": 26438,
      "seed": 1822959985
    },
    {
      "name": "minus025",
      "bytes": 26384,
      "seed": 1822959985
    },
    {
      "name": "plus025",
      "bytes": 26492,
      "seed": 1822959985
    },
    {
      "name": "minus05",
      "bytes": 26330,
      "seed": 1822959985
    },
    {
      "name": "plus05",
      "bytes": 26546,
      "seed": 1822959985
    },
    {
      "name": "minus10",
      "bytes": 26220,
      "seed": 1822959985
    },
    {
      "name": "plus10",
      "bytes": 26656,
      "seed": 1822959985
    },
    {
      "name": "minus05-noise",
      "bytes": 26330,
      "seed": 1822959985
    },
    {
      "name": "plus05-noise",
      "bytes": 26546,
      "seed": 1822959985
    },
    {
      "name": "minus05-first-erased",
      "bytes": 26330,
      "seed": 1822959985
    },
    {
      "name": "plus05-second-erased",
      "bytes": 26546,
      "seed": 1822959985
    },
    {
      "name": "prefix-erased-clean",
      "bytes": 26438,
      "seed": 1822959985
    },
    {
      "name": "noise-only",
      "bytes": 26438,
      "seed": 1822959985
    },
    {
      "name": "foreign",
      "bytes": 26546,
      "seed": 1822959985
    },
    {
      "name": "shifted-marker",
      "bytes": 26438,
      "seed": 1822959985
    },
    {
      "name": "plus20",
      "bytes": 26874,
      "seed": 1822959985
    }
  ]
}
*/
