"use strict";
// Refs #452 / Grammars lane. Exploratory synthetic control grammar.
// Two labelled, honest reply paths are an explicit oracle assumption, NOT acoustic identity.
const M=require("./systematic-mds.cjs"),A=require("./algebraic-binding.cjs"),I=require("./integrity.cjs"),R=require("./recursive.cjs");
const parent="2615721f0f49431535ff62f55e8a3352483e2b5e",pinnedBlobs={"systematic-mds.cjs":"3e74ca6f76b0e9fdb267c5b4e5734828ca27ddf3","algebraic-binding.cjs":"7415235429fd86aa96bde3f69bcfe10cf5eb8fa2","recursive.cjs":"7d9e305857b59e029913432bb40f713ab84b5a90","integrity.cjs":"a58403f51806c17d89c7ebaf098d2e19b0995a02","injective-tags.cjs":"d91e0ed1e8700ff78b12e7732c07ddfcfc189e08","block-binding.cjs":"4c8be6987b345a5084dee16cf9e7053726c034c9","clock-hypotheses.cjs":"45a5fafb6506ba9211970c1cd58ac2840fbfc670","clock.cjs":"49a6849ae8a0094d30d499718ce21dd3029c0f8a","distributed.cjs":"c727fe13c7131e9a5eac9240fa909c34bcc5011c","acquisition.cjs":"70fb9823d596300112282a73386d6c6088b5d793","local-clock.cjs":"18e86536a85a7327499be1d5ff5719518d1a696a"};
const all=[0,1,2,3,4,5,6,7],key=x=>x.reduce((s,v)=>17*s+v,0),equal=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const masks=Array.from({length:256},(_,b)=>all.filter(j=>b&(1<<j))).filter(m=>m.length<=4);
const controlRows=[];
for(let side=0;side<2;side++)for(const j of all){controlRows.push([15,side,j,0]);for(let v=0;v<17;v++)controlRows.push([16,side,j,v]);}
const control=M.build(controlRows);
function encodeRequest(side,slot){const x=[15,side,slot,0];if(!control.map.has(key(x))||!Number.isInteger(side)||side<0||side>1||!all.includes(slot))throw Error("request");return M.encode(x);}
function encodeReply(side,slot,value){const x=[16,side,slot,value];if(!Number.isInteger(side)||side<0||side>1||!all.includes(slot)||!Number.isInteger(value)||value<0||value>16)throw Error("reply");return M.encode(x);}
function parseControl(observation){
 const k=M.decode(observation,control);if(k===null)return null;
 const [type,side,slot,value]=control.map.get(k);
 return {type:type===15?"request":"reply",side,slot,value:type===15?null:value};
}
function checkReply(observation,query,candidate){
 const t=parseControl(observation);
 return t!==null&&t.type==="reply"&&t.side===query.side&&t.slot===query.slot&&t.value===candidate[query.slot];
}
function groups(book,mask){
 const sides=[all.slice(0,4),all.slice(4)].map(s=>s.filter(j=>!mask.includes(j)));
 return sides.map(slots=>{
  const map=new Map(),lookup=[];
  for(let i=0;i<book.length;i++){
   const w=book[i],k=key(slots.map(j=>w[j]));let g=map.get(k);
   if(!g){g={ids:[],hist:Array.from({length:8},()=>new Uint32Array(17))};map.set(k,g);}
   g.ids.push(i);for(const j of all)g.hist[j][w[j]]++;lookup[i]=g;
  }
  return lookup;
 });
}
const policies=["strict","firstMissingBoth","adaptiveOne","adaptiveBoth"];
function plans(candidate,g,mask){
 const best=g.map((h,side)=>{
  if(h.ids.length===1)return null;
  let slot=0;for(const j of all)if(h.hist[j][candidate[j]]<h.hist[slot][candidate[slot]])slot=j;
  return {side,slot};
 });
 const ranked=best.filter(Boolean).sort((a,b)=>(
  g[a.side].hist[a.slot][candidate[a.slot]]*g[1-a.side].ids.length-
  g[b.side].hist[b.slot][candidate[b.slot]]*g[1-b.side].ids.length)||a.side-b.side);
 return {strict:[],firstMissingBoth:mask.length?[{side:0,slot:mask[0]},{side:1,slot:mask[0]}]:[],adaptiveOne:ranked.slice(0,1),adaptiveBoth:best.filter(Boolean)};
}
function sizes(candidate,g,queries){
 const n=g.map(h=>h.ids.length);
 for(const q of queries)n[q.side]=g[q.side].hist[q.slot][candidate[q.slot]];
 return n;
}
function empty(){return {asA:0,asB:0,third:0,queries:0,genuine:0,zeroQueries:0};}
function add(v,n,queries){
 v.asA+=n[1]-1;v.asB+=n[0]-1;v.third+=(n[0]-1)*(n[1]-1);
 v.queries+=queries.length;v.genuine++;v.zeroQueries+=+(queries.length===0);
}
function splice(book,a,b,mask){return [...book[a].slice(0,4),...book[b].slice(4)].map((v,j)=>mask.includes(j)?null:v);}
function qualify(){
 let assertions=0;function check(ok,why){assertions++;if(!ok)throw Error(why);}
 const result={},witnesses={},specimens=[],traces=[];let peak=0;
 for(const [version,rows] of [["original",A.versions.original],["expanded",A.versions.append]]){
  const codec=M.build(rows),book=codec.book;
  check(rows.every(x=>x[0]!==15&&x[0]!==16),"control namespace");
  const aggregate=Array.from({length:5},(_,erasures)=>({erasures,patterns:0,orderedPairs:0,policies:Object.fromEntries(policies.map(n=>[n,empty()]))}));
  for(const mask of masks){
   const g=groups(book,mask),s=aggregate[mask.length],local=Object.fromEntries(policies.map(n=>[n,empty()]));s.patterns++;s.orderedPairs+=book.length*(book.length-1);
   for(let c=0;c<book.length;c++){
    const candidate=book[c],gg=g.map(h=>h[c]),ps=plans(candidate,gg,mask);
    const observation=candidate.map((v,j)=>mask.includes(j)?null:v);
    check(M.decode(observation,codec)===key(rows[c]),"genuine strict");
    for(const policy of policies){
     const qs=ps[policy],n=sizes(candidate,gg,qs);
     check(n.every(v=>v>=1),"honest genuine reply survives");
     add(local[policy],n,qs);
    }
    const l=gg[0].ids.filter(i=>i!==c),rr=gg[1].ids.filter(i=>i!==c);
    if(l.length&&rr.length){
     const qs=ps.adaptiveBoth,accepted=(i,side)=>qs.filter(q=>q.side===side).every(q=>book[i][q.slot]===candidate[q.slot]);
     const a=l.find(i=>accepted(i,0)),b=rr.find(i=>accepted(i,1));
     for(const [kind,aa,bb] of [["rejected",l.find(i=>!accepted(i,0))??l[0],rr.find(i=>!accepted(i,1))??rr[0]],["survives",a,b]]){
      if(aa===undefined||bb===undefined||aa===bb||kind==="rejected"&&accepted(aa,0)&&accepted(bb,1))continue;
      const id=version+"-"+mask.length+"-"+kind;
      if(!witnesses[id])witnesses[id]={version,kind,a:aa,b:bb,c,mask,queries:qs,input:splice(book,aa,bb,mask)};
     }
    }
   }
   const exact=M.census(book,mask);for(const k of ["asA","asB","third"])check(local.strict[k]===exact[k],"pinned strict census");
   // Independent direct pair enumeration on a fixed mask; no projected multiplicity formula.
   if(version==="original"&&equal(mask,[0,4])){
    const projected=new Map(book.map((w,c)=>[key(w.filter((_,j)=>!mask.includes(j))),c]));
    const left=book.map(w=>key(w.slice(1,4))),right=book.map(w=>key(w.slice(5,8)));
    const direct=Object.fromEntries(policies.map(n=>[n,{asA:0,asB:0,third:0}]));
    for(let a=0;a<book.length;a++)for(let b=0;b<book.length;b++)if(a!==b){
     const c=projected.get(left[a]*4913+right[b]);if(c===undefined)continue;
     const ps=plans(book[c],g.map(h=>h[c]),mask);
     for(const policy of policies)if(ps[policy].every(q=>book[q.side===0?a:b][q.slot]===book[c][q.slot]))direct[policy][c===a?"asA":c===b?"asB":"third"]++;
    }
    for(const policy of policies)for(const k of ["asA","asB","third"])check(direct[policy][k]===local[policy][k],"independent direct pairs");
   }
   for(const policy of policies)for(const k of Object.keys(local[policy]))s.policies[policy][k]+=local[policy][k];
  }
  result[version]={catalogue:rows.length,aggregate};
 }
 // New control frames are actual PCM. Same eight slots, 640 ms body, no acquisition.
 function pcm(tokens,name,phase){
  const samples=I.render(tokens,phase),decoded=I.receive(samples),wav=R.wav(samples),v=new DataView(wav.buffer,wav.byteOffset,wav.byteLength);
  check(equal(decoded,tokens),"PCM tokens");check(v.getUint32(24,true)===16000&&v.getUint32(40,true)===samples.length*2,"WAV header");
  for(const sample of samples)peak=Math.max(peak,Math.abs(sample));
  if(phase===.137)specimens.push({name:name+".wav",tokens,phase});
  return decoded;
 }
 const chosen=Object.entries(witnesses).filter(([k])=>k.startsWith("original-")&&(/-2-|-4-/.test(k)));
 for(const [name,w] of chosen){
  const codec=M.build(A.versions.original),candidate=codec.book[w.c];
  for(const phase of [.137,2.419,5.827]){
   check(M.decode(pcm(w.input,name+"-splice",phase),codec)===key(codec.rows[w.c]),"splice candidate");
   let accepted=true;const replies=[];
   for(const q of w.queries){
    const request=parseControl(pcm(encodeRequest(q.side,q.slot),name+"-request-"+q.side,phase));
    check(request.type==="request"&&request.side===q.side&&request.slot===q.slot,"request");
    const actual=codec.book[q.side===0?w.a:w.b][q.slot];
    const response=pcm(encodeReply(q.side,q.slot,actual),name+"-reply-"+q.side,phase);
    const pass=checkReply(response,q,candidate);accepted=accepted&&pass;replies.push({query:q,actual,expected:candidate[q.slot],pass});
    check(!checkReply(response,{side:1-q.side,slot:q.slot},candidate),"wrong side refused");
    check(!checkReply(response,{side:q.side,slot:(q.slot+1)%8},candidate),"wrong slot refused");
    check(!checkReply(Array(8).fill(null),q,candidate),"missing reply refused");
   }
   check(accepted===(w.kind==="survives"),"witness result");
   traces.push({name,phase,candidate,replies,accepted});
  }
 }
 check(peak<=4096,"digital peak");
 return {schema:"mhac-clarification-v1",parent,pinnedBlobs,assertions,controlRows:controlRows.length,bodyMs:640,exchangeMs:1280,results:result,witnesses,traces,specimens,peak};
}
module.exports={encodeRequest,encodeReply,parseControl,checkReply,groups,plans,qualify};
if(require.main===module){
 const fs=require("node:fs"),path=require("node:path"),crypto=require("node:crypto");
 for(const [n,expected] of Object.entries(pinnedBlobs)){
  const bytes=fs.readFileSync(path.join(__dirname,n));
  if(crypto.createHash("sha1").update("blob "+bytes.length+"\0").update(bytes).digest("hex")!==expected)throw Error("pinned dependency changed: "+n);
 }
 const out=process.argv[2]||"output-clarification";fs.mkdirSync(out,{recursive:true});
 const q=qualify(),manifest=[];
 for(const s of q.specimens){const bytes=R.wav(I.render(s.tokens,s.phase));fs.writeFileSync(path.join(out,s.name),bytes);manifest.push({...s,sha256:crypto.createHash("sha256").update(bytes).digest("hex")});}
 fs.writeFileSync(path.join(out,"qualification.json"),JSON.stringify(q,null,2)+"\n");
 fs.writeFileSync(path.join(out,"stimuli.json"),JSON.stringify(manifest,null,2)+"\n");
 fs.writeFileSync(path.join(out,"index.html"),'<!doctype html><meta charset="utf-8"><title>Clarification controls</title><h1>Synthetic clarification controls</h1><p>Start at low volume. No autoplay; machine-code specimens only.</p>'+manifest.map(s=>'<h2>'+s.name+'</h2><audio controls preload="none" src="'+s.name+'"></audio><pre>'+JSON.stringify(s.tokens)+'</pre>').join(""));
 console.log(JSON.stringify({assertions:q.assertions,results:q.results,peak:q.peak},null,2));
}

