'use strict';
// Refs #512. Experimental acquisition epoch adapter; unchanged wire and decoder.
const {Stream}=require('./stream-v4.cjs');
class EpochReceiver {
  constructor(emit,mode='cooldown',maxResets=4){
    if(typeof emit!=='function'||!['sticky','cooldown','peak512'].includes(mode)||!Number.isInteger(maxResets)||maxResets<0)throw Error('configuration');
    Object.assign(this,{emit,mode,maxResets,at:0,origin:0,epoch:0,blocked:false,quiet:0,closed:false,one:new Int16Array(1),lossFrom:null,overflowAt:null});this.start();
  }
  start(){this.stream=new Stream(e=>{
    const event={...e,epoch:this.epoch,at:this.origin+e.at};
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
    for(const x of p){this.at++;if(!this.blocked){this.one[0]=x;this.stream.push(this.one);continue;}
      if(this.mode==='sticky'||this.epoch>=this.maxResets)continue;
      this.quiet=this.mode==='cooldown'?this.quiet+1:Math.abs(x)<=512?this.quiet+1:0;
      if(this.quiet>=(this.mode==='cooldown'?320:8000)){
        const previous=this.epoch;this.epoch++;this.origin=this.at;this.blocked=false;this.quiet=0;this.start();
        this.emit({status:'rearm',epoch:this.epoch,previous,at:this.at,discardedFrom:this.overflowAt,possibleUnresolvedFrom:this.lossFrom});this.lossFrom=null;this.overflowAt=null;
      }
    }
  }
  // No EOF flush: a receiver reset or experiment horizon must not promote pending evidence.
  finish(){if(this.closed)throw Error('closed');this.closed=true;return this.readiness();}
}
module.exports={EpochReceiver};
