'use strict';
// Refs #448/#449. Adversarial lane, synthetic stream association audit, 2026-11-25.
// Integration #513 remains a pinned Draft comparator, not accepted research.
// No receiver changes. One GPT-6.2 agent; no independent review or human evidence.
const REF="45c8f1b1432172d70ec5b05716150c5ec2a5a894", BLOBS={"relay.cjs":"3ba457f85f496e4d57d9789a2dc3b7d68fe2c071","bound-v2.cjs":"2aa2905d4f4d756276814d5ca941c02c51e63f97","stream-v4.cjs":"31769f808469b4416412be25a41eb238bfc1fdde"};
const seeds=[30719,61987], gaps=[0,80,160,240,320,480,640,960,1280],
cuts=[0,160,320,480,640,960,1280,1920,2560,3200], floods=[0,6,7,8,9,10];
const eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b), z=n=>new Int16Array(n);
const energy=p=>p.reduce((s,x)=>s+x*x,0), peak=p=>p.reduce((s,x)=>Math.max(s,Math.abs(x)),0);
function run(v1,v2,v4,hash){
 let assertions=0;const check=(x,m)=>{assertions++;if(!x)throw Error(m);};
 const rows=[],specimens={},controls=[];
 function trial(id,pcm,expected,meta,save=false){
  const r=v4.decode(pcm), actual=r.events.filter(e=>e.status==='ok').map(e=>e.packet);
  const unknown=actual.filter(p=>!expected.some(q=>eq(p,q))).length;
  const row={id,...meta,samples:pcm.length,peak:peak(pcm),sha256:hash(v1.wav(pcm)),expected,actual,unknown,exact:eq(expected,actual),events:r.events,stats:r.stats};
  check(r.stats.maxPending<=v4.MAX_PENDING,'pending bound');
  check(row.peak<=4096,'nominal peak');check(r.events.every(e=>e.at<=pcm.length),'release within capture');
  check(r.events.every((e,i)=>i===0||e.at>=r.events[i-1].at),'monotonic release time');
  if(save){specimens[id]=pcm;check(eq(r,v4.decode(pcm,127)),'chunk invariance at 127');check(eq(r,v4.decode(pcm,8192)),'chunk invariance at 8192');}
  rows.push(row);return row;
 }
 for(const seed of seeds){
  let state=seed;const rnd=()=>{state=(Math.imul(state,1664525)+1013904223)>>>0;return state/4294967296;};
  const phase=rnd()*2*Math.PI,phaseB=rnd()*2*Math.PI,offset=160+Math.floor(rnd()*480);
  const A={...v1.base,seq:1+seed%16},B={...A,source:2,actor:3,event:2,kind:1,tree:['question',['open']]};
  const a=v2.render(A,phase),b=v2.render(B,phaseB);check(a.length===31360&&b.length===31360,'frame length');
  for(const [p,w] of [[A,a],[B,b]]){const r=v4.decode(v1.join(z(offset),w,z(1280)));check(eq(r.events.filter(e=>e.status==='ok').map(e=>e.packet),[p]),'isolated clean control');controls.push({seed,packet:p,events:r.events});}
  for(const gap of gaps){
   const pcm=v1.join(z(offset),a,z(gap),b,z(1280));check(energy(pcm)===energy(a)+energy(b),'guard changes no energy');
   const row=trial('gap-'+gap+'-'+seed,pcm,[A,B],{family:'gap',seed,gap,phase,phaseB,offset,ends:[offset+a.length,offset+a.length+gap+b.length]},seed===seeds[0]&&[0,160,320,640].includes(gap));
   row.releaseLag=row.events.filter(e=>e.status==='ok').map(e=>({source:e.packet.source,samples:e.at-row.ends[e.packet.source===A.source?0:1]}));
  }
  for(const cut of cuts){
   const raw=a.slice(0,a.length-cut);const removed=a.slice(raw.length);
   for(const pad of [0,3200]){
    const pcm=v1.join(z(offset),raw,z(pad));
    trial('cut-'+cut+'-pad-'+pad+'-'+seed,pcm,[A],{family:'cut',seed,cut,pad,phase,offset,removedNonzero:removed.filter(x=>x!==0).length,removedEnergy:energy(removed)},seed===seeds[0]&&[320,1280,2560].includes(cut));
   }
  }
  for(const n of floods){
   const pre=v1.join(...Array.from({length:n},()=>v1.join(a.slice(0,640),z(640))));
   const pcm=v1.join(z(offset),pre,z(3200),a,z(40000),b,z(1280));
   trial('flood-'+n+'-'+seed,pcm,[A,B],{family:'flood',seed,n,phase,phaseB,offset,quietBeforeB:40000},seed===seeds[0]&&[0,7,8,9].includes(n));
  }
 }
 const summarize=rr=>({trials:rr.length,exact:rr.filter(r=>r.exact).length,accepted:rr.reduce((s,r)=>s+r.actual.length,0),unknown:rr.reduce((s,r)=>s+r.unknown,0),ambiguous:rr.filter(r=>r.events.some(e=>e.status==='ambiguous')).length,overflow:rr.filter(r=>r.events.some(e=>e.status==='overflow')).length});
 const summary={ref:REF,blobs:BLOBS,seeds,rate:16000,streams:rows.length,assertions,isolatedControls:controls.length,peak:Math.max(...rows.map(r=>r.peak)),gap:gaps.map(gap=>({gap,...summarize(rows.filter(r=>r.family==='gap'&&r.gap===gap)),lag:rows.filter(r=>r.family==='gap'&&r.gap===gap).flatMap(r=>r.releaseLag.map(e=>e.samples))})),cut:cuts.map(cut=>({cut,removedNonzero:rows.filter(r=>r.family==='cut'&&r.cut===cut&&r.pad===0).map(r=>r.removedNonzero),eof:summarize(rows.filter(r=>r.family==='cut'&&r.cut===cut&&r.pad===0)),padded:summarize(rows.filter(r=>r.family==='cut'&&r.cut===cut&&r.pad===3200))})),flood:floods.map(n=>({n,...summarize(rows.filter(r=>r.family==='flood'&&r.n===n)),events:rows.filter(r=>r.family==='flood'&&r.n===n).map(r=>r.events.map(e=>({status:e.status,reason:e.reason,source:e.packet?.source,at:e.at})))})),total:summarize(rows)};
 return {summary,rows,controls,specimens};
}
module.exports={run};
if(require.main===module){
 const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
 const dir=path.resolve(process.argv[2]||'.'),out=path.resolve(process.argv[3]||'stream-boundary-output');
 const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
 for(const [file,sha] of Object.entries(BLOBS)){const b=fs.readFileSync(path.join(dir,file)),got=crypto.createHash('sha1').update('blob '+b.length+'\0').update(b).digest('hex');if(got!==sha)throw Error('wrong upstream blob '+file);}
 const v1=require(path.join(dir,'relay.cjs')),v2=require(path.join(dir,'bound-v2.cjs')),v4=require(path.join(dir,'stream-v4.cjs'));
 const r=run(v1,v2,v4,hash);fs.mkdirSync(out,{recursive:true});
 const stimuli=[];for(const [id,p] of Object.entries(r.specimens)){const b=v1.wav(p);fs.writeFileSync(path.join(out,id+'.wav'),b);stimuli.push({id,file:id+'.wav',sha256:hash(b),samples:p.length,peak:peak(p)});}
 fs.writeFileSync(path.join(out,'receipt.json'),JSON.stringify({summary:r.summary,rows:r.rows,controls:r.controls,stimuli},null,2)+'\n');
 console.log(JSON.stringify(r.summary,null,2));
}

