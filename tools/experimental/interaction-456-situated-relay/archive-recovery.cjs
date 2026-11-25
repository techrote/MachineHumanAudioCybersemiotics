'use strict';
// Refs #456, Interaction lane, synthetic-only Draft/HOLD, AI-assisted.
// Reconstruction of Run 013, not byte-identical recovery of unpublished source.
// Parent c0db9ebcada623ad466f30ff298df25706e187f7. Narrow FSK stand-in, not Integration wire.
const parent=require('./narrow-deadline-relay.cjs'),{freshness}=require('./evidence-freshness.cjs');
const RATE=16000,SLOT=3200,FRAME=1600,H=20;
const pins={'narrow-deadline-relay.cjs':'10ed127dd84aee591f1addfa02fd1e2931114d67','evidence-freshness.cjs':'c459c6edd8446440adee6f4ee54ee405863d5b43'};
const key=p=>JSON.stringify([p.source,p.version,p.actor,p.event,p.seq,p.tree]);
const packet=(source,version,kind=0)=>({source,version,kind,actor:source+1,event:source,seq:version,tree:[['open','hold','close'][version-1]]});
const cases=['clean','revision','delayed','data-loss','ack-loss','forged','churn'],modes=['baseline','bilateral','idle-archive','reserved-archive'];
function simulate(name,mode,ttl,seed,cap=3,life=8){
  if(!cases.includes(name)||!modes.includes(mode)||!Number.isInteger(ttl)||ttl<1||!Number.isInteger(cap)||cap<0||cap>16||!Number.isInteger(life)||life<1||life>20)throw Error('configuration');
  const offers=[[0,packet(1,1)],[0,packet(2,1)]];
  if(name==='revision')offers.push([2,packet(1,2)],[5,packet(2,2)]);
  if(name==='churn')offers.push([2,packet(1,2)],[3,packet(2,2)],[5,packet(1,3)],[6,packet(2,3)]);
  const trace=[],pcm=new Int16Array(H*SLOT),records=new Map(),current=new Map(),received=new Set(),queue=[],archive=[];
  const log=(at,type,x={})=>trace.push({at,type,...x});
  const metrics={data:0,ack:0,idle:0,retry:0,abandoned:0,lateStarts:0,invalid:0,archived:0,archiveTx:0,evicted:0,expired:0,maxArchive:0};
  const useful=(rec,t)=>t*SLOT+FRAME<rec.at+ttl*SLOT;
  for(let t=0;t<H;t++){
    const at=t*SLOT,end=at+FRAME;
    for(const [when,p] of offers)if(when===t){const k=key(p);records.set(k,{p,at,ready:t,attempts:0,confirmed:false});current.set(p.source,k);log(at,'offer',{packet:p});}
    for(let j=archive.length-1;j>=0;j--)if(archive[j].expires<=t){const q=archive.splice(j,1)[0];metrics.expired++;log(at,'archive-expired',{packet:q.p});}
    if(mode!=='baseline')for(let j=queue.length-1;j>=0;j--){const a=queue[j],r=records.get(key(a.p));
      if(!useful(r,t)||current.get(a.p.source)!==key(a.p)){
        queue.splice(j,1);metrics.abandoned++;
        if(!mode.endsWith('archive'))log(at,'return-abandoned',{packet:a.p});
        else{archive.push({...a,expires:t+life});metrics.archived++;log(at,'archive-enqueued',{packet:a.p,ready:a.ready,expires:t+life});
          if(archive.length>cap){const q=archive.shift();metrics.evicted++;log(at,'archive-evicted',{packet:q.p});}
          metrics.maxArchive=Math.max(metrics.maxArchive,archive.length);}
      }
    }
    const ret=queue.findIndex(a=>a.ready<=t),old=archive.findIndex(a=>a.ready<=t);
    const data=[...records.values()].find(r=>!r.confirmed&&r.attempts<2&&r.ready<=t&&current.get(r.p.source)===key(r.p)&&(mode==='baseline'||useful(r,t)));
    let p=null,loss=false,origin='idle';
    if(name==='forged'&&t===1){p=packet(1,1,1);origin='fixture';}
    else if(ret>=0){p=queue.splice(ret,1)[0].p;origin='return';}
    else if(old>=0&&(!data||(mode==='reserved-archive'&&t%4===0))){p=archive.splice(old,1)[0].p;origin='archive';metrics.archiveTx++;log(at,'archive-service',{packet:p,displacedData:!!data});}
    else if(data){p=data.p;origin='data';data.attempts++;data.ready=t+3;if(data.attempts>1)metrics.retry++;loss=(name==='data-loss'||name==='forged')&&p.source===1&&data.attempts===1;}
    if(!p){metrics.idle++;log(at,'idle');continue;}
    const rec=records.get(key(p));
    if(origin==='return'||origin==='archive'){loss=name==='ack-loss'&&p.source===1&&!rec.ackLost;if(loss)rec.ackLost=true;}
    if(p.kind)metrics.ack++;else metrics.data++;
    if(!useful(rec,t))metrics.lateStarts++;
    log(at,'tx',{packet:p,origin,loss});
    const wave=parent.render(p,seed+t*997,loss);pcm.set(wave,at);
    const d=parent.decode(wave);if(!d){log(end,'refusal');continue;}
    const k=key(d);
    if(d.kind===0){const accepted=current.get(d.source)===k;log(end,'data-receipt',{packet:d,accepted});if(!accepted)continue;
      received.add(k);if(!queue.some(a=>key(a.p)===k))queue.push({p:{...d,kind:1},ready:t+(name==='delayed'?4:1)});
    }else{
      const r=records.get(k),accepted=!!r&&r.attempts>0&&!r.confirmed,genuine=received.has(k);
      if(accepted){r.confirmed=true;if(!genuine)metrics.invalid++;}
      log(end,'ack-receipt',{packet:d,accepted,evaluatorGenuine:genuine});
    }
  }
  metrics.archivePending=archive.length;return {name,mode,ttl,seed,cap,life,samples:pcm.length,trace,pcm,metrics};
}
function qualify(){
  let checks=0;const check=(b,m)=>{checks++;if(!b)throw Error(m);};
  const rows=[],specimens=[],aggregate={};let baselineMatches=0;
  const seeds=[419,27011],ttls=[2,3,4,6];
  function evaluate(s){const f=freshness(s.trace,s.samples,s.ttl*SLOT/RATE),m=f.totals;
    check(s.metrics.data+s.metrics.ack+s.metrics.idle===H,'slot accounting');
    check(s.metrics.archived===s.metrics.archiveTx+s.metrics.evicted+s.metrics.expired+s.metrics.archivePending,'archive conservation');
    check(s.metrics.maxArchive<=s.cap,'queue bound');
    check(f.records.filter(x=>x.confirmed&&!x.genuine).length===s.metrics.invalid,'false accounting');
    check(s.pcm.every(x=>Math.abs(x)<=3080),'PCM bound');
    if(s.mode==='idle-archive')check(!s.trace.some(e=>e.type==='archive-service'&&e.displacedData),'strict priority');
    return {f,row:{name:s.name,mode:s.mode,ttl:s.ttl,seed:s.seed,...m,...s.metrics,historicalGenuine:f.records.filter(x=>x.confirmed&&x.genuine).length}};
  }
  for(const seed of seeds)for(const name of cases)for(const ttl of ttls)for(const mode of modes){
    const s=simulate(name,mode,ttl,seed),{f,row}=evaluate(s);
    if(name!=='churn'&&(mode==='baseline'||mode==='bilateral')){
      const p=parent.simulate(name,mode,ttl,seed);
      check(JSON.stringify(s.trace)===JSON.stringify(p.trace),'parent trace');
      check(s.pcm.every((v,i)=>v===p.pcm[i]),'parent PCM');
      check(Object.keys(p.metrics).every(k=>p.metrics[k]===s.metrics[k]),'parent metrics');baselineMatches++;
    }
    rows.push(row);
    const k=ttl+'/'+mode,a=aggregate[k]??(aggregate[k]={sessions:0,genuine:0,received:0,falseBelief:0,historicalGenuine:0,ack:0,data:0,archiveTx:0,evicted:0,expired:0});
    a.sessions++;for(const k of Object.keys(a))if(k!=='sessions')a[k]+=row[k];
    if(seed===seeds[0]&&ttl===3&&['revision','delayed','forged','churn'].includes(name))specimens.push({row,trace:s.trace,pcm:s.pcm,intervals:f.timeline});
  }
  const paired=ttls.map(ttl=>{
    const rs=rows.filter(x=>x.ttl===ttl&&x.mode==='bilateral'),out={ttl,pairs:rs.length,idleCurrentLoss:0,idleCurrentGain:0,idleReceivedLoss:0,idleHistoryGain:0,reservedCurrentLoss:0};
    for(const b of rs){const get=m=>rows.find(x=>x.ttl===ttl&&x.seed===b.seed&&x.name===b.name&&x.mode===m),i=get('idle-archive'),r=get('reserved-archive');
      if(i.genuine<b.genuine)out.idleCurrentLoss++;if(i.genuine>b.genuine)out.idleCurrentGain++;if(i.received<b.received)out.idleReceivedLoss++;if(i.historicalGenuine>b.historicalGenuine)out.idleHistoryGain++;if(r.genuine<i.genuine)out.reservedCurrentLoss++;
    }return out;
  });
  const sensitivity=[];
  for(const cap of [0,1,3])for(const life of [2,8])for(const name of ['revision','delayed','churn']){
    const s=simulate(name,'idle-archive',3,8191,cap,life),{row}=evaluate(s);sensitivity.push({cap,life,...row});
    if(cap===0){const b=simulate(name,'bilateral',3,8191),f=freshness(b.trace,b.samples,3*SLOT/RATE);check(row.genuine===f.totals.genuine&&row.received===f.totals.received&&row.archiveTx===0,'zero capacity control');}
  }
  return {receipt:{schema:'mhac-interaction-archive-recovery-v1',parentRef:'c0db9ebcada623ad466f30ff298df25706e187f7',pins,rate:RATE,slotSamples:SLOT,frameSamples:FRAME,horizonSamples:H*SLOT,seeds,ttls,checks,baselineMatches,rows,aggregate,paired,sensitivity},specimens};
}
module.exports={simulate,qualify};
if(require.main===module){
  const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
  for(const [file,sha] of Object.entries(pins)){const b=fs.readFileSync(path.join(__dirname,file));if(crypto.createHash('sha1').update('blob '+b.length+'\0').update(b).digest('hex')!==sha)throw Error('parent mismatch '+file);}
  const {receipt,specimens}=qualify(),out=process.argv[2]||'archive-recovery-output';fs.mkdirSync(out,{recursive:true});receipt.stimuli=[];
  for(const {row,trace,pcm,intervals} of specimens){
    const stem=row.name+'-'+row.mode,b=Buffer.alloc(44+pcm.length*2);b.write('RIFF');b.writeUInt32LE(b.length-8,4);b.write('WAVEfmt ',8);b.writeUInt32LE(16,16);b.writeUInt16LE(1,20);b.writeUInt16LE(1,22);b.writeUInt32LE(RATE,24);b.writeUInt32LE(RATE*2,28);b.writeUInt16LE(2,32);b.writeUInt16LE(16,34);b.write('data',36);b.writeUInt32LE(pcm.length*2,40);pcm.forEach((v,i)=>b.writeInt16LE(Math.round(v/2),44+2*i));
    fs.writeFileSync(path.join(out,stem+'.wav'),b);fs.writeFileSync(path.join(out,stem+'.json'),JSON.stringify({row,trace,intervals},null,2));receipt.stimuli.push({file:stem+'.wav',gain:.5,sha256:crypto.createHash('sha256').update(b).digest('hex')});
  }
  fs.writeFileSync(path.join(out,'receipt.json'),JSON.stringify(receipt,null,2));
  const html='<!doctype html><meta charset=utf-8><title>Archival dialogue</title><style>body{font:16px system-ui;max-width:1100px;margin:2em auto;padding:1em}table{border-collapse:collapse}td,th{border:1px solid #999;padding:.4em}audio{width:240px}</style><h1>Archival dialogue recovery</h1><p>Synthetic FSK. Start at low volume; no autoplay. Historical knowledge is not current knowledge.</p><label>Deadline slots <select id="d"><option>2</option><option selected>3</option><option>4</option><option>6</option></select></label> <label>Case <select id="c">'+cases.map(x=>'<option>'+x+'</option>').join('')+'</select></label><div id="v"></div><script>const rows='+JSON.stringify(receipt.rows.filter(x=>x.seed===419))+';const d=document.getElementById("d"),c=document.getElementById("c"),v=document.getElementById("v");function draw(){v.innerHTML="<table><tr><th>Policy</th><th>Current confirmed s</th><th>All genuine confirmations</th><th>Received s</th><th>Archive TX / evicted / expired</th><th>Replay</th></tr>"+rows.filter(x=>x.ttl==+d.value&&x.name===c.value).map(x=>{const s=x.name+"-"+x.mode;return "<tr><td>"+x.mode+"</td><td>"+(x.genuine/16000).toFixed(3)+"</td><td>"+x.historicalGenuine+"</td><td>"+(x.received/16000).toFixed(3)+"</td><td>"+x.archiveTx+"/"+x.evicted+"/"+x.expired+"</td><td>"+(x.ttl===3&&["revision","delayed","forged","churn"].includes(x.name)?"<audio controls preload=none src="+s+".wav></audio> <a href="+s+".json>trace</a>":"")+"</td></tr>"}).join("")+"</table>"}d.onchange=draw;c.onchange=draw;draw()</script>';fs.writeFileSync(path.join(out,'index.html'),html);console.log(JSON.stringify({checks:receipt.checks,aggregate:receipt.aggregate,paired:receipt.paired}));
}

