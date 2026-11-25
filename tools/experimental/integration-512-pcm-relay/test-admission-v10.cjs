'use strict';
const {AdmissionStream}=require('./admission-v10.cjs'),{Stream}=require('./stream-v4.cjs'),{CandidateReceiver}=require('./candidate-v9.cjs'),{EpochReceiver}=require('./epoch-v8.cjs'),v1=require('./relay.cjs'),v2=require('./bound-v2.cjs'),{simulate}=require('./deadline-epoch-v8.cjs');
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const Z=n=>new Int16Array(n),eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b),hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const out=process.argv[2]||'admission-v10-output',modes=['sticky','candidate','peak512','admission'],rows=[],stress=[];let checks=0;fs.mkdirSync(out,{recursive:true});
function check(b,m){checks++;assert.ok(b,m);}
function receiver(emit,mode,budget=4){if(mode==='candidate')return new CandidateReceiver(emit,mode,budget);if(mode==='peak512')return new EpochReceiver(emit,mode,budget);const s=new (mode==='admission'?AdmissionStream:Stream)(emit);s.finish=()=>{s.closed=true;return {sample:s.total,acquisition:s.overflow?'overloaded':s.cluster||s.pending.length?'pending':'clear'};};return s;}
function decode(p,mode,budget=4,chunk=511){const events=[],s=receiver(e=>events.push(e),mode,budget);for(let i=0;i<p.length;i+=chunk)s.push(p.subarray(i,i+chunk));const final=s.finish();check(events.every((e,i)=>e.at<=p.length&&(!i||e.at>=events[i-1].at)&&(e.sourceAt??e.at)<=e.at),'causal');const stats=s.stats||s.stream.stats;check(stats.maxPending<=8,'capacity');return {events,final,stats};}
function write(file,pcm){const bytes=v1.wav(pcm);fs.writeFileSync(path.join(out,file),bytes);const read=fs.readFileSync(path.join(out,file));check(hash(bytes)===hash(read)&&read.length===44+pcm.length*2,'export');return {file,sha256:hash(read),samples:pcm.length};}
function read(file){const b=fs.readFileSync(file);assert.equal(b.length,44+b.readUInt32LE(40));return Int16Array.from({length:(b.length-44)/2},(_,i)=>b.readInt16LE(44+2*i));}
const oks=d=>d.events.filter(e=>e.status==='ok').map(e=>e.packet);
function trial(seed,scenario,pcm,expected,budget=4){const meta=write(`stress-${seed}-${scenario}.wav`,pcm),baseline=decode(pcm,'sticky',budget);for(const mode of modes){const d=mode==='sticky'?baseline:decode(pcm,mode,budget);check(oks(d).every(p=>expected.some(q=>eq(p,q))),`unexpected packet ${scenario}/${mode}`);if(mode==='admission'){check(eq(d,decode(pcm,mode,budget,127)),'partition');if(!baseline.events.some(e=>e.status==='overflow'))check(eq(oks(d),oks(baseline)),`baseline agreement ${scenario}`);}stress.push({...meta,seed,scenario,mode,budget,exact:eq(oks(d),expected),ok:oks(d),...d});}}
for(const seed of [17239,88301]){
 const A={...v1.base,seq:1+seed%16},a=v2.render(A,seed/997),B={...A,seq:1+(seed+1)%16,tree:['question',['open']]},b=v2.render(B,seed/991),tail=Z(2400),flood=(n,gap)=>v1.join(...Array.from({length:n},()=>v1.join(a.slice(0,640),Z(gap))));
 for(const gap of [0,640,1280,1920,3200])trial(seed,'onsets-'+gap,v1.join(flood(70,gap),Z(24000),b,tail),[B]);
 // Legal-looking metadata carrier survives the prefix screen; not a legal frame.
 for(const spacing of [1280,1920]){const p=new Int16Array(spacing*70);for(let i=0;i<p.length;i++)p[i]=Math.round(4096*Math.sin(2*Math.PI*500*i/16000+seed/997));for(let j=0;j<70;j++)p.set(a.slice(0,640),j*spacing);trial(seed,'filled-'+spacing,v1.join(p,Z(24000),b,tail),[B]);}
 const erase=indices=>{const x=a.slice();for(const j of indices)x.fill(0,640+j*1280,640+(j+1)*1280);return x;};
 trial(seed,'clean',v1.join(a,tail),[A]);trial(seed,'two-erased',v1.join(erase([0,1]),tail),[A]);trial(seed,'three-erased',v1.join(erase([0,1,2]),tail),[]);
 trial(seed,'weak',v1.join(Int16Array.from(a,x=>Math.round(x/8)),tail),[A]);trial(seed,'false-onset',v1.join(a.slice(0,640),Z(9600),a,tail),[A]);
 trial(seed,'drift',v1.join(Int16Array.from({length:Math.round(a.length*1.009)},(_,i)=>a[Math.min(a.length-1,Math.floor(i/1.009))]),tail),[A]);
}
const flood=v1.join(...Array.from({length:20},()=>v1.join(v2.render(v1.base).slice(0,640),Z(640))));
for(const scenario of ['clean','ack-loss','revision','drift','forged'])for(const mode of ['sticky','candidate','admission']){
 const hooks={receiver:emit=>receiver(emit,mode),interference:(pcm,at,slot)=>{if((scenario==='ack-loss'||scenario==='revision')&&slot===1){pcm.fill(0,at,at+32000);pcm.set(flood,at+64);}}};
 const {pcm,...r}=simulate(scenario,'ack-first','adaptive',511,'absolute',hooks),meta=write(`${scenario}-${mode}.wav`,pcm),d=decode(read(path.join(out,meta.file)),mode,4,127);check(eq(d.events,r.evidence),'PCM rescan');check(r.trace.filter(e=>e.type==='tx'&&e.origin==='return').every(e=>e.evidenceAt<=e.at),'causal return');check(r.metrics.invalid===0||scenario==='forged','unexpected false confirmation');rows.push({...meta,...r,scenario,mode,events:r.evidence});
}
const summary=modes.map(mode=>({mode,...Object.fromEntries(['onsets','filled','clean','two-erased','three-erased','weak','false-onset','drift'].map(k=>[k,stress.filter(r=>r.mode===mode&&r.scenario.startsWith(k)&&r.exact).length]))}));
const interaction=rows.map(r=>({scenario:r.scenario,mode:r.mode,genuine:r.metrics.genuineConfirmations,retries:r.metrics.retries,overflow:r.metrics.overflow,invalid:r.metrics.invalid}));
fs.writeFileSync(path.join(out,'receipt.json'),JSON.stringify({schema:'mhac-admission-v10',rate:16000,node:process.version,checks,summary,interaction,rows,stress},null,2)+'\n');console.log(JSON.stringify({checks,summary,interaction}));
