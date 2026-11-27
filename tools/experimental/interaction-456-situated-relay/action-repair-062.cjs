'use strict';
// Refs #456. Synthetic, unauthenticated, known-frame transport; no device control.
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const PIN='a6a84ee7e2f1a56460196e42ece287eb935f0b07',BLOB='3ba457f85f496e4d57d9789a2dc3b7d68fe2c071';
const hash=b=>crypto.createHash('sha256').update(b).digest('hex'),eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const packet=(kind,source,version,event,seq,tree)=>({kind,source,version,actor:3,event,seq,tree});
const match=(p,k,s,e,n)=>p&&p.kind===k&&p.source===s&&p.actor===3&&p.event===e&&p.seq===n;
const policies=['revision','age','repair'],cases=['clean','delay','reobserve','query-replay','receipt-loss','action-loss','both-receipts-lost','changed','conflicting-retry','receipt-loss-world-change','joint-rollback'];
const MAX_AGE=3,H=12,FRAME=21120;
function run(R,root,seed,scenario,policy){
 const file=path.join(root,'state.json');let tick=0,clips=[],events=[],effects=0,knowledge='unknown',attempts=0,checks=0,stale=0,observedAt=0;
 const ck=(v,m)=>{checks++;assert.ok(v,m)},read=()=>JSON.parse(fs.readFileSync(file,'utf8'));
 const save=s=>{fs.writeFileSync(file+'.tmp',JSON.stringify(s));fs.renameSync(file+'.tmp',file)};
 save({revision:2,value:'open',samples:{},outcomes:{}});
 const change=value=>{let s=read();s.revision++;s.value=value;save(s);events.push({tick,type:'change',value,revision:s.revision})};
 function send(label,p,lost=false){ck(tick<H,'horizon');const raw=p?R.render(p,seed*.013+tick*.071):new Int16Array(FRAME),x=lost?new Int16Array(FRAME):raw;ck(x.length===FRAME,'frame');const hits=R.acquire(x).filter(h=>h.status==='ok'),decoded=hits.length===1?hits[0].packet:null;clips.push(x);events.push({tick:++tick,type:'pcm',label,decoded,lost,sha256:hash(Buffer.from(x.buffer,x.byteOffset,x.byteLength))});return decoded;}
 function observe(n){const q=send('query',packet(0,1,1,1,n,['question',['open']]));if(!match(q,0,1,1,n))return null;let s=read();if(!s.samples[n]){s.samples[n]={revision:s.revision,value:s.value,at:tick};save(s)}const v=s.samples[n];const a=send('sample',packet(1,2,v.revision,2,n,[v.value]));if(match(a,1,2,2,n)&&eq(a.tree,['open'])){observedAt=v.at;return a}return null;}
 function action(obs,lost=false,receiptLost=false,alter=false){attempts++;const req=send('action',packet(0,1,obs.version+(alter?1:0),3,obs.seq,['stopped']),lost);if(!match(req,0,1,3,obs.seq)||!eq(req.tree,['stopped'])){send('no receipt',null);return}let s=read(),key=String(req.seq),v=s.samples[key],age=v?tick-v.at:null,prior=s.outcomes[key],decision;
  if(policy==='repair'&&prior){decision=eq(prior.request,req)?prior.decision:'conflict';}
  else {decision=!v||v.revision!==req.version||v.value!=='open'||s.revision!==req.version?'refused':policy!=='revision'&&age>MAX_AGE?'refused':'applied';if(decision==='applied'){effects++;stale+=Number(tick-observedAt>MAX_AGE);s.revision++;s.value='stopped'}if(policy==='repair')s.outcomes[key]={request:req,decision};save(s)}
  events.push({tick,type:'decision',decision,age,duplicate:!!prior,revision:s.revision});const a=send('receipt',decision==='conflict'?null:packet(1,2,req.version,4,req.seq,decision==='applied'?['verify',['stopped']]:['not',['stopped']]),receiptLost);
  if(match(a,1,2,4,obs.seq)&&a.version===obs.version){if(eq(a.tree,['verify',['stopped']]))knowledge='applied-report';if(eq(a.tree,['not',['stopped']]))knowledge='refused-report';}
 }
 let obs=observe(1);ck(!!obs,'initial sample');const snap=fs.readFileSync(file);
 if(['delay','reobserve','query-replay'].includes(scenario)){for(let i=0;i<3;i++)send('wait',null);if(scenario==='reobserve')obs=observe(2);if(scenario==='query-replay')obs=observe(1)}
 if(scenario==='changed')change('fault');
 const retry=['receipt-loss','action-loss','both-receipts-lost','conflicting-retry','receipt-loss-world-change','joint-rollback'].includes(scenario);
 action(obs,scenario==='action-loss',retry&&scenario!=='action-loss');
 if(retry){if(scenario==='receipt-loss-world-change')change('fault');if(scenario==='joint-rollback'){fs.writeFileSync(file,snap);events.push({tick,type:'rollback'})}action(obs,false,scenario==='both-receipts-lost',scenario==='conflicting-retry')}
 const actual=read();while(tick<H)send('idle',null);
 ck(attempts<=2,'bounded repair');ck(effects<=1||scenario==='joint-rollback','only rollback permits duplicate effect');
 if(scenario==='clean'||scenario==='reobserve')ck(effects===1&&knowledge==='applied-report','normal action');
 if(['delay','query-replay'].includes(scenario))ck(effects===Number(policy==='revision'),'age fence');
 if(scenario==='receipt-loss'||scenario==='receipt-loss-world-change')ck(effects===1&&knowledge===(policy==='repair'?'applied-report':'refused-report'),'historical receipt');
 if(scenario==='both-receipts-lost')ck(knowledge==='unknown'&&effects===1,'unknown after loss');
 if(scenario==='changed')ck(effects===0,'revision fence');
 if(scenario==='conflicting-retry'&&policy==='repair')ck(knowledge==='unknown'&&effects===1,'conflict withheld');
 if(scenario==='joint-rollback')ck(effects===(policy==='revision'?2:1),'rollback and age witness');
 const bytes=R.wav(R.join(...clips));return {bytes,row:{seed,scenario,policy,effects,stale,knowledge,attempts,actual,checks,events,sha256:hash(bytes)}};
}
function main(){const codec=path.resolve(process.argv[2]),out=path.resolve(process.argv[3]);const b=fs.readFileSync(codec);assert.equal(crypto.createHash('sha1').update(`blob ${b.length}\0`).update(b).digest('hex'),BLOB);const R=require(codec);fs.mkdirSync(out,{recursive:true});const root=fs.mkdtempSync(path.join(os.tmpdir(),'mhac062-')),rows=[];try{for(const seed of [71,113])for(const scenario of cases)for(const policy of policies){const a=run(R,root,seed,scenario,policy),name=`${seed}-${scenario}-${policy}.wav`;fs.writeFileSync(path.join(out,name),a.bytes);rows.push({...a.row,file:name})}const receipt={pin:PIN,blob:BLOB,parent:'21b1a396e71aac25fe5e2a391fc4b05f45124d93',node:process.version,rate:16000,frame:FRAME,horizon:H,maxAge:MAX_AGE,rows};fs.writeFileSync(path.join(out,'receipt.json'),JSON.stringify(receipt,null,2)+'\n');console.log(JSON.stringify({sessions:rows.length,checks:rows.reduce((n,r)=>n+r.checks,0)}));}finally{fs.rmSync(root,{recursive:true,force:true})}}
if(require.main===module)main();
