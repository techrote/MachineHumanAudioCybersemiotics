'use strict';
// Interaction lane, Refs #456, synthetic only, Draft/HOLD. AI-assisted.
// Narrow independent four-symbol FSK adapter, NOT the Integration v6 wire.
// Uses the pinned parent freshness evaluator, 16 kHz clock. Shared synthetic
// offer/deadline context at both endpoints, not an authenticated wire field.
const RATE=16000,SLOT=3200,SYMBOL=400,FRAME=1600,H=20;
const key=p=>JSON.stringify([p.source,p.version,p.actor,p.event,p.seq,p.tree]);
const packet=(source,version,kind=0)=>({source,version,kind,actor:source+1,event:source,seq:version,tree:[['open','hold','close'][version-1]]});
const freq=n=>400+80*n;
const basis=Array.from({length:4},(_,n)=>Array.from({length:SYMBOL},(_,i)=>[Math.cos(2*Math.PI*freq(n)*i/RATE),Math.sin(2*Math.PI*freq(n)*i/RATE)]));
function render(p,seed,loss=false){
  const a=new Int16Array(SLOT),s=[p.kind,p.source-1,p.version-1];s.push((s[0]+2*s[1]+3*s[2])%4);
  let state=seed>>>0;
  for(let i=0;i<FRAME;i++){state=(Math.imul(1664525,state)+1013904223)>>>0;const n=s[Math.floor(i/SYMBOL)],j=i%SYMBOL;
    a[i]=(loss?0:Math.round(3000*basis[n][j][1]))+(state%161)-80;}
  return a;
}
function decode(pcm){
  const s=[];
  for(let j=0;j<4;j++){let powers=basis.map(b=>{let x=0,y=0;for(let i=0;i<SYMBOL;i++){const v=pcm[j*SYMBOL+i];x+=v*b[i][0];y+=v*b[i][1];}return x*x+y*y;});
    const m=Math.max(...powers),n=powers.indexOf(m);powers[n]=0;
    if(m<1e10||m<4*Math.max(...powers))return null;s.push(n);}
  if(s[0]>1||s[1]>1||s[2]>2||s[3]!==((s[0]+2*s[1]+3*s[2])%4))return null;
  return packet(s[1]+1,s[2]+1,s[0]);
}
const cases=['clean','revision','delayed','data-loss','ack-loss','forged'];
const modes=['baseline','sender','bilateral'];
function simulate(name,mode,ttl,seed){
  if(!cases.includes(name)||!modes.includes(mode)||!Number.isInteger(ttl)||ttl<1)throw Error('configuration');
  const offers=[[0,packet(1,1)],[0,packet(2,1)]];if(name==='revision')offers.push([2,packet(1,2)],[5,packet(2,2)]);
  const trace=[],pcm=new Int16Array(H*SLOT),records=new Map(),current=new Map(),received=new Set(),queue=[];
  const log=(at,type,x={})=>trace.push({at,type,...x});
  const metrics={data:0,ack:0,idle:0,retry:0,abandoned:0,lateStarts:0,invalid:0};
  function useful(rec,t){return t*SLOT+FRAME<rec.at+ttl*SLOT;}
  for(let t=0;t<H;t++){
    const at=t*SLOT,end=at+FRAME;
    for(const [when,p] of offers)if(when===t){const k=key(p);records.set(k,{p,at,ready:t,attempts:0,confirmed:false});current.set(p.source,k);log(at,'offer',{packet:p});}
    if(mode==='bilateral')for(let j=queue.length-1;j>=0;j--){const a=queue[j],r=records.get(key(a.p));if(!useful(r,t)||current.get(a.p.source)!==key(a.p)){queue.splice(j,1);metrics.abandoned++;log(at,'return-abandoned',{packet:a.p});}}
    const ret=queue.findIndex(a=>a.ready<=t);
    const data=[...records.values()].find(r=>!r.confirmed&&r.attempts<2&&r.ready<=t&&current.get(r.p.source)===key(r.p)&&(mode==='baseline'||useful(r,t)));
    let p=null,loss=false,origin='idle';
    if(name==='forged'&&t===1){p=packet(1,1,1);origin='fixture';}
    else if(ret>=0){p=queue.splice(ret,1)[0].p;origin='return';loss=name==='ack-loss'&&p.source===1&&!records.get(key(p)).ackLost;if(loss)records.get(key(p)).ackLost=true;}
    else if(data){p=data.p;origin='data';data.attempts++;data.ready=t+3;if(data.attempts>1)metrics.retry++;loss=(name==='data-loss'||name==='forged')&&p.source===1&&data.attempts===1;}
    if(!p){metrics.idle++;log(at,'idle');continue;}
    if(p.kind)metrics.ack++;else metrics.data++;
    const rec=records.get(key(p));if(!useful(rec,t))metrics.lateStarts++;
    log(at,'tx',{packet:p,origin,loss});
    const wave=render(p,seed+t*997,loss);pcm.set(wave,at);
    const d=decode(wave);if(!d){log(end,'refusal');continue;}
    const k=key(d);
    if(d.kind===0){const accepted=current.get(d.source)===k;log(end,'data-receipt',{packet:d,accepted});if(!accepted)continue;received.add(k);
      if(!queue.some(a=>key(a.p)===k))queue.push({p:{...d,kind:1},ready:t+(name==='delayed'?4:1)});
    }else{const r=records.get(k),accepted=!!r&&r.attempts>0&&!r.confirmed,genuine=received.has(k);
      if(accepted){r.confirmed=true;if(!genuine)metrics.invalid++;}
      log(end,'ack-receipt',{packet:d,accepted,evaluatorGenuine:genuine});
    }
  }
  return {name,mode,ttl,seed,samples:pcm.length,trace,pcm,metrics};
}
function qualify(freshness){
  let checks=0;const check=(b,m)=>{checks++;if(!b)throw Error(m);};
  for(let source=1;source<=2;source++)for(let version=1;version<=3;version++)for(let kind=0;kind<=1;kind++){
    const p=packet(source,version,kind);check(JSON.stringify(decode(render(p,7)))===JSON.stringify(p),'FSK roundtrip');check(decode(render(p,7,true))===null,'lost refusal');}
  const rows=[],specimens=[];
  for(const seed of [117,419,8191,27011])for(const name of cases)for(const ttl of [2,3,4,6,9])for(const mode of modes){
    const s=simulate(name,mode,ttl,seed),f=freshness(s.trace,s.samples,ttl*SLOT/RATE),m=f.totals;
    check(s.metrics.data+s.metrics.ack+s.metrics.idle===H,'slot accounting');
    check(m.genuine+m.falseBelief===m.believed,'belief partition');
    check(f.records.filter(x=>x.confirmed&&!x.genuine).length===s.metrics.invalid,'false acceptance');
    check(s.pcm.every(x=>Math.abs(x)<=3080),'PCM bound');
    if(mode==='bilateral')check(s.trace.filter(x=>x.type==='tx'&&x.origin!=='fixture').every(x=>{const offer=s.trace.find(o=>o.type==='offer'&&key(o.packet)===key(x.packet));return x.at+FRAME<offer.at+ttl*SLOT;}),'bilateral admission');
    const row={name,mode,ttl,seed,...m,...s.metrics};rows.push(row);
    if(seed===117&&ttl===3&&['revision','delayed','forged'].includes(name))specimens.push({row,trace:s.trace,pcm:s.pcm,intervals:f.timeline});
  }
  return {receipt:{schema:'mhac-interaction-narrow-fsk-deadlines-v1',parent:'77f8b63a7844d70a227e80ea96ae254478a82b11',parentBlob:'c459c6edd8446440adee6f4ee54ee405863d5b43',rate:RATE,slotSamples:SLOT,frameSamples:FRAME,checks,rows},specimens};
}
module.exports={simulate,qualify,render,decode};
if(require.main===module){
  const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
  const parent=path.join(__dirname,'evidence-freshness.cjs'),bytes=fs.readFileSync(parent);
  if(crypto.createHash('sha1').update('blob '+bytes.length+'\0').update(bytes).digest('hex')!=='c459c6edd8446440adee6f4ee54ee405863d5b43')throw Error('parent mismatch');
  const {receipt,specimens}=qualify(require(parent).freshness),out=process.argv[2]||'narrow-deadline-output';fs.mkdirSync(out,{recursive:true});
  receipt.stimuli=[];for(const {row,trace,pcm,intervals} of specimens){
    const stem=row.name+'-'+row.mode,b=Buffer.alloc(44+pcm.length*2);b.write('RIFF');b.writeUInt32LE(b.length-8,4);b.write('WAVEfmt ',8);b.writeUInt32LE(16,16);b.writeUInt16LE(1,20);b.writeUInt16LE(1,22);b.writeUInt32LE(RATE,24);b.writeUInt32LE(RATE*2,28);b.writeUInt16LE(2,32);b.writeUInt16LE(16,34);b.write('data',36);b.writeUInt32LE(pcm.length*2,40);pcm.forEach((v,i)=>b.writeInt16LE(Math.round(v/2),44+2*i));
    fs.writeFileSync(path.join(out,stem+'.wav'),b);fs.writeFileSync(path.join(out,stem+'.json'),JSON.stringify({row,trace,intervals},null,2));receipt.stimuli.push({file:stem+'.wav',gain:.5,sha256:crypto.createHash('sha256').update(b).digest('hex')});
  }
  fs.writeFileSync(path.join(out,'receipt.json'),JSON.stringify(receipt,null,2));
  const html='<!doctype html><meta charset=utf-8><title>Deadline relay replay</title><h1>Deadline relay replay</h1><p>Synthetic FSK stand-in. Start at low volume. No autoplay.</p><label>Deadline in 200 ms slots <select id=d><option>2</option><option selected>3</option><option>4</option><option>6</option><option>9</option></select></label><div id=v></div><script>const rows='+JSON.stringify(receipt.rows.filter(x=>x.seed===117))+';function draw(){v.innerHTML="<table border=1><tr><th>Case/policy</th><th>Genuine seconds</th><th>False seconds</th><th>DATA/ACK</th><th>Replay</th></tr>"+rows.filter(x=>x.ttl==+d.value).map(x=>{const s=x.name+"-"+x.mode;return "<tr><td>"+s+"</td><td>"+(x.genuine/16000).toFixed(3)+"</td><td>"+(x.falseBelief/16000).toFixed(3)+"</td><td>"+x.data+"/"+x.ack+"</td><td>"+(x.ttl===3&&["revision","delayed","forged"].includes(x.name)?"<audio controls preload=none src="+s+".wav></audio> <a href="+s+".json>trace</a>":"")+"</td></tr>"}).join("")+"</table>"}d.onchange=draw;draw()</script>';
  fs.writeFileSync(path.join(out,'index.html'),html);console.log(JSON.stringify(receipt));
}

