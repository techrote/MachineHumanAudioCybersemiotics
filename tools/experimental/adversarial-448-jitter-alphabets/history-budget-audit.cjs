'use strict';
// Adversarial Observatory, Refs #448 #449 #512; 2026-11-25.
// Exploratory synthetic experiment, not human evidence. No change to upstream.
// Independent fixed-cooldown adapter with variable history; actual v8 controls.
const REF='f001f6b2f39428eb4c9c174fa2b001ad3cb2332e',BLOBS={"relay.cjs":"3ba457f85f496e4d57d9789a2dc3b7d68fe2c071","bound-v2.cjs":"2aa2905d4f4d756276814d5ca941c02c51e63f97","stream-v4.cjs":"31769f808469b4416412be25a41eb238bfc1fdde","epoch-v8.cjs":"40a591b005dcbbbcff380effe23f80aa446685e9"};
const SEEDS=[29473,85159],OFFSETS=[-960,-640,-480,-320,0],HIST=[960,1280,1920];
const z=n=>new Int16Array(n),eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
function candidate(v4,pcm,history,budget){
 const ring=new Int16Array(history),one=z(1),events=[];
 let stream,now=0,origin=0,epoch=0,blocked=false,rearm=0,replayed=0,scans=0,hypotheses=0;
 function start(){stream=new v4.Stream(e=>{
  const x={...e,sourceAt:origin+e.at,at:now,epoch};
  for(const k of ['first','last','start','end'])if(Number.isFinite(e[k]))x[k]=origin+e[k];
  if(e.evidence)x.evidence=e.evidence.map(h=>({...h,start:origin+h.start}));
  if(e.status==='overflow'){blocked=true;rearm=now+320;}
  events.push(x);
 });}
 start();
 for(const x of pcm){
  ring[now%history]=x;now++;
  if(!blocked){one[0]=x;stream.push(one);}
  if(blocked&&now>=rearm&&epoch<budget){
   scans+=stream.stats.scans;hypotheses+=stream.stats.hypotheses;
   epoch++;origin=Math.max(0,now-history);blocked=false;start();
   events.push({status:'rearm',at:now,epoch,historyFrom:origin,historySamples:now-origin});
   for(let j=origin;j<now&&!blocked;j++){one[0]=ring[j%history];stream.push(one);replayed++;}
  }
 }
 return {events,epoch,replayed,scans:scans+stream.stats.scans,hypotheses:hypotheses+stream.stats.hypotheses};
}
function upstream(v8,pcm,mode,budget,chunk=511){
 const events=[],receiver=new v8.EpochReceiver(e=>events.push(e),mode,budget);
 for(let i=0;i<pcm.length;i+=chunk)receiver.push(pcm.subarray(i,i+chunk));
 const final=receiver.finish();
 return {events,epoch:final.epoch,replayed:receiver.replayed};
}
function run(v1,v2,v4,v8,hash){
 let checks=0;const check=(v,m)=>{checks++;if(!v)throw Error(m);};
 const rows=[],specimens={},calibration=[];
 for(const seed of SEEDS){
  const A={...v1.base,seq:1+seed%16},a=v2.render(A,seed/997);
  const flood=n=>v1.join(z(320),...Array.from({length:n},()=>v1.join(a.slice(0,640),z(640))));
  const f=flood(10),at=upstream(v8,f,'sticky',0).events.find(e=>e.status==='overflow').at;
  calibration.push({seed,at});
  check(eq(upstream(v8,v1.join(z(320),a,z(2400)),'history',4).events.filter(e=>e.status==='ok').map(e=>e.packet),[A]),'isolated control');
  const stimuli=[...OFFSETS.map(offset=>({name:'offset'+offset,start:at+offset,pcm:v1.join(f.slice(0,Math.min(at,at+offset)),z(Math.max(0,offset)),a,z(2400)),budget:1})),{name:'long-flood',start:flood(45).length+24000,pcm:v1.join(flood(45),z(24000),a,z(2400)),budget:4}];
  for(const {name,start,pcm,budget} of stimuli){
   const id=seed+'-'+name,sha256=hash(v1.wav(pcm));
   if(seed===SEEDS[0])specimens[id]=pcm;
   for(const [policy,history] of [['cooldown',0],['history',640],...HIST.map(h=>['candidate'+h,h])]){
    const d=policy.startsWith('candidate')?candidate(v4,pcm,history,budget):upstream(v8,pcm,policy,budget);
    const ok=d.events.filter(e=>e.status==='ok'),resets=d.events.filter(e=>e.status==='rearm'),overflow=d.events.filter(e=>e.status==='overflow');
    check(d.events.every((e,i)=>e.at<=pcm.length&&(!i||e.at>=d.events[i-1].at)&&(e.sourceAt??e.at)<=e.at),'causal');
    check(ok.every(e=>eq(e.packet,A)),'unexpected packet');
    check(d.epoch<=budget&&d.replayed<=history*d.epoch,'bounded replay');
    check(resets.every(e=>e.historySamples<=history),'history bound');
    rows.push({id,seed,name,start,sha256,policy,history,budget,exact:eq(ok.map(e=>e.packet),[A]),accepted:ok.length,release:ok[0]?.at??null,overflows:overflow.map(e=>e.at),rearms:resets.map(e=>({at:e.at,from:e.historyFrom})),replayed:d.replayed,scans:d.scans??null,events:d.events});
   }
  }
 }
 const summary=['cooldown','history',...HIST.map(h=>'candidate'+h)].map(policy=>{
  const r=rows.filter(x=>x.policy===policy);
  return {policy,exact:r.filter(x=>x.exact).length,replayed:r.reduce((s,x)=>s+x.replayed,0),byCondition:[...OFFSETS.map(x=>'offset'+x),'long-flood'].map(name=>{const q=r.filter(x=>x.name===name);return {name,exact:q.filter(x=>x.exact).length,overflow:q.map(x=>x.overflows),rearms:q.map(x=>x.rearms)};})};
 });
 return {checks,calibration,rows,summary,specimens};
}
module.exports={run,candidate,upstream};
if(require.main===module){
 const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),dir=path.resolve(process.argv[2]||'.'),out=path.resolve(process.argv[3]||'history-budget-output');
 for(const [f,sha] of Object.entries(BLOBS)){const b=fs.readFileSync(path.join(dir,f));if(crypto.createHash('sha1').update('blob '+b.length+'\0').update(b).digest('hex')!==sha)throw Error('wrong pinned blob '+f);}
 const v1=require(path.join(dir,'relay.cjs')),v2=require(path.join(dir,'bound-v2.cjs')),v4=require(path.join(dir,'stream-v4.cjs')),v8=require(path.join(dir,'epoch-v8.cjs')),hash=b=>crypto.createHash('sha256').update(b).digest('hex');
 const {specimens,...receipt}=run(v1,v2,v4,v8,hash);fs.mkdirSync(out,{recursive:true});
 const stimuli=Object.entries(specimens).map(([id,pcm])=>{const b=v1.wav(pcm);fs.writeFileSync(path.join(out,id+'.wav'),b);return {id,samples:pcm.length,sha256:hash(b),peak:pcm.reduce((a,b)=>Math.max(a,Math.abs(b)),0)};});
 fs.writeFileSync(path.join(out,'receipt.json'),JSON.stringify({ref:REF,blobs:BLOBS,seeds:SEEDS,offsets:OFFSETS,histories:HIST,...receipt,stimuli},null,2)+'\n');
 console.log(JSON.stringify({checks:receipt.checks,summary:receipt.summary,stimuli},null,2));
}

