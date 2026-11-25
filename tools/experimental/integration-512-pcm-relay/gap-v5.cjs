'use strict';
// Refs #512: independent two-frame association stress; exact v4 wire and decoder.
const v1=require('./relay.cjs'),v2=require('./bound-v2.cjs'),{decode}=require('./stream-v4.cjs');
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const dir=process.argv[2]||'gap-v5-output';fs.mkdirSync(dir,{recursive:true});const A=v1.base,B={...A,source:2,actor:3,event:2,seq:4,tree:['quote',['open']]},rows=[];
for(const gap of [0,80,160,240,640]){const pcm=v1.join(v2.render(A,.19),new Int16Array(gap),v2.render(B,.38),new Int16Array(40000)),events=decode(pcm,127).events,bytes=v1.wav(pcm);assert.equal(events.length,2);assert.ok(events.every(e=>e.status===(gap<=160?'ambiguous':'ok')));if(gap>=240)assert.deepEqual(events.map(e=>e.packet),[A,B]);fs.writeFileSync(path.join(dir,'gap-'+gap+'.wav'),bytes);rows.push({gap,sha256:crypto.createHash('sha256').update(bytes).digest('hex'),events});}
fs.writeFileSync(path.join(dir,'receipt.json'),JSON.stringify({rate:16000,rows},null,2)+'\n');console.log(JSON.stringify(rows.map(r=>({gap:r.gap,status:r.events.map(e=>e.status),release:r.events.map(e=>e.at)}))));
