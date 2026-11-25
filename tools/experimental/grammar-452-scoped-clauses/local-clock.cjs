"use strict";
// Grammars lane, Refs #452 / Draft #453. Synthetic experiment only.
// Dependency head 7bff2afe88b38803f996490d4d1dc72209e24217. No protocol changes.
const R=require("./recursive.cjs"),I=require("./integrity.cjs"),D=require("./distributed.cjs"),H=require("./clock-hypotheses.cjs");
const RATE=16000,HALF=5440,MARK=320,BODY=5120,BOUND=480;
const same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const join=(...a)=>{const p=new Int16Array(a.reduce((n,x)=>n+x.length,0));let k=0;for(const x of a){p.set(x,k);k+=x.length;}return p;};
const lerp=(p,t)=>{const j=Math.floor(t),u=t-j;return Math.round((p[j]||0)*(1-u)+(p[j+1]||0)*u);};
const stretch=(p,s)=>Int16Array.from({length:Math.round(p.length*s)},(_,i)=>lerp(p,i/s));
function local(p,x,y,sa,sb){
 if(![sa,sb].every(s=>Number.isFinite(s)&&s>=.98&&s<=1.02))return {status:"refused",reason:"scale-bound"};
 const at=x.at+MARK*sa,bt=y.at+MARK*sb;
 if(at<0||bt<0||at+(BODY-1)*sa>=p.length||bt+(BODY-1)*sb>=p.length)return {status:"truncated"};
 const a=Int16Array.from({length:BODY},(_,i)=>lerp(p,at+i*sa)),b=Int16Array.from({length:BODY},(_,i)=>lerp(p,bt+i*sb));
 const tokens=I.receive(join(a,b));return {tokens,...I.decode(tokens,"protected")};
}
function receive(p){
 const old=H.receive(p),[as,bs]=old.peaks;
 // Deliberately conservative association scope: exactly one marker of each kind.
 // Multiple markers, absent markers or out-of-bound separation use the old receiver.
 if(old.overflow||as.length!==1||bs.length!==1||Math.abs(bs[0].at-as[0].at-HALF)>BOUND)return {old,groups:old.groups,localAttempts:0,reason:"association-not-unique-or-bounded"};
 const [a]=as,[b]=bs;
 const hypotheses=old.groups.flatMap(g=>g.hypotheses);
 const locals=[{name:"local-nominal",...local(p,a,b,1,1)},{name:"local-spectral",...local(p,a,b,a.scale,b.scale)}];
 hypotheses.push(...locals);
 const distinct=new Map();for(const h of hypotheses)if(h.status==="ok")distinct.set(JSON.stringify(h.tree),h.tree);
 const union=distinct.size===1?{status:"ok",tree:[...distinct.values()][0]}:{status:"refused",reason:distinct.size?"semantic-disagreement":"no-valid-interpretation"};
 return {old,groups:[{anchor:a.at,marks:[a,b],hypotheses,union}],localAttempts:2,reason:"bounded-single-pair"};
}
const conditions=[
 ["clean",0,1,1,0,"none"],["gap-minus5",-80,1,1,0,"none"],["gap-minus15",-240,1,1,0,"none"],["gap-minus20",-320,1,1,0,"none"],
 ["gap-plus15",240,1,1,0,"none"],["gap-plus25",400,1,1,0,"none"],["uniform-drift",0,1.01,1.01,0,"none"],
 ["drift-and-gap",240,.995,.995,500,"none"],["piecewise-clock",0,.99,1.01,0,"none"],
 ["marker-only-shift",0,1,1,0,"shift"],["erased-B",0,1,1,0,"erase"],["foreign",0,1,1,0,"foreign"],
 ["noise-only",0,1,1,900,"noise"],["cross-source-splice",0,1,1,0,"splice"],["two-frames",0,1,1,0,"two"]
];
const trees=R.catalog(),book=trees.map(t=>I.encode(t,"protected"));
function spliceWitness(){
 const prefixes=new Map(),suffixes=new Map();
 book.forEach((x,i)=>{for(const [m,k] of [[prefixes,x.slice(0,4).join()],[suffixes,x.slice(4).join()]]){if(!m.has(k))m.set(k,[]);m.get(k).push(i);}});
 for(let c=0;c<book.length;c++){
  const a=prefixes.get(book[c].slice(0,4).join()).find(i=>i!==c),b=suffixes.get(book[c].slice(4).join()).find(i=>i!==c);
  if(a!==undefined&&b!==undefined&&a!==b)return {a,b,c,trees:[trees[a],trees[b],trees[c]],frames:[book[a],book[b],book[c]]};
 }throw Error("no splice witness");
}
const splice=spliceWitness();
function stimulus(name,seed){
 const row=conditions.find(x=>x[0]===name);if(!row)throw Error("condition");
 const [,gap,sa,sb,sigma,fault]=row;
 let state=seed>>>0;const rand=()=>{state=(Math.imul(state,1664525)+1013904223)>>>0;return state/4294967296;};
 const tree=trees[Math.floor(rand()*trees.length)],phase=rand()*Math.PI*2,lead=800+Math.floor(rand()*512);
 let frame=D.packet(tree,"split-either",phase),truth=[{start:lead,tree}],sources=[tree];
 if(fault==="splice"){frame=join(D.packet(splice.trees[0],"split-either",phase).slice(0,HALF),D.packet(splice.trees[1],"split-either",phase).slice(HALF));truth=[];sources=splice.trees.slice(0,2);}
 if(fault==="shift"){const m=frame.slice(HALF,HALF+MARK);frame.fill(0,HALF,HALF+MARK);frame.set(m,HALF+48);}
 if(fault==="erase")frame.fill(0,HALF,HALF+MARK);
 if(fault==="foreign")truth=[];
 if(fault==="noise"){frame.fill(0);truth=[];sources=[];}
 const a=stretch(frame.slice(0,HALF),sa),b=stretch(frame.slice(HALF),sb);
 if(gap<0&&!a.slice(a.length+gap).every(v=>v===0))throw Error("not a silent contraction");
 let body=gap<0?join(a.slice(0,a.length+gap),b):join(a,new Int16Array(gap),b);
 const energy=x=>x.reduce((n,v)=>n+v*v,0);
 const energyPreserved=energy(body)===energy(a)+energy(b);
 if(fault==="two"){const other=trees[(trees.indexOf(tree)+1)%trees.length];truth.push({start:lead+body.length+640,tree:other});sources.push(other);body=join(body,new Int16Array(640),D.packet(other,"split-either",phase));}
 const pcm=join(new Int16Array(lead),body,new Int16Array(1200));
 if(sigma)for(let i=0;i<pcm.length;i++)pcm[i]=Math.round(pcm[i]+(rand()*2-1)*Math.sqrt(3)*sigma);
 return {name,seed,pcm,truth,sources,gap,sa,sb,energyPreserved};
}
function score(s,groups){
 const m={correct:0,wrong:0,refused:0,missed:0,falseAccept:0},used=new Set();
 for(const t of s.truth){const hit=groups.map((g,i)=>({g,i})).filter(v=>!used.has(v.i)&&Math.abs(v.g.anchor-t.start)<=96).sort((a,b)=>Math.abs(a.g.anchor-t.start)-Math.abs(b.g.anchor-t.start))[0];if(!hit){m.missed++;continue;}used.add(hit.i);const d=hit.g.union;m[d.status!=="ok"?"refused":same(d.tree,t.tree)?"correct":"wrong"]++;}
 groups.forEach((g,i)=>{if(!used.has(i)&&g.union.status==="ok")m.falseAccept++;});return m;
}
function qualify(){
 let assertions=0;const check=(x,m)=>{assertions++;if(!x)throw Error(m);};
 const seeds=Array.from({length:6},(_,i)=>(0x392ab71d+Math.imul(i,2654435761))>>>0),metrics={},traces=[];
 check(splice.trees.every((t,i)=>splice.trees.every((u,j)=>i===j||!same(t,u))),"distinct splice trees");
 check(same([...splice.frames[0].slice(0,4),...splice.frames[1].slice(4)],splice.frames[2]),"exact splice frame");
 for(const [name] of conditions){const row={old:{},local:{},attempts:0,disagreements:0,windows:0,peak:0};
 for(const seed of seeds){const s=stimulus(name,seed),o=receive(s.pcm),old=score(s,o.old.groups),now=score(s,o.groups);
  for(const [key,m] of [["old",old],["local",now]]){check(m.correct+m.wrong+m.refused+m.missed===s.truth.length,"truth accounting");for(const [k,v] of Object.entries(m))row[key][k]=(row[key][k]||0)+v;}
  check(s.energyPreserved,"silent gap preserves pre-noise energy");check(s.pcm.every(v=>Math.abs(v)<32768),"peak");
  if(o.localAttempts)for(const g of o.groups){const distinct=new Set(g.hypotheses.filter(h=>h.status==="ok").map(h=>JSON.stringify(h.tree)));check((g.union.status==="ok")===(distinct.size===1),"arbitration");if(distinct.size>1)row.disagreements++;}
  if(name==="cross-source-splice"){check(o.groups.some(g=>g.union.status==="ok"&&same(g.union.tree,splice.trees[2])),"PCM splice third tree");}
  if(name==="two-frames")check(o.localAttempts===0&&same(o.groups,o.old.groups),"multi-frame fallback");
  const w=R.wav(s.pcm),v=new DataView(w.buffer);check(v.getUint32(24,true)===RATE&&v.getUint32(40,true)===2*s.pcm.length,"wav header");
  row.attempts+=o.localAttempts;row.windows+=o.old.windows;for(const v of s.pcm)row.peak=Math.max(row.peak,Math.abs(v));
  traces.push({name,seed,truth:s.truth,sources:s.sources,gap:s.gap,scales:[s.sa,s.sb],old,now,energyPreserved:s.energyPreserved,...o});
 }metrics[name]=row;}
 check(metrics.clean.local.correct===seeds.length,"clean");
 return {schema:"mhac-grammar-local-block-clock-v1",dependency:"7bff2afe88b38803f996490d4d1dc72209e24217",assertions,seeds,conditions,metrics,splice,traces};
}
module.exports={receive,stimulus,score,qualify,spliceWitness};
if(require.main===module){
 const fs=require("node:fs"),path=require("node:path"),crypto=require("node:crypto"),dir=process.argv[2]||"output-local-clock";fs.mkdirSync(dir,{recursive:true});
 const q=qualify(),manifest=[];
 for(const [name] of conditions){const s=stimulus(name,q.seeds[0]),w=R.wav(s.pcm),file=name+".wav";fs.writeFileSync(path.join(dir,file),w);manifest.push({file,seed:s.seed,truth:s.truth,sources:s.sources,sha256:crypto.createHash("sha256").update(w).digest("hex")});}
 fs.writeFileSync(path.join(dir,"qualification.json"),JSON.stringify(q,null,2)+"\n");fs.writeFileSync(path.join(dir,"stimuli.json"),JSON.stringify(manifest,null,2)+"\n");
 console.log(JSON.stringify({assertions:q.assertions,metrics:q.metrics,splice:q.splice},null,2));
}

