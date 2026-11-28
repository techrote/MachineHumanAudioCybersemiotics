'use strict';
// Refs #512. Incremental nominal-clock forward waveform; same v40/v45 wire format.
const crypto=require('node:crypto'), A=require('./session-v40.cjs'), F=require('./fresh-v45.cjs'), G=require('./generation-v23.cjs'), E=require('./epoch-v26.cjs'), B=require('./bound-v2.cjs'), C=require('./sequence-v22.cjs'), S=require('./semantic-v33.cjs'), {frame}=require('./relay.cjs');
const MAX_CHUNK=1024, CAP=128, RATE=16000, BLOCK=C.FRAME+128;
function prepare({session=1,packet:p,generation:g,mode='data',challenge=null,phase=0,wrong=false}){
 if(!Number.isInteger(session)||session<0||session>255||!Number.isInteger(g)||g<0||g>255||!Number.isFinite(phase)||typeof wrong!=='boolean'||!p||p.kind!==0||![1,2].includes(p.source)||!S.contract(p)||!['data','query'].includes(mode))throw Error('descriptor');
 if(mode==='query'&&(!Number.isInteger(challenge)||challenge<1||challenge>0xffffffff)||mode==='data'&&challenge!==null)throw Error('challenge');
 if(mode==='query'&&wrong)throw Error('wrong-key query fixture unsupported');
 const table=new Uint16Array(CAP*4);let count=0,end=0;
 function add(n,f=0,active=0,ramp=16){if(!Number.isInteger(n)||n<0||n>65535||active>n||count>=CAP)throw Error('layout');if(n){table.set([n,f,active,ramp],4*count++);end+=n;}}
 function pad(target){add(target-end);}
 function control(d){add(320,3500,320);add(320,3100,320);for(const v of C.protect(d))add(640,400+100*v,480);}
 function digits(b){return [...b].flatMap(v=>[1+(v>>4),1+(v&15)]);}
 const words=frame(p),tag=B.tag(p),a=tag.reduce((s,v)=>s+v,0),b=tag.reduce((s,v,i)=>s+v*(i+1),0),mod=x=>(x%17+17)%17,z=mod(7*a-b);
 pad(64);add(320,2300,320,32);add(320,2700,320,32);for(const v of [...words,...tag,mod(-a-z),z])add(1280,400+100*v,960,32);
 pad(G.HEAD+64);control(G.token(p,g,'body'));pad(G.STEP+64);control(E.token(p,g,0));
 let k=crypto.createHash('sha256').update('MHAC-required-role-v29:').update(Buffer.from([...words,g,0,1])).digest().readUInt32BE(0)%17**6;const role=[];for(let i=0;i<6;i++){role.push(k%17);k=Math.floor(k/17);}pad(E.STEP+64);control([...role,1,15]);
 const base=E.STEP+BLOCK,nonce=A.nonce(p,g),ctx=mode==='query'?F.context(session,'query',challenge):A.ctx(session,wrong),auth=Buffer.alloc(12);auth.writeUInt32BE(nonce);A.tag(ctx,64,'data',p,g,0,null,0,nonce).copy(auth,4);const d=digits(auth);
 if(base+3*BLOCK!==F.BASE)throw Error('layout version');for(let i=0;i<3;i++){pad(base+i*BLOCK+64);control(d.slice(8*i,8*i+8));}
 if(mode==='query'){const q=Buffer.alloc(4);q.writeUInt32BE(challenge);pad(F.BASE+64);control(digits(q));}const samples=mode==='query'?F.L:F.BASE;pad(samples);
 let segment=0,offset=0,remaining=samples;
 return {samples,segments:count,descriptorBytes:table.byteLength,pcmBytes:0,get remaining(){return remaining;},pull(out){if(!(out instanceof Int16Array)||out.length<1||out.length>MAX_CHUNK)throw Error('output chunk bound');let written=0;while(written<out.length&&remaining){const j=4*segment,n=table[j],f=table[j+1],active=table[j+2],ramp=table[j+3],take=Math.min(out.length-written,n-offset);for(let h=0;h<take;h++){const i=offset+h;out[written+h]=i>=active?0:Math.round(4096*Math.min(1,i/ramp,(active-1-i)/ramp)*Math.sin(2*Math.PI*f*i/RATE+phase));}written+=take;offset+=take;remaining-=take;if(offset===n){segment++;offset=0;}}return written;}};
}
module.exports={prepare,MAX_CHUNK,RATE,DESCRIPTOR_BYTES:CAP*8};
