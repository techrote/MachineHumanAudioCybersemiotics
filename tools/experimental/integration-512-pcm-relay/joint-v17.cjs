'use strict';
// Refs #512. Fixed-window sufficient bounds only; never receipt authority.
const {bounds,BoundReceiver,CAPS}=require('./bounds-v16.cjs');
// Use support along the observed phasor, intersect rectangle with triangle bound,
// and compare the common-denominator score difference directly.
function envelope(n,c,read,seen,M){
  const w=Math.acos(c/2);let re=0,im=0,e=0,rx=0,ry=0;const holes=[];
  for(let i=0;i<n;i++){const u=Math.cos(w*i),v=Math.sin(w*i);if(seen(i)){const x=read(i);re+=x*u;im+=x*v;e+=x*x;}else{holes.push([u,v]);rx+=M*Math.abs(u);ry+=M*Math.abs(v);}}
  const r=Math.hypot(re,im),pad=1e-7*n*32768,m=holes.length;
  const support=r?holes.reduce((a,[u,v])=>a+M*Math.abs((re*u+im*v)/r),0):0;
  const lo=Math.max(0,r-support-pad,Math.hypot(Math.max(0,Math.abs(re)-rx-pad),Math.max(0,Math.abs(im)-ry-pad)));
  const hi=Math.min(r+m*M+pad,Math.hypot(Math.abs(re)+rx+pad,Math.abs(im)+ry+pad));
  return {lo2:lo*lo,hi2:hi*hi,e,emax:e+m*M*M};
}
function joint(n,coeff,read,seen,M,word){
  const old=coeff.map(c=>bounds(n,c,read,seen,M)),b=coeff.map(c=>envelope(n,c,read,seen,M)),{e,emax}=b[0],gate=n*250**2;
  const lower=b.map((x,i)=>Math.max(old[i][0],e<gate?0:Math.max(0,2*x.lo2/(n*emax)-1e-8)));
  const upper=b.map((x,i)=>Math.min(old[i][1],emax<gate?0:2*x.hi2/(n*Math.max(e,gate))+1e-8));
  if(word===null)return {stable:upper.every(x=>x<.85),lower:null,rivalUpper:Math.max(...upper),margin:null};
  const rivalUpper=Math.max(...upper.filter((_,i)=>i!==word));
  const delta=b[word].lo2-Math.max(...b.filter((_,i)=>i!==word).map(x=>x.hi2));
  // Positive difference divided by maximal energy is a lower bound. Negative
  // differences require minimal energy; we use independent score bounds instead.
  const margin=Math.max(lower[word]-rivalUpper,e>=gate&&delta>=0?2*delta/(n*emax)-2e-8:-Infinity);
  return {stable:lower[word]>=.85&&margin>=.2,lower:lower[word],rivalUpper,margin};
}
class JointReceiver extends BoundReceiver {
  resetDiagnostic(){super.resetDiagnostic();const s=this.shadow,base=s.evaluate.bind(s);s.evaluate=c=>{base(c);const detail=s.details.get(c.first);if(!detail)return;
    for(const h of c.evidence.filter(h=>h.valid)){const n=Math.round(320*h.scale),coeff=Array.from({length:17},(_,i)=>2*Math.cos(2*Math.PI*(400+100*i)/(16000*h.scale))),d=detail.hypotheses.find(d=>d.start===h.start&&d.k===h.k);
      for(const win of d.completionAudit.windows){const at=Math.round(h.start+(640+win.index*1280+320)*h.scale);win.joint=win.missing===null?[]:CAPS.map(M=>({M,...joint(n,coeff,j=>s.ring[at%(s.ring.length/2)+j],j=>s.missingIn(at+j,1)===0,M,win.word)}));}
    }};}
}
module.exports={envelope,joint,JointReceiver};
