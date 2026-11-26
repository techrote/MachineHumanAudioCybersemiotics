const lab = function lab(){
  const abs=x=>x<0n?-x:x,gcd=(a,b)=>b?gcd(b,a%b):abs(a);
  function Q(n,d=1n){n=BigInt(n);d=BigInt(d);if(!d)throw Error("zero denominator");if(d<0n){n=-n;d=-d;}const g=gcd(n,d);return [n/g,d/g];}
  const Z=Q(0),O=Q(1),add=(a,b)=>Q(a[0]*b[1]+b[0]*a[1],a[1]*b[1]),sub=(a,b)=>Q(a[0]*b[1]-b[0]*a[1],a[1]*b[1]),mul=(a,b)=>Q(a[0]*b[0],a[1]*b[1]),div=(a,b)=>Q(a[0]*b[1],a[1]*b[0]),eq=(a,b)=>a[0]===b[0]&&a[1]===b[1],le=(a,b)=>sub(b,a)[0]>=0n,min=(a,b)=>le(a,b)?a:b,max=(a,b)=>le(a,b)?b:a,show=a=>a[0]+"/"+a[1],pow=(a,k)=>Q(a[0]**BigInt(k),a[1]**BigInt(k)),sum=a=>a.reduce(add,Z);
  const H=40,zeros=n=>Array(n).fill(Z);
  let assertions=0,profiles=0,convolution=0,symmetry=0,bounded=0,transport=0;
  function check(v,msg){assertions++;if(!v)throw Error(msg);}
  // Literal forward recursion: rates[x]=[right,left], absorbing endpoints 0,N.
  function exit(N,i,rates,H){
    let v=zeros(N+1);v[i]=O;const hi=zeros(H+1),lo=zeros(H+1);
    for(let t=1;t<=H;t++){
      const w=zeros(N+1);
      for(let x=1;x<N;x++){
        const [p,q]=rates[x],h=sub(O,add(p,q));
        w[x+1]=add(w[x+1],mul(v[x],p));
        w[x-1]=add(w[x-1],mul(v[x],q));
        w[x]=add(w[x],mul(v[x],h));
      }
      hi[t]=w[N];lo[t]=w[0];w[0]=Z;w[N]=Z;v=w;
      check(eq(add(add(sum(hi),sum(lo)),sum(v)),O),"mass");
    }return {hi,lo,tail:sum(v)};
  }
  function hit(N,i,r){return eq(r,O)?Q(i,N):div(sub(O,pow(r,i)),sub(O,pow(r,N)));}
  const rates=(N,p)=>Array.from({length:N+1},()=>[p,sub(O,p)]);
  function conditional(N,i,p,horizon=H){
    const r=div(sub(O,p),p),h=hit(N,i,r),x=exit(N,i,rates(N,p),horizon);
    return {hi:x.hi.map(v=>div(v,h)),lo:x.lo.map(v=>div(v,sub(O,h))),h,x};
  }
  const cdf=a=>{let v=Z;return a.map(x=>v=add(v,x));};
  function conv(a,b,t){let v=Z;for(let j=0;j<=t;j++)if(a[j][0]&&b[t-j][0])v=add(v,mul(a[j],b[t-j]));return v;}
  function means(N,i,p){
    const r=div(sub(O,p),p);
    const f=k=>eq(r,O)?Q(k*k,3):mul(Q(k),div(add(O,pow(r,k)),sub(O,pow(r,k))));
    return eq(r,O)?sub(f(N),f(i)):div(sub(f(N),f(i)),sub(mul(Q(2),p),O));
  }
  for(const p of [Q(1,2),Q(2,3),Q(3,4),Q(9,10)]){
    for(let a=1;a<=6;a++)for(let b=a;b<=7;b++){
      const N=a+b,near=conditional(N,b,p),flip=conditional(N,b,sub(O,p)),reflected=conditional(N,a,p);
      const delay=a===b?[O,...zeros(H)]:conditional(b,a,p).hi;
      const FN=cdf(near.hi),FF=cdf(near.lo);profiles++;
      for(let t=0;t<=H;t++){
        check(eq(near.hi[t],flip.hi[t])&&eq(near.lo[t],flip.lo[t]),"state conditioned symmetry");
        check(eq(near.lo[t],reflected.hi[t]),"reflected far");
        check(eq(conv(near.hi,delay,t),near.lo[t]),"convolution");convolution++;
        check(le(FF[t],FN[t]),"stochastic order");
        if((a+b)%2)check(!near.hi[t][0]||!near.lo[t][0],"parity separates");
      }
      check(eq(sub(means(N,a,p),means(N,b,p)),a===b?Z:means(b,a,p)),"mean difference");
    }
  }
  // Published Conjecture 2.9: varying holding probabilities, fixed up/down ratio.
  for(let N=3;N<=8;N++)for(const r of [Q(1,3),Q(2,3),Q(1),Q(3,2),Q(3)]){
    const rr=Array.from({length:N+1},(_,i)=>{const move=Q(2+(i%4),6);const p=div(move,add(O,r));return [p,mul(r,p)];});
    for(let i=1;i<N;i++){
      const x=exit(N,i,rr,H),y=exit(N,i,rr.map(([p,q])=>[q,p]),H);
      for(let t=0;t<=H;t++){
        check(eq(y.hi[t],mul(pow(r,N-i),x.hi[t])),"upper swap ratio");
        check(eq(x.lo[t],mul(pow(r,i),y.lo[t])),"lower swap ratio");symmetry+=2;
      }
    }
  }
  // Variable ratio negative control: upper first-passage coefficient ratio changes.
  const rr=[[Z,Z],[Q(1,2),Q(1,4)],[Q(1,4),Q(1,2)],[Z,Z]];
  const x=exit(3,1,rr,4),y=exit(3,1,rr.map(([p,q])=>[q,p]),4);
  check(!eq(mul(x.hi[2],y.hi[4]),mul(x.hi[4],y.hi[2])),"variable-ratio control");
  for(let j=1;j<=19;j++){
    const p=Q(j,20),w=mul(p,sub(O,p)),m=conditional(4,3,p),A=cdf(m.hi),B=cdf(m.lo);
    check(eq(m.hi[1],div(sub(O,mul(Q(2),w)),sub(O,w))),"near atom");
    check(eq(m.lo[3],sub(O,mul(Q(2),w))),"far atom");
    check(!le(A[1],B[4]),"3-tick cap impossible");
    for(let t=0;t<=H;t++){
      check(le(t>=4?A[t-4]:Z,B[t])&&le(B[t],A[t]),"4-tick cap");bounded++;
      if(t%2===1){
        const k=(t-1)/2;
        check(eq(sub(O,A[t]),mul(div(w,sub(O,w)),pow(mul(Q(2),w),k))),"near closed tail");
        check(eq(sub(O,B[t]),pow(mul(Q(2),w),k)),"far closed tail");
      }
    }
    // Explicit quantile overlap transport on finite observed prefix.
    for(let s=1;s<=H;s++)if(m.hi[s][0])for(let t=1;t<=H;t++)if(m.lo[t][0]){
      const overlap=max(Z,sub(min(A[s],B[t]),max(A[s-1],B[t-1])));
      if(overlap[0]){check(t>=s&&t-s<=4,"transport support");transport++;}
    }
  }
  const p=Q(3,4),m=conditional(4,3,p),other=conditional(4,3,sub(O,p));
  const priorNear=div(add(m.h,other.h),Q(2)),stateTV=sub(m.h,other.h),nearFarTV=m.hi[1],timeTV=mul(stateTV,nearFarTV),farMean=means(4,1,p),nearMean=means(4,3,p),added=mul(priorNear,sub(farMean,nearMean));
  check(eq(timeTV,Q(1,2))&&eq(added,Q(8,5))&&eq(farMean,Q(21,5)),"worked example");
  const odd=conditional(3,2,p),oddFlip=conditional(3,2,sub(O,p));
  return {status:"PASS",arithmetic:"exact BigInt rational",horizon:H,assertions,homogeneousProfiles:profiles,convolutionCoefficientChecks:convolution,inhomogeneousSwapCoefficientChecks:symmetry,boundedCDFChecks:bounded,quantileTransportPositiveCells:transport,variableRatioNegative:{original:[show(x.hi[2]),show(x.hi[4])],swapped:[show(y.hi[2]),show(y.hi[4])]},example:{nearMassGivenPlus:show(m.h),nearMassGivenMinus:show(other.h),endpointAccuracy:show(div(add(O,stateTV),Q(2))),timingAccuracy:show(div(add(O,timeTV),Q(2))),nearMean:show(nearMean),farMean:show(farMean),fairPriorAddedMean:show(added),paddedTimingAccuracy:"1/2",parityExampleAccuracy:show(div(add(O,sub(odd.h,oddFlip.h)),Q(2))),nearPMF:m.hi.slice(0,12).map(show),farPMF:m.lo.slice(0,12).map(show)}};
};
if (typeof module !== 'undefined') module.exports=lab;
if (typeof require !== 'undefined' && require.main===module) console.log(JSON.stringify(lab(),null,2));
