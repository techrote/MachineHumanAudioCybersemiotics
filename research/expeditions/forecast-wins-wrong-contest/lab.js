"use strict";
// Synthetic bounded integer checks, not empirical data. Node: node lab.js
function laboratory(){
  const out={histograms:0,inequalityChecks:0,medianChecks:0,constructedLaws:0,affineChecks:0,brierChecks:0,comparativeControls:0,refusals:0};
  const yes=(b,m)=>{if(!b)throw Error(m)};
  // Integer posterior numerators x on denominator D, integer probability weights.
  function stats(rows,D){
    if(!Number.isSafeInteger(D)||D<=0||!Array.isArray(rows)||!rows.length||
      rows.some(r=>!Array.isArray(r)||r.length!==2||!Number.isSafeInteger(r[0])||r[0]<0||r[0]>D||!Number.isSafeInteger(r[1])||r[1]<0))throw Error("invalid law");
    const W=rows.reduce((s,r)=>s+r[1],0);
    if(W<=0||W%2)throw Error("positive even mass required; double odd weights");
    const S=rows.reduce((s,[x,w])=>s+x*w,0),T=rows.reduce((s,[x,w])=>s+x*x*w,0);
    let left=W/2,L=0,m=0;
    for(const [x,w] of [...rows].sort((a,b)=>a[0]-b[0])){
      const take=Math.min(left,w);L+=take*x;left-=take;if(take)m=x;
    }
    const N=S-2*L,V=W*T-S*S,M=Math.max(S,W*D-S);
    yes([W,S,T,N,V,M,W*D].every(Number.isSafeInteger),"unsafe arithmetic");
    yes(N>=0&&N<=Math.min(S,W*D-S),"half-spread support");
    yes(N*N<=V&&V<=M*N,"variance bounds");out.inequalityChecks+=2;
    yes(rows.reduce((s,[x,w])=>s+w*Math.abs(x-m),0)===N,"median identity");out.medianChecks++;
    // Direct calibrated binary joint counts: w*(D-x), w*x; loss numerators.
    const loss=rows.reduce((s,[x,w])=>s+w*((D-x)*x*x+x*(D-x)*(D-x)),0);
    yes(loss===D*(D*S-T),"direct Brier identity");out.brierChecks++;
    return {W,S,N,V,den:W*D,loss:D*S-T,acc:rows.reduce((s,[x,w])=>s+w*Math.max(x,D-x),0)};
  }
  for(let D=1;D<=12;D++)for(let n=2;n<=8;n+=2){
    const xs=[];
    function walk(lo){
      if(xs.length===n){stats(xs.map(x=>[x,1]),D);out.histograms++;return}
      for(let x=lo;x<=D;x++){xs.push(x);walk(x);xs.pop()}
    }
    walk(0);
  }
  for(let D=2;D<=30;D++)for(let A=Math.ceil(D/2);A<=D;A++)for(let B=0;B<=D-A;B++)for(let F=1;F<=8;F++)for(let C=0;C<=F;C++){
    const W=2*F*(A+B);
    const rows=[[0,2*C*B],[A-B,(F-C)*(A+B)],[A+B,(F-C)*(A+B)+2*C*A]];
    for(const reflected of [false,true]){
      const rr=rows.map(([x,w])=>[reflected?D-x:x,w]);
      const a=reflected?D-A:A;
      const s=stats(rr,D);
      yes(s.W===W&&s.S===W*a&&s.N===W*B,"constructed mean/spread");
      yes(s.V*F===W*W*((F-C)*B*B+C*A*B),"constructed variance");
      out.constructedLaws++;
      const t=stats(rr.map(([x,w])=>[D+x,w]),2*D);
      yes(t.N===s.N&&t.V===s.V&&t.S===s.S+W*D,"affine support");
      out.affineChecks++;
    }
  }
  // A: half 2/3 and half 1; B: 1/5 at 1/2, 4/5 at 11/12.
  // C: 3/13 at 1/2, 10/13 at 14/15. All on denominator 60.
  const a=stats([[40,1],[60,1]],60),b=stats([[30,2],[55,8]],60),c=stats([[30,6],[56,20]],60);
  const eqRat=(n,d,N,D)=>n*D===N*d;
  for(const s of [a,b,c]){
    yes(eqRat(s.S,s.den,5,6)&&eqRat(s.acc,s.den,5,6),"same mean and hard accuracy");
    out.comparativeControls++;
  }
  const tv=s=>[Math.max(0,3*(s.S-s.N)-2*s.den),8*s.den];
  for(const [s,lossN,lossD,tvN,tvD] of [[a,1,9,0,1],[b,1,9,1,32],[c,19,180,1,40]]){
    yes(eqRat(s.loss,s.W*60*60,lossN,lossD),"named Brier");
    yes(eqRat(...tv(s),tvN,tvD),"named leakage");out.comparativeControls+=2;
  }
  const no=stats([[50,2]],60);yes(eqRat(...tv(no),1,16),"constant preview");out.comparativeControls++;
  for(const [rows,D] of [[[],1],[[[0,0]],1],[[[2,2]],1],[[[0,-2]],1],[[[0,1]],1],[[[0,2]],0]]){
    let threw=false;try{stats(rows,D)}catch(e){threw=true}yes(threw,"expected refusal");out.refusals++;
  }
  return out;
}
console.log(JSON.stringify(laboratory(),null,2));
