'use strict';
// MHAC Adversarial Observatory, #448 / #449, Run 008, 2026-11-25.
// Independent synthetic timing audit of Integration #513 at 4d2d0b2c067924305675e92eabd2b9cc28676842.
// No source vendoring. Supply the exact pinned upstream files in a separate directory.
// Same v2 PCM for prefix and strict receiver comparisons; not matched standalone frame lengths.
// Ground-truth inverse is a diagnostic oracle, not a deployable receiver.
// No human evidence, device interaction, authentication or canonical evidence claim.
const UPSTREAM='4d2d0b2c067924305675e92eabd2b9cc28676842';
const BLOBS={'relay.cjs':'3ba457f85f496e4d57d9789a2dc3b7d68fe2c071','bound-v2.cjs':'2aa2905d4f4d756276814d5ca941c02c51e63f97'};
const RATE=16000,FRAME=31360,V1=21120,SLOT=1280,HEADER=640;
const EQ=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const zeros=n=>new Int16Array(n);
function linear(x,n,scale){return Int16Array.from({length:n},(_,i)=>{const t=i*scale,k=Math.floor(t),a=t-k;return Math.round((x[k]||0)*(1-a)+(x[k+1]||0)*a);});}
function audit(v1,v2,hash){
 let assertions=0;const check=(b,m)=>{assertions++;if(!b)throw Error(m);};
 const seeds=[937,2017,4099,8111],conditions=[0,-.001,.001,-.0025,.0025,-.005,.005,-.01,.01].map(s=>({name:'scale '+s,scale:1+s,slip:0}));
 for(const slip of [-80,80,-160,160,-240,240])conditions.push({name:'tag guard '+slip,scale:1,slip});
 // The first tag tone is active for 960 samples, then exactly 320 silent samples.
 // Modify only that silent interval, so no nonzero transmitted sample is removed.
 const pivot=V1+SLOT;
 const metrics=conditions.map(c=>({condition:c.name,scale:c.scale,slipSamples:c.slip,trials:0,prefix:{correct:0,wrong:0,refused:0},strict:{correct:0,wrong:0,refused:0},oracle:{correct:0,wrong:0,refused:0},prefixCorrectStrictRefused:0,strictNoHeader:0,strictBodyRefused:0,strictBindingRefused:0,strictTruncated:0}));
 const rows=[],specimens={};let peak=0;
 function decide(h,p){const q=h.filter(x=>x.status==='ok').map(x=>x.packet);return q.length===0?'refused':q.length===1&&EQ(q[0],p)?'correct':'wrong';}
 function inspect(pcm,p){return {prefix:v1.acquire(pcm),strict:v2.acquire(pcm)};}
 const choose=new Set(['scale 0','scale 0.005','scale -0.005','tag guard -240','tag guard 240']);
 for(const [ci,c] of conditions.entries())for(const kind of [0,1])for(const seed of seeds){
  const packet={...v1.base,kind},phase=((seed*16807)%2147483647)/2147483647*2*Math.PI,offset=160+(seed%480),tail=640;
  const original=v2.render(packet,phase);check(original.length===FRAME,'frame length');check(original.slice(pivot-320,pivot).every(x=>x===0),'guard silence');
  let warped=original,restored;
  if(c.slip>0){warped=v1.join(original.slice(0,pivot),zeros(c.slip),original.slice(pivot));restored=v1.join(warped.slice(0,pivot),warped.slice(pivot+c.slip));}
  else if(c.slip<0){warped=v1.join(original.slice(0,pivot+c.slip),original.slice(pivot));restored=v1.join(warped.slice(0,pivot+c.slip),zeros(-c.slip),warped.slice(pivot+c.slip));}
  else if(c.scale!==1){warped=linear(original,Math.round(FRAME*c.scale),1/c.scale);restored=linear(warped,FRAME,c.scale);}
  else restored=original;
  if(c.slip){check(EQ(Array.from(restored),Array.from(original)),'exact silent guard inverse');check(warped.reduce((s,x)=>s+x*x,0)===original.reduce((s,x)=>s+x*x,0),'nonzero energy unchanged');}
  const pcm=v1.join(zeros(offset),warped,zeros(tail)),corrected=v1.join(zeros(offset),restored,zeros(tail));
  const h=inspect(pcm,packet),o=v2.acquire(corrected),a=decide(h.prefix,packet),b=decide(h.strict,packet),d=decide(o,packet);
  const m=metrics[ci];m.trials++;m.prefix[a]++;m.strict[b]++;m.oracle[d]++;
  if(a==='correct'&&b==='refused')m.prefixCorrectStrictRefused++;
  if(b==='refused'){if(!h.strict.length)m.strictNoHeader++;else if(h.strict.some(x=>x.status==='binding-refused'))m.strictBindingRefused++;else if(h.strict.some(x=>x.status.includes('truncated')))m.strictTruncated++;else m.strictBodyRefused++;}
  const p=pcm.reduce((s,x)=>Math.max(s,Math.abs(x)),0);peak=Math.max(peak,p);check(p<=4096,'peak bound');
  if(c.scale===1&&!c.slip)check(a==='correct'&&b==='correct'&&d==='correct','clean control');
  if(c.slip)check(d==='correct','guard oracle recovers');
  const name='c'+ci+'-kind'+kind+'-seed'+seed;
  const row={name,condition:c.name,seed,kind,offset,phase,scale:c.scale,slipSamples:c.slip,samples:pcm.length,peak:p,prefix:a,strict:b,oracle:d,hits:h,oracleHits:o};
  rows.push(row);
  if(kind===0&&seed===seeds[0]&&choose.has(c.name)){specimens[name]=pcm;specimens[name+'-oracle']=corrected;}
 }
 for(const m of metrics){for(const k of ['prefix','strict','oracle'])check(Object.values(m[k]).reduce((s,x)=>s+x,0)===m.trials,'outcome partition');check(m.strictNoHeader+m.strictBodyRefused+m.strictBindingRefused+m.strictTruncated===m.strict.refused,'refusal partition');}
 const stimuli=Object.entries(specimens).map(([name,pcm])=>({file:name+'.wav',samples:pcm.length,sha256:hash(v1.wav(pcm))}));
 const summary={upstream:UPSTREAM,blobs:BLOBS,rate:RATE,frameSamples:FRAME,seeds,assertions,streams:rows.length,peak,metrics,stimuli};
 return {summary,rows,specimens};
}
module.exports={audit};
if(require.main===module){
 const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
 const dir=path.resolve(process.argv[2]||'.'),out=path.resolve(process.argv[3]||'relay-clock-audit-output');
 const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
 for(const [file,sha] of Object.entries(BLOBS)){const b=fs.readFileSync(path.join(dir,file)),got=crypto.createHash('sha1').update('blob '+b.length+'\0').update(b).digest('hex');if(got!==sha)throw Error('wrong pinned upstream blob '+file+' '+got);}
 const v1=require(path.join(dir,'relay.cjs')),v2=require(path.join(dir,'bound-v2.cjs'));
 const result=audit(v1,v2,hash);
 fs.mkdirSync(out,{recursive:true});
 for(const [name,pcm] of Object.entries(result.specimens))fs.writeFileSync(path.join(out,name+'.wav'),v1.wav(pcm));
 fs.writeFileSync(path.join(out,'receipt.json'),JSON.stringify({summary:result.summary,rows:result.rows},null,2)+'\n');
 console.log(JSON.stringify(result.summary,null,2));
}

