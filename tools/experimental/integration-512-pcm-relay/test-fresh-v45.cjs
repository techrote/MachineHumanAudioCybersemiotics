'use strict';
const fs=require('node:fs'),os=require('node:os'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const F=require('./fresh-v45.cjs'),A=require('./session-v40.cjs'),J=require('./journal-v42.cjs'),{wav}=require('./relay.cjs');
const seed=Number(process.env.SEED||71),phase=seed*.013,out=process.argv[2]||'fresh-output',root=fs.mkdtempSync(path.join(os.tmpdir(),'mhac45-'));fs.mkdirSync(out,{recursive:true});let checks=0,rescans=0;const rows=[];
const ck=(a,b)=>{assert.deepEqual(a,b);checks++;},hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const p={kind:0,source:2,version:1,actor:9,event:8,seq:1,tree:['pump-reports',['fault']]},g=0,n1=101,n2=102;
const data=A.encode(A.ctx(1),64,'data',p,g,null,0,A.nonce(p,g),phase);
const zero=()=>new Int16Array(F.L);
try{for(const name of ['clean','archive-after-loss','explicit-absence','response-loss','query-loss','challenge-reuse','delayed-current-report','authorized-lie','wrong-reference','challenge-splice'])for(const policy of ['unbound','bound']){
 const bound=policy==='bound',dir=path.join(root,name+'-'+policy),w=dir+'.w';J.provision(dir,w);let r=J.open(dir,w);const old=[fs.readFileSync(path.join(dir,'state.json')),fs.readFileSync(w)];const slots=[],trace=[];
 function slot(role,x,n,fn){const decoded=role==='data'?A.decode(A.ctx(1),64,'data',x.subarray(0,F.BASE)):role==='query'?F.decodeQuery(1,x):F.decodeReply(1,p,g,n,x,bound);const result=fn?fn(x):decoded;slots.push(x);trace.push({slot:slots.length-1,role,n,decoded,result});return result;}
 ck(slot('data',F.wrap(data),0,x=>r.receive('data',x.subarray(0,F.BASE)).decision),'new');
 const first=F.query(1,p,g,n1,phase);slot('query',first,n1);const saved=F.answer(r,first,phase,bound);ck(saved.decision,'retained-report');ck(slot('reply',saved.pcm,n1).status,'applied');
 const rollback=()=>{fs.writeFileSync(path.join(dir,'state.json'),old[0]);fs.writeFileSync(w,old[1]);r=J.open(dir,w);};
 if(['archive-after-loss','explicit-absence','challenge-reuse','authorized-lie'].includes(name))rollback();
 const start=slots.length,nonce=name==='challenge-reuse'?n1:n2,before=r.snapshot();let result={kind:'unknown',status:'no-admitted-response'};
 for(let attempt=0;attempt<2;attempt++){
  const n=nonce+attempt,request=F.query(1,p,g,n,phase);if(name==='challenge-splice')request.set(F.query(1,p,g,n+5,phase).subarray(F.BASE),F.BASE);
  if(name==='query-loss'&&attempt===0)request.fill(0);
  slot('query',request,n);const a=F.answer(r,request,phase,bound);let response=a.pcm??zero();
  if(name==='delayed-current-report'&&attempt===0){ck(a.decision,'retained-report');rollback();}
  if(['archive-after-loss','challenge-reuse'].includes(name)&&attempt===0)response=saved.pcm;
  if(name==='response-loss'&&attempt===0)response=zero();
  if(name==='authorized-lie')response=F.reply(1,p,g,n,{status:'applied',revision:1},phase,bound);
  if(name==='wrong-reference')response=F.reply(1,{...p,tree:['pump-reports',['open']]},g,n,{status:'applied',revision:1},phase,bound);
  result=slot('reply',response,n);if(result.kind!=='unknown')break;
 }
 const final=r.snapshot();if(name!=='delayed-current-report')ck(final,before);else ck(final.epochs[0].records.length,0);
 const expected=({clean:'applied','archive-after-loss':bound?'no-exact-retained-record':'applied','explicit-absence':'no-exact-retained-record','response-loss':'applied','query-loss':'applied','challenge-reuse':'applied','delayed-current-report':'applied','authorized-lie':'applied','wrong-reference':'no-admitted-response','challenge-splice':'no-admitted-response'})[name];ck(result.status,expected);
 const pcm=new Int16Array(slots.length*F.L);slots.forEach((x,i)=>pcm.set(x,i*F.L));const file=`${seed}-${name}-${policy}.wav`,b=wav(pcm);fs.writeFileSync(path.join(out,file),b);const bytes=fs.readFileSync(path.join(out,file));for(const t of trace){const x=Int16Array.from({length:F.L},(_,i)=>bytes.readInt16LE(44+2*(t.slot*F.L+i)));const d=t.role==='data'?A.decode(A.ctx(1),64,'data',x.subarray(0,F.BASE),127):t.role==='query'?F.decodeQuery(1,x):F.decodeReply(1,p,g,t.n,x,bound);ck(d,t.decoded);rescans++;}
 rows.push({name,policy,file,sha256:hash(bytes),samples:pcm.length,repairSlots:slots.length-start,decision:result.status,belief:result.kind,records:final.epochs[0].records.length,newAdmission:false,trace});
}fs.writeFileSync(path.join(out,'receipt.json'),JSON.stringify({schema:'mhac-fresh-v45',parent:'0bbe9efc7704c66d526bf56c14218503f0b217c6',seed,rate:16000,step:F.L,checks,rescans,rows},null,2)+'\n');console.log({seed,checks,rescans,sessions:rows.length});}finally{fs.rmSync(root,{recursive:true,force:true});}
