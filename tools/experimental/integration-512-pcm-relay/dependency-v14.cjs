'use strict';
// Refs #512. Diagnostic masked acquisition; strict v13 remains the sole receipt authority.
const {ChronologicalStream,ContinuityReceiver}=require('./continuity-v13.cjs');
const {CAP}=require('./stream-v4.cjs');
const MAX_GAP=CAP, BLOCK=256;
class MaskedStream extends ChronologicalStream {
  constructor(emit){super(e=>{const detail=this.details.get(e.first);this.details.delete(e.first);if(e.status==='overflow')this.details.clear();emit({...e,detail,scanAtRelease:this.scan});},'reserve',1);this.missing=new Uint32Array(CAP+1);this.count=0;this.details=new Map();}
  missingIn(s,n){if(s<Math.max(0,this.total-CAP)||s+n>this.total)return null;return (this.missing[(s+n)%(CAP+1)]-this.missing[s%(CAP+1)])>>>0;}
  score(s,n,c){return this.missingIn(s,n)===0?super.score(s,n,c):0;}
  ingest(p,isGap=false){if(this.closed||!(p instanceof Int16Array))throw Error('input');for(const x of p){const i=this.total%CAP;this.ring[i]=this.ring[i+CAP]=isGap?0:x;this.total++;if(isGap)this.count=(this.count+1)>>>0;this.missing[this.total%(CAP+1)]=this.count;if(!this.overflow&&this.total>=this.scan+650){this.step();this.drain(false);}}}
  evaluate(c){super.evaluate(c);this.details.set(c.first,{evaluatedAt:this.total,hypotheses:c.evidence.map(h=>({start:h.start,k:h.k,valid:h.valid,missingWords:h.words.map((_,i)=>this.missingIn(Math.round(h.start+(640+i*1280+320)*h.scale),Math.round(320*h.scale))),missingPreamble:this.missingIn(h.start,2*Math.round(320*h.scale))}))});}
}
class DependencyReceiver {
  constructor(emit){this.emit=emit;this.events=[];this.total=0;this.offset=0;this.notice=0;this.closed=false;this.strict=new ContinuityReceiver(e=>this.events.push(e));this.stats=this.strict.stats;this.resetDiagnostic();}
  resetDiagnostic(){this.shadow=new MaskedStream(e=>{const x={...e,status:'diagnostic-'+e.status,authority:false,diagnosticEpochStart:this.offset};for(const k of ['at','start','end','first','last','lossStart','lossEnd','scanAtRelease'])if(Number.isFinite(x[k]))x[k]+=this.offset;if(x.ranges)x.ranges=x.ranges.map(r=>r.map(v=>v+this.offset));if(x.evidence)x.evidence=x.evidence.map(h=>({...h,start:h.start+this.offset}));if(x.detail)x.detail={evaluatedAt:x.detail.evaluatedAt+this.offset,hypotheses:x.detail.hypotheses.map(h=>({...h,start:h.start+this.offset}))};x.logicalAt=x.at;x.at=Math.max(x.at,this.notice);this.events.push(x);});}
  flush(){this.events.sort((a,b)=>a.at-b.at||Number(a.authority===false)-Number(b.authority===false));for(const e of this.events)this.emit(e);this.events=[];}
  push(p){if(this.closed||!(p instanceof Int16Array)||!Number.isSafeInteger(this.total+p.length+40000))throw Error('input');for(let i=0;i<p.length;i+=BLOCK){const q=p.subarray(i,i+BLOCK);this.strict.push(q);this.shadow.ingest(q);this.total+=q.length;this.flush();}}
  gap(n){if(this.closed||!Number.isSafeInteger(n)||n<=0||!Number.isSafeInteger(this.total+n+40000))throw Error('gap');this.notice=this.total+n;this.strict.gap(n);if(n>MAX_GAP){this.offset=this.notice;this.resetDiagnostic();this.events.push({status:'diagnostic-reset',authority:false,at:this.notice,reason:'gap-exceeds-history',missingSamples:n});this.flush();}else{this.flush();for(let left=n;left;){const k=Math.min(BLOCK,left);this.shadow.ingest(new Int16Array(k),true);left-=k;this.flush();}}this.total+=n;}
  readiness(){return this.strict.readiness();}
  finish(){if(this.closed)throw Error('closed');this.closed=true;this.strict.finish();this.shadow.finish();this.flush();return this.readiness();}
}
module.exports={MaskedStream,DependencyReceiver,MAX_GAP};
