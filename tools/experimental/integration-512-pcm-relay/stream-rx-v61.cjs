'use strict';
// Refs #512. Finite clock-rate hypotheses; slot origin remains host supplied.
const V=require('./stream-rx-v60.cjs'),F=require('./fresh-v45.cjs');
const RATES=Object.freeze([995,1000,1005]),CHUNK=1024;
const PATHS=Object.freeze([{rate:995,mode:'ceil'},{rate:995,mode:'linear'},{rate:1000,mode:'ceil'},{rate:1005,mode:'ceil'},{rate:1005,mode:'linear'}].map(Object.freeze));
const MIN=Math.floor(F.L*RATES[0]/1000),MAX=Math.ceil(F.L*RATES[2]/1000);
class Receiver {
 constructor(){this.paths=PATHS.map(({rate,mode})=>({rate,mode,rx:new V.Receiver(),buf:new Int16Array(CHUNK),used:0,next:0}));this.prev=0;this.total=0;this.gapped=false;this.closed=false;}
 get pcmBytes(){return this.paths.length*(V.PCM_BYTES+2*CHUNK);}
 flush(p){if(p.used){p.rx.push(p.buf.subarray(0,p.used));p.used=0;}}
 emit(p,v){p.buf[p.used++]=v;p.next++;if(p.used===CHUNK)this.flush(p);}
 advance(n,input){if(this.closed||!Number.isInteger(n)||n<1||this.total+n>MAX)throw Error('capture bounds');for(let j=0;j<n;j++){const i=this.total++,v=input?input[j]:0;for(const p of this.paths)while(p.next<F.L&&Math.ceil(p.next*p.rate/1000)===i){const frac=p.next*p.rate/1000-(i-1);this.emit(p,p.mode==='linear'&&i!==0?Math.round(this.prev*(1-frac)+v*frac):v);}this.prev=v;}}
 push(x){if(!(x instanceof Int16Array)||x.length<1||x.length>CHUNK)throw Error('chunk bounds');this.advance(x.length,x);}
 gap(n){this.advance(n,null);this.gapped=true;}
 finish(){if(this.closed)throw Error('closed');this.closed=true;const refuse=reason=>({status:'refused',reason,hypotheses:[]});if(this.gapped)return refuse('capture-gap');if(this.total<MIN)return refuse('truncated');const hypotheses=this.paths.map(p=>{const observed=p.next;if(observed<F.BASE)return {rate:p.rate,mode:p.mode,observed,candidate:{status:'refused',reason:'truncated-data'}};while(p.next<F.L)this.emit(p,0);this.flush(p);return {rate:p.rate,mode:p.mode,observed,candidate:p.rx.finish()};});const candidates=hypotheses.filter(h=>h.candidate.status==='candidate');const distinct=new Set(candidates.map(h=>JSON.stringify(h.candidate)));return {status:distinct.size===1?'candidate':'refused',reason:distinct.size===1?null:distinct.size?'conflicting-rate-candidates':'no-rate-candidate',hypotheses};}
}
// Never select a rate using sender truth, nor choose among conflicting decoded packets.
function admit(result,session,offers){const unknown={kind:'unknown',status:'no-admitted-response'};if(result.status!=='candidate')return unknown;return V.admit(result.hypotheses.find(h=>h.candidate.status==='candidate').candidate,session,offers);}
module.exports={Receiver,admit,RATES,MIN,MAX,MAX_CHUNK:CHUNK,PCM_BYTES:PATHS.length*(V.PCM_BYTES+2*CHUNK)};
