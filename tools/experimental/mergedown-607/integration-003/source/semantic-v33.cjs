'use strict';
// Refs #512. Fictional semantic execution over pinned v29 PCM; independent v32-style admission subset.
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const R=require('./role-v29.cjs'),E=require('./epoch-v26.cjs'),{frame,wav}=require('./relay.cjs');
const PARENT='48e0c22265f45a93e299eb73d7e3b31b623d0a7c',STEP=R.STEP,RATE=16000,CAP=4,LIMIT=16384;
const policies=['arrival','typed'],eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b),hash=b=>crypto.createHash('sha256').update(b).digest('hex'),id=n=>Number.isInteger(n)&&n>=0&&n<=255;
const words=['open','stopped','fault','overload'];
// Trusted local contract, not acoustic authority. All class/stream/index/value fields are decoded PCM.
function contract(p){if(!p||p.kind!==0||p.version!==1||p.actor!==9||![1,2].includes(p.source)||!Number.isInteger(p.seq)||p.seq<1||p.seq>16||!Array.isArray(p.tree))return null;
 const t=p.tree;if(p.event===6&&p.source===1&&t.length===1&&words.includes(t[0]))return {type:'state',value:t[0],index:p.seq};
 if(p.event===7&&p.source===1&&p.seq<=4&&t.length===2&&t[0]==='verify'&&Array.isArray(t[1])&&t[1].length===1&&words.includes(t[1][0]))return {type:'ordered',value:t[1][0],index:p.seq};
 if(p.event===8&&t.length===2&&t[0]==='pump-reports'&&Array.isArray(t[1])&&t[1].length===1&&words.includes(t[1][0]))return {type:'event',value:t[1][0],index:p.seq};return null;}
const key=r=>`${r.p.source}:${r.g}`,body=p=>frame(p).join(',');
// Pure deterministic reducer is also the committed simulated application, not an evaluator overlay.
function interpret(records,policy){const world={state:null,tape:[],events:[],floor:0,blocked:false},status={},effects=[],pending=new Map(),ordered=new Map();
 const apply=(r,c)=>{status[key(r)]='applied';effects.push(key(r));if(c.type==='state')world.state={index:c.index,value:c.value};else if(c.type==='event')world.events.push({id:key(r),value:c.value});else world.tape.push({index:c.index,value:c.value});};
 for(const r of records){const c=contract(r.p),k=key(r);if(policy==='arrival'||c.type==='event'){apply(r,c);continue;}
 if(c.type==='state'){if(!world.state||c.index>world.state.index)apply(r,c);else status[k]=c.index<world.state.index?'superseded':c.value===world.state.value?'same-version':'version-conflict';continue;}
 if(ordered.has(c.index)){const prior=ordered.get(c.index);if(prior.value!==c.value){world.blocked=true;status[k]='dependency-conflict';for(const b of pending.values())status[key(b)]='blocked';pending.clear();}else status[k]='same-operation';continue;}
 ordered.set(c.index,c);if(world.blocked){status[k]='blocked';continue;}pending.set(c.index,r);status[k]='buffered';while(pending.has(world.floor+1)){const b=pending.get(++world.floor);pending.delete(world.floor);apply(b,contract(b.p));}}
 return {world,status,effects};}
