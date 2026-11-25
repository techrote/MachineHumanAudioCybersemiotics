'use strict';
// Native filesystem/WAV replay and adversarial boundary checks; no external dependencies.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),L=require('./relay.cjs');
const assert=require('node:assert/strict'),dir=process.argv[2]||'relay-output';
function pcm(bytes){assert.equal(bytes.toString('ascii',0,4),'RIFF');assert.equal(bytes.toString('ascii',8,12),'WAVE');assert.equal(bytes.toString('ascii',36,40),'data');assert.equal(bytes.readUInt16LE(20),1);assert.equal(bytes.readUInt16LE(22),1);assert.equal(bytes.readUInt32LE(24),16000);assert.equal(bytes.readUInt16LE(34),16);assert.equal(bytes.readUInt32LE(40),bytes.length-44);return Int16Array.from({length:(bytes.length-44)/2},(_,i)=>bytes.readInt16LE(44+2*i));}
const manifest=JSON.parse(fs.readFileSync(path.join(dir,'stimuli.json'),'utf8'));
const rows=[];for(const m of manifest){const bytes=fs.readFileSync(path.join(dir,m.filename));assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'),m.sha256);const p=pcm(bytes);assert.equal(p.length,m.samples);const trace=JSON.parse(fs.readFileSync(path.join(dir,m.filename.replace('.wav','.json')),'utf8'));const expected=trace.trace.flatMap(t=>(t.hits||[]).filter(h=>h.status==='ok').map(h=>h.packet));const hits=L.acquire(p),actual=hits.filter(h=>h.status==='ok').map(h=>h.packet);rows.push({file:m.filename,expected:expected.length,actual:actual.length,equal:JSON.stringify(expected)===JSON.stringify(actual),statuses:hits.map(h=>h.status)});}
// An independently valid semantic body may be spliced onto a different valid metadata block.
const a=L.base,b={...a,source:2,version:5,seq:6,tree:['quote',['open']]};
const x=L.render(a),y=L.render(b),splice=L.join(x.slice(0,640+8*1280),y.slice(640+8*1280));
const observed=L.acquire(L.join(new Int16Array(320),splice,new Int16Array(640))).filter(h=>h.status==='ok');assert.equal(observed.length,1);assert.deepEqual(observed[0].packet,{...a,tree:b.tree});
// Two valid packets: same parser result, different claimed origin/authority is not authenticated.
const forgery=L.run('forged','bound');assert.equal(forgery.invalid,1);assert.equal(forgery.uniqueReceipts,0);
const output={schema:'mhac-native-relay-inspection-v1',wavFiles:rows.length,continuousMatches:rows.filter(r=>r.equal).length,continuousMismatches:rows.filter(r=>!r.equal),rows,splice:{metadata:a,body:b.tree,observed:observed[0].packet},forgery:{confirmed:forgery.confirmed,actualReceipts:forgery.uniqueReceipts}};
fs.writeFileSync(path.join(dir,'native-inspection.json'),JSON.stringify(output,null,2)+'\n');fs.writeFileSync(path.join(dir,'splice.wav'),L.wav(splice));console.log(JSON.stringify(output,null,2));
