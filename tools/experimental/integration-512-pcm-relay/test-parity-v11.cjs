'use strict';
const {ParityStream,feasible}=require('./parity-v11.cjs');
const {AdmissionStream}=require('./admission-v10.cjs'),v1=require('./relay.cjs'),v2=require('./bound-v2.cjs'),{simulate}=require('./deadline-epoch-v8.cjs');
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const Z=n=>new Int16Array(n),eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b),hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const out=process.argv[2]||'parity-v11-output',modes=['admission','parity','oldest','incoming'],rows=[],stress=[];let checks=0;fs.mkdirSync(out,{recursive:true});
function check(b,m){checks++;assert.ok(b,m);}
function receiver(emit,mode){return mode==='admission'?new AdmissionStream(emit):new ParityStream(emit,mode);}
function decode(p,mode,budget=4,chunk=511){const events=[],s=receiver(e=>events.push(e),mode,budget);for(let i=0;i<p.length;i+=chunk)s.push(p.subarray(i,i+chunk));const final=s.finish();check(events.every((e,i)=>e.at<=p.length&&(!i||e.at>=events[i-1].at)&&(e.sourceAt??e.at)<=e.at),'causal');const stats=s.stats||s.stream.stats;check(stats.maxPending<=8,'capacity');return {events,final,stats};}
function write(file,pcm){const bytes=v1.wav(pcm);fs.writeFileSync(path.join(out,file),bytes);const read=fs.readFileSync(path.join(out,file));check(hash(bytes)===hash(read)&&read.length===44+pcm.length*2,'export');return {file,sha256:hash(read),samples:pcm.length};}
function read(file){const b=fs.readFileSync(file);assert.equal(b.length,44+b.readUInt32LE(40));return Int16Array.from({length:(b.length-44)/2},(_,i)=>b.readInt16LE(44+2*i));}
const oks=d=>d.events.filter(e=>e.status==='ok').map(e=>e.packet);
function trial(seed,scenario,pcm,expected,budget=4){const meta=write(`stress-${seed}-${scenario}.wav`,pcm),baseline=decode(pcm,'admission',budget);for(const mode of modes){const d=mode==='admission'?baseline:decode(pcm,mode,budget);check(oks(d).every(p=>expected.some(q=>eq(p,q))),`unexpected packet ${scenario}/${mode}`);if(mode!=='admission'){if(scenario==='clean'||scenario==='filled-1280')check(eq(d,decode(pcm,mode,budget,127)),'partition');if(!baseline.events.some(e=>e.status==='overflow')&&!d.stats.evicted)check(eq(oks(d),oks(baseline)),`baseline agreement ${scenario}`);}stress.push({...meta,seed,scenario,mode,budget,exact:eq(oks(d),expected),ok:oks(d),...d});}}
// Independent brute completion, not the algebraic solver. Check valid codewords and arbitrary observations.
let rng=873241;const rand=n=>{rng=(Math.imul(rng,1664525)+1013904223)>>>0;return rng%n;};
function brute(w){if(w.filter(x=>x===null).length>2)return false;const a=Array.from({length:8},(_,i)=>w[i]??null);function rec(i){if(i===8)return a[0]<=1&&a.slice(1,6).every(x=>x>=1)&&a.reduce((s,x)=>s+x,0)%17===0&&a.reduce((s,x,j)=>s+x*(j+1),0)%17===0;if(a[i]!==null)return rec(i+1);for(let j=0;j<17;j++){a[i]=j;if(rec(i+1)){a[i]=null;return true;}}a[i]=null;return false;}return rec(0);}
for(let i=0;i<1000;i++){const p={...v1.base,kind:rand(2),source:1+rand(16),version:1+rand(16),actor:1+rand(16),event:1+rand(16),seq:1+rand(16)},w=v1.frame(p).slice(0,7+rand(2));if(i%2)w[rand(w.length)]=rand(17);for(let j=0;j<i%3;j++)w[rand(w.length)]=null;check(feasible(w)===brute(w),'GF feasibility');}
for(const seed of [49157,90281]){
 const A={...v1.base,seq:1+seed%16},a=v2.render(A,seed/997),B={...A,seq:1+(seed+1)%16,tree:['question',['open']]},b=v2.render(B,seed/991),tail=Z(2400),flood=(n,gap)=>v1.join(...Array.from({length:n},()=>v1.join(a.slice(0,640),Z(gap))));
 for(const gap of [0,1280,1920])trial(seed,'onsets-'+gap,v1.join(flood(70,gap),Z(24000),b,tail),[B]);
 // Legal-looking metadata carrier survives the prefix screen; not a legal frame.
 for(const spacing of [640,1280,1920]){const p=new Int16Array(spacing*70);for(let i=0;i<p.length;i++)p[i]=Math.round(4096*Math.sin(2*Math.PI*500*i/16000+seed/997));for(let j=0;j<70;j++)p.set(a.slice(0,640),j*spacing);trial(seed,'filled-'+spacing,v1.join(p,Z(24000),b,tail),[B]);trial(seed,'dense-tail-'+spacing,v1.join(p,Z(320),b,tail),[B]);}
 // Observed erasures can keep parity feasible longer. Preserve finite-cap failure and eviction uncertainty.
 const partial=Z(1280*25);for(let i=0;i<25;i++){partial.set(a.slice(0,640),i*1280);if(i%4!==3)for(let j=640;j<1280;j++)partial[i*1280+j]=Math.round(4096*Math.sin(2*Math.PI*500*j/16000+seed/997));}
 trial(seed,'parity-plausible-separated',v1.join(partial,Z(64000),b,tail),[B]);
 trial(seed,'parity-plausible-adjacent',v1.join(partial,Z(320),b,tail),[B]);
 const erase=indices=>{const x=a.slice();for(const j of indices)x.fill(0,640+j*1280,640+(j+1)*1280);return x;};
 trial(seed,'clean',v1.join(a,tail),[A]);trial(seed,'two-erased',v1.join(erase([0,1]),tail),[A]);trial(seed,'three-erased',v1.join(erase([0,1,2]),tail),[]);
 trial(seed,'weak',v1.join(Int16Array.from(a,x=>Math.round(x/8)),tail),[A]);trial(seed,'false-onset',v1.join(a.slice(0,640),Z(9600),a,tail),[A]);
 trial(seed,'drift',v1.join(Int16Array.from({length:Math.round(a.length*1.009)},(_,i)=>a[Math.min(a.length-1,Math.floor(i/1.009))]),tail),[A]);
}
// Independently recreate the upstream held-out 28-onset stimuli and check published SHA256.
for(const seed of [42737,91583]){const A={...v1.base,seq:1+seed%16},a=v2.render(A,seed/997),B={...A,seq:1+(seed+1)%16,tree:['question',['open']]},b=v2.render(B,seed/991);
 for(const spacing of [1280,1920,2560]){const p=Z(spacing*28);for(let i=0;i<p.length;i++)p[i]=Math.round(4096*Math.sin(2*Math.PI*500*i/16000+seed/997));for(let j=0;j<28;j++)p.set(a.slice(0,640),j*spacing);const pcm=v1.join(p,Z(24000),b,Z(2400));
 if(seed===42737)check(hash(v1.wav(pcm))===({1280:'600935f563947c7ff543d338d39b4fdcd60e37c9b95c7b3ba3f9e238355be71e',1920:'9da4214ad7016c3e0be8ba4533b717dd86bd1248c8fc555b5b0903fe2ea64425',2560:'68dc5c4512da5178136d6b907024b3d103354ac0b2c852231a84f85074ffda78'})[spacing],'upstream WAV hash');trial(seed,'upstream-'+spacing,pcm,[B]);}}
