'use strict';
// Refs #448/#449, #512/#513. Adversarial lane, 2026-11-25. Synthetic only.
// External reset adapter; upstream untouched. No human or security claims.
// First exploratory control with peak 51 failed the upstream 250-count RMS gate.
// Revised low-frame peak 512 tests a deliberately permissive quiet threshold.
const REF='af092b0994f60e54a80b6e294e943a2f042421eb';
const BLOBS={'relay.cjs':'3ba457f85f496e4d57d9789a2dc3b7d68fe2c071','bound-v2.cjs':'2aa2905d4f4d756276814d5ca941c02c51e63f97','stream-v4.cjs':'31769f808469b4416412be25a41eb238bfc1fdde'};
const z=n=>new Int16Array(n),eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const seeds=[48119,93001],thresholds=[0,64,512],lengths=[8000,16000];
function decode(v4,pcm,threshold,required){
 let stream,origin=0,epoch=0,blocked=false,quiet=0;const events=[],one=new Int16Array(1);
 const start=()=>{stream=new v4.Stream(e=>{events.push({...e,epoch,at:origin+e.at});if(e.status==='overflow')blocked=true;});};start();
 for(let i=0;i<pcm.length;i++){
  const x=pcm[i];
  if(blocked){quiet=Math.abs(x)<=threshold?quiet+1:0;
   if(quiet>=required){events.push({status:'reset',epoch,at:i+1});origin=i+1;epoch++;quiet=0;blocked=false;start();}
  }else{one[0]=x;stream.push(one);}
 }
 return events;
}
function run(v1,v2,v4,hash){
 let checks=0;const check=(b,m)=>{checks++;if(!b)throw Error(m);};
 const rows=[],specimens={},controls=[];
 for(const seed of seeds){
  const A={...v1.base,seq:1+seed%16},B={...A,source:2,kind:1,tree:['question',['open']]},phase=seed/997;
  const a=v2.render(A,phase),b=v2.render(B,phase+.7);
  const flood=v1.join(...Array.from({length:10},()=>v1.join(a.slice(0,640),z(640))));
  const low=Int16Array.from(a,x=>Math.round(x/8)),peak=Math.max(...low.map(Math.abs));
  const isolated=v4.decode(v1.join(z(320),low,z(2400))).events.filter(e=>e.status==='ok').map(e=>e.packet);
  controls.push({seed,peak,decoded:eq(isolated,[A])});check(eq(isolated,[A]),'low-level reference must decode');
  const floor=Int16Array.from({length:24000},(_,i)=>i%2?32:-32);
  const impulses=z(24000);for(let i=6000;i<24000;i+=6000)impulses[i]=128;
  const cases=[['quiet',z(24000),null],['floor',floor,null],['impulses',impulses,null],['low-frame',v1.join(z(4000),low,z(24000)),[4000,4000+low.length]]];
  for(const [scenario,gap,interval] of cases){
   const pre=v1.join(z(320),flood),pcm=v1.join(pre,gap,b,z(2400));
   const active=interval?.map(x=>x+pre.length)||null,stimulus=hash(v1.wav(pcm));
   if(seed===seeds[0])specimens[scenario]=pcm;
   for(const threshold of thresholds)for(const required of lengths){
    const events=decode(v4,pcm,threshold,required),accepted=events.filter(e=>e.status==='ok').map(e=>e.packet),resets=events.filter(e=>e.status==='reset').map(e=>e.at);
    check(events.some(e=>e.status==='overflow'),'expected initial overflow');
    check(events.every((e,i)=>e.at<=pcm.length&&(!i||e.at>=events[i-1].at)),'causal trace');
    check(accepted.every(p=>eq(p,A)||eq(p,B)),'unknown packet');
    rows.push({seed,scenario,threshold,required,stimulus,active,resets,resetInside:!!active&&resets.some(t=>t>active[0]&&t<active[1]),a:accepted.some(p=>eq(p,A)),b:accepted.some(p=>eq(p,B)),events});
   }
  }
 }
 const summary=thresholds.flatMap(threshold=>lengths.map(required=>({threshold,required,cases:['quiet','floor','impulses','low-frame'].map(s=>{const r=rows.filter(x=>x.threshold===threshold&&x.required===required&&x.scenario===s);return {s,b:r.filter(x=>x.b).length,a:r.filter(x=>x.a).length,inside:r.filter(x=>x.resetInside).length};})})));
 return {checks,controls,rows,summary,specimens};
}
module.exports={run,decode};
if(require.main===module){
 const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),dir=path.resolve(process.argv[2]||'.'),out=path.resolve(process.argv[3]||'quiet-sweep-output');
 for(const [f,sha] of Object.entries(BLOBS)){const b=fs.readFileSync(path.join(dir,f));if(crypto.createHash('sha1').update('blob '+b.length+'\0').update(b).digest('hex')!==sha)throw Error('wrong pinned blob '+f);}
 const v1=require(path.join(dir,'relay.cjs')),v2=require(path.join(dir,'bound-v2.cjs')),v4=require(path.join(dir,'stream-v4.cjs')),hash=b=>crypto.createHash('sha256').update(b).digest('hex');
 const {specimens,...r}=run(v1,v2,v4,hash);fs.mkdirSync(out,{recursive:true});
 const stimuli=Object.entries(specimens).map(([id,p])=>{const b=v1.wav(p);fs.writeFileSync(path.join(out,id+'.wav'),b);return {id,samples:p.length,sha256:hash(b)};});
 fs.writeFileSync(path.join(out,'receipt.json'),JSON.stringify({ref:REF,blobs:BLOBS,seeds,...r,stimuli},null,2)+'\n');
 console.log(JSON.stringify({checks:r.checks,controls:r.controls,summary:r.summary,stimuli},null,2));
}

