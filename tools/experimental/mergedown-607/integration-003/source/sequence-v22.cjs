'use strict';
// Refs #512. Original experimental control namespace. Sequence labels are not authentication.
const {tag}=require('./bound-v2.cjs');
const RATE=16000,N=320,SLOT=640,HEADER=640,DATA=8,WORDS=10,FRAME=HEADER+WORDS*SLOT,MAX=33600;
const mod=x=>((x%17)+17)%17,eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
function token(p){if(![p.source,p.seq].every(v=>Number.isInteger(v)&&v>=1&&v<=16))throw Error('label');return [...tag(p),p.source,p.seq];}
function protect(d){if(d.length!==DATA||d.some(v=>!Number.isInteger(v)||v<0||v>16))throw Error('digits');const a=d.reduce((s,v)=>s+v,0),b=d.reduce((s,v,i)=>s+v*(i+1),0),z=mod((DATA+1)*a-b);return [...d,mod(-a-z),z];}
function recover(w){if(w.length!==WORDS||w.some(v=>v!==null&&(!Number.isInteger(v)||v<0||v>16)))return null;const m=w.flatMap((v,i)=>v===null?[i]:[]);if(m.length>2)return null;for(let a=0;a<(m.length?17:1);a++)for(let b=0;b<(m.length===2?17:1);b++){const d=w.slice();if(m.length)d[m[0]]=a;if(m.length===2)d[m[1]]=b;if(eq(d,protect(d.slice(0,DATA))))return d.slice(0,DATA);}return null;}
const freq=v=>400+100*v;
function render(p,phase=0,edit=x=>x){const out=new Int16Array(FRAME);function tone(f,s,n){for(let i=0;i<n;i++)out[s+i]=Math.round(4096*Math.min(1,i/16,(n-1-i)/16)*Math.sin(2*Math.PI*f*i/RATE+phase));}tone(3500,0,N);tone(3100,N,N);const w=edit(protect(token(p)));if(w.length!==WORDS)throw Error('edit');w.forEach((v,i)=>{if(v!==null)tone(freq(v),HEADER+i*SLOT,480);});return out;}
const bank=new Map([...Array.from({length:17},(_,i)=>freq(i)),3100,3500].map(f=>[f,[Float64Array.from({length:N},(_,i)=>Math.cos(2*Math.PI*f*i/RATE)),Float64Array.from({length:N},(_,i)=>Math.sin(2*Math.PI*f*i/RATE))]]));
function score(p,s,f){const [c,t]=bank.get(f);let a=0,b=0,e=0;for(let i=0;i<N;i++){const v=p[s+i];a+=v*c[i];b+=v*t[i];e+=v*v;}return e<N*250**2?0:2*(a*a+b*b)/(N*e);}
function acquire(p,gaps=[]){if(!(p instanceof Int16Array)||p.length>MAX)throw Error('capture bound');let groups=[];for(let s=0;s+HEADER<=p.length;s+=16){if(gaps.some(([l,h])=>l<s+HEADER&&h>s))continue;const a=score(p,s,3500);if(a<.82)continue;const b=score(p,s+N,3100);if(b<.82)continue;const quality=Math.min(a,b),g=groups.at(-1);if(g&&s-g.last<HEADER){g.last=s;if(quality>g.quality){g.start=s;g.quality=quality;}}else{groups.push({last:s,start:s,quality});if(groups.length>1)return {status:'ambiguous-onset'};}}
 if(!groups.length)return {status:'no-onset'};const {start}=groups[0];if(start+FRAME>p.length)return {status:'truncated',start};if(gaps.length)return {status:'capture-incomplete',start};const words=Array.from({length:WORDS},(_,i)=>{const s=start+HEADER+i*SLOT+80;const z=Array.from({length:17},(_,v)=>({v,q:score(p,s,freq(v))})).sort((a,b)=>b.q-a.q);return z[0].q>=.85&&z[0].q-z[1].q>=.2?z[0].v:null;});const d=recover(words);return d&&d.slice(6).every(v=>v>=1&&v<=16)?{status:'ok',start,words,token:d}:{status:'parity-or-domain-refused',start,words};}
function resolve(d,records){const matches=records.filter(p=>eq(token(p),d));return matches.length===1?{status:'unique',packet:matches[0]}:{status:matches.length?'ambiguous-reference':'unknown-reference'};}
module.exports={token,protect,recover,render,acquire,resolve,FRAME,MAX};
