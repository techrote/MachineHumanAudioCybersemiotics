'use strict';
// Refs #512: v33 durable semantic world + v34 PCM outcomes; asynchronous shared-channel experiment.
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const R=require('./role-v29.cjs'),O=require('./outcome-v34.cjs'),S=require('./semantic-v33.cjs'),{wav}=require('./relay.cjs');
const STEP=R.STEP,H=12,CAP=8,ATTEMPTS=3,PARENT='a7be40886f91b7ec763419fc5382e86e95eda5b9';
const policies=['poll','push','hybrid','hybrid-debt'],cases=['gap','lost-update','missing','pressure','conflict','forged'];
const hash=x=>crypto.createHash('sha256').update(x).digest('hex'),eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const packet=(source,event,seq,value)=>({kind:0,source,version:1,actor:9,event,seq,tree:[event===7?'verify':'pump-reports',[value]]});
const key=(p,g)=>`${p.source}:${g}`,terminal=b=>b&&!b.conflict&&b.outcome!=='buffered';
function offers(name){return [
 {id:'B',g:1,p:packet(1,7,2,'stopped'),at:0,deadline:H},
 {id:'A',g:0,p:packet(1,7,1,'open'),at:name==='pressure'?6:4,deadline:H},
 {id:'C',g:0,p:packet(2,8,1,'fault'),at:name==='pressure'?1:5,deadline:name==='pressure'?5:H},
 name==='conflict'?{id:'F',g:2,p:packet(1,7,2,'fault'),at:2,deadline:H}:{id:'D',g:1,p:packet(2,8,2,'open'),at:name==='pressure'?3:7,deadline:name==='pressure'?7:H}
 ];}
