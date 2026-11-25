'use strict';
// Refs #448/#449 and #512/#513. Adversarial lane, synthetic only, 2026-11-25.
// Read-only pinned v4; external epoch adapter is an experimental candidate, not an integration change.
// No human evidence, security claim, device control or independent review.
const REF="af092b0994f60e54a80b6e294e943a2f042421eb", BLOBS={"relay.cjs":"3ba457f85f496e4d57d9789a2dc3b7d68fe2c071","bound-v2.cjs":"2aa2905d4f4d756276814d5ca941c02c51e63f97","stream-v4.cjs":"31769f808469b4416412be25a41eb238bfc1fdde"};
const seeds=[73181,94007], quietSamples=16000, threshold=64;
const z=n=>new Int16Array(n), eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
function epochDecode(v4,pcm,mode,chunk=511){
 let stream,origin=0,epoch=0,total=0,quiet=0,blocked=false;
 const events=[];let epochs=0;
 const start=()=>{epochs++;stream=new v4.Stream(e=>{events.push({...e,epoch,at:origin+e.at,first:e.first==null?null:origin+e.first,last:e.last==null?null:origin+e.last,start:e.start==null?null:origin+e.start,end:e.end==null?null:origin+e.end});if(e.status==='overflow')blocked=true;});};
 start();
 // Process causal samples only. Once overflow occurs, discard tainted epoch,
 // retain its emitted event history, and require a new observed quiet run.
 // Never finish() an abandoned epoch: EOF is not observed silence.
 const one=new Int16Array(1);
 for(let i=0;i<pcm.length;i+=chunk)for(const x of pcm.subarray(i,i+chunk)){
  total++;
  if(blocked){
   quiet=(mode==='exact'?x===0:Math.abs(x)<=threshold)?quiet+1:0;
   if(mode!=='sticky'&&quiet>=quietSamples){
    events.push({status:'epoch-reset',at:total,epoch,quietSamples,mode});
    epoch++;origin=total;quiet=0;blocked=false;start();
   }
  }else{one[0]=x;stream.push(one);}
 }
 // Continuous stream horizon, not EOF; no terminal flush on any branch.
 return {events,epochs};
}
function run(v1,v2,v4,hash){
 let assertions=0;const check=(x,m)=>{assertions++;if(!x)throw Error(m);};
 const rows=[],specimens={};
 const scenarios=['clean','short-quiet','long-quiet','quiet-floor','interrupted-quiet','prehistory','second-overflow'];
 for(const seed of seeds){
  let state=seed;const rnd=()=>{state=(Math.imul(state,1664525)+1013904223)>>>0;return state/4294967296;};
  const A={...v1.base,seq:1+seed%16},B={...A,source:2,actor:3,event:2,kind:1,tree:['question',['open']]},C={...A,source:3,seq:1+(seed+1)%16};
  const a=v2.render(A,rnd()*2*Math.PI),b=v2.render(B,rnd()*2*Math.PI),c=v2.render(C,rnd()*2*Math.PI);
  const offset=160+Math.floor(rnd()*480),flood=v1.join(...Array.from({length:10},()=>v1.join(a.slice(0,640),z(640))));
  const floor=Int16Array.from({length:24000},()=>rnd()<.5?-32:32);
  const interrupted=z(24000);interrupted[12000]=256;
  for(const scenario of scenarios){
   let pcm,expected,after;
   if(scenario==='clean'){pcm=v1.join(z(offset),a,z(24000),b,z(1600));expected=[A,B];after=expected;}
   else{
    const gap=scenario==='short-quiet'?z(8000):scenario==='quiet-floor'?floor:scenario==='interrupted-quiet'?interrupted:z(24000);
    const prefix=scenario==='prehistory'?v1.join(c,z(24000)):z(0);
    const second=scenario==='second-overflow'?v1.join(flood,z(24000),c):z(0);
    pcm=v1.join(z(offset),prefix,flood,gap,b,z(24000),second,z(1600));
    expected=scenario==='prehistory'?[C,B]:scenario==='second-overflow'?[B,C]:[B];after=expected;
   }
   const raw=v4.decode(pcm); // EOF reference separately reported; padding allows regular release.
   const rawEvents=raw.events.filter(e=>e.status==='ok').map(e=>e.packet);
   for(const mode of ['sticky','exact','threshold']){
    const r=epochDecode(v4,pcm,mode), accepted=r.events.filter(e=>e.status==='ok').map(e=>e.packet);
    const resets=r.events.filter(e=>e.status==='epoch-reset'),overflows=r.events.filter(e=>e.status==='overflow');
    const unknown=accepted.filter(p=>!expected.some(q=>eq(p,q))).length;
    check(r.events.every((e,i)=>e.at<=pcm.length&&(!i||e.at>=r.events[i-1].at)),'causal order');
    check(resets.every(e=>r.events.some(o=>o.status==='overflow'&&o.epoch===e.epoch&&o.at<e.at)),'reset must follow overflow');
    check(mode!=='sticky'||eq(accepted,rawEvents),'sticky matches padded native receiver');
    check(!unknown,'unexpected packet in declared fixtures');
    if(seed===seeds[0]&&mode==='threshold')check(eq(r,epochDecode(v4,pcm,mode,127)),'chunk invariant');
    rows.push({seed,scenario,mode,samples:pcm.length,expected,accepted,exact:eq(expected,accepted),unknown,resets:resets.map(e=>e.at),overflows:overflows.map(e=>e.at),epochs:r.epochs,events:r.events,sha256:hash(v1.wav(pcm))});
   }
   if(seed===seeds[0])specimens[scenario]=pcm;
  }
 }
 const summary=scenarios.map(s=>({scenario:s,modes:['sticky','exact','threshold'].map(mode=>{const r=rows.filter(x=>x.scenario===s&&x.mode===mode);return {mode,exact:r.filter(x=>x.exact).length,packets:r.reduce((a,x)=>a+x.accepted.length,0),resets:r.reduce((a,x)=>a+x.resets.length,0),overflows:r.reduce((a,x)=>a+x.overflows.length,0)};})}));
 return {rows,summary,assertions,specimens};
}
module.exports={run,epochDecode};
if(require.main===module){
 const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
 const dir=path.resolve(process.argv[2]||'.'),out=path.resolve(process.argv[3]||'epoch-output');
 for(const [f,sha] of Object.entries(BLOBS)){const b=fs.readFileSync(path.join(dir,f));if(crypto.createHash('sha1').update('blob '+b.length+'\\0').update(b).digest('hex')!==sha)throw Error('wrong pinned blob '+f);}
 const v1=require(path.join(dir,'relay.cjs')),v2=require(path.join(dir,'bound-v2.cjs')),v4=require(path.join(dir,'stream-v4.cjs'));
 const hash=b=>crypto.createHash('sha256').update(b).digest('hex'),r=run(v1,v2,v4,hash);fs.mkdirSync(out,{recursive:true});
 const stimuli=Object.entries(r.specimens).map(([id,p])=>{const b=v1.wav(p);fs.writeFileSync(path.join(out,id+'.wav'),b);return {id,samples:p.length,sha256:hash(b)};});
 fs.writeFileSync(path.join(out,'receipt.json'),JSON.stringify({ref:REF,blobs:BLOBS,seeds,assertions:r.assertions,summary:r.summary,rows:r.rows,stimuli},null,2)+'\\n');
 console.log(JSON.stringify({assertions:r.assertions,summary:r.summary,stimuli},null,2));
}

