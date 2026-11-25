'use strict';
// Adversarial Observatory, Refs #448 #449 #512. Synthetic, exploratory, 2026-11-25.
// Independent comparison; no changes to Integration. v10 is a draft source, not accepted main.
const REF="0fd93d1fab2b4fd177940511c09b0683fd8d9772", PINS={"relay.cjs":"3ba457f85f496e4d57d9789a2dc3b7d68fe2c071","bound-v2.cjs":"2aa2905d4f4d756276814d5ca941c02c51e63f97","stream-v4.cjs":"31769f808469b4416412be25a41eb238bfc1fdde","admission-v10.cjs":"835877805b8a73fc29016487ba7096db96abee1a"};
const SEEDS=[42737,91583], Z=n=>new Int16Array(n), eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b),mod=x=>(x%17+17)%17;
const cfg=Array.from({length:13},(_,k)=>{const s=1+(k-6)*.0025;return {s,n:Math.round(320*s),body:Array.from({length:17},(_,i)=>2*Math.cos(2*Math.PI*(400+100*i)/(16000*s)))};});
// Exact existence of a legal metadata codeword for eight observed symbols, with <=2 erasures.
// No speculative inference from incomplete windows.
function viable(w){
 if(w.length!==8)throw Error('metadata width');
 const missing=w.flatMap((x,i)=>x===null?[i]:[]);
 if(missing.length>2)return false;
 for(let a=0;a<(missing.length?17:1);a++)for(let b=0;b<(missing.length===2?17:1);b++){
  const x=w.slice();if(missing.length)x[missing[0]]=a;if(missing.length===2)x[missing[1]]=b;
  if(x[0]>1||x.slice(1,6).some(v=>v<1))continue;
  if(mod(x.reduce((s,v)=>s+v,0))===0&&mod(x.reduce((s,v,i)=>s+v*(i+1),0))===0)return true;
 }
 return false;
}
function makeParity(Stream){
 return class ParityStream extends Stream{
  constructor(emit){super(emit);Object.assign(this.stats,{prefixSymbols:0,prefixHypothesesRejected:0,prefixCandidatesRejected:0,parityRejected:0});}
  drain(eof){
   if(this.overflow)return;
   for(let i=0;i<this.pending.length;){
    const c=this.pending[i];if(c.done){i++;continue;}
    if(!c.prefix)c.prefix=c.best.filter(Boolean).map(h=>({h,words:[],erasures:0,rejected:null}));
    for(const p of c.prefix){if(p.rejected)continue;const {s,n,body}=cfg[p.h.k];
     while(p.words.length<8){const j=p.words.length,at=Math.round(p.h.start+(640+j*1280+320)*s);
      if(at+n>this.total||at<Math.max(0,this.total-38400))break;
      let a=0,b=0,v=-1;for(let k=0;k<17;k++){const q=this.score(at,n,body[k]);if(q>a){b=a;a=q;v=k;}else if(q>b)b=q;}
      const w=a>=.85&&a-b>=.2?v:null;p.words.push(w);this.stats.prefixSymbols++;
      if(w===null)p.erasures++;
      if(p.erasures>2)p.rejected='erasure-budget';
      else if(w!==null&&j<6&&(j===0?w>1:w<1))p.rejected='domain';
      else if(p.words.length===8&&!viable(p.words)){p.rejected='parity-or-repaired-domain';this.stats.parityRejected++;}
      if(p.rejected){this.stats.prefixHypothesesRejected++;break;}
     }
    }
    if(c.prefix.every(p=>p.rejected)){this.pending.splice(i,1);this.stats.prefixCandidatesRejected++;this.emit({status:'prefix-refused',reason:'no-viable-metadata',first:c.first,last:c.last,at:this.total,evidence:c.prefix.map(p=>({...p.h,words:p.words,reason:p.rejected}))});}
    else i++;
   }
   super.drain(eof);
  }
 };
}
function run(v1,v2,Stream,AdmissionStream,hash){
 let checks=0;const check=(v,m)=>{checks++;if(!v)throw Error(m);};
 const Parity=makeParity(Stream),rows=[],specimens={};
 // All erasure patterns up to two for 16 distinct legal metadata values, plus corrupted controls.
 for(let seq=1;seq<=16;seq++){const w=v1.frame({...v1.base,seq}).slice(0,8);
  check(viable(w),'clean codeword');
  for(let i=0;i<8;i++){const x=w.slice();x[i]=null;check(viable(x),'single erasure');for(let j=i+1;j<8;j++){const y=x.slice();y[j]=null;check(viable(y),'double erasure');}}
  const bad=w.slice();bad[7]=(bad[7]+1)%17;check(!viable(bad),'bad parity');
 }
 function decode(p,C,chunk){const events=[],s=new C(e=>events.push(e));for(let i=0;i<p.length;i+=chunk)s.push(p.subarray(i,i+chunk));
  // Common causal observation horizon; no EOF promotion.
  return {events,stats:s.stats,overload:s.overflow};
 }
 const policies=[['sticky',Stream],['v10',AdmissionStream],['parity',Parity]];
 for(const seed of SEEDS){
  const A={...v1.base,seq:1+seed%16},a=v2.render(A,seed/997),B={...A,seq:1+(seed+1)%16,tree:['question',['open']]},b=v2.render(B,seed/991),tail=Z(2400);
  const filled=(spacing,f)=>{const p=new Int16Array(spacing*28);for(let i=0;i<p.length;i++)p[i]=Math.round(4096*Math.sin(2*Math.PI*f*i/16000+seed/997));for(let j=0;j<28;j++)p.set(a.slice(0,640),j*spacing);return p;};
  const plain=v1.join(...Array.from({length:28},()=>v1.join(a.slice(0,640),Z(640))));
  const er=a.slice();for(const j of [0,1])er.fill(0,640+j*1280,640+(j+1)*1280);
  const bad=v1.join(v1.render(A,seed/997,w=>{w[7]=(w[7]+1)%17;return w;}),a.slice(21120));
  const scenarios=[['clean',v1.join(a,tail),[A]],['two-erased',v1.join(er,tail),[A]],['bad-parity',v1.join(bad,tail),[]],['plain-80',v1.join(plain,Z(24000),b,tail),[B]],...[[1280,500],[1920,500],[2560,500],[1920,600]].map(([sp,f])=>['filled-'+sp+'-'+f,v1.join(filled(sp,f),Z(24000),b,tail),[B]])];
  for(const [name,pcm,expected] of scenarios){const id=seed+'-'+name,sha256=hash(v1.wav(pcm));if(seed===SEEDS[0])specimens[id]=pcm;
   const baseline=decode(pcm,Stream,511);
   const oks=d=>d.events.filter(e=>e.status==='ok').map(e=>e.packet);
   for(const [policy,C] of policies){const d=policy==='sticky'?baseline:decode(pcm,C,511),ok=oks(d);
    check(d.events.every((e,i)=>e.at<=pcm.length&&(!i||e.at>=d.events[i-1].at)),'causality');
    check(d.stats.maxPending<=8,'pending cap');
    check(ok.every(p=>expected.some(q=>eq(p,q))),'unexpected identity');
    if(!baseline.overload)check(eq(ok,oks(baseline)),'nonoverflow parity with baseline');
    if(policy==='parity')check(eq(d,decode(pcm,C,127)),'chunk partition');
    rows.push({id,seed,name,sha256,samples:pcm.length,policy,exact:eq(ok,expected),accepted:ok.length,...d});
   }
  }
 }
 const summary=policies.map(([policy])=>({policy,byCondition:Object.fromEntries([...new Set(rows.map(x=>x.name))].map(name=>{const r=rows.filter(x=>x.policy===policy&&x.name===name);return [name,{exact:r.filter(x=>x.exact).length,overloads:r.filter(x=>x.overload).length,parityRejected:r.reduce((s,x)=>s+(x.stats.parityRejected||0),0)}];})),prefixSymbols:rows.filter(x=>x.policy===policy).reduce((s,x)=>s+(x.stats.prefixSymbols||0),0)}));
 return {checks,summary,rows,specimens};
}
module.exports={run,viable,makeParity};
if(require.main===module){
 const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),dir=path.resolve(process.argv[2]||'.'),out=path.resolve(process.argv[3]||'parity-admission-output');
 for(const [f,sha] of Object.entries(PINS)){const b=fs.readFileSync(path.join(dir,f));if(crypto.createHash('sha1').update('blob '+b.length+'\0').update(b).digest('hex')!==sha)throw Error('wrong blob '+f);}
 const v1=require(path.join(dir,'relay.cjs')),v2=require(path.join(dir,'bound-v2.cjs')),{Stream}=require(path.join(dir,'stream-v4.cjs')),{AdmissionStream}=require(path.join(dir,'admission-v10.cjs')),hash=b=>crypto.createHash('sha256').update(b).digest('hex');
 const {specimens,...receipt}=run(v1,v2,Stream,AdmissionStream,hash);fs.mkdirSync(out,{recursive:true});
 const stimuli=Object.entries(specimens).map(([id,p])=>{const b=v1.wav(p);fs.writeFileSync(path.join(out,id+'.wav'),b);return {id,samples:p.length,sha256:hash(b),peak:p.reduce((m,v)=>Math.max(m,Math.abs(v)),0)};});
 fs.writeFileSync(path.join(out,'receipt.json'),JSON.stringify({ref:REF,pins:PINS,seeds:SEEDS,...receipt,stimuli},null,2)+'\n');console.log(JSON.stringify({checks:receipt.checks,summary:receipt.summary,stimuli},null,2));
}

