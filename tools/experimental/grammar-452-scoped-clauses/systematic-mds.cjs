"use strict";
// Refs #452 / Grammars lane. Synthetic aligned acoustic bodies only.
const A=require("./algebraic-binding.cjs"), I=require("./integrity.cjs"), R=require("./recursive.cjs");
const parent="7186c0d3a66960c789fb70f70d315c20033f483c";
const pinnedBlobs={"algebraic-binding.cjs":"7415235429fd86aa96bde3f69bcfe10cf5eb8fa2","recursive.cjs":"7d9e305857b59e029913432bb40f713ab84b5a90","integrity.cjs":"a58403f51806c17d89c7ebaf098d2e19b0995a02","injective-tags.cjs":"d91e0ed1e8700ff78b12e7732c07ddfcfc189e08","block-binding.cjs":"4c8be6987b345a5084dee16cf9e7053726c034c9","clock-hypotheses.cjs":"45a5fafb6506ba9211970c1cd58ac2840fbfc670","clock.cjs":"49a6849ae8a0094d30d499718ce21dd3029c0f8a","distributed.cjs":"c727fe13c7131e9a5eac9240fa909c34bcc5011c","acquisition.cjs":"70fb9823d596300112282a73386d6c6088b5d793","local-clock.cjs":"18e86536a85a7327499be1d5ff5719518d1a696a"};
const mod=x=>(x%17+17)%17;
const equal=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const key=x=>x.reduce((s,v)=>17*s+v,0);
const slots=[0,1,4,5], all=[0,1,2,3,4,5,6,7];
const inverse=x=>{for(let j=1;j<17;j++)if(mod(x*j)===1)return j;throw Error("zero inverse");};
function weights(from,to){
  return to.map(z=>from.map(i=>from.reduce((p,j)=>j===i?p:mod(p*(z-j)*inverse(mod(i-j))),1)));
}
const apply=(w,y)=>w.map(row=>mod(row.reduce((s,v,i)=>s+v*y[i],0)));
const generator=weights(slots,all);
function encode(x){
  if(!Array.isArray(x)||x.length!==4||x.some(v=>!Number.isInteger(v)||v<0||v>16))throw Error("four GF17 symbols required");
  return apply(generator,x);
}
const fourSets=[];
for(let a=0;a<8;a++)for(let b=a+1;b<8;b++)for(let c=b+1;c<8;c++)for(let d=c+1;d<8;d++)fourSets.push([a,b,c,d]);
const inverses=new Map(fourSets.map(s=>[s.join(","),weights(s,slots)]));
function build(rows){
  const map=new Map(rows.map(x=>[key(x),x]));
  if(map.size!==rows.length)throw Error("duplicate meaning");
  return {rows,map,book:rows.map(encode)};
}
function reconstruct(input,indices){
  return apply(inverses.get(indices.join(",")),indices.map(i=>input[i]));
}
// Strict decoder: no silent correction of contradictory observed symbols.
function decode(input,codec,correctOne=false){
  if(!Array.isArray(input)||input.length!==8||input.some(v=>v!==null&&(!Number.isInteger(v)||v<0||v>16)))return null;
  const seen=all.filter(i=>input[i]!==null);
  if(seen.length<4)return null;
  const e=8-seen.length;
  const radius=correctOne&&e<=2?1:0;
  const possible=new Set();
  const candidates=[seen.slice(0,4)];
  if(radius)for(const i of seen)candidates.push(seen.filter(j=>j!==i).slice(0,4));
  for(const s of candidates){
    const x=reconstruct(input,s), k=key(x);
    if(!codec.map.has(k))continue;
    const y=encode(x);
    if(seen.filter(i=>input[i]!==y[i]).length<=radius)possible.add(k);
  }
  return possible.size===1?[...possible][0]:null;
}
const masks=Array.from({length:256},(_,b)=>all.filter(i=>b&(1<<i))).filter(m=>m.length<=4);
const erase=(x,mask)=>x.map((v,i)=>mask.includes(i)?null:v);
function census(book,mask){
  const L=new Map(),Q=new Map(),p=[],q=[],full=new Set();
  const left=all.slice(0,4).filter(i=>!mask.includes(i)),right=all.slice(4).filter(i=>!mask.includes(i));
  for(let i=0;i<book.length;i++){
    p[i]=key(left.map(j=>book[i][j]));q[i]=key(right.map(j=>book[i][j]));
    for(const [m,k] of [[L,p[i]],[Q,q[i]]]){let a=m.get(k);if(!a)m.set(k,a=[]);a.push(i);}
    full.add(p[i]+":"+q[i]);
  }
  if(full.size!==book.length)throw Error("nonunique projection");
  let asA=0,asB=0,third=0,witness=null;
  for(let i=0;i<book.length;i++){
    const l=L.get(p[i]),r=Q.get(q[i]);
    asA+=r.length-1;asB+=l.length-1;third+=(l.length-1)*(r.length-1);
    if(!witness&&l.length>1&&r.length>1)witness={a:l.find(j=>j!==i),b:r.find(j=>j!==i),c:i,mask};
  }
  return {mask,asA,asB,third,witness};
}
function splice(book,w){return erase([...book[w.a].slice(0,4),...book[w.b].slice(4)],w.mask);}
function aggregate(rows){return Array.from({length:1+Math.max(...rows.map(r=>r.mask.length))},(_,e)=>{
  const a=rows.filter(r=>r.mask.length===e);
  return {erasures:e,patterns:a.length,asA:a.reduce((s,r)=>s+r.asA,0),asB:a.reduce((s,r)=>s+r.asB,0),third:a.reduce((s,r)=>s+r.third,0),witness:a.find(r=>r.witness)?.witness??null};
});}
function qualify(){
  let assertions=0;const check=(ok,why)=>{assertions++;if(!ok)throw Error(why);};
  // Each four-slot inverse verified on the four basis vectors: linearity extends to the entire field.
  for(const s of fourSets)for(let j=0;j<4;j++){
    const x=slots.map((_,i)=>+(i===j)),y=encode(x);
    check(equal(reconstruct(y,s),x),"four-position inverse");
    check(equal(slots.map(i=>y[i]),x),"systematic positions");
  }
  const original=build(A.versions.original),extended=build(A.versions.append);
  const reversed=build(A.versions.reverse),expandedPrepend=build(A.versions.prepend);
  const old={algebraic:A.build(A.versions.original,"algebraic"),greedy:A.build(A.versions.original,"greedy"),rank:A.build(A.versions.original,"rank")};
  const metrics={};
  for(const [name,codec] of Object.entries({...old,mds:original,mdsExpanded:extended})){
    const mds=name.startsWith("mds"), rows=masks.filter(m=>mds||m.length<=2).map(mask=>census(codec.book,mask));
    for(const row of rows)if(row.witness){
      const w=row.witness,input=splice(codec.book,w);
      check((mds?decode(input,codec):A.decode(input,codec))===key(codec.rows[w.c]),"splice witness");
    }
    metrics[name]=aggregate(rows);
  }
  check(metrics.algebraic[2].third===140166,"prior algebraic exact census");
  check(metrics.greedy[2].third===56394,"prior greedy exact census");
  check(metrics.rank[2].third===0,"prior rank exact census");
  // Independent direct enumeration of every distinct ordered pair for one two-erasure mask.
  const mask=[0,4], projected=new Map(original.book.map((v,i)=>[key(v.filter((_,j)=>!mask.includes(j))),i]));
  let asA=0,asB=0,third=0;
  const left=original.book.map(y=>key(y.slice(1,4))),right=original.book.map(y=>key(y.slice(5,8)));
  for(let a=0;a<left.length;a++)for(let b=0;b<right.length;b++)if(a!==b){
    const c=projected.get(left[a]*4913+right[b]);
    if(c!==undefined){if(c===a)asA++;else if(c===b)asB++;else third++;}
  }
  const direct={asA,asB,third};
  const analytic=census(original.book,mask);
  check(equal(direct,{asA:analytic.asA,asB:analytic.asB,third:analytic.third}),"independent pair enumeration");
  const erasures=[0,0,0,0,0],unknown=[0,0,0,0,0],shared=[0,0,0,0,0];
  for(let i=0;i<extended.rows.length;i++){
    const x=extended.rows[i],y=extended.book[i],k=key(x),known=original.map.has(k);
    for(const m of masks){
      const input=erase(y,m);
      check(decode(input,expandedPrepend)===k,"expanded reordered recovery");
      erasures[m.length]++;
      if(known){
        check(decode(input,reversed)===k,"original reordered recovery");
        shared[m.length]++;
      }else{
        check(decode(input,original)===null,"unknown vocabulary refusal");
        unknown[m.length]++;
      }
    }
  }
  // Fixed stratified deterministic fixtures; not an exhaustive error census.
  const corruption={strict:{correct:0,wrong:0,refused:0},correctOne:{correct:0,wrong:0,refused:0},cases:0};
  for(let i=0;i<original.rows.length;i+=37)for(const m of masks.filter(m=>m.length<=2)){
    const y=original.book[i],k=key(original.rows[i]);
    for(const j of all.filter(j=>!m.includes(j))){
      const input=erase(y,m);input[j]=mod(input[j]+1+(i+j)%16);
      for(const [name,flag] of [["strict",false],["correctOne",true]]){
        const got=decode(input,original,flag);
        corruption[name][got===null?"refused":got===k?"correct":"wrong"]++;
        check(got===(flag?k:null),"bounded one substitution");
      }
      corruption.cases++;
    }
  }
  // Refuse malformed/under-observed input, even with correction enabled.
  check(decode([null,null,null,null,null,0,0,0],original,true)===null,"underobserved");
  check(decode([0,0,0,0,0,0,0,17],original,true)===null,"out of field");
  const specimens=[],traces=[];let peak=0;
  const cases=[{name:"mds-clean",input:original.book[309],codec:original,expect:key(original.rows[309])},
    {name:"mds-four-erasure",input:erase(original.book[309],[0,2,4,6]),codec:original,expect:key(original.rows[309])},
    {name:"mds-new-vocabulary",input:extended.book[2304],codec:original,expect:null}];
  const corrupt=erase(original.book[309],[0,4]);corrupt[2]=mod(corrupt[2]+1);
  cases.push({name:"mds-two-erasure-one-error",input:corrupt,codec:original,expect:null,corrected:key(original.rows[309])});
  for(const e of [2,3,4]){
    const w=metrics.mds[e].witness;if(w)cases.push({name:"mds-splice-"+e,input:splice(original.book,w),codec:original,expect:key(original.rows[w.c]),witness:w});
  }
  const oldW=metrics.algebraic[2].witness;
  cases.push({name:"algebraic-two-erasure-splice",input:splice(old.algebraic.book,oldW),codec:old.algebraic,expect:key(old.algebraic.rows[oldW.c]),legacy:true,witness:oldW});
  for(const c of cases)for(const phase of [.137,2.419,5.827]){
    const pcm=I.render(c.input,phase),tokens=I.receive(pcm);
    check(equal(tokens,c.input),"aligned PCM tokens");
    const got=c.legacy?A.decode(tokens,c.codec):decode(tokens,c.codec);
    check(got===c.expect,"aligned PCM semantic");
    if(c.corrected!==undefined)check(decode(tokens,c.codec,true)===c.corrected,"PCM correction");
    let energy=0;for(const v of pcm){peak=Math.max(peak,Math.abs(v));energy+=v*v;}
    const wav=R.wav(pcm),view=new DataView(wav.buffer,wav.byteOffset,wav.byteLength);
    check(view.getUint32(24,true)===16000&&view.getUint32(40,true)===pcm.length*2,"WAV");
    const t={case:c.name,phase,tokens,got,expected:c.expect,energy,witness:c.witness??null,corrected:c.corrected??null};
    traces.push(t);
    if(phase===.137)specimens.push({...t,name:c.name+".wav"});
  }
  check(peak<=4096,"digital peak");
  return {schema:"mhac-systematic-mds-v1",parent,pinnedBlobs,assertions,generator,fourSlotInverses:fourSets.length,catalog:{original:original.rows.length,expanded:extended.rows.length},metrics,independentPairCensus:{mask,...direct},erasures,shared,unknown,corruption,traces,specimens,peak};
}
module.exports={encode,build,decode,qualify,census,generator};
if(require.main===module){
  const fs=require("node:fs"),path=require("node:path"),crypto=require("node:crypto");
  for(const [n,expected] of Object.entries(pinnedBlobs)){
    const bytes=fs.readFileSync(path.join(__dirname,n));
    const actual=crypto.createHash("sha1").update("blob "+bytes.length+"\0").update(bytes).digest("hex");
    if(actual!==expected)throw Error("pinned dependency changed: "+n);
  }
  const out=process.argv[2]||"output-systematic-mds";fs.mkdirSync(out,{recursive:true});
  const q=qualify(),manifest=[];
  for(const s of q.specimens){
    const wav=R.wav(I.render(s.tokens,s.phase));fs.writeFileSync(path.join(out,s.name),wav);
    manifest.push({...s,sha256:crypto.createHash("sha256").update(wav).digest("hex")});
  }
  fs.writeFileSync(path.join(out,"qualification.json"),JSON.stringify(q,null,2)+"\n");
  fs.writeFileSync(path.join(out,"stimuli.json"),JSON.stringify(manifest,null,2)+"\n");
  fs.writeFileSync(path.join(out,"index.html"),'<!doctype html><meta charset="utf-8"><title>Systematic MDS grammar</title><h1>Aligned synthetic acoustic specimens</h1><p>Start at low volume. No autoplay. These are machine-code examples, not human evidence.</p>'+manifest.map(s=>'<h2>'+s.case+'</h2><audio controls preload="none" src="'+s.name+'"></audio><pre>'+JSON.stringify({tokens:s.tokens,decoded:s.got,witness:s.witness,sha256:s.sha256},null,2)+'</pre>').join(""));
  console.log(JSON.stringify({assertions:q.assertions,catalog:q.catalog,metrics:q.metrics,corruption:q.corruption,peak:q.peak},null,2));
}

