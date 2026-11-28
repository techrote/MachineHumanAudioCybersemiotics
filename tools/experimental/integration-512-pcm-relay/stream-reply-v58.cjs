'use strict';
// Refs #512. Experimental v45 reply TX, preserving the exact v56 descriptor semantics.
// No new wire format, no production authentication or hardware qualification claim.
const crypto=require('node:crypto');
const F=require('./fresh-v45.cjs'), A=require('./session-v40.cjs');
const C=require('./sequence-v22.cjs'), G=require('./generation-v23.cjs');
const E=require('./epoch-v26.cjs'), B=require('./bound-v2.cjs');
const D=require('./compact-queue-v56.cjs'), {frame}=require('./relay.cjs');
const MAX_CHUNK=1024, RATE=16000;
const labels=['applied','buffered','superseded','same-version','version-conflict','dependency-conflict','same-operation','blocked'];
function parity6(d){const mod=x=>(x%17+17)%17,a=d.reduce((s,x)=>s+x,0),b=d.reduce((s,x,i)=>s+x*(i+1),0),z=mod(7*a-b);return [...d,mod(-a-z),z];}
function outcomeToken(p,g,s,v){const c=labels.indexOf(s)+1;if(!c||p.kind!==1||!Number.isInteger(v)||v<1||v>4)throw Error('outcome fields');let n=crypto.createHash('sha256').update('MHAC-outcome-v34:').update(Buffer.from([...frame(p),g,0,c,v])).digest().readUInt32BE(0)%17**6;const t=[];for(let i=0;i<6;i++){t.push(n%17);n=Math.floor(n/17);}return [...t,c,v];}
function prepare(descriptor,reporter=null){const d=D.unpack(descriptor);let report=d.report;if(reporter){const e=reporter.snapshot().epochs.find(x=>x.session===d.session);if(!e)return null;const r=e.records.find(x=>x.g===d.g&&JSON.stringify(frame(x.p))===JSON.stringify(frame(d.p)));report=r?e.reports[r.p.source+':'+d.g]:null;}
 const p={...d.p,kind:1},s=report?report.status:'blocked',v=report?report.revision:1,kind=report?'report':'absent',n=A.nonce(p,d.g),ctx=F.context(d.session,kind,d.n);
 const segments=[];let end=0;function add(length,f=0,active=0,ramp=16){if(length<0)throw Error('layout');if(length){segments.push({length,f,active,ramp});end+=length;}}function pad(target){add(target-end);}function control(digits){add(320,3500,320);add(320,3100,320);for(const x of C.protect(digits))add(640,400+100*x,480);}
 pad(64);add(320,2300,320,32);add(320,2700,320,32);for(const x of [...frame(p),...parity6(B.tag(p))])add(1280,400+100*x,960,32);
 pad(G.HEAD+64);control(G.token(p,d.g,'body'));pad(G.STEP+64);control(E.token(p,d.g,0));pad(E.STEP+64);control(outcomeToken(p,d.g,s,v));
 const auth=Buffer.alloc(12);auth.writeUInt32BE(n);A.tag(ctx,64,'outcome',p,d.g,0,s,v,n).copy(auth,4);const digits=[...auth].flatMap(x=>[1+(x>>4),1+(x&15)]);const base=E.STEP+C.FRAME+128;if(base+3*(C.FRAME+128)!==F.BASE)throw Error('base layout');for(let i=0;i<3;i++){pad(base+i*(C.FRAME+128)+64);control(digits.slice(i*8,i*8+8));}pad(F.L);
 let segment=0,offset=0,remaining=F.L;
 return {samples:F.L,segments:segments.length,status:report?.status??'no-exact-retained-record',revision:report?.revision??null,get remaining(){return remaining;},pull(out){if(!(out instanceof Int16Array)||out.length<1||out.length>MAX_CHUNK)throw Error('output chunk bound');let written=0;while(written<out.length&&remaining){const z=segments[segment],take=Math.min(out.length-written,z.length-offset);for(let j=0;j<take;j++){const i=offset+j;out[written+j]=i>=z.active?0:Math.round(4096*Math.min(1,i/z.ramp,(z.active-1-i)/z.ramp)*Math.sin(2*Math.PI*z.f*i/RATE+d.phase));}written+=take;offset+=take;remaining-=take;if(offset===z.length){segment++;offset=0;}}return written;}};
}
module.exports={prepare,MAX_CHUNK,RATE};
