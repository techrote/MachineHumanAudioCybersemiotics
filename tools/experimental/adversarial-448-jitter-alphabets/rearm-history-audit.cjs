'use strict';
// Observatory Adversarial lane. Refs #448 #449 #512. 2026-11-25.
// Exploratory synthetic boundary sweep; not human evidence or receiver certification.
const REF='af092b0994f60e54a80b6e294e943a2f042421eb';
const BLOBS={'relay.cjs':'3ba457f85f496e4d57d9789a2dc3b7d68fe2c071','bound-v2.cjs':'2aa2905d4f4d756276814d5ca941c02c51e63f97','stream-v4.cjs':'31769f808469b4416412be25a41eb238bfc1fdde'};
const SEEDS=[16493,79241],OFFSETS=[-320,-160,0,80,160,320,640],POLICIES=[['fresh20',320,0],['immediate',0,0],['replay20',320,320],['replay40',320,640]];
const z=n=>new Int16Array(n),eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
function decode(v4,pcm,[policy,cooldown,history]){
 const events=[],ring=new Int16Array(Math.max(1,history)),one=z(1);
 let stream,origin=0,epoch=0,blocked=false,now=0,rearmAt=0,scans=0,hypotheses=0,replayed=0;
 function start(at){origin=at;stream=new v4.Stream(e=>{
  // Observation-time release is never backdated during history replay.
  events.push({...e,localAt:e.at,sourceAt:origin+e.at,at:now,epoch});
  if(e.status==='overflow'){blocked=true;rearmAt=now+cooldown;}
 });}
 function reset(){
  scans+=stream.stats.scans;hypotheses+=stream.stats.hypotheses;
  const from=Math.max(0,now-history);
  events.push({status:'reset',at:now,epoch,historyFrom:from,historySamples:now-from});
  epoch++;blocked=false;start(from);
  // Replay only samples already observed; bounded single attempt per reset.
  for(let j=from;j<now&&!blocked;j++){one[0]=ring[j%ring.length];stream.push(one);replayed++;}
 }
 start(0);
 for(let i=0;i<pcm.length;i++){
  ring[i%ring.length]=pcm[i];now=i+1;
  if(!blocked){one[0]=pcm[i];stream.push(one);}
  if(blocked&&now>=rearmAt)reset();
 }
 return {events,scans:scans+stream.stats.scans,hypotheses:hypotheses+stream.stats.hypotheses,replayed};
}
function run(v1,v2,v4,hash){
 let checks=0;const check=(b,m)=>{checks++;if(!b)throw Error(m);};
 const rows=[],calibration=[],specimens={};
 for(const seed of SEEDS){
  const A={...v1.base,seq:1+seed%16},a=v2.render(A,seed/997),flood=v1.join(z(320),...Array.from({length:10},()=>v1.join(a.slice(0,640),z(640))));
  const isolated=v4.decode(v1.join(z(320),a,z(2400))).events.filter(e=>e.status==='ok').map(e=>e.packet);
  check(eq(isolated,[A]),'isolated control');
  const of=decode(v4,flood,POLICIES[0]).events.find(e=>e.status==='overflow');
  check(!!of,'calibration overflow');calibration.push({seed,at:of.at});
  for(const offset of OFFSETS){
   const start=of.at+offset;
   // Negative offsets replace the final incomplete-preamble train samples, not additive overlap.
   const pcm=v1.join(flood.slice(0,Math.min(of.at,start)),z(Math.max(0,offset)),a,z(2400));
   const id=seed+'_'+offset,stimulus=hash(v1.wav(pcm));
   if(seed===SEEDS[0])specimens[id]=pcm;
   for(const policy of POLICIES){
    const d=decode(v4,pcm,policy),ok=d.events.filter(e=>e.status==='ok'),overflow=d.events.filter(e=>e.status==='overflow'),resets=d.events.filter(e=>e.status==='reset');
    check(d.events.every((e,i)=>e.at<=pcm.length&&(!i||e.at>=d.events[i-1].at)),'noncausal release');
    check(d.events.every(e=>e.sourceAt===undefined||e.sourceAt<=e.at),'future evidence');
    check(ok.every(e=>eq(e.packet,A)),'unexpected identity');
    check(resets.every(e=>e.historySamples<=policy[2]),'history bound');
    check(d.replayed<=resets.length*policy[2],'replay work bound');
    rows.push({seed,offset,policy:policy[0],stimulus,start,actualOverflow:overflow[0]?.at??null,exact:eq(ok.map(e=>e.packet),[A]),accepted:ok.length,release:ok[0]?.at??null,overflows:overflow.length,resets:resets.length,replayed:d.replayed,scans:d.scans,hypotheses:d.hypotheses,events:d.events});
   }
  }
 }
 const summary=POLICIES.map(([policy])=>{const r=rows.filter(x=>x.policy===policy);return {policy,exact:r.filter(x=>x.exact).length,overflows:r.reduce((s,x)=>s+x.overflows,0),scans:r.reduce((s,x)=>s+x.scans,0),replayed:r.reduce((s,x)=>s+x.replayed,0),byOffset:OFFSETS.map(offset=>{const q=r.filter(x=>x.offset===offset);return {offset,exact:q.filter(x=>x.exact).length,overflow:q.filter(x=>x.actualOverflow!==null).length,release:q.map(x=>x.release===null?null:x.release-x.start)};})};});
 return {checks,calibration,rows,summary,specimens};
}
module.exports={run,decode};
if(require.main===module){
 const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),dir=path.resolve(process.argv[2]||'.'),out=path.resolve(process.argv[3]||'rearm-history-output');
 for(const [f,sha] of Object.entries(BLOBS)){const b=fs.readFileSync(path.join(dir,f));if(crypto.createHash('sha1').update('blob '+b.length+'\0').update(b).digest('hex')!==sha)throw Error('wrong pinned blob '+f);}
 const v1=require(path.join(dir,'relay.cjs')),v2=require(path.join(dir,'bound-v2.cjs')),v4=require(path.join(dir,'stream-v4.cjs')),hash=b=>crypto.createHash('sha256').update(b).digest('hex');
 const {specimens,...r}=run(v1,v2,v4,hash);fs.mkdirSync(out,{recursive:true});
 const stimuli=Object.entries(specimens).map(([id,p])=>{const b=v1.wav(p);fs.writeFileSync(path.join(out,id+'.wav'),b);return {id,samples:p.length,sha256:hash(b),peak:p.reduce((a,b)=>Math.max(a,Math.abs(b)),0)};});
 fs.writeFileSync(path.join(out,'receipt.json'),JSON.stringify({ref:REF,blobs:BLOBS,seeds:SEEDS,offsets:OFFSETS,policies:POLICIES,...r,stimuli},null,2)+'\n');
 console.log(JSON.stringify({checks:r.checks,calibration:r.calibration,summary:r.summary,stimuli},null,2));
}