/*
Run 013 / 2026-11-25 / Refs #452 / Draft #453. Main 495a98ca12bae467a507031f04931aa4254b1866; parent 2615721f0f49431535ff62f55e8a3352483e2b5e. One AI agent, no subagents. Exploratory exact finite ordered splice census, no physical-channel probability. Control namespace is disjoint from the pinned expression catalogues; explicit request and reply roles, side and slot. Honest labelled source reply paths are stipulated, not provided or authenticated by acoustics; stale replies or impersonation can defeat this scheme. No automatic action permission or human evidence. Strict control decoding, aligned bodies only, no synchronization or streaming qualification. Cost 640 ms per body, 1280 ms per query/reply exchange, not including guard, preamble, processing or waiting. All genuine counts assume replies arrive; absent/mismatched replies refuse confirmation. Adaptive choice uses only candidate, mask and catalogue; no true source identity in selection. Comparison uses the same initial body and variable explicit extra transmission cost. No claim of matched total airtime. Two identical V8 executions of actual pinned dependencies; native Node 22.16.0 available but GitHub DNS resolution failed (git ls-remote exit 128). Native CLI, filesystem, SHA manifest, browser and physical audition not tested. Results below; replay via node clarification-controls.cjs output-clarification.
{
  "assertions": 4405433,
  "controlRows": 288,
  "results": {
    "original": {
      "catalogue": 2304,
      "aggregate": [
        {
          "erasures": 0,
          "patterns": 1,
          "orderedPairs": 5306112,
          "policies": {
            "strict": {
              "asA": 0,
              "asB": 0,
              "third": 0,
              "queries": 0,
              "genuine": 2304,
              "zeroQueries": 2304
            },
            "firstMissingBoth": {
              "asA": 0,
              "asB": 0,
              "third": 0,
              "queries": 0,
              "genuine": 2304,
              "zeroQueries": 2304
            },
            "adaptiveOne": {
              "asA": 0,
              "asB": 0,
              "third": 0,
              "queries": 0,
              "genuine": 2304,
              "zeroQueries": 2304
            },
            "adaptiveBoth": {
              "asA": 0,
              "asB": 0,
              "third": 0,
              "queries": 0,
              "genuine": 2304,
              "zeroQueries": 2304
            }
          }
        },
        {
          "erasures": 1,
          "patterns": 8,
          "orderedPairs": 42448896,
          "policies": {
            "strict": {
              "asA": 16924,
              "asB": 8410,
              "third": 0,
              "queries": 0,
              "genuine": 18432,
              "zeroQueries": 18432
            },
            "firstMissingBoth": {
              "asA": 0,
              "asB": 0,
              "third": 0,
              "queries": 36864,
              "genuine": 18432,
              "zeroQueries": 0
            },
            "adaptiveOne": {
              "asA": 0,
              "asB": 0,
              "third": 0,
              "queries": 13294,
              "genuine": 18432,
              "zeroQueries": 5138
            },
            "adaptiveBoth": {
              "asA": 0,
              "asB": 0,
              "third": 0,
              "queries": 13294,
              "genuine": 18432,
              "zeroQueries": 5138
            }
          }
        },
        {
          "erasures": 2,
          "patterns": 28,
          "orderedPairs": 148571136,
          "policies": {
            "strict": {
              "asA": 381644,
              "asB": 234964,
              "third": 65005,
              "queries": 0,
              "genuine": 64512,
              "zeroQueries": 64512
            },
            "firstMissingBoth": {
              "asA": 31768,
              "asB": 15432,
              "third": 0,
              "queries": 129024,
              "genuine": 64512,
              "zeroQueries": 0
            },
            "adaptiveOne": {
              "asA": 16400,
              "asB": 13992,
              "third": 0,
              "queries": 61749,
              "genuine": 64512,
              "zeroQueries": 2763
            },
            "adaptiveBoth": {
              "asA": 5209,
              "asB": 912,
              "third": 0,
              "queries": 80769,
              "genuine": 64512,
              "zeroQueries": 2763
            }
          }
        },
        {
          "erasures": 3,
          "patterns": 56,
          "orderedPairs": 297142272,
          "policies": {
            "strict": {
              "asA": 3564750,
              "asB": 2563900,
              "third": 2700035,
              "queries": 0,
              "genuine": 129024,
              "zeroQueries": 129024
            },
            "firstMissingBoth": {
              "asA": 371908,
              "asB": 253752,
              "third": 0,
              "queries": 258048,
              "genuine": 129024,
              "zeroQueries": 0
            },
            "adaptiveOne": {
              "asA": 221659,
              "asB": 131820,
              "third": 27488,
              "queries": 128925,
              "genuine": 129024,
              "zeroQueries": 99
            },
            "adaptiveBoth": {
              "asA": 121533,
              "asB": 80634,
              "third": 0,
              "queries": 208564,
              "genuine": 129024,
              "zeroQueries": 99
            }
          }
        },
        {
          "erasures": 4,
          "patterns": 70,
          "orderedPairs": 371427840,
          "policies": {
            "strict": {
              "asA": 16087152,
              "asB": 13380272,
              "third": 48610583,
              "queries": 0,
              "genuine": 161280,
              "zeroQueries": 161280
            },
            "firstMissingBoth": {
              "asA": 1334578,
              "asB": 1446788,
              "third": 177340,
              "queries": 322560,
              "genuine": 161280,
              "zeroQueries": 0
            },
            "adaptiveOne": {
              "asA": 1424701,
              "asB": 1076748,
              "third": 1209538,
              "queries": 161266,
              "genuine": 161280,
              "zeroQueries": 14
            },
            "adaptiveBoth": {
              "asA": 710590,
              "asB": 589964,
              "third": 2347,
              "queries": 297054,
              "genuine": 161280,
              "zeroQueries": 14
            }
          }
        }
      ]
    },
    "expanded": {
      "catalogue": 3100,
      "aggregate": [
        {
          "erasures": 0,
          "patterns": 1,
          "orderedPairs": 9606900,
          "policies": {
            "strict": {
              "asA": 0,
              "asB": 0,
              "third": 0,
              "queries": 0,
              "genuine": 3100,
              "zeroQueries": 3100
            },
            "firstMissingBoth": {
              "asA": 0,
              "asB": 0,
              "third": 0,
              "queries": 0,
              "genuine": 3100,
              "zeroQueries": 3100
            },
            "adaptiveOne": {
              "asA": 0,
              "asB": 0,
              "third": 0,
              "queries": 0,
              "genuine": 3100,
              "zeroQueries": 3100
            },
            "adaptiveBoth": {
              "asA": 0,
              "asB": 0,
              "third": 0,
              "queries": 0,
              "genuine": 3100,
              "zeroQueries": 3100
            }
          }
        },
        {
          "erasures": 1,
          "patterns": 8,
          "orderedPairs": 76855200,
          "policies": {
            "strict": {
              "asA": 24030,
              "asB": 14772,
              "third": 0,
              "queries": 0,
              "genuine": 24800,
              "zeroQueries": 24800
            },
            "firstMissingBoth": {
              "asA": 0,
              "asB": 0,
              "third": 0,
              "queries": 49600,
              "genuine": 24800,
              "zeroQueries": 0
            },
            "adaptiveOne": {
              "asA": 0,
              "asB": 0,
              "third": 0,
              "queries": 19568,
              "genuine": 24800,
              "zeroQueries": 5232
            },
            "adaptiveBoth": {
              "asA": 0,
              "asB": 0,
              "third": 0,
              "queries": 19568,
              "genuine": 24800,
              "zeroQueries": 5232
            }
          }
        },
        {
          "erasures": 2,
          "patterns": 28,
          "orderedPairs": 268993200,
          "policies": {
            "strict": {
              "asA": 565908,
              "asB": 416610,
              "third": 117614,
              "queries": 0,
              "genuine": 86800,
              "zeroQueries": 86800
            },
            "firstMissingBoth": {
              "asA": 43618,
              "asB": 26270,
              "third": 0,
              "queries": 173600,
              "genuine": 86800,
              "zeroQueries": 0
            },
            "adaptiveOne": {
              "asA": 28444,
              "asB": 24965,
              "third": 0,
              "queries": 84550,
              "genuine": 86800,
              "zeroQueries": 2250
            },
            "adaptiveBoth": {
              "asA": 7730,
              "asB": 3320,
              "third": 0,
              "queries": 115406,
              "genuine": 86800,
              "zeroQueries": 2250
            }
          }
        },
        {
          "erasures": 3,
          "patterns": 56,
          "orderedPairs": 537986400,
          "policies": {
            "strict": {
              "asA": 5593022,
              "asB": 4565754,
              "third": 5099701,
              "queries": 0,
              "genuine": 173600,
              "zeroQueries": 173600
            },
            "firstMissingBoth": {
              "asA": 537090,
              "asB": 443054,
              "third": 0,
              "queries": 347200,
              "genuine": 173600,
              "zeroQueries": 0
            },
            "adaptiveOne": {
              "asA": 335266,
              "asB": 242856,
              "third": 65183,
              "queries": 173500,
              "genuine": 173600,
              "zeroQueries": 100
            },
            "adaptiveBoth": {
              "asA": 192198,
              "asB": 153711,
              "third": 0,
              "queries": 290739,
              "genuine": 173600,
              "zeroQueries": 100
            }
          }
        },
        {
          "erasures": 4,
          "patterns": 70,
          "orderedPairs": 672483000,
          "policies": {
            "strict": {
              "asA": 26800508,
              "asB": 23999256,
              "third": 95568944,
              "queries": 0,
              "genuine": 217000,
              "zeroQueries": 217000
            },
            "firstMissingBoth": {
              "asA": 2163860,
              "asB": 2573246,
              "third": 326585,
              "queries": 434000,
              "genuine": 217000,
              "zeroQueries": 0
            },
            "adaptiveOne": {
              "asA": 2428509,
              "asB": 1960810,
              "third": 2321327,
              "queries": 216988,
              "genuine": 217000,
              "zeroQueries": 12
            },
            "adaptiveBoth": {
              "asA": 1193673,
              "asB": 1083825,
              "third": 8879,
              "queries": 406456,
              "genuine": 217000,
              "zeroQueries": 12
            }
          }
        }
      ]
    }
  },
  "witnesses": {
    "original-2-rejected": {
      "version": "original",
      "kind": "rejected",
      "a": 1950,
      "b": 202,
      "c": 7,
      "mask": [
        0,
        4
      ],
      "queries": [
        {
          "side": 0,
          "slot": 0
        },
        {
          "side": 1,
          "slot": 0
        }
      ],
      "input": [
        null,
        3,
        4,
        3,
        null,
        13,
        16,
        1
      ]
    },
    "original-3-rejected": {
      "version": "original",
      "kind": "rejected",
      "a": 461,
      "b": 48,
      "c": 0,
      "mask": [
        0,
        1,
        4
      ],
      "queries": [
        {
          "side": 0,
          "slot": 0
        },
        {
          "side": 1,
          "slot": 0
        }
      ],
      "input": [
        null,
        null,
        5,
        2,
        null,
        13,
        11,
        16
      ]
    },
    "original-4-rejected": {
      "version": "original",
      "kind": "rejected",
      "a": 5,
      "b": 48,
      "c": 0,
      "mask": [
        0,
        1,
        2,
        4
      ],
      "queries": [
        {
          "side": 0,
          "slot": 0
        },
        {
          "side": 1,
          "slot": 0
        }
      ],
      "input": [
        null,
        null,
        null,
        2,
        null,
        13,
        11,
        16
      ]
    },
    "original-4-survives": {
      "version": "original",
      "kind": "survives",
      "a": 62,
      "b": 214,
      "c": 512,
      "mask": [
        1,
        2,
        4,
        5
      ],
      "queries": [
        {
          "side": 0,
          "slot": 1
        },
        {
          "side": 1,
          "slot": 2
        }
      ],
      "input": [
        5,
        null,
        null,
        11,
        null,
        null,
        2,
        3
      ]
    },
    "expanded-2-rejected": {
      "version": "expanded",
      "kind": "rejected",
      "a": 1894,
      "b": 2319,
      "c": 5,
      "mask": [
        0,
        4
      ],
      "queries": [
        {
          "side": 0,
          "slot": 0
        },
        {
          "side": 1,
          "slot": 0
        }
      ],
      "input": [
        null,
        1,
        2,
        2,
        null,
        13,
        14,
        11
      ]
    },
    "expanded-3-rejected": {
      "version": "expanded",
      "kind": "rejected",
      "a": 461,
      "b": 48,
      "c": 0,
      "mask": [
        0,
        1,
        4
      ],
      "queries": [
        {
          "side": 0,
          "slot": 0
        },
        {
          "side": 1,
          "slot": 0
        }
      ],
      "input": [
        null,
        null,
        5,
        2,
        null,
        13,
        11,
        16
      ]
    },
    "expanded-4-rejected": {
      "version": "expanded",
      "kind": "rejected",
      "a": 5,
      "b": 48,
      "c": 0,
      "mask": [
        0,
        1,
        2,
        4
      ],
      "queries": [
        {
          "side": 0,
          "slot": 0
        },
        {
          "side": 1,
          "slot": 0
        }
      ],
      "input": [
        null,
        null,
        null,
        2,
        null,
        13,
        11,
        16
      ]
    },
    "expanded-4-survives": {
      "version": "expanded",
      "kind": "survives",
      "a": 2825,
      "b": 1063,
      "c": 982,
      "mask": [
        0,
        1,
        4,
        5
      ],
      "queries": [
        {
          "side": 0,
          "slot": 4
        },
        {
          "side": 1,
          "slot": 0
        }
      ],
      "input": [
        null,
        null,
        14,
        15,
        null,
        null,
        1,
        1
      ]
    }
  },
  "traces": [
    {
      "name": "original-2-rejected",
      "phase": 0.137,
      "candidate": [
        4,
        3,
        4,
        3,
        13,
        13,
        16,
        1
      ],
      "replies": [
        {
          "query": {
            "side": 0,
            "slot": 0
          },
          "actual": 11,
          "expected": 4,
          "pass": false
        },
        {
          "query": {
            "side": 1,
            "slot": 0
          },
          "actual": 10,
          "expected": 4,
          "pass": false
        }
      ],
      "accepted": false
    },
    {
      "name": "original-4-rejected",
      "phase": 0.137,
      "candidate": [
        0,
        13,
        5,
        2,
        13,
        13,
        11,
        16
      ],
      "replies": [
        {
          "query": {
            "side": 0,
            "slot": 0
          },
          "actual": 4,
          "expected": 0,
          "pass": false
        },
        {
          "query": {
            "side": 1,
            "slot": 0
          },
          "actual": 4,
          "expected": 0,
          "pass": false
        }
      ],
      "accepted": false
    },
    {
      "name": "original-4-survives",
      "phase": 0.137,
      "candidate": [
        5,
        4,
        16,
        11,
        10,
        0,
        2,
        3
      ],
      "replies": [
        {
          "query": {
            "side": 0,
            "slot": 1
          },
          "actual": 4,
          "expected": 4,
          "pass": true
        },
        {
          "query": {
            "side": 1,
            "slot": 2
          },
          "actual": 16,
          "expected": 16,
          "pass": true
        }
      ],
      "accepted": true
    }
  ],
  "specimens": 15,
  "peak": 4096
}
*/
