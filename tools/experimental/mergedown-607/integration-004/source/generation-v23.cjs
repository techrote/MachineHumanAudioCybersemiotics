'use strict';
// Refs #512. Experimental slot envelope; public binding, NOT authentication.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const control=require('./sequence-v22.cjs'),{render}=require('./bound-v2.cjs');
const {frame}=require('./relay.cjs'),{scan,STEP:HEAD}=require('./clarify-v18.cjs');
const STEP=41600, CAP=256, eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const valid=g=>Number.isInteger(g)&&g>=0&&g<CAP;
function token(p,g,role){if(!valid(g)||!['body','request'].includes(role))throw Error('generation/role');let n=crypto.createHash('sha256').update('MHAC-occurrence-v23:'+role+'\0').update(Buffer.from([...frame(p),g])).digest().readUInt32BE(0)%17**6;const t=[];for(let i=0;i<6;i++){t.push(n%17);n=Math.floor(n/17);}return [...t,1+(g%16),1+Math.floor(g/16)];}
const generation=t=>(t[6]-1)+16*(t[7]-1);
function short(p,g,role,phase=0,edit=w=>w){return control.render(p,phase,()=>edit(control.protect(token(p,g,role))));}
function envelope(p,g,phase=0){const x=new Int16Array(STEP);x.set(render(p,phase),64);x.set(short(p,g,'body',phase),HEAD+64);return x;}
function request(p,g,phase=0){const x=new Int16Array(STEP);x.set(short(p,g,'request',phase),64);return x;}
// Host-supplied fixed capture slots. No transmitter identity or expected generation used.
function acquire(x,gaps=[],chunk=511){if(!(x instanceof Int16Array)||x.length!==STEP)throw Error('slot length');let events=[];const cut=(a,b)=>gaps.filter(([l,r])=>l<b&&r>a).map(([l,r])=>[Math.max(l,a)-a,Math.min(r,b)-a]);const hg=cut(0,HEAD),tg=cut(HEAD,STEP);const s=scan(x.subarray(0,HEAD),hg,e=>events.push(e),chunk);s.feed(HEAD);s.finish();const bodies=events.filter(e=>e.packet&&['ok','diagnostic-ok'].includes(e.status)),strict=bodies.filter(e=>e.authority!==false&&e.status==='ok');const a=control.acquire(x.subarray(0,HEAD),hg),b=control.acquire(x.subarray(HEAD),tg);const result={at:STEP-1,events,headControl:a,tailControl:b,status:'refused'};
 if(!bodies.length&&b.status==='no-onset'&&a.status==='ok'&&!gaps.length&&Math.abs(a.start-64)<=16)return {...result,status:'request',token:a.token};
 if(a.status!=='no-onset'||b.status!=='ok'||Math.abs(b.start-64)>16||!bodies.length||strict.length>1)return result;
 const p=bodies[0].packet,g=generation(b.token);if(!bodies.every(e=>eq(e.packet,p)&&Math.abs(e.start-64)<=96)||!eq(token(p,g,'body'),b.token))return result;
 return {...result,status:strict.length===1&&!gaps.length?'receipt-candidate':'diagnostic',packet:p,generation:g};
}
// One writer per namespace. Exclusive append-only files; no automatic reprovisioning.
// Linux fsync of file and directory before returning. A valid older snapshot is NOT detectable.
function syncDir(d){const f=fs.openSync(d,'r');try{fs.fsyncSync(f);}finally{fs.closeSync(f);}}
function provision(d){fs.mkdirSync(d);const f=fs.openSync(path.join(d,'namespace'),'wx');try{fs.writeFileSync(f,'MHAC-generation-v23\n');fs.fsyncSync(f);}finally{fs.closeSync(f);}syncDir(d);syncDir(path.dirname(d));}
function allocate(d){if(fs.readFileSync(path.join(d,'namespace'),'utf8')!=='MHAC-generation-v23\n')throw Error('namespace');const names=fs.readdirSync(d).filter(n=>n!=='namespace').sort();if(names.length>CAP||names.some((n,i)=>n!==String(i).padStart(3,'0')||fs.statSync(path.join(d,n)).size!==0))throw Error('history invalid');if(names.length===CAP)throw Error('generation exhausted');const g=names.length,f=fs.openSync(path.join(d,String(g).padStart(3,'0')),'wx');try{fs.fsyncSync(f);}finally{fs.closeSync(f);}syncDir(d);return g;}
module.exports={STEP,HEAD,CAP,token,short,envelope,request,acquire,provision,allocate};
