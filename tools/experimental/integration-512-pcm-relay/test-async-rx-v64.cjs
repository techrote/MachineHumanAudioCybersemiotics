'use strict';
// Refs #512. Synthetic continuous-capture differential laboratory.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const R=require('./async-rx-v64.cjs'),Old=require('./stream-rx-v63.cjs'),F=require('./fresh-v45.cjs'),{wav}=require('./relay.cjs');
const D=require('./compact-queue-v56.cjs'),T=require('./stream-reply-v58.cjs');
const root=process.argv[2]||'rx61-results',out=process.argv[3]||'async64-results';fs.mkdirSync(out,{recursive:true});
const p={kind:0,source:1,version:1,actor:9,event:7,seq:2,tree:['verify',['stopped']]},q={...p,source:2,event:8,tree:['pump-reports',['fault']]},offers=[{p,g:1,pending:7},{p:q,g:1,pending:8}];
let checks=0;const ck=(a,b)=>{assert.deepEqual(a,b);checks++;},sha=b=>crypto.createHash('sha256').update(b).digest('hex');
function read(file){const b=fs.readFileSync(path.join(root,file));return Int16Array.from({length:(b.length-44)/2},(_,i)=>b.readInt16LE(44+i*2));}
function scan(x,chunk,gap){const r=new R.Receiver(),events=[],emit=e=>events.push({...e,decision:R.admit(e.acquisition,1,offers)});for(let i=0;i<x.length;){if(gap&&i===gap[0]){r.gap(gap[1]-i,emit);i=gap[1];continue;}const end=Math.min(x.length,i+chunk,gap&&i<gap[0]?gap[0]:Infinity);r.push(x.subarray(i,end),emit);i=end;}r.finish(emit);return events;}
function fixed(x){const r=new Old.Receiver();for(let i=0;i<x.length;i+=511)r.push(x.subarray(i,i+511));return Old.admit(r.finish(),1,offers);}
function place(x,off=13,tail=1500){const y=new Int16Array(off+x.length+tail);y.set(x,off);return y;}
const admitted=e=>e.filter(z=>z.decision.kind!=='unknown');const archive=JSON.parse(fs.readFileSync(path.join(root,'receipt.json'))),rows=[],specimens=[];
for(const row of archive.rows){const x=read(row.file),off=13,y=place(x,off),gap=row.knownGap?.map(n=>n+off);const events=scan(y,511,gap);ck(scan(y,127,gap),events);ck(admitted(events).length<=1,true);if(admitted(events).length&&row.decision.kind!=='unknown')ck(admitted(events)[0].decision,row.decision);rows.push({seed:row.seed,scenario:row.scenario,baseline:row.decision,events});}
ck(rows.filter(r=>r.baseline.kind==='unknown'&&admitted(r.events).length).map(r=>r.scenario),['offset160','offset160']);
ck(rows.filter(r=>r.baseline.kind!=='unknown'&&!admitted(r.events).length).map(r=>r.scenario),['bodyOffset96','bodyOffset96','bodyPlus48','bodyPlus128','bodyPlus48','bodyPlus128']);
function specimen(seed,name,x,gap,expected,extra={}){const events=scan(x,511,gap);for(const n of [1,127,1024])ck(scan(x,n,gap),events);ck(admitted(events).length,expected);const file=seed+'-'+name+'.wav',b=Buffer.from(wav(x));fs.writeFileSync(path.join(out,file),b);specimens.push({seed,name,file,samples:x.length,sha256:sha(b),gap:gap??null,events,...extra});return events;}
for(const seed of [71,113]){const clean=read(seed+'-clean.wav');for(const off of [0,1,13,999])specimen(seed,'offset-'+off,place(clean,off),null,1,{trueOrigins:[off]});
 const two=new Int16Array(13+2*clean.length+1500);two.set(clean,13);two.set(clean,13+clean.length);const ev=specimen(seed,'back-to-back',two,null,2,{trueOrigins:[13,13+clean.length]});ck(ev[0].decision,ev[1].decision);
 const short=place(clean,13,0);specimen(seed,'end-without-guard',short,null,0);
 const guard=place(clean);specimen(seed,'guard-gap',guard,[13+R.HORIZON+20,13+R.HORIZON+38],0);ck(sha(fs.readFileSync(path.join(out,seed+'-guard-gap.wav'))),sha(fs.readFileSync(path.join(out,seed+'-offset-13.wav'))));
 const decoy=place(clean),at=13+R.HORIZON-300;for(let i=0;i<640;i++)decoy[at+i]=clean[64+i];const base=fixed(decoy.subarray(13,13+clean.length));ck(base.kind,'report');const z=specimen(seed,'cross-boundary-pilot',decoy,null,0,{insertedPilot:at,fixedDecision:base});ck(z[0].acquisition.reason,'overlapping-body-pilot');
 for(const name of ['rate1005','rate995','linear1005','linear995','rate1003','bodyOffset96']){const x=read(seed+'-'+name+'.wav'),want=['rate1005','rate995','linear1005','linear995'].includes(name)?1:0;specimen(seed,name,place(x),null,want,{fixedDecision:fixed(x)});}
 const falseLock=new Int16Array(4000+clean.length+1500);falseLock.set(clean.subarray(64,704),500);falseLock.set(clean,4000);specimen(seed,'early-decoy-lock',falseLock,null,0,{trueOrigins:[4000],insertedPilot:500});
 const direct=new R.Receiver(),received=[],emit=e=>received.push(R.admit(e.acquisition,1,offers)),buf=new Int16Array(511);direct.push(new Int16Array(13),emit);for(const [packet,challenge] of [[p,7],[q,8]]){const tx=T.prepare(D.pack(1,packet,1,challenge,{status:'applied',revision:2},seed*.013));while(tx.remaining){const n=tx.pull(buf);direct.push(buf.subarray(0,n),emit);}}direct.push(new Int16Array(1024),emit);direct.push(new Int16Array(512),emit);direct.finish(emit);ck(received,[{kind:'report',status:'applied',revision:2},{kind:'report',status:'applied',revision:2}]);
 const silence=new Int16Array(2*F.L);ck(scan(silence,511),[]);
 // Unknown sender offset must not provide authentication context or authorize reuse.
 const e=scan(place(clean),511)[0];ck(R.admit(e.acquisition,1,[{...offers[0],pending:8}]).kind,'unknown');ck(R.admit(e.acquisition,2,offers).kind,'unknown');
}
const r=new R.Receiver();ck(r.pcmBytes,45312);ck(r.validityBytes,2048);assert.throws(()=>r.push(new Int16Array(1025),()=>{}));checks++;assert.throws(()=>r.gap(0,()=>{}));checks++;r.finish(()=>{});assert.throws(()=>r.push(new Int16Array(1),()=>{}));checks++;
const receipt={schema:'mhac-async-rx-v64',parent:'a300e104957cbc1ad87053c19e217c184ad13003',node:process.version,checks,pcmBytes:R.PCM_BYTES,validityBytes:R.VALIDITY_BYTES,horizon:R.HORIZON,rows,specimens};fs.writeFileSync(path.join(out,'receipt.json'),JSON.stringify(receipt,null,2)+'\n');console.log(JSON.stringify({checks,rows:rows.length,baselineAdmit:rows.filter(r=>r.baseline.kind!=='unknown').length,asyncAdmit:rows.filter(r=>admitted(r.events).length).length,specimens:specimens.length}));
