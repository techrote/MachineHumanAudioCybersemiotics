'use strict';
// Refs #512. One offer, one locally provisioned session; simulated independent witness.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const A=require('./session-v40.cjs'),O=require('./outcome-v34.cjs'),E=require('./epoch-v26.cjs'),{frame}=require('./relay.cjs');
const LIMIT=16384, L=A.step(64), hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const labels=['applied','buffered','superseded','same-version','version-conflict','dependency-conflict','same-operation','blocked'];
const bytes=x=>Buffer.from(JSON.stringify(x));
function read(f){const fd=fs.openSync(f,'r');try{const b=Buffer.alloc(LIMIT+1);let n=0;while(n<b.length){const k=fs.readSync(fd,b,n,b.length-n,n);if(!k)break;n+=k;}if(n>LIMIT)throw Error('size');return b.subarray(0,n);}finally{fs.closeSync(fd);}}
function put(f,b){if(b.length>LIMIT)throw Error('size');const t=f+'.write',fd=fs.openSync(t,'w');try{fs.writeFileSync(fd,b);fs.fsyncSync(fd);}finally{fs.closeSync(fd);}fs.renameSync(t,f);const d=fs.openSync(path.dirname(f),'r');try{fs.fsyncSync(d);}finally{fs.closeSync(d);}}
function checked(s){if(s.schema!=='mhac-requester-v43'||!Number.isSafeInteger(s.commit)||s.commit<0||!Number.isInteger(s.session)||s.session<1||s.session>255||!Number.isInteger(s.g)||s.g<0||s.g>255||s.p.kind!==0||![1,2].includes(s.p.source))throw Error('state');frame(s.p);const b=s.belief;if(b!==null&&(!labels.includes(b.outcome)||!Number.isInteger(b.revision)||b.revision<1||b.revision>4||(b.conflict!==undefined&&b.conflict!==true)))throw Error('belief');return s;}
const seal=(s,b)=>bytes({commit:s.commit,sha256:hash(b)});
function provision(dir,w,p,g,session=1){const s=checked({schema:'mhac-requester-v43',commit:0,session,p,g,belief:null}),b=bytes(s);if(fs.existsSync(w))throw Error('existing witness');fs.mkdirSync(dir);put(path.join(dir,'current'),b);put(w,seal(s,b));}
function open(dir,w){const current=path.join(dir,'current'),candidate=path.join(dir,'candidate');
 function recover(){const a=read(w);for(const f of [current,candidate]){let b,s;try{b=read(f);s=checked(JSON.parse(b));}catch{continue;}if(!seal(s,b).equals(a))continue;if(f===candidate)put(current,b);return s;}throw Error('no-witness-matching-state');}
 function receive(pcm,cut=()=>{}){const s=recover(),d=A.decode(A.ctx(s.session),64,'outcome',pcm);if(!d.authenticated||!E.matches(d,s.p,s.g,0))return 'refused';const b=O.observe(s.belief,d,s.p,s.g,'outcome');if(bytes(b).equals(bytes(s.belief)))return 'unchanged';const t=checked({...s,commit:s.commit+1,belief:b}),raw=bytes(t);cut('before-stage');put(candidate,raw);cut('after-stage');put(w,seal(t,raw));cut('after-witness');put(current,raw);cut('after-publish');return 'retained';}
 function confirmation(phase){const s=recover(),b=s.belief;if(!b||b.conflict||b.outcome==='buffered')return null;const q={...s.p,kind:1};return A.encode(A.ctx(s.session),64,'confirm',q,s.g,b.outcome,b.revision,A.nonce(q,s.g),phase);}
 recover();return {snapshot:recover,receive,confirmation};
}
module.exports={provision,open,L,LIMIT};