function validate(s){if(!s||s.schema!=='mhac-semantic-v33'||!policies.includes(s.policy)||!Array.isArray(s.records)||s.records.length>CAP)throw Error('state');const keys=new Set();for(const r of s.records){if(!id(r.g)||!contract(r.p)||keys.has(key(r)))throw Error('record');keys.add(key(r));}if(!eq(s.semantic,interpret(s.records,s.policy)))throw Error('semantic state');return s;}
function sync(dir){const f=fs.openSync(dir,'r');try{fs.fsyncSync(f);}finally{fs.closeSync(f);}}
function save(dir,s,first=false){validate(s);const b=JSON.stringify({s,sha256:hash(JSON.stringify(s))});if(Buffer.byteLength(b)>LIMIT)throw Error('state size');const f=fs.openSync(path.join(dir,first?'state.json':'pending.json'),first?'wx':'w');try{fs.writeFileSync(f,b);fs.fsyncSync(f);}finally{fs.closeSync(f);}if(!first)fs.renameSync(path.join(dir,'pending.json'),path.join(dir,'state.json'));sync(dir);}
function read(dir){const f=fs.openSync(path.join(dir,'state.json'),'r');try{if(fs.fstatSync(f).size>LIMIT)throw Error('state size');const b=JSON.parse(fs.readFileSync(f,'utf8'));if(hash(JSON.stringify(b.s))!==b.sha256)throw Error('digest');return validate(b.s);}finally{fs.closeSync(f);}}
function provision(dir,policy){fs.mkdirSync(dir);save(dir,{schema:'mhac-semantic-v33',policy,records:[],semantic:interpret([],policy)},true);sync(path.dirname(dir));}
function receiver(dir){read(dir);return {snapshot:()=>read(dir),receive(a){const s=read(dir),p=a.packet,reply=(decision,ack=false,semantic=null)=>({decision,ack,semantic});if(a.status!=='receipt-candidate'||a.role!==0||a.epoch!==0||!id(a.generation)||!contract(p))return reply('no-receipt');const g=a.generation,k=key({p,g}),old=s.records.find(r=>key(r)===k);if(old)return body(old.p)===body(p)?reply('duplicate',true,s.semantic.status[k]):reply('occurrence-conflict');const high=Math.max(-1,...s.records.filter(r=>r.p.source===p.source).map(r=>r.g));if(g<high-2)return reply('stale');if(s.records.length===CAP)return reply('capacity');s.records.push({p,g});s.semantic=interpret(s.records,s.policy);save(dir,s);return reply('new',true,s.semantic.status[k]);}};}
const packet=(event,seq,value,source=1)=>({kind:0,source,version:1,actor:9,event,seq,tree:event===6?[value]:[event===7?'verify':'pump-reports',[value]]});
// [generation, packet, fault, reopen]. Identical fixed offer/channel tape for both policies.
const cases={
 reverse:[[1,packet(6,2,'stopped')],[0,packet(6,1,'open')]],
 gap:[[1,packet(7,2,'stopped')],[0,packet(7,1,'open'),null,true],[1,packet(7,2,'stopped')],[1,packet(7,2,'fault')]],
 lost:[[0,packet(7,1,'open'),'drop'],[1,packet(7,2,'stopped')],[2,packet(8,1,'fault')],[1,packet(7,2,'stopped')]],
 interleave:[[0,packet(7,1,'open')],[1,packet(8,1,'fault')],[2,packet(7,2,'stopped')],[0,packet(8,1,'open',2)]],
 version:[[0,packet(6,2,'stopped')],[1,packet(6,2,'open')],[2,packet(6,1,'fault')]],
 dependencyConflict:[[1,packet(7,2,'stopped')],[2,packet(7,2,'fault')],[0,packet(7,1,'open')]],
 authority:[[0,packet(6,1,'open')],[1,packet(6,2,'stopped',2)],[1,packet(6,16,'stopped')],[2,packet(6,2,'open')]],
 repair:[[0,packet(8,1,'fault'),'erase'],[0,packet(8,1,'fault'),'ack-drop'],[0,packet(8,1,'fault'),null,true]],
 capacity:[[0,packet(8,1,'fault')],[1,packet(8,2,'open')],[2,packet(8,3,'stopped')],[3,packet(8,4,'overload')],[4,packet(8,5,'open')],[0,packet(8,1,'fault')]]};
