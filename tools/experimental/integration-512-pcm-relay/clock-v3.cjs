'use strict';
// Refs #512. Clock-aware receiver for unchanged v2 wire format; experimental.
const v1=require('./relay.cjs'), v2=require('./bound-v2.cjs');
const RATE=16000, FRAME=31360, MAX=38400, STEP=1280, HEAD=640;
const eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b), mod=x=>(x%17+17)%17;
const scales=Array.from({length:13},(_,i)=>1+(i-6)*.0025);
const bank=new Map();
function score(p,s,n,f){
  if(s<0||s+n>p.length)return 0;
  const key=n+':'+f;let b=bank.get(key);
  if(!b){b=[Float64Array.from({length:n},(_,i)=>Math.cos(2*Math.PI*f*i/RATE)),Float64Array.from({length:n},(_,i)=>Math.sin(2*Math.PI*f*i/RATE))];bank.set(key,b);}
  let x=0,y=0,e=0;for(let i=0;i<n;i++){const a=p[s+i];x+=a*b[0][i];y+=a*b[1][i];e+=a*a;}
  return e<n*250**2?0:2*(x*x+y*y)/(n*e);
}
function repair(w){
  const miss=w.flatMap((x,i)=>x===null?[i]:[]);if(miss.length>2)return null;
  const valid=x=>mod(x.reduce((a,b)=>a+b,0))===0&&mod(x.reduce((a,b,i)=>a+(i+1)*b,0))===0;
  for(let a=0;a<(miss.length?17:1);a++)for(let b=0;b<(miss.length===2?17:1);b++){const x=w.slice();if(miss.length)x[miss[0]]=a;if(miss.length===2)x[miss[1]]=b;if(valid(x))return x;}return null;
}
const vocab=['fault','open','stopped','overload','not','quote','question','verify','pump-reports','relay-reports','uncertain','and','if'];
function parse(w){
  const a=repair(w.slice(0,8)),b=repair(w.slice(8,16)),c=repair(w.slice(16));if(!a||!b||!c||a[0]>1||a.slice(1,6).some(x=>x<1))return null;
  const n=b[0]+1;if(n<1||n>4||b.slice(n+1,6).some(x=>x!==13))return null;
  let j=1;function read(){if(j>n||b[j]>=13)throw Error('tree');const i=b[j++];return [vocab[i],...Array.from({length:i<4?0:i<11?1:2},read)];}
  try{const tree=read();if(j!==n+1)return null;const [kind,source,version,actor,event,seq]=a,p={kind,source,version,actor,event,seq,tree};return eq(c.slice(0,6),v2.tag(p))&&eq(v1.frame(p),[...a,...b])?p:null;}catch{return null;}
}
function symbol(p,s,scale){
  const n=Math.round(320*scale);let best=-1,a=0,b=0;
  for(let v=0;v<17;v++){const q=score(p,s,n,(400+100*v)/scale);if(q>a){b=a;a=q;best=v;}else if(q>b)b=q;}
  return a>=.85&&a-b>=.2?best:null;
}
function acquire(p){
  if(!(p instanceof Int16Array)||p.length>MAX)throw Error('bounded single-frame capture');
  const candidates=[];let minOnset=Infinity,maxOnset=-Infinity;
  for(const scale of scales){const n=Math.round(320*scale);let best=null;
    // Single-frame interface: search all offsets with enough room for the preamble.
    for(let s=0;s+2*n<=p.length;s+=16){const a=score(p,s,n,2300/scale);if(a<.72)continue;const b=score(p,s+n,n,2700/scale),q=Math.min(a,b);if(q>=.72){minOnset=Math.min(minOnset,s);maxOnset=Math.max(maxOnset,s);if(!best||q>best.q)best={s,scale,q};}}
    if(best)candidates.push(best);
  }
  // Refuse competing physical onset clusters rather than choose by semantic content.
  const found=new Map(), evidence=[];
  for(const h of candidates){
    // Short centred windows absorb guard-only edits without changing the transmitted waveform.
    const w=Array.from({length:24},(_,i)=>symbol(p,Math.round(h.s+(HEAD+i*STEP+320)*h.scale),h.scale));
    const complete=h.s+Math.round(FRAME*h.scale)-320<=p.length;
    const packet=complete?parse(w):null;evidence.push({...h,words:w,erasures:w.filter(x=>x===null).length,complete,valid:!!packet});
    if(packet)found.set(JSON.stringify(packet),packet);
  }
  const ambiguous=maxOnset-minOnset>320;
  return {status:ambiguous||found.size>1?'ambiguous':found.size===1?'ok':candidates.length?'refused':'no-acquisition',packet:!ambiguous&&found.size===1?[...found.values()][0]:null,onsetSpan:candidates.length?maxOnset-minOnset:0,evidence};
}
module.exports={acquire,MAX};
if(require.main===module){
  const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict');
  const dir=process.argv[2]||'clock-v3-output';fs.mkdirSync(dir,{recursive:true});
  const rows=[];let assertions=0;const check=(x,m)=>{assertions++;assert.ok(x,m);};
  const A=v1.base,B={...A,source:2,actor:3,event:2,seq:4,tree:['quote',['open']]};
  const shift=(p,n)=>v1.join(p.slice(0,21120+1000),n>0?new Int16Array(n):new Int16Array(),p.slice(21120+1000+Math.max(0,-n)));
  const drift=(p,s)=>Int16Array.from({length:Math.round(p.length*s)},(_,i)=>p[Math.min(p.length-1,Math.floor(i/s))]);
  function test(name,p,expected,offset=617){const pcm=v1.join(new Int16Array(offset),p,new Int16Array(640));const fixed=v2.acquire(pcm).filter(h=>h.status==='ok').map(h=>h.packet);const got=acquire(pcm);const ok=eq(got.packet,expected);check(ok,name+' '+JSON.stringify(got));const bytes=v1.wav(pcm),file=name+'.wav';fs.writeFileSync(path.join(dir,file),bytes);rows.push({name,file,expected,fixed:fixed.length===1?fixed[0]:null,clock:got,samples:pcm.length,sha256:crypto.createHash('sha256').update(bytes).digest('hex')});}
  for(const kind of [0,1])for(const [i,phase] of [0,.37,1.2,2.6].entries()){
    const a={...A,kind},p=v2.render(a,phase),o=[160,617,943,1199][i],cut=shift(p,-240);check(p.reduce((s,x)=>s+x*x,0)===cut.reduce((s,x)=>s+x*x,0),'guard-only energy');
    test(`clean-${kind}-${i}`,p,a,o);test(`guard-${kind}-${i}`,cut,a,o);
    for(const s of [.988,.995,1.005,1.012])test(`drift-${kind}-${i}-${s}`,drift(p,s),a,o);
  }
  const p=v2.render(A),b=v2.render(B);
  test('splice',v1.join(p.slice(0,10880),b.slice(10880,21120),p.slice(21120)),null);
  test('v1-only',v1.render(A),null);test('tag-substitution',v2.render(A,0,w=>w.map((x,i)=>i===3?(x+1)%17:x)),null);
  test('lost',new Int16Array(FRAME),null);test('competing-preamble',v1.join(p.slice(0,640),new Int16Array(1000),p),null);test('truncated',p.slice(0,24000),null);test('forged-ack',v2.render({...A,kind:1}),{...A,kind:1});
  const C={...A,version:1,actor:9,event:6,seq:15},D={...A,version:2,actor:5,event:9,seq:16};
  check(eq(v2.tag(C),v2.tag(D)),'collision baseline');test('tag-collision',v1.join(v2.render(D).slice(0,21120),v2.render(C).slice(21120)),D);
    // Fresh reproduction of #449 timing conditions; inverse oracle not used.
  for(const kind of [0,1])for(const seed of [937,2017,4099,8111]){
    const a={...A,kind},phase=((seed*16807)%2147483647)/2147483647*2*Math.PI,o=160+seed%480,p=v2.render(a,phase),pivot=22400;
    for(const d of [0,-.001,.001,-.0025,.0025,-.005,.005,-.01,.01]){
      const scale=1+d,w=Int16Array.from({length:Math.round(FRAME*scale)},(_,i)=>{const t=i/scale,k=Math.floor(t),f=t-k;return Math.round((p[k]||0)*(1-f)+(p[k+1]||0)*f);});
      test(`audit-scale-${kind}-${seed}-${d}`,w,a,o);
    }
    for(const d of [-80,80,-160,160,-240,240]){
      const w=d<0?v1.join(p.slice(0,pivot+d),p.slice(pivot)):v1.join(p.slice(0,pivot),new Int16Array(d),p.slice(pivot));
      check(p.reduce((s,x)=>s+x*x,0)===w.reduce((s,x)=>s+x*x,0),'audit energy');test(`audit-guard-${kind}-${seed}-${d}`,w,a,o);
    }
  }
  const report={schema:'mhac-clock-v3',assertions,rows};fs.writeFileSync(path.join(dir,'receipt.json'),JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify({assertions,rows:rows.length,fixedCorrect:rows.filter(r=>eq(r.fixed,r.expected)).length,clockCorrect:rows.filter(r=>eq(r.clock.packet,r.expected)).length}));
}
