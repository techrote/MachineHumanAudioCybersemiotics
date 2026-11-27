'use strict';
// Refs #512. Diagnostic-only observed-sample sinusoid fit; no wire change.
const {DependencyReceiver}=require('./dependency-v14.cjs');
// fit a*cos(w*i)+b*sin(w*i) on observed coordinates, not a compressed clock.
// Missing sample values are never read. Ill-conditioned or quiet fits abstain.
function observedScore(n,c,read,seen,minCoverage=.75){
  const cw=c/2,sw=Math.sqrt(Math.max(0,1-cw*cw));let u=1,v=0,aa=0,ab=0,bb=0,ax=0,bx=0,e=0,k=0;
  for(let i=0;i<n;i++){if(seen(i)){const x=read(i);aa+=u*u;ab+=u*v;bb+=v*v;ax+=u*x;bx+=v*x;e+=x*x;k++;}const t=u*cw-v*sw;v=v*cw+u*sw;u=t;}
  const det=aa*bb-ab*ab;if(k<n*minCoverage||e<k*250**2||det<.05*k*k)return 0;
  return Math.max(0,Math.min(1,(bb*ax*ax-2*ab*ax*bx+aa*bx*bx)/(det*e)));
}
class PartialReceiver extends DependencyReceiver {
  resetDiagnostic(){super.resetDiagnostic();const s=this.shadow,base=s.score.bind(s);s.stats.partialScores=0;
    s.score=(at,n,c)=>{const missing=s.missingIn(at,n);if(missing===0||missing===null)return base(at,n,c);
      // Preamble stays whole-window only: all body frequencies <= 2000 Hz;
      // the smallest preamble frequency is 2300 Hz, even with clock scaling.
      if(c<2*Math.cos(2*Math.PI*2150/16000)||missing>n/4)return 0;
      s.stats.partialScores++;return observedScore(n,c,i=>s.ring[at%(s.ring.length/2)+i],i=>s.missingIn(at+i,1)===0);
    };
  }
}
module.exports={PartialReceiver,observedScore};
