'use strict';
// Refs #512. Synthetic, single writer, independently retained witness assumed.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const T=require('./transition-control-v48.cjs'), U=require('./status-control-v49.cjs');
const F=require('./fresh-v45.cjs'),S=require('./semantic-v33.cjs'),{frame}=require('./relay.cjs');
const MAX=0xffffffff,CAP=4,LIMIT=16384;
const bytes=x=>Buffer.from(JSON.stringify(x));
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const key=(p,g)=>p.source+':'+g;
function read(f){const fd=fs.openSync(f,'r');try{const b=Buffer.alloc(LIMIT+1);let n=0;while(n<b.length){const k=fs.readSync(fd,b,n,b.length-n,n);if(!k)break;n+=k;}if(n>LIMIT)throw Error('size');return b.subarray(0,n);}finally{fs.closeSync(fd);}}
function put(f,b){if(b.length>LIMIT)throw Error('size');const t=f+'.write',fd=fs.openSync(t,'w');try{fs.writeFileSync(fd,b);fs.fsyncSync(fd);}finally{fs.closeSync(fd);}fs.renameSync(t,f);const d=fs.openSync(path.dirname(f),'r');try{fs.fsyncSync(d);}finally{fs.closeSync(d);}}
const u=x=>Number.isInteger(x)&&x>=0&&x<=MAX;
function checked(s){if(s.schema!=='mhac-status-v49'||!['isolated','shared'].includes(s.policy)||!Number.isSafeInteger(s.commit)||s.commit<0||!u(s.high)||!u(s.statusHigh)||!(s.statusPending===null||s.next!==null&&s.statusPending===s.statusHigh&&s.statusHigh>0)||!Number.isInteger(s.session)||s.session<1||s.session>255||!(s.next===null||s.next===s.session+1&&s.next<=255)||!Array.isArray(s.offers)||s.offers.length>CAP)throw Error('state');const keys=new Set(),pending=new Set();for(const o of s.offers){if(!S.contract(o.p)||!Number.isInteger(o.g)||o.g<0||o.g>255||keys.has(key(o.p,o.g))||!u(o.high)||o.high>s.high||!(o.pending===null||o.pending===o.high&&o.high>0))throw Error('offer');frame(o.p);keys.add(key(o.p,o.g));if(o.pending!==null){if(s.policy==='shared'&&pending.has(o.pending))throw Error('challenge collision');pending.add(o.pending);}if(o.evidence!==null){const e=o.evidence;if(!u(e.challenge)||!e.challenge||!Number.isInteger(e.session)||e.session<1||e.session>s.session||(e.session===s.session&&(e.challenge>o.high||e.challenge===o.pending))||!(e.kind==='absent'?e.status==='no-exact-retained-record'&&e.revision===null:e.kind==='report'&&['applied','buffered','superseded','same-version','version-conflict','dependency-conflict','same-operation','blocked'].includes(e.status)&&Number.isInteger(e.revision)&&e.revision>=1&&e.revision<=4))throw Error('evidence');}}return s;}
const seal=(s,b)=>bytes({commit:s.commit,sha256:hash(b)});
function provision(dir,w,policy,session=1,high=0){const s=checked({schema:'mhac-status-v49',policy,session,next:null,high,statusHigh:0,statusPending:null,commit:0,offers:[]}),b=bytes(s);if(fs.existsSync(w))throw Error('existing witness');fs.mkdirSync(dir);put(path.join(dir,'current'),b);put(w,seal(s,b));}
function open(dir,w){const current=path.join(dir,'current'),candidate=path.join(dir,'candidate');
 function recover(){const a=read(w);for(const f of [current,candidate]){let s,b;try{b=read(f);s=checked(JSON.parse(b));}catch{continue;}if(!seal(s,b).equals(a))continue;if(f===candidate)put(current,b);return s;}throw Error('no-witness-matching-state');}
 function change(s,cut=()=>{}){s.commit++;checked(s);const b=bytes(s);cut('before-stage');put(candidate,b);cut('after-stage');put(w,seal(s,b));cut('after-witness');put(current,b);cut('after-publish');return s;}
 function advance(s){s.session=s.next;s.next=null;s.high=0;s.statusHigh=0;s.statusPending=null;for(const o of s.offers){o.high=0;o.pending=null;}}
 function find(s,id){const o=s.offers.find(x=>key(x.p,x.g)===id);if(!o)throw Error('unknown-offer');return o;}
 recover();return {snapshot:recover,
 begin(cut){const s=recover();if(s.next!==null)throw Error('transition-pending');if(s.session===255)throw Error('session-exhausted');s.next=s.session+1;change(s,cut);},
 prepare(phase){const s=recover();if(s.next===null)throw Error('no-transition');return T.encode(s.session,s.next,'prepare',phase);},
 finish(pcm,cut){const s=recover();if(s.next===null||!T.decode(s.session,s.next,'ack',pcm))return 'refused';advance(s);change(s,cut);return 'transitioned';},
 allocateStatus(cut){const s=recover();if(s.next===null)throw Error('no-transition');if(s.statusHigh===MAX)throw Error('status-exhausted');s.statusPending=++s.statusHigh;change(s,cut);return s.statusPending;},
 status(phase){const s=recover();if(s.statusPending===null)throw Error('no-status');return U.encode(s.session,s.next,s.statusPending,'status',phase);},
 finishStatus(pcm,cut){const s=recover();if(s.statusPending===null)return 'refused';const result=U.reply(s.session,s.next,s.statusPending,pcm);if(result==='refused')return result;if(result==='committed')advance(s);else s.statusPending=null;change(s,cut);return result;},
 cancel(id){const s=recover(),o=find(s,id);if(s.next!==null)throw Error('transition-pending');if(o.pending===null)return false;o.pending=null;change(s);return true;},
 register(p,g){const s=recover(),id=key(p,g);if(s.next!==null)throw Error('transition-pending');if(s.offers.some(x=>key(x.p,x.g)===id))throw Error('duplicate-offer');if(s.offers.length===CAP)throw Error('capacity');s.offers.push({p,g,high:0,pending:null,evidence:null});change(s);return id;},
 retire(id){const s=recover(),o=find(s,id);if(s.next!==null)throw Error('transition-pending');if(o.pending!==null)throw Error('pending-offer');s.offers=s.offers.filter(x=>x!==o);change(s);},
 allocate(id,cut){const s=recover(),o=find(s,id),h=s.policy==='shared'?s.high:o.high;if(s.next!==null)throw Error('transition-pending');if(h===MAX)throw Error('challenge-exhausted');o.high=h+1;s.high=Math.max(s.high,o.high);o.pending=o.high;change(s,cut);return o.pending;},
 query(id,phase){const s=recover(),o=find(s,id);if(s.next!==null)throw Error('transition-pending');if(o.pending===null)throw Error('no-pending');return F.query(s.session,o.p,o.g,o.pending,phase);},
 receive(pcm,cut){const s=recover(),hits=[];if(s.next!==null)return {decision:'transition-pending'};for(const o of s.offers){if(o.pending===null)continue;const d=F.decodeReply(s.session,o.p,o.g,o.pending,pcm,true);if(d.kind!=='unknown')hits.push({o,d});}if(hits.length!==1)return {decision:hits.length?'ambiguous':'refused'};const {o,d}=hits[0],id=key(o.p,o.g);o.evidence={session:s.session,challenge:o.pending,kind:d.kind,status:d.status,revision:d.revision??null};o.pending=null;change(s,cut);return {decision:'consumed',id,evidence:o.evidence};}
 };}
module.exports={provision,open,CAP,MAX,LIMIT};
