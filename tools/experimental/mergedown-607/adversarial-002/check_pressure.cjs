'use strict';
// Independent synthetic regression for #607, not a reproduction of #449's Python receiver.
const fs=require('node:fs'), path=require('node:path'), crypto=require('node:crypto'), assert=require('node:assert/strict');
const ROOT=__dirname, SOURCE=path.join(ROOT,'source');
const REF='3637529f313949d31e55d66d04bb119547c1e29a';
const PINS={
 'relay.cjs':'3ba457f85f496e4d57d9789a2dc3b7d68fe2c071',
 'bound-v2.cjs':'2aa2905d4f4d756276814d5ca941c02c51e63f97',
 'stream-v4.cjs':'31769f808469b4416412be25a41eb238bfc1fdde',
 'parity-v11.cjs':'4d1ad5ead8f94ce219bc879fe05269bb1ce1f7df',
 'ledger-v12.cjs':'538bf2e28da108bfe9751cab6720e21325c55be1',
 'continuity-v13.cjs':'53291ce6dace840075b18d8db79ba481329ca509'};
const digest=(b,alg='sha256')=>crypto.createHash(alg).update(b).digest('hex');
for(const [f,id] of Object.entries(PINS)){const b=fs.readFileSync(path.join(SOURCE,f));assert.equal(digest(Buffer.concat([Buffer.from(`blob ${b.length}\0`),b]),'sha1'),id,f);}
const v1=require('./source/relay.cjs'),v2=require('./source/bound-v2.cjs'),{Stream,MAX_PENDING}=require('./source/stream-v4.cjs'),{ParityStream}=require('./source/parity-v11.cjs'),{ChronologicalStream}=require('./source/continuity-v13.cjs');
const cases=[['clean',0,40000],['four',4,40000],['eight',8,40000],['nine',9,40000],['twelve',12,40000],['twenty-four',24,40000],['long-gap',24,80000],['decoy-only',24,null]];
const modes={base:emit=>new Stream(emit),parity:emit=>new ParityStream(emit),reserve:emit=>new ChronologicalStream(emit,'reserve',4)};
const PCM_BYTES=p=>Buffer.from(p.buffer,p.byteOffset,p.byteLength); // Node host is little-endian; verify below.
assert.equal(require('node:os').endianness(),'LE');
function run(p,mode,chunk,finish=true){const events=[],s=modes[mode](e=>events.push(e));for(let i=0;i<p.length;i+=chunk)s.push(p.subarray(i,i+chunk));const before=events.length;if(finish)s.finish();return {events,stats:s.stats,overflow:s.overflow,eventsAtFinish:events.length-before};}
function main(out){fs.mkdirSync(out,{recursive:false});const rows=[],specimens=[];for(const seed of [71,113]){
 const expected={...v1.base,seq:1+seed%16};const signal=v2.render(expected,seed/997);const preamble=signal.slice(0,640);assert.equal(signal.length,31360);
 for(const [name,n,targetStart] of cases){const p=new Int16Array(150000);const decoyStarts=Array.from({length:n},(_,i)=>1024+i*1280);for(const s of decoyStarts)p.set(preamble,s);const decoyEnd=n?decoyStarts.at(-1)+preamble.length:0;
  if(targetStart!==null){assert.ok(decoyEnd<=targetStart);p.set(signal,targetStart);assert.deepEqual(p.slice(targetStart,targetStart+signal.length),signal);}
  const specimen=`${seed}-${name}.wav`,wav=v1.wav(p);fs.writeFileSync(path.join(out,specimen),wav);const hash=digest(PCM_BYTES(p));specimens.push({file:specimen,sha256:digest(wav),pcmSha256:hash,targetSha256:targetStart===null?null:digest(PCM_BYTES(signal)),samples:p.length,peak:p.reduce((a,b)=>Math.max(a,Math.abs(b)),0),decoyStarts,decoyEnd,targetStart});
  for(const mode of Object.keys(modes)){const a=run(p,mode,511),b=run(p,mode,127);assert.deepEqual(a,b,`${seed}/${name}/${mode}: partition dependence`);assert.equal(a.eventsAtFinish,0,'EOF must not promote evidence in padded fixtures');assert.ok(a.stats.maxPending<=MAX_PENDING);const accepted=a.events.filter(e=>e.status==='ok');const correct=accepted.filter(e=>JSON.stringify(e.packet)===JSON.stringify(expected)&&targetStart!==null);assert.equal(accepted.length,correct.length,'unexpected semantic release');assert.ok(correct.length<=1,'duplicate');for(const e of correct){assert.ok(e.at>=targetStart+signal.length-320);assert.ok(e.at<=p.length);}
   // Prefix replay at the first terminal overflow or accepted event, excluding EOF.
   const witness=a.events.find(e=>e.status==='overflow'||e.status==='ok');if(witness){const prefix=run(p.subarray(0,witness.at),mode,257,false);assert.deepEqual(prefix.events,a.events.filter(e=>e.at<=witness.at),'causal prefix mismatch');}
   rows.push({seed,name,mode,targetStart,decoyEnd,pcmSha256:hash,expected:targetStart===null?null:expected,correct:correct.length,wrong:accepted.length-correct.length,causalPrefixChecked:!!witness,...a});
  }
 }
}
 for(const seed of [71,113])for(const mode of Object.keys(modes)){const clean=rows.find(r=>r.seed===seed&&r.mode===mode&&r.name==='clean');assert.equal(clean.correct,1);const decoys=rows.find(r=>r.seed===seed&&r.mode===mode&&r.name==='decoy-only');assert.equal(decoys.correct,0);}
 const summary=cases.map(([name,n])=>({name,n,modes:Object.fromEntries(Object.keys(modes).map(m=>{const r=rows.filter(x=>x.name===name&&x.mode===m);return [m,{correct:r.reduce((a,x)=>a+x.correct,0),wrong:r.reduce((a,x)=>a+x.wrong,0),overflow:r.filter(x=>x.overflow).length,maxPending:Math.max(...r.map(x=>x.stats.maxPending)),scans:r.reduce((a,x)=>a+x.stats.scans,0),prefixRefused:r.reduce((a,x)=>a+(x.stats.prefixCandidatesRejected||0),0)}]}))}));
 const receipt={schema:'mhac-607-independent-preamble-pressure-v1',ref:REF,pins:PINS,node:process.version,seeds:[71,113],chunkSizes:[511,127],rate:16000,summary,rows,specimens,limits:'Fixed synthetic disjoint waveforms, exact frozen Integration receivers, not #449 Python Run062, no CPU parity, no physical or human evidence. Prefix replay checks observed events only.'};fs.writeFileSync(path.join(out,'receipt.json'),JSON.stringify(receipt,null,2)+'\n');console.log(JSON.stringify(summary,null,2));}
main(process.argv[2]||path.join(ROOT,'out'));