/* Executed V8 receipt (two identical row traces; native CLI pending):
{
  "checks": 146,
  "controls": [
    {
      "seed": 48119,
      "peak": 512,
      "decoded": true
    },
    {
      "seed": 93001,
      "peak": 512,
      "decoded": true
    }
  ],
  "summary": [
    {
      "threshold": 0,
      "required": 8000,
      "cases": [
        {
          "s": "quiet",
          "b": 2,
          "a": 0,
          "inside": 0
        },
        {
          "s": "floor",
          "b": 0,
          "a": 0,
          "inside": 0
        },
        {
          "s": "impulses",
          "b": 0,
          "a": 0,
          "inside": 0
        },
        {
          "s": "low-frame",
          "b": 2,
          "a": 0,
          "inside": 0
        }
      ]
    },
    {
      "threshold": 0,
      "required": 16000,
      "cases": [
        {
          "s": "quiet",
          "b": 2,
          "a": 0,
          "inside": 0
        },
        {
          "s": "floor",
          "b": 0,
          "a": 0,
          "inside": 0
        },
        {
          "s": "impulses",
          "b": 0,
          "a": 0,
          "inside": 0
        },
        {
          "s": "low-frame",
          "b": 2,
          "a": 0,
          "inside": 0
        }
      ]
    },
    {
      "threshold": 64,
      "required": 8000,
      "cases": [
        {
          "s": "quiet",
          "b": 2,
          "a": 0,
          "inside": 0
        },
        {
          "s": "floor",
          "b": 2,
          "a": 0,
          "inside": 0
        },
        {
          "s": "impulses",
          "b": 0,
          "a": 0,
          "inside": 0
        },
        {
          "s": "low-frame",
          "b": 2,
          "a": 0,
          "inside": 0
        }
      ]
    },
    {
      "threshold": 64,
      "required": 16000,
      "cases": [
        {
          "s": "quiet",
          "b": 2,
          "a": 0,
          "inside": 0
        },
        {
          "s": "floor",
          "b": 2,
          "a": 0,
          "inside": 0
        },
        {
          "s": "impulses",
          "b": 0,
          "a": 0,
          "inside": 0
        },
        {
          "s": "low-frame",
          "b": 2,
          "a": 0,
          "inside": 0
        }
      ]
    },
    {
      "threshold": 512,
      "required": 8000,
      "cases": [
        {
          "s": "quiet",
          "b": 2,
          "a": 0,
          "inside": 0
        },
        {
          "s": "floor",
          "b": 2,
          "a": 0,
          "inside": 0
        },
        {
          "s": "impulses",
          "b": 2,
          "a": 0,
          "inside": 0
        },
        {
          "s": "low-frame",
          "b": 2,
          "a": 0,
          "inside": 2
        }
      ]
    },
    {
      "threshold": 512,
      "required": 16000,
      "cases": [
        {
          "s": "quiet",
          "b": 2,
          "a": 0,
          "inside": 0
        },
        {
          "s": "floor",
          "b": 2,
          "a": 0,
          "inside": 0
        },
        {
          "s": "impulses",
          "b": 2,
          "a": 0,
          "inside": 0
        },
        {
          "s": "low-frame",
          "b": 2,
          "a": 0,
          "inside": 2
        }
      ]
    }
  ],
  "stimuli": [
    {
      "id": "quiet",
      "samples": 70880,
      "sha256": "b6b96a8822a0a907fc39f3f005d25b756898e1debcb6e382c58f0d9b7f891f8e"
    },
    {
      "id": "floor",
      "samples": 70880,
      "sha256": "e69b04524e760a29dddb31a9afbf0409efab7568077584106b16bc0dadac606c"
    },
    {
      "id": "impulses",
      "samples": 70880,
      "sha256": "ecd57f2d65dffdd14d4e816ea5f8a8270db33e70e9062766e600c2a4c16a102c"
    },
    {
      "id": "low-frame",
      "samples": 106240,
      "sha256": "0a9dba0bb2cd81a054798c694b0477e462be1e635233fe39364d3f0f5d80768c"
    }
  ],
  "selected": [
    {
      "seed": 48119,
      "threshold": 0,
      "required": 8000,
      "active": [
        17120,
        48480
      ],
      "resets": [
        56159
      ],
      "a": false,
      "b": true
    },
    {
      "seed": 48119,
      "threshold": 0,
      "required": 16000,
      "active": [
        17120,
        48480
      ],
      "resets": [
        64159
      ],
      "a": false,
      "b": true
    },
    {
      "seed": 48119,
      "threshold": 64,
      "required": 8000,
      "active": [
        17120,
        48480
      ],
      "resets": [
        56153
      ],
      "a": false,
      "b": true
    },
    {
      "seed": 48119,
      "threshold": 64,
      "required": 16000,
      "active": [
        17120,
        48480
      ],
      "resets": [
        64153
      ],
      "a": false,
      "b": true
    },
    {
      "seed": 48119,
      "threshold": 512,
      "required": 8000,
      "active": [
        17120,
        48480
      ],
      "resets": [
        20475
      ],
      "a": false,
      "b": true
    },
    {
      "seed": 48119,
      "threshold": 512,
      "required": 16000,
      "active": [
        17120,
        48480
      ],
      "resets": [
        28475
      ],
      "a": false,
      "b": true
    },
    {
      "seed": 93001,
      "threshold": 0,
      "required": 8000,
      "active": [
        17120,
        48480
      ],
      "resets": [
        56159
      ],
      "a": false,
      "b": true
    },
    {
      "seed": 93001,
      "threshold": 0,
      "required": 16000,
      "active": [
        17120,
        48480
      ],
      "resets": [
        64159
      ],
      "a": false,
      "b": true
    },
    {
      "seed": 93001,
      "threshold": 64,
      "required": 8000,
      "active": [
        17120,
        48480
      ],
      "resets": [
        56155
      ],
      "a": false,
      "b": true
    },
    {
      "seed": 93001,
      "threshold": 64,
      "required": 16000,
      "active": [
        17120,
        48480
      ],
      "resets": [
        64155
      ],
      "a": false,
      "b": true
    },
    {
      "seed": 93001,
      "threshold": 512,
      "required": 8000,
      "active": [
        17120,
        48480
      ],
      "resets": [
        20475
      ],
      "a": false,
      "b": true
    },
    {
      "seed": 93001,
      "threshold": 512,
      "required": 16000,
      "active": [
        17120,
        48480
      ],
      "resets": [
        28475
      ],
      "a": false,
      "b": true
    }
  ]
}
*/