// Executed twice in V8, identical receipt. Native CLI not executed at publication.
// {"checks":1578,"rows":224,"baselineMatches":96,"aggregate":{"2/baseline":{"sessions":14,"genuine":9600,"received":60800,"falseBelief":3200,"historicalGenuine":36,"ack":40,"data":44,"archiveTx":0,"evicted":0,"expired":0},"2/bilateral":{"sessions":14,"genuine":22400,"received":99200,"falseBelief":3200,"historicalGenuine":14,"ack":18,"data":30,"archiveTx":0,"evicted":0,"expired":0},"2/idle-archive":{"sessions":14,"genuine":22400,"received":99200,"falseBelief":3200,"historicalGenuine":24,"ack":28,"data":30,"archiveTx":10,"evicted":0,"expired":0},"2/reserved-archive":{"sessions":14,"genuine":22400,"received":99200,"falseBelief":3200,"historicalGenuine":24,"ack":28,"data":30,"archiveTx":10,"evicted":0,"expired":0},"3/baseline":{"sessions":14,"genuine":25600,"received":131200,"falseBelief":9600,"historicalGenuine":36,"ack":40,"data":44,"archiveTx":0,"evicted":0,"expired":0},"3/bilateral":{"sessions":14,"genuine":38400,"received":153600,"falseBelief":9600,"historicalGenuine":16,"ack":20,"data":40,"archiveTx":0,"evicted":0,"expired":0},"3/idle-archive":{"sessions":14,"genuine":38400,"received":153600,"falseBelief":9600,"historicalGenuine":34,"ack":38,"data":40,"archiveTx":18,"evicted":0,"expired":0},"3/reserved-archive":{"sessions":14,"genuine":38400,"received":150400,"falseBelief":9600,"historicalGenuine":32,"ack":36,"data":38,"archiveTx":16,"evicted":0,"expired":0},"4/baseline":{"sessions":14,"genuine":70400,"received":217600,"falseBelief":16000,"historicalGenuine":36,"ack":40,"data":44,"archiveTx":0,"evicted":0,"expired":0},"4/bilateral":{"sessions":14,"genuine":73600,"received":227200,"falseBelief":16000,"historicalGenuine":26,"ack":30,"data":44,"archiveTx":0,"evicted":0,"expired":0},"4/idle-archive":{"sessions":14,"genuine":73600,"received":227200,"falseBelief":16000,"historicalGenuine":36,"ack":40,"data":44,"archiveTx":10,"evicted":0,"expired":0},"4/reserved-archive":{"sessions":14,"genuine":70400,"received":220800,"falseBelief":16000,"historicalGenuine":36,"ack":40,"data":44,"archiveTx":12,"evicted":0,"expired":0},"6/baseline":{"sessions":14,"genuine":217600,"received":390400,"falseBelief":28800,"historicalGenuine":36,"ack":40,"data":44,"archiveTx":0,"evicted":0,"expired":0},"6/bilateral":{"sessions":14,"genuine":220800,"received":400000,"falseBelief":28800,"historicalGenuine":34,"ack":38,"data":46,"archiveTx":0,"evicted":0,"expired":0},"6/idle-archive":{"sessions":14,"genuine":220800,"received":400000,"falseBelief":28800,"historicalGenuine":38,"ack":42,"data":46,"archiveTx":4,"evicted":0,"expired":0},"6/reserved-archive":{"sessions":14,"genuine":214400,"received":393600,"falseBelief":28800,"historicalGenuine":38,"ack":42,"data":46,"archiveTx":4,"evicted":0,"expired":0}},"paired":[{"ttl":2,"pairs":14,"idleCurrentLoss":0,"idleCurrentGain":0,"idleReceivedLoss":0,"idleHistoryGain":6,"reservedCurrentLoss":0},{"ttl":3,"pairs":14,"idleCurrentLoss":0,"idleCurrentGain":0,"idleReceivedLoss":0,"idleHistoryGain":12,"reservedCurrentLoss":0},{"ttl":4,"pairs":14,"idleCurrentLoss":0,"idleCurrentGain":0,"idleReceivedLoss":0,"idleHistoryGain":6,"reservedCurrentLoss":2},{"ttl":6,"pairs":14,"idleCurrentLoss":0,"idleCurrentGain":0,"idleReceivedLoss":0,"idleHistoryGain":2,"reservedCurrentLoss":2}],"sensitivity":[{"name":"revision","cap":0,"life":2,"genuine":8000,"historicalGenuine":3,"evicted":1,"expired":0,"archiveTx":0},{"name":"delayed","cap":0,"life":2,"genuine":0,"historicalGenuine":0,"evicted":2,"expired":0,"archiveTx":0},{"name":"churn","cap":0,"life":2,"genuine":4800,"historicalGenuine":3,"evicted":3,"expired":0,"archiveTx":0},{"name":"revision","cap":0,"life":8,"genuine":8000,"historicalGenuine":3,"evicted":1,"expired":0,"archiveTx":0},{"name":"delayed","cap":0,"life":8,"genuine":0,"historicalGenuine":0,"evicted":2,"expired":0,"archiveTx":0},{"name":"churn","cap":0,"life":8,"genuine":4800,"historicalGenuine":3,"evicted":3,"expired":0,"archiveTx":0},{"name":"revision","cap":1,"life":2,"genuine":8000,"historicalGenuine":3,"evicted":0,"expired":1,"archiveTx":0},{"name":"delayed","cap":1,"life":2,"genuine":0,"historicalGenuine":1,"evicted":1,"expired":0,"archiveTx":1},{"name":"churn","cap":1,"life":2,"genuine":4800,"historicalGenuine":4,"evicted":0,"expired":2,"archiveTx":1},{"name":"revision","cap":1,"life":8,"genuine":8000,"historicalGenuine":4,"evicted":0,"expired":0,"archiveTx":1},{"name":"delayed","cap":1,"life":8,"genuine":0,"historicalGenuine":1,"evicted":1,"expired":0,"archiveTx":1},{"name":"churn","cap":1,"life":8,"genuine":4800,"historicalGenuine":4,"evicted":2,"expired":0,"archiveTx":1},{"name":"revision","cap":3,"life":2,"genuine":8000,"historicalGenuine":3,"evicted":0,"expired":1,"archiveTx":0},{"name":"delayed","cap":3,"life":2,"genuine":0,"historicalGenuine":1,"evicted":0,"expired":1,"archiveTx":1},{"name":"churn","cap":3,"life":2,"genuine":4800,"historicalGenuine":4,"evicted":0,"expired":2,"archiveTx":1},{"name":"revision","cap":3,"life":8,"genuine":8000,"historicalGenuine":4,"evicted":0,"expired":0,"archiveTx":1},{"name":"delayed","cap":3,"life":8,"genuine":0,"historicalGenuine":2,"evicted":0,"expired":0,"archiveTx":2},{"name":"churn","cap":3,"life":8,"genuine":4800,"historicalGenuine":6,"evicted":0,"expired":0,"archiveTx":3}],"specimens":16,"peak":3080}