function run(dir,name,policy,seed,ck){S.provision(dir,'typed');const r=S.receiver(dir),push=policy!=='poll',poll=policy!=='push',debt=policy==='hybrid-debt';
 const tx=offers(name).map(o=>({...o,attempts:0,next:o.at,belief:null,progress:o.at,first:null,finalAt:null})),q=[],trace=[],pcm=new Int16Array(H*STEP);let serial=0,lost=false,maxQueue=0,coalesced=0,refused=0;
 const byKey=new Map(tx.map(o=>[key(o.p,o.g),o])),add=j=>{if(q.length===CAP){refused++;return false;}q.push({...j,serial:serial++});maxQueue=Math.max(maxQueue,q.length);return true;};
 function response(rec,status,revision,why,t){const k=key(rec.p,rec.g),old=q.find(j=>j.type==='response'&&key(j.p,j.g)===k);if(old){old.status=status;old.revision=revision;old.why=why;coalesced++;return;}add({type:'response',p:{...rec.p,kind:1},g:rec.g,status,revision,why,at:t});}
 for(let t=0;t<H;t++){
  // Sender timers use local offer/attempt history and acoustically recovered belief.
  for(const o of tx){if(t<o.at||t>=o.deadline||o.attempts>=ATTEMPTS||t<o.next||terminal(o.belief)||(!poll&&o.belief))continue;if(!q.some(j=>j.type==='data'&&j.id===o.id))add({type:'data',id:o.id,p:o.p,g:o.g,at:t});}
  // Receiver responses do not consult sender belief; centralized arbiter may observe it for debt.
  for(let i=q.length-1;i>=0;i--){const j=q[i],o=byKey.get(key(j.p,j.g));if(j.type==='data'&&(t>=o.deadline||terminal(o.belief)))q.splice(i,1);}
  const age=j=>{const o=byKey.get(key(j.p,j.g));return o&&!terminal(o.belief)?t-o.progress:0;};
  q.sort((a,b)=>(debt?age(b)-age(a):0)||a.serial-b.serial);
  const j=q.shift(),before=r.snapshot(),slot=new Int16Array(STEP);let decoded={status:'refused'},decision=null,fault=null,admitted=null;
  if(j){const o=byKey.get(key(j.p,j.g));ck(!!o,'known obligation');
   if(j.type==='data'){
    o.attempts++;o.next=t+3;slot.set(R.encode(j.p,j.g,0,0,seed*.013));
    if(name==='missing'&&o.id==='A'){slot.fill(0);fault='data-loss';}
    decoded=R.acquire(slot);decision=r.receive(decoded);const after=r.snapshot();
    if(decision.ack){const rec=after.records.find(x=>key(x.p,x.g)===key(decoded.packet,decoded.generation));response(rec,decision.semantic,after.records.length,'receipt',t);}
    if(push)for(const rec of after.records){const k=key(rec.p,rec.g),prior=before.semantic.status[k],now=after.semantic.status[k];if(prior&&prior!==now)response(rec,now,after.records.length,'push',t);}
   }else{
    let s=j.status,v=j.revision;
    if(name==='forged'&&o.id==='B'&&!lost){s='applied';v=4;lost=true;fault='forged';}
    slot.set(O.encode(j.p,j.g,0,s,v,seed*.013));
    if(name==='lost-update'&&o.id==='B'&&s==='applied'&&!lost){slot.fill(0);lost=true;fault='update-loss';}
    decoded=O.acquire(slot);const prior=o.belief;o.belief=O.observe(prior,decoded,o.p,o.g,'outcome');admitted=!eq(prior,o.belief);
    if(o.belief){if(o.first===null)o.first=t+1;if(!prior||prior.outcome!==o.belief.outcome||!!prior.conflict!==!!o.belief.conflict)o.progress=t+1;if(terminal(o.belief)&&o.finalAt===null)o.finalAt=t+1;}
    if(admitted&&o.belief&&!terminal(o.belief))o.next=Math.max(o.next,t+(policy.startsWith('hybrid')?4:2));
   }
  }
  pcm.set(slot,t*STEP);const state=r.snapshot();ck(state.records.length<=4&&new Set(state.semantic.effects).size===state.semantic.effects.length,'bounded effects');ck(q.length<=CAP&&tx.every(o=>o.attempts<=ATTEMPTS),'bounds');
  trace.push({t,job:j??null,fault,decoded,decision,admitted,state:state.semantic,beliefs:Object.fromEntries(tx.map(o=>[o.id,o.belief])),queue:q.map(x=>({...x})),debt:Object.fromEntries(tx.map(o=>[o.id,terminal(o.belief)?0:Math.max(0,t+1-o.progress)]))});
 }
 const final=r.snapshot();ck(eq(S.receiver(dir).snapshot(),final),'persistent reopen');const result=tx.map(o=>({id:o.id,attempts:o.attempts,first:o.first,finalAt:o.finalAt,deadline:o.deadline,belief:o.belief,actual:final.semantic.status[key(o.p,o.g)]??null,correct:!!o.belief&&!o.belief.conflict&&o.belief.outcome===final.semantic.status[key(o.p,o.g)],onTime:o.first!==null&&o.first<=o.deadline}));
 return {pcm,trace,result,final:final.semantic,metrics:{used:trace.filter(x=>x.job).length,data:trace.filter(x=>x.job?.type==='data').length,responses:trace.filter(x=>x.job?.type==='response').length,pushes:trace.filter(x=>x.job?.why==='push').length,polls:tx.reduce((s,o)=>s+Math.max(0,o.attempts-1),0),maxQueue,coalesced,refused,correct:result.filter(x=>x.correct).length,onTime:result.filter(x=>x.onTime).length,wrong:result.filter(x=>x.belief&&!x.correct).length}};
}
function main(out){fs.mkdirSync(out,{recursive:true});const root=fs.mkdtempSync(path.join(os.tmpdir(),'mhac-v35-'));let checks=0,rescans=0;const ck=(x,m)=>{checks++;assert.ok(x,m);},rows=[];
 try{for(const seed of [71,113])for(const name of cases)for(const policy of policies){const {pcm,...r}=run(path.join(root,`${seed}-${name}-${policy}`),name,policy,seed,ck),file=`${seed}-${name}-${policy}.wav`;const raw=wav(pcm);fs.writeFileSync(path.join(out,file),raw);const bytes=fs.readFileSync(path.join(out,file));for(const t of r.trace){const x=Int16Array.from({length:STEP},(_,i)=>bytes.readInt16LE(44+2*(t.t*STEP+i)));const a=t.job?.type==='response'?O.acquire(x,127):R.acquire(x,true,127);assert.deepEqual(a,t.decoded);rescans++;}ck(r.metrics.used<=H&&r.metrics.data+r.metrics.responses===r.metrics.used,'airtime accounting');rows.push({seed,name,policy,file,sha256:hash(bytes),samples:pcm.length,...r});}
 fs.writeFileSync(path.join(out,'receipt.json'),JSON.stringify({schema:'mhac-outcome-arbitration-v35',parent:PARENT,rate:16000,step:STEP,horizon:H,checks,rescans,rows},null,2)+'\n');console.log({checks,rescans,sessions:rows.length});
 }finally{fs.rmSync(root,{recursive:true,force:true});}}
module.exports={run};if(require.main===module)main(process.argv[2]||'outcome-arbitration-v35-output');
