'use strict';
// Interaction #456 / Draft #457, synthetic-only. Stand-in, NOT Grammar wire.
// Parent 66141259400d2e6d5581e0aeddbd6f57aeeefde4; semantic inspiration:
// Grammar terminal-receipts.cjs at 0b93531cce6c9ee273566d096517bbca36e43d99.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const RATE=16000,N=400,SLOT=3200,H=24,policies=['stop-negative','ignore-finality','semantic'];
const kinds=['request','provisional','positive','terminal-negative','ack-positive','ack-negative'];
const basis=Array.from({length:4},(_,k)=>Array.from({length:N},(_,i)=>[Math.cos(2*Math.PI*(400+80*k)*i/RATE),Math.sin(2*Math.PI*(400+80*k)*i/RATE)]));
function code(p){if(p.kind==='current')return 63;const k=kinds.indexOf(p.kind);assert(k>=0&&[0,1].includes(p.address)&&[0,1,2].includes(p.tag));return 18*p.address+6*p.tag+k;}
function render(p,seed,lost){let s=seed>>>0;const n=code(p),a=[n%4,(n>>2)%4,(n>>4)%4];a.push((a[0]+2*a[1]+3*a[2])%4);const w=new Int16Array(SLOT);for(let j=0;j<4;j++)for(let i=0;i<N;i++){s=(Math.imul(s,1664525)+1013904223)>>>0;w[j*N+i]=Math.round((lost&&j===1?0:2600*basis[a[j]][i][1])+(s%81-40));}return w;}
function decode(w){const a=[];for(let j=0;j<4;j++){const scores=basis.map(b=>{let x=0,y=0;for(let i=0;i<N;i++){x+=w[j*N+i]*b[i][0];y+=w[j*N+i]*b[i][1];}return x*x+y*y;});const m=Math.max(...scores),k=scores.indexOf(m);scores[k]=0;if(m<1e10||m<4*Math.max(...scores))return null;a.push(k);}if(a[3]!==((a[0]+2*a[1]+3*a[2])%4))return null;const n=a[0]+4*a[1]+16*a[2];if(n===63)return {kind:'current'};if(n>=36)return null;return {kind:kinds[n%6],address:Math.floor(n/18),tag:Math.floor(n%18/6)};}
function simulate(c,policy){assert(policies.includes(policy));const {delay,retention,absent,seed,loss,traffic}=c,available=1-absent;
 const R=Array.from({length:2},()=>({attempts:0,open:null,next:0,report:null,terminal:false,stopped:false})),S=[null,null],queue=[],trace=[],pcm=new Int16Array(H*SLOT),counts={},seen=new Set();let requests=0,current=0,history=0;
 const log=(slot,type,extra={})=>trace.push({slot,type,...extra});
 for(let t=0;t<H;t++){
  for(let a=0;a<2;a++){const r=R[a];if(r.open&&t>r.open.until){log(t,'timeout',{address:a,tag:r.open.tag});r.open=null;r.next=t;}}
  let p=null;
  if(traffic.includes(t))p={kind:'current'};
  else if(queue.length)p=queue.shift();
  else if(requests<3){const eligible=R.map((r,address)=>({...r,address})).filter(r=>!r.open&&!r.stopped&&r.attempts<3&&r.next<=t).sort((a,b)=>a.attempts-b.attempts||a.address-b.address);if(eligible.length){const a=eligible[0].address,r=R[a];p={kind:'request',address:a,tag:r.attempts++};r.open={tag:p.tag,until:t+5};requests++;}}
  if(!p){log(t,'idle');continue;}
  const key=p.address+'/'+p.kind,first=!seen.has(key);seen.add(key);
  const lost=first&&p.address===available&&((loss==='request'&&p.kind==='request')||(loss==='reply'&&['positive','provisional'].includes(p.kind)))||first&&p.address===absent&&loss==='ack'&&p.kind==='ack-negative';
  counts[p.kind]=(counts[p.kind]||0)+1;if(p.kind!=='current')history++;
  const w=render(p,seed+t*997,lost);pcm.set(w,t*SLOT);const d=decode(w);assert.deepEqual(d,lost?null:p);log(t,'tx',{packet:p,lost,decoded:d,receiptSample:t*SLOT+4*N});if(!d)continue;
  if(d.kind==='current'){current++;continue;}
  const a=d.address,r=R[a];
  if(d.kind==='request'){
   const found=a===available&&t>=delay&&t<delay+retention;
   const kind=found?'positive':a===absent?'terminal-negative':'provisional';
   // Terminal means closed for this enquiry, never global absence. Sender has local archive state only.
   log(t,'lookup',{address:a,tag:d.tag,found,kind});
   const response={kind,address:a,tag:d.tag};if(kind!=='provisional'){if(S[a]?.pending)log(t,'superseded-pending',{address:a,old:S[a].tag});S[a]={...response,pending:true};}queue.push(response);
  }else if(d.kind.startsWith('ack-')){
   const s=S[a],expected=d.kind==='ack-positive'?'positive':'terminal-negative';if(s&&s.pending&&s.tag===d.tag&&s.kind===expected){s.pending=false;log(t,'release',{address:a,tag:d.tag});}
  }else if(r.open&&r.open.tag===d.tag&&t<=r.open.until){
   r.open=null;r.report=d.kind;r.terminal=d.kind!=='provisional';r.next=t+2;
   if(d.kind==='positive'||policy==='stop-negative'||(policy==='semantic'&&r.terminal))r.stopped=true;
   if(r.terminal)queue.push({kind:d.kind==='positive'?'ack-positive':'ack-negative',address:a,tag:d.tag});
   log(t,'admit',{address:a,tag:d.tag,report:r.report,terminal:r.terminal,stopped:r.stopped});
  }else log(t,'reject-stale',{address:a,tag:d.tag});
 }
 const metrics={positive:+(R[available].report==='positive'),current,requests,history,terminalRequester:R.filter(r=>r.terminal).length,released:S.filter(s=>s&&!s.pending).length,pending:S.filter(s=>s?.pending).length,wasted:trace.filter(e=>e.type==='tx'&&e.packet.kind==='request'&&e.packet.address===absent&&e.packet.tag>0).length};
 assert(requests<=3&&history+current<=H);assert.equal(current,traffic.length);for(const e of trace.filter(e=>e.type==='release'))assert(trace.some(x=>x.slot<=e.slot&&x.type==='admit'&&x.address===e.address&&x.tag===e.tag&&x.terminal));
 return {c,policy,metrics,counts,requester:R,sender:S,trace,pcm};}
