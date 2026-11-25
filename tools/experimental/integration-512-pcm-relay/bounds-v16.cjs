'use strict';
// Refs #512. Conditional bounds on the unchanged v4 Goertzel body score.
const {PartialReceiver}=require('./partial-v15.cjs');
const CAPS=[128,512,1024,4096,32768];
function bounds(n,c,read,seen,M){
  if(!Number.isInteger(n)||n<1||!Number.isFinite(c)||Math.abs(c)>2||!Number.isInteger(M)||M<0||M>32768)throw Error('bounds input');
  const w=Math.acos(c/2);let re=0,im=0,e=0,rx=0,ry=0,m=0;
  for(let i=0;i<n;i++){const u=Math.cos(w*i),v=Math.sin(w*i);if(seen(i)){const x=read(i);re+=x*u;im+=x*v;e+=x*x;}else{m++;rx+=M*Math.abs(u);ry+=M*Math.abs(v);}}
  // Rectangle contains every possible missing-sample Fourier contribution.
  // Floating-point padding is an engineering margin, not formal interval arithmetic.
  const pad=1e-7*n*32768,lo=Math.hypot(Math.max(0,Math.abs(re)-rx-pad),Math.max(0,Math.abs(im)-ry-pad)),hi=Math.hypot(Math.abs(re)+rx+pad,Math.abs(im)+ry+pad),emax=e+m*M*M,threshold=n*250**2;
  return [e<threshold?0:Math.max(0,2*lo*lo/(n*emax)-1e-8),emax<threshold?0:2*hi*hi/(n*Math.max(e,threshold))+1e-8];
}
function certify(n,coeff,read,seen,M,word){
  const ranges=coeff.map(c=>bounds(n,c,read,seen,M));
  if(word===null)return {stable:ranges.every(r=>r[1]<.85),lower:null,rivalUpper:Math.max(...ranges.map(r=>r[1]))};
  const lower=ranges[word][0],rivalUpper=Math.max(...ranges.filter((_,i)=>i!==word).map(r=>r[1]));
  return {stable:lower>=.85&&lower-rivalUpper>=.2,lower,rivalUpper};
}
class BoundReceiver extends PartialReceiver {
  resetDiagnostic(){super.resetDiagnostic();const s=this.shadow,base=s.evaluate.bind(s);s.evaluate=c=>{base(c);const detail=s.details.get(c.first);if(!detail)return;
    for(const h of c.evidence.filter(h=>h.valid)){const n=Math.round(320*h.scale),coeff=Array.from({length:17},(_,i)=>2*Math.cos(2*Math.PI*(400+100*i)/(16000*h.scale))),windows=[];
      for(let i=0;i<h.words.length;i++){const at=Math.round(h.start+(640+i*1280+320)*h.scale),missing=s.missingIn(at,n);if(missing===0)continue;
        const certificates=missing===null?[]:CAPS.map(M=>({M,...certify(n,coeff,j=>s.ring[at%(s.ring.length/2)+j],j=>s.missingIn(at+j,1)===0,M,h.words[i])}));windows.push({index:i,missing,word:h.words[i],certificates});}
      const d=detail.hypotheses.find(d=>d.start===h.start&&d.k===h.k);d.completionAudit={windows,scope:'fixed-body-hypothesis-only',associationCertified:false};}};}
}
module.exports={bounds,certify,BoundReceiver,CAPS};
