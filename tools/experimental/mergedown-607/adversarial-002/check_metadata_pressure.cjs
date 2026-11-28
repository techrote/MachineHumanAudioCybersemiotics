'use strict';
// #607/#817: overlapping feasible metadata trains, disjoint genuine PCM.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const ref='3637529f313949d31e55d66d04bb119547c1e29a';
const pins={'relay.cjs':'3ba457f85f496e4d57d9789a2dc3b7d68fe2c071','bound-v2.cjs':'2aa2905d4f4d756276814d5ca941c02c51e63f97','stream-v4.cjs':'31769f808469b4416412be25a41eb238bfc1fdde','parity-v11.cjs':'4d1ad5ead8f94ce219bc879fe05269bb1ce1f7df','ledger-v12.cjs':'538bf2e28da108bfe9751cab6720e21325c55be1','continuity-v13.cjs':'53291ce6dace840075b18d8db79ba481329ca509'};
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
for(const [f,h] of Object.entries(pins)){const b=fs.readFileSync(path.join(__dirname,'source',f));assert.equal(crypto.createHash('sha1').update(`blob ${b.length}\0`).update(b).digest('hex'),h);}
const v1=require('./source/relay.cjs'),v2=require('./source/bound-v2.cjs'),{Stream,MAX_PENDING}=require('./source/stream-v4.cjs'),{ParityStream,feasible}=require('./source/parity-v11.cjs'),{ChronologicalStream}=require('./source/continuity-v13.cjs');
const modes={base:e=>new Stream(e),parity:e=>new ParityStream(e),reserve:e=>new ChronologicalStream(e,'reserve',4)};
const cases=[['clean',0,50000],['eight',8,50000],['nine-near',9,50000],['nine-far',9,90000],['nine-only',9,null]];
const bytes=p=>Buffer.from(p.buffer,p.byteOffset,p.byteLength);assert.equal(require('node:os').endianness(),'LE');
function run(p,mode,chunk,finish=true){const events=[],s=modes[mode](e=>events.push(e));for(let i=0;i<p.length;i+=chunk)s.push(p.subarray(i,i+chunk));const n=events.length;if(finish)s.finish();return {events,stats:s.stats,overflow:s.overflow,atFinish:events.length-n};}
const out=process.argv[2];assert.ok(out,'new output directory required');fs.mkdirSync(out);const rows=[],specimens=[];
for(const seed of [71,113]){
 const target={...v1.base,seq:1+seed%16},signal=v2.render(target,seed/997),decoy={...v1.base,kind:1,source:1,version:14,actor:1,event:1,seq:14},src=v1.render(decoy,seed/997),words=v1.frame(decoy).slice(0,8);
 assert.deepEqual(words,[1,1,14,1,1,14,1,1]);assert.equal(words.reduce((a,x)=>a+x,0)%17,0);assert.equal(words.reduce((a,x,i)=>a+(i+1)*x,0)%17,0);assert.ok(feasible(words));
 for(const [name,n,targetStart] of cases){const p=new Int16Array(150000),starts=Array.from({length:n},(_,i)=>1024+3840*i),decoyEnd=n?starts.at(-1)+10880:0;
  for(const s of starts)for(let j=0;j<8;j++)p.set(src.subarray(640+j*1280,640+(j+1)*1280),s+640+j*1280);
  for(const s of starts)p.set(src.subarray(0,640),s);
  // Exact nominal receiver observation windows preserved despite overlapping decoys.
  for(const s of starts)for(let j=0;j<8;j++)assert.deepEqual(p.subarray(s+960+j*1280,s+1280+j*1280),src.subarray(960+j*1280,1280+j*1280));
  if(targetStart!==null){assert.ok(decoyEnd<=targetStart);p.set(signal,targetStart);assert.deepEqual(p.subarray(targetStart,targetStart+signal.length),signal);}
  const file=`${seed}-${name}.wav`,wav=v1.wav(p),hash=sha(bytes(p));fs.writeFileSync(path.join(out,file),wav);specimens.push({seed,name,file,sha256:sha(wav),pcmSha256:hash,starts,decoyEnd,targetStart,targetSha256:targetStart===null?null:sha(bytes(signal)),words,peak:p.reduce((a,x)=>Math.max(a,Math.abs(x)),0)});
  for(const mode of Object.keys(modes)){const a=run(p,mode,511),b=run(p,mode,127);assert.deepEqual(a,b);assert.equal(a.atFinish,0);assert.ok(a.stats.maxPending<=MAX_PENDING);
   const good=a.events.filter(e=>e.status==='ok'),correct=good.filter(e=>targetStart!==null&&JSON.stringify(e.packet)===JSON.stringify(target));assert.equal(good.length,correct.length);assert.ok(correct.length<=1);
   const witnesses=a.events.filter(e=>['overflow','evicted','association-incomplete','ok'].includes(e.status));for(const w of witnesses){assert.deepEqual(run(p.subarray(0,w.at),mode,257,false).events,a.events.filter(e=>e.at<=w.at));}
   const loss=a.events.filter(e=>e.status==='association-incomplete');for(const e of loss){assert.equal(e.packet,null);assert.ok(a.events.some(w=>w.status==='evicted'&&w.lossStart<e.end&&e.start<w.lossEnd));}
   rows.push({seed,name,mode,pcmSha256:hash,correct:correct.length,wrong:good.length-correct.length,prefixChecks:witnesses.length,...a});
  }
 }
}
const summary=cases.map(([name])=>({name,modes:Object.fromEntries(Object.keys(modes).map(mode=>{const r=rows.filter(x=>x.name===name&&x.mode===mode);return [mode,{correct:r.reduce((a,x)=>a+x.correct,0),overflow:r.filter(x=>x.overflow).length,evicted:r.reduce((a,x)=>a+(x.stats.evicted||0),0),lossAbstentions:r.reduce((a,x)=>a+(x.stats.lossAbstentions||0),0),prefixRefused:r.reduce((a,x)=>a+(x.stats.prefixCandidatesRejected||0),0)}];}))}));
for(const r of rows){const expected=r.name==='clean'||r.name==='eight'||(r.name==='nine-far'&&r.mode==='reserve')?1:0;assert.equal(r.correct,expected,JSON.stringify([r.seed,r.name,r.mode]));if(r.name.startsWith('nine')){if(r.mode==='reserve')assert.equal(r.stats.evicted,1);else assert.ok(r.overflow);}if(r.name==='nine-near'&&r.mode==='reserve')assert.equal(r.stats.lossAbstentions,1);}
const receipt={schema:'mhac-607-metadata-pressure-v1',ref,pins,node:process.version,rate:16000,samples:150000,seeds:[71,113],chunkSizes:[511,127],summary,rows,specimens,limits:'Decoys overlap each other; genuine PCM disjoint. Fixed synthetic construction, not Python Run062 or CPU/physical/human evidence.'};fs.writeFileSync(path.join(out,'receipt.json'),JSON.stringify(receipt,null,2)+'\n');console.log(JSON.stringify(summary,null,2));
