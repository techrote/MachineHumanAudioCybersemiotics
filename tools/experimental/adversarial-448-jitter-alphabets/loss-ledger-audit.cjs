'use strict';
// Adversarial Observatory Refs #448 #449 #512. 2026-11-25. Synthetic only.
// Evaluate pinned v11 draft; no upstream edits. Bounded interval ledger, same oldest eviction.
const REF="51b32dd3f75d3e22233f62f0fe1adcd80dc355e5", PINS={"relay.cjs":"3ba457f85f496e4d57d9789a2dc3b7d68fe2c071","bound-v2.cjs":"2aa2905d4f4d756276814d5ca941c02c51e63f97","stream-v4.cjs":"31769f808469b4416412be25a41eb238bfc1fdde","parity-v11.cjs":"4d1ad5ead8f94ce219bc879fe05269bb1ce1f7df"};
const factory=function factory(){
 const eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b),endDelta=Math.round(31360*1.015);
 const overlaps=(a,b)=>a[0]<b[1]&&b[0]<a[1];
 class Ledger{
  constructor(cap){if(!Number.isInteger(cap)||cap<1)throw Error('capacity');this.cap=cap;this.ranges=[];this.floor=0;this.merges=0;this.pruned=0;this.peak=0;}
  prune(floor){if(floor<this.floor)throw Error('nonmonotone frontier');this.floor=floor;const old=this.ranges.length;this.ranges=this.ranges.filter(r=>r[1]>floor);this.pruned+=old-this.ranges.length;}
  add(a,b){if(!Number.isSafeInteger(a)||!Number.isSafeInteger(b)||a>=b)throw Error('interval');if(b<=this.floor)return;
   const sorted=[...this.ranges,[a,b]].sort((x,y)=>x[0]-y[0]),out=[];
   for(const r of sorted){const prev=out[out.length-1];if(prev&&r[0]<=prev[1])prev[1]=Math.max(prev[1],r[1]);else out.push(r.slice());}
   while(out.length>this.cap){let k=0;for(let j=1;j<out.length-1;j++)if(out[j+1][0]-out[j][1]<out[k+1][0]-out[k][1])k=j;out.splice(k,2,[out[k][0],out[k+1][1]]);this.merges++;}
   this.ranges=out;this.peak=Math.max(this.peak,out.length);
  }
  blocks(a,b){if(a<this.floor)throw Error('query below retired frontier');return this.ranges.some(r=>overlaps(r,[a,b]));}
 }
 function make(ParityStream,cap){
  return class LedgerStream extends ParityStream{
   constructor(emit){super(emit,'oldest');this.ledger=new Ledger(cap);
    // The parent wrapper enforces a permanent hull. Replace only the release gate;
    // inherited detector, eviction choice, parity admission and full validation remain unchanged.
    this.emit=e=>{if(e.status==='evicted'){this.ledger.add(e.first,e.last+endDelta);emit({...e,lossIntervals:this.ledger.ranges.map(r=>r.slice())});}
     else if(e.status==='ok'&&this.ledger.blocks(e.start,e.end)){this.stats.lossAbstentions++;emit({...e,status:'association-incomplete',packet:null,reason:'overlap-with-evicted-candidate-ledger'});}
     else emit(e);};
   }
   drain(eof){super.drain(eof);const floor=Math.min(this.scan,this.cluster?.first??Infinity,...this.pending.map(c=>c.first));this.ledger.prune(floor);}
  };
 }
 function run(v1,v2,ParityStream,hash){
  let checks=0;const ck=(b,m)=>{checks++;if(!b)throw Error(m);};
  const control=new Ledger(2);control.add(0,10);control.add(30,40);ck(!control.blocks(15,25),'disjoint gap');ck(control.blocks(9,11),'true overlap');ck(!control.blocks(10,30),'half open');control.add(100,110);ck(control.blocks(15,25),'conservative gap merge');control.prune(40);ck(control.ranges.length===1,'retire merged region');
  let rng=12980731;const rnd=n=>{rng=(Math.imul(rng,1664525)+1013904223)>>>0;return rng%n;};
  let gapAbstentions=0,oracleTests=0;
  for(const cap of [1,2,4,8])for(let t=0;t<40;t++){const L=new Ledger(cap),all=[];let floor=0;
   for(let k=0;k<24;k++){floor+=rnd(12);L.prune(floor);const a=floor+rnd(80),b=a+1+rnd(20);all.push([a,b]);L.add(a,b);ck(L.ranges.length<=cap,'ledger bound');
    for(let j=0;j<5;j++){const x=floor+rnd(120),y=x+1+rnd(24),want=all.some(r=>overlaps(r,[x,y])),got=L.blocks(x,y);ck(!want||got,'oracle false release');oracleTests++;if(got&&!want)gapAbstentions++;}
   }
  }
  const Z=n=>new Int16Array(n),rows=[],specimens={},classes=[['hull',ParityStream],['ledger1',make(ParityStream,1)],['ledger4',make(ParityStream,4)]],seeds=[53813,97331];
  function decode(p,C,policy,chunk){const events=[],s=policy==='hull'?new C(e=>events.push(e),'oldest'):new C(e=>events.push(e));for(let i=0;i<p.length;i+=chunk)s.push(p.subarray(i,i+chunk));s.finish();
   const discarded=[];for(let i=0;i<events.length;i++){const e=events[i];ck(e.at<=p.length&&(!i||e.at>=events[i-1].at),'causal');if(e.status==='evicted')discarded.push([e.first,e.last+endDelta]);if(e.status==='ok')ck(!discarded.some(r=>overlaps(r,[e.start,e.end])),'accepted intersects discarded region');}
   ck(s.stats.maxPending<=8,'candidate cap');if(s.ledger)ck(s.ledger.peak<=s.ledger.cap,'loss cap');
   return {events,stats:s.stats,ledger:s.ledger?{ranges:s.ledger.ranges,peak:s.ledger.peak,merges:s.ledger.merges,pruned:s.ledger.pruned,floor:s.ledger.floor}:null};
  }
  for(const seed of seeds){const A={...v1.base,seq:1+seed%16},B={...A,seq:1+(seed+1)%16,tree:['question',['open']]},C={...A,seq:1+(seed+2)%16,tree:['verify',['fault']]},a=v2.render(A,seed/997),b=v2.render(B,seed/991),c=v2.render(C,seed/983),tail=Z(2400);
   const flood=n=>{const p=Z(n*1280);for(let i=0;i<n;i++){p.set(a.slice(0,640),i*1280);if(i%4!==3)for(let j=640;j<1280;j++)p[i*1280+j]=Math.round(4096*Math.sin(2*Math.PI*500*j/16000+seed/997));}return p;};
   const f=flood(25),g=flood(13);
   const scenarios=[['clean',v1.join(a,tail),[A]],['adjacent',v1.join(f,Z(320),b,tail),[B]],['separated',v1.join(f,Z(64000),b,tail),[B]],['two-bursts',v1.join(f,Z(64000),b,Z(6400),g,Z(64000),c,tail),[B,C]],['two-bursts-tight',v1.join(g,Z(32000),b,Z(320),g,Z(32000),c,tail),[B,C]]];
   for(const [name,pcm,expected] of scenarios){const id=seed+'-'+name,sha256=hash(v1.wav(pcm));if(seed===seeds[0])specimens[id]=pcm;
    for(const [policy,Cl] of classes){const d=decode(pcm,Cl,policy,511),ok=d.events.filter(e=>e.status==='ok').map(e=>e.packet);let next=0;for(const x of ok){while(next<expected.length&&!eq(expected[next],x))next++;ck(next<expected.length,'unexpected or duplicate packet');next++;}
     if(name==='clean'||name==='two-bursts-tight')ck(eq(d,decode(pcm,Cl,policy,127)),'chunk partition');
     rows.push({id,seed,name,policy,sha256,samples:pcm.length,expected,exact:eq(ok,expected),accepted:ok.length,...d});
    }
   }
  }
  const summary=classes.map(([policy])=>{const a=rows.filter(x=>x.policy===policy);return {policy,byCondition:Object.fromEntries([...new Set(a.map(x=>x.name))].map(name=>[name,a.filter(x=>x.name===name&&x.exact).length])),accepted:a.reduce((s,x)=>s+x.accepted,0),evictions:a.reduce((s,x)=>s+x.stats.evicted,0),abstentions:a.reduce((s,x)=>s+x.stats.lossAbstentions,0),maxLossRanges:Math.max(...a.map(x=>x.ledger?.peak??1)),pruned:a.reduce((s,x)=>s+(x.ledger?.pruned??0),0),merges:a.reduce((s,x)=>s+(x.ledger?.merges??0),0)};});
  return {checks,oracleTests,gapAbstentions,summary,rows,specimens};
 }
 return {Ledger,make,run};
};
module.exports=factory();
if(require.main===module){
 const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),dir=path.resolve(process.argv[2]||'.'),out=path.resolve(process.argv[3]||'loss-ledger-output');
 for(const [f,sha] of Object.entries(PINS)){const b=fs.readFileSync(path.join(dir,f));if(crypto.createHash('sha1').update('blob '+b.length+'\0').update(b).digest('hex')!==sha)throw Error('wrong blob '+f);}
 const v1=require(path.join(dir,'relay.cjs')),v2=require(path.join(dir,'bound-v2.cjs')),{ParityStream}=require(path.join(dir,'parity-v11.cjs')),hash=b=>crypto.createHash('sha256').update(b).digest('hex');
 const {specimens,...receipt}=module.exports.run(v1,v2,ParityStream,hash);fs.mkdirSync(out,{recursive:true});const stimuli=Object.entries(specimens).map(([id,p])=>{const b=v1.wav(p);fs.writeFileSync(path.join(out,id+'.wav'),b);return {id,samples:p.length,sha256:hash(b),peak:p.reduce((m,x)=>Math.max(m,Math.abs(x)),0)};});
 fs.writeFileSync(path.join(out,'receipt.json'),JSON.stringify({ref:REF,pins:PINS,...receipt,stimuli},null,2)+'\n');console.log(JSON.stringify({checks:receipt.checks,oracleTests:receipt.oracleTests,gapAbstentions:receipt.gapAbstentions,summary:receipt.summary,stimuli},null,2));
}
/* Executed V8 receipt, actual pinned sources, SHA256 known answers empty/abc. Native CLI not executed. The abstract interval census is not a PCM or perceptual measurement. Finite tests do not prove end-to-end association safety.\n{
  "checks": 24117,
  "oracleTests": 19200,
  "gapAbstentions": 288,
  "summary": [
    {
      "policy": "hull",
      "byCondition": {
        "clean": 2,
        "adjacent": 0,
        "separated": 2,
        "two-bursts": 2,
        "two-bursts-tight": 2
      },
      "accepted": 12,
      "evictions": 132,
      "abstentions": 2,
      "maxLossRanges": 1,
      "pruned": 0,
      "merges": 0
    },
    {
      "policy": "ledger1",
      "byCondition": {
        "clean": 2,
        "adjacent": 0,
        "separated": 2,
        "two-bursts": 2,
        "two-bursts-tight": 2
      },
      "accepted": 12,
      "evictions": 132,
      "abstentions": 2,
      "maxLossRanges": 1,
      "pruned": 12,
      "merges": 0
    },
    {
      "policy": "ledger4",
      "byCondition": {
        "clean": 2,
        "adjacent": 0,
        "separated": 2,
        "two-bursts": 2,
        "two-bursts-tight": 2
      },
      "accepted": 12,
      "evictions": 132,
      "abstentions": 2,
      "maxLossRanges": 1,
      "pruned": 12,
      "merges": 0
    }
  ],
  "stimuli": [
    {
      "id": "53813-clean",
      "samples": 33760,
      "sha256": "d7803c0d01adf8130b6828932929587b6bca1f7822163ddb834973a9bd593d54",
      "peak": 4095
    },
    {
      "id": "53813-adjacent",
      "samples": 66080,
      "sha256": "82475d48d660ead7cd7420148d642b26ea730587cbfa72cde762cb3f19d9141b",
      "peak": 4096
    },
    {
      "id": "53813-separated",
      "samples": 129760,
      "sha256": "3ef1c0388c48348b9ae2bca0c41852f79570b64641bc3a5d9a57e7e21db0153d",
      "peak": 4096
    },
    {
      "id": "53813-two-bursts",
      "samples": 248160,
      "sha256": "d8284a6c8b268cfcfcf4caf99f6534d592fdbdce57cb1cdac591afd4cfe1d2ee",
      "peak": 4096
    },
    {
      "id": "53813-two-bursts-tight",
      "samples": 162720,
      "sha256": "923bb9412e145de6812d44de8f0b79a3d9f99aa9ef05ecdb0e853d409089e285",
      "peak": 4096
    }
  ]
}
*/
