'use strict';
// Refs #512. Local queue/history tests, distinct from acoustic trials.
const assert=require('node:assert/strict'),fs=require('node:fs'),os=require('node:os'),path=require('node:path');
const {attention}=require('./fairness-v57.cjs'),C=require('./compact-queue-v56.cjs'),J=require('./journal-v42.cjs');
let checks=0;const ck=(a,b)=>{assert.deepEqual(a,b);checks++;};
const p=i=>({kind:0,source:1,version:1,actor:9,event:8,seq:i+1,tree:['pump-reports',['open']]});
const d=(i,n,s=1)=>C.pack(s,p(i),i,n,null,.5);
for(const policy of ['fifo','debt']){
 const q=attention(policy);ck(q.add(d(0,1)),'queued');ck(q.add(d(1,2)),'queued');ck(q.add(d(0,3)),'renewed');ck(q.add(d(0,3)),'duplicate');ck(q.add(d(0,1)),'older-refused');
 ck(q.add(d(2,4)),'queue-full');ck(q.add(d(3,5)),'queue-full');ck(q.add(d(4,6)),'history-full');ck(q.snapshot().queue.length,2);ck(q.snapshot().history.length,4);
 const b=q.take();ck(C.unpack(b).n,3);q.emitted(b);q.take();ck(q.add(d(0,1)),'older-refused');ck(q.add(d(0,3)),'queued');q.take();
 // Newer refused query advances the high water; lower replay does not become eligible when drained.
 ck(q.add(d(2,3)),'older-refused');ck(q.add(d(2,4)),'queued');q.take();ck(q.add(d(4,7)),'history-full');
 const root=fs.mkdtempSync(path.join(os.tmpdir(),'mhac57-test-'));
 try{const dir=path.join(root,'r'),w=dir+'.w';J.provision(dir,w);const r=J.open(dir,w);ck(r.transition(0,2,true),'transitioned');ck(q.retire(r),0);ck(q.add(d(0,8,2)),'history-full');ck(r.transition(0,3),'transitioned');ck(q.retire(r),4);ck(q.add(d(0,8,2)),'queued');ck(q.add(d(1,9,3)),'queued');ck(r.transition(0,4),'transitioned');ck(q.retire(r),1);ck(C.unpack(q.take()).session,2);ck(q.take(),null);}finally{fs.rmSync(root,{recursive:true,force:true});}
 // Rotating the exogenous query order removes FIFO starvation in this finite fixture.
 const fair=attention(policy),counts=[0,0,0];let n=0;for(const order of [[0,1,2],[1,2,0],[2,0,1]]){for(const i of order)fair.add(d(i,++n));for(let j=0;j<2;j++){const b=fair.take();counts[C.unpack(b).g]++;fair.emitted(b);}}ck(counts,[2,2,2]);
}
const lines=fs.readFileSync(process.argv[2]||'descriptor-vectors-v56.txt','utf8').trim().split(/\r?\n/);for(const s of lines){const b=Buffer.from(s,'hex'),x=C.unpack(b);ck(C.pack(x.session,x.p,x.g,x.n,x.report,x.phase).equals(b),true);}
console.log(JSON.stringify({checks,vectorInstances:lines.length,qualification:'local queue/history tests, no PCM decoding'}));
