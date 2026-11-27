'use strict';
// Refs #512. Synthetic single-namespace monotonic session transition.
const crypto=require('node:crypto'),A=require('./session-v40.cjs'),F=require('./fresh-v45.cjs'),{frame}=require('./relay.cjs');
const P={kind:0,source:1,version:1,actor:9,event:7,seq:1,tree:['verify',['open']]};
function ctx(old,role){return {...A.ctx(old),session:crypto.createHash('sha256').update('MHAC-v48:'+role+'\0').update(A.ctx(old).session).digest().subarray(0,16)};}
function encode(old,next,role,phase){if(old<1||next!==old+1||next>255||!['prepare','ack'].includes(role))throw Error('transition');return F.wrap(A.encode(ctx(old,role),64,'data',P,next,null,0,A.nonce(P,next),phase));}
function decode(old,next,role,pcm){if(old<1||next!==old+1||next>255||pcm.length!==F.L)return false;const d=A.decode(ctx(old,role),64,'data',pcm.subarray(0,F.BASE));return !!(d.authenticated&&d.generation===next&&JSON.stringify(frame(d.packet))===JSON.stringify(frame(P)));}
function answer(reporter,pcm,phase,cut){const s=reporter.snapshot();if(s.epochs.length!==1||s.high!==s.epochs[0].session)throw Error('single-namespace-only');const current=s.high;
 if(decode(current,current+1,'prepare',pcm)){if(reporter.transition(0,current+1,false,cut)!=='transitioned')throw Error('transition-refused');return {decision:'transitioned',pcm:encode(current,current+1,'ack',phase)};}
 if(decode(current-1,current,'prepare',pcm))return {decision:'repeat-ack',pcm:encode(current-1,current,'ack',phase)};
 return {decision:'refused',pcm:null};}
module.exports={encode,decode,answer};
