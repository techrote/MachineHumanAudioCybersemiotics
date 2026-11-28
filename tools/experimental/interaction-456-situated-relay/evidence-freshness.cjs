'use strict';
// Interaction lane, Refs #456; synthetic only. AI-assisted, not independently reviewed.
// Retrospective deadline evaluation of actual Integration v6 PCM callbacks.
// Obtain four files at pinned ref; run node evidence-freshness.cjs PINNED_DIR OUT_DIR.
// No scheduler changes, no human claims. Offer-relative deadlines and exact sample clock.
const REF='693d17609df1fd5175ec4040fd701c7451e6c666', BLOBS={"relay.cjs":"3ba457f85f496e4d57d9789a2dc3b7d68fe2c071","bound-v2.cjs":"2aa2905d4f4d756276814d5ca941c02c51e63f97","stream-v4.cjs":"31769f808469b4416412be25a41eb238bfc1fdde","deadline-v6.cjs":"a5cda47d4ccdbe705c27cd1580f9b946236e8864"};
const RATE=16000, deadlines=[2,4,6,8,12], modes=[['zero',0],['fixed',640],['adaptive','adaptive']], cases=['clean','revision','forged','delayed'];
const key=p=>JSON.stringify([p.source,p.version,p.actor,p.event,p.seq,p.tree]);
function freshness(trace,horizon,seconds){
  const ttl=seconds*RATE, records=new Map(), current=new Map(), received=new Set();
  const totals={eligible:0,received:0,believed:0,genuine:0,falseBelief:0,lateAck:0,staleAck:0,acceptedAck:0};
  const timeline=[];let last=0;
  function advance(to){
    if(to<last||to>horizon)throw Error('nonmonotonic trace');
    for(const k of current.values()){
      const rec=records.get(k),end=Math.min(to,rec.offer+ttl),dt=Math.max(0,end-last);
      if(!dt)continue;
      totals.eligible+=dt;
      if(received.has(k))totals.received+=dt;
      if(rec.confirmed){totals.believed+=dt;if(rec.genuine)totals.genuine+=dt;else totals.falseBelief+=dt;}
      timeline.push({start:last,end,source:rec.packet.source,version:rec.packet.version,received:received.has(k),confirmed:rec.confirmed,genuine:rec.genuine});
    }
    last=to;
  }
  for(const e of trace){
    advance(e.at);
    if(e.type==='offer'){const k=key(e.packet);if(records.has(k))throw Error('duplicate offer');records.set(k,{packet:e.packet,offer:e.at,confirmed:false,genuine:false});current.set(e.packet.source,k);}
    else if(e.type==='data-receipt'&&e.accepted){received.add(key(e.packet));}
    else if(e.type==='ack-receipt'&&e.accepted){
      const k=key(e.packet),rec=records.get(k);if(!rec||rec.confirmed)throw Error('bad accepted ACK');
      rec.confirmed=true;rec.genuine=received.has(k);rec.ack=e.at;totals.acceptedAck++;
      if(e.at>=rec.offer+ttl)totals.lateAck++;
      if(current.get(e.packet.source)!==k)totals.staleAck++;
      if(rec.genuine!==e.evaluatorGenuine)throw Error('receipt truth mismatch');
    }
  }
  advance(horizon);
  if(totals.genuine+totals.falseBelief!==totals.believed||totals.received>totals.eligible||totals.believed>totals.eligible||totals.genuine>totals.received)throw Error('interval accounting');
  return {totals,timeline,records:[...records.values()]};
}
function qualify(simulate){
  let checks=0;const check=(v,m)=>{checks++;if(!v)throw Error(m);};
  const p={source:1,version:1,actor:2,event:1,seq:1,tree:['open']},q={...p,version:2};
  const synthetic=[{at:0,type:'offer',packet:p},{at:16000,type:'data-receipt',packet:p,accepted:true},{at:32000,type:'ack-receipt',packet:p,accepted:true,evaluatorGenuine:true},{at:48000,type:'offer',packet:q},{at:64000,type:'ack-receipt',packet:q,accepted:true,evaluatorGenuine:false},{at:80000,type:'data-receipt',packet:q,accepted:true}];
  const k=freshness(synthetic,96000,4).totals;
  check(k.eligible===96000&&k.received===48000&&k.believed===48000&&k.genuine===16000&&k.falseBelief===32000,'known-answer integral');
  const short=freshness(synthetic,96000,2).totals;check(short.genuine===0&&short.lateAck===1&&short.falseBelief===16000,'deadline equality');
  const rows=[],sessions=[];
  for(const name of cases)for(const [mode,guard] of modes){
    const s=simulate(name,'ack-first',guard,511,'absolute');
    check(s.samples===320000,'common horizon');
    const metrics=deadlines.map(seconds=>{
      const f=freshness(s.trace,s.samples,seconds),t=f.totals;
      check(t.acceptedAck===s.metrics.confirmations,'confirmed accounting');
      check(f.records.filter(r=>r.genuine).length===s.metrics.genuineConfirmations,'genuine accounting');
      check(f.records.filter(r=>r.confirmed&&!r.genuine).length===s.metrics.invalid,'false accounting');
      check(f.timeline.reduce((a,x)=>a+x.end-x.start,0)===t.eligible,'interval coverage');
      return {seconds,...t};
    });
    const unrestricted=freshness(s.trace,s.samples,20);
    check(unrestricted.records.length===s.metrics.offered,'offer accounting');
    for(let i=1;i<metrics.length;i++)for(const f of ['eligible','received','believed','genuine','falseBelief'])check(metrics[i][f]>=metrics[i-1][f],'nested integral '+f);
    rows.push({name,mode,upstream:s.metrics,metrics,acks:unrestricted.records.filter(r=>r.confirmed).map(r=>({source:r.packet.source,version:r.packet.version,offer:r.offer,ack:r.ack,genuine:r.genuine}))});
    sessions.push({name,mode,pcm:s.pcm,trace:s.trace,metrics,intervals:deadlines.map(seconds=>({seconds,...freshness(s.trace,s.samples,seconds)}))});
  }
  return {receipt:{schema:'mhac-interaction-evidence-freshness-v1',ref:REF,blobs:BLOBS,sampleRate:RATE,checks,rows},sessions};
}
module.exports={freshness,qualify,REF,BLOBS};
if(require.main===module){
  const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
  if(!process.argv[2]||!process.argv[3])throw Error('usage: node evidence-freshness.cjs PINNED_DIR OUT_DIR');
  const src=path.resolve(process.argv[2]),out=path.resolve(process.argv[3]);
  for(const [n,sha] of Object.entries(BLOBS)){const b=fs.readFileSync(path.join(src,n)),actual=crypto.createHash('sha1').update('blob '+b.length+String.fromCharCode(0)).update(b).digest('hex');if(actual!==sha)throw Error('wrong source blob '+n);}
  const {simulate}=require(path.join(src,'deadline-v6.cjs')),{wav}=require(path.join(src,'relay.cjs'));
  const {receipt,sessions}=qualify(simulate);fs.mkdirSync(out,{recursive:true});receipt.stimuli=[];
  for(const {pcm,...s} of sessions){const stem=s.name+'-'+s.mode,raw=wav(pcm),preview=wav(Int16Array.from(pcm,x=>Math.round(x/2)));for(const [suffix,b] of [['raw',raw],['preview',preview]]){const file=stem+'-'+suffix+'.wav';fs.writeFileSync(path.join(out,file),b);receipt.stimuli.push({file,sha256:crypto.createHash('sha256').update(b).digest('hex'),gain:suffix==='raw'?1:.5});}fs.writeFileSync(path.join(out,stem+'.json'),JSON.stringify(s,null,2));}
  fs.writeFileSync(path.join(out,'receipt.json'),JSON.stringify(receipt,null,2));
  const html='<!doctype html><meta charset="utf-8"><title>Evidence freshness replay</title><style>body{font:16px system-ui;max-width:1000px;margin:2em auto;padding:1em}table{border-collapse:collapse}td,th{padding:.4em;border:1px solid #888}audio{width:260px}</style><h1>Evidence freshness replay</h1><p>Synthetic observations. Low device volume; opt-in previews with shared half amplitude. Deadline is measured, not enforced.</p><label>Offer-relative deadline <select id="d">'+deadlines.map(x=>'<option>'+x+'</option>').join('')+'</select></label><div id="view"></div><script>const rows='+JSON.stringify(receipt.rows)+';function draw(){let h="<table><tr><th>Case / mode</th><th>Eligible s</th><th>Received s</th><th>Genuine confirmed s</th><th>False belief s</th><th>Preview / trace</th></tr>";for(const r of rows){const m=r.metrics.find(x=>x.seconds==+d.value),s=r.name+"-"+r.mode;h+="<tr><td>"+s+"</td>"+["eligible","received","genuine","falseBelief"].map(k=>"<td>"+(m[k]/16000).toFixed(3)+"</td>").join("")+"<td><audio controls preload=none src="+s+"-preview.wav></audio> <a href="+s+".json>trace</a></td></tr>"}view.innerHTML=h+"</table>"}d.onchange=draw;draw()</script>';
  fs.writeFileSync(path.join(out,'index.html'),html);console.log(JSON.stringify(receipt));
}
