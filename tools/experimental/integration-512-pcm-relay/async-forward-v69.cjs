'use strict';
// Refs #512. Nominal-clock continuous DATA/QUERY acquisition, using v68 unchanged.
// No slot or role metadata; local session configuration only. Single serialized caller.
const F=require('./fresh-v45.cjs'), {Receiver:Slot}=require('./forward-rx-v68.cjs');
const RING=2048, STRIDE=8, PILOT=640, QUIET=128, THRESH=.68;
class Receiver {
 constructor(session=1){this.session=session;this.ring=new Int16Array(RING);this.valid=new Uint8Array(RING);this.one=new Int16Array(1);this.total=0;this.group=null;this.active=null;this.closed=false;this.busy=false;}
 get pcmBytes(){return this.ring.byteLength+this.one.byteLength+2*1280;}
 get validityBytes(){return this.valid.byteLength;}
 score(s,f){let a=0,b=0,e=0;const c=2*Math.cos(2*Math.PI*f/16000);for(let i=0;i<320;i++){const k=(s+i)%RING;if(!this.valid[k])return 0;const v=this.ring[k],z=v+c*a-b;b=a;a=z;e+=v*v;}return e<320*250**2?0:2*(a*a+b*b-c*a*b)/(320*e);}
 feed(i){const a=this.active,k=i%RING;if(i>=a.end)return;this.one[0]=this.ring[k];for(const rx of [a.data,a.query])if(rx){if(this.valid[k])rx.push(this.one);else rx.gap(1);}a.next=i+1;
  if(a.data&&a.next===a.origin+F.BASE){a.short=a.data.finish(this.session);a.data=null;if(a.short.authenticated){a.mode='data';a.end=a.next;a.result=a.short;a.query=null;}}
  if(a.query&&a.next===a.origin+F.L){a.result=a.query.finish(this.session);a.mode=a.result.authenticated?'query':null;a.query=null;}
 }
 start(g){const origin=Math.max(0,g.best-64);this.active={origin,pilot:g.best,end:origin+F.L,next:origin,data:new Slot('data'),query:new Slot('query'),short:null,result:null,mode:null,overlap:false,gapped:false};if(this.total-origin>RING)throw Error('prefix invariant');for(let i=origin;i<this.total;i++)this.feed(i);}
 complete(emit,reason=null){const a=this.active,why=a.overlap?'overlapping-body-pilot':a.gapped?'capture-or-guard-gap':reason;this.active=null;emit({origin:a.origin,pilot:a.pilot,end:a.end,decisionAt:this.total,mode:why?null:a.mode,acquisition:why?{status:'refused',reason:why}:a.result??{status:'refused',reason:'incomplete-role'},dataDecision:a.short?.status??null});}
 advance(v,valid,emit){const i=this.total++,k=i%RING;this.ring[k]=v;this.valid[k]=Number(valid);if(this.active){if(!valid)this.active.gapped=true;if(i===this.active.next)this.feed(i);}
  const s=this.total-PILOT;if(s<0||s%STRIDE!==0)return;const a=this.score(s,2300),b=a>=THRESH?this.score(s+320,2700):0,q=Math.min(a,b);
  if(q>=THRESH){if(!this.group)this.group={first:s,last:s,best:s,q};else{this.group.last=s;if(q>this.group.q){this.group.best=s;this.group.q=q;}}}
  if(this.group&&s-this.group.first>=1024){if(this.active)this.active.overlap=true;else emit({origin:null,pilot:this.group.best,end:null,decisionAt:this.total,mode:null,acquisition:{status:'refused',reason:'pilot-group-budget'},dataDecision:null});this.group=null;}
  if(this.group&&s-this.group.last>=QUIET){const g=this.group;this.group=null;if(this.active){const old=this.active;
    if(g.first>=old.end){this.complete(emit);this.start(g);}
    // A candidate following a failed short DATA hypothesis may be a new frame or
    // interference in a QUERY extension. Refuse old capture, never admit it early.
    else if(old.short&&!old.short.authenticated&&g.first>=old.origin+F.BASE){old.overlap=true;this.complete(emit);this.start(g);}
    else old.overlap=true;
   }else this.start(g);}
  if(this.active&&s>=this.active.end+64+QUIET&&!this.group)this.complete(emit);
 }
 run(fn){if(this.busy)throw Error('reentrant receiver');this.busy=true;try{fn();}catch(e){this.closed=true;throw e;}finally{this.busy=false;}}
 push(x,emit){if(this.closed||!(x instanceof Int16Array)||x.length<1||x.length>1024||typeof emit!=='function')throw Error('chunk bounds');this.run(()=>{for(const v of x)this.advance(v,true,emit);});}
 gap(n,emit){if(this.closed||!Number.isSafeInteger(n)||n<1||n>F.L||typeof emit!=='function')throw Error('gap bounds');this.run(()=>{for(let i=0;i<n;i++)this.advance(0,false,emit);});}
 finish(emit){if(this.closed||typeof emit!=='function')throw Error('closed or callback');this.run(()=>{this.closed=true;if(this.group){if(this.active)this.active.overlap=true;else this.start(this.group);this.group=null;}if(this.active)this.complete(emit,'unobserved-final-guard');});}
}
module.exports={Receiver,PCM_BYTES:2*(RING+1)+2560,VALIDITY_BYTES:RING};
