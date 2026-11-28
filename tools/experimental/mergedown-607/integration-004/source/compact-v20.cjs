'use strict';
// Refs #512. Experimental short control, not an authenticated or self-describing packet.
const {tag}=require('./bound-v2.cjs');
const RATE=16000, HALF=320, HEADER=640, SLOT=640, FRAME=HEADER+8*SLOT, MAX=33600;
const mod=x=>((x%17)+17)%17;
const eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
function protect(d){const a=d.reduce((s,v)=>s+v,0),b=d.reduce((s,v,i)=>s+v*(i+1),0),z=mod(7*a-b);return [...d,mod(-a-z),z];}
function recover(w){const missing=w.flatMap((v,i)=>v===null?[i]:[]);if(missing.length>2)return null;for(let a=0;a<(missing.length?17:1);a++)for(let b=0;b<(missing.length===2?17:1);b++){const d=w.slice();if(missing.length)d[missing[0]]=a;if(missing.length===2)d[missing[1]]=b;if(eq(d,protect(d.slice(0,6))))return d.slice(0,6);}return null;}
const freq=v=>400+100*v;
function render(p,phase=0,edit=x=>x){const out=new Int16Array(FRAME);function tone(f,s,n){for(let i=0;i<n;i++)out[s+i]=Math.round(4096*Math.min(1,i/16,(n-1-i)/16)*Math.sin(2*Math.PI*f*i/RATE+phase));}tone(3100,0,HALF);tone(3500,HALF,HALF);edit(protect(tag(p))).forEach((v,i)=>{if(v!==null)tone(freq(v),HEADER+i*SLOT,480);});return out;}
const bank=new Map([...Array.from({length:17},(_,i)=>freq(i)),3100,3500].map(f=>[f,[Float64Array.from({length:HALF},(_,i)=>Math.cos(2*Math.PI*f*i/RATE)),Float64Array.from({length:HALF},(_,i)=>Math.sin(2*Math.PI*f*i/RATE))]]));
function score(p,s,f){const [c,t]=bank.get(f);let a=0,b=0,e=0;for(let i=0;i<HALF;i++){const v=p[s+i];a+=v*c[i];b+=v*t[i];e+=v*v;}return e<HALF*250**2?0:2*(a*a+b*b)/(HALF*e);}
// All samples supplied by host; local gaps are explicit half-open ranges. No expected onset/identity.
function acquire(p,gaps=[]){if(!(p instanceof Int16Array)||p.length>MAX)throw Error('capture bound');const hits=[];for(let s=0;s+HEADER<=p.length;s+=16){const a=score(p,s,3100);if(a<.82)continue;const b=score(p,s+HALF,3500);if(b>=.82)hits.push({start:s,quality:Math.min(a,b)});}const groups=[];for(const h of hits){const g=groups.at(-1);if(g&&h.start-g.last<HEADER){g.last=h.start;if(h.quality>g.best.quality)g.best=h;}else groups.push({last:h.start,best:h});}if(!groups.length)return {status:'no-onset'};if(groups.length!==1)return {status:'ambiguous-onset',count:groups.length};const {start}=groups[0].best;if(start+FRAME>p.length)return {status:'truncated',start};if(gaps.some(([l,h])=>l<start+FRAME&&h>start))return {status:'capture-incomplete',start};const words=Array.from({length:8},(_,i)=>{const s=start+HEADER+i*SLOT+80;const z=Array.from({length:17},(_,v)=>({v,q:score(p,s,freq(v))})).sort((a,b)=>b.q-a.q);return z[0].q>=.85&&z[0].q-z[1].q>=.2?z[0].v:null;});const token=recover(words);return {status:token?'ok':'parity-refused',start,words,...(token?{token}:{})};}
// A token denotes a candidate reference, not identity, authority or freshness. Refuse ambiguity even if one candidate is inactive.
function resolve(token,records){const matches=records.filter(p=>eq(tag(p),token));return matches.length===1?{status:'unique',packet:matches[0]}:{status:matches.length?'ambiguous-reference':'unknown-reference'};}
module.exports={render,acquire,resolve,FRAME,MAX,protect,recover};
