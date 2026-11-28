'use strict';
// Refs #512. Experimental continuous PCM adapter for v63 replies only.
// v65: bounded deferred origin, proof of unrecoverable first GF(17) block.
// Refs #512; parent 1214185ae18750cfea9aec5171d72272fea8b57c.
const R=require('./stream-rx-v63.cjs');
const RING=2048, STRIDE=8, QUIET=128, PILOT=640, THRESH=.68, HORIZON=R.MIN;
class Receiver {
 constructor(){this.ring=new Int16Array(RING);this.valid=new Uint8Array(RING);this.batch=new Int16Array(128);this.used=0;this.total=0;this.group=null;this.active=null;this.pending=null;this.closed=false;this.busy=false;}
 get pcmBytes(){return this.ring.byteLength+this.batch.byteLength+R.PCM_BYTES;}
 get validityBytes(){return this.valid.byteLength;}
 score(s,f){let a=0,b=0,e=0;const c=2*Math.cos(2*Math.PI*f/16000);for(let i=0;i<320;i++){const k=(s+i)%RING;if(!this.valid[k])return 0;const v=this.ring[k],z=v+c*a-b;b=a;a=z;e+=v*v;}return e<320*250**2?0:2*(a*a+b*b-c*a*b)/(320*e);}
 flush(){if(this.used){this.active.rx.push(this.batch.subarray(0,this.used));this.used=0;}}
 feed(i){const a=this.active,k=i%RING;if(i>=a.end)return;if(!this.valid[k]){this.flush();a.rx.gap(1);}else{this.batch[this.used++]=this.ring[k];if(this.used===this.batch.length)this.flush();}a.next=i+1;}
 start(g){const origin=Math.max(0,g.best-64);this.active={origin,end:origin+HORIZON,next:origin,rx:new R.Receiver(),overlap:false,gapped:false,pilot:g.best};if(this.total-origin>RING)throw Error('internal prefix invariant');for(let i=origin;i<this.total;i++)this.feed(i);}
 complete(emit,reason=null,preemption=null){const a=this.active;this.flush();const why=a.overlap?'overlapping-body-pilot':a.gapped?'capture-or-guard-gap':reason;const acquisition=why?{status:'refused',reason:why,hypotheses:[]}:a.rx.finish();this.active=null;this.pending=null;emit({origin:a.origin,pilot:a.pilot,end:a.end,decisionAt:this.total,acquisition,...(preemption?{preemption}:{})});}
 // The first eight symbols form one GF(17) block. The pinned decoder cannot
 // recover more than two erasures, and its emitted symbol decisions never change.
 // No early eviction based merely on pilot score or authentication outcome.
 prefixErasures(){this.flush();return this.active.rx.paths.map(p=>p.rx.inner.body.words.slice(0,8).filter(v=>v===null).length); }
 consider(emit){if(!this.pending)return;const g=this.pending,a=this.active,origin=Math.max(0,g.best-64);
  if(a.overlap||a.gapped||this.total-origin>RING){a.overlap=true;this.pending=null;return;}
  const erasures=this.prefixErasures();if(erasures.every(n=>n>2)){this.complete(emit,"unrecoverable-prefix-preempted",{erasures,nextOrigin:origin,historySamples:this.total-origin});this.start(g);}
 }
 advance(v,valid,emit){const i=this.total++,k=i%RING;this.ring[k]=v;this.valid[k]=Number(valid);if(this.active){if(!valid)this.active.gapped=true;if(i===this.active.next)this.feed(i);}
  const s=this.total-PILOT;if(s>=0&&s%STRIDE===0){const a=this.score(s,2300),b=a>=THRESH?this.score(s+320,2700):0,q=Math.min(a,b);
   if(q>=THRESH){if(!this.group)this.group={first:s,last:s,best:s,q};else{this.group.last=s;if(q>this.group.q){this.group.best=s;this.group.q=q;}}}
   if(this.group&&s-this.group.first>=1024){if(this.active)this.active.overlap=true;else emit({origin:null,pilot:this.group.best,end:null,decisionAt:this.total,acquisition:{status:"refused",reason:"pilot-group-budget",hypotheses:[]}});this.group=null;}
   if(this.group&&s-this.group.last>=QUIET){const g=this.group;this.group=null;
    if(this.active){if(g.first<this.active.end){
      // At most one deferred origin; multiple competing groups fail closed.
      if(this.pending||this.active.overlap||this.active.gapped||g.first-this.active.origin>8192){this.active.overlap=true;this.pending=null;}
      else this.pending=g;
    }else{this.complete(emit);this.start(g);}}
    else this.start(g);
   }
   if(this.pending)this.consider(emit);
   // Delay output until all pilot starts inside the horizon have been inspected.
   if(this.active&&s>=this.active.end+64+QUIET&&!this.group)this.complete(emit);
  }
 }
 run(fn){if(this.busy)throw Error('reentrant receiver');this.busy=true;try{fn();}catch(e){this.closed=true;throw e;}finally{this.busy=false;}}
 push(x,emit){if(this.closed||!(x instanceof Int16Array)||x.length<1||x.length>1024||typeof emit!=='function')throw Error('chunk bounds');this.run(()=>{for(const v of x)this.advance(v,true,emit);});}
 gap(n,emit){if(this.closed||!Number.isSafeInteger(n)||n<1||n>R.MAX||typeof emit!=='function')throw Error('gap bounds');this.run(()=>{for(let i=0;i<n;i++)this.advance(0,false,emit);});}
 finish(emit){if(this.closed||typeof emit!=='function')throw Error('closed or callback');this.run(()=>{this.closed=true;if(this.pending&&this.active)this.active.overlap=true;if(this.group){if(this.active)this.active.overlap=true;else this.start(this.group);this.group=null;}if(this.active)this.complete(emit,'unobserved-final-guard');});}
}
module.exports={Receiver,admit:R.admit,HORIZON,PCM_BYTES:2*(RING+128)+R.PCM_BYTES,VALIDITY_BYTES:RING};