/* Executed synthetic receipt (V8, two identical full traces; native CLI untested)
{
  "checks": 284,
  "calibration": [
    {
      "seed": 16493,
      "at": 11594
    },
    {
      "seed": 79241,
      "at": 11594
    }
  ],
  "summary": [
    {
      "policy": "fresh20",
      "exact": 4,
      "overflows": 14,
      "scans": 38380,
      "replayed": 0,
      "byOffset": [
        {
          "offset": -320,
          "exact": 0,
          "overflow": 2,
          "release": [
            null,
            null
          ]
        },
        {
          "offset": -160,
          "exact": 0,
          "overflow": 2,
          "release": [
            null,
            null
          ]
        },
        {
          "offset": 0,
          "exact": 0,
          "overflow": 2,
          "release": [
            null,
            null
          ]
        },
        {
          "offset": 80,
          "exact": 0,
          "overflow": 2,
          "release": [
            null,
            null
          ]
        },
        {
          "offset": 160,
          "exact": 0,
          "overflow": 2,
          "release": [
            null,
            null
          ]
        },
        {
          "offset": 320,
          "exact": 2,
          "overflow": 2,
          "release": [
            32410,
            32410
          ]
        },
        {
          "offset": 640,
          "exact": 2,
          "overflow": 2,
          "release": [
            32362,
            32362
          ]
        }
      ]
    },
    {
      "policy": "immediate",
      "exact": 10,
      "overflows": 14,
      "scans": 38660,
      "replayed": 0,
      "byOffset": [
        {
          "offset": -320,
          "exact": 0,
          "overflow": 2,
          "release": [
            null,
            null
          ]
        },
        {
          "offset": -160,
          "exact": 0,
          "overflow": 2,
          "release": [
            null,
            null
          ]
        },
        {
          "offset": 0,
          "exact": 2,
          "overflow": 2,
          "release": [
            32410,
            32410
          ]
        },
        {
          "offset": 80,
          "exact": 2,
          "overflow": 2,
          "release": [
            32362,
            32362
          ]
        },
        {
          "offset": 160,
          "exact": 2,
          "overflow": 2,
          "release": [
            32362,
            32362
          ]
        },
        {
          "offset": 320,
          "exact": 2,
          "overflow": 2,
          "release": [
            32362,
            32362
          ]
        },
        {
          "offset": 640,
          "exact": 2,
          "overflow": 2,
          "release": [
            32362,
            32362
          ]
        }
      ]
    },
    {
      "policy": "replay20",
      "exact": 10,
      "overflows": 14,
      "scans": 38660,
      "replayed": 4480,
      "byOffset": [
        {
          "offset": -320,
          "exact": 0,
          "overflow": 2,
          "release": [
            null,
            null
          ]
        },
        {
          "offset": -160,
          "exact": 0,
          "overflow": 2,
          "release": [
            null,
            null
          ]
        },
        {
          "offset": 0,
          "exact": 2,
          "overflow": 2,
          "release": [
            32410,
            32410
          ]
        },
        {
          "offset": 80,
          "exact": 2,
          "overflow": 2,
          "release": [
            32362,
            32362
          ]
        },
        {
          "offset": 160,
          "exact": 2,
          "overflow": 2,
          "release": [
            32362,
            32362
          ]
        },
        {
          "offset": 320,
          "exact": 2,
          "overflow": 2,
          "release": [
            32362,
            32362
          ]
        },
        {
          "offset": 640,
          "exact": 2,
          "overflow": 2,
          "release": [
            32362,
            32362
          ]
        }
      ]
    },
    {
      "policy": "replay40",
      "exact": 14,
      "overflows": 14,
      "scans": 38940,
      "replayed": 8960,
      "byOffset": [
        {
          "offset": -320,
          "exact": 2,
          "overflow": 2,
          "release": [
            32410,
            32410
          ]
        },
        {
          "offset": -160,
          "exact": 2,
          "overflow": 2,
          "release": [
            32362,
            32362
          ]
        },
        {
          "offset": 0,
          "exact": 2,
          "overflow": 2,
          "release": [
            32362,
            32362
          ]
        },
        {
          "offset": 80,
          "exact": 2,
          "overflow": 2,
          "release": [
            32362,
            32362
          ]
        },
        {
          "offset": 160,
          "exact": 2,
          "overflow": 2,
          "release": [
            32362,
            32362
          ]
        },
        {
          "offset": 320,
          "exact": 2,
          "overflow": 2,
          "release": [
            32362,
            32362
          ]
        },
        {
          "offset": 640,
          "exact": 2,
          "overflow": 2,
          "release": [
            32362,
            32362
          ]
        }
      ]
    }
  ],
  "stimuli": [
    {
      "id": "16493_-320",
      "samples": 45034,
      "sha256": "6b7e2c96f201184927d07d49aa8f4d0a84a848946af815d31fc02a61b21312f3",
      "peak": 4096
    },
    {
      "id": "16493_-160",
      "samples": 45194,
      "sha256": "8cdfaddb88a26e120abf88d84c5d73d7711be3d2f6c1bb8345b02936a9f62630",
      "peak": 4096
    },
    {
      "id": "16493_0",
      "samples": 45354,
      "sha256": "52562cab1c25a34a4fb4d50fb8178e590d19765605b5a549709f54efd3922a37",
      "peak": 4096
    },
    {
      "id": "16493_80",
      "samples": 45434,
      "sha256": "e8a884ebf672240289cd5db6c45f1ec7331872be41fdcb062cb867a73c48459d",
      "peak": 4096
    },
    {
      "id": "16493_160",
      "samples": 45514,
      "sha256": "a499eee447f29166fe7ba537a51964ccea50cc309785137445ae14d462af8384",
      "peak": 4096
    },
    {
      "id": "16493_320",
      "samples": 45674,
      "sha256": "6dc2c51c32ad9b43aa3041c79854690589981daa1ee9eb1058b69b206d7d588f",
      "peak": 4096
    },
    {
      "id": "16493_640",
      "samples": 45994,
      "sha256": "ead86c7502d2c5de6a801006381161ab6f3c9e63b0ac2c041a939fb2c5c92d0d",
      "peak": 4096
    }
  ]
}
*/
