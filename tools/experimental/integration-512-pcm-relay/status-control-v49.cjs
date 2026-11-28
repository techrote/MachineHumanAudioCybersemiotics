'use strict';
// Refs #512. Synthetic status enquiry, independent authentication domains.
const crypto=require('node:crypto'),A=require('./session-v40.cjs'),F=require('./fresh-v45.cjs'),C=require('./sequence-v22.cjs'),{frame}=require('./relay.cjs');
const P={kind:0,source:1,version:1,actor:9,event:7,seq:1,tree:['verify',['open']]};
const valid=(old,next,n)=>Number.isInteger(old)&&old>=1&&next===old+1&&next<=255&&Number.isInteger(n)&&n>=1&&n<=0xffffffff;
function ctx(old,role,n){const b=Buffer.alloc(4);b.writeUInt32BE(n);return {...A.ctx(old),session:crypto.createHash('sha256').update('MHAC-v49:'+role+'\0').update(A.ctx(old).session).update(b).digest().subarray(0,16)};}
function encode(old,next,n,role,phase){if(!valid(old,next,n)||!['status','committed','not-committed'].includes(role))throw Error('status-context');const x=F.wrap(A.encode(ctx(old,role,n),64,'data',P,next,null,0,A.nonce(P,next),phase));if(role==='status'){const b=Buffer.alloc(4);b.writeUInt32BE(n);x.set(C.render(P,phase,()=>C.protect([...b].flatMap(v=>[1+(v>>4),1+(v&15)]))),F.BASE+64);}return x;}
function decode(old,next,n,role,x){if(!valid(old,next,n)||x.length!==F.L)return false;const d=A.decode(ctx(old,role,n),64,'data',x.subarray(0,F.BASE));return !!(d.authenticated&&d.generation===next&&JSON.stringify(frame(d.packet))===JSON.stringify(frame(P)));}
function challenge(x){if(x.length!==F.L)return 0;const z=C.acquire(x.subarray(F.BASE));if(z.status!=='ok'||Math.abs(z.start-64)>16||z.token.some(v=>v<1||v>16))return 0;const d=z.token.map(v=>v-1);return Buffer.from(Array.from({length:4},(_,i)=>16*d[2*i]+d[2*i+1])).readUInt32BE(0);}
function answer(reporter,x,phase){const s=reporter.snapshot(),n=challenge(x),hits=[];if(s.epochs.length!==1||s.high!==s.epochs[0].session)throw Error('single-namespace-only');for(const old of [s.high-1,s.high])if(decode(old,old+1,n,'status',x))hits.push(old);if(hits.length!==1)return {decision:'refused',pcm:null};const old=hits[0],role=s.high===old+1?'committed':'not-committed';return {decision:role,pcm:encode(old,old+1,n,role,phase)};}
function reply(old,next,n,x){const hits=['committed','not-committed'].filter(role=>decode(old,next,n,role,x));return hits.length===1?hits[0]:'refused';}
module.exports={encode,decode,answer,reply,challenge};