function wav(pcm){const b=Buffer.alloc(44+2*pcm.length);b.write('RIFF');b.writeUInt32LE(b.length-8,4);b.write('WAVEfmt ',8);b.writeUInt32LE(16,16);b.writeUInt16LE(1,20);b.writeUInt16LE(1,22);b.writeUInt32LE(RATE,24);b.writeUInt32LE(2*RATE,28);b.writeUInt16LE(2,32);b.writeUInt16LE(16,34);b.write('data',36);b.writeUInt32LE(2*pcm.length,40);pcm.forEach((v,i)=>b.writeInt16LE(Math.round(v*.5),44+2*i));return b;}
function run(out){fs.mkdirSync(out,{recursive:true});const rows=[],stats={},pairs={all:0,matched:0,win:0,tie:0,loss:0,less:0,more:0},specimens=[];let peak=0;
 for(let n=0;n<36;n++){const p={address:Math.floor(n/18),tag:Math.floor(n%18/6),kind:kinds[n%6]};assert.deepEqual(decode(render(p,91,false)),p);assert.equal(decode(render(p,91,true)),null);}
 for(const seed of [221019,221021])for(const absent of [0,1])for(const delay of [2,5,8,11,14,17])for(const retention of [3,8])for(const loss of ['none','request','reply','ack'])for(const traffic of [[2,6,10],[1,2,7,8,13,14]]){
  const c={seed,absent,delay,retention,loss,traffic},group=policies.map(p=>simulate(c,p));
  for(const z of group){const {pcm,...row}=z;rows.push(row);for(const v of pcm)peak=Math.max(peak,Math.abs(v));const s=stats[z.policy]??={runs:0};s.runs++;for(const [k,v] of Object.entries(z.metrics))s[k]=(s[k]||0)+v;}
  const a=group[1].metrics,b=group[2].metrics;pairs.all++;if(a.history===b.history){pairs.matched++;pairs[b.positive>a.positive?'win':b.positive<a.positive?'loss':'tie']++;}else pairs[b.history<a.history?'less':'more']++;
  if(seed===221019&&absent===0&&retention===8&&traffic.length===3&&((delay===8&&loss==='none')||(delay===11&&loss==='ack')))for(const z of group){const stem=`delay-${delay}-${loss}-${z.policy}`,bytes=wav(z.pcm);fs.writeFileSync(path.join(out,stem+'.wav'),bytes);const {pcm,...row}=z;fs.writeFileSync(path.join(out,stem+'.json'),JSON.stringify(row,null,2));specimens.push({stem,sha256:crypto.createHash('sha256').update(bytes).digest('hex')});}
 }
 assert(peak<=2640);const receipt={schema:'mhac-interaction-semantic-patience-v1',parent:'66141259400d2e6d5581e0aeddbd6f57aeeefde4',grammarInspiration:'0b93531cce6c9ee273566d096517bbca36e43d99',stats,pairs,peak,rows,specimens};fs.writeFileSync(path.join(out,'receipt.json'),JSON.stringify(receipt));
 const html='<!doctype html><meta charset=utf-8><title>Semantic patience</title><style>body{font:16px system-ui;max-width:900px;margin:2em auto}pre{white-space:pre-wrap}audio{display:block}</style><h1>Semantic patience</h1><p>Synthetic fixed-slot dialogue. Start with low volume; no autoplay. Terminal means enquiry closure, not permanent absence.</p><label>Replay <select id="s">'+specimens.map(x=>`<option>${x.stem}</option>`).join('')+'</select></label><audio id="a" controls preload="none"></audio><a id="link">Replay JSON</a><pre id="trace"></pre><script>const rows='+JSON.stringify(rows.filter(r=>r.c.seed===221019&&r.c.absent===0&&r.c.retention===8&&r.c.traffic.length===3&&((r.c.delay===8&&r.c.loss==='none')||(r.c.delay===11&&r.c.loss==='ack'))))+';const s=document.getElementById("s"),a=document.getElementById("a"),l=document.getElementById("link"),v=document.getElementById("trace");function draw(){a.src=s.value+".wav";l.href=s.value+".json";const r=rows.find(r=>s.value===`delay-${r.c.delay}-${r.c.loss}-${r.policy}`);v.textContent=JSON.stringify({metrics:r.metrics,trace:r.trace},null,2)}s.onchange=draw;draw()</script>';fs.writeFileSync(path.join(out,'index.html'),html);
 console.log(JSON.stringify({stats,pairs,peak,runs:rows.length,specimens}));return receipt;}
module.exports={simulate,render,decode,run};if(require.main===module)run(process.argv[2]||'semantic-patience-output');
