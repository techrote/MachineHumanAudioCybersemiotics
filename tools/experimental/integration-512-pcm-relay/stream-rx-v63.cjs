'use strict';
// Refs #512. Derived from v59/v60/v61 at 28ae88fb94b3b7f796b2a97569fc182d3104c3c5.
// Preserve finite rate paths; bound each control decoder with a shared rolling buffer.
const R=require('./stream-rx-v59.cjs'), G=require('./generation-v23.cjs'), F=require('./fresh-v45.cjs'), C=require('./sequence-v22.cjs');
const HEAD=G.HEAD, CAP=HEAD-704-24*1280, RING=640, PREFIX=1024, BATCH=128, CHUNK=1024;
const BLOCK=C.FRAME+128, FIRST=G.STEP-HEAD;
// Goertzel power as in v59/v60; avoids a second static sinusoid bank.
class Control {
 constructor(ring){this.ring=ring;this.n=0;this.groups=0;this.last=-10000;this.best=0;this.start=null;this.early=null;this.words=[];}
 score(s,f){let a=0,b=0,e=0;const c=2*Math.cos(2*Math.PI*f/16000);for(let i=0;i<320;i++){const v=this.ring[(s+i)%640],z=v+c*a-b;b=a;a=z;e+=v*v;}return e<320*250**2?0:2*(a*a+b*b-c*a*b)/(320*e);}
 sample(v){this.ring[this.n%640]=v;const end=++this.n,s=end-640;
  if(s>=0&&s%16===0){const a=this.score(s,3500);if(a>=.82){const b=this.score(s+320,3100);if(b>=.82){const q=Math.min(a,b);if(s-this.last>=640){this.groups=Math.min(2,this.groups+1);}this.last=s;if(q>this.best){this.best=q;this.start=s;}}}}
  // All admissible onset starts (48,64,80) have now been examined. First symbol ends no earlier than 1088.
  if(end===720&&this.groups===1&&this.start>=48&&this.start<=80)this.early=this.start;
  if(this.early!==null&&this.words.length<10&&end===this.early+640+80+320+640*this.words.length){let best=0,second=0,d=null;for(let k=0;k<17;k++){const q=this.score(end-320,400+100*k);if(q>best){second=best;best=q;d=k;}else if(q>second)second=q;}this.words.push(best>=.85&&best-second>=.2?d:null);}
 }
 finish(){if(this.groups!==1||this.early===null||this.start!==this.early||this.start+C.FRAME>this.n||this.words.length!==10)return null;const d=C.recover(this.words);return d&&d.slice(6).every(v=>v>=1&&v<=16)?d:null;}
}
class Nominal {
 constructor(){// Reuse pinned v59 body and semantic finish logic, without constructing its full control buffer.
  this.body=Object.assign(Object.create(R.Receiver.prototype),{buf:new Int16Array(CAP),words:[],controls:[],stage:0,used:0,total:0,gapped:false,closed:false,pilot:false});this.ring=this.body.buf.subarray(0,RING);this.total=0;this.control=null;this.controlIndex=0;this.closed=false;}
 get pcmBytes(){return this.body.buf.byteLength;}
 push(x){if(this.closed||!(x instanceof Int16Array)||x.length<1||x.length>CHUNK||this.total+x.length>F.L)throw Error('chunk bounds');let i=0;if(this.total<HEAD){const n=Math.min(x.length,HEAD-this.total);this.body.push(x.subarray(0,n));this.total+=n;i=n;}for(;i<x.length;i++,this.total++){if(this.controlIndex>=6)continue;if(!this.control)this.control=new Control(this.ring);this.control.sample(x[i]);if(this.control.n===(this.controlIndex===0?FIRST:BLOCK)){this.body.controls.push(this.control.finish());this.control=null;this.controlIndex++;}}}
 finish(){if(this.closed)throw Error('closed');this.closed=true;this.body.total=this.total;return this.body.finish();}
}
const nominal=64,maxShift=128;
class Pilot {
 constructor(){this.inner=new Nominal();this.prefix=new Int16Array(PREFIX);this.ring=new Int16Array(RING);this.out=new Int16Array(BATCH);this.used=0;this.total=0;this.bodyOut=0;this.start=null;this.best=0;this.last=-10000;this.groups=0;this.foreign=false;this.gapped=false;this.closed=false;}
 get pcmBytes(){return this.inner.pcmBytes+this.prefix.byteLength+this.ring.byteLength+this.out.byteLength;}
 score(start,f){let a=0,b=0,e=0;const c=2*Math.cos(2*Math.PI*f/16000);for(let i=0;i<320;i++){const v=this.ring[(start+i)%RING],z=v+c*a-b;b=a;a=z;e+=v*v;}return e<320*250**2?0:2*(a*a+b*b-c*a*b)/(320*e);}
 inspect(end){const s=end-RING;if(s<0||s%16)return;const a=this.score(s,2300);if(a>=.72){const b=this.score(s+320,2700);if(b>=.72){if(s-this.last>=RING)this.groups=Math.min(2,this.groups+1);this.last=s;if(s<=nominal+maxShift&&Math.min(a,b)>this.best){this.best=Math.min(a,b);this.start=s;}}}if(this.score(s,3500)>=.82&&this.score(s+320,3100)>=.82)this.foreign=true;}
 emit(v){this.out[this.used++]=v;if(this.used===BATCH)this.flush();}
 flush(){if(this.used){this.inner.push(this.out.subarray(0,this.used));this.used=0;}}
 body(v,i){const j=i-(this.start===null?0:this.start-nominal);if(j>=0&&j<HEAD){while(this.bodyOut<j){this.emit(0);this.bodyOut++;}this.emit(v);this.bodyOut++;}}
 advance(n,input){if(this.closed||!Number.isInteger(n)||n<1||this.total+n>F.L)throw Error('slot bounds');for(let k=0;k<n;k++){const i=this.total++,v=input?input[k]:0;if(i<HEAD){this.ring[i%RING]=v;this.inspect(i+1);if(i<PREFIX){this.prefix[i]=v;if(i===PREFIX-1){for(let j=0;j<PREFIX;j++)this.body(this.prefix[j],j);}}else this.body(v,i);if(i===HEAD-1)while(this.bodyOut<HEAD){this.emit(0);this.bodyOut++;}}else this.emit(v);}}
 push(x){if(!(x instanceof Int16Array)||x.length<1||x.length>CHUNK)throw Error('chunk bounds');this.advance(x.length,x);}
 gap(n){this.advance(n,null);this.gapped=true;}
 finish(){if(this.closed)throw Error('closed');this.closed=true;const refuse=reason=>({status:'refused',reason});if(this.total!==F.L)return refuse('truncated');if(this.gapped)return refuse('capture-gap');if(this.foreign)return refuse('foreign-body-control-pilot');if(this.groups!==1)return refuse(this.groups?'ambiguous-body-pilot':'pilot');if(this.start===null)return refuse('body-pilot-outside-search');this.flush();return this.inner.finish();}
}

