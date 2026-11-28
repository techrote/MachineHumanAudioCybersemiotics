'use strict';
// Refs #512. Explicit chronological victim selection and discontinuity contract.
const {LedgerStream}=require('./ledger-v12.cjs');
const {MAX_PENDING}=require('./stream-v4.cjs');
class ChronologicalStream extends LedgerStream {
  closeCluster(){
    if(this.pending.length<MAX_PENDING||!this.cluster||this.policy==='incoming')return super.closeCluster();
    // Select by acquisition time, not mutable array position. Preserve array order.
    let i=-1;
    for(let j=0;j<this.pending.length;j++)if(!this.pending[j].done&&(i<0||(this.policy==='oldest'?this.pending[j].first<this.pending[i].first:this.pending[j].first>this.pending[i].first)))i=j;
    if(i<0)return super.closeCluster();
    const c=this.cluster;this.cluster=null;this.stats.clusters++;
    const drop=this.pending.splice(i,1,c)[0],a=drop.first,b=drop.last+Math.round(31360*1.015);
    this.ledger.add(a,b);this.stats.evicted++;this.stats.ledgerPeak=this.ledger.peak;this.stats.ledgerMerges=this.ledger.merges;
    this.emit({status:'evicted',reason:this.policy,first:drop.first,last:drop.last,start:null,end:null,lossStart:a,lossEnd:b,ranges:this.ledger.ranges.map(r=>r.slice()),packet:null,at:this.total});
  }
}
// Known forward gap, measured on the same monotonic host sample clock. No fill,
// retrospective decode, or EOF promotion. Unknown duration requires a new session.
class ContinuityReceiver {
  constructor(emit,mode='reserve',cap=1){this.emit=emit;this.mode=mode;this.cap=cap;this.total=0;this.offset=0;this.epoch=0;this.closed=false;this.stats={gaps:0,missingSamples:0,discardedCandidates:0,maxPending:0};this.reset();}
  reset(){this.inner=new ChronologicalStream(e=>{const x={...e,epoch:this.epoch};for(const k of ['at','start','end','first','last','lossStart','lossEnd'])if(Number.isFinite(x[k]))x[k]+=this.offset;if(x.ranges)x.ranges=x.ranges.map(r=>r.map(v=>v+this.offset));if(x.evidence)x.evidence=x.evidence.map(h=>({...h,start:h.start+this.offset}));this.emit(x);},this.mode,this.cap);}
  push(p){if(this.closed||!(p instanceof Int16Array)||!Number.isSafeInteger(this.total+p.length+40000))throw Error('input');this.inner.push(p);this.total+=p.length;this.stats.maxPending=Math.max(this.stats.maxPending,this.inner.stats.maxPending);}
  gap(n){if(this.closed||!Number.isSafeInteger(n)||n<=0||!Number.isSafeInteger(this.total+n+40000))throw Error('gap');const from=this.total,to=from+n,s=this.inner,count=s.pending.length+(s.cluster?1:0);this.stats.gaps++;this.stats.missingSamples+=n;this.stats.discardedCandidates+=count;
    this.emit({status:'discontinuity',reason:'host-reported-missing-samples',epoch:this.epoch,at:to,start:null,end:null,packet:null,gapStart:from,gapEnd:to,discardedCandidates:count,discardedValidated:s.pending.filter(c=>c.done&&c.interpretations).length,wasOverloaded:s.overflow});
    s.finish();this.total=to;this.offset=to;this.epoch++;this.reset();}
  readiness(){return {...this.inner.readiness(),sample:this.total,epoch:this.epoch};}
  finish(){if(this.closed)throw Error('closed');this.closed=true;this.inner.finish();return this.readiness();}
}
module.exports={ChronologicalStream,ContinuityReceiver};