// Executed V8 twice; identical receipt. Aggregate samples/counts:
// {"2/baseline":{"genuine":12800,"received":96000,"falseBelief":6400,"data":68,"ack":60,"idle":352,"invalid":4,"abandoned":0,"lateStarts":76},"2/sender":{"genuine":25600,"received":128000,"falseBelief":6400,"data":40,"ack":36,"idle":404,"invalid":4,"abandoned":0,"lateStarts":12},"2/bilateral":{"genuine":25600,"received":128000,"falseBelief":6400,"data":40,"ack":24,"idle":416,"invalid":4,"abandoned":12,"lateStarts":0},"3/baseline":{"genuine":38400,"received":204800,"falseBelief":19200,"data":68,"ack":60,"idle":352,"invalid":4,"abandoned":0,"lateStarts":48},"3/sender":{"genuine":38400,"received":204800,"falseBelief":19200,"data":56,"ack":52,"idle":372,"invalid":4,"abandoned":0,"lateStarts":28},"3/bilateral":{"genuine":57600,"received":230400,"falseBelief":19200,"data":56,"ack":28,"idle":396,"invalid":4,"abandoned":24,"lateStarts":0},"4/baseline":{"genuine":108800,"received":352000,"falseBelief":32000,"data":68,"ack":60,"idle":352,"invalid":4,"abandoned":0,"lateStarts":20},"4/sender":{"genuine":108800,"received":352000,"falseBelief":32000,"data":64,"ack":56,"idle":360,"invalid":4,"abandoned":0,"lateStarts":12},"4/bilateral":{"genuine":108800,"received":352000,"falseBelief":32000,"data":64,"ack":44,"idle":372,"invalid":4,"abandoned":12,"lateStarts":0},"6/baseline":{"genuine":352000,"received":646400,"falseBelief":57600,"data":68,"ack":60,"idle":352,"invalid":4,"abandoned":0,"lateStarts":0},"6/sender":{"genuine":352000,"received":646400,"falseBelief":57600,"data":68,"ack":60,"idle":352,"invalid":4,"abandoned":0,"lateStarts":0},"6/bilateral":{"genuine":352000,"received":646400,"falseBelief":57600,"data":68,"ack":60,"idle":352,"invalid":4,"abandoned":0,"lateStarts":0},"9/baseline":{"genuine":774400,"received":1068800,"falseBelief":96000,"data":68,"ack":60,"idle":352,"invalid":4,"abandoned":0,"lateStarts":0},"9/sender":{"genuine":774400,"received":1068800,"falseBelief":96000,"data":68,"ack":60,"idle":352,"invalid":4,"abandoned":0,"lateStarts":0},"9/bilateral":{"genuine":774400,"received":1068800,"falseBelief":96000,"data":68,"ack":60,"idle":352,"invalid":4,"abandoned":0,"lateStarts":0}}
