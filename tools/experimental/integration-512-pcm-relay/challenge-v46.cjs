'use strict';
// Refs #512. Single writer; simulated independent witness; public test keys.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const F=require('./fresh-v45.cjs'),{frame}=require('./relay.cjs');
const LIMIT=16384, MAX=0xffffffff;
const bytes=x=>Buffer.from(JSON.stringify(x));
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
function read(f){const fd=fs.openSync(f,'r');try{const b=Buffer.alloc(LIMIT+1);let n=0;while(n<b.length){const k=fs.readSync(fd,b,n,b.length-n,n);if(!k)break;n+=k;}if(n>LIMIT)throw Error('size');return b.subarray(0,n);}finally{fs.closeSync(fd);}}
function put(f,b){if(b.length>LIMIT)throw Error('size');const t=f+'.write',fd=fs.openSync(t,'w');try{fs.writeFileSync(fd,b);fs.fsyncSync(fd);}finally{fs.closeSync(fd);}fs.renameSync(t,f);const d=fs.openSync(path.dirname(f),'r');try{fs.fsyncSync(d);}finally{fs.closeSync(d);}}
function checked(s){if(s.schema!=='mhac-challenge-v46'||!Number.isSafeInteger(s.commit)||s.commit<0||!Number.isInteger(s.session)||s.session<1||s.session>255||!Number.isInteger(s.g)||s.g<0||s.g>255||!Number.isInteger(s.high)||s.high<0||s.high>MAX||!(s.pending===null||s.pending===s.high&&s.high>0)||s.p.kind!==0||![1,2].includes(s.p.source))throw Error('state');frame(s.p);if(s.evidence!==null){const e=s.evidence;if(!Number.isInteger(e.challenge)||e.challenge<1||e.challenge>s.high||e.challenge===s.pending||!['report','absent'].includes(e.kind)||!(e.kind==='absent'?e.status==='no-exact-retained-record'&&e.revision===null:['applied','buffered','superseded','same-version','version-conflict','dependency-conflict','same-operation','blocked'].includes(e.status)&&Number.isInteger(e.revision)&&e.revision>=1&&e.revision<=4))throw Error('evidence');}return s;}
const seal=(s,b)=>bytes({commit:s.commit,sha256:hash(b)});
function provision(dir,w,p,g,session=1,high=0){const s=checked({schema:'mhac-challenge-v46',commit:0,session,p,g,high,pending:null,evidence:null}),b=bytes(s);if(fs.existsSync(w))throw Error('existing witness');fs.mkdirSync(dir);put(path.join(dir,'current'),b);put(w,seal(s,b));}
function open(dir,w){const current=path.join(dir,'current'),candidate=path.join(dir,'candidate');
 function recover(){const a=read(w);for(const f of [current,candidate]){let s,b;try{b=read(f);s=checked(JSON.parse(b));}catch{continue;}if(!seal(s,b).equals(a))continue;if(f===candidate)put(current,b);return s;}throw Error('no-witness-matching-state');}
 function commit(s,t,cut){const next=checked({...t,commit:s.commit+1}),b=bytes(next);cut('before-stage');put(candidate,b);cut('after-stage');put(w,seal(next,b));cut('after-witness');put(current,b);cut('after-publish');return next;}
 function allocate(cut=()=>{}){const s=recover();if(s.high===MAX)throw Error('challenge-exhausted');return commit(s,{...s,high:s.high+1,pending:s.high+1},cut).pending;}
 function query(phase){const s=recover();if(s.pending===null)throw Error('no-pending-challenge');return F.query(s.session,s.p,s.g,s.pending,phase);}
 function receive(pcm,cut=()=>{}){const s=recover();if(s.pending===null)return {decision:'no-pending-challenge'};const d=F.decodeReply(s.session,s.p,s.g,s.pending,pcm,true);if(d.kind==='unknown')return {decision:'refused',decoded:d};const e={challenge:s.pending,kind:d.kind,status:d.status,revision:d.revision??null};commit(s,{...s,pending:null,evidence:e},cut);return {decision:'consumed',evidence:e,decoded:d};}
 recover();return {snapshot:recover,allocate,query,receive};}
module.exports={provision,open,LIMIT,MAX};