/*
Grammars Run 008, one GPT-6.2 agent, no subagents. Refs #452 and Draft #453. Prior exact head CI 45576724863 success. Synthetic exploratory extension of pinned receiver, no transmitter changes. Motivated by local timing discontinuity in Adversarial #449 / Integration #513. Nominal and independent spectral reconstruction of two half-bodies, with same GF(17) integrity check and unique-distinct-tree arbitration including previous hypotheses. Only exactly one marker per carrier and separation within 480 samples of nominal qualifies; otherwise fall back to prior receiver. No cross-group source binding claimed. Same PCM for both receivers; no thresholds tuned against these fixtures. Six fresh deterministic seeds per condition; no population inference. Gap removal is verified to remove only silence and preserve energy before added noise; piecewise clocks generated separately. Splice witness deliberately combines halves of two different legal trees and produces a third legal tree; checks do not bind source or message identity. Splice is a constructed counterexample, not an estimated error rate. Multiple-frame fallback is unchanged. Additional work is at most two full body demodulations per eligible observation; no measured runtime or embedded claims. Two identical full V8 qualification receipts, all WAV headers checked. Native Node v22.16.0 available but Git retrieval DNS failure; CLI/filesystem export/hashes/listening not executed. Run node local-clock.cjs output-local-clock for traces and 15 original WAV specimens with SHA-256 manifest. Independent review remains outstanding. No human evidence, no shared or frozen modifications. Executed summary:
{
  "schema": "mhac-grammar-local-block-clock-v1",
  "assertions": 537,
  "seeds": [
    959100701,
    3613536462,
    1973004927,
    332473392,
    2986909153,
    1346377618
  ],
  "metrics": {
    "clean": {
      "old": {
        "correct": 6,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAccept": 0
      },
      "local": {
        "correct": 6,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAccept": 0
      },
      "attempts": 12,
      "disagreements": 0,
      "windows": 9686,
      "peak": 4096
    },
    "gap-minus5": {
      "old": {
        "correct": 6,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAccept": 0
      },
      "local": {
        "correct": 6,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAccept": 0
      },
      "attempts": 12,
      "disagreements": 0,
      "windows": 9626,
      "peak": 4096
    },
    "gap-minus15": {
      "old": {
        "correct": 0,
        "wrong": 0,
        "refused": 6,
        "missed": 0,
        "falseAccept": 0
      },
      "local": {
        "correct": 6,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAccept": 0
      },
      "attempts": 12,
      "disagreements": 0,
      "windows": 9506,
      "peak": 4096
    },
    "gap-minus20": {
      "old": {
        "correct": 0,
        "wrong": 0,
        "refused": 6,
        "missed": 0,
        "falseAccept": 0
      },
      "local": {
        "correct": 6,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAccept": 0
      },
      "attempts": 12,
      "disagreements": 0,
      "windows": 9446,
      "peak": 4096
    },
    "gap-plus15": {
      "old": {
        "correct": 0,
        "wrong": 0,
        "refused": 6,
        "missed": 0,
        "falseAccept": 0
      },
      "local": {
        "correct": 6,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAccept": 0
      },
      "attempts": 12,
      "disagreements": 0,
      "windows": 9866,
      "peak": 4096
    },
    "gap-plus25": {
      "old": {
        "correct": 0,
        "wrong": 0,
        "refused": 6,
        "missed": 0,
        "falseAccept": 0
      },
      "local": {
        "correct": 6,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAccept": 0
      },
      "attempts": 12,
      "disagreements": 0,
      "windows": 9986,
      "peak": 4096
    },
    "uniform-drift": {
      "old": {
        "correct": 6,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAccept": 0
      },
      "local": {
        "correct": 6,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAccept": 0
      },
      "attempts": 12,
      "disagreements": 0,
      "windows": 9768,
      "peak": 4096
    },
    "drift-and-gap": {
      "old": {
        "correct": 0,
        "wrong": 0,
        "refused": 6,
        "missed": 0,
        "falseAccept": 0
      },
      "local": {
        "correct": 6,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAccept": 0
      },
      "attempts": 12,
      "disagreements": 0,
      "windows": 9828,
      "peak": 4940
    },
    "piecewise-clock": {
      "old": {
        "correct": 0,
        "wrong": 0,
        "refused": 6,
        "missed": 0,
        "falseAccept": 0
      },
      "local": {
        "correct": 6,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAccept": 0
      },
      "attempts": 12,
      "disagreements": 0,
      "windows": 9686,
      "peak": 4096
    },
    "marker-only-shift": {
      "old": {
        "correct": 6,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAccept": 0
      },
      "local": {
        "correct": 6,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAccept": 0
      },
      "attempts": 12,
      "disagreements": 0,
      "windows": 9686,
      "peak": 4096
    },
    "erased-B": {
      "old": {
        "correct": 6,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAccept": 0
      },
      "local": {
        "correct": 6,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAccept": 0
      },
      "attempts": 0,
      "disagreements": 0,
      "windows": 9686,
      "peak": 4096
    },
    "foreign": {
      "old": {
        "correct": 0,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAccept": 6
      },
      "local": {
        "correct": 0,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAccept": 6
      },
      "attempts": 12,
      "disagreements": 0,
      "windows": 9686,
      "peak": 4096
    },
    "noise-only": {
      "old": {
        "correct": 0,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAccept": 0
      },
      "local": {
        "correct": 0,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAccept": 0
      },
      "attempts": 0,
      "disagreements": 0,
      "windows": 9686,
      "peak": 1559
    },
    "cross-source-splice": {
      "old": {
        "correct": 0,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAccept": 6
      },
      "local": {
        "correct": 0,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAccept": 6
      },
      "attempts": 12,
      "disagreements": 0,
      "windows": 9686,
      "peak": 4096
    },
    "two-frames": {
      "old": {
        "correct": 12,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAccept": 0
      },
      "local": {
        "correct": 12,
        "wrong": 0,
        "refused": 0,
        "missed": 0,
        "falseAccept": 0
      },
      "attempts": 0,
      "disagreements": 0,
      "windows": 18326,
      "peak": 4096
    }
  },
  "splice": {
    "a": 261,
    "b": 1792,
    "c": 260,
    "trees": [
      [
        "not",
        [
          "not",
          [
            "not",
            [
              "open"
            ]
          ]
        ]
      ],
      [
        "uncertain",
        [
          "relay-reports",
          [
            "uncertain",
            [
              "fault"
            ]
          ]
        ]
      ],
      [
        "not",
        [
          "not",
          [
            "not",
            [
              "fault"
            ]
          ]
        ]
      ]
    ],
    "frames": [
      [
        3,
        4,
        4,
        4,
        1,
        13,
        9,
        13
      ],
      [
        3,
        10,
        9,
        10,
        0,
        13,
        12,
        11
      ],
      [
        3,
        4,
        4,
        4,
        0,
        13,
        12,
        11
      ]
    ]
  }
}
*/