const flood=v1.join(...Array.from({length:20},()=>v1.join(v2.render(v1.base).slice(0,640),Z(640))));
const plausible=Z(1280*20),pre=v2.render(v1.base).slice(0,640);for(let i=0;i<20;i++){plausible.set(pre,i*1280);if(i%4!==3)for(let j=640;j<1280;j++)plausible[i*1280+j]=Math.round(4096*Math.sin(2*Math.PI*500*j/16000));}
for(const scenario of ['clean','ack-loss','revision','forged'])for(const mode of ['admission','parity','oldest','incoming']){
 const hooks={receiver:emit=>receiver(emit,mode),interference:(pcm,at,slot)=>{if((scenario==='ack-loss'||scenario==='revision')&&slot===1){pcm.fill(0,at,at+32000);pcm.set(scenario==='revision'?plausible:flood,at+64);}}};
 const {pcm,...r}=simulate(scenario,'ack-first','adaptive',511,'absolute',hooks),meta=write(`${scenario}-${mode}.wav`,pcm),d=decode(read(path.join(out,meta.file)),mode,4,127);check(eq(d.events,r.evidence),'PCM rescan');check(r.trace.filter(e=>e.type==='tx'&&e.origin==='return').every(e=>e.evidenceAt<=e.at),'causal return');check(r.metrics.invalid===0||scenario==='forged','unexpected false confirmation');rows.push({...meta,...r,scenario,mode,events:r.evidence});
}
const summary=modes.map(mode=>({mode,...Object.fromEntries(['onsets','filled','dense-tail','upstream-1280','upstream-1920','upstream-2560','parity-plausible-separated','parity-plausible-adjacent','clean','two-erased','three-erased','weak','false-onset','drift'].map(k=>[k,stress.filter(r=>r.mode===mode&&r.scenario.startsWith(k)&&r.exact).length]))}));
const interaction=rows.map(r=>({scenario:r.scenario,mode:r.mode,genuine:r.metrics.genuineConfirmations,retries:r.metrics.retries,overflow:r.metrics.overflow,invalid:r.metrics.invalid}));
fs.writeFileSync(path.join(out,'receipt.json'),JSON.stringify({schema:'mhac-parity-v11',rate:16000,node:process.version,checks,summary,interaction,rows,stress},null,2)+'\n');console.log(JSON.stringify({checks,summary,interaction}));