/* Executed V8 receipt (two matching runs; upstream sources loaded at exact ref; Node crypto shim checked against all four upstream SHA-256 vectors and abc; native CLI pending). AI-assisted, one agent, no independent human review.
{
  "upstream": "4d2d0b2c067924305675e92eabd2b9cc28676842",
  "blobs": {
    "relay.cjs": "3ba457f85f496e4d57d9789a2dc3b7d68fe2c071",
    "bound-v2.cjs": "2aa2905d4f4d756276814d5ca941c02c51e63f97"
  },
  "rate": 16000,
  "frameSamples": 31360,
  "seeds": [
    937,
    2017,
    4099,
    8111
  ],
  "assertions": 572,
  "streams": 120,
  "peak": 4096,
  "metrics": [
    {
      "condition": "scale 0",
      "scale": 1,
      "slipSamples": 0,
      "trials": 8,
      "prefix": {
        "correct": 8,
        "wrong": 0,
        "refused": 0
      },
      "strict": {
        "correct": 8,
        "wrong": 0,
        "refused": 0
      },
      "oracle": {
        "correct": 8,
        "wrong": 0,
        "refused": 0
      },
      "prefixCorrectStrictRefused": 0,
      "strictNoHeader": 0,
      "strictBodyRefused": 0,
      "strictBindingRefused": 0,
      "strictTruncated": 0
    },
    {
      "condition": "scale -0.001",
      "scale": 0.999,
      "slipSamples": 0,
      "trials": 8,
      "prefix": {
        "correct": 8,
        "wrong": 0,
        "refused": 0
      },
      "strict": {
        "correct": 8,
        "wrong": 0,
        "refused": 0
      },
      "oracle": {
        "correct": 8,
        "wrong": 0,
        "refused": 0
      },
      "prefixCorrectStrictRefused": 0,
      "strictNoHeader": 0,
      "strictBodyRefused": 0,
      "strictBindingRefused": 0,
      "strictTruncated": 0
    },
    {
      "condition": "scale 0.001",
      "scale": 1.001,
      "slipSamples": 0,
      "trials": 8,
      "prefix": {
        "correct": 8,
        "wrong": 0,
        "refused": 0
      },
      "strict": {
        "correct": 8,
        "wrong": 0,
        "refused": 0
      },
      "oracle": {
        "correct": 8,
        "wrong": 0,
        "refused": 0
      },
      "prefixCorrectStrictRefused": 0,
      "strictNoHeader": 0,
      "strictBodyRefused": 0,
      "strictBindingRefused": 0,
      "strictTruncated": 0
    },
    {
      "condition": "scale -0.0025",
      "scale": 0.9975,
      "slipSamples": 0,
      "trials": 8,
      "prefix": {
        "correct": 8,
        "wrong": 0,
        "refused": 0
      },
      "strict": {
        "correct": 8,
        "wrong": 0,
        "refused": 0
      },
      "oracle": {
        "correct": 8,
        "wrong": 0,
        "refused": 0
      },
      "prefixCorrectStrictRefused": 0,
      "strictNoHeader": 0,
      "strictBodyRefused": 0,
      "strictBindingRefused": 0,
      "strictTruncated": 0
    },
    {
      "condition": "scale 0.0025",
      "scale": 1.0025,
      "slipSamples": 0,
      "trials": 8,
      "prefix": {
        "correct": 8,
        "wrong": 0,
        "refused": 0
      },
      "strict": {
        "correct": 8,
        "wrong": 0,
        "refused": 0
      },
      "oracle": {
        "correct": 8,
        "wrong": 0,
        "refused": 0
      },
      "prefixCorrectStrictRefused": 0,
      "strictNoHeader": 0,
      "strictBodyRefused": 0,
      "strictBindingRefused": 0,
      "strictTruncated": 0
    },
    {
      "condition": "scale -0.005",
      "scale": 0.995,
      "slipSamples": 0,
      "trials": 8,
      "prefix": {
        "correct": 0,
        "wrong": 0,
        "refused": 8
      },
      "strict": {
        "correct": 0,
        "wrong": 0,
        "refused": 8
      },
      "oracle": {
        "correct": 8,
        "wrong": 0,
        "refused": 0
      },
      "prefixCorrectStrictRefused": 0,
      "strictNoHeader": 0,
      "strictBodyRefused": 8,
      "strictBindingRefused": 0,
      "strictTruncated": 0
    },
    {
      "condition": "scale 0.005",
      "scale": 1.005,
      "slipSamples": 0,
      "trials": 8,
      "prefix": {
        "correct": 0,
        "wrong": 0,
        "refused": 8
      },
      "strict": {
        "correct": 0,
        "wrong": 0,
        "refused": 8
      },
      "oracle": {
        "correct": 8,
        "wrong": 0,
        "refused": 0
      },
      "prefixCorrectStrictRefused": 0,
      "strictNoHeader": 0,
      "strictBodyRefused": 8,
      "strictBindingRefused": 0,
      "strictTruncated": 0
    },
    {
      "condition": "scale -0.01",
      "scale": 0.99,
      "slipSamples": 0,
      "trials": 8,
      "prefix": {
        "correct": 0,
        "wrong": 0,
        "refused": 8
      },
      "strict": {
        "correct": 0,
        "wrong": 0,
        "refused": 8
      },
      "oracle": {
        "correct": 8,
        "wrong": 0,
        "refused": 0
      },
      "prefixCorrectStrictRefused": 0,
      "strictNoHeader": 8,
      "strictBodyRefused": 0,
      "strictBindingRefused": 0,
      "strictTruncated": 0
    },
    {
      "condition": "scale 0.01",
      "scale": 1.01,
      "slipSamples": 0,
      "trials": 8,
      "prefix": {
        "correct": 0,
        "wrong": 0,
        "refused": 8
      },
      "strict": {
        "correct": 0,
        "wrong": 0,
        "refused": 8
      },
      "oracle": {
        "correct": 8,
        "wrong": 0,
        "refused": 0
      },
      "prefixCorrectStrictRefused": 0,
      "strictNoHeader": 8,
      "strictBodyRefused": 0,
      "strictBindingRefused": 0,
      "strictTruncated": 0
    },
    {
      "condition": "tag guard -80",
      "scale": 1,
      "slipSamples": -80,
      "trials": 8,
      "prefix": {
        "correct": 8,
        "wrong": 0,
        "refused": 0
      },
      "strict": {
        "correct": 8,
        "wrong": 0,
        "refused": 0
      },
      "oracle": {
        "correct": 8,
        "wrong": 0,
        "refused": 0
      },
      "prefixCorrectStrictRefused": 0,
      "strictNoHeader": 0,
      "strictBodyRefused": 0,
      "strictBindingRefused": 0,
      "strictTruncated": 0
    },
    {
      "condition": "tag guard 80",
      "scale": 1,
      "slipSamples": 80,
      "trials": 8,
      "prefix": {
        "correct": 8,
        "wrong": 0,
        "refused": 0
      },
      "strict": {
        "correct": 8,
        "wrong": 0,
        "refused": 0
      },
      "oracle": {
        "correct": 8,
        "wrong": 0,
        "refused": 0
      },
      "prefixCorrectStrictRefused": 0,
      "strictNoHeader": 0,
      "strictBodyRefused": 0,
      "strictBindingRefused": 0,
      "strictTruncated": 0
    },
    {
      "condition": "tag guard -160",
      "scale": 1,
      "slipSamples": -160,
      "trials": 8,
      "prefix": {
        "correct": 8,
        "wrong": 0,
        "refused": 0
      },
      "strict": {
        "correct": 8,
        "wrong": 0,
        "refused": 0
      },
      "oracle": {
        "correct": 8,
        "wrong": 0,
        "refused": 0
      },
      "prefixCorrectStrictRefused": 0,
      "strictNoHeader": 0,
      "strictBodyRefused": 0,
      "strictBindingRefused": 0,
      "strictTruncated": 0
    },
    {
      "condition": "tag guard 160",
      "scale": 1,
      "slipSamples": 160,
      "trials": 8,
      "prefix": {
        "correct": 8,
        "wrong": 0,
        "refused": 0
      },
      "strict": {
        "correct": 8,
        "wrong": 0,
        "refused": 0
      },
      "oracle": {
        "correct": 8,
        "wrong": 0,
        "refused": 0
      },
      "prefixCorrectStrictRefused": 0,
      "strictNoHeader": 0,
      "strictBodyRefused": 0,
      "strictBindingRefused": 0,
      "strictTruncated": 0
    },
    {
      "condition": "tag guard -240",
      "scale": 1,
      "slipSamples": -240,
      "trials": 8,
      "prefix": {
        "correct": 8,
        "wrong": 0,
        "refused": 0
      },
      "strict": {
        "correct": 6,
        "wrong": 0,
        "refused": 2
      },
      "oracle": {
        "correct": 8,
        "wrong": 0,
        "refused": 0
      },
      "prefixCorrectStrictRefused": 2,
      "strictNoHeader": 0,
      "strictBodyRefused": 0,
      "strictBindingRefused": 2,
      "strictTruncated": 0
    },
    {
      "condition": "tag guard 240",
      "scale": 1,
      "slipSamples": 240,
      "trials": 8,
      "prefix": {
        "correct": 8,
        "wrong": 0,
        "refused": 0
      },
      "strict": {
        "correct": 8,
        "wrong": 0,
        "refused": 0
      },
      "oracle": {
        "correct": 8,
        "wrong": 0,
        "refused": 0
      },
      "prefixCorrectStrictRefused": 0,
      "strictNoHeader": 0,
      "strictBodyRefused": 0,
      "strictBindingRefused": 0,
      "strictTruncated": 0
    }
  ],
  "stimuli": [
    {
      "file": "c0-kind0-seed937.wav",
      "samples": 32617,
      "sha256": "9f504ea1b278b374e0a78b1bf6e19686c26fc53eb478d9d5eda8e26eaaf34687"
    },
    {
      "file": "c0-kind0-seed937-oracle.wav",
      "samples": 32617,
      "sha256": "9f504ea1b278b374e0a78b1bf6e19686c26fc53eb478d9d5eda8e26eaaf34687"
    },
    {
      "file": "c5-kind0-seed937.wav",
      "samples": 32460,
      "sha256": "da25511f97be5ae8629655e64533d57a149cd995dc41959997649821b798a69b"
    },
    {
      "file": "c5-kind0-seed937-oracle.wav",
      "samples": 32617,
      "sha256": "a18eb9e259df6b87669e522ea291247effc169b9e0bf9370472f3cc78e6f80fe"
    },
    {
      "file": "c6-kind0-seed937.wav",
      "samples": 32774,
      "sha256": "68f80195219c503a9e01731db264a9a91c07df2a600faf9fe120dea6de71402c"
    },
    {
      "file": "c6-kind0-seed937-oracle.wav",
      "samples": 32617,
      "sha256": "ca6d54ec279505033e36210b4d5f70fe257bcbdda7fece0e095c5d831fbef340"
    },
    {
      "file": "c13-kind0-seed937.wav",
      "samples": 32377,
      "sha256": "39d9578d6b6d9fe4b019741d7ed1de00d6d10ae7adffa4d452b7eeb031cd4379"
    },
    {
      "file": "c13-kind0-seed937-oracle.wav",
      "samples": 32617,
      "sha256": "9f504ea1b278b374e0a78b1bf6e19686c26fc53eb478d9d5eda8e26eaaf34687"
    },
    {
      "file": "c14-kind0-seed937.wav",
      "samples": 32857,
      "sha256": "7b39a0219e78061da4368290aa189ecf8a129954f00cdd0b37b29cff67c85680"
    },
    {
      "file": "c14-kind0-seed937-oracle.wav",
      "samples": 32617,
      "sha256": "9f504ea1b278b374e0a78b1bf6e19686c26fc53eb478d9d5eda8e26eaaf34687"
    }
  ]
}
*/