/* Executed V8 receipt: two identical full traces, SHA256 shim verified against abc and empty. Native Node CLI not executed. Pinned connector Git blob IDs; CLI verifies them. No claim of acoustic hardware, human evidence, or safe generic reset: threshold is arbitrary, an interruption restarts the count, low-energy valid signals can be mistaken for quiet, and a new epoch does not resolve lost history. No EOF used in candidate.\n{
  "assertions": 175,
  "summary": [
    {
      "scenario": "clean",
      "modes": [
        {
          "mode": "sticky",
          "exact": 2,
          "packets": 4,
          "resets": 0,
          "overflows": 0
        },
        {
          "mode": "exact",
          "exact": 2,
          "packets": 4,
          "resets": 0,
          "overflows": 0
        },
        {
          "mode": "threshold",
          "exact": 2,
          "packets": 4,
          "resets": 0,
          "overflows": 0
        }
      ]
    },
    {
      "scenario": "short-quiet",
      "modes": [
        {
          "mode": "sticky",
          "exact": 0,
          "packets": 0,
          "resets": 0,
          "overflows": 2
        },
        {
          "mode": "exact",
          "exact": 0,
          "packets": 0,
          "resets": 2,
          "overflows": 2
        },
        {
          "mode": "threshold",
          "exact": 0,
          "packets": 0,
          "resets": 2,
          "overflows": 2
        }
      ]
    },
    {
      "scenario": "long-quiet",
      "modes": [
        {
          "mode": "sticky",
          "exact": 0,
          "packets": 0,
          "resets": 0,
          "overflows": 2
        },
        {
          "mode": "exact",
          "exact": 2,
          "packets": 2,
          "resets": 2,
          "overflows": 2
        },
        {
          "mode": "threshold",
          "exact": 2,
          "packets": 2,
          "resets": 2,
          "overflows": 2
        }
      ]
    },
    {
      "scenario": "quiet-floor",
      "modes": [
        {
          "mode": "sticky",
          "exact": 0,
          "packets": 0,
          "resets": 0,
          "overflows": 2
        },
        {
          "mode": "exact",
          "exact": 0,
          "packets": 0,
          "resets": 2,
          "overflows": 2
        },
        {
          "mode": "threshold",
          "exact": 2,
          "packets": 2,
          "resets": 2,
          "overflows": 2
        }
      ]
    },
    {
      "scenario": "interrupted-quiet",
      "modes": [
        {
          "mode": "sticky",
          "exact": 0,
          "packets": 0,
          "resets": 0,
          "overflows": 2
        },
        {
          "mode": "exact",
          "exact": 0,
          "packets": 0,
          "resets": 2,
          "overflows": 2
        },
        {
          "mode": "threshold",
          "exact": 0,
          "packets": 0,
          "resets": 2,
          "overflows": 2
        }
      ]
    },
    {
      "scenario": "prehistory",
      "modes": [
        {
          "mode": "sticky",
          "exact": 0,
          "packets": 2,
          "resets": 0,
          "overflows": 2
        },
        {
          "mode": "exact",
          "exact": 2,
          "packets": 4,
          "resets": 2,
          "overflows": 2
        },
        {
          "mode": "threshold",
          "exact": 2,
          "packets": 4,
          "resets": 2,
          "overflows": 2
        }
      ]
    },
    {
      "scenario": "second-overflow",
      "modes": [
        {
          "mode": "sticky",
          "exact": 0,
          "packets": 0,
          "resets": 0,
          "overflows": 2
        },
        {
          "mode": "exact",
          "exact": 2,
          "packets": 4,
          "resets": 4,
          "overflows": 4
        },
        {
          "mode": "threshold",
          "exact": 2,
          "packets": 4,
          "resets": 4,
          "overflows": 4
        }
      ]
    }
  ],
  "stimuli": [
    {
      "id": "clean",
      "samples": 88750,
      "sha256": "b2916e9b7b9da946410000f777b0e9fdc9624549d28d0ab528b0d63060a1b79b"
    },
    {
      "id": "short-quiet",
      "samples": 78190,
      "sha256": "9121c6445410550164ba69125d8e06aa44b16de0f0a0e8ecba610aa9821f3928"
    },
    {
      "id": "long-quiet",
      "samples": 94190,
      "sha256": "f2691438cf8fd3a924771027f836ef0bf62a2b8717cebc2f7c3f35bd2a82ab06"
    },
    {
      "id": "quiet-floor",
      "samples": 94190,
      "sha256": "9a3838b0be25c3c792eecbf17c5f26269cb44afba0f9ecbe8f673498ecd0d589"
    },
    {
      "id": "interrupted-quiet",
      "samples": 94190,
      "sha256": "68fd461fdc3065577f54bc8c96210c3110137de2ee24a48d84807c4219bdb858"
    },
    {
      "id": "prehistory",
      "samples": 149550,
      "sha256": "524bac95aa29aed15f8e7c308f4696ce60351e469806c0405689c003e873a533"
    },
    {
      "id": "second-overflow",
      "samples": 162350,
      "sha256": "91ba41ee78c26c96c82766d0f31844f86968a94a38d594804940550dc18fb8f4"
    }
  ],
  "detail": [
    {
      "seed": 73181,
      "scenario": "clean",
      "mode": "sticky",
      "resets": [],
      "overflows": [],
      "accepted": [
        1,
        2
      ],
      "release": [
        32794,
        88154
      ]
    },
    {
      "seed": 73181,
      "scenario": "clean",
      "mode": "exact",
      "resets": [],
      "overflows": [],
      "accepted": [
        1,
        2
      ],
      "release": [
        32794,
        88154
      ]
    },
    {
      "seed": 73181,
      "scenario": "clean",
      "mode": "threshold",
      "resets": [],
      "overflows": [],
      "accepted": [
        1,
        2
      ],
      "release": [
        32794,
        88154
      ]
    },
    {
      "seed": 73181,
      "scenario": "short-quiet",
      "mode": "sticky",
      "resets": [],
      "overflows": [
        11706
      ],
      "accepted": [],
      "release": []
    },
    {
      "seed": 73181,
      "scenario": "short-quiet",
      "mode": "exact",
      "resets": [
        68269
      ],
      "overflows": [
        11706
      ],
      "accepted": [],
      "release": []
    },
    {
      "seed": 73181,
      "scenario": "short-quiet",
      "mode": "threshold",
      "resets": [
        68269
      ],
      "overflows": [
        11706
      ],
      "accepted": [],
      "release": []
    },
    {
      "seed": 73181,
      "scenario": "long-quiet",
      "mode": "sticky",
      "resets": [],
      "overflows": [
        11706
      ],
      "accepted": [],
      "release": []
    },
    {
      "seed": 73181,
      "scenario": "long-quiet",
      "mode": "exact",
      "resets": [
        28589
      ],
      "overflows": [
        11706
      ],
      "accepted": [
        2
      ],
      "release": [
        69591
      ]
    },
    {
      "seed": 73181,
      "scenario": "long-quiet",
      "mode": "threshold",
      "resets": [
        28589
      ],
      "overflows": [
        11706
      ],
      "accepted": [
        2
      ],
      "release": [
        69591
      ]
    },
    {
      "seed": 73181,
      "scenario": "quiet-floor",
      "mode": "sticky",
      "resets": [],
      "overflows": [
        11706
      ],
      "accepted": [],
      "release": []
    },
    {
      "seed": 73181,
      "scenario": "quiet-floor",
      "mode": "exact",
      "resets": [
        84269
      ],
      "overflows": [
        11706
      ],
      "accepted": [],
      "release": []
    },
    {
      "seed": 73181,
      "scenario": "quiet-floor",
      "mode": "threshold",
      "resets": [
        28589
      ],
      "overflows": [
        11706
      ],
      "accepted": [
        2
      ],
      "release": [
        69591
      ]
    },
    {
      "seed": 73181,
      "scenario": "interrupted-quiet",
      "mode": "sticky",
      "resets": [],
      "overflows": [
        11706
      ],
      "accepted": [],
      "release": []
    },
    {
      "seed": 73181,
      "scenario": "interrupted-quiet",
      "mode": "exact",
      "resets": [
        84269
      ],
      "overflows": [
        11706
      ],
      "accepted": [],
      "release": []
    },
    {
      "seed": 73181,
      "scenario": "interrupted-quiet",
      "mode": "threshold",
      "resets": [
        84269
      ],
      "overflows": [
        11706
      ],
      "accepted": [],
      "release": []
    },
    {
      "seed": 73181,
      "scenario": "prehistory",
      "mode": "sticky",
      "resets": [],
      "overflows": [
        67066
      ],
      "accepted": [
        3
      ],
      "release": [
        32794
      ]
    },
    {
      "seed": 73181,
      "scenario": "prehistory",
      "mode": "exact",
      "resets": [
        83949
      ],
      "overflows": [
        67066
      ],
      "accepted": [
        3,
        2
      ],
      "release": [
        32794,
        124951
      ]
    },
    {
      "seed": 73181,
      "scenario": "prehistory",
      "mode": "threshold",
      "resets": [
        83949
      ],
      "overflows": [
        67066
      ],
      "accepted": [
        3,
        2
      ],
      "release": [
        32794,
        124951
      ]
    },
    {
      "seed": 73181,
      "scenario": "second-overflow",
      "mode": "sticky",
      "resets": [],
      "overflows": [
        11706
      ],
      "accepted": [],
      "release": []
    },
    {
      "seed": 73181,
      "scenario": "second-overflow",
      "mode": "exact",
      "resets": [
        28589,
        120749
      ],
      "overflows": [
        11706,
        103863
      ],
      "accepted": [
        2,
        3
      ],
      "release": [
        69591,
        161751
      ]
    },
    {
      "seed": 73181,
      "scenario": "second-overflow",
      "mode": "threshold",
      "resets": [
        28589,
        120749
      ],
      "overflows": [
        11706,
        103863
      ],
      "accepted": [
        2,
        3
      ],
      "release": [
        69591,
        161751
      ]
    },
    {
      "seed": 94007,
      "scenario": "clean",
      "mode": "sticky",
      "resets": [],
      "overflows": [],
      "accepted": [
        1,
        2
      ],
      "release": [
        32746,
        88106
      ]
    },
    {
      "seed": 94007,
      "scenario": "clean",
      "mode": "exact",
      "resets": [],
      "overflows": [],
      "accepted": [
        1,
        2
      ],
      "release": [
        32746,
        88106
      ]
    },
    {
      "seed": 94007,
      "scenario": "clean",
      "mode": "threshold",
      "resets": [],
      "overflows": [],
      "accepted": [
        1,
        2
      ],
      "release": [
        32746,
        88106
      ]
    },
    {
      "seed": 94007,
      "scenario": "short-quiet",
      "mode": "sticky",
      "resets": [],
      "overflows": [
        11658
      ],
      "accepted": [],
      "release": []
    },
    {
      "seed": 94007,
      "scenario": "short-quiet",
      "mode": "exact",
      "resets": [
        68222
      ],
      "overflows": [
        11658
      ],
      "accepted": [],
      "release": []
    },
    {
      "seed": 94007,
      "scenario": "short-quiet",
      "mode": "threshold",
      "resets": [
        68221
      ],
      "overflows": [
        11658
      ],
      "accepted": [],
      "release": []
    },
    {
      "seed": 94007,
      "scenario": "long-quiet",
      "mode": "sticky",
      "resets": [],
      "overflows": [
        11658
      ],
      "accepted": [],
      "release": []
    },
    {
      "seed": 94007,
      "scenario": "long-quiet",
      "mode": "exact",
      "resets": [
        28542
      ],
      "overflows": [
        11658
      ],
      "accepted": [
        2
      ],
      "release": [
        69544
      ]
    },
    {
      "seed": 94007,
      "scenario": "long-quiet",
      "mode": "threshold",
      "resets": [
        28542
      ],
      "overflows": [
        11658
      ],
      "accepted": [
        2
      ],
      "release": [
        69544
      ]
    },
    {
      "seed": 94007,
      "scenario": "quiet-floor",
      "mode": "sticky",
      "resets": [],
      "overflows": [
        11658
      ],
      "accepted": [],
      "release": []
    },
    {
      "seed": 94007,
      "scenario": "quiet-floor",
      "mode": "exact",
      "resets": [
        84222
      ],
      "overflows": [
        11658
      ],
      "accepted": [],
      "release": []
    },
    {
      "seed": 94007,
      "scenario": "quiet-floor",
      "mode": "threshold",
      "resets": [
        28542
      ],
      "overflows": [
        11658
      ],
      "accepted": [
        2
      ],
      "release": [
        69544
      ]
    },
    {
      "seed": 94007,
      "scenario": "interrupted-quiet",
      "mode": "sticky",
      "resets": [],
      "overflows": [
        11658
      ],
      "accepted": [],
      "release": []
    },
    {
      "seed": 94007,
      "scenario": "interrupted-quiet",
      "mode": "exact",
      "resets": [
        84222
      ],
      "overflows": [
        11658
      ],
      "accepted": [],
      "release": []
    },
    {
      "seed": 94007,
      "scenario": "interrupted-quiet",
      "mode": "threshold",
      "resets": [
        84221
      ],
      "overflows": [
        11658
      ],
      "accepted": [],
      "release": []
    },
    {
      "seed": 94007,
      "scenario": "prehistory",
      "mode": "sticky",
      "resets": [],
      "overflows": [
        67018
      ],
      "accepted": [
        3
      ],
      "release": [
        32746
      ]
    },
    {
      "seed": 94007,
      "scenario": "prehistory",
      "mode": "exact",
      "resets": [
        83902
      ],
      "overflows": [
        67018
      ],
      "accepted": [
        3,
        2
      ],
      "release": [
        32746,
        124904
      ]
    },
    {
      "seed": 94007,
      "scenario": "prehistory",
      "mode": "threshold",
      "resets": [
        83902
      ],
      "overflows": [
        67018
      ],
      "accepted": [
        3,
        2
      ],
      "release": [
        32746,
        124904
      ]
    },
    {
      "seed": 94007,
      "scenario": "second-overflow",
      "mode": "sticky",
      "resets": [],
      "overflows": [
        11658
      ],
      "accepted": [],
      "release": []
    },
    {
      "seed": 94007,
      "scenario": "second-overflow",
      "mode": "exact",
      "resets": [
        28542,
        120702
      ],
      "overflows": [
        11658,
        103816
      ],
      "accepted": [
        2,
        3
      ],
      "release": [
        69544,
        161704
      ]
    },
    {
      "seed": 94007,
      "scenario": "second-overflow",
      "mode": "threshold",
      "resets": [
        28542,
        120702
      ],
      "overflows": [
        11658,
        103816
      ],
      "accepted": [
        2,
        3
      ],
      "release": [
        69544,
        161704
      ]
    }
  ]
}
*/
