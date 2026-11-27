'use strict';
// Refs #512. Bounded body-pilot alignment and wrong-family pilot refusal.
// Host still supplies slot boundaries; control timing remains nominal.
const R=require('./stream-rx-v59.cjs'),G=require('./generation-v23.cjs'),F=require('./fresh-v45.cjs');
const HEAD=G.HEAD,PREFIX=1024,RING=640,CHUNK=1024;
const nominal=64,maxShift=128;
class Receiver {
 constructor(){this.inner=new R.Receiver();this.prefix=new Int16Array(PREFIX);this.ring=new Int16Array(RING);this.out=new Int16Array(CHUNK);this.used=0;this.total=0;this.bodyOut=0;this.start=null;this.best=0;this.last=-10000;this.groups=0;this.foreign=false;this.gapped=false;this.closed=false;}
 get pcmBytes(){return this.inner.pcmBytes+this.prefix.byteLength+this.ring.byteLength+this.out.byteLength;}
 score(start,f){let a=0,b=0,e=0;const c=2*Math.cos(2*Math.PI*f/16000);for(let i=0;i<320;i++){const v=this.ring[(start+i)%RING],z=v+c*a-b;b=a;a=z;e+=v*v;}return e<320*250**2?0:2*(a*a+b*b-c*a*b)/(320*e);}
 inspect(end){const s=end-RING;if(s<0||s%16)return;const a=this.score(s,2300);if(a>=.72){const b=this.score(s+320,2700);if(b>=.72){if(s-this.last>=RING)this.groups=Math.min(2,this.groups+1);this.last=s;if(s<=nominal+maxShift&&Math.min(a,b)>this.best){this.best=Math.min(a,b);this.start=s;}}}if(this.score(s,3500)>=.82&&this.score(s+320,3100)>=.82)this.foreign=true;}
 emit(v){this.out[this.used++]=v;if(this.used===CHUNK)this.flush();}
 flush(){if(this.used){this.inner.push(this.out.subarray(0,this.used));this.used=0;}}
 body(v,i){const j=i-(this.start===null?0:this.start-nominal);if(j>=0&&j<HEAD){while(this.bodyOut<j){this.emit(0);this.bodyOut++;}this.emit(v);this.bodyOut++;}}
 advance(n,input){if(this.closed||!Number.isInteger(n)||n<1||this.total+n>F.L)throw Error('slot bounds');for(let k=0;k<n;k++){const i=this.total++,v=input?input[k]:0;if(i<HEAD){this.ring[i%RING]=v;this.inspect(i+1);if(i<PREFIX){this.prefix[i]=v;if(i===PREFIX-1){for(let j=0;j<PREFIX;j++)this.body(this.prefix[j],j);}}else this.body(v,i);if(i===HEAD-1)while(this.bodyOut<HEAD){this.emit(0);this.bodyOut++;}}else this.emit(v);}}
 push(x){if(!(x instanceof Int16Array)||x.length<1||x.length>CHUNK)throw Error('chunk bounds');this.advance(x.length,x);}
 gap(n){this.advance(n,null);this.gapped=true;}
 finish(){if(this.closed)throw Error('closed');this.closed=true;const refuse=reason=>({status:'refused',reason});if(this.total!==F.L)return refuse('truncated');if(this.gapped)return refuse('capture-gap');if(this.foreign)return refuse('foreign-body-control-pilot');if(this.groups!==1)return refuse(this.groups?'ambiguous-body-pilot':'pilot');if(this.start===null)return refuse('body-pilot-outside-search');this.flush();return this.inner.finish();}
}
module.exports={Receiver,admit:R.admit,MAX_CHUNK:CHUNK,PCM_BYTES:R.CAP*2+2*(PREFIX+RING+CHUNK)};
