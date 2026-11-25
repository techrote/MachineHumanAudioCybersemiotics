"use strict";
// Refs #452 / Grammars lane / Run 014. Synthetic, honest separately addressed replies.
// Candidate agreement is not the same as proving that both source fragments match.
const M=require("./systematic-mds.cjs"), C=require("./clarification-controls.cjs"),
 A=require("./algebraic-binding.cjs"), I=require("./integrity.cjs"), R=require("./recursive.cjs");
const parent="dc8c5b03ce03861adeab192eef72da5abf3994cb", pinnedBlobs={"clarification-controls.cjs":"9434b7134f23c54e3870f78efcc84fa145a70d2d","systematic-mds.cjs":"3e74ca6f76b0e9fdb267c5b4e5734828ca27ddf3","algebraic-binding.cjs":"7415235429fd86aa96bde3f69bcfe10cf5eb8fa2","recursive.cjs":"7d9e305857b59e029913432bb40f713ab84b5a90","integrity.cjs":"a58403f51806c17d89c7ebaf098d2e19b0995a02","injective-tags.cjs":"d91e0ed1e8700ff78b12e7732c07ddfcfc189e08","block-binding.cjs":"4c8be6987b345a5084dee16cf9e7053726c034c9","clock-hypotheses.cjs":"45a5fafb6506ba9211970c1cd58ac2840fbfc670","clock.cjs":"49a6849ae8a0094d30d499718ce21dd3029c0f8a","distributed.cjs":"c727fe13c7131e9a5eac9240fa909c34bcc5011c","acquisition.cjs":"70fb9823d596300112282a73386d6c6088b5d793","local-clock.cjs":"18e86536a85a7327499be1d5ff5719518d1a696a"};
const all=[0,1,2,3,4,5,6,7], key=x=>x.reduce((s,v)=>17*s+v,0);
const equal=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const masks=Array.from({length:256},(_,b)=>all.filter(j=>b&(1<<j))).filter(m=>m.length<=4);
function groups(book,slots){
 const map=new Map();
 return book.map((w,i)=>{const k=key(slots.map(j=>w[j]));let g=map.get(k);
 if(!g){g=[];map.set(k,g);}g.push(i);return g;});
}
// Along the all-agree path, greedily reduce the candidate-compatible source set.
// The candidate must be present. No ground truth or actual respondent consulted.
function sidePlan(book,c,ids,side){
 const candidate=book[c],steps=[],sizes=[ids.length];let remain=ids;
 while(remain.length>1){
  let best=-1,min=remain.length;
  for(const j of all){
   let count=0;for(const i of remain)count+=+(book[i][j]===candidate[j]);
   if(count<min){min=count;best=j;}
  }
  if(best<0||min<1||steps.length>=4)throw Error("invalid source refinement");
  steps.push({side,slot:best});remain=remain.filter(i=>book[i][best]===candidate[best]);sizes.push(remain.length);
 }
 return {steps,sizes};
}
function session(observation,codec,cap,reply){
 if(!Number.isInteger(cap)||cap<0||cap>4)throw Error("cap");
 const k=M.decode(observation,codec);
 if(k===null)return {status:"refused",reason:"invalid body",trace:[]};
 const c=codec.rows.findIndex(x=>key(x)===k),candidate=codec.book[c],trace=[];
 const plans=[0,1].map(side=>sidePlan(codec.book,c,codec.book.map((_,i)=>i).filter(i=>all.filter(j=>Math.floor(j/4)===side&&observation[j]!==null).every(j=>codec.book[i][j]===observation[j])),side));
 const residual=plans.map(p=>p.sizes[0]);
 // Interleave sides; stop on the first disagreeing/missing reply. The caller is the transport.
 for(let round=0;round<cap;round++)for(const side of [0,1]){
  const q=plans[side].steps[round];if(!q)continue;
  const response=reply(C.encodeRequest(side,q.slot),q);
  const pass=C.checkReply(response,q,candidate);
  if(pass)residual[side]=plans[side].sizes[round+1];
  trace.push({query:q,request:C.encodeRequest(side,q.slot),response,pass,residual:[...residual]});
  if(!pass)return {status:"refused",reason:"reply missing or contradictory",candidate:c,trace,residual};
 }
 return {status:residual.every(n=>n===1)?"certified":"provisional",candidate:c,trace,residual};
}
function qualify(){
 let assertions=0;const check=(ok,msg)=>{assertions++;if(!ok)throw Error(msg);};
 const results={};
 for(const [version,rows] of [["original",A.versions.original],["expanded",A.versions.append]]){
  const codec=M.build(rows),book=codec.book,N=book.length;
  const aggregate=Array.from({length:5},(_,e)=>({e,patterns:0,orderedPairs:0,genuine:0,caps:Array.from({length:5},()=>({asA:0,asB:0,third:0,queries:0,certified:0,maxQueries:0}))}));
  for(const mask of masks){
   const out=aggregate[mask.length],g=[0,1].map(side=>groups(book,all.filter(j=>Math.floor(j/4)===side&&!mask.includes(j))));
   out.patterns++;out.orderedPairs+=N*(N-1);out.genuine+=N;
   let direct=0;
   for(let c=0;c<N;c++){
    const p=g.map((gg,s)=>sidePlan(book,c,gg[c],s));
    check(p.every(x=>x.sizes.at(-1)===1&&x.steps.length<=4),"complete certificate");
    // Four retained or queried distinct coordinates uniquely determine the MDS word.
    for(let s=0;s<2;s++)check(new Set(p[s].steps.map(q=>q.slot)).size===p[s].steps.length,"distinct query positions");
    for(let cap=0;cap<=4;cap++){
     const n=p.map(x=>x.sizes[Math.min(cap,x.steps.length)]),q=p.reduce((sum,x)=>sum+Math.min(cap,x.steps.length),0),v=out.caps[cap];
     v.asA+=n[1]-1;v.asB+=n[0]-1;v.third+=(n[0]-1)*(n[1]-1);v.queries+=q;v.certified+=+(n[0]===1&&n[1]===1);v.maxQueries=Math.max(v.maxQueries,q);
     check(n[0]>=1&&n[1]>=1&&q<=8,"bounds");
     if(cap===1&&equal(mask,[0,4]))direct+=(n[0]-1)*(n[1]-1);
    }
   }
   if(version==="original"&&equal(mask,[0,4])){
    // Independent ordered-pair cross-check, using actual session plans for each accepted projection.
    const observed=all.filter(j=>!mask.includes(j)),projected=new Map(book.map((w,c)=>[key(observed.map(j=>w[j])),c]));
    const left=book.map(w=>key(w.slice(1,4))),right=book.map(w=>key(w.slice(5,8)));
    const p=book.map((_,c)=>g.map((gg,s)=>sidePlan(book,c,gg[c],s).steps[0]));
    let count=0;
    for(let a=0;a<N;a++)for(let b=0;b<N;b++)if(a!==b){
     const c=projected.get(left[a]*4913+right[b]);if(c===undefined||c===a||c===b)continue;
     if(p[c].every((q,s)=>!q||book[s===0?a:b][q.slot]===book[c][q.slot]))count++;
    }
    check(count===direct,"direct pair check");
   }
  }
  const prior=version==="original"?[0,0,65005,2700035,48610583]:[0,0,117614,5099701,95568944],
   priorOne=version==="original"?[0,0,0,0,2347]:[0,0,0,0,8879];
  for(const o of aggregate){
   check(o.caps[0].third===prior[o.e]&&o.caps[1].third===priorOne[o.e],"Run 013 reproduction");
   check(o.caps[4].third+o.caps[4].asA+o.caps[4].asB===0&&o.caps[4].certified===o.genuine,"full certificate");
   for(let i=1;i<5;i++)check(o.caps[i].third<=o.caps[i-1].third&&o.caps[i].certified>=o.caps[i-1].certified,"monotone");
  }
  results[version]={catalogue:N,aggregate};
 }
 const codec=M.build(A.versions.original),book=codec.book,scenarios=[
  {name:"truthful-splice",a:62,b:214,c:512,mask:[1,2,4,5]},
  {name:"genuine-512",a:512,b:512,c:512,mask:[1,2,4,5]},
  {name:"all-left-erased",a:62,b:214,c:214,mask:[0,1,2,3]},
  {name:"missing-reply",a:512,b:512,c:512,mask:[1,2,4,5],missing:true}
 ];
 const traces=[],specimens=[];let peak=0;
 for(const phase of [.137,2.419,5.827])for(const s of scenarios){
  function pcm(tokens,label){
   const samples=I.render(tokens,phase),wav=R.wav(samples),v=new DataView(wav.buffer,wav.byteOffset,wav.byteLength);
   check(equal(I.receive(samples),tokens),"aligned PCM round trip");
   check(v.getUint32(24,true)===16000&&v.getUint32(40,true)===samples.length*2,"wav header");
   for(const x of samples)peak=Math.max(peak,Math.abs(x));
   if(phase===.137)specimens.push({name:s.name+"-"+label+".wav",tokens,phase});
   return I.receive(samples);
  }
  const observation=pcm([...book[s.a].slice(0,4),...book[s.b].slice(4)].map((v,j)=>s.mask.includes(j)?null:v),"body");
  let n=0;
  const t=session(observation,codec,4,(request,q)=>{
   const parsed=C.parseControl(pcm(request,"request-"+n));check(parsed.type==="request"&&parsed.side===q.side&&parsed.slot===q.slot,"request round trip");
   if(s.missing)return Array(8).fill(null);
   return pcm(C.encodeReply(q.side,q.slot,book[q.side===0?s.a:s.b][q.slot]),"reply-"+n++);
  });
  check(t.candidate===s.c,"candidate");
  check(t.status===(s.a===s.b&&!s.missing?"certified":"refused"),"witness");
  if(s.name==="truthful-splice"){const p=session(observation,codec,1,(_,q)=>C.encodeReply(q.side,q.slot,book[q.side===0?s.a:s.b][q.slot]));check(p.status==="provisional"&&p.trace.every(q=>q.pass),"previous truthful failure reproduced");}
  traces.push({scenario:s.name,phase,...t});
 }
 check(peak<=4096,"peak");
 return {schema:"mhac-sequential-clarification-v1",parent,pinnedBlobs,assertions,bodyMs:640,exchangeMs:1280,results,traces,specimens,peak};
}
module.exports={sidePlan,session,qualify};
if(require.main===module){
 const fs=require("node:fs"),path=require("node:path"),crypto=require("node:crypto");
 for(const [n,expected] of Object.entries(pinnedBlobs)){
  const bytes=fs.readFileSync(path.join(__dirname,n));
  if(crypto.createHash("sha1").update("blob "+bytes.length+"\0").update(bytes).digest("hex")!==expected)throw Error("dependency changed: "+n);
 }
 const out=process.argv[2]||"output-sequential";fs.mkdirSync(out,{recursive:true});
 const q=qualify(),manifest=[];
 for(const s of q.specimens){const bytes=R.wav(I.render(s.tokens,s.phase));fs.writeFileSync(path.join(out,s.name),bytes);manifest.push({...s,sha256:crypto.createHash("sha256").update(bytes).digest("hex")});}
 fs.writeFileSync(path.join(out,"qualification.json"),JSON.stringify(q,null,2)+"\n");
 fs.writeFileSync(path.join(out,"stimuli.json"),JSON.stringify(manifest,null,2)+"\n");
 fs.writeFileSync(path.join(out,"index.html"),'<!doctype html><meta charset="utf-8"><title>Sequential clarification</title><h1>Synthetic sequential clarification</h1><p>Start at low volume. No autoplay. Aligned machine-code bodies; no human evidence.</p>'+manifest.map(s=>'<h2>'+s.name+'</h2><audio controls preload="none" src="'+s.name+'"></audio><pre>'+JSON.stringify(s.tokens)+'</pre>').join("")+'<h2>Replay traces</h2><pre>'+JSON.stringify(q.traces,null,2)+'</pre>');
 console.log(JSON.stringify({assertions:q.assertions,results:q.results,peak:q.peak},null,2));
}

