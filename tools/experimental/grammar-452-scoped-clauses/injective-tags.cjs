"use strict";
// Grammars lane / Refs #452 / Draft #453. Original synthetic codebook experiment.
// Exact upstream b0a47254c527823e71abe874adb84d75f0102ded; unchanged sibling dependencies. No human evidence.
const R=require("./recursive.cjs"),I=require("./integrity.cjs"),B=require("./block-binding.cjs");
const lab=(function laboratory(R,I,B){
"use strict";
const trees=R.catalog(),N=trees.length,modes=["protected","tagged","replicated","injective"],mod=x=>(x%17+17)%17,key=x=>x.reduce((a,v)=>a*17+v,0),eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
function tagged(i,t){const x=R.encode(trees[i],"prefix").map(v=>I.vocab.indexOf(v));while(x.length<4)x.push(13);const y=[x[0],x[1],t,0,x[2],x[3],t,0],[a,b]=I.synd(y);y[7]=mod((4*a-b)*13);y[3]=mod(-a-y[7]);return y;}
function construct(){const left=new Set,right=new Set,book=[],tags=[],attempts=[];for(let i=0;i<N;i++){let chosen=false;for(let d=0;d<17;d++){const t=(i+d)%17,x=tagged(i,t),a=key(x.slice(0,4)),b=key(x.slice(4));if(left.has(a)||right.has(b))continue;left.add(a);right.add(b);book.push(x);tags.push(t);attempts.push(d+1);chosen=true;break;}if(!chosen)throw Error("no injective tag for rank "+i);}return {book,tags,attempts};}
const design=construct(),books=Object.fromEntries(modes.map(m=>[m,m==="injective"?design.book:trees.map((_,i)=>B.encode(i,m))])),map=new Map(design.book.map((x,i)=>[key(x),i]));
function encode(i,mode="injective"){if(!modes.includes(mode)||!Number.isInteger(i)||i<0||i>=N)throw Error("encode");return books[mode][i].slice();}
function decode(input,mode="injective"){if(mode!=="injective")return B.decode(input,mode);if(!Array.isArray(input)||input.length!==8||input.some(v=>v!==null&&(!Number.isInteger(v)||v<0||v>=17)))return null;const x=input.slice(),e=x.map((v,i)=>v===null?i:-1).filter(i=>i>=0);if(e.length>2)return null;const [a,b]=I.synd(x.map(v=>v??0));if(e.length===1)x[e[0]]=mod(-a);if(e.length===2){const [i,j]=e;let inv=1;while(mod(inv*(j-i))!==1)inv++;const q=mod(((i+1)*a-b)*inv);x[i]=mod(-a-q);x[j]=q;}return map.get(key(x))??null;}
const masks=[[]];for(let i=0;i<8;i++){masks.push([i]);for(let j=i+1;j<8;j++)masks.push([i,j]);}
function erase(x,mask){const y=x.slice();for(const j of mask)y[j]=null;return y;}
function splice(mode,a,b,mask=[]){return erase([...books[mode][a].slice(0,4),...books[mode][b].slice(4)],mask);}
function census(mode,mask){const book=books[mode],left=new Map,right=new Map,full=new Set;const l=x=>key(x.slice(0,4).filter((_,j)=>!mask.includes(j))),r=x=>key(x.slice(4).filter((_,j)=>!mask.includes(j+4))),p=book.map(l),q=book.map(r),factor=17**(4-mask.filter(j=>j>=4).length);for(let i=0;i<N;i++){for(const [m,k] of [[left,p[i]],[right,q[i]]]){if(!m.has(k))m.set(k,[]);m.get(k).push(i);}full.add(p[i]*factor+q[i]);}if(full.size!==N)throw Error("projected codebook collision");let asA=0,asB=0,third=0,witness=null,sourceWitness=null;for(let c=0;c<N;c++){const a=left.get(p[c]),b=right.get(q[c]);asA+=b.length-1;asB+=a.length-1;third+=(a.length-1)*(b.length-1);if(!witness&&a.length>1&&b.length>1)witness={a:a.find(i=>i!==c),b:b.find(i=>i!==c),c,mask};if(!sourceWitness&&(a.length>1||b.length>1))sourceWitness={a:a.find(i=>i!==c)??c,b:a.length>1?c:b.find(i=>i!==c),c,mask};}
return {mask,asA,asB,third,accepted:asA+asB+third,refused:N*(N-1)-asA-asB-third,unique:[left.size,right.size],witness,sourceWitness};}
function brute(mode,mask){const book=books[mode],p=book.map(x=>key(x.slice(0,4).filter((_,j)=>!mask.includes(j)))),q=book.map(x=>key(x.slice(4).filter((_,j)=>!mask.includes(j+4)))),f=17**(4-mask.filter(j=>j>=4).length),m=new Map(p.map((v,i)=>[v*f+q[i],i]));const c={asA:0,asB:0,third:0,refused:0};for(let i=0;i<N;i++)for(let j=0;j<N;j++)if(i!==j){const z=m.get(p[i]*f+q[j]);c[z===undefined?"refused":z===i?"asA":z===j?"asB":"third"]++;}return c;}
function qualify(){let assertions=0;const check=(v,msg)=>{assertions++;if(!v)throw Error(msg);};const metrics={},traces=[],specimens=[];let peak=0;
check(N===2304,"catalog");check(eq(construct(),design),"deterministic design");for(let i=0;i<N;i++){check(eq(tagged(i,i%17),B.encode(i,"tagged")),"legacy encoding");check(eq(encode(i).filter((_,j)=>[0,1,4,5].includes(j)),tagged(i,i%17).filter((_,j)=>[0,1,4,5].includes(j))),"preserved grammar tokens");}
for(const mode of modes){const book=books[mode],rows=masks.map(mask=>census(mode,mask));let minDistance=8,halfDistance=[4,4],one=0,two=0,sub=0;for(let i=0;i<N;i++){const x=book[i];check(decode(x,mode)===i,"round trip");for(const mask of masks.slice(1)){check(decode(erase(x,mask),mode)===i,"erasure recovery");if(mask.length===1)one++;else two++;}for(let k=0;k<8;k++)for(let v=0;v<17;v++)if(v!==x[k]){const y=x.slice();y[k]=v;check(decode(y,mode)===null,"substitution refusal");sub++;}for(let j=i+1;j<N;j++){let a=0,b=0;for(let k=0;k<4;k++){a+=x[k]!==book[j][k];b+=x[k+4]!==book[j][k+4];}minDistance=Math.min(minDistance,a+b);halfDistance[0]=Math.min(halfDistance[0],a);halfDistance[1]=Math.min(halfDistance[1],b);}}
for(const row of rows){for(const w of [row.witness,row.sourceWitness])if(w){check(w.a!==w.b,"different sources");check(decode(splice(mode,w.a,w.b,w.mask),mode)===w.c,"witness decode");}}
for(const mask of [[],[0],[0,4]]){const a=rows.find(x=>eq(x.mask,mask)),b=brute(mode,mask);for(const k of Object.keys(b))check(a[k]===b[k],"independent exhaustive projected lookup");}
const totals=[0,1,2].map(n=>{const rs=rows.filter(x=>x.mask.length===n);return {erasures:n,patterns:rs.length,orderedCases:rs.length*N*(N-1),asA:rs.reduce((s,x)=>s+x.asA,0),asB:rs.reduce((s,x)=>s+x.asB,0),third:rs.reduce((s,x)=>s+x.third,0),accepted:rs.reduce((s,x)=>s+x.accepted,0),maxAccepted:Math.max(...rs.map(x=>x.accepted))};});
metrics[mode]={minDistance,halfDistance,one,two,sub,totals,rows};}
check(metrics.injective.rows[0].accepted===0,"injective intact splice guarantee");
const first=metrics.injective.rows.find(x=>x.witness),fallback=metrics.injective.rows.find(x=>x.sourceWitness),w=first?.witness??fallback?.sourceWitness;check(!!w,"partial witness retained");
const cases=[{name:"clean",a:309,b:309,mask:[]},{name:"two-erasure",a:309,b:309,mask:[0,4]},{name:"prior-splice",a:261,b:1792,mask:[]},{name:"tag-splice",a:309,b:241,mask:[]},{name:"partial-witness-intact",a:w.a,b:w.b,mask:[]},{name:"partial-witness-erased",a:w.a,b:w.b,mask:w.mask},{name:"single-replacement",a:309,b:309,mask:[],replace:true}];
for(const mode of modes)for(const c of cases)for(const phase of [.137,2.419,5.827]){const x=splice(mode,c.a,c.b,c.mask);if(c.replace)x[2]=mod(x[2]+1);const pcm=I.render(x,phase),tokens=I.receive(pcm),expected=decode(x,mode),got=decode(tokens,mode);check(eq(x,tokens),"aligned demodulation");check(got===expected,"PCM decode");const wav=R.wav(pcm),v=new DataView(wav.buffer);check(v.getUint32(24,true)===16000&&v.getUint32(40,true)===pcm.length*2,"WAV header");let energy=0;for(const s of pcm){peak=Math.max(peak,Math.abs(s));energy+=s*s;}const row={mode,case:c.name,phase,a:c.a,b:c.b,mask:c.mask,tokens,got,energy};traces.push(row);if(phase===.137)specimens.push({...row,name:mode+"-"+c.name+".wav"});}
check(peak<=8192,"digital peak");
return {schema:"mhac-grammar-injective-tags-v1",source:"b0a47254c527823e71abe874adb84d75f0102ded",trees:N,assertions,design:{changed:design.tags.filter((t,i)=>t!==i%17).length,maxAttempts:Math.max(...design.attempts),totalAttempts:design.attempts.reduce((a,b)=>a+b,0),tags:design.tags},metrics,witness:{...w,trees:[trees[w.a],trees[w.b],trees[w.c]],intact:splice("injective",w.a,w.b),erased:splice("injective",w.a,w.b,w.mask),target:encode(w.c)},cases,traces,specimens,peak};}
return {encode,decode,construct,census,qualify,trees,modes};
})(R,I,B);
module.exports=lab;
if(require.main===module){
 const fs=require("node:fs"),path=require("node:path"),crypto=require("node:crypto"),dir=process.argv[2]||"output-injective-tags";fs.mkdirSync(dir,{recursive:true});
 const q=lab.qualify(),manifest=[];for(const s of q.specimens){const wav=R.wav(I.render(s.tokens,s.phase));fs.writeFileSync(path.join(dir,s.name),wav);manifest.push({...s,sha256:crypto.createHash("sha256").update(wav).digest("hex")});}
 fs.writeFileSync(path.join(dir,"qualification.json"),JSON.stringify(q,null,2)+"\n");fs.writeFileSync(path.join(dir,"stimuli.json"),JSON.stringify(manifest,null,2)+"\n");console.log(JSON.stringify({assertions:q.assertions,design:{changed:q.design.changed,maxAttempts:q.design.maxAttempts},metrics:Object.fromEntries(Object.entries(q.metrics).map(([m,v])=>[m,v.totals])),peak:q.peak},null,2));
}

