'use strict';
// Refs #512. Single-writer, simulated independently trusted witness; synthetic only.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const V=require('./epochs-v41.cjs');
const digest=b=>crypto.createHash('sha256').update(b).digest('hex');
function read(f){const fd=fs.openSync(f,'r');try{const b=Buffer.alloc(V.LIMIT+1);let n=0;while(n<b.length){const k=fs.readSync(fd,b,n,b.length-n,n);if(!k)break;n+=k;}if(n>V.LIMIT)throw Error('size');return b.subarray(0,n);}finally{fs.closeSync(fd);}}
function put(f,b){if(b.length>V.LIMIT)throw Error('size');const t=f+'.write',fd=fs.openSync(t,'w');try{fs.writeFileSync(fd,b);fs.fsyncSync(fd);}finally{fs.closeSync(fd);}fs.renameSync(t,f);const d=fs.openSync(path.dirname(f),'r');try{fs.fsyncSync(d);}finally{fs.closeSync(d);}}
const seal=(s,b)=>Buffer.from(JSON.stringify({commit:s.commit,sha256:digest(b)}));
function provision(dir,w){V.provision(dir,w);fs.mkdirSync(path.join(dir,'stage'));}
function open(dir,w){const current=path.join(dir,'state.json'),stage=path.join(dir,'stage'),candidate=path.join(stage,'state.json');
 function match(d,f,a){try{const b=read(f),s=V.open(d).snapshot();return seal(s,b).equals(a)?{s,b}:null;}catch{return null;}}
 function recover(){const a=read(w),c=match(dir,current,a);if(c)return {state:c.s,recovery:'current'};const p=match(stage,candidate,a);if(!p)throw Error('no-witness-matching-state');put(current,p.b);return {state:p.s,recovery:'candidate'};}
 function transact(action,cut='none'){const before=recover().state;const fail=k=>{if(cut===k)throw Error('cut:'+k);};fail('before-stage');put(candidate,read(current));const r=V.open(stage),result=action(r),after=r.snapshot();if(after.commit===before.commit)return result;if(after.commit!==before.commit+1)throw Error('commit-step');const b=read(candidate);fail('after-stage');put(w,seal(after,b));fail('after-witness');put(current,b);fail('after-publish');return result;}
 const initial=recover().recovery;return {initial,snapshot:()=>recover().state,transition:(e,s,n=false,cut)=>transact(r=>r.transition(e,s,n),cut),receive:(role,pcm,cut)=>transact(r=>r.receive(role,pcm),cut),outcome:(...args)=>{recover();return V.open(dir).outcome(...args);}};
}
module.exports={provision,open};
