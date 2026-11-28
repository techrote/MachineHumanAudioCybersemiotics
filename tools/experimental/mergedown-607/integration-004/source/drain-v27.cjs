'use strict';
// Refs #512; single-writer experimental receiver, no authentication or external effects.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{frame}=require('./relay.cjs');
const hash=s=>crypto.createHash('sha256').update(s).digest('hex'),eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b),id=n=>Number.isInteger(n)&&n>=0&&n<256,blank=()=>Array(17).fill(null);
function sync(d){const f=fs.openSync(d,'r');try{fs.fsyncSync(f);}finally{fs.closeSync(f);}}
const record=x=>x===null||(x&&id(x.g)&&typeof x.k==='string'&&x.k.length<=1024&&/^[0-9,]+$/.test(x.k));
const records=a=>Array.isArray(a)&&a.length===17&&a[0]===null&&a.every(record);
function validate(s){if(!s||s.schema!=='mhac-drain-v27'||!['immediate','drain'].includes(s.policy)||!id(s.active)||!records(s.last)||!Number.isSafeInteger(s.count)||s.count<0||!(s.old===null||(s.policy==='drain'&&s.old.e===s.active-1&&id(s.old.e)&&records(s.old.last)&&Number.isInteger(s.old.credits)&&s.old.credits>=0&&s.old.credits<=2)))throw Error('invalid state');return s;}
function write(d,s,first=false){validate(s);const data=JSON.stringify(s),f=fs.openSync(path.join(d,first?'state.json':'pending.json'),first?'wx':'w');try{fs.writeFileSync(f,JSON.stringify({state:s,sha256:hash(data)})+'\n');fs.fsyncSync(f);}finally{fs.closeSync(f);}if(!first)fs.renameSync(path.join(d,'pending.json'),path.join(d,'state.json'));sync(d);}
function read(d){const f=fs.openSync(path.join(d,'state.json'),'r');try{if(fs.fstatSync(f).size>65536)throw Error('state too large');const p=JSON.parse(fs.readFileSync(f,'utf8'));if(hash(JSON.stringify(p.state))!==p.sha256)throw Error('state digest');return validate(p.state);}finally{fs.closeSync(f);}}
function provision(d,policy){fs.mkdirSync(d);write(d,{schema:'mhac-drain-v27',policy,active:0,last:blank(),old:null,count:0},true);sync(path.dirname(d));}
const result=(decision,ack=false,apply=false)=>({decision,ack,apply});
function receiver(d){read(d);return {snapshot:()=>read(d),grant(e){const s=read(d);if(!id(e)||e!==s.active+1||s.old) return false;s.old=s.policy==='drain'?{e:s.active,last:s.last,credits:2}:null;s.active=e;s.last=blank();write(d,s);return true;},retire(e){const s=read(d);if(!s.old||s.old.e!==e)return false;s.old=null;write(d,s);return true;},receive(a){const s=read(d),p=a.packet;if(a.status!=='receipt-candidate'||!p||p.kind!==0)return result('no-receipt');if(!id(a.epoch)||!id(a.generation)||!Number.isInteger(p.source)||p.source<1||p.source>16||p.version!==1)return result('context-refused');const k=frame(p).join(','),g=a.generation,i=p.source;
 if(a.epoch>s.active)return result('epoch-not-granted');if(a.epoch<s.active){const o=s.old;if(!o||a.epoch!==o.e)return result('old-epoch');const prev=o.last[i];if(!prev||prev.g!==g||prev.k!==k)return result('drain-not-exact');if(!o.credits)return result('drain-budget');o.credits--;write(d,s);return result('drain-ack',true);}
 const prev=s.last[i];if(prev&&g<prev.g)return result('stale');if(prev&&g===prev.g){if(prev.k!==k)return result('conflict');sync(d);return result('duplicate',true);}if(s.count===Number.MAX_SAFE_INTEGER)return result('count-exhausted');s.last[i]={g,k};s.count++;write(d,s);return result('new',true,true);
 }};}
module.exports={provision,receiver};
