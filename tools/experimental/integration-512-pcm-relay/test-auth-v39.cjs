'use strict';
// Refs #512. Known-slot negative controls; no security assurance or human evidence.
const A=require('./auth-v39.cjs'),O=require('./outcome-v34.cjs'),V=require('./paired-v38.cjs'),C=require('./sequence-v22.cjs'),{frame}=require('./relay.cjs'),fs=require('node:fs'),assert=require('node:assert/strict');
const p={kind:1,source:1,version:1,actor:9,event:7,seq:2,tree:['verify',['stopped']]},ctx=A.fixture(),phase=.37,n=0xfedcba98,rows=[];
for(const role of ['outcome','confirm']){
 const w=A.encode(ctx,role,p,1,0,'applied',2,n,phase),a=A.acquire(ctx,role,w);assert.equal(a.challenge,n);assert.equal(a.authenticated,true);
 const badKey=A.acquire(A.fixture(1,9),role,w),badSession=A.acquire(A.fixture(2),role,w);assert.equal(badKey.reason,'mac');assert.equal(badSession.reason,'mac');
 const stripped=w.slice();stripped.fill(0,A.BASE);assert.equal(A.acquire(ctx,role,stripped).reason,'extension');
 const erased=w.slice();erased.fill(0,A.BASE+64+C.FRAME/11,A.BASE+C.FRAME);assert.equal(A.acquire(ctx,role,erased).status,'refused');
 const other={...p,tree:['verify',['fault']]},splice=w.slice();splice.set((role==='outcome'?O:V).encode(other,1,0,'applied',2,phase));assert.equal(A.acquire(ctx,role,splice).reason,'mac');
 const differentRole=role==='outcome'?'confirm':'outcome',sub=w.slice();sub.set((role==='outcome'?V:O).encode(p,1,0,'applied',2,phase));assert.equal(A.acquire(ctx,differentRole,sub).reason,'mac');
 const validAgain=A.acquire(ctx,role,w);assert.deepEqual(validAgain,a); // codec is intentionally stateless; lifecycle admission is separate.
 rows.push({role,challenge:n,frame:frame(p),generation:1,epoch:0,statusIndex:1,revision:2,sessionHex:ctx.session.toString('hex'),keyHex:ctx[role].toString('hex'),tagHex:A.mac(ctx,role,p,1,0,'applied',2,n).toString('hex'),wrongKey:badKey.reason,wrongSession:badSession.reason,strip:'refused',erase:'refused',semanticSplice:'refused',roleSplice:'refused',sameSessionExactReplay:'accepted-by-stateless-codec'});
}
fs.writeFileSync(process.argv[2]||'auth-controls-v39.json',JSON.stringify(rows,null,2)+'\n');console.log('2 role controls; 18 assertions passed');
