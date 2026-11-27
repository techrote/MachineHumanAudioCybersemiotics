'use strict';
// Refs #512. Additional native PCM controls, not independent review or a security proof.
const fs=require('node:fs'),os=require('node:os'),path=require('node:path'),assert=require('node:assert/strict');
const A=require('./session-v40.cjs'),R=require('./role-v29.cjs'),O=require('./outcome-v34.cjs'),V=require('./paired-v38.cjs'),S=require('./semantic-v33.cjs'),{frame}=require('./relay.cjs');
const root=fs.mkdtempSync(path.join(os.tmpdir(),'mhac40-controls-')),rows=[];let checks=0;const ck=(actual,expected)=>{checks++;assert.equal(actual,expected);};
try{for(const bits of [32,64])for(const role of ['data','outcome','confirm']){
 const c=A.ctx(),p={kind:role==='data'?0:1,source:1,version:1,actor:9,event:8,seq:1,tree:['pump-reports',['fault']]},g=0,s=role==='data'?null:'applied',v=role==='data'?0:2,n=A.nonce(p,g),phase=.37;
 const x=A.encode(c,bits,role,p,g,s,v,n,phase),a=A.decode(c,bits,role,x),base=R.STEP;
 ck(a.authenticated,true);ck(a.challenge,n);ck(A.decode(A.ctx(2),bits,role,x).reason,'mac');ck(A.decode(A.ctx(1,true),bits,role,x).reason,'mac');
 ck(A.decode(c,bits,role,A.encode(c,bits,role,p,g,s,v,n+1,phase)).reason,'challenge');
 const erase=x.slice();erase.fill(0,base);ck(A.decode(c,bits,role,erase).reason,'extension');
 const other={...p,source:2},splice=x.slice();splice.set(A.encode(c,bits,role,other,g,s,v,A.nonce(other,g),phase).subarray(0,base));ck(A.decode(c,bits,role,splice).reason,'mac');
 if(role!=='data'){const wrongRole=role==='outcome'?'confirm':'outcome',y=x.slice();y.set(A.encode(c,bits,wrongRole,p,g,s,v,n,phase).subarray(base),base);ck(A.decode(c,bits,role,y).reason,'mac');}
 if(bits===64)ck(A.decode(c,32,role,x.subarray(0,A.step(32))).reason,'mac');
 ck(A.decode(c,bits,role,x).authenticated,true); // exact replay is still valid at codec boundary
 rows.push({bits,role,frame:frame(p),challenge:n,session:c.session.toString('hex'),tag:A.tag(c,bits,role,p,g,0,s,v,n).toString('hex'),generation:g,statusIndex:role==='data'?0:1,revision:v});
 if(role==='data'){const dir=path.join(root,String(bits));S.provision(dir,'typed');const r=S.receiver(dir);ck(r.receive(a).decision,'new');const fresh=A.ctx(2),b=A.decode(fresh,bits,'data',A.encode(fresh,bits,'data',p,g,null,0,n,phase));ck(b.authenticated,true);ck(r.receive(b).decision,'duplicate');const changed={...p,tree:['pump-reports',['open']]},d=A.decode(fresh,bits,'data',A.encode(fresh,bits,'data',changed,g,null,0,n,phase));ck(d.authenticated,true);ck(r.receive(d).decision,'occurrence-conflict');rows.at(-1).rotationWithRetainedSemanticState='same occurrence duplicate; changed payload conflict';}
}
fs.writeFileSync(process.argv[2]||'session-controls-v40.json',JSON.stringify({checks,rows},null,2)+'\n');console.log({checks,roles:rows.length});}finally{fs.rmSync(root,{recursive:true,force:true});}
