'use strict';
// Refs #512. Independent body/control origin recovery. Parent v70 exact head 870a16c9.
// Uses v68 slot receiver unchanged; only physical-to-logical sample mapping changes.
// No slot or role metadata; local session configuration only. Single serialized caller.
const F=require('./fresh-v45.cjs'), G=require('./generation-v23.cjs'), {Receiver:Slot}=require('./forward-rx-v68.cjs');
const RING=2048, STRIDE=8, PILOT=640, QUIET=128, THRESH=.68, ALIGN=112;
class Receiver {
 constructor(session=1){this.session=session;this.ring=new Int16Array(RING);this.valid=new Uint8Array(RING);this.one=new Int16Array(1);this.total=0;this.group=null;this.active=null;this.closed=false;this.busy=false;}
 get pcmBytes(){return this.ring.byteLength+this.one.byteLength+2*1280;}
 get validityBytes(){return this.valid.byteLength;}
 score(s,f){let a=0,b=0,e=0;const c=2*Math.cos(2*Math.PI*f/16000);for(let i=0;i<320;i++){const k=(s+i)%RING;if(!this.valid[k])return 0;const v=this.ring[k],z=v+c*a-b;b=a;a=z;e+=v*v;}return e<320*250**2?0:2*(a*a+b*b-c*a*b)/(320*e);}
 pushSample(a,i){const k=i%RING;this.one[0]=this.ring[k];for(const rx of [a.data,a.query])if(rx){if(this.valid[k])rx.push(this.one);else rx.gap(1);}}
 feedControl(a,i){if(i>=a.end)return;this.pushSample(a,i);const logical=G.HEAD+i-a.controlOrigin+1;
  if(a.data&&logical===F.BASE){a.short=a.data.finish(this.session);a.data=null;if(a.short.authenticated){a.mode='data';a.end=i+1;a.result=a.short;a.query=null;}}
  if(a.query&&logical===F.L){a.result=a.query.finish(this.session);a.mode=a.result.authenticated?'query':null;a.query=null;}
 }
 align(a){const nominal=a.origin+G.HEAD+64;let best=null,qbest=0;
  for(let s=Math.ceil((nominal-ALIGN)/STRIDE)*STRIDE;s<=nominal+ALIGN;s+=STRIDE){const q=Math.min(this.score(s,3500),this.score(s+320,3100));if(q>=.82&&q>qbest){best=s;qbest=q;}}
  // No oracle: fallback is the nominal body-relative origin, not transmitter metadata.
  a.controlPilot=best;a.controlOrigin=best===null?a.origin+G.HEAD:best-64;
  a.shortEnd=a.controlOrigin+F.BASE-G.HEAD;a.end=a.controlOrigin+F.L-G.HEAD;
  if(this.total-a.controlOrigin>RING)throw Error('control prefix invariant');
  for(let j=a.controlOrigin;j<this.total;j++)this.feedControl(a,j);
 }
 feed(i){const a=this.active;if(i>=a.end)return;
  if(i<a.origin+G.HEAD)this.pushSample(a,i);
  else if(a.controlOrigin!==null)this.feedControl(a,i);
  else if(this.total>=a.origin+G.HEAD+64+ALIGN+PILOT)this.align(a);
  a.next=i+1;
 }
 start(g){const origin=Math.max(0,g.best-64);this.active={origin,pilot:g.best,controlOrigin:null,controlPilot:null,shortEnd:origin+F.BASE,end:origin+F.L+ALIGN,next:origin,data:new Slot('data'),query:new Slot('query'),short:null,result:null,mode:null,overlap:false,gapped:false};if(this.total-origin>RING)throw Error('prefix invariant');for(let i=origin;i<this.total;i++)this.feed(i);}
 complete(emit,reason=null){const a=this.active,why=a.overlap?'overlapping-body-pilot':a.gapped?'capture-or-guard-gap':reason;this.active=null;emit({origin:a.origin,pilot:a.pilot,controlPilot:a.controlPilot,controlOffset:a.controlOrigin===null?null:a.controlOrigin-a.origin-G.HEAD,end:a.end,decisionAt:this.total,mode:why?null:a.mode,acquisition:why?{status:'refused',reason:why}:a.result??{status:'refused',reason:'incomplete-role'},dataDecision:a.short?.status??null});}
 advance(v,valid,emit){const i=this.total++,k=i%RING;this.ring[k]=v;this.valid[k]=Number(valid);if(this.active){if(!valid)this.active.gapped=true;if(i===this.active.next)this.feed(i);}
  const s=this.total-PILOT;if(s<0||s%STRIDE!==0)return;const a=this.score(s,2300),b=a>=THRESH?this.score(s+320,2700):0,q=Math.min(a,b);
  if(q>=THRESH){if(!this.group)this.group={first:s,last:s,best:s,q};else{this.group.last=s;if(q>this.group.q){this.group.best=s;this.group.q=q;}}}
  if(this.group&&s-this.group.first>=1024){if(this.active)this.active.overlap=true;else emit({origin:null,pilot:this.group.best,end:null,decisionAt:this.total,mode:null,acquisition:{status:'refused',reason:'pilot-group-budget'},dataDecision:null});this.group=null;}
  if(this.group&&s-this.group.last>=QUIET){const g=this.group;this.group=null;if(this.active){const old=this.active;
    if(g.first>=old.end){this.complete(emit);this.start(g);}
    // A candidate following a failed short DATA hypothesis may be a new frame or
    // interference in a QUERY extension. Refuse old capture, never admit it early.
    else if(old.short&&!old.short.authenticated&&g.first>=old.shortEnd){old.overlap=true;this.complete(emit);this.start(g);}
    else old.overlap=true;
   }else this.start(g);}
  if(this.active&&s>=this.active.end+64+QUIET&&!this.group)this.complete(emit);
 }
 run(fn){if(this.busy)throw Error('reentrant receiver');this.busy=true;try{fn();}catch(e){this.closed=true;throw e;}finally{this.busy=false;}}
 push(x,emit){if(this.closed||!(x instanceof Int16Array)||x.length<1||x.length>1024||typeof emit!=='function')throw Error('chunk bounds');this.run(()=>{for(const v of x)this.advance(v,true,emit);});}
 gap(n,emit){if(this.closed||!Number.isSafeInteger(n)||n<1||n>F.L||typeof emit!=='function')throw Error('gap bounds');this.run(()=>{for(let i=0;i<n;i++)this.advance(0,false,emit);});}
 finish(emit){if(this.closed||typeof emit!=='function')throw Error('closed or callback');this.run(()=>{this.closed=true;if(this.group){if(this.active)this.active.overlap=true;else this.start(this.group);this.group=null;}if(this.active)this.complete(emit,'unobserved-final-guard');});}
}
module.exports={Receiver,PCM_BYTES:2*(RING+1)+2560,VALIDITY_BYTES:RING,MAX_CONTROL_OFFSET:ALIGN};