/*
Run 012, 2026-11-25, Refs #452 / Draft #453. Accepted main 495a98ca12bae467a507031f04931aa4254b1866; previous head 7186c0d3a66960c789fb70f70d315c20033f483c; prior exact-head workflow 45613109243 success. One GPT-6.2 agent, no subagents. New systematic polynomial evaluation code over GF(17), evaluation positions 0..7, data at 0,1,4,5. Nonzero polynomial degree <=3 has at most three roots: distance >=5, any four observed positions invertible, two erasures plus one substitution correctable under a bounded single-source corruption model. Membership is mandatory. Strict decoding is default; correction may conceal splices, is not source authentication, and has not received a splice census. The 796 new expressions were not used to choose the code. Census counts ordered distinct source pairs times erasure masks, not physical probabilities. Same eight 80ms tones, aligned 640ms body only; nominal framed acquisition not requalified. Equal nominal amplitude/airtime and alphabet, exact PCM energy varies slightly by tone. Native Node v22.16.0 available but GitHub DNS failed, exit 128; actual pinned dependencies and this file executed twice in V8 with identical full receipts. Native CLI, filesystem, browser, SHA manifest and physical audition not executed. The CLI verifies dependency git-blob hashes, exports original WAVs, qualification JSON and a simple offline gallery. No human evidence, no canonical edits, no merge. Executed summary:
{
  "schema": "mhac-systematic-mds-v1",
  "parent": "7186c0d3a66960c789fb70f70d315c20033f483c",
  "pinnedBlobs": {
    "algebraic-binding.cjs": "7415235429fd86aa96bde3f69bcfe10cf5eb8fa2",
    "recursive.cjs": "7d9e305857b59e029913432bb40f713ab84b5a90",
    "integrity.cjs": "a58403f51806c17d89c7ebaf098d2e19b0995a02",
    "injective-tags.cjs": "d91e0ed1e8700ff78b12e7732c07ddfcfc189e08",
    "block-binding.cjs": "4c8be6987b345a5084dee16cf9e7053726c034c9",
    "clock-hypotheses.cjs": "45a5fafb6506ba9211970c1cd58ac2840fbfc670",
    "clock.cjs": "49a6849ae8a0094d30d499718ce21dd3029c0f8a",
    "distributed.cjs": "c727fe13c7131e9a5eac9240fa909c34bcc5011c",
    "acquisition.cjs": "70fb9823d596300112282a73386d6c6088b5d793",
    "local-clock.cjs": "18e86536a85a7327499be1d5ff5719518d1a696a"
  },
  "assertions": 1040770,
  "generator": [
    [
      1,
      0,
      0,
      0
    ],
    [
      0,
      1,
      0,
      0
    ],
    [
      15,
      1,
      9,
      10
    ],
    [
      10,
      9,
      1,
      15
    ],
    [
      0,
      0,
      1,
      0
    ],
    [
      0,
      0,
      0,
      1
    ],
    [
      8,
      1,
      6,
      3
    ],
    [
      5,
      12,
      10,
      8
    ]
  ],
  "fourSlotInverses": 70,
  "catalog": {
    "original": 2304,
    "expanded": 3100
  },
  "metrics": {
    "algebraic": [
      {
        "erasures": 0,
        "patterns": 1,
        "asA": 0,
        "asB": 0,
        "third": 0,
        "witness": null
      },
      {
        "erasures": 1,
        "patterns": 8,
        "asA": 26538,
        "asB": 11854,
        "third": 0,
        "witness": null
      },
      {
        "erasures": 2,
        "patterns": 28,
        "asA": 479852,
        "asB": 291656,
        "third": 140166,
        "witness": {
          "a": 260,
          "b": 71,
          "c": 90,
          "mask": [
            0,
            4
          ]
        }
      }
    ],
    "greedy": [
      {
        "erasures": 0,
        "patterns": 1,
        "asA": 0,
        "asB": 0,
        "third": 0,
        "witness": null
      },
      {
        "erasures": 1,
        "patterns": 8,
        "asA": 17528,
        "asB": 7192,
        "third": 0,
        "witness": null
      },
      {
        "erasures": 2,
        "patterns": 28,
        "asA": 384336,
        "asB": 230318,
        "third": 56394,
        "witness": {
          "a": 1998,
          "b": 43,
          "c": 9,
          "mask": [
            0,
            4
          ]
        }
      }
    ],
    "rank": [
      {
        "erasures": 0,
        "patterns": 1,
        "asA": 0,
        "asB": 0,
        "third": 0,
        "witness": null
      },
      {
        "erasures": 1,
        "patterns": 8,
        "asA": 0,
        "asB": 0,
        "third": 0,
        "witness": null
      },
      {
        "erasures": 2,
        "patterns": 28,
        "asA": 158480,
        "asB": 158480,
        "third": 0,
        "witness": null
      }
    ],
    "mds": [
      {
        "erasures": 0,
        "patterns": 1,
        "asA": 0,
        "asB": 0,
        "third": 0,
        "witness": null
      },
      {
        "erasures": 1,
        "patterns": 8,
        "asA": 16924,
        "asB": 8410,
        "third": 0,
        "witness": null
      },
      {
        "erasures": 2,
        "patterns": 28,
        "asA": 381644,
        "asB": 234964,
        "third": 65005,
        "witness": {
          "a": 1950,
          "b": 202,
          "c": 7,
          "mask": [
            0,
            4
          ]
        }
      },
      {
        "erasures": 3,
        "patterns": 56,
        "asA": 3564750,
        "asB": 2563900,
        "third": 2700035,
        "witness": {
          "a": 461,
          "b": 48,
          "c": 0,
          "mask": [
            0,
            1,
            4
          ]
        }
      },
      {
        "erasures": 4,
        "patterns": 70,
        "asA": 16087152,
        "asB": 13380272,
        "third": 48610583,
        "witness": {
          "a": 5,
          "b": 48,
          "c": 0,
          "mask": [
            0,
            1,
            2,
            4
          ]
        }
      }
    ],
    "mdsExpanded": [
      {
        "erasures": 0,
        "patterns": 1,
        "asA": 0,
        "asB": 0,
        "third": 0,
        "witness": null
      },
      {
        "erasures": 1,
        "patterns": 8,
        "asA": 24030,
        "asB": 14772,
        "third": 0,
        "witness": null
      },
      {
        "erasures": 2,
        "patterns": 28,
        "asA": 565908,
        "asB": 416610,
        "third": 117614,
        "witness": {
          "a": 1894,
          "b": 2319,
          "c": 5,
          "mask": [
            0,
            4
          ]
        }
      },
      {
        "erasures": 3,
        "patterns": 56,
        "asA": 5593022,
        "asB": 4565754,
        "third": 5099701,
        "witness": {
          "a": 461,
          "b": 48,
          "c": 0,
          "mask": [
            0,
            1,
            4
          ]
        }
      },
      {
        "erasures": 4,
        "patterns": 70,
        "asA": 26800508,
        "asB": 23999256,
        "third": 95568944,
        "witness": {
          "a": 5,
          "b": 48,
          "c": 0,
          "mask": [
            0,
            1,
            2,
            4
          ]
        }
      }
    ]
  },
  "independentPairCensus": {
    "mask": [
      0,
      4
    ],
    "asA": 3148,
    "asB": 1174,
    "third": 1431
  },
  "erasures": [
    3100,
    24800,
    86800,
    173600,
    217000
  ],
  "shared": [
    2304,
    18432,
    64512,
    129024,
    161280
  ],
  "unknown": [
    796,
    6368,
    22288,
    44576,
    55720
  ],
  "corruption": {
    "strict": {
      "correct": 0,
      "wrong": 0,
      "refused": 14616
    },
    "correctOne": {
      "correct": 14616,
      "wrong": 0,
      "refused": 0
    },
    "cases": 14616
  },
  "traces": [
    {
      "case": "mds-clean",
      "phase": 0.137,
      "tokens": [
        4,
        5,
        3,
        7,
        9,
        1,
        9,
        8
      ],
      "got": 21251,
      "expected": 21251,
      "energy": 57192897412,
      "witness": null,
      "corrected": null
    },
    {
      "case": "mds-four-erasure",
      "phase": 0.137,
      "tokens": [
        null,
        5,
        null,
        7,
        null,
        1,
        null,
        8
      ],
      "got": 21251,
      "expected": 21251,
      "energy": 28596108164,
      "witness": null,
      "corrected": null
    },
    {
      "case": "mds-new-vocabulary",
      "phase": 0.137,
      "tokens": [
        14,
        13,
        11,
        6,
        13,
        13,
        4,
        1
      ],
      "got": null,
      "expected": null,
      "energy": 57197151399,
      "witness": null,
      "corrected": null
    },
    {
      "case": "mds-two-erasure-one-error",
      "phase": 0.137,
      "tokens": [
        null,
        5,
        4,
        7,
        null,
        1,
        9,
        8
      ],
      "got": null,
      "expected": null,
      "energy": 42894665168,
      "witness": null,
      "corrected": 21251
    },
    {
      "case": "mds-splice-2",
      "phase": 0.137,
      "tokens": [
        null,
        3,
        4,
        3,
        null,
        13,
        16,
        1
      ],
      "got": 20753,
      "expected": 20753,
      "energy": 42895138760,
      "witness": {
        "a": 1950,
        "b": 202,
        "c": 7,
        "mask": [
          0,
          4
        ]
      },
      "corrected": null
    },
    {
      "case": "mds-splice-3",
      "phase": 0.137,
      "tokens": [
        null,
        null,
        5,
        2,
        null,
        13,
        11,
        16
      ],
      "got": 3991,
      "expected": 3991,
      "energy": 35748597477,
      "witness": {
        "a": 461,
        "b": 48,
        "c": 0,
        "mask": [
          0,
          1,
          4
        ]
      },
      "corrected": null
    },
    {
      "case": "mds-splice-4",
      "phase": 0.137,
      "tokens": [
        null,
        null,
        null,
        2,
        null,
        13,
        11,
        16
      ],
      "got": 3991,
      "expected": 3991,
      "energy": 28599445066,
      "witness": {
        "a": 5,
        "b": 48,
        "c": 0,
        "mask": [
          0,
          1,
          2,
          4
        ]
      },
      "corrected": null
    },
    {
      "case": "algebraic-two-erasure-splice",
      "phase": 0.137,
      "tokens": [
        null,
        4,
        8,
        6,
        null,
        13,
        8,
        4
      ],
      "got": 30681,
      "expected": 30681,
      "energy": 42896967189,
      "witness": {
        "a": 260,
        "b": 71,
        "c": 90,
        "mask": [
          0,
          4
        ]
      },
      "corrected": null
    }
  ],
  "specimens": [
    "mds-clean.wav",
    "mds-four-erasure.wav",
    "mds-new-vocabulary.wav",
    "mds-two-erasure-one-error.wav",
    "mds-splice-2.wav",
    "mds-splice-3.wav",
    "mds-splice-4.wav",
    "algebraic-two-erasure-splice.wav"
  ],
  "peak": 4096
}
*/
