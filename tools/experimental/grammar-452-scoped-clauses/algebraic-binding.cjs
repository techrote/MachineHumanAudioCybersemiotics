"use strict";
// Grammars lane / Refs #452. Synthetic only. No source authentication.
const R=require("./recursive.cjs"),I=require("./integrity.cjs"),J=require("./injective-tags.cjs");
const lab=(function laboratory(R,I,J){
"use strict";
const mod=x=>(x%17+17)%17,key=x=>x.reduce((a,v)=>a*17+v,0),eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const original=R.catalog().map(t=>{const x=R.encode(t,"prefix").map(v=>I.vocab.indexOf(v));while(x.length<4)x.push(13);return x;});
const newAtoms=[0,1,2,3,14],unary=[4,5,6,7,8,9,10],binary=[11,12],levels=[[],newAtoms.map(x=>[x])];
for(let n=2;n<=4;n++){const rows=[];for(const u of unary)for(const x of levels[n-1])rows.push([u,...x]);for(let l=1;l<n-1;l++)for(const b of binary)for(const x of levels[l])for(const y of levels[n-1-l])rows.push([b,...x,...y]);levels.push(rows);}
const added=levels.flat().filter(x=>x.includes(14)).map(x=>[...x,...Array(4-x.length).fill(13)]);
const versions={original,reverse:original.slice().reverse(),append:[...original,...added],prepend:[...added,...original]};
const modes=["greedy","rank","algebraic"];
function tagged(x,t){const [a,b,c,d]=x,q=mod(13*(3*a+2*b-c-2*d-2*t)),p=mod(-a-b-c-d-2*t-q);return [a,b,t,p,c,d,t,q];}
function algebraic(x){return tagged(x,mod(x[0]+x[2]));}
function invertHalf(h,side){if(!Array.isArray(h)||h.length!==4||h.some(v=>!Number.isInteger(v)||v<0||v>=17)||!["left","right"].includes(side))throw Error("half");if(side==="left"){const [a,b,t,p]=h,c=mod(t-a),d=mod(9*(-7*a-6*b-3*c-6*t-4*p));return [a,b,c,d];}const [c,d,t,q]=h,a=mod(t-c),b=mod(9*(4*q-3*a+c+2*d+2*t));return [a,b,c,d];}
function build(rows,mode){const left=new Set,right=new Set,book=[],map=new Map,semantic=new Map;for(let i=0;i<rows.length;i++){const x=rows[i];let y;if(mode==="algebraic")y=algebraic(x);else if(mode==="rank"){const a=i%17,b=Math.floor(i/17)%17,c=Math.floor(i/289);if(c>=17)throw Error("rank overflow");y=[a,b,c,mod(a+b+c),a,b,c,mod(a+2*b+3*c)];}else if(mode==="greedy"){for(let d=0;d<17;d++){const v=tagged(x,(i+d)%17);if(!left.has(key(v.slice(0,4)))&&!right.has(key(v.slice(4)))){y=v;break;}}if(!y)throw Error("greedy exhausted "+i);}else throw Error("mode");const a=key(y.slice(0,4)),b=key(y.slice(4)),k=key(y),s=key(x);if(left.has(a)||right.has(b)||map.has(k)||semantic.has(s))throw Error("duplicate");left.add(a);right.add(b);book.push(y);map.set(k,s);semantic.set(s,y);}return {book,map,semantic,rows,mode};}
function decode(input,codec){if(!Array.isArray(input)||input.length!==8||input.some(v=>v!==null&&(!Number.isInteger(v)||v<0||v>=17)))return null;const x=input.slice(),e=x.map((v,i)=>v===null?i:-1).filter(i=>i>=0);if(e.length>2)return null;
if(codec.mode==="rank"){for(let j=0;j<3;j++){const a=x[j],b=x[j+4];if(a!==null&&b!==null&&a!==b)return null;if(a===null)x[j]=b;if(b===null)x[j+4]=a;}const j=x.slice(0,3).indexOf(null);if(j>=0){if(x[3]===null)return null;x[j]=x[j+4]=mod(x[3]-x.slice(0,3).reduce((s,v)=>s+(v??0),0));}if(x[3]===null)x[3]=mod(x[0]+x[1]+x[2]);if(x[7]===null)x[7]=mod(x[0]+2*x[1]+3*x[2]);}
else{const [a,b]=I.synd(x.map(v=>v??0));if(e.length===1)x[e[0]]=mod(-a);if(e.length===2){const [i,j]=e;let inv=1;while(mod(inv*(j-i))!==1)inv++;const q=mod(((i+1)*a-b)*inv);x[i]=mod(-a-q);x[j]=q;}}
return codec.map.get(key(x))??null;}
const masks=[[]];for(let i=0;i<8;i++){masks.push([i]);for(let j=i+1;j<8;j++)masks.push([i,j]);}
const erased=(x,mask)=>x.map((v,j)=>mask.includes(j)?null:v);
function census(codec,mask){const a=new Map,b=new Map,full=new Set,p=[],q=[];const n=codec.book.length;for(let i=0;i<n;i++){const x=codec.book[i];p[i]=key(x.slice(0,4).filter((_,j)=>!mask.includes(j)));q[i]=key(x.slice(4).filter((_,j)=>!mask.includes(j+4)));for(const [m,k] of [[a,p[i]],[b,q[i]]]){if(!m.has(k))m.set(k,[]);m.get(k).push(i);}full.add(p[i]+":"+q[i]);}if(full.size!==n)throw Error("nonunique full projection");let asA=0,asB=0,third=0,witness=null;for(let i=0;i<n;i++){const l=a.get(p[i]),r=b.get(q[i]);asA+=r.length-1;asB+=l.length-1;third+=(l.length-1)*(r.length-1);if(!witness&&l.length>1&&r.length>1)witness={a:l.find(j=>j!==i),b:r.find(j=>j!==i),c:i,mask};}return {mask,asA,asB,third,witness};}
function qualify(){let assertions=0;const check=(x,m)=>{assertions++;if(!x)throw Error(m);};const metrics={},codecs={};let field=0;
for(let a=0;a<17;a++)for(let b=0;b<17;b++)for(let c=0;c<17;c++)for(let d=0;d<17;d++){const x=[a,b,c,d],y=algebraic(x);check(I.synd(y).every(v=>v===0),"syndrome");check(eq(invertHalf(y.slice(0,4),"left"),x),"left inverse");check(eq(invertHalf(y.slice(4),"right"),x),"right inverse");field++;}
check(original.length===2304,"old catalog");check(new Set(versions.append.map(key)).size===versions.append.length,"extension uniqueness");
for(const mode of modes){codecs[mode]={};for(const [v,rows] of Object.entries(versions)){codecs[mode][v]=build(rows,mode);}const old=codecs[mode].original;for(let i=0;i<original.length;i++){if(mode==="greedy")check(eq(old.book[i],J.encode(i,"injective")),"exact prior greedy");if(mode==="rank")check(eq(old.book[i],J.encode(i,"replicated")),"exact prior rank");}
const comparisons={};for(const [from,to] of [["original","original"],["original","reverse"],["original","append"],["original","prepend"],["prepend","original"]]){const s=codecs[mode][from],t=codecs[mode][to],stats=[0,1,2].map(n=>({erasures:n,shared:{correct:0,wrong:0,refused:0},new:{wrong:0,refused:0}}));let changed=0,shared=0,witness=null;for(let i=0;i<s.rows.length;i++){const semantic=key(s.rows[i]),isShared=t.semantic.has(semantic);if(isShared){shared++;changed+=!eq(s.book[i],t.semantic.get(semantic));}for(const mask of masks){const got=decode(erased(s.book[i],mask),t),k=got===null?"refused":got===semantic?"correct":"wrong";if(isShared)stats[mask.length].shared[k]++;else{check(k!=="correct","unknown meaning cannot be correct");stats[mask.length].new[k]++;}if(from===to||mode==="algebraic")check(k===(isShared?"correct":"refused"),"compatible semantic outcome");if(!witness&&k==="wrong")witness={sent:s.rows[i],input:s.book[i],mask,decoded:t.rows.find(x=>key(x)===got)};}}comparisons[from+"->"+to]={shared,changed,stats,witness};}
const rows=masks.map(mask=>census(old,mask));for(const row of rows)if(row.witness){const w=row.witness;check(decode(erased([...old.book[w.a].slice(0,4),...old.book[w.b].slice(4)],w.mask),old)===key(old.rows[w.c]),"splice witness");}
const splice=[0,1,2].map(n=>{const r=rows.filter(x=>x.mask.length===n);return {erasures:n,patterns:r.length,asA:r.reduce((s,x)=>s+x.asA,0),asB:r.reduce((s,x)=>s+x.asB,0),third:r.reduce((s,x)=>s+x.third,0)};});
check(splice[0].asA+splice[0].asB+splice[0].third===0,"intact binding");if(mode==="greedy")check(splice[2].third===56394,"prior census");if(mode==="rank")check(splice[2].third===0,"prior rank census");
metrics[mode]={comparisons,splice,spliceWitness:rows.find(x=>x.witness)?.witness??null};}
const traces=[],specimens=[];let peak=0;for(const mode of modes){const v=codecs[mode],idx=309;const cases=[{name:"reverse",s:v.original,t:v.reverse,i:idx,mask:[]},{name:"prepend",s:v.original,t:v.prepend,i:idx,mask:[0,4]},{name:"new-atom",s:v.prepend,t:v.original,i:0,mask:[]},{name:"new-atom-own",s:v.prepend,t:v.prepend,i:0,mask:[0,4]}];const w=metrics[mode].spliceWitness;if(w)cases.push({name:"partial-splice",s:v.original,t:v.original,i:w.a,mask:w.mask,splice:w.b});
for(const c of cases)for(const phase of [.137,2.419,5.827]){let x=c.s.book[c.i];if(c.splice!==undefined)x=[...x.slice(0,4),...c.s.book[c.splice].slice(4)];x=erased(x,c.mask);const pcm=I.render(x,phase),tokens=I.receive(pcm),got=decode(tokens,c.t);check(eq(x,tokens),"PCM tokens");check(got===decode(x,c.t),"PCM semantics");const wav=R.wav(pcm),view=new DataView(wav.buffer);check(view.getUint32(24,true)===16000&&view.getUint32(40,true)===pcm.length*2,"WAV header");let energy=0;for(const s of pcm){peak=Math.max(peak,Math.abs(s));energy+=s*s;}const row={mode,case:c.name,phase,tokens,got,semantic:key(c.s.rows[c.i]),energy};traces.push(row);if(phase===.137)specimens.push({...row,name:mode+"-"+c.name+".wav"});}}
check(peak<=4096,"peak");return {schema:"mhac-algebraic-compositional-binding-v1",source:"47b99f00cda01cf9a30b0c3ad5a7337667f2a06f",assertions,field,catalog:{original:original.length,added:added.length,extended:versions.append.length},metrics,traces,specimens,peak};}
return {algebraic,invertHalf,build,decode,versions,qualify};
})(R,I,J);
module.exports=lab;
if(require.main===module){const fs=require("node:fs"),path=require("node:path"),crypto=require("node:crypto"),dir=process.argv[2]||"output-algebraic-binding";fs.mkdirSync(dir,{recursive:true});const q=lab.qualify(),manifest=[];for(const s of q.specimens){const wav=R.wav(I.render(s.tokens,s.phase));fs.writeFileSync(path.join(dir,s.name),wav);manifest.push({...s,sha256:crypto.createHash("sha256").update(wav).digest("hex")});}fs.writeFileSync(path.join(dir,"qualification.json"),JSON.stringify(q,null,2)+"\n");fs.writeFileSync(path.join(dir,"stimuli.json"),JSON.stringify(manifest,null,2)+"\n");console.log(JSON.stringify({assertions:q.assertions,field:q.field,catalog:q.catalog,metrics:q.metrics,peak:q.peak},null,2));}
/* Grammars Run 011 — 2026-11-25; Refs #452 / Draft #453. One GPT-6.2 agent, no subagents. Main/base 495a98ca12bae467a507031f04931aa4254b1866, parent 47b99f00cda01cf9a30b0c3ad5a7337667f2a06f. Pinned local dependency blobs {"recursive.cjs":"7d9e305857b59e029913432bb40f713ab84b5a90","integrity.cjs":"a58403f51806c17d89c7ebaf098d2e19b0995a02","injective-tags.cjs":"d91e0ed1e8700ff78b12e7732c07ddfcfc189e08","block-binding.cjs":"4c8be6987b345a5084dee16cf9e7053726c034c9","clock-hypotheses.cjs":"45a5fafb6506ba9211970c1cd58ac2840fbfc670","clock.cjs":"49a6849ae8a0094d30d499718ce21dd3029c0f8a","distributed.cjs":"c727fe13c7131e9a5eac9240fa909c34bcc5011c","acquisition.cjs":"70fb9823d596300112282a73386d6c6088b5d793","local-clock.cjs":"18e86536a85a7327499be1d5ff5719518d1a696a"}. Four explicit prefix grammar tokens a,b,c,d (pad=13); t=a+c mod17; q=(3a+2b-c-2d-2t)/4, p=-a-b-c-d-2t-q, arithmetic GF(17). Inverse formulas prove both intact halves recover all four tokens, including arbitrary field tuples, not necessarily valid grammar. Membership remains mandatory. No extra slots; 640ms aligned body, nominal existing 680ms framed format not requalified. Extension adds atom 'ready' at formerly check-only token 14; all old assignments preserved, old receiver rejects unknown expressions in algebraic mode. Renaming token14 at peer still aliases semantics; version/vocabulary authority not solved. Reorder and prepend are explicit artificial catalogue changes; exact finite counts, no population or human claims. Rank and greedy baseline match actual prior encoder for every original expression. Repeated V8 execution identical; native node v22.16.0 present but git ls-remote failed DNS exit 128. Native CLI, listening and full acquisition remain unverified. No merge, no canonical modifications. CLI node algebraic-binding.cjs output-algebraic-binding. Exact prior workflow records: [{"id":45604059147,"conclusion":"success","status":"completed"}].
Executed summary:
{
  "schema": "mhac-algebraic-compositional-binding-v1",
  "source": "47b99f00cda01cf9a30b0c3ad5a7337667f2a06f",
  "assertions": 969881,
  "field": 83521,
  "catalog": {
    "original": 2304,
    "added": 796,
    "extended": 3100
  },
  "metrics": {
    "greedy": {
      "comparisons": {
        "original->original": {
          "shared": 2304,
          "changed": 0,
          "stats": [
            {
              "erasures": 0,
              "shared": {
                "correct": 2304,
                "wrong": 0,
                "refused": 0
              },
              "new": {
                "wrong": 0,
                "refused": 0
              }
            },
            {
              "erasures": 1,
              "shared": {
                "correct": 18432,
                "wrong": 0,
                "refused": 0
              },
              "new": {
                "wrong": 0,
                "refused": 0
              }
            },
            {
              "erasures": 2,
              "shared": {
                "correct": 64512,
                "wrong": 0,
                "refused": 0
              },
              "new": {
                "wrong": 0,
                "refused": 0
              }
            }
          ],
          "witness": null
        },
        "original->reverse": {
          "shared": 2304,
          "changed": 2166,
          "stats": [
            {
              "erasures": 0,
              "shared": {
                "correct": 138,
                "wrong": 0,
                "refused": 2166
              },
              "new": {
                "wrong": 0,
                "refused": 0
              }
            },
            {
              "erasures": 1,
              "shared": {
                "correct": 1104,
                "wrong": 0,
                "refused": 17328
              },
              "new": {
                "wrong": 0,
                "refused": 0
              }
            },
            {
              "erasures": 2,
              "shared": {
                "correct": 3864,
                "wrong": 0,
                "refused": 60648
              },
              "new": {
                "wrong": 0,
                "refused": 0
              }
            }
          ],
          "witness": null
        },
        "original->append": {
          "shared": 2304,
          "changed": 0,
          "stats": [
            {
              "erasures": 0,
              "shared": {
                "correct": 2304,
                "wrong": 0,
                "refused": 0
              },
              "new": {
                "wrong": 0,
                "refused": 0
              }
            },
            {
              "erasures": 1,
              "shared": {
                "correct": 18432,
                "wrong": 0,
                "refused": 0
              },
              "new": {
                "wrong": 0,
                "refused": 0
              }
            },
            {
              "erasures": 2,
              "shared": {
                "correct": 64512,
                "wrong": 0,
                "refused": 0
              },
              "new": {
                "wrong": 0,
                "refused": 0
              }
            }
          ],
          "witness": null
        },
        "original->prepend": {
          "shared": 2304,
          "changed": 2303,
          "stats": [
            {
              "erasures": 0,
              "shared": {
                "correct": 1,
                "wrong": 0,
                "refused": 2303
              },
              "new": {
                "wrong": 0,
                "refused": 0
              }
            },
            {
              "erasures": 1,
              "shared": {
                "correct": 8,
                "wrong": 0,
                "refused": 18424
              },
              "new": {
                "wrong": 0,
                "refused": 0
              }
            },
            {
              "erasures": 2,
              "shared": {
                "correct": 28,
                "wrong": 0,
                "refused": 64484
              },
              "new": {
                "wrong": 0,
                "refused": 0
              }
            }
          ],
          "witness": null
        },
        "prepend->original": {
          "shared": 2304,
          "changed": 2303,
          "stats": [
            {
              "erasures": 0,
              "shared": {
                "correct": 1,
                "wrong": 0,
                "refused": 2303
              },
              "new": {
                "wrong": 0,
                "refused": 796
              }
            },
            {
              "erasures": 1,
              "shared": {
                "correct": 8,
                "wrong": 0,
                "refused": 18424
              },
              "new": {
                "wrong": 0,
                "refused": 6368
              }
            },
            {
              "erasures": 2,
              "shared": {
                "correct": 28,
                "wrong": 0,
                "refused": 64484
              },
              "new": {
                "wrong": 0,
                "refused": 22288
              }
            }
          ],
          "witness": null
        }
      },
      "splice": [
        {
          "erasures": 0,
          "patterns": 1,
          "asA": 0,
          "asB": 0,
          "third": 0
        },
        {
          "erasures": 1,
          "patterns": 8,
          "asA": 17528,
          "asB": 7192,
          "third": 0
        },
        {
          "erasures": 2,
          "patterns": 28,
          "asA": 384336,
          "asB": 230318,
          "third": 56394
        }
      ],
      "spliceWitness": {
        "a": 1998,
        "b": 43,
        "c": 9,
        "mask": [
          0,
          4
        ]
      }
    },
    "rank": {
      "comparisons": {
        "original->original": {
          "shared": 2304,
          "changed": 0,
          "stats": [
            {
              "erasures": 0,
              "shared": {
                "correct": 2304,
                "wrong": 0,
                "refused": 0
              },
              "new": {
                "wrong": 0,
                "refused": 0
              }
            },
            {
              "erasures": 1,
              "shared": {
                "correct": 18432,
                "wrong": 0,
                "refused": 0
              },
              "new": {
                "wrong": 0,
                "refused": 0
              }
            },
            {
              "erasures": 2,
              "shared": {
                "correct": 64512,
                "wrong": 0,
                "refused": 0
              },
              "new": {
                "wrong": 0,
                "refused": 0
              }
            }
          ],
          "witness": null
        },
        "original->reverse": {
          "shared": 2304,
          "changed": 2304,
          "stats": [
            {
              "erasures": 0,
              "shared": {
                "correct": 0,
                "wrong": 2304,
                "refused": 0
              },
              "new": {
                "wrong": 0,
                "refused": 0
              }
            },
            {
              "erasures": 1,
              "shared": {
                "correct": 0,
                "wrong": 18432,
                "refused": 0
              },
              "new": {
                "wrong": 0,
                "refused": 0
              }
            },
            {
              "erasures": 2,
              "shared": {
                "correct": 0,
                "wrong": 64512,
                "refused": 0
              },
              "new": {
                "wrong": 0,
                "refused": 0
              }
            }
          ],
          "witness": {
            "sent": [
              0,
              13,
              13,
              13
            ],
            "input": [
              0,
              0,
              0,
              0,
              0,
              0,
              0,
              0
            ],
            "mask": [],
            "decoded": [
              12,
              10,
              3,
              3
            ]
          }
        },
        "original->append": {
          "shared": 2304,
          "changed": 0,
          "stats": [
            {
              "erasures": 0,
              "shared": {
                "correct": 2304,
                "wrong": 0,
                "refused": 0
              },
              "new": {
                "wrong": 0,
                "refused": 0
              }
            },
            {
              "erasures": 1,
              "shared": {
                "correct": 18432,
                "wrong": 0,
                "refused": 0
              },
              "new": {
                "wrong": 0,
                "refused": 0
              }
            },
            {
              "erasures": 2,
              "shared": {
                "correct": 64512,
                "wrong": 0,
                "refused": 0
              },
              "new": {
                "wrong": 0,
                "refused": 0
              }
            }
          ],
          "witness": null
        },
        "original->prepend": {
          "shared": 2304,
          "changed": 2304,
          "stats": [
            {
              "erasures": 0,
              "shared": {
                "correct": 0,
                "wrong": 2304,
                "refused": 0
              },
              "new": {
                "wrong": 0,
                "refused": 0
              }
            },
            {
              "erasures": 1,
              "shared": {
                "correct": 0,
                "wrong": 18432,
                "refused": 0
              },
              "new": {
                "wrong": 0,
                "refused": 0
              }
            },
            {
              "erasures": 2,
              "shared": {
                "correct": 0,
                "wrong": 64512,
                "refused": 0
              },
              "new": {
                "wrong": 0,
                "refused": 0
              }
            }
          ],
          "witness": {
            "sent": [
              0,
              13,
              13,
              13
            ],
            "input": [
              0,
              0,
              0,
              0,
              0,
              0,
              0,
              0
            ],
            "mask": [],
            "decoded": [
              14,
              13,
              13,
              13
            ]
          }
        },
        "prepend->original": {
          "shared": 2304,
          "changed": 2304,
          "stats": [
            {
              "erasures": 0,
              "shared": {
                "correct": 0,
                "wrong": 1508,
                "refused": 796
              },
              "new": {
                "wrong": 796,
                "refused": 0
              }
            },
            {
              "erasures": 1,
              "shared": {
                "correct": 0,
                "wrong": 12064,
                "refused": 6368
              },
              "new": {
                "wrong": 6368,
                "refused": 0
              }
            },
            {
              "erasures": 2,
              "shared": {
                "correct": 0,
                "wrong": 42224,
                "refused": 22288
              },
              "new": {
                "wrong": 22288,
                "refused": 0
              }
            }
          ],
          "witness": {
            "sent": [
              14,
              13,
              13,
              13
            ],
            "input": [
              0,
              0,
              0,
              0,
              0,
              0,
              0,
              0
            ],
            "mask": [],
            "decoded": [
              0,
              13,
              13,
              13
            ]
          }
        }
      },
      "splice": [
        {
          "erasures": 0,
          "patterns": 1,
          "asA": 0,
          "asB": 0,
          "third": 0
        },
        {
          "erasures": 1,
          "patterns": 8,
          "asA": 0,
          "asB": 0,
          "third": 0
        },
        {
          "erasures": 2,
          "patterns": 28,
          "asA": 158480,
          "asB": 158480,
          "third": 0
        }
      ],
      "spliceWitness": null
    },
    "algebraic": {
      "comparisons": {
        "original->original": {
          "shared": 2304,
          "changed": 0,
          "stats": [
            {
              "erasures": 0,
              "shared": {
                "correct": 2304,
                "wrong": 0,
                "refused": 0
              },
              "new": {
                "wrong": 0,
                "refused": 0
              }
            },
            {
              "erasures": 1,
              "shared": {
                "correct": 18432,
                "wrong": 0,
                "refused": 0
              },
              "new": {
                "wrong": 0,
                "refused": 0
              }
            },
            {
              "erasures": 2,
              "shared": {
                "correct": 64512,
                "wrong": 0,
                "refused": 0
              },
              "new": {
                "wrong": 0,
                "refused": 0
              }
            }
          ],
          "witness": null
        },
        "original->reverse": {
          "shared": 2304,
          "changed": 0,
          "stats": [
            {
              "erasures": 0,
              "shared": {
                "correct": 2304,
                "wrong": 0,
                "refused": 0
              },
              "new": {
                "wrong": 0,
                "refused": 0
              }
            },
            {
              "erasures": 1,
              "shared": {
                "correct": 18432,
                "wrong": 0,
                "refused": 0
              },
              "new": {
                "wrong": 0,
                "refused": 0
              }
            },
            {
              "erasures": 2,
              "shared": {
                "correct": 64512,
                "wrong": 0,
                "refused": 0
              },
              "new": {
                "wrong": 0,
                "refused": 0
              }
            }
          ],
          "witness": null
        },
        "original->append": {
          "shared": 2304,
          "changed": 0,
          "stats": [
            {
              "erasures": 0,
              "shared": {
                "correct": 2304,
                "wrong": 0,
                "refused": 0
              },
              "new": {
                "wrong": 0,
                "refused": 0
              }
            },
            {
              "erasures": 1,
              "shared": {
                "correct": 18432,
                "wrong": 0,
                "refused": 0
              },
              "new": {
                "wrong": 0,
                "refused": 0
              }
            },
            {
              "erasures": 2,
              "shared": {
                "correct": 64512,
                "wrong": 0,
                "refused": 0
              },
              "new": {
                "wrong": 0,
                "refused": 0
              }
            }
          ],
          "witness": null
        },
        "original->prepend": {
          "shared": 2304,
          "changed": 0,
          "stats": [
            {
              "erasures": 0,
              "shared": {
                "correct": 2304,
                "wrong": 0,
                "refused": 0
              },
              "new": {
                "wrong": 0,
                "refused": 0
              }
            },
            {
              "erasures": 1,
              "shared": {
                "correct": 18432,
                "wrong": 0,
                "refused": 0
              },
              "new": {
                "wrong": 0,
                "refused": 0
              }
            },
            {
              "erasures": 2,
              "shared": {
                "correct": 64512,
                "wrong": 0,
                "refused": 0
              },
              "new": {
                "wrong": 0,
                "refused": 0
              }
            }
          ],
          "witness": null
        },
        "prepend->original": {
          "shared": 2304,
          "changed": 0,
          "stats": [
            {
              "erasures": 0,
              "shared": {
                "correct": 2304,
                "wrong": 0,
                "refused": 0
              },
              "new": {
                "wrong": 0,
                "refused": 796
              }
            },
            {
              "erasures": 1,
              "shared": {
                "correct": 18432,
                "wrong": 0,
                "refused": 0
              },
              "new": {
                "wrong": 0,
                "refused": 6368
              }
            },
            {
              "erasures": 2,
              "shared": {
                "correct": 64512,
                "wrong": 0,
                "refused": 0
              },
              "new": {
                "wrong": 0,
                "refused": 22288
              }
            }
          ],
          "witness": null
        }
      },
      "splice": [
        {
          "erasures": 0,
          "patterns": 1,
          "asA": 0,
          "asB": 0,
          "third": 0
        },
        {
          "erasures": 1,
          "patterns": 8,
          "asA": 26538,
          "asB": 11854,
          "third": 0
        },
        {
          "erasures": 2,
          "patterns": 28,
          "asA": 479852,
          "asB": 291656,
          "third": 140166
        }
      ],
      "spliceWitness": {
        "a": 260,
        "b": 71,
        "c": 90,
        "mask": [
          0,
          4
        ]
      }
    }
  },
  "traces": [
    {
      "mode": "greedy",
      "case": "reverse",
      "phase": 0.137,
      "tokens": [
        4,
        5,
        4,
        2,
        9,
        1,
        4,
        5
      ],
      "got": null,
      "semantic": 21251,
      "energy": 57190942828
    },
    {
      "mode": "greedy",
      "case": "prepend",
      "phase": 0.137,
      "tokens": [
        null,
        5,
        4,
        2,
        null,
        1,
        4,
        5
      ],
      "got": null,
      "semantic": 21251,
      "energy": 42892385824
    },
    {
      "mode": "greedy",
      "case": "new-atom",
      "phase": 0.137,
      "tokens": [
        14,
        13,
        0,
        12,
        13,
        13,
        0,
        3
      ],
      "got": null,
      "semantic": 72773,
      "energy": 57188861923
    },
    {
      "mode": "greedy",
      "case": "new-atom-own",
      "phase": 0.137,
      "tokens": [
        null,
        13,
        0,
        12,
        null,
        13,
        0,
        3
      ],
      "got": 72773,
      "semantic": 72773,
      "energy": 42889267122
    },
    {
      "mode": "greedy",
      "case": "partial-splice",
      "phase": 0.137,
      "tokens": [
        null,
        1,
        9,
        11,
        null,
        13,
        9,
        7
      ],
      "got": 25088,
      "semantic": 59315,
      "energy": 42897043111
    },
    {
      "mode": "rank",
      "case": "reverse",
      "phase": 0.137,
      "tokens": [
        3,
        1,
        1,
        5,
        3,
        1,
        1,
        8
      ],
      "got": 59128,
      "semantic": 21251,
      "energy": 57188173267
    },
    {
      "mode": "rank",
      "case": "prepend",
      "phase": 0.137,
      "tokens": [
        null,
        1,
        1,
        5,
        null,
        1,
        1,
        8
      ],
      "got": 36870,
      "semantic": 21251,
      "energy": 42890931047
    },
    {
      "mode": "rank",
      "case": "new-atom",
      "phase": 0.137,
      "tokens": [
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0
      ],
      "got": 3991,
      "semantic": 72773,
      "energy": 57165278064
    },
    {
      "mode": "rank",
      "case": "new-atom-own",
      "phase": 0.137,
      "tokens": [
        null,
        0,
        0,
        0,
        null,
        0,
        0,
        0
      ],
      "got": 72773,
      "semantic": 72773,
      "energy": 42873958548
    },
    {
      "mode": "algebraic",
      "case": "reverse",
      "phase": 0.137,
      "tokens": [
        4,
        5,
        13,
        14,
        9,
        1,
        13,
        9
      ],
      "got": 21251,
      "semantic": 21251,
      "energy": 57194805117
    },
    {
      "mode": "algebraic",
      "case": "prepend",
      "phase": 0.137,
      "tokens": [
        null,
        5,
        13,
        14,
        null,
        1,
        13,
        9
      ],
      "got": 21251,
      "semantic": 21251,
      "energy": 42896248113
    },
    {
      "mode": "algebraic",
      "case": "new-atom",
      "phase": 0.137,
      "tokens": [
        14,
        13,
        10,
        14,
        13,
        13,
        10,
        15
      ],
      "got": null,
      "semantic": 72773,
      "energy": 57198122445
    },
    {
      "mode": "algebraic",
      "case": "new-atom-own",
      "phase": 0.137,
      "tokens": [
        null,
        13,
        10,
        14,
        null,
        13,
        10,
        15
      ],
      "got": 72773,
      "semantic": 72773,
      "energy": 42898527644
    },
    {
      "mode": "algebraic",
      "case": "partial-splice",
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
      "semantic": 20876,
      "energy": 42896967189
    }
  ],
  "specimens": [
    "greedy-reverse.wav",
    "greedy-prepend.wav",
    "greedy-new-atom.wav",
    "greedy-new-atom-own.wav",
    "greedy-partial-splice.wav",
    "rank-reverse.wav",
    "rank-prepend.wav",
    "rank-new-atom.wav",
    "rank-new-atom-own.wav",
    "algebraic-reverse.wav",
    "algebraic-prepend.wav",
    "algebraic-new-atom.wav",
    "algebraic-new-atom-own.wav",
    "algebraic-partial-splice.wav"
  ],
  "peak": 4096
}
*/
