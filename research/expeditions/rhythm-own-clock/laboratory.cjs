'use strict';
// Synthetic experiment; run: node laboratory.cjs
function laboratory(){
  const ok=(c,msg)=>{if(!c)throw Error(msg)};
  const gcd=(a,b)=>b?gcd(b,a%b):Math.abs(a);
  const rat=(a,b=1)=>{let g=gcd(a,b);return [a/g,b/g]};
  const cmp=(a,b)=>a[0]*b[1]-b[0]*a[1];
  const eq=(a,b)=>cmp(a,b)===0;
  const P=n=>Math.floor((n-1)**2/4);
  function* subsets(n,k,start=0,prefix=[]){
    if(!k){yield prefix;return}
    for(let i=start;i<=n-k;i++)yield* subsets(n,k-1,i+1,[...prefix,i]);
  }
  function* words(n,alphabet,prefix=[]){
    if(!n){yield prefix;return}
    for(const a of alphabet)yield* words(n-1,alphabet,[...prefix,a]);
  }
  // Triple certificate; all arguments integer, fractions exact in tested range.
  function radius(z,I){
    let best=[0,1], witness=null;
    for(let a=0;a<I.length;a++)for(let b=a+1;b<I.length;b++)for(let c=b+1;c<I.length;c++){
      let i=I[a],j=I[b],k=I[c];
      let r=rat(Math.abs((k-i)*z[j]-(k-j)*z[i]-(j-i)*z[k]),2*(k-i));
      if(cmp(r,best)>0){best=r;witness=[i,j,k]}
    }
    return {r:best,witness};
  }
  // Independent oracle: choose slope at an intersection of two adjusted samples.
  // The range of adjusted samples is convex piecewise linear and has a minimum
  // at a breakpoint (or on a flat segment ending at one).
  function slopeOracle(z,I){
    if(I.length<=2)return [0,1];
    let best=null;
    for(let a=0;a<I.length;a++)for(let b=a+1;b<I.length;b++){
      let i=I[a],j=I[b],den=j-i,num=z[j]-z[i];
      let v=I.map(k=>den*z[k]-num*k);
      let r=rat(Math.max(...v)-Math.min(...v),2*den);
      if(best===null||cmp(r,best)<0)best=r;
    }
    return best;
  }
  // Pair slope constraints for a given radius, with exact integer cross products.
  function feasible(z,I,E){
    let lower=null,upper=null;
    for(let a=0;a<I.length;a++)for(let b=a+1;b<I.length;b++){
      let i=I[a],j=I[b],den=(j-i)*E[1],num=(z[j]-z[i])*E[1];
      let lo=[num-2*E[0],den],hi=[num+2*E[0],den];
      if(lower===null||cmp(lo,lower)>0)lower=lo;
      if(upper===null||cmp(hi,upper)<0)upper=hi;
    }
    return lower===null||cmp(lower,upper)<=0;
  }
  let counts={full_words:0,subset_radii:0,feasibility_checks:0,curvature_words:0,quadratic_subsets:0,quadratic_minima:0,adversarial_profiles:0,adversarial_subset_comparisons:0};
  let example=null;
  for(let n=1;n<=8;n++)for(const z of words(n,[-1,0,1])){
    let I=Array.from({length:n},(_,i)=>i),a=radius(z,I).r,b=slopeOracle(z,I);
    ok(eq(a,b),"full radius mismatch");
    ok(feasible(z,I,a),"radius infeasible"); counts.feasibility_checks++;
    if(a[0]>0){let smaller=[2*a[0]-1,2*a[1]];ok(!feasible(z,I,smaller),"smaller radius feasible");counts.feasibility_checks++;}
    counts.full_words++;
    if(n<=6){
      let minimum=Array.from({length:n+1},()=>null);
      for(let m=0;m<=n;m++)for(const J of subsets(n,m)){
        let u=radius(z,J).r,v=slopeOracle(z,J);
        ok(eq(u,v),"subset radius mismatch"); counts.subset_radii++;
        if(minimum[m]===null||cmp(u,minimum[m])<0)minimum[m]=u;
      }
      // At each threshold, equivalence between robust radius and existence of
      // a subset of n-2t-e samples inside the common affine strip.
      for(let t=0;2*t<=n;t++)for(let e=0;2*t+e<=n;e++)for(const E of [[0,1],[1,4],[1,2],[1,1]]){
        let m=n-2*t-e, possible=false;
        for(const J of subsets(n,m)){counts.adversarial_subset_comparisons++;if(feasible(z,J,E))possible=true;}
        ok(possible===(cmp(minimum[m],E)<=0),"adversarial strip mismatch");counts.adversarial_profiles++;
      }
    }
  }
  for(let n=3;n<=10;n++)for(const curvature of words(n-2,[-1,0,1])){
    let z=[0,0];for(let c of curvature)z.push(2*z.at(-1)-z.at(-2)+c);
    let I=Array.from({length:n},(_,i)=>i),r=radius(z,I).r;
    let kappa=Math.max(...curvature.map(Math.abs));
    ok(cmp(r,[kappa*P(n),4])<=0,"curvature bound");
    if(curvature.every(x=>x===1)||curvature.every(x=>x===-1))ok(eq(r,[P(n),4]),"curvature equality");
    counts.curvature_words++;
  }
  let quadratic=[];
  for(let n=3;n<=15;n++){
    let z=Array.from({length:n},(_,i)=>i*i);
    for(let m=0;m<=n;m++){
      let best=null;
      for(const I of subsets(n,m)){
        let r=radius(z,I).r;
        let expected=0;
        if(m>=3)for(const j of I)expected=Math.max(expected,(j-I[0])*(I.at(-1)-j));
        ok(eq(r,[expected,2]),"quadratic subset formula");
        if(best===null||cmp(r,best)<0)best=r;
        counts.quadratic_subsets++;
      }
      let v=m>=3?P(m):0;ok(eq(best,[v,2]),"quadratic worst removal");
      counts.quadratic_minima++;
      if(n===12)quadratic.push({survivors:m,minimum_radius:best[0]/best[1]});
    }
  }
  // Concrete negative case: adjacent triple radius = 1/4, long witness = 9/4.
  const z=Array.from({length:7},(_,i)=>i*(i-1)/2);
  example={z,global:radius(z,[0,1,2,3,4,5,6]),adjacent:radius(z,[0,1,2]).r};
  ok(eq(example.global.r,[9,4]),"example");
  return {model:"exact integer/rational arithmetic; bounded affine log-tempo nuisance",counts,example,quadratic,assertion_failures:0};
}
if(require.main===module) console.log(JSON.stringify(laboratory(),null,2));
module.exports={laboratory};