/* Run 010 — 2026-11-25. Refs #452 / Draft #453. One GPT-6.2 agent; no subagents. Accepted main 495a98ca12bae467a507031f04931aa4254b1866; previous head b0a47254c527823e71abe874adb84d75f0102ded CI 45594001164 success. Greedy catalog-order tag reassignment tests candidates (rank+d) mod 17 for d=0..16, accepts first with unique left and right four-slot keys; failure is explicit, not guaranteed on arbitrary catalogs. Four direct grammar-token positions remain unchanged relative to tagged grammar, with duplicate tag and two GF(17) checks. Exact intact and known-erasure splice census via projected half equivalence classes; distinct ordered A,B only, unique full projections for up to two erasures. Cross-check exhaustive numerical projected lookup for masks [],[0],[0,4] in every mode. Counts are combinatorial, not field error rates; masks weight equally, no independent trial inference. Greedy design optimized on entire finite catalog, no held-out catalog claim. Exact aligned PCM body tests at three fixed phases (640 ms body, no acquisition or marker test; unchanged 680 ms nominal framed format). All modes same slot/carrier bank/amplitude; actual energies recorded. Native Node 22.16.0 installed but git ls-remote failed DNS exit 128; two complete V8 runs identical; native CLI, disk export and listening not executed. CLI node injective-tags.cjs output-injective-tags exports qualification, WAVs and SHA-256 manifest. Codebook version mismatch, source/transaction authority, arbitrary mixed corruption and human learnability remain unqualified. No canonical research changes, merges, or human studies. Executed summary:
{
  "assertions": 1525977,
  "design": {
    "changed": 71,
    "maxAttempts": 2,
    "totalAttempts": 2375
  },
  "metrics": {
    "protected": {
      "minDistance": 3,
      "halfDistance": [
        0,
        0
      ],
      "one": 18432,
      "two": 64512,
      "sub": 294912,
      "totals": [
        {
          "erasures": 0,
          "patterns": 1,
          "orderedCases": 5306112,
          "asA": 4764,
          "asB": 6132,
          "third": 13104,
          "accepted": 24000,
          "maxAccepted": 24000
        },
        {
          "erasures": 1,
          "patterns": 8,
          "orderedCases": 42448896,
          "asA": 173972,
          "asB": 178148,
          "third": 762007,
          "accepted": 1114127,
          "maxAccepted": 247824
        },
        {
          "erasures": 2,
          "patterns": 28,
          "orderedCases": 148571136,
          "asA": 2528196,
          "asB": 2118372,
          "third": 19088945,
          "accepted": 23735513,
          "maxAccepted": 4243232
        }
      ]
    },
    "tagged": {
      "minDistance": 3,
      "halfDistance": [
        0,
        0
      ],
      "one": 18432,
      "two": 64512,
      "sub": 294912,
      "totals": [
        {
          "erasures": 0,
          "patterns": 1,
          "orderedCases": 5306112,
          "asA": 96,
          "asB": 52,
          "third": 6,
          "accepted": 154,
          "maxAccepted": 154
        },
        {
          "erasures": 1,
          "patterns": 8,
          "orderedCases": 42448896,
          "asA": 18092,
          "asB": 7430,
          "third": 630,
          "accepted": 26152,
          "maxAccepted": 6013
        },
        {
          "erasures": 2,
          "patterns": 28,
          "orderedCases": 148571136,
          "asA": 385686,
          "asB": 230866,
          "third": 70262,
          "accepted": 686814,
          "maxAccepted": 118196
        }
      ]
    },
    "replicated": {
      "minDistance": 4,
      "halfDistance": [
        2,
        2
      ],
      "one": 18432,
      "two": 64512,
      "sub": 294912,
      "totals": [
        {
          "erasures": 0,
          "patterns": 1,
          "orderedCases": 5306112,
          "asA": 0,
          "asB": 0,
          "third": 0,
          "accepted": 0,
          "maxAccepted": 0
        },
        {
          "erasures": 1,
          "patterns": 8,
          "orderedCases": 42448896,
          "asA": 0,
          "asB": 0,
          "third": 0,
          "accepted": 0,
          "maxAccepted": 0
        },
        {
          "erasures": 2,
          "patterns": 28,
          "orderedCases": 148571136,
          "asA": 158480,
          "asB": 158480,
          "third": 0,
          "accepted": 316960,
          "maxAccepted": 36792
        }
      ]
    },
    "injective": {
      "minDistance": 3,
      "halfDistance": [
        1,
        1
      ],
      "one": 18432,
      "two": 64512,
      "sub": 294912,
      "totals": [
        {
          "erasures": 0,
          "patterns": 1,
          "orderedCases": 5306112,
          "asA": 0,
          "asB": 0,
          "third": 0,
          "accepted": 0,
          "maxAccepted": 0
        },
        {
          "erasures": 1,
          "patterns": 8,
          "orderedCases": 42448896,
          "asA": 17528,
          "asB": 7192,
          "third": 0,
          "accepted": 24720,
          "maxAccepted": 5758
        },
        {
          "erasures": 2,
          "patterns": 28,
          "orderedCases": 148571136,
          "asA": 384336,
          "asB": 230318,
          "third": 56394,
          "accepted": 671048,
          "maxAccepted": 115232
        }
      ]
    }
  },
  "witness": {
    "a": 1998,
    "b": 43,
    "c": 9,
    "mask": [
      0,
      4
    ],
    "trees": [
      [
        "if",
        [
          "open"
        ],
        [
          "not",
          [
            "stopped"
          ]
        ]
      ],
      [
        "not",
        [
          "question",
          [
            "overload"
          ]
        ]
      ],
      [
        "quote",
        [
          "open"
        ]
      ]
    ],
    "intact": [
      12,
      1,
      9,
      11,
      3,
      13,
      9,
      7
    ],
    "erased": [
      null,
      1,
      9,
      11,
      null,
      13,
      9,
      7
    ],
    "target": [
      5,
      1,
      9,
      11,
      13,
      13,
      9,
      7
    ]
  },
  "pcm": 84,
  "specimens": 28,
  "peak": 4096,
  "pcmCases": [
    {
      "mode": "protected",
      "case": "clean",
      "got": 309,
      "energy": 57192128908
    },
    {
      "mode": "protected",
      "case": "two-erasure",
      "got": 309,
      "energy": 42895418033
    },
    {
      "mode": "protected",
      "case": "prior-splice",
      "got": 260,
      "energy": 57191129636
    },
    {
      "mode": "protected",
      "case": "tag-splice",
      "got": null,
      "energy": 57194466321
    },
    {
      "mode": "protected",
      "case": "partial-witness-intact",
      "got": null,
      "energy": 57192502314
    },
    {
      "mode": "protected",
      "case": "partial-witness-erased",
      "got": null,
      "energy": 42894081202
    },
    {
      "mode": "protected",
      "case": "single-replacement",
      "got": null,
      "energy": 57193412792
    },
    {
      "mode": "tagged",
      "case": "clean",
      "got": 309,
      "energy": 57192562691
    },
    {
      "mode": "tagged",
      "case": "two-erasure",
      "got": 309,
      "energy": 42894005687
    },
    {
      "mode": "tagged",
      "case": "prior-splice",
      "got": null,
      "energy": 57189187253
    },
    {
      "mode": "tagged",
      "case": "tag-splice",
      "got": 37,
      "energy": 57192613755
    },
    {
      "mode": "tagged",
      "case": "partial-witness-intact",
      "got": null,
      "energy": 57195390713
    },
    {
      "mode": "tagged",
      "case": "partial-witness-erased",
      "got": 9,
      "energy": 42897043111
    },
    {
      "mode": "tagged",
      "case": "single-replacement",
      "got": null,
      "energy": 57192887451
    },
    {
      "mode": "replicated",
      "case": "clean",
      "got": 309,
      "energy": 57188173267
    },
    {
      "mode": "replicated",
      "case": "two-erasure",
      "got": 309,
      "energy": 42890931047
    },
    {
      "mode": "replicated",
      "case": "prior-splice",
      "got": null,
      "energy": 57193159390
    },
    {
      "mode": "replicated",
      "case": "tag-splice",
      "got": null,
      "energy": 57187823517
    },
    {
      "mode": "replicated",
      "case": "partial-witness-intact",
      "got": null,
      "energy": 57192836673
    },
    {
      "mode": "replicated",
      "case": "partial-witness-erased",
      "got": null,
      "energy": 42893614405
    },
    {
      "mode": "replicated",
      "case": "single-replacement",
      "got": null,
      "energy": 57188182999
    },
    {
      "mode": "injective",
      "case": "clean",
      "got": 309,
      "energy": 57190942828
    },
    {
      "mode": "injective",
      "case": "two-erasure",
      "got": 309,
      "energy": 42892385824
    },
    {
      "mode": "injective",
      "case": "prior-splice",
      "got": null,
      "energy": 57189187253
    },
    {
      "mode": "injective",
      "case": "tag-splice",
      "got": null,
      "energy": 57190069050
    },
    {
      "mode": "injective",
      "case": "partial-witness-intact",
      "got": null,
      "energy": 57195390713
    },
    {
      "mode": "injective",
      "case": "partial-witness-erased",
      "got": 9,
      "energy": 42897043111
    },
    {
      "mode": "injective",
      "case": "single-replacement",
      "got": null,
      "energy": 57191149369
    }
  ]
}
*/
