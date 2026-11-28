'use strict';
// Refs #448/#449; independent audit of Integration #513 v3, 2026-11-25.
// Synthetic single-frame receiver stress tests; no authority or human claims.
// No vendoring, no wire changes, no receiver tuning; same PCM to both receivers.
// Upstream draft is a pinned experimental comparator, not accepted evidence.
// AI: one GPT-6.2 agent; no independent review.
const REF='a62f4d485998dca3d64baa9ed8a87fda982f7aea';
const BLOBS={'relay.cjs':'3ba457f85f496e4d57d9789a2dc3b7d68fe2c071','bound-v2.cjs':'2aa2905d4f4d756276814d5ca941c02c51e63f97','clock-v3.cjs':'1f629ae5dc1a995326ff47cba1a6338f16c080df'};
const EQ=(a,b)=>JSON.stringify(a)===JSON.stringify(b), zeros=n=>new Int16Array(n);
const seeds=[13217,28793];
const conditions=[
 ['clean',[],1,0,0],['one-cut',[0],1,0,0],['two-cuts',[0,1],1,0,0],
 ['three-cuts',[0,1,2],1,0,0],['distributed-cuts',[0,8,16],1,0,0],
 ['scale-plus',[],1.009,0,0],['scale-minus',[],.991,0,0],
 ['mixed-plus',[0,8],1.009,800,0],['mixed-minus',[0,8],.991,800,0],
 ['noise',[],1,1600,0],['isolated-preamble',[],1,0,640],
 ['isolated-preamble-noise',[],1,800,640]];
function run(v1,v2,v3,hash){
 let assertions=0;const check=(x,m)=>{assertions++;if(!x)throw Error(m);};
 const rows=[],specimens={},metrics=[];
 for(const [name,cuts,scale,noise,decoy] of conditions){
  const m={name,removedSamples:cuts.length*240,scale,noisePeak:noise,decoyGap:decoy,fixed:{correct:0,wrong:0,refused:0},clock:{correct:0,wrong:0,refused:0},statuses:{},oracle:{correct:0,wrong:0,refused:0}};
  for(const seed of seeds)for(const kind of [0,1]){
   let state=seed;const random=()=>{state=(Math.imul(state,1664525)+1013904223)>>>0;return state/4294967296;};
   const packet={...v1.base,kind,seq:1+seed%16,version:1+(seed>>>3)%16},phase=random()*2*Math.PI,offset=160+Math.floor(random()*480);
   const raw=v2.render(packet,phase);let p=raw;
   // Delete exactly 240 samples from each chosen 320-sample silent guard, descending indices.
   for(const k of [...cuts].reverse()){const end=640+(k+1)*1280;check(p.slice(end-240,end).every(x=>x===0),'only silence');p=v1.join(p.slice(0,end-240),p.slice(end));}
   check(p.reduce((s,x)=>s+x*x,0)===raw.reduce((s,x)=>s+x*x,0),'energy preservation before noise/resampling');
   if(scale!==1){const q=p;p=Int16Array.from({length:Math.round(q.length*scale)},(_,i)=>{const t=i/scale,k=Math.floor(t),f=t-k;return Math.round((q[k]||0)*(1-f)+(q[k+1]||0)*f);});}
   const prefix=decoy?v1.join(raw.slice(0,640),zeros(decoy)):zeros(0);
   let pcm=v1.join(zeros(offset),prefix,p,zeros(640));
   if(noise)pcm=Int16Array.from(pcm,x=>Math.round(x+(2*random()-1)*noise));
   check(pcm.length<=v3.MAX,'capture bound');
   const fixed=v2.acquire(pcm).filter(h=>h.status==='ok').map(h=>h.packet),clock=v3.acquire(pcm);
   const classify=a=>a.length===0?'refused':a.length===1&&EQ(a[0],packet)?'correct':'wrong';
   const a=classify(fixed),b=classify(clock.packet?[clock.packet]:[]);
   // Privileged clean-reference control, NOT inverse recovery of mixed channel noise.
   const control=v3.acquire(v1.join(zeros(offset),raw,zeros(640))),c=classify(control.packet?[control.packet]:[]);
   check(c==='correct','clean-reference control');m.fixed[a]++;m.clock[b]++;m.oracle[c]++;m.statuses[clock.status]=(m.statuses[clock.status]||0)+1;
   const peak=pcm.reduce((s,x)=>Math.max(s,Math.abs(x)),0);check(peak<=4096+noise,'peak');
   const id=name+'-'+seed+'-'+kind,sha256=hash(v1.wav(pcm));
   rows.push({id,seed,kind,packet,phase,offset,sha256,samples:pcm.length,peak,fixed:a,clock:b,clockEvidence:clock,control:c});
   if(seed===seeds[0]&&kind===0)specimens[id]=pcm;
  }
  for(const k of ['fixed','clock','oracle'])check(Object.values(m[k]).reduce((s,x)=>s+x,0)===4,'outcome partition');metrics.push(m);
 }
 return {summary:{ref:REF,blobs:BLOBS,seeds,streams:rows.length,assertions,metrics},rows,specimens};
}
module.exports={run};
if(require.main===module){
 const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
 const dir=path.resolve(process.argv[2]||'.'),out=path.resolve(process.argv[3]||'clock-v3-audit-output');
 const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
 for(const [file,sha] of Object.entries(BLOBS)){const b=fs.readFileSync(path.join(dir,file)),got=crypto.createHash('sha1').update('blob '+b.length+'\0').update(b).digest('hex');if(got!==sha)throw Error('wrong upstream blob '+file);}
 const v1=require(path.join(dir,'relay.cjs')),v2=require(path.join(dir,'bound-v2.cjs')),v3=require(path.join(dir,'clock-v3.cjs'));
 const r=run(v1,v2,v3,hash);fs.mkdirSync(out,{recursive:true});
 for(const [id,p] of Object.entries(r.specimens)){const wav=v1.wav(p);fs.writeFileSync(path.join(out,id+'.wav'),wav);const a=p.reduce((s,x)=>Math.max(s,Math.abs(x)),0);const quiet=Int16Array.from(p,x=>Math.round(x*Math.min(1,4096/Math.max(1,a))));fs.writeFileSync(path.join(out,id+'-audition.wav'),v1.wav(quiet));}
 fs.writeFileSync(path.join(out,'receipt.json'),JSON.stringify({summary:r.summary,rows:r.rows},null,2)+'\n');console.log(JSON.stringify(r.summary,null,2));
}

