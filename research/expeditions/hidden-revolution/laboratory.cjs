"use strict";
// Standalone synthetic checks; no external dependencies. node laboratory.cjs
function laboratory() {
  const pi=Math.PI, root=Math.sqrt(3), D=4*pi/root;
  let checks=0, maxError=0, maxGridExcess=0, aliasProfiles=0, gridProfiles=0, gridPoints=0, tickChecks=0;
  function check(ok,msg){checks++;if(!ok)throw Error(msg);}
  function close(x,y,tol=2e-12){maxError=Math.max(maxError,Math.abs(x-y));check(Math.abs(x-y)<tol,"numeric mismatch "+x+" "+y);}
  function fourier(s,d,t) {
    const rho=Math.exp(-1.5*s*t), phase=root*d*t/2;
    return Array.from({length:3},(_,j)=>(1+2*rho*Math.cos(phase-2*pi*j/3))/3);
  }
  // Independent Poisson mixture of literal random-walk steps.
  function uniformization(s,d,t) {
    let a=(s+d)/(2*s), b=1-a, x=[1,0,0], w=Math.exp(-s*t), p=x.map(v=>w*v);
    for(let j=1;j<=Math.max(80,Math.ceil(s*t+16*Math.sqrt(s*t)+60));j++){
      x=x.map((_,k)=>a*x[(k+2)%3]+b*x[(k+1)%3]);w*=s*t/j;
      p=p.map((v,k)=>v+w*x[k]);
    }
    return p;
  }
  function gap(m,c,t) {
    let v=Infinity;
    for(let k=1;k<=m;k++)v=Math.min(v,2*Math.exp(-c*t)*Math.abs(Math.sin(pi*k*t)));
    return v;
  }
  function gcd(a,b){while(b){let x=a%b;a=b;b=x;}return a;}
  // Candidate populations including exact boundary; D is the rate-difference spacing at T=1.
  for(let m=1;m<=16;m++)for(let excess of [0,.125,.75,2.5]){
    let s=m*D/2+excess, d0=-m*D/2, baseline=fourier(s,d0,1);
    for(let j=0;j<=m;j++){
      let d=d0+j*D;
      check(Math.abs(d)<=s+1e-12,"nonnegative rate");
      for(let t of [0,.01,.07,.23,1,2]){
        let p=fourier(s,d,t), q=uniformization(s,d,t);
        close(p.reduce((a,b)=>a+b,0),1);
        check(p.every(v=>v>=-1e-12),"positive row");
        p.forEach((v,i)=>close(v,q[i]));
        if(t===1) p.forEach((v,i)=>close(v,baseline[i]));
      }
      aliasProfiles++;
    }
    let c=1.5*s, tstar=Math.atan(pi/c)/pi, value=2*Math.exp(-c*tstar)*Math.sin(pi*tstar);
    check(tstar<1/(m+1),"optimal lag before packing");
    close(gap(m,c,tstar),value);
    for(let j=0;j<=2000;j++){
      let val=gap(m,c,j/2000); maxGridExcess=Math.max(maxGridExcess,val-value);
      check(val<=value+1e-12,"grid exceeds analytic optimum");gridPoints++;
    }
    gridProfiles++;
  }
  // Exact clock tick collision tests: second lag u/v, first lag one.
  for(let v=1;v<=48;v++)for(let u=1;u<=v;u++)for(let k=1;k<=64;k++){
    check(((k*u)%v===0)===(k%(v/gcd(u,v))===0),"rational clock collision");tickChecks++;
  }
  // A reversible process and a biased process agree at all integer lags.
  let examples=[];
  for(let eps of [1,.1,.01,.001,.000001]){
    let s=D+eps, d=D, a=(s+d)/2,b=(s-d)/2,c=1.5*s,tstar=Math.atan(pi/c)/pi;
    for(let t of [1,2,3])fourier(s,0,t).forEach((x,i)=>close(x,fourier(s,d,t)[i]));
    let p=fourier(s,0,tstar),q=fourier(s,d,tstar);
    check(p.some((v,i)=>Math.abs(v-q[i])>.01),"off-grid witness");
    examples.push({eps,a,b,reversibleRates:[s/2,s/2],sampleRow:fourier(s,0,1),optimalLag:tstar,modeGap:2*Math.exp(-c*tstar)*Math.sin(pi*tstar),halfLagGap:gap(1,c,.5),pathKL:d*Math.log(a/b),offGridRows:[p,q]});
  }
  return {classification:"synthetic numerical witness, not independent review",checks,aliasProfiles,gridProfiles,gridPoints,tickChecks,maxError,maxGridExcess,examples};
}
if(typeof module!=="undefined" && require.main===module) console.log(JSON.stringify(laboratory(),null,2));
