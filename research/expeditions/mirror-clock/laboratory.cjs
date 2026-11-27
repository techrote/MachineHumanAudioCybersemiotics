"use strict";
function laboratory(){
  const assert=(x,m)=>{if(!x)throw Error(m)};
  const seq=(x,N,s=0)=>Array.from({length:N},(_,t)=>x[(t+s)%x.length]);
  const dot=(x,y)=>x.reduce((a,v,i)=>a+v*y[i],0);
  const codes=(x,N,K)=>Array.from({length:K},(_,s)=>[-1,1].map(sign=>({s,sign,v:seq(x,N,s).map(a=>sign*a)}))).flat();
  const trim=(a,b,r)=>a.map((v,i)=>(v-b[i])**2).sort((a,b)=>a-b).slice(0,a.length-r).reduce((a,b)=>a+b,0);
  function profile(x,N,K=3){
    const c=codes(x,N,K),p=Array(N+1).fill(Infinity);
    for(let s=0;s<K;s++)for(let u=s+1;u<K;u++)for(let sign of [0,1]){
      const a=c[2*s].v,b=c[2*u+sign].v;
      const q=a.map((v,i)=>(v-b[i])**2).sort((a,b)=>a-b);let sum=0;p[N]=0;
      for(let j=0;j<N;j++){sum+=q[j];p[N-j-1]=Math.min(p[N-j-1],sum)}
    }
    return p
  }
  function db(K){
    const a=Array(2*K+1).fill(0),out=[];
    function rec(t,p){if(t>K){if(K%p===0)out.push(...a.slice(1,p+1));return}a[t]=a[t-p];rec(t+1,p);for(let j=a[t-p]+1;j<2;j++){a[t]=j;rec(t+1,t)}}
    rec(1,1);return out.map(b=>2*b-1)
  }
  let dbProfiles=[],orthogonalityChecks=0,trimChecks=0;
  for(let K=2;K<=9;K++){
    const x=db(K),N=x.length;
    assert(N===2**K,"DB length");
    assert(new Set(Array.from({length:N},(_,s)=>seq(x,K,s).join(","))).size===N,"DB windows");
    assert(x.reduce((a,b)=>a+b,0)===0,"DB centered");
    for(let s=0;s<K;s++)for(let u=s+1;u<K;u++){assert(dot(seq(x,N,s),seq(x,N,u))===0,"DB orthogonal");orthogonalityChecks++}
    let p=profile(x,N,K);
    for(let r=0;r<=N;r++){assert(p[r]===4*Math.max(0,N/2-r),"DB trim");trimChecks++}
    dbProfiles.push({K,N,clean:p[0],atHalf:p[N/2]})
  }
  let p3=0;
  for(let a=-40;a<=40;a++)for(let b=-40;b<=40;b++)for(let c=-40;c<=40;c++){
    const E=a*a+b*b+c*c,C=a*b+b*c+c*a;
    assert(2*(E-Math.abs(C))<=7200,"period 3 bound");p3++
  }
  assert(profile([2,2,-1],3)[0]===18,"sharp scalar triple");
  const p4=profile([1,1,1,-1],4,4);assert(p4.join(",")==="8,4,0,0,0","four-tick result");
  const centered=[2,2,2,-6];assert(dot(centered,seq(centered,4,1))===-16,"centered four-tick correlation");
  let radialChecks=0;
  for(let K=2;K<=8;K++)for(let N=1;N<=12;N++){
    const p=profile(Array.from({length:K},(_,i)=>i),N,K);
    assert(p[N-1]===1,"one-survivor radial");
    for(let r=N-Math.ceil(N/(K*(K-1)));r<N;r++){assert(p[r]===N-r,"high-fault radial");radialChecks++}
  }
  let exhaustive=[];
  for(let [N,alphabet] of [[4,[-2,-1,0,1,2]],[8,[-1,0,1]],[9,[-1,0,1]]]){
    let best=Array(N+1).fill(-1),w=Array(N+1),x=Array(N+2),count=0;
    function visit(i){if(i===x.length){count++;let p=profile(x,N);for(let r=0;r<=N;r++)if(p[r]>best[r]){best[r]=p[r];w[r]=x.slice()}return}for(let a of alphabet){x[i]=a;visit(i+1)}}
    visit(0);
    for(let r=0;r<=N;r++)assert(profile(w[r],N)[r]===best[r],"witness replay");
    exhaustive.push({N,alphabet,count,best,witnesses:w})
  }
  assert(exhaustive[0].best.join(",")==="32,16,4,1,0","5-level census");
  assert(exhaustive[1].best.join(",")==="16,12,8,4,2,1,0,0,0","8-tick census");
  assert(exhaustive[2].best.join(",")==="16,12,8,4,3,2,1,0,0,0","9-tick census");
  function list(c,z,e,bound){
    const ok=new Set();
    for(let h of c){
      const d=z.flatMap((v,i)=>v===null?[]:[(v-4*h.v[i])**2]).sort((a,b)=>a-b);
      if(d.slice(0,Math.max(0,d.length-e)).reduce((a,b)=>a+b,0)<=bound)ok.add(h.s)
    }return [...ok].sort((a,b)=>a-b)
  }
  let midpointChecks=0,strictChecks=0;
  for(let [x,N,K] of [[[1,1,1,-1],8,4],[db(3),8,3],[[0,1,2],9,3],[[2,2,-1],9,3],[exhaustive[2].witnesses[4],9,3]]){
    const c=codes(x,N,K),p=profile(x,N,K);
    for(let e=0;e<=3;e++)for(let f=0;2*e+f<=N;f++){
      const r=2*e+f;
      for(let a of c)for(let b of c)if(a.s<b.s){
        const order=Array.from({length:N},(_,i)=>i).sort((i,j)=>(a.v[j]-b.v[j])**2-(a.v[i]-b.v[i])**2);
        let z=a.v.map((v,i)=>2*(v+b.v[i]));
        for(let j=0;j<r;j++){let i=order[j];z[i]=j<f?null:j<f+e?4*b.v[i]:4*a.v[i]}
        const D=trim(a.v,b.v,r);
        let L=list(c,z,e,4*D);
        assert(L.includes(a.s)&&L.includes(b.s),"attained midpoint");midpointChecks++;
        if(D===p[r]&&D>0){
          z=a.v.map((v,i)=>3*v+b.v[i]);
          for(let j=0;j<r;j++){let i=order[j];z[i]=j<f?null:j<f+e?4*b.v[i]:4*a.v[i]}
          L=list(c,z,e,D);assert(L.length===1&&L[0]===a.s,"strict quarter-distance decode");strictChecks++;
        }
      }
    }
  }
  // Integer simplex in three coordinates; cycling coordinates is an isometry.
  let simplex=[[2,-1,-1],[-1,2,-1],[-1,-1,2]];
  for(let t=0;t<3;t++){assert(simplex[t].map((_,i)=>simplex[t][(i+2)%3]).join(",")===simplex[(t+1)%3].join(","),"simplex alias")}
  // Independent per-tick sign can erase every phase of a constant-magnitude pilot.
  for(let s=0;s<4;s++)assert(seq([1,1,1,-1],8,s).every(v=>v*v===1),"time-varying sign alias");
  return {dbProfiles,orthogonalityChecks,trimChecks,periodThreeGridChecks:p3,periodFourProfile:p4,radialChecks,exhaustive,midpointChecks,strictChecks,negativeControls:{simplexCyclicCoordinatePermutation:true,perTickSignAlias:true,periodFourCenteredEnergy:48,periodFourCenteredCross:-16,periodFourUnknownBiasSquaredDistance:4},assertionFailures:0}
}
console.log(JSON.stringify(laboratory(),null,2));