const PILOT_BYTES=2*(CAP+PREFIX+RING+BATCH);
const RATES=Object.freeze([995,1000,1005]);
const PATHS=Object.freeze([{rate:995,mode:'ceil'},{rate:995,mode:'linear'},{rate:1000,mode:'ceil'},{rate:1005,mode:'ceil'},{rate:1005,mode:'linear'}].map(Object.freeze));
const MIN=Math.floor(F.L*RATES[0]/1000),MAX=Math.ceil(F.L*RATES[2]/1000);
class Receiver {
 constructor(){this.paths=PATHS.map(({rate,mode})=>({rate,mode,rx:new Pilot(),buf:new Int16Array(BATCH),used:0,next:0}));this.prev=0;this.total=0;this.gapped=false;this.closed=false;}
 get pcmBytes(){return this.paths.length*(PILOT_BYTES+2*BATCH);}
 flush(p){if(p.used){p.rx.push(p.buf.subarray(0,p.used));p.used=0;}}
 emit(p,v){p.buf[p.used++]=v;p.next++;if(p.used===BATCH)this.flush(p);}
 advance(n,input){if(this.closed||!Number.isInteger(n)||n<1||this.total+n>MAX)throw Error('capture bounds');for(let j=0;j<n;j++){const i=this.total++,v=input?input[j]:0;for(const p of this.paths)while(p.next<F.L&&Math.ceil(p.next*p.rate/1000)===i){const frac=p.next*p.rate/1000-(i-1);this.emit(p,p.mode==='linear'&&i!==0?Math.round(this.prev*(1-frac)+v*frac):v);}this.prev=v;}}
 push(x){if(!(x instanceof Int16Array)||x.length<1||x.length>CHUNK)throw Error('chunk bounds');this.advance(x.length,x);}
 gap(n){this.advance(n,null);this.gapped=true;}
 finish(){if(this.closed)throw Error('closed');this.closed=true;const refuse=reason=>({status:'refused',reason,hypotheses:[]});if(this.gapped)return refuse('capture-gap');if(this.total<MIN)return refuse('truncated');const hypotheses=this.paths.map(p=>{const observed=p.next;if(observed<F.BASE)return {rate:p.rate,mode:p.mode,observed,candidate:{status:'refused',reason:'truncated-data'}};while(p.next<F.L)this.emit(p,0);this.flush(p);return {rate:p.rate,mode:p.mode,observed,candidate:p.rx.finish()};});const candidates=hypotheses.filter(h=>h.candidate.status==='candidate');const distinct=new Set(candidates.map(h=>JSON.stringify(h.candidate)));return {status:distinct.size===1?'candidate':'refused',reason:distinct.size===1?null:distinct.size?'conflicting-rate-candidates':'no-rate-candidate',hypotheses};}
}
// Never select a rate using sender truth, nor choose among conflicting decoded packets.
function admit(result,session,offers){const unknown={kind:'unknown',status:'no-admitted-response'};if(result.status!=='candidate')return unknown;return R.admit(result.hypotheses.find(h=>h.candidate.status==='candidate').candidate,session,offers);}
module.exports={Receiver,admit,RATES,MIN,MAX,MAX_CHUNK:CHUNK,PCM_BYTES:PATHS.length*(PILOT_BYTES+2*BATCH)};

module.exports.Control=Control;
