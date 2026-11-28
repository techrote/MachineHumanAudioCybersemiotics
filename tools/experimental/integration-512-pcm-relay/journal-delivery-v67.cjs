'use strict';
// Refs #512. v67 bounded durable delivery; distinct schema, single writer, synthetic continuity witness.
// Parent 7430b06f8dfcbfa82765109da5ec8c26d2bdb243; v66 blob 717125194caaf427f47ebd71312c5f32d73b981f.
const RX=require('./stream-rx-v63.cjs');
const ASYNC=require('./async-rx-v65.cjs');
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const F=require('./fresh-v45.cjs'),S=require('./semantic-v33.cjs'),{frame}=require('./relay.cjs');
const MAX=0xffffffff,CAP=4,DELIVERY_CAP=2,LIMIT=16384;
const bytes=x=>Buffer.from(JSON.stringify(x));
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const key=(p,g)=>p.source+':'+g;
function read(f){const fd=fs.openSync(f,'r');try{const b=Buffer.alloc(LIMIT+1);let n=0;while(n<b.length){const k=fs.readSync(fd,b,n,b.length-n,n);if(!k)break;n+=k;}if(n>LIMIT)throw Error('size');return b.subarray(0,n);}finally{fs.closeSync(fd);}}
function put(f,b){if(b.length>LIMIT)throw Error('size');const t=f+'.write',fd=fs.openSync(t,'w');try{fs.writeFileSync(fd,b);fs.fsyncSync(fd);}finally{fs.closeSync(fd);}fs.renameSync(t,f);const d=fs.openSync(path.dirname(f),'r');try{fs.fsyncSync(d);}finally{fs.closeSync(d);}}
const u=x=>Number.isInteger(x)&&x>=0&&x<=MAX;
const token=(session,r)=>hash(bytes(['mhac-delivery-v67',session,r.seq,r.id,r.p,r.g,r.evidence]));
function checkDelivery(s){if(!Array.isArray(s.delivery)||s.delivery.length>DELIVERY_CAP)throw Error('delivery-capacity');let prev=0;for(const r of s.delivery){if(!Number.isSafeInteger(r.seq)||r.seq<=prev||r.seq>s.commit||!S.contract(r.p)||!Number.isInteger(r.g)||r.g<0||r.g>255||r.id!==key(r.p,r.g)||!r.evidence||!u(r.evidence.challenge)||!r.evidence.challenge||r.token!==token(s.session,r))throw Error('delivery-record');prev=r.seq;}return s;}
function checked(s){if(s.schema!=='mhac-delivery-v67'||!['isolated','shared'].includes(s.policy)||!Number.isSafeInteger(s.commit)||s.commit<0||!u(s.high)||!Number.isInteger(s.session)||s.session<1||s.session>255||!Array.isArray(s.offers)||s.offers.length>CAP)throw Error('state');const keys=new Set(),pending=new Set();for(const o of s.offers){if(!S.contract(o.p)||!Number.isInteger(o.g)||o.g<0||o.g>255||keys.has(key(o.p,o.g))||!u(o.high)||o.high>s.high||!(o.pending===null||o.pending===o.high&&o.high>0))throw Error('offer');frame(o.p);keys.add(key(o.p,o.g));if(o.pending!==null){if(s.policy==='shared'&&pending.has(o.pending))throw Error('challenge collision');pending.add(o.pending);}if(o.evidence!==null){const e=o.evidence;if(!u(e.challenge)||!e.challenge||e.challenge>o.high||e.challenge===o.pending||!(e.kind==='absent'?e.status==='no-exact-retained-record'&&e.revision===null:e.kind==='report'&&['applied','buffered','superseded','same-version','version-conflict','dependency-conflict','same-operation','blocked'].includes(e.status)&&Number.isInteger(e.revision)&&e.revision>=1&&e.revision<=4))throw Error('evidence');}}return checkDelivery(s);}
const seal=(s,b)=>bytes({commit:s.commit,sha256:hash(b)});
function provision(dir,w,policy,session=1,high=0){const s=checked({schema:'mhac-delivery-v67',policy,session,high,commit:0,offers:[],delivery:[]}),b=bytes(s);if(fs.existsSync(w))throw Error('existing witness');fs.mkdirSync(dir);put(path.join(dir,'current'),b);put(w,seal(s,b));}
function open(dir,w){const current=path.join(dir,'current'),candidate=path.join(dir,'candidate');
 function recover(){const a=read(w);for(const f of [current,candidate]){let s,b;try{b=read(f);s=checked(JSON.parse(b));}catch{continue;}if(!seal(s,b).equals(a))continue;if(f===candidate)put(current,b);return s;}throw Error('no-witness-matching-state');}
 function change(s,cut=()=>{}){s.commit++;checked(s);const b=bytes(s);cut('before-stage');put(candidate,b);cut('after-stage');put(w,seal(s,b));cut('after-witness');put(current,b);cut('after-publish');return s;}
 function find(s,id){const o=s.offers.find(x=>key(x.p,x.g)===id);if(!o)throw Error('unknown-offer');return o;}
 // Re-read persistent state at completion, not when the capture begins.
 function consume(decode,cut){const s=recover(),hits=[];for(const o of s.offers){if(o.pending===null)continue;const d=decode(s,o);if(d.kind!=='unknown')hits.push({o,d});}if(hits.length!==1)return {decision:hits.length?'ambiguous':'refused'};if(s.delivery.length===DELIVERY_CAP)return {decision:'backpressure'};const {o,d}=hits[0],id=key(o.p,o.g);o.evidence={challenge:o.pending,kind:d.kind,status:d.status,revision:d.revision??null};o.pending=null;const r={seq:s.commit+1,id,p:o.p,g:o.g,evidence:o.evidence};r.token=token(s.session,r);s.delivery.push(r);change(s,cut);return {decision:'consumed',id,evidence:o.evidence,deliveryToken:r.token};}
 recover();return {snapshot:recover,
 peek(){return recover().delivery[0]??null;},
 ack(t,cut){const s=recover(),r=s.delivery[0];if(!r||r.token!==t)return {decision:'refused'};s.delivery.shift();change(s,cut);return {decision:'acknowledged',token:t};},
 register(p,g){const s=recover(),id=key(p,g);if(s.offers.some(x=>key(x.p,x.g)===id))throw Error('duplicate-offer');if(s.offers.length===CAP)throw Error('capacity');s.offers.push({p,g,high:0,pending:null,evidence:null});change(s);return id;},
 retire(id){const s=recover(),o=find(s,id);if(o.pending!==null)throw Error('pending-offer');s.offers=s.offers.filter(x=>x!==o);change(s);},
 allocate(id,cut){const s=recover(),o=find(s,id),h=s.policy==='shared'?s.high:o.high;if(h===MAX)throw Error('challenge-exhausted');o.high=h+1;s.high=Math.max(s.high,o.high);o.pending=o.high;change(s,cut);return o.pending;},
 query(id,phase){const s=recover(),o=find(s,id);if(o.pending===null)throw Error('no-pending');return F.query(s.session,o.p,o.g,o.pending,phase);},
 receive(pcm,cut){return consume((s,o)=>F.decodeReply(s.session,o.p,o.g,o.pending,pcm,true),cut);},
 // Callback is advisory; durable FIFO is committed with evidence and survives callback failure.
 continuous(emit,cut){if(typeof emit!=='function')throw Error('callback');const rx=new ASYNC.Receiver();
  const onEvent=e=>{const result=e.acquisition.status==='candidate'?consume((s,o)=>ASYNC.admit(e.acquisition,s.session,[o]),cut):{decision:'refused'};emit({...e,...result});};
  return {push:x=>rx.push(x,onEvent),gap:n=>rx.gap(n,onEvent),finish:()=>rx.finish(onEvent),get pcmBytes(){return rx.pcmBytes;},get validityBytes(){return rx.validityBytes;}};
 },
 capture(){const rx=new RX.Receiver();return {push:x=>rx.push(x),gap:n=>rx.gap(n),get pcmBytes(){return rx.pcmBytes;},finish(cut){const acquisition=rx.finish();const result=consume((s,o)=>RX.admit(acquisition,s.session,[o]),cut);return {acquisition,...result};}};}
 };}
module.exports={provision,open,CAP,DELIVERY_CAP,MAX,LIMIT};