/* Executed exploratory receipt: one V8 run, actual pinned decoder; native CLI and repeated execution not tested.
{
  "checks": 242,
  "calibration": [
    {
      "seed": 29473,
      "at": 11594
    },
    {
      "seed": 85159,
      "at": 11594
    }
  ],
  "summary": [
    {
      "policy": "cooldown",
      "exact": 2,
      "replayed": 0,
      "byCondition": [
        {
          "name": "offset-960",
          "exact": 0,
          "overflow": [
            [
              11658
            ],
            [
              11658
            ]
          ],
          "rearms": [
            [
              {
                "at": 11978,
                "from": 11978
              }
            ],
            [
              {
                "at": 11978,
                "from": 11978
              }
            ]
          ]
        },
        {
          "name": "offset-640",
          "exact": 0,
          "overflow": [
            [
              11978
            ],
            [
              11978
            ]
          ],
          "rearms": [
            [
              {
                "at": 12298,
                "from": 12298
              }
            ],
            [
              {
                "at": 12298,
                "from": 12298
              }
            ]
          ]
        },
        {
          "name": "offset-480",
          "exact": 0,
          "overflow": [
            [
              12138
            ],
            [
              12138
            ]
          ],
          "rearms": [
            [
              {
                "at": 12458,
                "from": 12458
              }
            ],
            [
              {
                "at": 12458,
                "from": 12458
              }
            ]
          ]
        },
        {
          "name": "offset-320",
          "exact": 0,
          "overflow": [
            [
              11594
            ],
            [
              11594
            ]
          ],
          "rearms": [
            [
              {
                "at": 11914,
                "from": 11914
              }
            ],
            [
              {
                "at": 11914,
                "from": 11914
              }
            ]
          ]
        },
        {
          "name": "offset0",
          "exact": 0,
          "overflow": [
            [
              11594
            ],
            [
              11594
            ]
          ],
          "rearms": [
            [
              {
                "at": 11914,
                "from": 11914
              }
            ],
            [
              {
                "at": 11914,
                "from": 11914
              }
            ]
          ]
        },
        {
          "name": "long-flood",
          "exact": 2,
          "overflow": [
            [
              11594,
              24388,
              37198,
              49992
            ],
            [
              11594,
              24388,
              37198,
              49992
            ]
          ],
          "rearms": [
            [
              {
                "at": 11914,
                "from": 11914
              },
              {
                "at": 24708,
                "from": 24708
              },
              {
                "at": 37518,
                "from": 37518
              },
              {
                "at": 50312,
                "from": 50312
              }
            ],
            [
              {
                "at": 11914,
                "from": 11914
              },
              {
                "at": 24708,
                "from": 24708
              },
              {
                "at": 37518,
                "from": 37518
              },
              {
                "at": 50312,
                "from": 50312
              }
            ]
          ]
        }
      ]
    },
    {
      "policy": "history",
      "exact": 4,
      "replayed": 11520,
      "byCondition": [
        {
          "name": "offset-960",
          "exact": 0,
          "overflow": [
            [
              11658
            ],
            [
              11658
            ]
          ],
          "rearms": [
            [
              {
                "at": 11978,
                "from": 11338
              }
            ],
            [
              {
                "at": 11978,
                "from": 11338
              }
            ]
          ]
        },
        {
          "name": "offset-640",
          "exact": 0,
          "overflow": [
            [
              11978
            ],
            [
              11978
            ]
          ],
          "rearms": [
            [
              {
                "at": 12298,
                "from": 11658
              }
            ],
            [
              {
                "at": 12298,
                "from": 11658
              }
            ]
          ]
        },
        {
          "name": "offset-480",
          "exact": 0,
          "overflow": [
            [
              12138
            ],
            [
              12138
            ]
          ],
          "rearms": [
            [
              {
                "at": 12458,
                "from": 11818
              }
            ],
            [
              {
                "at": 12458,
                "from": 11818
              }
            ]
          ]
        },
        {
          "name": "offset-320",
          "exact": 2,
          "overflow": [
            [
              11594
            ],
            [
              11594
            ]
          ],
          "rearms": [
            [
              {
                "at": 11914,
                "from": 11274
              }
            ],
            [
              {
                "at": 11914,
                "from": 11274
              }
            ]
          ]
        },
        {
          "name": "offset0",
          "exact": 2,
          "overflow": [
            [
              11594
            ],
            [
              11594
            ]
          ],
          "rearms": [
            [
              {
                "at": 11914,
                "from": 11274
              }
            ],
            [
              {
                "at": 11914,
                "from": 11274
              }
            ]
          ]
        },
        {
          "name": "long-flood",
          "exact": 0,
          "overflow": [
            [
              11594,
              23108,
              34638,
              46152,
              57666
            ],
            [
              11594,
              23108,
              34638,
              46152,
              57666
            ]
          ],
          "rearms": [
            [
              {
                "at": 11914,
                "from": 11274
              },
              {
                "at": 23428,
                "from": 22788
              },
              {
                "at": 34958,
                "from": 34318
              },
              {
                "at": 46472,
                "from": 45832
              }
            ],
            [
              {
                "at": 11914,
                "from": 11274
              },
              {
                "at": 23428,
                "from": 22788
              },
              {
                "at": 34958,
                "from": 34318
              },
              {
                "at": 46472,
                "from": 45832
              }
            ]
          ]
        }
      ]
    },
    {
      "policy": "candidate960",
      "exact": 4,
      "replayed": 17280,
      "byCondition": [
        {
          "name": "offset-960",
          "exact": 0,
          "overflow": [
            [
              11658
            ],
            [
              11658
            ]
          ],
          "rearms": [
            [
              {
                "at": 11978,
                "from": 11018
              }
            ],
            [
              {
                "at": 11978,
                "from": 11018
              }
            ]
          ]
        },
        {
          "name": "offset-640",
          "exact": 0,
          "overflow": [
            [
              11978
            ],
            [
              11978
            ]
          ],
          "rearms": [
            [
              {
                "at": 12298,
                "from": 11338
              }
            ],
            [
              {
                "at": 12298,
                "from": 11338
              }
            ]
          ]
        },
        {
          "name": "offset-480",
          "exact": 0,
          "overflow": [
            [
              12138
            ],
            [
              12138
            ]
          ],
          "rearms": [
            [
              {
                "at": 12458,
                "from": 11498
              }
            ],
            [
              {
                "at": 12458,
                "from": 11498
              }
            ]
          ]
        },
        {
          "name": "offset-320",
          "exact": 2,
          "overflow": [
            [
              11594
            ],
            [
              11594
            ]
          ],
          "rearms": [
            [
              {
                "at": 11914,
                "from": 10954
              }
            ],
            [
              {
                "at": 11914,
                "from": 10954
              }
            ]
          ]
        },
        {
          "name": "offset0",
          "exact": 2,
          "overflow": [
            [
              11594
            ],
            [
              11594
            ]
          ],
          "rearms": [
            [
              {
                "at": 11914,
                "from": 10954
              }
            ],
            [
              {
                "at": 11914,
                "from": 10954
              }
            ]
          ]
        },
        {
          "name": "long-flood",
          "exact": 0,
          "overflow": [
            [
              11594,
              23108,
              34638,
              46152,
              57666
            ],
            [
              11594,
              23108,
              34638,
              46152,
              57666
            ]
          ],
          "rearms": [
            [
              {
                "at": 11914,
                "from": 10954
              },
              {
                "at": 23428,
                "from": 22468
              },
              {
                "at": 34958,
                "from": 33998
              },
              {
                "at": 46472,
                "from": 45512
              }
            ],
            [
              {
                "at": 11914,
                "from": 10954
              },
              {
                "at": 23428,
                "from": 22468
              },
              {
                "at": 34958,
                "from": 33998
              },
              {
                "at": 46472,
                "from": 45512
              }
            ]
          ]
        }
      ]
    },
    {
      "policy": "candidate1280",
      "exact": 4,
      "replayed": 23040,
      "byCondition": [
        {
          "name": "offset-960",
          "exact": 0,
          "overflow": [
            [
              11658
            ],
            [
              11658
            ]
          ],
          "rearms": [
            [
              {
                "at": 11978,
                "from": 10698
              }
            ],
            [
              {
                "at": 11978,
                "from": 10698
              }
            ]
          ]
        },
        {
          "name": "offset-640",
          "exact": 0,
          "overflow": [
            [
              11978
            ],
            [
              11978
            ]
          ],
          "rearms": [
            [
              {
                "at": 12298,
                "from": 11018
              }
            ],
            [
              {
                "at": 12298,
                "from": 11018
              }
            ]
          ]
        },
        {
          "name": "offset-480",
          "exact": 0,
          "overflow": [
            [
              12138
            ],
            [
              12138
            ]
          ],
          "rearms": [
            [
              {
                "at": 12458,
                "from": 11178
              }
            ],
            [
              {
                "at": 12458,
                "from": 11178
              }
            ]
          ]
        },
        {
          "name": "offset-320",
          "exact": 2,
          "overflow": [
            [
              11594
            ],
            [
              11594
            ]
          ],
          "rearms": [
            [
              {
                "at": 11914,
                "from": 10634
              }
            ],
            [
              {
                "at": 11914,
                "from": 10634
              }
            ]
          ]
        },
        {
          "name": "offset0",
          "exact": 2,
          "overflow": [
            [
              11594
            ],
            [
              11594
            ]
          ],
          "rearms": [
            [
              {
                "at": 11914,
                "from": 10634
              }
            ],
            [
              {
                "at": 11914,
                "from": 10634
              }
            ]
          ]
        },
        {
          "name": "long-flood",
          "exact": 0,
          "overflow": [
            [
              11594,
              23108,
              34638,
              46152,
              57666
            ],
            [
              11594,
              23108,
              34638,
              46152,
              57666
            ]
          ],
          "rearms": [
            [
              {
                "at": 11914,
                "from": 10634
              },
              {
                "at": 23428,
                "from": 22148
              },
              {
                "at": 34958,
                "from": 33678
              },
              {
                "at": 46472,
                "from": 45192
              }
            ],
            [
              {
                "at": 11914,
                "from": 10634
              },
              {
                "at": 23428,
                "from": 22148
              },
              {
                "at": 34958,
                "from": 33678
              },
              {
                "at": 46472,
                "from": 45192
              }
            ]
          ]
        }
      ]
    },
    {
      "policy": "candidate1920",
      "exact": 10,
      "replayed": 34560,
      "byCondition": [
        {
          "name": "offset-960",
          "exact": 2,
          "overflow": [
            [
              11658
            ],
            [
              11658
            ]
          ],
          "rearms": [
            [
              {
                "at": 11978,
                "from": 10058
              }
            ],
            [
              {
                "at": 11978,
                "from": 10058
              }
            ]
          ]
        },
        {
          "name": "offset-640",
          "exact": 2,
          "overflow": [
            [
              11978
            ],
            [
              11978
            ]
          ],
          "rearms": [
            [
              {
                "at": 12298,
                "from": 10378
              }
            ],
            [
              {
                "at": 12298,
                "from": 10378
              }
            ]
          ]
        },
        {
          "name": "offset-480",
          "exact": 2,
          "overflow": [
            [
              12138
            ],
            [
              12138
            ]
          ],
          "rearms": [
            [
              {
                "at": 12458,
                "from": 10538
              }
            ],
            [
              {
                "at": 12458,
                "from": 10538
              }
            ]
          ]
        },
        {
          "name": "offset-320",
          "exact": 2,
          "overflow": [
            [
              11594
            ],
            [
              11594
            ]
          ],
          "rearms": [
            [
              {
                "at": 11914,
                "from": 9994
              }
            ],
            [
              {
                "at": 11914,
                "from": 9994
              }
            ]
          ]
        },
        {
          "name": "offset0",
          "exact": 2,
          "overflow": [
            [
              11594
            ],
            [
              11594
            ]
          ],
          "rearms": [
            [
              {
                "at": 11914,
                "from": 9994
              }
            ],
            [
              {
                "at": 11914,
                "from": 9994
              }
            ]
          ]
        },
        {
          "name": "long-flood",
          "exact": 0,
          "overflow": [
            [
              11594,
              21828,
              32078,
              42312,
              52546
            ],
            [
              11594,
              21828,
              32078,
              42312,
              52546
            ]
          ],
          "rearms": [
            [
              {
                "at": 11914,
                "from": 9994
              },
              {
                "at": 22148,
                "from": 20228
              },
              {
                "at": 32398,
                "from": 30478
              },
              {
                "at": 42632,
                "from": 40712
              }
            ],
            [
              {
                "at": 11914,
                "from": 9994
              },
              {
                "at": 22148,
                "from": 20228
              },
              {
                "at": 32398,
                "from": 30478
              },
              {
                "at": 42632,
                "from": 40712
              }
            ]
          ]
        }
      ]
    }
  ],
  "stimuli": [
    {
      "id": "29473-offset-960",
      "samples": 44394,
      "sha256": "0854c42e038a26ca9083f2946e3f17fff9fb4673c88a4b71c480b0baf5bdb836",
      "peak": 4096
    },
    {
      "id": "29473-offset-640",
      "samples": 44714,
      "sha256": "3e0bafcfa046a7f2c8bf18084af62198d3ea9d8cad7134d8b64fc74fcc36beb6",
      "peak": 4096
    },
    {
      "id": "29473-offset-480",
      "samples": 44874,
      "sha256": "4b59407801f255de7b519b37f0dec7c084835f9f2e0f13e4e5b23551e45db28f",
      "peak": 4096
    },
    {
      "id": "29473-offset-320",
      "samples": 45034,
      "sha256": "bc28da4b996871488c1fc21c5dafe60506569075bdfe8cca9bba3c975ac7822e",
      "peak": 4096
    },
    {
      "id": "29473-offset0",
      "samples": 45354,
      "sha256": "2fe439fb56c2d29b77c790fce26ec54b8f14c7d613dde3ad01112227634a9f71",
      "peak": 4096
    },
    {
      "id": "29473-long-flood",
      "samples": 115680,
      "sha256": "aa70b6c932a57f12d43b4bf48b869e85ea4a989d9eb774402c2e7fe07c9ee406",
      "peak": 4096
    }
  ]
}
*/
