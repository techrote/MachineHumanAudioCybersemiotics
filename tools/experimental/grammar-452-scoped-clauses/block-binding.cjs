"use strict";
// Grammars lane / Refs #452 / Draft #453. Synthetic, not authentication.
// Pinned dependency: c2eb5783dfd9b3272512ef17ea08986d44e29228.
const R=require("./recursive.cjs"),I=require("./integrity.cjs"),H=require("./clock-hypotheses.cjs"),A=require("./acquisition.cjs"),L=require("./local-clock.cjs");
const trees=R.catalog(),N=trees.length,modes=["protected","tagged","replicated"],mod=x=>(x%17+17)%17;
const key=x=>x.reduce((a,v)=>a*17+v,0),eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const treeIndex=new Map(trees.map((t,i)=>[JSON.stringify(t),i]));
const inverse=x=>{for(let i=1;i<17;i++)if(mod(x*i)===1)return i;throw Error("inverse");};
function encode(i,mode){
 if(!Number.isInteger(i)||i<0||i>=N||!modes.includes(mode))throw Error("encode");
 if(mode==="protected")return I.encode(trees[i],"protected");
 if(mode==="replicated"){const a=i%17,b=Math.floor(i/17)%17,c=Math.floor(i/289);return [a,b,c,mod(a+b+c),a,b,c,mod(a+2*b+3*c)];}
 const t=R.encode(trees[i],"prefix").map(v=>I.vocab.indexOf(v));while(t.length<4)t.push(13);
 const x=[t[0],t[1],i%17,0,t[2],t[3],i%17,0], [a,b]=I.synd(x);
 x[7]=mod((4*a-b)*inverse(4));x[3]=mod(-a-x[7]);return x;
}
const books=Object.fromEntries(modes.map(m=>[m,trees.map((_,i)=>encode(i,m))]));
const maps=Object.fromEntries(modes.map(m=>[m,new Map(books[m].map((x,i)=>[key(x),i]))]));
function decode(input,mode){
 if(!modes.includes(mode)||!Array.isArray(input)||input.length!==8||input.some(v=>v!==null&&(!Number.isInteger(v)||v<0||v>=17)))return null;
 const x=input.slice(),missing=x.map((v,i)=>v===null?i:-1).filter(i=>i>=0);
 if(missing.length>2)return null;
 if(mode==="replicated"){
  for(let j=0;j<3;j++){const a=x[j],b=x[j+4];if(a!==null&&b!==null&&a!==b)return null;if(a===null)x[j]=b;if(b===null)x[j+4]=a;}
  const j=x.slice(0,3).indexOf(null);
  if(j>=0){if(x[3]===null)return null;x[j]=x[j+4]=mod(x[3]-x.slice(0,3).reduce((s,v)=>s+(v??0),0));}
  if(x[3]===null)x[3]=mod(x[0]+x[1]+x[2]);
  if(x[7]===null)x[7]=mod(x[0]+2*x[1]+3*x[2]);
 }else{
  const [a,b]=I.synd(x.map(v=>v??0));
  if(missing.length===1)x[missing[0]]=mod(-a);
  if(missing.length===2){const [i,j]=missing,q=mod(((i+1)*a-b)*inverse(j-i));x[i]=mod(-a-q);x[j]=q;}
 }
 const index=maps[mode].get(key(x));return index===undefined?null:index;
}
// Exact ordered-pair census by disjoint prefix/suffix equivalence classes.
// A != B; an accepted C can equal A, B, or neither. Unique complete codewords.
function census(mode){
 const book=books[mode],a=new Map(),b=new Map(),hist=Array(9).fill(0);
 for(let i=0;i<N;i++)for(const [m,k] of [[a,key(book[i].slice(0,4))],[b,key(book[i].slice(4))]]){if(!m.has(k))m.set(k,[]);m.get(k).push(i);}
 let asA=0,asB=0,third=0,witness=null;
 for(let c=0;c<N;c++){
  const aa=a.get(key(book[c].slice(0,4))),bb=b.get(key(book[c].slice(4)));
  asA+=bb.length-1;asB+=aa.length-1;third+=(aa.length-1)*(bb.length-1);
  if(!witness&&aa.length>1&&bb.length>1)witness={a:aa.find(i=>i!==c),b:bb.find(i=>i!==c),c};
  for(let j=c+1;j<N;j++){let d=0;for(let k=0;k<8;k++)d+=book[c][k]!==book[j][k];hist[d]++;}
 }
 const total=N*(N-1);return {total,asA,asB,third,refused:total-asA-asB-third,uniqueA:a.size,uniqueB:b.size,maxA:Math.max(...[...a.values()].map(x=>x.length)),maxB:Math.max(...[...b.values()].map(x=>x.length)),distance:hist.findIndex(v=>v>0),distanceHistogram:hist,witness};
}
const join=(...a)=>{const p=new Int16Array(a.reduce((n,x)=>n+x.length,0));let j=0;for(const x of a){p.set(x,j);j+=x.length;}return p;};
const lerp=(p,t)=>{const j=Math.floor(t),u=t-j;return Math.round((p[j]||0)*(1-u)+(p[j+1]||0)*u);};
const stretch=(p,s)=>Int16Array.from({length:Math.round(p.length*s)},(_,i)=>lerp(p,i/s));
const HALF=5440,MARK=320,BODY=5120,RATE=16000;
function packet(x,phase){const h=A.preamble("ordered",phase),p=I.render(x,phase);return join(h.slice(0,MARK),p.slice(0,BODY),h.slice(MARK),p.slice(BODY));}
// Same acquisition for all variants; deliberately bounded single-pair receiver.
function receive(p,mode){
 const a=H.acquire(p),[as,bs]=a.peaks,hypotheses=[];
 if(a.overflow||as.length!==1||bs.length!==1||Math.abs(bs[0].at-as[0].at-HALF)>480)return {...a,hypotheses,index:null};
 const [x]=as,[y]=bs;
 for(const [name,sa,sb] of [["nominal",1,1],["spectral",x.scale,y.scale]]){
  const at=x.at+MARK*sa,bt=y.at+MARK*sb;
  if(at<0||bt<0||at+(BODY-1)*sa>=p.length||bt+(BODY-1)*sb>=p.length)continue;
  const tokens=I.receive(join(Int16Array.from({length:BODY},(_,i)=>lerp(p,at+i*sa)),Int16Array.from({length:BODY},(_,i)=>lerp(p,bt+i*sb))));
  hypotheses.push({name,tokens,index:decode(tokens,mode)});
 }
 const ids=[...new Set(hypotheses.map(h=>h.index).filter(i=>i!==null))];
 return {...a,hypotheses,index:ids.length===1?ids[0]:null};
}
const conditions=["clean","gap-minus20","gap-plus25","piecewise","two-erasures","single-substitution","prior-splice","tag-splice","foreign","noise-only"];
const seeds=[197502403,2846156604,1199091069,3853526830,2206461295,559395760];
const prior=L.spliceWitness(),tag=census("tagged").witness;
function stimulus(mode,condition,seed){
 let state=seed>>>0;const rand=()=>{state=(Math.imul(state,1664525)+1013904223)>>>0;return state/4294967296;};
 const i=Math.floor(rand()*N),phase=rand()*Math.PI*2,lead=800+Math.floor(rand()*512);
 let x=books[mode][i].slice(),truth=i,sources=[i],gap=0,sa=1,sb=1,noise=0;
 if(condition==="gap-minus20")gap=-320;if(condition==="gap-plus25")gap=400;
 if(condition==="piecewise"){sa=.99;sb=1.01;noise=400;}
 if(condition==="two-erasures"){x[1]=null;x[6]=null;}
 if(condition==="single-substitution")x[2]=mod(x[2]+1);
 if(condition==="prior-splice"||condition==="tag-splice"){
  const w=condition==="prior-splice"?prior:tag;
  if(!w)throw Error("no tag witness");
  sources=[w.a,w.b];x=[...books[mode][w.a].slice(0,4),...books[mode][w.b].slice(4)];truth=null;
 }
 if(condition==="foreign")truth=null;
 let p=packet(x,phase);if(condition==="noise-only"){p.fill(0);truth=null;sources=[];noise=900;}
 const a=stretch(p.slice(0,HALF),sa),b=stretch(p.slice(HALF),sb);
 if(gap<0&&a.slice(a.length+gap).some(v=>v!==0))throw Error("nonzero contraction");
 p=join(new Int16Array(lead),gap<0?a.slice(0,a.length+gap):join(a,new Int16Array(gap)),b,new Int16Array(1200));
 if(noise)for(let j=0;j<p.length;j++)p[j]=Math.round(p[j]+(rand()*2-1)*Math.sqrt(3)*noise);
 return {pcm:p,truth,sources,mode,condition,seed,tokens:x,phase};
}
function qualify(){
 let assertions=0;const check=(v,m)=>{assertions++;if(!v)throw Error(m);};
 const metrics={},traces=[],specimens=[];let peak=0;
 for(const mode of modes){
  const book=books[mode],c=census(mode),m={census:c,clean:0,oneErase:0,twoErase:0,singleSubRefused:0,pcm:{},cleanEnergy:{min:Infinity,max:0}};
  check(maps[mode].size===N,"unique");check(c.distance>=3,"distance");
  for(let i=0;i<N;i++){
   const x=book[i];check(decode(x,mode)===i,"clean");m.clean++;
   if(mode==="protected")check(eq(I.decode(x,"protected").tree,trees[i]),"legacy equivalence");
   for(let j=0;j<8;j++){
    const e=x.slice();e[j]=null;check(decode(e,mode)===i,"single erasure");m.oneErase++;
    for(let k=j+1;k<8;k++){const z=e.slice();z[k]=null;check(decode(z,mode)===i,"double erasure");m.twoErase++;}
    for(let v=0;v<17;v++)if(v!==x[j]){const z=x.slice();z[j]=v;check(decode(z,mode)===null,"single replacement");m.singleSubRefused++;}
   }
  }
  // Independent brute-force check of the analytical census, numeric four-slot keys.
  const prefixes=book.map(x=>key(x.slice(0,4))),suffixes=book.map(x=>key(x.slice(4))),factor=17**4;
  const counts={asA:0,asB:0,third:0,refused:0};
  for(let i=0;i<N;i++)for(let j=0;j<N;j++)if(i!==j){const got=maps[mode].get(prefixes[i]*factor+suffixes[j]);counts[got===undefined?"refused":got===i?"asA":got===j?"asB":"third"]++;}
  for(const k of Object.keys(counts))check(counts[k]===c[k],"census "+k);
  if(c.witness){const {a,b,c:j}=c.witness;check(decode([...book[a].slice(0,4),...book[b].slice(4)],mode)===j,"witness");}
  for(const condition of conditions){
   const row={correct:0,wrong:0,refused:0,unintended:0,expectedRefusal:0};
   for(const seed of seeds){
    const s=stimulus(mode,condition,seed),o=receive(s.pcm,mode);
    const status=s.truth===null?(o.index===null?"expectedRefusal":"unintended"):(o.index===null?"refused":o.index===s.truth?"correct":"wrong");row[status]++;
    if(condition==="clean"){check(status==="correct","PCM clean");const en=s.pcm.reduce((n,v)=>n+v*v,0);m.cleanEnergy.min=Math.min(m.cleanEnergy.min,en);m.cleanEnergy.max=Math.max(m.cleanEnergy.max,en);}
    if(condition==="single-substitution")check(o.index===null,"PCM substitution");
    if(mode==="replicated"&&condition.endsWith("splice"))check(o.index===null,"PCM splice refusal");
    const wav=R.wav(s.pcm),view=new DataView(wav.buffer);check(view.getUint32(24,true)===RATE&&view.getUint32(40,true)===2*s.pcm.length,"WAV");
    for(const v of s.pcm)peak=Math.max(peak,Math.abs(v));
    if(seed===seeds[0])specimens.push({mode,condition,seed,bytes:wav.length});
    traces.push({mode,condition,seed,truth:s.truth,sources:s.sources,tokens:s.tokens,status,...o});
   }m.pcm[condition]=row;
  }
  metrics[mode]=m;
 }
 check(metrics.replicated.census.refused===N*(N-1),"all distinct intact splice refusals");
 check(peak<=8192,"digital gain");
 return {schema:"mhac-grammar-block-binding-v1",dependency:"c2eb5783dfd9b3272512ef17ea08986d44e29228",assertions,trees:N,seeds,conditions,metrics,prior,tag,peak,specimens,traces};
}
module.exports={encode,decode,census,receive,stimulus,qualify};
if(require.main===module){
 const fs=require("node:fs"),path=require("node:path"),crypto=require("node:crypto"),dir=process.argv[2]||"output-block-binding";fs.mkdirSync(dir,{recursive:true});
 const q=qualify(),manifest=[];
 for(const {mode,condition,seed} of q.specimens){const s=stimulus(mode,condition,seed),wav=R.wav(s.pcm),file=mode+"-"+condition+".wav";fs.writeFileSync(path.join(dir,file),wav);manifest.push({file,mode,condition,seed,truth:s.truth,sources:s.sources,sha256:crypto.createHash("sha256").update(wav).digest("hex")});}
 fs.writeFileSync(path.join(dir,"qualification.json"),JSON.stringify(q,null,2)+"\n");fs.writeFileSync(path.join(dir,"stimuli.json"),JSON.stringify(manifest,null,2)+"\n");
 console.log(JSON.stringify({assertions:q.assertions,metrics:q.metrics,peak:q.peak},null,2));
}

