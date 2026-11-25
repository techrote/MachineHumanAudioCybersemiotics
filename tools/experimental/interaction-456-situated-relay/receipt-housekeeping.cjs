'use strict';
// Refs #456 / Draft #457. Synthetic, aligned PCM; not Grammar wire compatible.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const parent='d70aa68fb60608efab8ff34089e8e3dc66fe2d11',grammar='7f06ab778df0c3d43f2bcad8bda5a7a70acb8d68';
const RATE=16000,N=400,SLOT=3200,H=24,kinds=['request','provisional','positive','terminal-negative','ack-positive','ack-negative'],policies=['none','idle-repair','repair-first'];
const basis=Array.from({length:4},(_,k)=>Array.from({length:N},(_,i)=>[Math.cos(2*Math.PI*(400+80*k)*i/RATE),Math.sin(2*Math.PI*(400+80*k)*i/RATE)]));
const key=p=>`${p.address}/${p.tag}`,terminal=p=>['positive','terminal-negative'].includes(p.kind),ack=p=>({...p,kind:p.kind==='positive'?'ack-positive':'ack-negative'});
function render(p,seed,lost){const n=p.kind==='current'?63:18*p.address+6*p.tag+kinds.indexOf(p.kind),a=[n%4,(n>>2)%4,(n>>4)%4];a.push((a[0]+2*a[1]+3*a[2])%4);let s=seed>>>0;const w=new Int16Array(SLOT);for(let j=0;j<4;j++)for(let i=0;i<N;i++){s=(Math.imul(s,1664525)+1013904223)>>>0;w[j*N+i]=Math.round((lost&&j===1?0:2600*basis[a[j]][i][1])+(s%81-40));}return w;}
function decode(w){const a=[];for(let j=0;j<4;j++){const scores=basis.map(b=>{let x=0,y=0;for(let i=0;i<N;i++){x+=w[j*N+i]*b[i][0];y+=w[j*N+i]*b[i][1];}return x*x+y*y;});const m=Math.max(...scores),k=scores.indexOf(m);scores[k]=0;if(m<1e10||m<4*Math.max(...scores))return null;a.push(k);}if(a[3]!==((a[0]+2*a[1]+3*a[2])%4))return null;const n=a[0]+4*a[1]+16*a[2];if(n===63)return {kind:'current'};if(n>=36)return null;return {kind:kinds[n%6],address:Math.floor(n/18),tag:Math.floor(n%18/6)};}
function simulate(c,policy,keep=false){assert(policies.includes(policy));const R=[0,1].map(()=>({attempts:0,open:null,next:0,stopped:false,positive:false})),S=new Map(),admitted=new Map(),queue=[],seen=new Set(),trace=[],pcm=keep?new Int16Array(H*SLOT):null;let requests=0,bodies=0,current=0,retries=0,peak=0,duplicate=0;const log=(slot,type,data={})=>trace.push({slot,type,...data});
 for(let t=0;t<H;t++){
  for(const r of R)if(r.open&&t>r.open.until){r.open=null;r.next=t;}
  let p=null,reason='idle';
  if(c.traffic.includes(t)){p={kind:'current'};reason='reservation';}
  else if(bodies<c.budget){
   const eligible=R.map((r,address)=>({...r,address})).filter(r=>!r.open&&!r.stopped&&r.attempts<3&&r.next<=t).sort((a,b)=>a.attempts-b.attempts||a.address-b.address);
   const repair=[...S.values()].filter(s=>s.pending&&s.sent!==null&&s.attempts<2&&t>=s.sent+2).sort((a,b)=>a.sent-b.sent||a.p.address-b.p.address)[0];
   if(queue.length){p=queue.shift();reason='queued';}
   else if(policy!=='none'&&repair&&bodies+2<=c.budget&&(policy==='repair-first'||requests>=3||!eligible.length)){p=repair.p;reason='repair';retries++;}
   else if(requests<3&&eligible.length){const a=eligible[0].address,r=R[a];p={kind:'request',address:a,tag:r.attempts++};r.open={tag:p.tag,until:t+5};requests++;reason='enquiry';}
  }
  if(!p){log(t,'idle');continue;}
  const first=!seen.has(`${p.address}/${p.kind}`);seen.add(`${p.address}/${p.kind}`);
  const lost=p.kind!=='current'&&((c.loss==='ack-first'&&p.kind==='ack-negative'&&first)||(c.loss==='ack-all'&&p.kind==='ack-negative')||(c.loss==='reply-first'&&terminal(p)&&first));
  if(p.kind!=='current')bodies++;
  if(terminal(p)){const s=S.get(key(p));assert(s&&s.pending);s.sent=t;s.attempts++;}
  const w=render(p,c.seed+t*997,lost),d=decode(w);assert.deepEqual(d,lost?null:p);if(pcm)pcm.set(w,t*SLOT);for(let i=0;i<4*N;i++)peak=Math.max(peak,Math.abs(w[i]));log(t,'tx',{p,reason,lost,decoded:d,receiptSample:t*SLOT+4*N});if(!d)continue;
  if(d.kind==='current'){current++;continue;}
  const r=R[d.address],k=key(d);
  if(d.kind==='request'){
   const found=d.address!==c.absent&&t>=c.delay&&t<c.delay+c.retention,reply={...d,kind:found?'positive':d.address===c.absent?'terminal-negative':'provisional'};
   if(terminal(reply)){assert(!S.has(k));S.set(k,{p:reply,pending:true,sent:null,attempts:0});}queue.push(reply);log(t,'lookup',{reply,found});
  }else if(d.kind.startsWith('ack-')){
   const s=S.get(k);if(s?.pending&&ack(s.p).kind===d.kind){assert.equal(admitted.get(k),s.p.kind);s.pending=false;log(t,'release',{key:k,kind:s.p.kind});}
  }else if(terminal(d)&&admitted.get(k)===d.kind){duplicate++;queue.push(ack(d));log(t,'duplicate',{key:k});}
  else if(r.open&&r.open.tag===d.tag&&t<=r.open.until){r.open=null;r.next=t+2;if(terminal(d)){admitted.set(k,d.kind);r.stopped=true;r.positive=d.kind==='positive';queue.push(ack(d));}log(t,'admit',{key:k,kind:d.kind});}
  else log(t,'reject-stale',{key:k,kind:d.kind});
 }
 const sender=[...S.values()],m={positive:+R.some(r=>r.positive),bodies,current,requests,retries,duplicate,pending:sender.filter(s=>s.pending).length,unconfirmedAdmitted:sender.filter(s=>s.pending&&admitted.has(key(s.p))).length,released:sender.filter(s=>!s.pending).length,queued:queue.length};
 assert(bodies<=c.budget&&requests<=3&&current===c.traffic.length&&peak<=2640);assert(sender.every(s=>s.attempts<=2));assert.equal(m.released,trace.filter(e=>e.type==='release').length);return {c,policy,m,trace,sender,peak,pcm};}
