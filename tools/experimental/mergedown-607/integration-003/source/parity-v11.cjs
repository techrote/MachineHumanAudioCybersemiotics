'use strict';
// Refs #512. Experimental metadata feasibility and conservative lossy admission.
const {Stream,MAX_PENDING}=require('./stream-v4.cjs');
const mod=x=>(x%17+17)%17;
const cfg=Array.from({length:13},(_,k)=>{const s=1+(k-6)*.0025;return {s,n:Math.round(320*s),body:Array.from({length:17},(_,i)=>2*Math.cos(2*Math.PI*(400+100*i)/(16000*s)))};});
// Future unobserved positions are not erasures. For 7/8 observed words,
// enumerate at most one free GF(17) variable and solve the remaining two.
function feasible(words){
  if(words.filter(x=>x===null).length>2||words.some((x,j)=>x!==null&&(j===0?x>1:j<6?x<1:false)))return false;
  if(words.length<7)return true;
  const w=Array.from({length:8},(_,j)=>words[j]??null),m=w.flatMap((x,i)=>x===null?[i]:[]);
  const domain=()=>w[0]<=1&&w.slice(1,6).every(x=>x>=1);
  const solve=ids=>{const a=mod(-w.reduce((s,x,i)=>s+(ids.includes(i)?0:x),0)),b=mod(-w.reduce((s,x,i)=>s+(ids.includes(i)?0:(i+1)*x),0));
    if(!ids.length)return a===0&&b===0&&domain();
    const [i,j]=ids;if(ids.length===1){w[i]=a;return mod((i+1)*a)===b&&domain();}
    let x=0;while(mod((i-j)*x)!==mod(b-(j+1)*a))x++;w[i]=x;w[j]=mod(a-x);return domain();};
  if(m.length<=2)return solve(m);
  for(let x=0;x<17;x++){w[m[0]]=x;if(solve(m.slice(1)))return true;}return false;
}
class ParityStream extends Stream {
  constructor(emit,mode='parity'){
    if(!['parity','oldest','incoming'].includes(mode))throw Error('mode');
    super(e=>{if(e.status==='ok'&&e.start<this.lossEnd&&this.lossStart<e.end){this.stats.lossAbstentions++;emit({...e,status:'association-incomplete',packet:null,reason:'overlap-with-evicted-candidate'});}else emit(e);});
    this.mode=mode;this.lossStart=Infinity;this.lossEnd=-Infinity;Object.assign(this.stats,{prefixSymbols:0,prefixCandidatesRejected:0,parityRejected:0,evicted:0,lossAbstentions:0});
  }
  readiness(){return {sample:this.total,acquisition:this.overflow?'overloaded':this.cluster||this.pending.length?'pending':'clear'};}
  finish(){if(this.closed)throw Error('already finished');this.closed=true;return this.readiness();}
  closeCluster(){if(this.mode==='parity'||this.pending.length<MAX_PENDING)return super.closeCluster();const c=this.cluster;if(!c)return;this.cluster=null;this.stats.clusters++;
    const i=this.mode==='oldest'?this.pending.findIndex(p=>!p.done):-1,drop=i<0?c:this.pending.splice(i,1,c)[0];
    // A bounded conservative hull of all discarded extents; never promote
    // evidence whose association might depend on one of those candidates.
    this.lossStart=Math.min(this.lossStart,drop.first);this.lossEnd=Math.max(this.lossEnd,drop.last+Math.round(31360*1.015));this.stats.evicted++;
    this.emit({status:'evicted',reason:this.mode,first:drop.first,last:drop.last,start:null,end:null,lossStart:this.lossStart,lossEnd:this.lossEnd,packet:null,at:this.total});
  }
  drain(eof){for(let i=0;i<this.pending.length;){const c=this.pending[i];if(c.done){i++;continue;}
    if(!c.prefix)c.prefix=c.best.filter(Boolean).map(h=>({h,words:[],rejected:false}));
    for(const p of c.prefix){if(p.rejected)continue;const {s,n,body}=cfg[p.h.k];while(p.words.length<8){const j=p.words.length,at=Math.round(p.h.start+(640+j*1280+320)*s);if(at+n>this.total||at<Math.max(0,this.total-38400))break;
      let a=0,b=0,v=-1;for(let k=0;k<17;k++){const q=this.score(at,n,body[k]);if(q>a){b=a;a=q;v=k;}else if(q>b)b=q;}p.words.push(a>=.85&&a-b>=.2?v:null);this.stats.prefixSymbols++;
      if(!feasible(p.words)){p.rejected=true;if(j>=6)this.stats.parityRejected++;break;}
    }}
    if(c.prefix.every(p=>p.rejected)){this.pending.splice(i,1);this.stats.prefixCandidatesRejected++;this.emit({status:'prefix-refused',reason:'no-feasible-metadata',first:c.first,last:c.last,start:null,end:null,packet:null,at:this.total,evidence:c.prefix.map(p=>({...p.h,words:p.words,rejected:p.rejected}))});}else i++;
  }super.drain(eof);}
}
module.exports={ParityStream,feasible};