/* V8 receipt: two identical complete executions; SHA256 shim checked against abc and empty string. Native Node CLI not executed; connector-reported pinned Git blobs checked. All counts finite synthetic results. Isolated controls use privileged segmentation; not a receiver candidate. Cut outcomes measure semantic recovery, not physical frame completeness.
{
  "summary": {
    "ref": "45c8f1b1432172d70ec5b05716150c5ec2a5a894",
    "blobs": {
      "relay.cjs": "3ba457f85f496e4d57d9789a2dc3b7d68fe2c071",
      "bound-v2.cjs": "2aa2905d4f4d756276814d5ca941c02c51e63f97",
      "stream-v4.cjs": "31769f808469b4416412be25a41eb238bfc1fdde"
    },
    "seeds": [
      30719,
      61987
    ],
    "rate": 16000,
    "streams": 70,
    "assertions": 332,
    "isolatedControls": 4,
    "peak": 4096,
    "gap": [
      {
        "gap": 0,
        "trials": 2,
        "exact": 0,
        "accepted": 0,
        "unknown": 0,
        "ambiguous": 2,
        "overflow": 0,
        "lag": []
      },
      {
        "gap": 80,
        "trials": 2,
        "exact": 0,
        "accepted": 0,
        "unknown": 0,
        "ambiguous": 2,
        "overflow": 0,
        "lag": []
      },
      {
        "gap": 160,
        "trials": 2,
        "exact": 2,
        "accepted": 4,
        "unknown": 0,
        "ambiguous": 0,
        "overflow": 0,
        "lag": [
          32519,
          999,
          32524,
          1004
        ]
      },
      {
        "gap": 240,
        "trials": 2,
        "exact": 2,
        "accepted": 4,
        "unknown": 0,
        "ambiguous": 0,
        "overflow": 0,
        "lag": [
          999,
          999,
          1004,
          1004
        ]
      },
      {
        "gap": 320,
        "trials": 2,
        "exact": 2,
        "accepted": 4,
        "unknown": 0,
        "ambiguous": 0,
        "overflow": 0,
        "lag": [
          999,
          999,
          1004,
          1004
        ]
      },
      {
        "gap": 480,
        "trials": 2,
        "exact": 2,
        "accepted": 4,
        "unknown": 0,
        "ambiguous": 0,
        "overflow": 0,
        "lag": [
          999,
          999,
          1004,
          1004
        ]
      },
      {
        "gap": 640,
        "trials": 2,
        "exact": 2,
        "accepted": 4,
        "unknown": 0,
        "ambiguous": 0,
        "overflow": 0,
        "lag": [
          999,
          999,
          1004,
          1004
        ]
      },
      {
        "gap": 960,
        "trials": 2,
        "exact": 2,
        "accepted": 4,
        "unknown": 0,
        "ambiguous": 0,
        "overflow": 0,
        "lag": [
          999,
          999,
          1004,
          1004
        ]
      },
      {
        "gap": 1280,
        "trials": 2,
        "exact": 2,
        "accepted": 4,
        "unknown": 0,
        "ambiguous": 0,
        "overflow": 0,
        "lag": [
          999,
          999,
          1004,
          1004
        ]
      }
    ],
    "cut": [
      {
        "cut": 0,
        "removedNonzero": [
          0,
          0
        ],
        "eof": {
          "trials": 2,
          "exact": 2,
          "accepted": 2,
          "unknown": 0,
          "ambiguous": 0,
          "overflow": 0
        },
        "padded": {
          "trials": 2,
          "exact": 2,
          "accepted": 2,
          "unknown": 0,
          "ambiguous": 0,
          "overflow": 0
        }
      },
      {
        "cut": 160,
        "removedNonzero": [
          0,
          0
        ],
        "eof": {
          "trials": 2,
          "exact": 2,
          "accepted": 2,
          "unknown": 0,
          "ambiguous": 0,
          "overflow": 0
        },
        "padded": {
          "trials": 2,
          "exact": 2,
          "accepted": 2,
          "unknown": 0,
          "ambiguous": 0,
          "overflow": 0
        }
      },
      {
        "cut": 320,
        "removedNonzero": [
          0,
          0
        ],
        "eof": {
          "trials": 2,
          "exact": 2,
          "accepted": 2,
          "unknown": 0,
          "ambiguous": 0,
          "overflow": 0
        },
        "padded": {
          "trials": 2,
          "exact": 2,
          "accepted": 2,
          "unknown": 0,
          "ambiguous": 0,
          "overflow": 0
        }
      },
      {
        "cut": 480,
        "removedNonzero": [
          159,
          159
        ],
        "eof": {
          "trials": 2,
          "exact": 1,
          "accepted": 1,
          "unknown": 0,
          "ambiguous": 0,
          "overflow": 0
        },
        "padded": {
          "trials": 2,
          "exact": 2,
          "accepted": 2,
          "unknown": 0,
          "ambiguous": 0,
          "overflow": 0
        }
      },
      {
        "cut": 640,
        "removedNonzero": [
          319,
          319
        ],
        "eof": {
          "trials": 2,
          "exact": 0,
          "accepted": 0,
          "unknown": 0,
          "ambiguous": 0,
          "overflow": 0
        },
        "padded": {
          "trials": 2,
          "exact": 2,
          "accepted": 2,
          "unknown": 0,
          "ambiguous": 0,
          "overflow": 0
        }
      },
      {
        "cut": 960,
        "removedNonzero": [
          639,
          639
        ],
        "eof": {
          "trials": 2,
          "exact": 0,
          "accepted": 0,
          "unknown": 0,
          "ambiguous": 0,
          "overflow": 0
        },
        "padded": {
          "trials": 2,
          "exact": 2,
          "accepted": 2,
          "unknown": 0,
          "ambiguous": 0,
          "overflow": 0
        }
      },
      {
        "cut": 1280,
        "removedNonzero": [
          958,
          958
        ],
        "eof": {
          "trials": 2,
          "exact": 0,
          "accepted": 0,
          "unknown": 0,
          "ambiguous": 0,
          "overflow": 0
        },
        "padded": {
          "trials": 2,
          "exact": 2,
          "accepted": 2,
          "unknown": 0,
          "ambiguous": 0,
          "overflow": 0
        }
      },
      {
        "cut": 1920,
        "removedNonzero": [
          1277,
          1277
        ],
        "eof": {
          "trials": 2,
          "exact": 0,
          "accepted": 0,
          "unknown": 0,
          "ambiguous": 0,
          "overflow": 0
        },
        "padded": {
          "trials": 2,
          "exact": 2,
          "accepted": 2,
          "unknown": 0,
          "ambiguous": 0,
          "overflow": 0
        }
      },
      {
        "cut": 2560,
        "removedNonzero": [
          1916,
          1916
        ],
        "eof": {
          "trials": 2,
          "exact": 0,
          "accepted": 0,
          "unknown": 0,
          "ambiguous": 0,
          "overflow": 0
        },
        "padded": {
          "trials": 2,
          "exact": 2,
          "accepted": 2,
          "unknown": 0,
          "ambiguous": 0,
          "overflow": 0
        }
      },
      {
        "cut": 3200,
        "removedNonzero": [
          2235,
          2235
        ],
        "eof": {
          "trials": 2,
          "exact": 0,
          "accepted": 0,
          "unknown": 0,
          "ambiguous": 0,
          "overflow": 0
        },
        "padded": {
          "trials": 2,
          "exact": 2,
          "accepted": 2,
          "unknown": 0,
          "ambiguous": 0,
          "overflow": 0
        }
      }
    ],
    "flood": [
      {
        "n": 0,
        "trials": 2,
        "exact": 2,
        "accepted": 4,
        "unknown": 0,
        "ambiguous": 0,
        "overflow": 0,
        "events": [
          [
            {
              "status": "ok",
              "source": 1,
              "at": 35898
            },
            {
              "status": "ok",
              "source": 2,
              "at": 107258
            }
          ],
          [
            {
              "status": "ok",
              "source": 1,
              "at": 36122
            },
            {
              "status": "ok",
              "source": 2,
              "at": 107482
            }
          ]
        ]
      },
      {
        "n": 6,
        "trials": 2,
        "exact": 2,
        "accepted": 4,
        "unknown": 0,
        "ambiguous": 0,
        "overflow": 0,
        "events": [
          [
            {
              "status": "refused",
              "at": 32698
            },
            {
              "status": "refused",
              "at": 33978
            },
            {
              "status": "refused",
              "at": 35258
            },
            {
              "status": "refused",
              "at": 36538
            },
            {
              "status": "refused",
              "at": 37818
            },
            {
              "status": "refused",
              "at": 39098
            },
            {
              "status": "ok",
              "source": 1,
              "at": 43578
            },
            {
              "status": "ok",
              "source": 2,
              "at": 114938
            }
          ],
          [
            {
              "status": "refused",
              "at": 32922
            },
            {
              "status": "refused",
              "at": 34202
            },
            {
              "status": "refused",
              "at": 35482
            },
            {
              "status": "refused",
              "at": 36762
            },
            {
              "status": "refused",
              "at": 38042
            },
            {
              "status": "refused",
              "at": 39322
            },
            {
              "status": "ok",
              "source": 1,
              "at": 43802
            },
            {
              "status": "ok",
              "source": 2,
              "at": 115162
            }
          ]
        ]
      },
      {
        "n": 7,
        "trials": 2,
        "exact": 2,
        "accepted": 4,
        "unknown": 0,
        "ambiguous": 0,
        "overflow": 0,
        "events": [
          [
            {
              "status": "refused",
              "at": 32698
            },
            {
              "status": "refused",
              "at": 33978
            },
            {
              "status": "refused",
              "at": 35258
            },
            {
              "status": "refused",
              "at": 36538
            },
            {
              "status": "refused",
              "at": 37818
            },
            {
              "status": "refused",
              "at": 39098
            },
            {
              "status": "refused",
              "at": 40378
            },
            {
              "status": "ok",
              "source": 1,
              "at": 44858
            },
            {
              "status": "ok",
              "source": 2,
              "at": 116218
            }
          ],
          [
            {
              "status": "refused",
              "at": 32922
            },
            {
              "status": "refused",
              "at": 34202
            },
            {
              "status": "refused",
              "at": 35482
            },
            {
              "status": "refused",
              "at": 36762
            },
            {
              "status": "refused",
              "at": 38042
            },
            {
              "status": "refused",
              "at": 39322
            },
            {
              "status": "refused",
              "at": 40602
            },
            {
              "status": "ok",
              "source": 1,
              "at": 45082
            },
            {
              "status": "ok",
              "source": 2,
              "at": 116442
            }
          ]
        ]
      },
      {
        "n": 8,
        "trials": 2,
        "exact": 0,
        "accepted": 0,
        "unknown": 0,
        "ambiguous": 0,
        "overflow": 2,
        "events": [
          [
            {
              "status": "overflow",
              "reason": "pending-cap",
              "at": 14810
            }
          ],
          [
            {
              "status": "overflow",
              "reason": "pending-cap",
              "at": 15034
            }
          ]
        ]
      },
      {
        "n": 9,
        "trials": 2,
        "exact": 0,
        "accepted": 0,
        "unknown": 0,
        "ambiguous": 0,
        "overflow": 2,
        "events": [
          [
            {
              "status": "overflow",
              "reason": "pending-cap",
              "at": 11610
            }
          ],
          [
            {
              "status": "overflow",
              "reason": "pending-cap",
              "at": 11834
            }
          ]
        ]
      },
      {
        "n": 10,
        "trials": 2,
        "exact": 0,
        "accepted": 0,
        "unknown": 0,
        "ambiguous": 0,
        "overflow": 2,
        "events": [
          [
            {
              "status": "overflow",
              "reason": "pending-cap",
              "at": 11610
            }
          ],
          [
            {
              "status": "overflow",
              "reason": "pending-cap",
              "at": 11834
            }
          ]
        ]
      }
    ],
    "total": {
      "trials": 70,
      "exact": 47,
      "accepted": 67,
      "unknown": 0,
      "ambiguous": 4,
      "overflow": 6
    }
  },
  "specimenHashes": [
    {
      "id": "gap-0-30719",
      "hash": "919f74d5f2a406fb7a689d4b0a7d75fe278ab10d2a769854f59f8085a342ab79",
      "samples": 64339
    },
    {
      "id": "gap-160-30719",
      "hash": "f3e56ef7c4277704bea1f604cd119b7a579d39282ff586db366bec1abbed2e18",
      "samples": 64499
    },
    {
      "id": "gap-320-30719",
      "hash": "028d800511c2d07d32a516d40f0c8523812faea1932f6dca47d7785066af65fd",
      "samples": 64659
    },
    {
      "id": "gap-640-30719",
      "hash": "622796d9a054342cc60222438863874144ff3ed7bb429bce89807c53f4f4b83e",
      "samples": 64979
    },
    {
      "id": "cut-320-pad-0-30719",
      "hash": "797c6b47b7faf09af55e8e6964c0310fc2c43f2ea757bc9433ea80e8193dd6a0",
      "samples": 31379
    },
    {
      "id": "cut-320-pad-3200-30719",
      "hash": "29ccc0f50ec0605133cf2246442cd3d8515cfd7f836831a8b618a2bc59a0a8e6",
      "samples": 34579
    },
    {
      "id": "cut-1280-pad-0-30719",
      "hash": "585b5d0252142d3c81d11861100025b38e3245c09dd3c0d2a04fe0c69d5439cf",
      "samples": 30419
    },
    {
      "id": "cut-1280-pad-3200-30719",
      "hash": "e268be5a4080756eef306f976b4f361a5390f4b100f7f088abd269ec6984f155",
      "samples": 33619
    },
    {
      "id": "cut-2560-pad-0-30719",
      "hash": "e6d2eba3c32fb620e65338ccd6f334d3408a4611f3460a48f6020401db970c42",
      "samples": 29139
    },
    {
      "id": "cut-2560-pad-3200-30719",
      "hash": "182794bd5480959469cbded5fa61a8c5837ba6a025eb877b5ec6854f04199465",
      "samples": 32339
    },
    {
      "id": "flood-0-30719",
      "hash": "44ddab871b5260d84ff0aca97e066d0c400dfd7cfa01607e0bb36f73bb54226b",
      "samples": 107539
    },
    {
      "id": "flood-7-30719",
      "hash": "baff9957dc07342be2b95f67e33270ec9294e008636f8d46583ee5984991b194",
      "samples": 116499
    },
    {
      "id": "flood-8-30719",
      "hash": "b6603a314ac1b472a0dbbe2338c19a92e18d445b2f9d87c47ae527b37f28d95f",
      "samples": 117779
    },
    {
      "id": "flood-9-30719",
      "hash": "fb343250f3c5c5644778328c6995cbaf8192916d15c42e06c927814a163bb83e",
      "samples": 119059
    }
  ]
}
*/
