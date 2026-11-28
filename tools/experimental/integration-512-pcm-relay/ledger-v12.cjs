'use strict';
// Refs #512. Half-open sample intervals; conservative bounded union.
const {ParityStream}=require('./parity-v11.cjs');
const {MAX_PENDING}=require('./stream-v4.cjs');
class LossLedger {
  constructor(cap=4){if(!Number.isInteger(cap)||cap<1||cap>64)throw Error('ledger capacity');this.cap=cap;this.floor=0;this.ranges=[];this.merges=0;this.retired=0;this.peak=0;}
  add(a,b){if(!Number.isSafeInteger(a)||!Number.isSafeInteger(b)||a<0||a>=b)throw Error('loss interval');if(b<=this.floor)return;const out=[];for(const [l,r] of [...this.ranges,[a,b]].sort((x,y)=>x[0]-y[0])){const last=out.at(-1);if(last&&l<=last[1])last[1]=Math.max(last[1],r);else out.push([l,r]);}while(out.length>this.cap){let i=0;for(let j=1;j<out.length-1;j++)if(out[j+1][0]-out[j][1]<out[i+1][0]-out[i][1])i=j;out.splice(i,2,[out[i][0],out[i+1][1]]);this.merges++;}this.ranges=out;this.peak=Math.max(this.peak,out.length);}
  overlaps(a,b){if(a<this.floor)throw Error("query below retired frontier");return this.ranges.some(([l,r])=>a<r&&l<b);}
  retire(watermark){if(watermark<this.floor)throw Error("nonmonotone retirement");this.floor=watermark;const old=this.ranges.length;this.ranges=this.ranges.filter(r=>r[1]>watermark);this.retired+=old-this.ranges.length;}
}
class LedgerStream extends ParityStream {
  constructor(emit,mode='oldest',cap=4){if(!['oldest','incoming','reserve'].includes(mode))throw Error('mode');super(e=>{if(e.status==='ok'&&this.ledger.overlaps(e.start,e.end)){this.stats.lossAbstentions++;emit({...e,status:'association-incomplete',packet:null,reason:'overlap-with-evicted-candidate'});}else emit(e);},'parity');this.policy=mode;this.ledger=new LossLedger(cap);Object.assign(this.stats,{ledgerPeak:0,ledgerMerges:0,ledgerRetired:0});}
  closeCluster(){if(this.pending.length<MAX_PENDING)return super.closeCluster();const c=this.cluster;if(!c)return;this.cluster=null;this.stats.clusters++;
    // reserve: protect earlier work but always admit fresh onset if an unfinished slot exists.
    const i=this.policy==='oldest'?this.pending.findIndex(p=>!p.done):this.policy==='reserve'?this.pending.findLastIndex(p=>!p.done):-1;
    const drop=i<0?c:this.pending.splice(i,1,c)[0];const a=drop.first,b=drop.last+Math.round(31360*1.015);this.ledger.add(a,b);this.stats.evicted++;this.stats.ledgerPeak=this.ledger.peak;this.stats.ledgerMerges=this.ledger.merges;
    this.emit({status:'evicted',reason:this.policy,first:drop.first,last:drop.last,start:null,end:null,lossStart:a,lossEnd:b,ranges:this.ledger.ranges.map(r=>r.slice()),packet:null,at:this.total});}
  drain(eof){super.drain(eof); // Never retire while an older candidate can still be released.
    const floor=Math.min(this.scan,this.cluster?.first??Infinity,...this.pending.map(c=>c.first));this.ledger.retire(floor);this.stats.ledgerRetired=this.ledger.retired;}
}
module.exports={LossLedger,LedgerStream};
