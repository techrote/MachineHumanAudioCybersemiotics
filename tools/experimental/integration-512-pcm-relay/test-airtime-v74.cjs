'use strict';
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),assert=require('node:assert/strict'),crypto=require('node:crypto'),{spawnSync}=require('node:child_process');
const A=require('./airtime-v74.cjs'),P=require('./session-playground-v72.cjs');
const out=process.argv[2]||'airtime74-results';fs.mkdirSync(out);const root=fs.mkdtempSync(path.join(os.tmpdir(),'mhac74-'));let checks=0,processes=0;const rows=[];
function eq(a,b){assert.deepEqual(a,b);checks++;}
function call(...args){const p=spawnSync(process.execPath,[path.join(__dirname,'airtime-v74.cjs'),...args],{encoding:'utf8'});processes++;assert.equal(p.status,0,p.stderr);return JSON.parse(p.stdout);}
function run(name,policy,budget,offers,jobs,expected,tape,events){const d=path.join(root,name);call('init',d,policy,String(budget));for(const [type,seq,value,source,g] of offers)call('register',d,type,String(seq),value,String(source),String(g));for(const [id,action,p,plan] of jobs)call('enqueue',d,id,action,String(p),plan);const order=[];for(let i=0;i<=jobs.length*3;i++){const r=call('step',d);if(r.decision==='no-eligible-job')break;order.push(r.job);}eq(order,expected);const s=call('show',d),ep=call('endpoints',d);eq(s.pending,null);eq(s.spent<=budget,true);eq(ep.reporter.semantic.world.tape.map(x=>x.index),tape);eq(ep.reporter.semantic.world.events.length,events);const dest=path.join(out,name);fs.mkdirSync(dest);let wire=0,wavs=0;for(const j of s.jobs)for(const a of j.attempts)if(a.trace){const r=JSON.parse(fs.readFileSync(path.join(d,a.trace)));eq(r.wireSamples,a.charged);wire+=r.wireSamples;const folder=path.dirname(a.trace);fs.cpSync(path.join(d,folder),path.join(dest,folder),{recursive:true});for(const t of r.attempts)for(const w of [t.forward,t.return].filter(Boolean)){const b=fs.readFileSync(path.join(d,folder,w.file));eq(crypto.createHash('sha256').update(b).digest('hex'),w.sha256);eq(b.length,44+2*w.samples);wavs++;}}eq(wire,s.spent);const row={name,policy,order,scheduler:s,world:ep.reporter.semantic.world,delivery:ep.requester.delivery,wire,wavs};rows.push(row);fs.writeFileSync(path.join(dest,'session.json'),JSON.stringify(row,null,2)+'\n');return row;}
const offers=[['ordered',1,'open',1,0],['ordered',2,'stopped',1,1],['event',1,'fault',1,2]];
const jobs=[['1:0','data',0,'clean:clean'],['1:1','data',1,'delay96:clean'],['1:2','data',3,'clean:clean']];
try{
 run('fifo','fifo',2*A.DATA,offers,jobs,[1,2],[1,2],0);
 run('priority','priority',2*A.DATA,offers,jobs,[3,2],[],1);
 run('dependency','dependency',2*A.DATA,offers,jobs,[3,1],[1],1);
 run('dependency-full','dependency',3*A.DATA,offers,jobs,[3,1,2],[1,2],1);
 run('reverse-enqueue','dependency',2*A.DATA,offers,[jobs[1],jobs[0]],[2,1],[1,2],0);
 run('erased-prerequisite','dependency',2*A.DATA,offers,[['1:0','data',0,'erase:clean'],jobs[1]],[1,2],[],0);
 run('missing-prerequisite','dependency',A.DATA,offers,[jobs[1]],[1],[],0);
 const r=run('query-not-donated','dependency',A.DATA+A.QUERY,offers,[jobs[0],['1:1','query',3,'clean:clean']],[2,1],[1],0);eq(r.delivery[0].evidence.kind,'absent');
 // Pure selector checks: no receiver state parameter; unaffordable query and full delivery queue cannot donate priority.
 const requester={offers:offers.map(([t,s,v,src,g])=>({p:P.packet(t,s,v,src),g})),delivery:[{},{}]};const state={policy:'dependency',budget:A.DATA,spent:0,jobs:[{n:1,id:'1:0',action:'data',priority:0,status:'queued'},{n:2,id:'1:1',action:'query',priority:3,status:'queued'}]};eq(A.select(state,requester).n,1);eq(A.select({...state,budget:A.DATA-1},requester),undefined);
 const receipt={schema:'mhac-airtime-test-v74',parent:'d626986f00a34b3f0ce661325e39de73256d9729',node:process.version,checks,processes,rows};fs.writeFileSync(path.join(out,'receipt.json'),JSON.stringify(receipt,null,2)+'\n');console.log({checks,processes,sessions:rows.length,wavs:rows.reduce((n,r)=>n+r.wavs,0)});
}finally{fs.rmSync(root,{recursive:true,force:true});}