function wav(pcm){const b=Buffer.alloc(44+2*pcm.length);b.write('RIFF');b.writeUInt32LE(b.length-8,4);b.write('WAVEfmt ',8);b.writeUInt32LE(16,16);b.writeUInt16LE(1,20);b.writeUInt16LE(1,22);b.writeUInt32LE(RATE,24);b.writeUInt32LE(2*RATE,28);b.writeUInt16LE(2,32);b.writeUInt16LE(16,34);b.write('data',36);b.writeUInt32LE(2*pcm.length,40);pcm.forEach((v,i)=>b.writeInt16LE(Math.round(v*.5),44+2*i));return b;}
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
function run(out){fs.mkdirSync(out,{recursive:true});const rows=[],stats={},pairs={},specimens=[];let peak=0;
 for(let n=0;n<36;n++){const p={kind:kinds[n%6],address:Math.floor(n/18),tag:Math.floor(n%18/6)};assert.deepEqual(decode(render(p,91,false)),p);assert.equal(decode(render(p,91,true)),null);}
 for(const seed of [221031,221033])for(const absent of [0,1])for(const delay of [2,5,8,11,14])for(const retention of [3,8])for(const loss of ['none','ack-first','ack-all','reply-first'])for(const traffic of [[2,6,10],[1,2,7,8,13,14]])for(const budget of [6,8,10]){
  const c={seed,absent,delay,retention,loss,traffic,budget},group=policies.map(p=>simulate(c,p));for(const z of group){const {pcm,...row}=z;rows.push(row);peak=Math.max(peak,z.peak);const s=stats[budget+'/'+z.policy]??={runs:0};s.runs++;for(const [k,v] of Object.entries(z.m))s[k]=(s[k]||0)+v;}
  for(const z of group.slice(1)){const a=group[0].m,b=z.m,s=pairs[budget+'/'+z.policy]??={equalBodies:0,positiveWin:0,positiveLoss:0,pendingWin:0,pendingLoss:0,equalBodiesPendingWin:0};s.equalBodies+=+(a.bodies===b.bodies);s.positiveWin+=+(b.positive>a.positive);s.positiveLoss+=+(b.positive<a.positive);s.pendingWin+=+(b.unconfirmedAdmitted<a.unconfirmedAdmitted);s.pendingLoss+=+(b.unconfirmedAdmitted>a.unconfirmedAdmitted);s.equalBodiesPendingWin+=+(a.bodies===b.bodies&&b.unconfirmedAdmitted<a.unconfirmedAdmitted);}
  if(seed===221031&&absent===0&&retention===3&&traffic.length===3&&budget===8&&loss==='ack-first'&&[2,5,8].includes(delay))for(const z of group){const stem=`delay-${delay}-${z.policy}`,x=simulate(c,z.policy,true);assert.deepEqual(x.m,z.m);assert.deepEqual(x.trace,z.trace);const b=wav(x.pcm);fs.writeFileSync(path.join(out,stem+'.wav'),b);specimens.push({stem,sha256:sha(b),c,policy:z.policy,m:z.m,trace:z.trace});}
 }
 const receipt={schema:'mhac-interaction-housekeeping-v1',parent,grammar,units:{slotMs:200,bodyMs:100,gain:.5},stats,pairs,peak,rows,specimens};fs.writeFileSync(path.join(out,'receipt.json'),JSON.stringify(receipt));
 const html='<!doctype html><meta charset=utf-8><title>Receipt housekeeping</title><style>body{font:16px system-ui;max-width:900px;margin:2em auto}pre{white-space:pre-wrap}audio{display:block}</style><h1>Receipt housekeeping</h1><p>Synthetic aligned dialogue. Start with low volume; no autoplay. Compare same body cap, not necessarily same realized airtime.</p><select id="s">'+specimens.map(x=>`<option>${x.stem}</option>`).join('')+'</select><audio id="a" controls preload="none"></audio><pre id="t"></pre><script>const data='+JSON.stringify(specimens)+';const s=document.getElementById("s"),a=document.getElementById("a"),t=document.getElementById("t");function draw(){a.src=s.value+".wav";t.textContent=JSON.stringify(data.find(x=>x.stem===s.value),null,2)}s.onchange=draw;draw()</script>';fs.writeFileSync(path.join(out,'index.html'),html);
 const files=fs.readdirSync(out).filter(x=>x!=='manifest.json').sort();fs.writeFileSync(path.join(out,'manifest.json'),JSON.stringify(Object.fromEntries(files.map(f=>[f,sha(fs.readFileSync(path.join(out,f)))])),null,2));console.log(JSON.stringify({stats,pairs,peak,runs:rows.length,specimens:specimens.map(({stem,sha256,m})=>({stem,sha256,m}))}));return receipt;}
module.exports={simulate,render,decode,run};if(require.main===module)run(process.argv[2]||'housekeeping-output');
