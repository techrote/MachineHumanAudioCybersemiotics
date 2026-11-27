'use strict';
// Refs #512. Experimental continuous PCM association; unchanged v2 wire.
const v1=require('./relay.cjs'),v2=require('./bound-v2.cjs');
const RATE=16000,CAP=38400,WAIT=32400,MAX_PENDING=8,STRIDE=16,GAP=320,FRAME=31360;
const scales=Array.from({length:13},(_,i)=>1+(i-6)*.0025);
const coeff=(f,s)=>2*Math.cos(2*Math.PI*f/(RATE*s));
const cfg=scales.map(s=>({s,n:Math.round(320*s),a:coeff(2300,s),b:coeff(2700,s),body:Array.from({length:17},(_,i)=>coeff(400+100*i,s))}));
const eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b),mod=x=>(x%17+17)%17;
function recover(w){const m=w.flatMap((x,i)=>x===null?[i]:[]);if(m.length>2)return null;for(let a=0;a<(m.length?17:1);a++)for(let b=0;b<(m.length===2?17:1);b++){const x=w.slice();if(m.length)x[m[0]]=a;if(m.length===2)x[m[1]]=b;if(mod(x.reduce((s,v)=>s+v,0))===0&&mod(x.reduce((s,v,i)=>s+(i+1)*v,0))===0)return x;}return null;}
const vocab=['fault','open','stopped','overload','not','quote','question','verify','pump-reports','relay-reports','uncertain','and','if'];
function parse(w){const a=recover(w.slice(0,8)),b=recover(w.slice(8,16)),c=recover(w.slice(16));if(!a||!b||!c||a[0]>1||a.slice(1,6).some(x=>x<1))return null;const n=b[0]+1;if(n<1||n>4||b.slice(n+1,6).some(x=>x!==13))return null;let j=1;function read(){if(j>n||b[j]>=13)throw Error('tree');const i=b[j++];return [vocab[i],...Array.from({length:i<4?0:i<11?1:2},read)];}try{const tree=read();if(j!==n+1)return null;const [kind,source,version,actor,event,seq]=a,p={kind,source,version,actor,event,seq,tree};return eq(c.slice(0,6),v2.tag(p))&&eq(v1.frame(p),[...a,...b])?p:null;}catch{return null;}}
class Stream {
  constructor(emit){if(typeof emit!=='function')throw Error('callback required');this.emit=emit;this.ring=new Int16Array(2*CAP);this.total=0;this.scan=0;this.cluster=null;this.pending=[];this.closed=false;this.overflow=false;this.stats={scans:0,hypotheses:0,clusters:0,maxPending:0,pcmBytes:this.ring.byteLength};}
  score(s,n,c){if(s<Math.max(0,this.total-CAP)||s+n>this.total)return 0;const p=this.ring,start=s%CAP;let a=0,b=0,e=0;for(let i=start;i<start+n;i++){const x=p[i],z=x+c*a-b;b=a;a=z;e+=x*x;}return e<n*250**2?0:2*(a*a+b*b-c*a*b)/(n*e);}
  push(p){if(this.closed||!(p instanceof Int16Array)||this.total+p.length>Number.MAX_SAFE_INTEGER-WAIT)throw Error('stream input');for(const x of p){const i=this.total%CAP;this.ring[i]=this.ring[i+CAP]=x;this.total++;if(!this.overflow&&this.total>=this.scan+650){this.step();this.drain(false);}}}
  step(){const s=this.scan;this.scan+=STRIDE;this.stats.scans++;const hits=[];
    for(let k=0;k<cfg.length;k++){const {n,a,b}=cfg[k];const x=this.score(s,n,a);if(x<.72)continue;const q=Math.min(x,this.score(s+n,n,b));if(q>=.72)hits.push({start:s,k,q});}
    if(this.cluster&&s-this.cluster.last>GAP)this.closeCluster();if(this.overflow)return;
    if(hits.length){if(!this.cluster)this.cluster={first:s,last:s,best:Array(13).fill(null)};const c=this.cluster;c.last=s;for(const h of hits)if(!c.best[h.k]||h.q>c.best[h.k].q)c.best[h.k]=h;
      // A continuous false-onset train cannot retain an unbounded candidate span.
      if(c.last-c.first>GAP)this.fail('onset-span-overflow');}
  }
  fail(reason){this.overflow=true;this.cluster=null;this.pending=[];this.emit({status:'overflow',reason,at:this.total});}
  closeCluster(){const c=this.cluster;if(!c)return;this.cluster=null;this.stats.clusters++;if(this.pending.length>=MAX_PENDING){this.fail('pending-cap');return;}this.pending.push(c);this.stats.maxPending=Math.max(this.stats.maxPending,this.pending.length);}
  evaluate(c){const valid=new Map();c.evidence=[];c.start=Infinity;c.end=-Infinity;
    for(const h of c.best){if(!h)continue;const {s,n,body}=cfg[h.k],complete=h.start+Math.round(FRAME*s)-320<=this.total;const words=Array.from({length:24},(_,i)=>{const at=Math.round(h.start+(640+i*1280+320)*s);let a=0,b=0,v=-1;for(let k=0;k<17;k++){const q=this.score(at,n,body[k]);if(q>a){b=a;a=q;v=k;}else if(q>b)b=q;}return a>=.85&&a-b>=.2?v:null;});const packet=complete?parse(words):null;this.stats.hypotheses++;c.evidence.push({...h,scale:s,complete,words,valid:!!packet});if(packet){valid.set(JSON.stringify(packet),packet);c.start=Math.min(c.start,h.start);c.end=Math.max(c.end,h.start+Math.round(FRAME*s));}}
    c.packet=valid.size===1?[...valid.values()][0]:null;c.interpretations=valid.size;c.conflict=valid.size>1;c.done=true;
    // Distinct detected candidate regions with overlapping validated extents conflict, even if their ASTs agree.
    if(valid.size)for(const other of this.pending)if(other!==c&&other.done&&other.interpretations&&other.start<c.end&&c.start<other.end){c.conflict=true;other.conflict=true;}
  }
  drain(eof){if(this.overflow)return;for(const c of this.pending)if(!c.done&&(eof||this.total>=c.first+WAIT))this.evaluate(c);
    for(let i=0;i<this.pending.length;){const c=this.pending[i];if(!c.done||(!eof&&c.interpretations&&(this.scan<=c.end||this.cluster&&this.cluster.first<c.end||this.pending.some(o=>o!==c&&!o.done&&o.first<c.end)))){i++;continue;}
      this.pending.splice(i,1);this.emit({status:c.conflict?'ambiguous':c.packet?'ok':'refused',first:c.first,last:c.last,start:Number.isFinite(c.start)?c.start:null,end:Number.isFinite(c.end)?c.end:null,packet:c.conflict?null:c.packet,at:this.total,evidence:c.evidence});}
  }
  finish(){if(this.closed)throw Error('already finished');this.closed=true;if(this.overflow)return;while(this.scan+630<=this.total&&!this.overflow)this.step();this.closeCluster();this.drain(true);}
}
function decode(p,chunk=511){if(!Number.isInteger(chunk)||chunk<1)throw Error('chunk size');const events=[],s=new Stream(e=>events.push(e));for(let i=0;i<p.length;i+=chunk)s.push(p.subarray(i,i+chunk));s.finish();return {events,stats:s.stats};}
module.exports={Stream,decode,CAP,WAIT,MAX_PENDING};
