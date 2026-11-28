'use strict';
// Refs #456 / #457. Synthetic action/dialogue experiment, not hardware control.
// Usage: node temporal-fence-061.cjs PINNED_RELAY_PATH NEW_OUTPUT
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const parent='a545ea2f649e13fadbc4ec2a29f6b879e1dc11b3',pin='377dadf894631ebd7063d7e4d5922f109fd6a420',blob='3ba457f85f496e4d57d9789a2dc3b7d68fe2c071';
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const gitblob=b=>crypto.createHash('sha1').update(`blob ${b.length}\0`).update(b).digest('hex');
const cases=['clean','changed','aba','world-rollback','joint-rollback','archived-status','query-loss','status-loss','receipt-loss','wrong-source','spoofed-source'];
const policies=['sample','revision','fenced'];
const packet=(kind,source,version,event,seq,tree)=>({kind,source,version,actor:3,event,seq,tree});
const equal=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
function run(R,root,seed,fault,policy){
  const dir=fs.mkdtempSync(path.join(root,'turn-')),world=path.join(dir,'world.json'),witness=path.join(dir,'witness.json');
  let generation=0,checks=0,clips=[],events=[],applied=0,unsafe=0,knowledge='unknown';
  const ck=(x,m)=>{checks++;assert.ok(x,m)};
  const read=f=>JSON.parse(fs.readFileSync(f,'utf8'));
  const put=(f,v)=>{const t=f+'.tmp';fs.writeFileSync(t,JSON.stringify(v));fs.renameSync(t,f)};
  const seal=s=>({revision:s.revision,digest:hash(JSON.stringify(s))});
  const state=()=>read(world);
  const consistent=()=>equal(read(witness),seal(state()));
  function change(value){const s=state();if(s.revision>=16)throw Error('revision exhausted');const next={revision:s.revision+1,value};put(world,next);put(witness,seal(next));generation++;events.push({type:'world-change',state:next,generation});}
  put(world,{revision:1,value:'fault'});put(witness,seal(state()));
  function transmit(label,p,loss=false,replay=null){const pcm=replay||R.render(p,seed*.013+clips.length*.071);const x=loss?new Int16Array(pcm.length):pcm;const hits=R.acquire(x).filter(h=>h.status==='ok');const decoded=hits.length===1?hits[0].packet:null;clips.push(x);events.push({type:'pcm',label,decoded,sha256:hash(Buffer.from(x.buffer,x.byteOffset,x.byteLength)),samples:x.length});return {decoded,pcm:x};}
  function match(p,kind,source,event,seq){return p&&p.kind===kind&&p.source===source&&p.actor===3&&p.event===event&&p.seq===seq;}
  function sample(n,loss=false,replyLoss=false,replay=null,source=2,spoof=false){const q=transmit('query',packet(0,1,1,1,n,['question',['open']]),loss).decoded;if(!match(q,0,1,1,n))return null;const s=state();return transmit('status',packet(1,source,s.revision,2,q.seq,[spoof?'fault':s.value]),replyLoss,replay);}
  const old=sample(1);ck(old&&match(old.decoded,1,2,2,1),'initial sample');change('open');
  const before=state(),snap=fs.readFileSync(world),snapW=fs.readFileSync(witness),observedGeneration=generation;
  const got=sample(2,fault==='query-loss',fault==='status-loss',fault==='archived-status'?old.pcm:null,fault==='wrong-source'?4:2,fault==='spoofed-source');
  const obs=got?.decoded;const valid=match(obs,1,2,2,2)&&['open','fault','stopped'].includes(obs.tree[0])&&obs.tree.length===1;
  events.push({type:'observation',valid:!!valid,sampled:valid?{revision:obs.version,value:obs.tree[0]}:null,certainty:valid?'sample-only':'unknown'});
  if(fault==='changed'||fault==='aba'||fault.includes('rollback'))change('fault');
  if(fault==='aba')change('open');
  if(fault.includes('rollback')){fs.writeFileSync(world,snap);if(fault==='joint-rollback')fs.writeFileSync(witness,snapW);events.push({type:'rollback',scope:fault,state:state(),witnessMatches:consistent()});}
  let decision='no-action';
  if(valid&&obs.tree[0]==='open'){
    const req=transmit('conditional-action',packet(0,1,obs.version,3,2,['stopped'])).decoded;
    ck(match(req,0,1,3,2)&&equal(req.tree,['stopped']),'action decoded');
    const s=state(),revisionOK=s.revision===req.version,continuityOK=consistent();
    decision=policy==='fenced'&&!continuityOK?'continuity-refused':policy!=='sample'&&!revisionOK?'revision-refused':'applied';
    if(decision==='applied'){applied++;unsafe=Number(generation!==observedGeneration);change(req.tree[0]);}
    events.push({type:'action-decision',decision,revisionOK,continuityOK,unsafeEvaluatorOnly:!!unsafe});
    const ack=transmit('action-receipt',packet(1,2,req.version,4,req.seq,decision==='applied'?['verify',['stopped']]:['not',['stopped']]),fault==='receipt-loss').decoded;
    if(match(ack,1,2,4,2)&&ack.version===req.version){if(equal(ack.tree,['verify',['stopped']]))knowledge='applied-report';else if(equal(ack.tree,['not',['stopped']]))knowledge='refused-report';}
  }
  ck(applied<=1,'at most one action in this tape');ck(knowledge!=='applied-report'||applied===1,'receipt not execution oracle');
  if(fault==='receipt-loss')ck(applied===1&&knowledge==='unknown','lost receipt');
  if(['archived-status','query-loss','status-loss','wrong-source','spoofed-source'].includes(fault))ck(applied===0,'no action from missing or non-open sample');
  if(fault==='clean')ck(applied===1&&!unsafe,'clean');
  if(['changed','aba'].includes(fault))ck(applied===Number(policy==='sample'),'revision fence');
  if(fault==='world-rollback')ck(applied===Number(policy!=='fenced'),'witness fence');
  if(fault==='joint-rollback')ck(applied===1&&unsafe===1,'joint rollback negative');
  const pcm=R.join(...clips),bytes=R.wav(pcm);let at=0;for(const e of events.filter(e=>e.type==='pcm')){const x=pcm.subarray(at,at+e.samples);at+=e.samples;ck(hash(Buffer.from(x.buffer,x.byteOffset,x.byteLength))===e.sha256,'PCM hash');const h=R.acquire(x).filter(z=>z.status==='ok');ck(equal(h.length===1?h[0].packet:null,e.decoded),'PCM rescan');}ck(at===pcm.length,'complete PCM');
  return {row:{seed,fault,policy,decision,applied,unsafe,knowledge,actual:state(),observationBefore:before,checks,events,samples:pcm.length,sha256:hash(bytes)},bytes};
}
function main(){const codec=path.resolve(process.argv[2]),out=path.resolve(process.argv[3]);assert.equal(gitblob(fs.readFileSync(codec)),blob,'pinned codec mismatch');const R=require(codec);fs.mkdirSync(out);const root=fs.mkdtempSync(path.join(os.tmpdir(),'mhac-061-'));let rows=[];try{for(const seed of [71,113])for(const fault of cases)for(const policy of policies){const a=run(R,root,seed,fault,policy),b=run(R,root,seed,fault,policy);assert.deepEqual(a.row,b.row);assert.deepEqual(a.bytes,b.bytes);const name=`${seed}-${fault}-${policy}.wav`;fs.writeFileSync(path.join(out,name),a.bytes);rows.push({...a.row,file:name});}fs.writeFileSync(path.join(out,'receipt.json'),JSON.stringify({parent,pin,blob,node:process.version,rate:16000,rows},null,2)+'\n');console.log(JSON.stringify({sessions:rows.length,repeated:rows.length,checks:rows.reduce((s,r)=>s+2*r.checks+2,0),policies:Object.fromEntries(policies.map(p=>[p,{applied:rows.filter(r=>r.policy===p).reduce((s,r)=>s+r.applied,0),unsafe:rows.filter(r=>r.policy===p).reduce((s,r)=>s+r.unsafe,0)}]))}));}finally{fs.rmSync(root,{recursive:true,force:true})}}
if(require.main===module)main();
