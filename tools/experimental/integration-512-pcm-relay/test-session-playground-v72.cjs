'use strict';
// Refs #512. Execute ordinary CLI in fresh processes, compare equal channel plans.
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),assert=require('node:assert/strict'),crypto=require('node:crypto'),{spawnSync}=require('node:child_process');
const P=require('./session-playground-v72.cjs');const out=process.argv[2]||'session72-results';fs.mkdirSync(out,{recursive:true});const root=fs.mkdtempSync(path.join(os.tmpdir(),'mhac72-'));let checks=0,processes=0;const rows=[];const eq=(a,b)=>{assert.deepEqual(a,b);checks++;};
function cli(...args){const r=spawnSync(process.execPath,[path.join(__dirname,'session-playground-v72.cjs'),...args],{encoding:'utf8'});processes++;assert.equal(r.status,0,r.stderr);return JSON.parse(r.stdout);}
function step(dir,name,action,id,channel){const dest=path.join(out,name);const z=cli(action,dir,id,channel,dest),r=JSON.parse(fs.readFileSync(path.join(dest,'trace.json')));eq(z,P.summary(r));for(const a of r.attempts)for(const w of [a.forward,a.return].filter(Boolean)){const b=fs.readFileSync(path.join(dest,w.file));eq(b.length,44+w.samples*2);eq(b.readUInt32LE(24),16000);eq(crypto.createHash('sha256').update(b).digest('hex'),w.sha256);eq(w.peak<=4096,true);}rows.push({name,stop:r.stop,wireSamples:r.wireSamples,attempts:r.attempts.length,missing:r.attempts.reduce((n,a)=>n+a.forward.missingSamples+(a.return?.missingSamples??0),0),evidence:r.after.requester.delivery.map(d=>d.evidence),world:r.after.reporter.semantic.world});return r;}
function reg(d,type,seq,value,g){return cli('register',d,type,String(seq),value,'1',String(g)).id;}
function ack(d){const p=cli('peek',d);eq(cli('ack',d,p.token).decision,'acknowledged');eq(cli('ack',d,p.token).decision,'refused');return p;}
try{for(const policy of ['typed','arrival']){const d=path.join(root,policy);cli('init',d,policy);const a=reg(d,'ordered',1,'open',0),b=reg(d,'ordered',2,'stopped',1),c=reg(d,'event',1,'fault',2);
 let r=step(d,policy+'-second-first','data',b,'delay96');eq(r.attempts[0].receipts[0].semantic,policy==='typed'?'buffered':'applied');
 r=step(d,policy+'-query-repair','query',b,'clean:erase,clean:clean');eq(r.stop,'evidence-consumed');eq(r.attempts.map(a=>a.challenge),[1,2]);eq(r.after.requester.delivery[0].evidence.status,policy==='typed'?'buffered':'applied');eq(r.wireSamples,4*84608);ack(d);
 r=step(d,policy+'-first-erased','data',a,'erase');eq(r.attempts[0].receipts,[]);
 r=step(d,policy+'-absent','query',a,'gap:clean,clean:clean');eq(r.stop,'evidence-consumed');eq(r.attempts[0].forward.missingSamples>0,true);eq(r.after.requester.delivery[0].evidence.kind,'absent');ack(d);
 r=step(d,policy+'-first-repair','data',a,'clean');eq(r.attempts[0].receipts[0].decision,'new');eq(r.after.reporter.semantic.world.tape.map(t=>t.index),policy==='typed'?[1,2]:[2,1]);
 r=step(d,policy+'-duplicate','data',a,'clean');eq(r.attempts[0].receipts[0].decision,'duplicate');eq(r.after.reporter.semantic.effects.length,2);
 r=step(d,policy+'-query-first','query',a,'clean:clean');eq(r.after.requester.delivery[0].evidence.status,'applied');
 // A fresh query can yield new evidence about the previous buffered action.
 r=step(d,policy+'-query-second','query',b,'clean:clean');eq(r.after.requester.delivery[1].evidence.status,'applied');
 const before=cli('show',d);r=step(d,policy+'-queue-full','query',c,'clean:clean');eq(r.stop,'delivery-backpressure');eq(r.attempts.length,0);eq(r.after,before);eq(cli('ack',d,before.requester.delivery[1].token).decision,'refused');ack(d);ack(d);
 r=step(d,policy+'-event','data',c,'clean');eq(r.after.reporter.semantic.world.events.length,1);
 r=step(d,policy+'-exhausted','query',c,'erase:clean,clean:erase,clean:gap');eq(r.stop,'budget-exhausted');eq(r.attempts.length,3);eq(r.after.requester.delivery.length,0);eq(r.after.requester.offers.find(o=>o.g===2).pending,r.attempts[2].challenge);eq(r.after.reporter.semantic.world.events.length,1);
 r=step(d,policy+'-reopened-query','query',c,'clean:clean');eq(r.stop,'evidence-consumed');eq(r.after.requester.delivery[0].evidence.status,'applied');eq(r.after.reporter.semantic.world.events.length,1);ack(d);
 eq(cli('show',d).reporter.semantic.effects.length,3);
 // Invalid plans cannot mutate endpoint or create output.
 const state=cli('show',d),bad=path.join(out,policy+'-invalid');const e=spawnSync(process.execPath,[path.join(__dirname,'session-playground-v72.cjs'),'query',d,c,'clean:clean,clean:clean,clean:clean,clean:clean',bad],{encoding:'utf8'});processes++;eq(e.status,1);eq(fs.existsSync(bad),false);eq(cli('show',d),state);
}const receipt={schema:'mhac-session-test-v72',node:process.version,checks,processes,rows};fs.writeFileSync(path.join(out,'receipt.json'),JSON.stringify(receipt,null,2)+'\n');console.log({checks,processes,rows:rows.length});}finally{fs.rmSync(root,{recursive:true,force:true});}
