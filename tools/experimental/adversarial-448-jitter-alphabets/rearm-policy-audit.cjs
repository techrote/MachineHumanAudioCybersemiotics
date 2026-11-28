'use strict';
// Observatory Adversarial lane, Refs #448 #449 #512. 2026-11-25.
// Exploratory synthetic recovery comparison, fixed policies; no human evidence.
// V4 Stream at pinned Integration v5; no upstream edits. Same PCM for all policies.
const REF='af092b0994f60e54a80b6e294e943a2f042421eb';
const BLOBS={'relay.cjs':'3ba457f85f496e4d57d9789a2dc3b7d68fe2c071','bound-v2.cjs':'2aa2905d4f4d756276814d5ca941c02c51e63f97','stream-v4.cjs':'31769f808469b4416412be25a41eb238bfc1fdde'};
const RATE=16000, seeds=[23147,83591], policies=['peak64','peak128','peak512','rms64','cooldown20'];
const z=n=>new Int16Array(n), eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
function decode(v4,pcm,policy){
 let stream,origin=0,epoch=0,blocked=false,quiet=0,count=0,energy=0,overflowAt=0;
 const events=[],one=new Int16Array(1);
 function start(){stream=new v4.Stream(e=>{
  events.push({...e,epoch,at:origin+e.at});
  if(e.status==='overflow'){blocked=true;overflowAt=origin+e.at;quiet=count=energy=0;}
 });}
 start();
 for(let i=0;i<pcm.length;i++){
  const x=pcm[i];
  if(!blocked){one[0]=x;stream.push(one);continue;}
  // Causal, constant-state recovery observers. No finish() at rearm.
  if(policy==='rms64'){
   energy+=x*x;count++;
   if(count===320){quiet=energy<=320*64**2?quiet+320:0;count=energy=0;}
  }else if(policy==='cooldown20')quiet++;
  else quiet=Math.abs(x)<=Number(policy.slice(4))?quiet+1:0;
  if(quiet>=(policy==='cooldown20'?320:8000)){
   events.push({status:'reset',epoch,at:i+1,discardedSince:overflowAt});
   origin=i+1;epoch++;blocked=false;quiet=count=energy=0;start();
  }
 }
 return events;
}
function run(v1,v2,v4,hash){
 let checks=0;const check=(b,m)=>{checks++;if(!b)throw Error(m);};
 const rows=[],specimens={},controls=[];
 for(const seed of seeds){
  const A={...v1.base,seq:1+seed%16},B={...A,source:2,kind:1,tree:['question',['open']]},phase=seed/997;
  const a=v2.render(A,phase),b=v2.render(B,phase+.7),low=Int16Array.from(a,x=>Math.round(x/8));
  const flood=n=>v1.join(...Array.from({length:n},()=>v1.join(a.slice(0,640),z(640))));
  const pre=v1.join(z(320),flood(10));
  const noisy=Int16Array.from({length:24000},(_,i)=>i%2?32:-32);
  for(let i=6000;i<24000;i+=6000)noisy[i]=256;
  const tone=Int16Array.from({length:24000},(_,i)=>Math.round(220*Math.sin(2*Math.PI*2300*i/RATE)));
  const cases=[
   ['quiet',z(24000),null],
   ['floor-impulses',noisy,null],
   ['tone',tone,null],
   ['weak-early',v1.join(z(4000),low,z(24000)),[4000,4000+low.length]],
   ['weak-late',v1.join(z(12000),low,z(24000)),[12000,12000+low.length]],
   ['continued-preambles',v1.join(flood(18),z(24000)),null]
  ];
  const isolated=v4.decode(v1.join(z(320),low,z(2400))).events.filter(e=>e.status==='ok').map(e=>e.packet);
  check(eq(isolated,[A]),'isolated weak reference');controls.push({seed,weak:true});
  for(const [scenario,gap,interval] of cases){
   const pcm=v1.join(pre,gap,b,z(2400)),active=interval?.map(x=>x+pre.length)||null;
   const stimulus=hash(v1.wav(pcm));
   if(seed===seeds[0])specimens[scenario]=pcm;
   for(const policy of policies){
    const events=decode(v4,pcm,policy),accepted=events.filter(e=>e.status==='ok').map(e=>e.packet);
    const resets=events.filter(e=>e.status==='reset'),overflows=events.filter(e=>e.status==='overflow');
    check(overflows.length>0,'initial overflow');
    check(events.every((e,i)=>e.at<=pcm.length&&(!i||e.at>=events[i-1].at)),'causal event times');
    check(accepted.every(p=>eq(p,A)||eq(p,B)),'unexpected identity');
    check(resets.every(e=>e.at>e.discardedSince),'positive discarded interval');
    rows.push({seed,scenario,policy,stimulus,active,expected:active?[A,B]:[B],a:accepted.some(p=>eq(p,A)),b:accepted.some(p=>eq(p,B)),exact:eq(accepted,active?[A,B]:[B]),inside:!!active&&resets.some(e=>e.at>active[0]&&e.at<active[1]),resets:resets.length,overflows:overflows.length,discarded:resets.reduce((s,e)=>s+e.at-e.discardedSince,0),events});
   }
  }
 }
 const summary=policies.map(policy=>{const p=rows.filter(x=>x.policy===policy);return {policy,exact:p.filter(x=>x.exact).length,b:p.filter(x=>x.b).length,a:p.filter(x=>x.a).length,inside:p.filter(x=>x.inside).length,overflows:p.reduce((s,x)=>s+x.overflows,0),cases:[...new Set(p.map(x=>x.scenario))].map(s=>{const q=p.filter(x=>x.scenario===s);return {s,a:q.filter(x=>x.a).length,b:q.filter(x=>x.b).length,inside:q.filter(x=>x.inside).length,overflows:q.reduce((t,x)=>t+x.overflows,0)};})};});
 return {checks,controls,rows,summary,specimens};
}
module.exports={run,decode};
if(require.main===module){
 const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),dir=path.resolve(process.argv[2]||'.'),out=path.resolve(process.argv[3]||'rearm-policy-output');
 for(const [f,sha] of Object.entries(BLOBS)){const b=fs.readFileSync(path.join(dir,f));if(crypto.createHash('sha1').update('blob '+b.length+'\0').update(b).digest('hex')!==sha)throw Error('wrong pinned blob '+f);}
 const v1=require(path.join(dir,'relay.cjs')),v2=require(path.join(dir,'bound-v2.cjs')),v4=require(path.join(dir,'stream-v4.cjs')),hash=b=>crypto.createHash('sha256').update(b).digest('hex');
 const {specimens,...r}=run(v1,v2,v4,hash);fs.mkdirSync(out,{recursive:true});
 const stimuli=Object.entries(specimens).map(([id,p])=>{const b=v1.wav(p);fs.writeFileSync(path.join(out,id+'.wav'),b);return {id,samples:p.length,sha256:hash(b)};});
 fs.writeFileSync(path.join(out,'receipt.json'),JSON.stringify({ref:REF,blobs:BLOBS,seeds,...r,stimuli},null,2)+'\n');
 console.log(JSON.stringify({checks:r.checks,controls:r.controls,summary:r.summary,stimuli},null,2));
}

