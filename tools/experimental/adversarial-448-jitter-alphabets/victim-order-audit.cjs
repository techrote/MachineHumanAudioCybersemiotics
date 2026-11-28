'use strict';
// Observatory Adversarial, Refs #448 #512. Synthetic only, 2026-11-25.
// Independent victim-order audit of pinned Integration v12; no changes to upstream.
const REF="c26e6e9bfdaf40c6d9cb941cfc36cda1c9da4dce", PINS={"relay.cjs":"3ba457f85f496e4d57d9789a2dc3b7d68fe2c071","bound-v2.cjs":"2aa2905d4f4d756276814d5ca941c02c51e63f97","stream-v4.cjs":"31769f808469b4416412be25a41eb238bfc1fdde","parity-v11.cjs":"4d1ad5ead8f94ce219bc879fe05269bb1ce1f7df","ledger-v12.cjs":"538bf2e28da108bfe9751cab6720e21325c55be1"};
const factory=function(){
 const equal=(a,b)=>JSON.stringify(a)===JSON.stringify(b),overlap=(a,b)=>a[0]<b[1]&&b[0]<a[1],delta=Math.round(31360*1.015);
 function run(v1,v2,LedgerStream,MAX_PENDING){
  let checks=0;const ck=(b,m)=>{checks++;if(!b)throw Error(m);};
  const rows=[],specimens={},seeds=[53813,97331,17093,84179],Z=n=>new Int16Array(n);
  function decode(p,mode,correct,chunk=511){
   const events=[],choices=[];
   class Audit extends LedgerStream {
    closeCluster(){
     if(this.pending.length<MAX_PENDING||!this.cluster)return super.closeCluster();
     const unfinished=this.pending.map((c,i)=>({c,i})).filter(x=>!x.c.done);
     if(mode==='incoming'||!unfinished.length)return super.closeCluster();
     const target=unfinished.reduce((a,b)=>(mode==='oldest'?b.c.first<a.c.first:b.c.first>a.c.first)?b:a);
     const selected=mode==='oldest'?unfinished[0]:unfinished.at(-1);
     const actual=correct?target:selected;
     choices.push({at:this.total,firsts:unfinished.map(x=>x.c.first),intended:target.c.first,actual:actual.c.first,wrong:actual.c.first!==target.c.first});
     if(!correct)return super.closeCluster();
     // Identical v12 eviction/ledger accounting, only the victim selector changes.
     const c=this.cluster;this.cluster=null;this.stats.clusters++;
     const drop=this.pending.splice(actual.i,1,c)[0],a=drop.first,b=drop.last+delta;
     this.ledger.add(a,b);this.stats.evicted++;this.stats.ledgerPeak=this.ledger.peak;this.stats.ledgerMerges=this.ledger.merges;
     this.emit({status:'evicted',reason:this.policy,first:drop.first,last:drop.last,start:null,end:null,lossStart:a,lossEnd:b,ranges:this.ledger.ranges.map(r=>r.slice()),packet:null,at:this.total});
    }
   }
   const s=new Audit(e=>events.push(e),mode,1);
   for(let i=0;i<p.length;i+=chunk)s.push(p.subarray(i,i+chunk));s.finish();
   const lost=[];for(const e of events){ck(e.at<=p.length,'causal');if(e.status==='evicted')lost.push([e.first,e.last+delta]);if(e.status==='ok')ck(!lost.some(r=>overlap(r,[e.start,e.end])),'loss oracle');}
   ck(s.stats.maxPending<=MAX_PENDING,'capacity');ck(s.ledger.peak<=1,'ledger capacity');ck(choices.length<=s.stats.evicted,'choice accounting');
   if(correct)ck(choices.every(c=>!c.wrong),'chronology');return {events,choices,stats:s.stats};
  }
  for(const seed of seeds){
   const A={...v1.base,seq:1+seed%16},B={...A,seq:1+(seed+1)%16,tree:['question',['open']]},C={...A,seq:1+(seed+2)%16,tree:['verify',['fault']]};
   const a=v2.render(A,seed/997),b=v2.render(B,seed/991),c=v2.render(C,seed/983);
   function flood(n,spacing){const p=Z(n*spacing);for(let i=0;i<n;i++){p.set(a.slice(0,640),i*spacing);if(i%4!==3)for(let j=640;j<spacing;j++)p[i*spacing+j]=Math.round(4096*Math.sin(2*Math.PI*500*j/16000+seed/997));}return p;}
   const f=flood(25,1280),g=flood(18,2560),mid=Z(b.length+1280);mid.set(b);mid.set(a.slice(0,640),b.length-160);
   const cases=[['clean',v1.join(b,Z(2400)),[B]],['adjacent',v1.join(f,Z(320),b,Z(2400)),[B]],['gap',v1.join(f,Z(64000),mid,f,Z(64000),c,Z(2400)),[B,C]],['slow-pressure',v1.join(g,Z(320),b,Z(2400)),[B]],['recovery',v1.join(f,Z(64000),b,Z(2400)),[B]]];
   for(const [name,p,expected] of cases){const id=seed+'-'+name;if(seed===seeds[0]||seed===seeds[2])specimens[id]=p;
    for(const mode of ['oldest','reserve'])for(const correct of [false,true]){
     const d=decode(p,mode,correct),ok=d.events.filter(e=>e.status==='ok').map(e=>e.packet);let next=0;for(const x of ok){while(next<expected.length&&!equal(expected[next],x))next++;ck(next<expected.length,'unexpected/repeated packet');next++;}
     if(seed===seeds[0]&&name==='gap')ck(equal(d,decode(p,mode,correct,127)),'chunk partition');
     rows.push({id,seed,split:seed===53813||seed===97331?'prior':'fresh',name,mode,correct,expected,exact:equal(ok,expected),accepted:ok.length,...d});
    }
   }
  }
  const summary=[];for(const split of ['prior','fresh'])for(const mode of ['oldest','reserve'])for(const correct of [false,true]){const a=rows.filter(x=>x.split===split&&x.mode===mode&&x.correct===correct);summary.push({split,mode,correct,exact:a.filter(x=>x.exact).length,trials:a.length,accepted:a.reduce((n,x)=>n+x.accepted,0),evictions:a.reduce((n,x)=>n+x.stats.evicted,0),choices:a.reduce((n,x)=>n+x.choices.length,0),wrong:a.reduce((n,x)=>n+x.choices.filter(c=>c.wrong).length,0),abstentions:a.reduce((n,x)=>n+x.stats.lossAbstentions,0)});}
  const witness=rows.flatMap(r=>r.choices.filter(c=>c.wrong).map(c=>({id:r.id,mode:r.mode,...c}))).slice(0,8);
  return {checks,summary,witness,rows,specimens};
 }
 return {run};
};
module.exports=factory();
if(require.main===module){
 const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),dir=path.resolve(process.argv[2]||'.'),out=path.resolve(process.argv[3]||'victim-order-output');
 for(const [f,sha] of Object.entries(PINS)){const b=fs.readFileSync(path.join(dir,f));if(crypto.createHash('sha1').update('blob '+b.length+'\0').update(b).digest('hex')!==sha)throw Error('wrong blob '+f);}
 const v1=require(path.join(dir,'relay.cjs')),v2=require(path.join(dir,'bound-v2.cjs')),{LedgerStream}=require(path.join(dir,'ledger-v12.cjs')),{MAX_PENDING}=require(path.join(dir,'stream-v4.cjs'));
 const {specimens,...receipt}=module.exports.run(v1,v2,LedgerStream,MAX_PENDING);fs.mkdirSync(out,{recursive:true});
 const stimuli=Object.entries(specimens).map(([id,p])=>{const b=v1.wav(p);fs.writeFileSync(path.join(out,id+'.wav'),b);return {id,samples:p.length,peak:p.reduce((m,x)=>Math.max(m,Math.abs(x)),0),sha256:crypto.createHash('sha256').update(b).digest('hex')};});
 fs.writeFileSync(path.join(out,'receipt.json'),JSON.stringify({ref:REF,pins:PINS,...receipt,stimuli},null,2)+'\n');
 console.log(JSON.stringify({checks:receipt.checks,summary:receipt.summary,witness:receipt.witness,stimuli},null,2));
}
/* Executed V8 receipt; prior seeds are regression, fresh seeds are new but not random population. Native CLI not executed; SHA256 empty/abc known answers. No human evidence.\n{
  "checks": 2628,
  "summary": [
    {
      "split": "prior",
      "mode": "oldest",
      "correct": false,
      "exact": 4,
      "trials": 10,
      "accepted": 6,
      "evictions": 146,
      "choices": 146,
      "wrong": 136,
      "abstentions": 6
    },
    {
      "split": "prior",
      "mode": "oldest",
      "correct": true,
      "exact": 4,
      "trials": 10,
      "accepted": 6,
      "evictions": 152,
      "choices": 152,
      "wrong": 0,
      "abstentions": 6
    },
    {
      "split": "prior",
      "mode": "reserve",
      "correct": false,
      "exact": 6,
      "trials": 10,
      "accepted": 8,
      "evictions": 146,
      "choices": 146,
      "wrong": 0,
      "abstentions": 4
    },
    {
      "split": "prior",
      "mode": "reserve",
      "correct": true,
      "exact": 6,
      "trials": 10,
      "accepted": 8,
      "evictions": 146,
      "choices": 146,
      "wrong": 0,
      "abstentions": 4
    },
    {
      "split": "fresh",
      "mode": "oldest",
      "correct": false,
      "exact": 4,
      "trials": 10,
      "accepted": 6,
      "evictions": 146,
      "choices": 146,
      "wrong": 136,
      "abstentions": 6
    },
    {
      "split": "fresh",
      "mode": "oldest",
      "correct": true,
      "exact": 4,
      "trials": 10,
      "accepted": 6,
      "evictions": 152,
      "choices": 152,
      "wrong": 0,
      "abstentions": 6
    },
    {
      "split": "fresh",
      "mode": "reserve",
      "correct": false,
      "exact": 6,
      "trials": 10,
      "accepted": 8,
      "evictions": 146,
      "choices": 146,
      "wrong": 0,
      "abstentions": 4
    },
    {
      "split": "fresh",
      "mode": "reserve",
      "correct": true,
      "exact": 6,
      "trials": 10,
      "accepted": 8,
      "evictions": 146,
      "choices": 146,
      "wrong": 0,
      "abstentions": 4
    }
  ],
  "witness": [
    {
      "id": "53813-adjacent",
      "mode": "oldest",
      "at": 12538,
      "firsts": [
        10192,
        1248,
        2528,
        3808,
        5072,
        6368,
        7648,
        8928
      ],
      "intended": 1248,
      "actual": 10192,
      "wrong": true
    },
    {
      "id": "53813-adjacent",
      "mode": "oldest",
      "at": 13818,
      "firsts": [
        11488,
        1248,
        2528,
        3808,
        5072,
        6368,
        7648,
        8928
      ],
      "intended": 1248,
      "actual": 11488,
      "wrong": true
    },
    {
      "id": "53813-adjacent",
      "mode": "oldest",
      "at": 15114,
      "firsts": [
        12768,
        1248,
        2528,
        3808,
        5072,
        6368,
        7648,
        8928
      ],
      "intended": 1248,
      "actual": 12768,
      "wrong": true
    },
    {
      "id": "53813-adjacent",
      "mode": "oldest",
      "at": 16378,
      "firsts": [
        14048,
        1248,
        2528,
        3808,
        5072,
        6368,
        7648,
        8928
      ],
      "intended": 1248,
      "actual": 14048,
      "wrong": true
    },
    {
      "id": "53813-adjacent",
      "mode": "oldest",
      "at": 17658,
      "firsts": [
        15312,
        1248,
        2528,
        3808,
        5072,
        6368,
        7648,
        8928
      ],
      "intended": 1248,
      "actual": 15312,
      "wrong": true
    },
    {
      "id": "53813-adjacent",
      "mode": "oldest",
      "at": 18938,
      "firsts": [
        16608,
        1248,
        2528,
        3808,
        5072,
        6368,
        7648,
        8928
      ],
      "intended": 1248,
      "actual": 16608,
      "wrong": true
    },
    {
      "id": "53813-adjacent",
      "mode": "oldest",
      "at": 20234,
      "firsts": [
        17888,
        1248,
        2528,
        3808,
        5072,
        6368,
        7648,
        8928
      ],
      "intended": 1248,
      "actual": 17888,
      "wrong": true
    },
    {
      "id": "53813-adjacent",
      "mode": "oldest",
      "at": 21498,
      "firsts": [
        19168,
        1248,
        2528,
        3808,
        5072,
        6368,
        7648,
        8928
      ],
      "intended": 1248,
      "actual": 19168,
      "wrong": true
    }
  ],
  "stimuli": [
    {
      "id": "53813-clean",
      "samples": 33760,
      "peak": 4096,
      "sha256": "424da68e6f3e42cc59f84eaf1626e8d938b33a34af47372e082563e6fc573c38"
    },
    {
      "id": "53813-adjacent",
      "samples": 66080,
      "peak": 4096,
      "sha256": "82475d48d660ead7cd7420148d642b26ea730587cbfa72cde762cb3f19d9141b"
    },
    {
      "id": "53813-gap",
      "samples": 258400,
      "peak": 4096,
      "sha256": "79d0db15621b8a2b4d410d9925bf033630b1fea4da9f70744db6900486600e89"
    },
    {
      "id": "53813-slow-pressure",
      "samples": 80160,
      "peak": 4096,
      "sha256": "5975f972ec28cf03befc2ad557652affe41339f944c0448aa22b24ab2d21bd1a"
    },
    {
      "id": "53813-recovery",
      "samples": 129760,
      "peak": 4096,
      "sha256": "3ef1c0388c48348b9ae2bca0c41852f79570b64641bc3a5d9a57e7e21db0153d"
    },
    {
      "id": "17093-clean",
      "samples": 33760,
      "peak": 4096,
      "sha256": "1713297c569acd842266f43f2b75bdb33cb2514fe8518c375dc5672d60a74723"
    },
    {
      "id": "17093-adjacent",
      "samples": 66080,
      "peak": 4096,
      "sha256": "a430ef5049828e9f0171e291cff87f499c6796f28cf6ead225ff72bdba8be459"
    },
    {
      "id": "17093-gap",
      "samples": 258400,
      "peak": 4096,
      "sha256": "89b19186a2af7ee80caa706437ec7330caab220cd107f05b5def23ea03761f3d"
    },
    {
      "id": "17093-slow-pressure",
      "samples": 80160,
      "peak": 4096,
      "sha256": "d8490add386f95ac07d2d263345da42faa0d8dfbb9a483449f69fef9204bf733"
    },
    {
      "id": "17093-recovery",
      "samples": 129760,
      "peak": 4096,
      "sha256": "3422be4691e095ceb00202609f84b50615b844fde7bd665855d7bc589bb6d0f1"
    }
  ]
}
*/