/* V8 executed receipt; native CLI not executed. SHA256 empty/abc controls passed.
{
  "checks": 786,
  "summary": [
    {
      "policy": "sticky",
      "byCondition": {
        "clean": {
          "exact": 2,
          "overloads": 0,
          "parityRejected": 0
        },
        "two-erased": {
          "exact": 2,
          "overloads": 0,
          "parityRejected": 0
        },
        "bad-parity": {
          "exact": 2,
          "overloads": 0,
          "parityRejected": 0
        },
        "plain-80": {
          "exact": 0,
          "overloads": 2,
          "parityRejected": 0
        },
        "filled-1280-500": {
          "exact": 0,
          "overloads": 2,
          "parityRejected": 0
        },
        "filled-1920-500": {
          "exact": 0,
          "overloads": 2,
          "parityRejected": 0
        },
        "filled-2560-500": {
          "exact": 0,
          "overloads": 2,
          "parityRejected": 0
        },
        "filled-1920-600": {
          "exact": 0,
          "overloads": 2,
          "parityRejected": 0
        }
      },
      "prefixSymbols": 0
    },
    {
      "policy": "v10",
      "byCondition": {
        "clean": {
          "exact": 2,
          "overloads": 0,
          "parityRejected": 0
        },
        "two-erased": {
          "exact": 2,
          "overloads": 0,
          "parityRejected": 0
        },
        "bad-parity": {
          "exact": 2,
          "overloads": 0,
          "parityRejected": 0
        },
        "plain-80": {
          "exact": 2,
          "overloads": 0,
          "parityRejected": 0
        },
        "filled-1280-500": {
          "exact": 0,
          "overloads": 2,
          "parityRejected": 0
        },
        "filled-1920-500": {
          "exact": 0,
          "overloads": 2,
          "parityRejected": 0
        },
        "filled-2560-500": {
          "exact": 0,
          "overloads": 2,
          "parityRejected": 0
        },
        "filled-1920-600": {
          "exact": 2,
          "overloads": 0,
          "parityRejected": 0
        }
      },
      "prefixSymbols": 2570
    },
    {
      "policy": "parity",
      "byCondition": {
        "clean": {
          "exact": 2,
          "overloads": 0,
          "parityRejected": 0
        },
        "two-erased": {
          "exact": 2,
          "overloads": 0,
          "parityRejected": 0
        },
        "bad-parity": {
          "exact": 2,
          "overloads": 0,
          "parityRejected": 10
        },
        "plain-80": {
          "exact": 2,
          "overloads": 0,
          "parityRejected": 0
        },
        "filled-1280-500": {
          "exact": 2,
          "overloads": 0,
          "parityRejected": 176
        },
        "filled-1920-500": {
          "exact": 2,
          "overloads": 0,
          "parityRejected": 0
        },
        "filled-2560-500": {
          "exact": 0,
          "overloads": 2,
          "parityRejected": 40
        },
        "filled-1920-600": {
          "exact": 2,
          "overloads": 0,
          "parityRejected": 0
        }
      },
      "prefixSymbols": 6384
    }
  ],
  "stimuli": [
    {
      "id": "42737-clean",
      "samples": 33760,
      "sha256": "5dea8f2071cdbe6261c27a1da7cab167fcdd1235278ab507e3239ceba1dc8824",
      "peak": 4095
    },
    {
      "id": "42737-two-erased",
      "samples": 33760,
      "sha256": "215abb5593b1ebdf1320c7447b387e68f3c561df2f2c7978cd7ea2bd793e86f5",
      "peak": 4095
    },
    {
      "id": "42737-bad-parity",
      "samples": 33760,
      "sha256": "03abe9c6fb409420db9f2ac8398258619aa7b63addd6630c54c5516cc5626517",
      "peak": 4095
    },
    {
      "id": "42737-plain-80",
      "samples": 93600,
      "sha256": "3059778638f943f6fa93b003788fe24ce3152a6569e641ae53b27a39d44888e2",
      "peak": 4096
    },
    {
      "id": "42737-filled-1280-500",
      "samples": 93600,
      "sha256": "600935f563947c7ff543d338d39b4fdcd60e37c9b95c7b3ba3f9e238355be71e",
      "peak": 4096
    },
    {
      "id": "42737-filled-1920-500",
      "samples": 111520,
      "sha256": "9da4214ad7016c3e0be8ba4533b717dd86bd1248c8fc555b5b0903fe2ea64425",
      "peak": 4096
    },
    {
      "id": "42737-filled-2560-500",
      "samples": 129440,
      "sha256": "68dc5c4512da5178136d6b907024b3d103354ac0b2c852231a84f85074ffda78",
      "peak": 4096
    },
    {
      "id": "42737-filled-1920-600",
      "samples": 111520,
      "sha256": "ac0e95327f6bf617c0743931caf957dd633b4c1b15d0a1dae3fe62620dd27b5e",
      "peak": 4096
    }
  ],
  "witnesses": [
    {
      "name": "filled-1280-500",
      "policy": "sticky",
      "exact": false,
      "overflow": 11258,
      "accepted": 0,
      "stats": {
        "scans": 664,
        "hypotheses": 0,
        "clusters": 9,
        "maxPending": 8,
        "pcmBytes": 153600
      }
    },
    {
      "name": "filled-1280-500",
      "policy": "v10",
      "exact": false,
      "overflow": 11258,
      "accepted": 0,
      "stats": {
        "scans": 664,
        "hypotheses": 0,
        "clusters": 9,
        "maxPending": 8,
        "pcmBytes": 153600,
        "prefixSymbols": 165,
        "prefixHypothesesRejected": 0,
        "prefixCandidatesRejected": 0
      }
    },
    {
      "name": "filled-1280-500",
      "policy": "parity",
      "exact": true,
      "overflow": null,
      "accepted": 1,
      "stats": {
        "scans": 5810,
        "hypotheses": 15,
        "clusters": 29,
        "maxPending": 8,
        "pcmBytes": 153600,
        "prefixSymbols": 1110,
        "prefixHypothesesRejected": 134,
        "prefixCandidatesRejected": 26,
        "parityRejected": 88
      }
    },
    {
      "name": "filled-1920-500",
      "policy": "sticky",
      "exact": false,
      "overflow": 16378,
      "accepted": 0,
      "stats": {
        "scans": 984,
        "hypotheses": 0,
        "clusters": 9,
        "maxPending": 8,
        "pcmBytes": 153600
      }
    },
    {
      "name": "filled-1920-500",
      "policy": "v10",
      "exact": false,
      "overflow": 16378,
      "accepted": 0,
      "stats": {
        "scans": 984,
        "hypotheses": 0,
        "clusters": 9,
        "maxPending": 8,
        "pcmBytes": 153600,
        "prefixSymbols": 200,
        "prefixHypothesesRejected": 5,
        "prefixCandidatesRejected": 0
      }
    },
    {
      "name": "filled-1920-500",
      "policy": "parity",
      "exact": true,
      "overflow": null,
      "accepted": 1,
      "stats": {
        "scans": 6930,
        "hypotheses": 5,
        "clusters": 29,
        "maxPending": 5,
        "pcmBytes": 153600,
        "prefixSymbols": 1062,
        "prefixHypothesesRejected": 140,
        "prefixCandidatesRejected": 28,
        "parityRejected": 0
      }
    },
    {
      "name": "filled-2560-500",
      "policy": "sticky",
      "exact": false,
      "overflow": 21498,
      "accepted": 0,
      "stats": {
        "scans": 1304,
        "hypotheses": 0,
        "clusters": 9,
        "maxPending": 8,
        "pcmBytes": 153600
      }
    },
    {
      "name": "filled-2560-500",
      "policy": "v10",
      "exact": false,
      "overflow": 21498,
      "accepted": 0,
      "stats": {
        "scans": 1304,
        "hypotheses": 0,
        "clusters": 9,
        "maxPending": 8,
        "pcmBytes": 153600,
        "prefixSymbols": 210,
        "prefixHypothesesRejected": 0,
        "prefixCandidatesRejected": 0
      }
    },
    {
      "name": "filled-2560-500",
      "policy": "parity",
      "exact": false,
      "overflow": 21498,
      "accepted": 0,
      "stats": {
        "scans": 1304,
        "hypotheses": 0,
        "clusters": 9,
        "maxPending": 8,
        "pcmBytes": 153600,
        "prefixSymbols": 260,
        "prefixHypothesesRejected": 20,
        "prefixCandidatesRejected": 0,
        "parityRejected": 20
      }
    },
    {
      "name": "filled-1920-600",
      "policy": "sticky",
      "exact": false,
      "overflow": 16378,
      "accepted": 0,
      "stats": {
        "scans": 984,
        "hypotheses": 0,
        "clusters": 9,
        "maxPending": 8,
        "pcmBytes": 153600
      }
    },
    {
      "name": "filled-1920-600",
      "policy": "v10",
      "exact": true,
      "overflow": null,
      "accepted": 1,
      "stats": {
        "scans": 6930,
        "hypotheses": 5,
        "clusters": 29,
        "maxPending": 1,
        "pcmBytes": 153600,
        "prefixSymbols": 170,
        "prefixHypothesesRejected": 140,
        "prefixCandidatesRejected": 28
      }
    },
    {
      "name": "filled-1920-600",
      "policy": "parity",
      "exact": true,
      "overflow": null,
      "accepted": 1,
      "stats": {
        "scans": 6930,
        "hypotheses": 5,
        "clusters": 29,
        "maxPending": 1,
        "pcmBytes": 153600,
        "prefixSymbols": 180,
        "prefixHypothesesRejected": 140,
        "prefixCandidatesRejected": 28,
        "parityRejected": 0
      }
    }
  ]
}
*/
