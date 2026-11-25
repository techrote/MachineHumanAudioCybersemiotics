'use strict';
const {EpochReceiver}=require('./epoch-v8.cjs'),v1=require('./relay.cjs'),v2=require('./bound-v2.cjs'),{simulate}=require('./deadline-epoch-v8.cjs');
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const Z=n=>new Int16Array(n),eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b),hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const modes=['sticky','peak512','cooldown','history','backoff'],out=process.argv[2]||'epoch-v8-output',rows=[],stress=[];let checks=0;fs.mkdirSync(out,{recursive:true});
function check(b,m){checks++;assert.ok(b,m);}
function decode(p,mode,budget,chunk){const events=[],r=new EpochReceiver(e=>events.push(e),mode,budget);for(let i=0;i<p.length;i+=chunk)r.push(p.subarray(i,i+chunk));const final=r.finish();check(final.epoch<=budget&&r.replayed<=640*final.epoch,'budget');check(events.every((e,i)=>e.at>=0&&(!i||e.at>=events[i-1].at)&&(e.sourceAt??e.at)<=e.at),'causal clock');return {events,final,replayed:r.replayed};}
function write(file,pcm){const bytes=v1.wav(pcm);fs.writeFileSync(path.join(out,file),bytes);const read=fs.readFileSync(path.join(out,file));check(hash(bytes)===hash(read)&&read.length===44+pcm.length*2,'export');return {file,sha256:hash(read),samples:pcm.length};}
for(const seed of [9173,62351]){
 const A={...v1.base,seq:1+seed%16},B={...A,seq:1+(seed+1)%16,tree:['question',['open']]},a=v2.render(A,seed/997),b=v2.render(B,seed/991),weak=Int16Array.from(a,x=>Math.round(x/8)),flood=n=>v1.join(Z(320),...Array.from({length:n},()=>v1.join(a.slice(0,640),Z(640))));
 const at=decode(flood(10),'sticky',0,127).events.find(e=>e.status==='overflow').at;
 const stimuli=[...[-480,-320,-160,0,160,320,640].map(offset=>({name:'boundary-'+offset,pcm:v1.join(flood(10).slice(0,Math.min(at,at+offset)),Z(Math.max(0,offset)),a,Z(2400)),budget:1,expected:[A]})),{name:'early-weak',pcm:v1.join(flood(10),Z(4000),weak,Z(24000),b,Z(2400)),budget:4,expected:[A,B]},{name:'long-one',pcm:v1.join(flood(70),Z(24000),b,Z(2400)),budget:1,expected:[B]},{name:'long-four',pcm:v1.join(flood(70),Z(24000),b,Z(2400)),budget:4,expected:[B]}];
 for(const {name,pcm,budget,expected} of stimuli){const meta=write(`stress-${seed}-${name}.wav`,pcm);for(const mode of modes){const d=decode(pcm,mode,budget,511),ok=d.events.filter(e=>e.status==='ok').map(e=>e.packet);check(ok.every(p=>expected.some(q=>eq(p,q))),'unexpected identity');check(eq(d,decode(pcm,mode,budget,127)),'partition');stress.push({...meta,seed,scenario:name,mode,budget,ok,exact:eq(ok,expected),...d});}}
}
const flood=v1.join(...Array.from({length:10},()=>v1.join(v2.render(v1.base).slice(0,640),Z(640))));
for(const scenario of ['clean','ack-loss','revision','forged'])for(const mode of modes){
 const hooks={receiver:emit=>new EpochReceiver(emit,mode,4),interference:(pcm,at,slot)=>{if(scenario!=='clean'&&scenario!=='forged'&&slot===1){pcm.fill(0,at,at+32000);pcm.set(flood,at+64);}}};
 const {pcm,...r}=simulate(scenario,'ack-first','adaptive',511,'absolute',hooks),meta=write(`${scenario}-${mode}.wav`,pcm);
 const read=fs.readFileSync(path.join(out,meta.file));const samples=Int16Array.from({length:meta.samples},(_,i)=>read.readInt16LE(44+2*i));const d=decode(samples,mode,4,127);check(eq(d.events,r.evidence),'PCM rescan');check(r.trace.filter(e=>e.type==='tx'&&e.origin==='return').every(e=>e.evidenceAt<=e.at),'causal return');check(r.metrics.invalid===0||scenario==='forged','unexpected false confirmation');rows.push({...meta,...r,scenario,mode,events:r.evidence});
}
const summary=modes.map(mode=>({mode,...Object.fromEntries(['boundary','early','long-one','long-four'].map(k=>[k,stress.filter(r=>r.mode===mode&&r.scenario.startsWith(k)&&r.exact).length]))}));
const interaction=rows.map(r=>({scenario:r.scenario,mode:r.mode,genuine:r.metrics.genuineConfirmations,retries:r.metrics.retries,overflow:r.metrics.overflow,invalid:r.metrics.invalid}));
fs.writeFileSync(path.join(out,'receipt.json'),JSON.stringify({schema:'mhac-epoch-v8',rate:16000,node:process.version,checks,summary,interaction,rows,stress},null,2)+'\n');console.log(JSON.stringify({checks,summary,interaction}));