function main(out){fs.mkdirSync(out,{recursive:true});const root=fs.mkdtempSync(path.join(os.tmpdir(),'mhac-v33-'));let checks=0,rescans=0;const ck=(x,m)=>{checks++;assert.ok(x,m);},rows=[];
 try{for(const seed of [71,113])for(const [name,steps] of Object.entries(cases))for(const policy of policies){const dir=path.join(root,`${seed}-${name}-${policy}`);provision(dir,policy);let r=receiver(dir);const trace=[],pcm=new Int16Array(2*steps.length*STEP),confirmed=new Set();
 for(const [i,[g,p,fault,reopen]] of steps.entries()){if(reopen)r=receiver(dir);const x=R.encode(p,g,0,0,seed*.013);if(fault==='drop')x.fill(0);if(fault==='erase')x.fill(0,E.STEP);const a=R.acquire(x),d=r.receive(a),s=r.snapshot();const ack=d.ack?R.encode({...a.packet,kind:1},a.generation,a.epoch,0,seed*.013):new Int16Array(STEP);if(fault==='ack-drop')ack.fill(0);const b=R.acquire(ack),matched=b.role===0&&E.matches(b,p,g,0);ck(matched===(d.ack&&fault!=='ack-drop'),'ACK match');if(matched)confirmed.add(key({p,g}));ck(s.records.length<=CAP,'bound');ck(new Set(s.semantic.effects).size===s.semantic.effects.length,'no repeat effect');pcm.set(x,2*i*STEP);pcm.set(ack,(2*i+1)*STEP);trace.push({start:2*i*STEP,g,offered:p,fault:fault??null,reopen:!!reopen,decoded:a,decision:d,ack:b,confirmed:matched,state:s});}
 const end=r.snapshot(),w=end.semantic.world,typed=policy==='typed';ck(eq(receiver(dir).snapshot(),end),'reopen');
 if(name==='reverse')ck(w.state.value===(typed?'stopped':'open'),'version order');
 if(name==='gap'){ck(eq(w.tape.map(x=>x.value),typed?['open','stopped']:['stopped','open']),'dependency order');ck(trace[0].decision.semantic===(typed?'buffered':'applied'),'receipt distinct');ck(trace[2].decision.decision==='duplicate'&&trace[3].decision.decision==='occurrence-conflict','dup and conflict');}
 if(name==='lost'){ck(w.tape.length===(typed?0:1)&&w.events.length===1,'gap does not block independent event');ck(trace[1].confirmed,'buffer receipt');}
 if(name==='interleave')ck(eq(w.tape.map(x=>x.index),[1,2])&&w.events.length===2,'stream index not global generation');
 if(name==='version')ck(w.state.value===(typed?'stopped':'fault'),'version conflict');
 if(name==='dependencyConflict')ck(typed?w.blocked&&w.tape.length===0:w.tape.length===3,'conflicting dependency');
 if(name==='authority')ck(trace[1].decision.decision==='no-receipt'&&w.state.value===(typed?'stopped':'open'),'claimed source remains forgeable');
 if(name==='repair')ck(w.events.length===1&&trace[0].decision.decision==='no-receipt'&&!trace[1].confirmed&&trace[2].confirmed,'role loss and ACK retry');
 if(name==='capacity')ck(trace[4].decision.decision==='capacity'&&trace[5].decision.decision==='duplicate','capacity with old exact duplicate');
 const file=`${seed}-${name}-${policy}.wav`,raw=wav(pcm);fs.writeFileSync(path.join(out,file),raw);const bytes=fs.readFileSync(path.join(out,file));for(const [i,t] of trace.entries())for(const [j,a] of [t.decoded,t.ack].entries()){const x=Int16Array.from({length:STEP},(_,n)=>bytes.readInt16LE(44+2*((2*i+j)*STEP+n)));assert.deepEqual(R.acquire(x,true,127),a);rescans++;}rows.push({seed,name,policy,file,sha256:hash(bytes),samples:pcm.length,confirmed:confirmed.size,receipts:end.records.length,effects:end.semantic.effects.length,final:end.semantic,trace});}
 const dir=path.join(root,'bad');provision(dir,'typed');const file=path.join(dir,'state.json'),original=fs.readFileSync(file);fs.writeFileSync(file,'{}');assert.throws(()=>receiver(dir));checks++;fs.writeFileSync(file,original);fs.unlinkSync(file);assert.throws(()=>receiver(dir));checks++;
 const receipt={schema:'mhac-semantic-v33',parent:PARENT,rate:RATE,step:STEP,checks,rescans,rows};fs.writeFileSync(path.join(out,'receipt.json'),JSON.stringify(receipt,null,2)+'\n');console.log(JSON.stringify({checks,rescans,sessions:rows.length,totals:Object.fromEntries(policies.map(p=>[p,rows.filter(r=>r.policy===p).reduce((m,r)=>({receipts:m.receipts+r.receipts,confirmed:m.confirmed+r.confirmed,effects:m.effects+r.effects}),{receipts:0,confirmed:0,effects:0})]))}));
 }finally{fs.rmSync(root,{recursive:true,force:true});}}
module.exports={contract,interpret,provision,receiver};if(require.main===module)main(process.argv[2]||'semantic-v33-output');
