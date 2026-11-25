"use strict";
// MHAC #426. Synthetic finite checks, no empirical or security claim.
function laboratory(){
  function ok(v,msg){if(!v)throw Error(msg)}
  const pc=x=>{x=x-((x>>>1)&0x55555555);x=(x&0x33333333)+((x>>>2)&0x33333333);return (((x+(x>>>4))&0x0f0f0f0f)*0x01010101)>>>24};
  const C=(n,k)=>{if(k<0||k>n)return 0;let a=1;for(let i=1;i<=k;i++)a=a*(n-i+1)/i;return a};
  const counts={fourierCoefficients:0,integerWeightVectors:0,weightSignEvaluations:0,orientationAssignments:0,balancedTargets:0,receiptTargetEvaluations:0,decoderCells:0,parityTargetEvaluations:0};
  const out=[];
  function support(m,z){let mask=0;for(let i=0;i<m;i++)mask|=1<<(2*i+((z>>i)&1));return mask}
  function audit(m,Z){
    const masks=Z.map(z=>support(m,z)), L=Z.length;
    // Each equally weighted label has a uniform posterior on its support.
    // The row probabilities are 2/L if x belongs to that support.
    for(let x=0;x<2*m;x++)ok(masks.filter(s=>(s>>x)&1).length*2===L,"uniform prior");
    for(let g=0;g<m;g++)for(let s of masks){
      const seen=new Set();
      for(let x=0;x<2*m;x++)if((s>>x)&1){
        const observed=x===2*g+1?2*g:x;
        ok(!seen.has(observed),"pair collapse decoder conflict");seen.add(observed);counts.decoderCells++;
      }
    }
    let max=0, arg=0;
    for(let t=0;t<(1<<(2*m));t++)if(pc(t)===m){
      let n=0;for(let s of masks)n+=Math.abs(2*pc(t&s)-m);
      counts.balancedTargets++;counts.receiptTargetEvaluations+=L;
      if(n>max){max=n;arg=t}
    }
    return {labels:new Set(Z).size,slots:L,scoreNumerator:L*m+max,scoreDenominator:2*L*m,witness:arg};
  }
  for(let m of [2,4,6,8,10]){
    const Q=1<<m, full=Q-1;
    // Direct Walsh spectrum of |sum signs|.
    for(let s=0;s<Q;s++){
      let a=0;for(let z=0;z<Q;z++)a+=Math.abs(m-2*pc(z))*(pc(s&z)%2?-1:1);
      const d=pc(s);
      if(d===0)ok(a===m*C(m,m/2),"constant spectrum");
      else if(d%2)ok(a===0,"odd spectrum");
      else ok(a*C(m-2,d-2)===4*C(m-2,(m-2)/2)*((-1)**(d/2-1))*C((m-2)/2,d/2-1),"even spectrum");
      counts.fourierCoefficients++;
    }
    // Exhaust fixed-denominator posterior weight vectors for small m.
    if(m<=6){
      const D=2*m, w=[];
      function visit(rem,i){
        if(i===m-1){w[i]=rem;let a=0;for(let z=0;z<Q;z++){let b=0;for(let j=0;j<m;j++)b+=w[j]*(((z>>j)&1)?-1:1);a+=Math.abs(b)}
          ok(a>=D*C(m,m/2),"convex lower bound");ok((a===D*C(m,m/2))===w.every(x=>x===D/m),"strict equality");
          counts.integerWeightVectors++;counts.weightSignEvaluations+=Q;return;
        }
        for(let v=0;v<=rem;v++){w[i]=v;visit(rem-v,i+1)}
      }visit(D,0)
    }
    const Z=Array.from({length:Q},(_,z)=>z).filter(z=>m===2||pc(z&7)%2===0);
    if(m<=8){
      const a=audit(m,Z);ok(a.scoreNumerator*2*Q===a.scoreDenominator*(Q+C(m,m/2)),"Boolean optimum");
      out.push({m,kind:"exact Boolean",...a});
    }
    if(m<=4){
      let valid=0;for(let orient=0;orient<(1<<(Q/2));orient++){
        let zs=[];for(let i=0;i<Q/2;i++)zs.push((orient>>i)&1?full^i:i);
        if(Array.from({length:m},(_,i)=>zs.filter(z=>(z>>i)&1).length*2===zs.length).every(Boolean))valid++;
        counts.orientationAssignments++;
      }ok(m===2?valid===0:valid>0,"orientation feasibility");out.push({m,kind:"balanced orientations",valid});
    }
    if((m&(m-1))===0){
      let A=[];for(let u=0;u<m;u++)for(let b=0;b<2;b++){
        let z=0;for(let y=0;y<m;y++)z|=((pc(u&y)%2)^b)<<y;A.push(z)
      }
      ok(new Set(A).size===2*m,"affine label count");
      for(let u=0;u<m;u++)for(let v=0;v<2;v++)if(u||v){
        let bias=0;for(let z of A){let sum=0;for(let y=0;y<m;y++)sum+=((pc(u&y)+v*((z>>y)&1))%2)?-1:1;bias+=Math.abs(sum);counts.parityTargetEvaluations++}
        ok(bias===(v?2*m:0),"parity optimum");
      }
      let a=audit(m,A);out.push({m,kind:"exact parity, Boolean audit",...a});
    }
  }
  let seed=0x41657;const rand=()=>{seed^=seed<<13;seed^=seed>>>17;seed^=seed<<5;return seed>>>0};
  for(let [m,L] of [[8,16],[10,64]]){
    let Z=[];for(let i=0;i<L;i++){let z=rand()&((1<<m)-1);Z.push(z,z^((1<<m)-1))}
    let a=audit(m,Z);ok(a.labels<2**(m-1),"sparse example");ok(a.scoreNumerator*2**(m+1)>=a.scoreDenominator*(2**m+C(m,m/2)),"optimum lower bound");out.push({m,kind:"sampled pairs, exhaustive Boolean audit",...a})
  }
  return {counts,results:out};
}
console.log(JSON.stringify(laboratory(), null, 2));