/*
Grammars Run 009. Refs #452 / Draft #453. One GPT-6.2 agent, no subagents. Previous exact-head CI 45585294545 success. Three equal-slot formats with same 680 ms airtime, carrier bank, amplitude and markers; actual clean energies reported. Protected is existing codebook, tagged retains four padded prefix grammar tokens plus duplicate rank mod 17 and two GF(17) checks; replicated uses full three-digit catalog rank in each half and separate parity. Replicated sacrifices directly compositional acoustic tokens and requires exact shared catalog ordering. Catalog-membership decoder, no authentication, no source identity, no replay protection, no claims about human interpretation. Exact ordered-pair intact splice census independently cross-checked by exhaustive numeric lookup; clean, all one/two erasures and all one replacement cases exhaustively tested. Single-pair PCM acquisition shared across formats, no oracle timing; no missing-marker fallback in this narrow comparator. Six fixed seeds per condition, no tuning or population inference. Foreign valid packets remain acceptable; distinct intact half-splice guarantee does not cover arbitrary corruption or same-message different-source splices. V8 two identical complete executions; native Node v22.16.0 available, git ls-remote DNS failed exit 128; native filesystem/CLI and playback not executed. CLI exports 30 original WAV specimens and hashes. No canonical changes or human study. Executed summary:
{
  "schema": "mhac-grammar-block-binding-v1",
  "dependency": "c2eb5783dfd9b3272512ef17ea08986d44e29228",
  "assertions": 1143034,
  "trees": 2304,
  "seeds": [
    197502403,
    2846156604,
    1199091069,
    3853526830,
    2206461295,
    559395760
  ],
  "conditions": [
    "clean",
    "gap-minus20",
    "gap-plus25",
    "piecewise",
    "two-erasures",
    "single-substitution",
    "prior-splice",
    "tag-splice",
    "foreign",
    "noise-only"
  ],
  "metrics": {
    "protected": {
      "census": {
        "total": 5306112,
        "asA": 4764,
        "asB": 6132,
        "third": 13104,
        "refused": 5282112,
        "uniqueA": 771,
        "uniqueB": 961,
        "maxA": 4,
        "maxB": 7,
        "distance": 3,
        "distanceHistogram": [
          0,
          0,
          0,
          45166,
          252712,
          830500,
          1161640,
          363038,
          0
        ],
        "witness": {
          "a": 261,
          "b": 1792,
          "c": 260
        }
      },
      "clean": 2304,
      "oneErase": 18432,
      "twoErase": 64512,
      "singleSubRefused": 294912,
      "pcm": {
        "clean": {
          "correct": 6,
          "wrong": 0,
          "refused": 0,
          "unintended": 0,
          "expectedRefusal": 0
        },
        "gap-minus20": {
          "correct": 6,
          "wrong": 0,
          "refused": 0,
          "unintended": 0,
          "expectedRefusal": 0
        },
        "gap-plus25": {
          "correct": 6,
          "wrong": 0,
          "refused": 0,
          "unintended": 0,
          "expectedRefusal": 0
        },
        "piecewise": {
          "correct": 6,
          "wrong": 0,
          "refused": 0,
          "unintended": 0,
          "expectedRefusal": 0
        },
        "two-erasures": {
          "correct": 6,
          "wrong": 0,
          "refused": 0,
          "unintended": 0,
          "expectedRefusal": 0
        },
        "single-substitution": {
          "correct": 0,
          "wrong": 0,
          "refused": 6,
          "unintended": 0,
          "expectedRefusal": 0
        },
        "prior-splice": {
          "correct": 0,
          "wrong": 0,
          "refused": 0,
          "unintended": 6,
          "expectedRefusal": 0
        },
        "tag-splice": {
          "correct": 0,
          "wrong": 0,
          "refused": 0,
          "unintended": 0,
          "expectedRefusal": 6
        },
        "foreign": {
          "correct": 0,
          "wrong": 0,
          "refused": 0,
          "unintended": 6,
          "expectedRefusal": 0
        },
        "noise-only": {
          "correct": 0,
          "wrong": 0,
          "refused": 0,
          "unintended": 0,
          "expectedRefusal": 6
        }
      },
      "cleanEnergy": {
        "min": 61827555348,
        "max": 61839087753
      }
    },
    "tagged": {
      "census": {
        "total": 5306112,
        "asA": 96,
        "asB": 52,
        "third": 6,
        "refused": 5305958,
        "uniqueA": 2278,
        "uniqueB": 2256,
        "maxA": 2,
        "maxB": 2,
        "distance": 3,
        "distanceHistogram": [
          0,
          0,
          0,
          1326,
          16669,
          99715,
          343628,
          898705,
          1293013
        ],
        "witness": {
          "a": 309,
          "b": 241,
          "c": 37
        }
      },
      "clean": 2304,
      "oneErase": 18432,
      "twoErase": 64512,
      "singleSubRefused": 294912,
      "pcm": {
        "clean": {
          "correct": 6,
          "wrong": 0,
          "refused": 0,
          "unintended": 0,
          "expectedRefusal": 0
        },
        "gap-minus20": {
          "correct": 6,
          "wrong": 0,
          "refused": 0,
          "unintended": 0,
          "expectedRefusal": 0
        },
        "gap-plus25": {
          "correct": 6,
          "wrong": 0,
          "refused": 0,
          "unintended": 0,
          "expectedRefusal": 0
        },
        "piecewise": {
          "correct": 6,
          "wrong": 0,
          "refused": 0,
          "unintended": 0,
          "expectedRefusal": 0
        },
        "two-erasures": {
          "correct": 6,
          "wrong": 0,
          "refused": 0,
          "unintended": 0,
          "expectedRefusal": 0
        },
        "single-substitution": {
          "correct": 0,
          "wrong": 0,
          "refused": 6,
          "unintended": 0,
          "expectedRefusal": 0
        },
        "prior-splice": {
          "correct": 0,
          "wrong": 0,
          "refused": 0,
          "unintended": 0,
          "expectedRefusal": 6
        },
        "tag-splice": {
          "correct": 0,
          "wrong": 0,
          "refused": 0,
          "unintended": 6,
          "expectedRefusal": 0
        },
        "foreign": {
          "correct": 0,
          "wrong": 0,
          "refused": 0,
          "unintended": 6,
          "expectedRefusal": 0
        },
        "noise-only": {
          "correct": 0,
          "wrong": 0,
          "refused": 0,
          "unintended": 0,
          "expectedRefusal": 6
        }
      },
      "cleanEnergy": {
        "min": 61828445605,
        "max": 61838193019
      }
    },
    "replicated": {
      "census": {
        "total": 5306112,
        "asA": 0,
        "asB": 0,
        "third": 0,
        "refused": 5306112,
        "uniqueA": 2304,
        "uniqueB": 2304,
        "maxA": 1,
        "maxB": 1,
        "distance": 4,
        "distanceHistogram": [
          0,
          0,
          0,
          0,
          44800,
          68880,
          490196,
          225008,
          1824172
        ],
        "witness": null
      },
      "clean": 2304,
      "oneErase": 18432,
      "twoErase": 64512,
      "singleSubRefused": 294912,
      "pcm": {
        "clean": {
          "correct": 6,
          "wrong": 0,
          "refused": 0,
          "unintended": 0,
          "expectedRefusal": 0
        },
        "gap-minus20": {
          "correct": 6,
          "wrong": 0,
          "refused": 0,
          "unintended": 0,
          "expectedRefusal": 0
        },
        "gap-plus25": {
          "correct": 6,
          "wrong": 0,
          "refused": 0,
          "unintended": 0,
          "expectedRefusal": 0
        },
        "piecewise": {
          "correct": 6,
          "wrong": 0,
          "refused": 0,
          "unintended": 0,
          "expectedRefusal": 0
        },
        "two-erasures": {
          "correct": 6,
          "wrong": 0,
          "refused": 0,
          "unintended": 0,
          "expectedRefusal": 0
        },
        "single-substitution": {
          "correct": 0,
          "wrong": 0,
          "refused": 6,
          "unintended": 0,
          "expectedRefusal": 0
        },
        "prior-splice": {
          "correct": 0,
          "wrong": 0,
          "refused": 0,
          "unintended": 0,
          "expectedRefusal": 6
        },
        "tag-splice": {
          "correct": 0,
          "wrong": 0,
          "refused": 0,
          "unintended": 0,
          "expectedRefusal": 6
        },
        "foreign": {
          "correct": 0,
          "wrong": 0,
          "refused": 0,
          "unintended": 6,
          "expectedRefusal": 0
        },
        "noise-only": {
          "correct": 0,
          "wrong": 0,
          "refused": 0,
          "unintended": 0,
          "expectedRefusal": 6
        }
      },
      "cleanEnergy": {
        "min": 61820069806,
        "max": 61838038351
      }
    }
  },
  "prior": {
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
  },
  "tag": {
    "a": 309,
    "b": 241,
    "c": 37
  },
  "peak": 4784
}
*/