/*
Run 014 / 2026-11-25 / Refs #452. Main 495a98ca12bae467a507031f04931aa4254b1866. One AI agent, no subagents. Actual pinned connector sources, matching reported Git blob IDs; two identical V8 runs. Native Node 22.16.0 available but git retrieval failed DNS exit 128; native filesystem export, browser, physical audition and streaming untested. Candidate-relative greedy queries, exact finite ordered half-splices, honest independently addressable respondents, shared catalogue and no stale replies. A certificate is relative to these assumptions, not authentication or permission to act. Cap is per respondent; provisional accepts every agreeing reply but is explicitly not certified. Census counts all-agree paths only; query totals are genuine cases, not all mixed traffic; cost excludes preamble, waiting, processing, guards. Strict baseline and one-query bilateral reproduced. No canonical records or human evidence. Results:
{
  "assertions": 7047058,
  "results": {
    "original": {
      "catalogue": 2304,
      "aggregate": [
        {
          "e": 0,
          "patterns": 1,
          "orderedPairs": 5306112,
          "genuine": 2304,
          "caps": [
            {
              "asA": 0,
              "asB": 0,
              "third": 0,
              "queries": 0,
              "certified": 2304,
              "maxQueries": 0
            },
            {
              "asA": 0,
              "asB": 0,
              "third": 0,
              "queries": 0,
              "certified": 2304,
              "maxQueries": 0
            },
            {
              "asA": 0,
              "asB": 0,
              "third": 0,
              "queries": 0,
              "certified": 2304,
              "maxQueries": 0
            },
            {
              "asA": 0,
              "asB": 0,
              "third": 0,
              "queries": 0,
              "certified": 2304,
              "maxQueries": 0
            },
            {
              "asA": 0,
              "asB": 0,
              "third": 0,
              "queries": 0,
              "certified": 2304,
              "maxQueries": 0
            }
          ]
        },
        {
          "e": 1,
          "patterns": 8,
          "orderedPairs": 42448896,
          "genuine": 18432,
          "caps": [
            {
              "asA": 16924,
              "asB": 8410,
              "third": 0,
              "queries": 0,
              "certified": 5138,
              "maxQueries": 0
            },
            {
              "asA": 0,
              "asB": 0,
              "third": 0,
              "queries": 13294,
              "certified": 18432,
              "maxQueries": 1
            },
            {
              "asA": 0,
              "asB": 0,
              "third": 0,
              "queries": 13294,
              "certified": 18432,
              "maxQueries": 1
            },
            {
              "asA": 0,
              "asB": 0,
              "third": 0,
              "queries": 13294,
              "certified": 18432,
              "maxQueries": 1
            },
            {
              "asA": 0,
              "asB": 0,
              "third": 0,
              "queries": 13294,
              "certified": 18432,
              "maxQueries": 1
            }
          ]
        },
        {
          "e": 2,
          "patterns": 28,
          "orderedPairs": 148571136,
          "genuine": 64512,
          "caps": [
            {
              "asA": 381644,
              "asB": 234964,
              "third": 65005,
              "queries": 0,
              "certified": 2763,
              "maxQueries": 0
            },
            {
              "asA": 5209,
              "asB": 912,
              "third": 0,
              "queries": 80769,
              "certified": 59588,
              "maxQueries": 2
            },
            {
              "asA": 0,
              "asB": 0,
              "third": 0,
              "queries": 85693,
              "certified": 64512,
              "maxQueries": 2
            },
            {
              "asA": 0,
              "asB": 0,
              "third": 0,
              "queries": 85693,
              "certified": 64512,
              "maxQueries": 2
            },
            {
              "asA": 0,
              "asB": 0,
              "third": 0,
              "queries": 85693,
              "certified": 64512,
              "maxQueries": 2
            }
          ]
        },
        {
          "e": 3,
          "patterns": 56,
          "orderedPairs": 297142272,
          "genuine": 129024,
          "caps": [
            {
              "asA": 3564750,
              "asB": 2563900,
              "third": 2700035,
              "queries": 0,
              "certified": 99,
              "maxQueries": 0
            },
            {
              "asA": 121533,
              "asB": 80634,
              "third": 0,
              "queries": 208564,
              "certified": 91011,
              "maxQueries": 2
            },
            {
              "asA": 973,
              "asB": 71,
              "third": 0,
              "queries": 246577,
              "certified": 128000,
              "maxQueries": 3
            },
            {
              "asA": 0,
              "asB": 0,
              "third": 0,
              "queries": 247601,
              "certified": 129024,
              "maxQueries": 3
            },
            {
              "asA": 0,
              "asB": 0,
              "third": 0,
              "queries": 247601,
              "certified": 129024,
              "maxQueries": 3
            }
          ]
        },
        {
          "e": 4,
          "patterns": 70,
          "orderedPairs": 371427840,
          "genuine": 161280,
          "caps": [
            {
              "asA": 16087152,
              "asB": 13380272,
              "third": 48610583,
              "queries": 0,
              "certified": 14,
              "maxQueries": 0
            },
            {
              "asA": 710590,
              "asB": 589964,
              "third": 2347,
              "queries": 297054,
              "certified": 55652,
              "maxQueries": 2
            },
            {
              "asA": 15447,
              "asB": 11839,
              "third": 0,
              "queries": 404466,
              "certified": 152606,
              "maxQueries": 4
            },
            {
              "asA": 2,
              "asB": 2,
              "third": 0,
              "queries": 413140,
              "certified": 161276,
              "maxQueries": 4
            },
            {
              "asA": 0,
              "asB": 0,
              "third": 0,
              "queries": 413144,
              "certified": 161280,
              "maxQueries": 4
            }
          ]
        }
      ]
    },
    "expanded": {
      "catalogue": 3100,
      "aggregate": [
        {
          "e": 0,
          "patterns": 1,
          "orderedPairs": 9606900,
          "genuine": 3100,
          "caps": [
            {
              "asA": 0,
              "asB": 0,
              "third": 0,
              "queries": 0,
              "certified": 3100,
              "maxQueries": 0
            },
            {
              "asA": 0,
              "asB": 0,
              "third": 0,
              "queries": 0,
              "certified": 3100,
              "maxQueries": 0
            },
            {
              "asA": 0,
              "asB": 0,
              "third": 0,
              "queries": 0,
              "certified": 3100,
              "maxQueries": 0
            },
            {
              "asA": 0,
              "asB": 0,
              "third": 0,
              "queries": 0,
              "certified": 3100,
              "maxQueries": 0
            },
            {
              "asA": 0,
              "asB": 0,
              "third": 0,
              "queries": 0,
              "certified": 3100,
              "maxQueries": 0
            }
          ]
        },
        {
          "e": 1,
          "patterns": 8,
          "orderedPairs": 76855200,
          "genuine": 24800,
          "caps": [
            {
              "asA": 24030,
              "asB": 14772,
              "third": 0,
              "queries": 0,
              "certified": 5232,
              "maxQueries": 0
            },
            {
              "asA": 0,
              "asB": 0,
              "third": 0,
              "queries": 19568,
              "certified": 24800,
              "maxQueries": 1
            },
            {
              "asA": 0,
              "asB": 0,
              "third": 0,
              "queries": 19568,
              "certified": 24800,
              "maxQueries": 1
            },
            {
              "asA": 0,
              "asB": 0,
              "third": 0,
              "queries": 19568,
              "certified": 24800,
              "maxQueries": 1
            },
            {
              "asA": 0,
              "asB": 0,
              "third": 0,
              "queries": 19568,
              "certified": 24800,
              "maxQueries": 1
            }
          ]
        },
        {
          "e": 2,
          "patterns": 28,
          "orderedPairs": 268993200,
          "genuine": 86800,
          "caps": [
            {
              "asA": 565908,
              "asB": 416610,
              "third": 117614,
              "queries": 0,
              "certified": 2250,
              "maxQueries": 0
            },
            {
              "asA": 7730,
              "asB": 3320,
              "third": 0,
              "queries": 115406,
              "certified": 77543,
              "maxQueries": 2
            },
            {
              "asA": 0,
              "asB": 0,
              "third": 0,
              "queries": 124663,
              "certified": 86800,
              "maxQueries": 2
            },
            {
              "asA": 0,
              "asB": 0,
              "third": 0,
              "queries": 124663,
              "certified": 86800,
              "maxQueries": 2
            },
            {
              "asA": 0,
              "asB": 0,
              "third": 0,
              "queries": 124663,
              "certified": 86800,
              "maxQueries": 2
            }
          ]
        },
        {
          "e": 3,
          "patterns": 56,
          "orderedPairs": 537986400,
          "genuine": 173600,
          "caps": [
            {
              "asA": 5593022,
              "asB": 4565754,
              "third": 5099701,
              "queries": 0,
              "certified": 100,
              "maxQueries": 0
            },
            {
              "asA": 192198,
              "asB": 153711,
              "third": 0,
              "queries": 290739,
              "certified": 111907,
              "maxQueries": 2
            },
            {
              "asA": 1469,
              "asB": 524,
              "third": 0,
              "queries": 352432,
              "certified": 171657,
              "maxQueries": 3
            },
            {
              "asA": 0,
              "asB": 0,
              "third": 0,
              "queries": 354375,
              "certified": 173600,
              "maxQueries": 3
            },
            {
              "asA": 0,
              "asB": 0,
              "third": 0,
              "queries": 354375,
              "certified": 173600,
              "maxQueries": 3
            }
          ]
        },
        {
          "e": 4,
          "patterns": 70,
          "orderedPairs": 672483000,
          "genuine": 217000,
          "caps": [
            {
              "asA": 26800508,
              "asB": 23999256,
              "third": 95568944,
              "queries": 0,
              "certified": 12,
              "maxQueries": 0
            },
            {
              "asA": 1193673,
              "asB": 1083825,
              "third": 8879,
              "queries": 406456,
              "certified": 63377,
              "maxQueries": 2
            },
            {
              "asA": 27824,
              "asB": 24044,
              "third": 0,
              "queries": 566848,
              "certified": 203062,
              "maxQueries": 4
            },
            {
              "asA": 24,
              "asB": 24,
              "third": 0,
              "queries": 580786,
              "certified": 216952,
              "maxQueries": 4
            },
            {
              "asA": 0,
              "asB": 0,
              "third": 0,
              "queries": 580834,
              "certified": 217000,
              "maxQueries": 4
            }
          ]
        }
      ]
    }
  },
  "traces": [
    {
      "scenario": "truthful-splice",
      "status": "refused",
      "candidate": 512,
      "residual": [
        2,
        2
      ],
      "steps": [
        {
          "query": {
            "side": 0,
            "slot": 1
          },
          "pass": true,
          "residual": [
            2,
            11
          ]
        },
        {
          "query": {
            "side": 1,
            "slot": 2
          },
          "pass": true,
          "residual": [
            2,
            2
          ]
        },
        {
          "query": {
            "side": 0,
            "slot": 2
          },
          "pass": false,
          "residual": [
            2,
            2
          ]
        }
      ]
    },
    {
      "scenario": "genuine-512",
      "status": "certified",
      "candidate": 512,
      "residual": [
        1,
        1
      ],
      "steps": [
        {
          "query": {
            "side": 0,
            "slot": 1
          },
          "pass": true,
          "residual": [
            2,
            11
          ]
        },
        {
          "query": {
            "side": 1,
            "slot": 2
          },
          "pass": true,
          "residual": [
            2,
            2
          ]
        },
        {
          "query": {
            "side": 0,
            "slot": 2
          },
          "pass": true,
          "residual": [
            1,
            2
          ]
        },
        {
          "query": {
            "side": 1,
            "slot": 0
          },
          "pass": true,
          "residual": [
            1,
            1
          ]
        }
      ]
    },
    {
      "scenario": "all-left-erased",
      "status": "refused",
      "candidate": 214,
      "residual": [
        2304,
        1
      ],
      "steps": [
        {
          "query": {
            "side": 0,
            "slot": 7
          },
          "pass": false,
          "residual": [
            2304,
            1
          ]
        }
      ]
    },
    {
      "scenario": "missing-reply",
      "status": "refused",
      "candidate": 512,
      "residual": [
        16,
        11
      ],
      "steps": [
        {
          "query": {
            "side": 0,
            "slot": 1
          },
          "pass": false,
          "residual": [
            16,
            11
          ]
        }
      ]
    }
  ],
  "specimens": 21,
  "peak": 4096
}
*/