/* V8 execution receipt: two identical full runs; connector-reported pinned blob IDs verified; SHA256 shim checked with abc. Native Node CLI not executed. Clean-reference control receives original PCM, not an inverse oracle. No tuning or population inference.
{
  "ref": "a62f4d485998dca3d64baa9ed8a87fda982f7aea",
  "blobs": {
    "relay.cjs": "3ba457f85f496e4d57d9789a2dc3b7d68fe2c071",
    "bound-v2.cjs": "2aa2905d4f4d756276814d5ca941c02c51e63f97",
    "clock-v3.cjs": "1f629ae5dc1a995326ff47cba1a6338f16c080df"
  },
  "seeds": [
    13217,
    28793
  ],
  "streams": 48,
  "assertions": 280,
  "metrics": [
    {
      "name": "clean",
      "removedSamples": 0,
      "scale": 1,
      "noisePeak": 0,
      "decoyGap": 0,
      "fixed": {
        "correct": 4,
        "wrong": 0,
        "refused": 0
      },
      "clock": {
        "correct": 4,
        "wrong": 0,
        "refused": 0
      },
      "statuses": {
        "ok": 4
      },
      "oracle": {
        "correct": 4,
        "wrong": 0,
        "refused": 0
      }
    },
    {
      "name": "one-cut",
      "removedSamples": 240,
      "scale": 1,
      "noisePeak": 0,
      "decoyGap": 0,
      "fixed": {
        "correct": 4,
        "wrong": 0,
        "refused": 0
      },
      "clock": {
        "correct": 4,
        "wrong": 0,
        "refused": 0
      },
      "statuses": {
        "ok": 4
      },
      "oracle": {
        "correct": 4,
        "wrong": 0,
        "refused": 0
      }
    },
    {
      "name": "two-cuts",
      "removedSamples": 480,
      "scale": 1,
      "noisePeak": 0,
      "decoyGap": 0,
      "fixed": {
        "correct": 0,
        "wrong": 0,
        "refused": 4
      },
      "clock": {
        "correct": 0,
        "wrong": 0,
        "refused": 4
      },
      "statuses": {
        "refused": 4
      },
      "oracle": {
        "correct": 4,
        "wrong": 0,
        "refused": 0
      }
    },
    {
      "name": "three-cuts",
      "removedSamples": 720,
      "scale": 1,
      "noisePeak": 0,
      "decoyGap": 0,
      "fixed": {
        "correct": 0,
        "wrong": 0,
        "refused": 4
      },
      "clock": {
        "correct": 0,
        "wrong": 0,
        "refused": 4
      },
      "statuses": {
        "refused": 4
      },
      "oracle": {
        "correct": 4,
        "wrong": 0,
        "refused": 0
      }
    },
    {
      "name": "distributed-cuts",
      "removedSamples": 720,
      "scale": 1,
      "noisePeak": 0,
      "decoyGap": 0,
      "fixed": {
        "correct": 0,
        "wrong": 0,
        "refused": 4
      },
      "clock": {
        "correct": 0,
        "wrong": 0,
        "refused": 4
      },
      "statuses": {
        "refused": 4
      },
      "oracle": {
        "correct": 4,
        "wrong": 0,
        "refused": 0
      }
    },
    {
      "name": "scale-plus",
      "removedSamples": 0,
      "scale": 1.009,
      "noisePeak": 0,
      "decoyGap": 0,
      "fixed": {
        "correct": 0,
        "wrong": 0,
        "refused": 4
      },
      "clock": {
        "correct": 4,
        "wrong": 0,
        "refused": 0
      },
      "statuses": {
        "ok": 4
      },
      "oracle": {
        "correct": 4,
        "wrong": 0,
        "refused": 0
      }
    },
    {
      "name": "scale-minus",
      "removedSamples": 0,
      "scale": 0.991,
      "noisePeak": 0,
      "decoyGap": 0,
      "fixed": {
        "correct": 0,
        "wrong": 0,
        "refused": 4
      },
      "clock": {
        "correct": 4,
        "wrong": 0,
        "refused": 0
      },
      "statuses": {
        "ok": 4
      },
      "oracle": {
        "correct": 4,
        "wrong": 0,
        "refused": 0
      }
    },
    {
      "name": "mixed-plus",
      "removedSamples": 480,
      "scale": 1.009,
      "noisePeak": 800,
      "decoyGap": 0,
      "fixed": {
        "correct": 0,
        "wrong": 0,
        "refused": 4
      },
      "clock": {
        "correct": 0,
        "wrong": 0,
        "refused": 4
      },
      "statuses": {
        "refused": 4
      },
      "oracle": {
        "correct": 4,
        "wrong": 0,
        "refused": 0
      }
    },
    {
      "name": "mixed-minus",
      "removedSamples": 480,
      "scale": 0.991,
      "noisePeak": 800,
      "decoyGap": 0,
      "fixed": {
        "correct": 0,
        "wrong": 0,
        "refused": 4
      },
      "clock": {
        "correct": 0,
        "wrong": 0,
        "refused": 4
      },
      "statuses": {
        "refused": 4
      },
      "oracle": {
        "correct": 4,
        "wrong": 0,
        "refused": 0
      }
    },
    {
      "name": "noise",
      "removedSamples": 0,
      "scale": 1,
      "noisePeak": 1600,
      "decoyGap": 0,
      "fixed": {
        "correct": 4,
        "wrong": 0,
        "refused": 0
      },
      "clock": {
        "correct": 4,
        "wrong": 0,
        "refused": 0
      },
      "statuses": {
        "ok": 4
      },
      "oracle": {
        "correct": 4,
        "wrong": 0,
        "refused": 0
      }
    },
    {
      "name": "isolated-preamble",
      "removedSamples": 0,
      "scale": 1,
      "noisePeak": 0,
      "decoyGap": 640,
      "fixed": {
        "correct": 4,
        "wrong": 0,
        "refused": 0
      },
      "clock": {
        "correct": 0,
        "wrong": 0,
        "refused": 4
      },
      "statuses": {
        "ambiguous": 4
      },
      "oracle": {
        "correct": 4,
        "wrong": 0,
        "refused": 0
      }
    },
    {
      "name": "isolated-preamble-noise",
      "removedSamples": 0,
      "scale": 1,
      "noisePeak": 800,
      "decoyGap": 640,
      "fixed": {
        "correct": 4,
        "wrong": 0,
        "refused": 0
      },
      "clock": {
        "correct": 0,
        "wrong": 0,
        "refused": 4
      },
      "statuses": {
        "ambiguous": 4
      },
      "oracle": {
        "correct": 4,
        "wrong": 0,
        "refused": 0
      }
    }
  ]
}
*/
