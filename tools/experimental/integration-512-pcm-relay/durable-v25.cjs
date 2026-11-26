'use strict';
// Refs #512. Single-writer Linux host experiment, not physical exactly-once or authentication.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{frame}=require('./relay.cjs');
const digest=x=>crypto.createHash('sha256').update(JSON.stringify(x)).digest('hex');
const validInt=(n,lo,hi)=>Number.isSafeInteger(n)&&n>=lo&&n<=hi;
const empty=()=>Array(17).fill(null);
function syncDir(dir){const fd=fs.openSync(dir,'r');try{fs.fsyncSync(fd);}finally{fs.closeSync(fd);}}
function pack(state){return JSON.stringify({state,sha256:digest(state)})+'\n';}
function read(file){const fd=fs.openSync(file,'r');try{if(fs.fstatSync(fd).size>16384)throw Error('state size');const {state,sha256}=JSON.parse(fs.readFileSync(fd,'utf8'));if(!state||state.schema!=='mhac-v25'||digest(state)!==sha256||!Array.isArray(state.last)||state.last.length!==17||state.last[0]!==null||!state.last.every(x=>x===null||(validInt(x.g,0,255)&&validInt(x.count,1,Number.MAX_SAFE_INTEGER)&&typeof x.k==='string'&&x.k.length<=1024&&/^[0-9,]+$/.test(x.k))))throw Error('state invalid');return state;}finally{fs.closeSync(fd);}}
function provision(dir){fs.mkdirSync(dir);const fd=fs.openSync(path.join(dir,'state.json'),'wx');try{fs.writeFileSync(fd,pack({schema:'mhac-v25',last:empty()}));fs.fsyncSync(fd);}finally{fs.closeSync(fd);}syncDir(dir);syncDir(path.dirname(dir));}
function commit(dir,state,checkpoint){const tmp=path.join(dir,'pending.json'),fd=fs.openSync(tmp,'w');try{fs.writeFileSync(fd,pack(state));fs.fsyncSync(fd);}finally{fs.closeSync(fd);}checkpoint('prepared');fs.renameSync(tmp,path.join(dir,'state.json'));checkpoint('renamed');syncDir(dir);checkpoint('durable');}
function receiver(dir,maxJump=256,checkpoint=()=>{}){
 if(!validInt(maxJump,1,256))throw Error('maxJump');const file=path.join(dir,'state.json');read(file);
 return {snapshot:()=>read(file),receive(e,version=1){
  const refuse=decision=>({decision,ack:false,apply:false});
  if(e.status!=='receipt-candidate'||!e.packet||e.packet.kind!==0)return refuse('no-receipt');
  const p=e.packet,g=e.generation;if(!validInt(p.source,1,16)||!validInt(g,0,255)||p.version!==version)return refuse('context-refused');
  const state=read(file),prev=state.last[p.source],k=frame(p).join(',');
  if(prev){if(g<prev.g)return refuse('stale');if(g===prev.g){if(prev.k!==k)return refuse('conflict');syncDir(dir);return {decision:'duplicate',ack:true,apply:false};}}
  if(g-(prev?prev.g:-1)>maxJump)return refuse('forward-gap');
  const count=(prev?.count||0)+1;if(!Number.isSafeInteger(count))return refuse('count-exhausted');
  // The count IS the simulated semantic effect; it shares the same atomic file as dedup state.
  state.last[p.source]={g,k,count};commit(dir,state,checkpoint);return {decision:'new',ack:true,apply:true};
 }};
}
module.exports={receiver,provision};