/* Executed V8 receipt; two identical full row traces, native CLI pending.
{
  "checks": 242,
  "controls": [
    {
      "seed": 23147,
      "weak": true
    },
    {
      "seed": 83591,
      "weak": true
    }
  ],
  "summary": [
    {
      "policy": "peak64",
      "exact": 6,
      "b": 8,
      "a": 2,
      "inside": 0,
      "overflows": 12,
      "cases": [
        {
          "s": "quiet",
          "a": 0,
          "b": 2,
          "inside": 0,
          "overflows": 2
        },
        {
          "s": "floor-impulses",
          "a": 0,
          "b": 0,
          "inside": 0,
          "overflows": 2
        },
        {
          "s": "tone",
          "a": 0,
          "b": 0,
          "inside": 0,
          "overflows": 2
        },
        {
          "s": "weak-early",
          "a": 0,
          "b": 2,
          "inside": 0,
          "overflows": 2
        },
        {
          "s": "weak-late",
          "a": 2,
          "b": 2,
          "inside": 0,
          "overflows": 2
        },
        {
          "s": "continued-preambles",
          "a": 0,
          "b": 2,
          "inside": 0,
          "overflows": 2
        }
      ]
    },
    {
      "policy": "peak128",
      "exact": 6,
      "b": 8,
      "a": 2,
      "inside": 0,
      "overflows": 12,
      "cases": [
        {
          "s": "quiet",
          "a": 0,
          "b": 2,
          "inside": 0,
          "overflows": 2
        },
        {
          "s": "floor-impulses",
          "a": 0,
          "b": 0,
          "inside": 0,
          "overflows": 2
        },
        {
          "s": "tone",
          "a": 0,
          "b": 0,
          "inside": 0,
          "overflows": 2
        },
        {
          "s": "weak-early",
          "a": 0,
          "b": 2,
          "inside": 0,
          "overflows": 2
        },
        {
          "s": "weak-late",
          "a": 2,
          "b": 2,
          "inside": 0,
          "overflows": 2
        },
        {
          "s": "continued-preambles",
          "a": 0,
          "b": 2,
          "inside": 0,
          "overflows": 2
        }
      ]
    },
    {
      "policy": "peak512",
      "exact": 10,
      "b": 12,
      "a": 2,
      "inside": 2,
      "overflows": 12,
      "cases": [
        {
          "s": "quiet",
          "a": 0,
          "b": 2,
          "inside": 0,
          "overflows": 2
        },
        {
          "s": "floor-impulses",
          "a": 0,
          "b": 2,
          "inside": 0,
          "overflows": 2
        },
        {
          "s": "tone",
          "a": 0,
          "b": 2,
          "inside": 0,
          "overflows": 2
        },
        {
          "s": "weak-early",
          "a": 0,
          "b": 2,
          "inside": 2,
          "overflows": 2
        },
        {
          "s": "weak-late",
          "a": 2,
          "b": 2,
          "inside": 0,
          "overflows": 2
        },
        {
          "s": "continued-preambles",
          "a": 0,
          "b": 2,
          "inside": 0,
          "overflows": 2
        }
      ]
    },
    {
      "policy": "rms64",
      "exact": 8,
      "b": 10,
      "a": 2,
      "inside": 0,
      "overflows": 12,
      "cases": [
        {
          "s": "quiet",
          "a": 0,
          "b": 2,
          "inside": 0,
          "overflows": 2
        },
        {
          "s": "floor-impulses",
          "a": 0,
          "b": 2,
          "inside": 0,
          "overflows": 2
        },
        {
          "s": "tone",
          "a": 0,
          "b": 0,
          "inside": 0,
          "overflows": 2
        },
        {
          "s": "weak-early",
          "a": 0,
          "b": 2,
          "inside": 0,
          "overflows": 2
        },
        {
          "s": "weak-late",
          "a": 2,
          "b": 2,
          "inside": 0,
          "overflows": 2
        },
        {
          "s": "continued-preambles",
          "a": 0,
          "b": 2,
          "inside": 0,
          "overflows": 2
        }
      ]
    },
    {
      "policy": "cooldown20",
      "exact": 12,
      "b": 12,
      "a": 4,
      "inside": 0,
      "overflows": 14,
      "cases": [
        {
          "s": "quiet",
          "a": 0,
          "b": 2,
          "inside": 0,
          "overflows": 2
        },
        {
          "s": "floor-impulses",
          "a": 0,
          "b": 2,
          "inside": 0,
          "overflows": 2
        },
        {
          "s": "tone",
          "a": 0,
          "b": 2,
          "inside": 0,
          "overflows": 2
        },
        {
          "s": "weak-early",
          "a": 2,
          "b": 2,
          "inside": 0,
          "overflows": 2
        },
        {
          "s": "weak-late",
          "a": 2,
          "b": 2,
          "inside": 0,
          "overflows": 2
        },
        {
          "s": "continued-preambles",
          "a": 0,
          "b": 2,
          "inside": 0,
          "overflows": 4
        }
      ]
    }
  ],
  "stimuli": [
    {
      "id": "quiet",
      "samples": 70880,
      "sha256": "4a08471051bc45f81b3841c6ff068755101ec88b649d0b5429c911da5415bff5",
      "peak": 4096
    },
    {
      "id": "floor-impulses",
      "samples": 70880,
      "sha256": "5e9332de658203c31d159c340a771bdb976de13e9af1a88d65c5c513dd4ff4b3",
      "peak": 4096
    },
    {
      "id": "tone",
      "samples": 70880,
      "sha256": "9b6e900863f11aa83961c6327d94de9d886a9dde00f912157873e4e4c0afa9b1",
      "peak": 4096
    },
    {
      "id": "weak-early",
      "samples": 106240,
      "sha256": "1ceee6d2af2639002ca11bdf144702cf6cf71f5077b5926bef7064bb6f5f2fd3",
      "peak": 4096
    },
    {
      "id": "weak-late",
      "samples": 114240,
      "sha256": "7568bc19f46122ecacac77ee0bdf5cf2bbe0b57cd29bb93519d115dddb87714f",
      "peak": 4096
    },
    {
      "id": "continued-preambles",
      "samples": 93920,
      "sha256": "312ac5518a940e66cf3506a39f674f59097eef6a84d07cc593a2202d3d2c9747",
      "peak": 4096
    }
  ],
  "selected": [
    {
      "seed": 23147,
      "scenario": "weak-early",
      "policy": "peak64",
      "a": false,
      "b": true,
      "inside": false,
      "resets": 1,
      "overflows": 1,
      "discarded": 44561,
      "epochs": [
        {
          "status": "overflow",
          "at": 11594,
          "epoch": 0
        },
        {
          "status": "reset",
          "at": 56155,
          "epoch": 0
        },
        {
          "status": "ok",
          "at": 104837,
          "epoch": 1
        }
      ]
    },
    {
      "seed": 23147,
      "scenario": "weak-early",
      "policy": "peak128",
      "a": false,
      "b": true,
      "inside": false,
      "resets": 1,
      "overflows": 1,
      "discarded": 44556,
      "epochs": [
        {
          "status": "overflow",
          "at": 11594,
          "epoch": 0
        },
        {
          "status": "reset",
          "at": 56150,
          "epoch": 0
        },
        {
          "status": "ok",
          "at": 104848,
          "epoch": 1
        }
      ]
    },
    {
      "seed": 23147,
      "scenario": "weak-early",
      "policy": "peak512",
      "a": false,
      "b": true,
      "inside": true,
      "resets": 1,
      "overflows": 1,
      "discarded": 8881,
      "epochs": [
        {
          "status": "overflow",
          "at": 11594,
          "epoch": 0
        },
        {
          "status": "reset",
          "at": 20475,
          "epoch": 0
        },
        {
          "status": "ok",
          "at": 104837,
          "epoch": 1
        }
      ]
    },
    {
      "seed": 23147,
      "scenario": "weak-early",
      "policy": "rms64",
      "a": false,
      "b": true,
      "inside": false,
      "resets": 1,
      "overflows": 1,
      "discarded": 44800,
      "epochs": [
        {
          "status": "overflow",
          "at": 11594,
          "epoch": 0
        },
        {
          "status": "reset",
          "at": 56394,
          "epoch": 0
        },
        {
          "status": "ok",
          "at": 104836,
          "epoch": 1
        }
      ]
    },
    {
      "seed": 23147,
      "scenario": "weak-early",
      "policy": "cooldown20",
      "a": true,
      "b": true,
      "inside": false,
      "resets": 1,
      "overflows": 1,
      "discarded": 320,
      "epochs": [
        {
          "status": "overflow",
          "at": 11594,
          "epoch": 0
        },
        {
          "status": "reset",
          "at": 11914,
          "epoch": 0
        },
        {
          "status": "ok",
          "at": 49476,
          "epoch": 1
        },
        {
          "status": "ok",
          "at": 104836,
          "epoch": 1
        }
      ]
    },
    {
      "seed": 23147,
      "scenario": "continued-preambles",
      "policy": "peak64",
      "a": false,
      "b": true,
      "inside": false,
      "resets": 1,
      "overflows": 1,
      "discarded": 31925,
      "epochs": [
        {
          "status": "overflow",
          "at": 11594,
          "epoch": 0
        },
        {
          "status": "reset",
          "at": 43519,
          "epoch": 0
        },
        {
          "status": "ok",
          "at": 92521,
          "epoch": 1
        }
      ]
    },
    {
      "seed": 23147,
      "scenario": "continued-preambles",
      "policy": "peak128",
      "a": false,
      "b": true,
      "inside": false,
      "resets": 1,
      "overflows": 1,
      "discarded": 31924,
      "epochs": [
        {
          "status": "overflow",
          "at": 11594,
          "epoch": 0
        },
        {
          "status": "reset",
          "at": 43518,
          "epoch": 0
        },
        {
          "status": "ok",
          "at": 92520,
          "epoch": 1
        }
      ]
    },
    {
      "seed": 23147,
      "scenario": "continued-preambles",
      "policy": "peak512",
      "a": false,
      "b": true,
      "inside": false,
      "resets": 1,
      "overflows": 1,
      "discarded": 31921,
      "epochs": [
        {
          "status": "overflow",
          "at": 11594,
          "epoch": 0
        },
        {
          "status": "reset",
          "at": 43515,
          "epoch": 0
        },
        {
          "status": "ok",
          "at": 92517,
          "epoch": 1
        }
      ]
    },
    {
      "seed": 23147,
      "scenario": "continued-preambles",
      "policy": "rms64",
      "a": false,
      "b": true,
      "inside": false,
      "resets": 1,
      "overflows": 1,
      "discarded": 32000,
      "epochs": [
        {
          "status": "overflow",
          "at": 11594,
          "epoch": 0
        },
        {
          "status": "reset",
          "at": 43594,
          "epoch": 0
        },
        {
          "status": "ok",
          "at": 92516,
          "epoch": 1
        }
      ]
    },
    {
      "seed": 23147,
      "scenario": "continued-preambles",
      "policy": "cooldown20",
      "a": false,
      "b": true,
      "inside": false,
      "resets": 2,
      "overflows": 2,
      "discarded": 640,
      "epochs": [
        {
          "status": "overflow",
          "at": 11594,
          "epoch": 0
        },
        {
          "status": "reset",
          "at": 11914,
          "epoch": 0
        },
        {
          "status": "overflow",
          "at": 24388,
          "epoch": 1
        },
        {
          "status": "reset",
          "at": 24708,
          "epoch": 1
        },
        {
          "status": "ok",
          "at": 92526,
          "epoch": 2
        }
      ]
    },
    {
      "seed": 83591,
      "scenario": "weak-early",
      "policy": "peak64",
      "a": false,
      "b": true,
      "inside": false,
      "resets": 1,
      "overflows": 1,
      "discarded": 44556,
      "epochs": [
        {
          "status": "overflow",
          "at": 11594,
          "epoch": 0
        },
        {
          "status": "reset",
          "at": 56150,
          "epoch": 0
        },
        {
          "status": "ok",
          "at": 104848,
          "epoch": 1
        }
      ]
    },
    {
      "seed": 83591,
      "scenario": "weak-early",
      "policy": "peak128",
      "a": false,
      "b": true,
      "inside": false,
      "resets": 1,
      "overflows": 1,
      "discarded": 44554,
      "epochs": [
        {
          "status": "overflow",
          "at": 11594,
          "epoch": 0
        },
        {
          "status": "reset",
          "at": 56148,
          "epoch": 0
        },
        {
          "status": "ok",
          "at": 104846,
          "epoch": 1
        }
      ]
    },
    {
      "seed": 83591,
      "scenario": "weak-early",
      "policy": "peak512",
      "a": false,
      "b": true,
      "inside": true,
      "resets": 1,
      "overflows": 1,
      "discarded": 8881,
      "epochs": [
        {
          "status": "overflow",
          "at": 11594,
          "epoch": 0
        },
        {
          "status": "reset",
          "at": 20475,
          "epoch": 0
        },
        {
          "status": "ok",
          "at": 104837,
          "epoch": 1
        }
      ]
    },
    {
      "seed": 83591,
      "scenario": "weak-early",
      "policy": "rms64",
      "a": false,
      "b": true,
      "inside": false,
      "resets": 1,
      "overflows": 1,
      "discarded": 44800,
      "epochs": [
        {
          "status": "overflow",
          "at": 11594,
          "epoch": 0
        },
        {
          "status": "reset",
          "at": 56394,
          "epoch": 0
        },
        {
          "status": "ok",
          "at": 104836,
          "epoch": 1
        }
      ]
    },
    {
      "seed": 83591,
      "scenario": "weak-early",
      "policy": "cooldown20",
      "a": true,
      "b": true,
      "inside": false,
      "resets": 1,
      "overflows": 1,
      "discarded": 320,
      "epochs": [
        {
          "status": "overflow",
          "at": 11594,
          "epoch": 0
        },
        {
          "status": "reset",
          "at": 11914,
          "epoch": 0
        },
        {
          "status": "ok",
          "at": 49476,
          "epoch": 1
        },
        {
          "status": "ok",
          "at": 104836,
          "epoch": 1
        }
      ]
    },
    {
      "seed": 83591,
      "scenario": "continued-preambles",
      "policy": "peak64",
      "a": false,
      "b": true,
      "inside": false,
      "resets": 1,
      "overflows": 1,
      "discarded": 31924,
      "epochs": [
        {
          "status": "overflow",
          "at": 11594,
          "epoch": 0
        },
        {
          "status": "reset",
          "at": 43518,
          "epoch": 0
        },
        {
          "status": "ok",
          "at": 92520,
          "epoch": 1
        }
      ]
    },
    {
      "seed": 83591,
      "scenario": "continued-preambles",
      "policy": "peak128",
      "a": false,
      "b": true,
      "inside": false,
      "resets": 1,
      "overflows": 1,
      "discarded": 31924,
      "epochs": [
        {
          "status": "overflow",
          "at": 11594,
          "epoch": 0
        },
        {
          "status": "reset",
          "at": 43518,
          "epoch": 0
        },
        {
          "status": "ok",
          "at": 92520,
          "epoch": 1
        }
      ]
    },
    {
      "seed": 83591,
      "scenario": "continued-preambles",
      "policy": "peak512",
      "a": false,
      "b": true,
      "inside": false,
      "resets": 1,
      "overflows": 1,
      "discarded": 31921,
      "epochs": [
        {
          "status": "overflow",
          "at": 11594,
          "epoch": 0
        },
        {
          "status": "reset",
          "at": 43515,
          "epoch": 0
        },
        {
          "status": "ok",
          "at": 92517,
          "epoch": 1
        }
      ]
    },
    {
      "seed": 83591,
      "scenario": "continued-preambles",
      "policy": "rms64",
      "a": false,
      "b": true,
      "inside": false,
      "resets": 1,
      "overflows": 1,
      "discarded": 32000,
      "epochs": [
        {
          "status": "overflow",
          "at": 11594,
          "epoch": 0
        },
        {
          "status": "reset",
          "at": 43594,
          "epoch": 0
        },
        {
          "status": "ok",
          "at": 92516,
          "epoch": 1
        }
      ]
    },
    {
      "seed": 83591,
      "scenario": "continued-preambles",
      "policy": "cooldown20",
      "a": false,
      "b": true,
      "inside": false,
      "resets": 2,
      "overflows": 2,
      "discarded": 640,
      "epochs": [
        {
          "status": "overflow",
          "at": 11594,
          "epoch": 0
        },
        {
          "status": "reset",
          "at": 11914,
          "epoch": 0
        },
        {
          "status": "overflow",
          "at": 24388,
          "epoch": 1
        },
        {
          "status": "reset",
          "at": 24708,
          "epoch": 1
        },
        {
          "status": "ok",
          "at": 92526,
          "epoch": 2
        }
      ]
    }
  ]
}
*/
