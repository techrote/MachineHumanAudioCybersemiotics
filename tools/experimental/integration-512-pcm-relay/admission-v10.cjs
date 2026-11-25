'use strict';
// Refs #512. Necessary-condition pruning for the exact v4 observation model.
const {Stream}=require('./stream-v4.cjs');
const cfg=Array.from({length:13},(_,k)=>{const s=1+(k-6)*.0025;return {s,n:Math.round(320*s),body:Array.from({length:17},(_,i)=>2*Math.cos(2*Math.PI*(400+100*i)/(16000*s)))};});
class AdmissionStream extends Stream {
  constructor(emit){super(emit);Object.assign(this.stats,{prefixSymbols:0,prefixHypothesesRejected:0,prefixCandidatesRejected:0});}
  drain(eof){
    // No prefix decisions at EOF: the same live sample availability rule applies.
    for(let i=0;i<this.pending.length;){const c=this.pending[i];if(c.done){i++;continue;}
      if(!c.prefix)c.prefix=c.best.filter(Boolean).map(h=>({h,words:[],erasures:0,rejected:null}));
      for(const p of c.prefix){if(p.rejected)continue;const {s,n,body}=cfg[p.h.k];while(p.words.length<6){const j=p.words.length,at=Math.round(p.h.start+(640+j*1280+320)*s);if(at+n>this.total)break;
        // Do not prune on overwritten evidence; full evaluator handles it.
        if(at<Math.max(0,this.total-38400))break;
        let a=0,b=0,v=-1;for(let k=0;k<17;k++){const q=this.score(at,n,body[k]);if(q>a){b=a;a=q;v=k;}else if(q>b)b=q;}
        const w=a>=.85&&a-b>=.2?v:null;p.words.push(w);this.stats.prefixSymbols++;
        if(w===null)p.erasures++;if(p.erasures>2)p.rejected='metadata-erasure-budget';else if(w!==null&&(j===0?w>1:w<1))p.rejected='metadata-domain';
        if(p.rejected){this.stats.prefixHypothesesRejected++;break;}
      }}
      if(c.prefix.every(p=>p.rejected)){this.pending.splice(i,1);this.stats.prefixCandidatesRejected++;this.emit({status:'prefix-refused',reason:'no-viable-metadata-prefix',first:c.first,last:c.last,start:null,end:null,packet:null,at:this.total,evidence:c.prefix.map(p=>({...p.h,words:p.words,reason:p.rejected}))});}else i++;
    }
    super.drain(eof);
  }
}
module.exports={AdmissionStream};
