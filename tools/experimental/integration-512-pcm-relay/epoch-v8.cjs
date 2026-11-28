'use strict';
// Refs #512. Experimental acquisition epoch adapter; unchanged wire and decoder.
const {Stream}=require('./stream-v4.cjs');
class EpochReceiver {
  constructor(emit,mode='cooldown',maxResets=4){
    if(typeof emit!=='function'||!['sticky','cooldown','peak512','history','backoff'].includes(mode)||!Number.isInteger(maxResets)||maxResets<0)throw Error('configuration');
    Object.assign(this,{emit,mode,maxResets,at:0,origin:0,epoch:0,blocked:false,quiet:0,closed:false,one:new Int16Array(1),lossFrom:null,overflowAt:null,history:new Int16Array(640),replayed:0});this.start();
  }
  start(){this.stream=new Stream(e=>{
    const event={...e,epoch:this.epoch,sourceAt:this.origin+e.at,at:this.at};
    for(const k of ['first','last','start','end'])if(Number.isFinite(e[k]))event[k]=this.origin+e[k];
    if(e.evidence)event.evidence=e.evidence.map(h=>({...h,start:this.origin+h.start}));
    if(e.status==='overflow'){
      this.blocked=true;this.overflowAt=event.at;this.lossFrom=this.origin;this.quiet=0;
      event.possibleUnresolvedFrom=this.lossFrom;
    }
    this.emit(event);
  });}
  readiness(){return {sample:this.at,epoch:this.epoch,acquisition:this.blocked?'overloaded':this.stream.cluster||this.stream.pending.length?'pending':'clear',channel:'not-inferred',context:'not-inferred',possibleUnresolvedFrom:this.lossFrom,overflowAt:this.overflowAt};}
  push(p){if(this.closed||!(p instanceof Int16Array)||!Number.isSafeInteger(this.at+p.length))throw Error('input');
    for(const x of p){this.history[this.at%640]=x;this.at++;if(!this.blocked){this.one[0]=x;this.stream.push(this.one);continue;}
      if(this.mode==='sticky'||this.epoch>=this.maxResets)continue;
      this.quiet=this.mode!=='peak512'?this.quiet+1:Math.abs(x)<=512?this.quiet+1:0;
      if(this.quiet>=(this.mode==='peak512'?8000:this.mode==='backoff'?Math.min(20480,320*4**this.epoch):320)){
        const previous=this.epoch;this.epoch++;this.origin=Math.max(0,this.at-(['history','backoff'].includes(this.mode)?640:0));this.blocked=false;this.quiet=0;this.start();
        this.emit({status:'rearm',epoch:this.epoch,previous,at:this.at,discardedFrom:this.overflowAt,possibleUnresolvedFrom:this.lossFrom,historyFrom:this.origin,historySamples:this.at-this.origin});this.lossFrom=null;this.overflowAt=null;for(let j=this.origin;j<this.at&&!this.blocked;j++){this.one[0]=this.history[j%640];this.stream.push(this.one);this.replayed++;}
      }
    }
  }
  // No EOF flush: a receiver reset or experiment horizon must not promote pending evidence.
  finish(){if(this.closed)throw Error('closed');this.closed=true;return this.readiness();}
}
module.exports={EpochReceiver};
