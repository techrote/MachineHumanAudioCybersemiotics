/* MHAC #788, exact standalone synthetic laboratory. Node >=18. */
const laboratory = function laboratory(){
 const gcd=(a,b)=>{a=a<0n?-a:a;b=b<0n?-b:b;while(b){[a,b]=[b,a%b]}return a||1n};
 const F=(a,b=1n)=>{a=BigInt(a);b=BigInt(b);if(!b)throw Error("zero denominator");if(b<0n){a=-a;b=-b}let g=gcd(a,b);return [a/g,b/g]};
 const add=(a,b)=>F(a[0]*b[1]+a[1]*b[0],a[1]*b[1]), neg=a=>[-a[0],a[1]], sub=(a,b)=>add(a,neg(b)), mul=(a,b)=>F(a[0]*b[0],a[1]*b[1]), div=(a,b)=>F(a[0]*b[1],a[1]*b[0]), cmp=(a,b)=>a[0]*b[1]<b[0]*a[1]?-1:a[0]*b[1]>b[0]*a[1]?1:0, abs=a=>a[0]<0n?neg(a):a, str=a=>a[0]+"/"+a[1], num=a=>Number(a[0])/Number(a[1]);
 const zero=F(0),one=F(1),two=F(2),four=F(4), max=(a,b)=>cmp(a,b)>=0?a:b,min=(a,b)=>cmp(a,b)<=0?a:b;
 const dot=(a,b)=>a.reduce((s,v,i)=>add(s,mul(v,b[i])),zero), scale=(a,k)=>a.map(v=>mul(v,k)), minus=(a,b)=>a.map((v,i)=>sub(v,b[i]));
 function assert(q,m){if(!q)throw Error(m)}
 function* subsets(n,k,start=0,p=[]){if(k===0){yield p;return}for(let i=start;i<=n-k;i++)yield*subsets(n,k-1,i+1,[...p,i])}
 function project(t,d,v){let basis=[];for(let k=0;k<=d;k++){let w=t.map(i=>F(BigInt(i)**BigInt(k)));for(const b of basis)w=minus(w,scale(b,div(dot(w,b),dot(b,b))));if(dot(w,w)[0])basis.push(w)}for(const b of basis)v=minus(v,scale(b,div(dot(v,b),dot(b,b))));return v}
 function pair(a,b){const P=dot(a,a),Q=dot(b,b),C=abs(dot(a,b));if(!P[0])return {D:Q,g1:one,g2:one};if(!Q[0])return {D:P,g1:one,g2:one};
  function score(x,y){return sub(add(mul(P,mul(x,x)),mul(Q,mul(y,y))),mul(two,mul(C,mul(x,y))))}
  const x=max(one,div(C,P)),y=max(one,div(C,Q)),D1=score(x,one),D2=score(one,y);
  return cmp(D1,D2)<=0?{D:D1,g1:x,g2:one}:{D:D2,g1:one,g2:y}
 }
 function binaryD(n,r){if(r>=n/2)return zero;let h=n/2-r,z=n-r,a=Math.min(h,r);return mul(four,sub(F(h),F(a*a,z)))}
 function trimmedCounts(a,b,c,n){let best=null;for(let i=0;i<=a;i++)for(let j=0;j<=b;j++){let k=n-i-j;if(k<0||k>c)continue;let v=F(4*((i+k)*n-(i-k)**2),n);best=best===null?v:min(best,v)}return best}
 let contingencyProfiles=0,balancedProfiles=0, gainChecks=0;
 // All binary pair contingency tables, all trim budgets: independently enumerate retained counts.
 for(let N=4;N<=20;N+=4)for(let a=0;a<=N;a++)for(let b=0;b<=N-a;b++)for(let c=0;c<=N-a-b;c++){let d=N-a-b-c;
  for(let n=1;n<=N;n++){let z=min(trimmedCounts(b,a+d,c,n),trimmedCounts(a,b+c,d,n));assert(cmp(z,binaryD(N,N-n))<=0,"binary upper");contingencyProfiles++;if(a===b&&b===c&&c===d){assert(cmp(z,binaryD(N,N-n))===0,"balanced equality");balancedProfiles++}}
  // Check centered covariance <= both variances for signed binary words; count formulas use N times norms.
  let P=4*(a+b)*(c+d), Q=4*(a+c)*(b+d), C=4*Math.abs(a*d-b*c);assert(C<=Math.min(P,Q),"binary gain floor");gainChecks++;
 }
 function pilot(t,s,d){return t.map(i=>F(BigInt(i+s)**BigInt(d+2)))}
 function qdist(t,s,u,d){return pair(project(t,d,pilot(t,s,d)),project(t,d,pilot(t,u,d))).D}
 let polynomialPairs=0, quotientChecks=0,sharpProfiles=[],profiles=[];
 for(let d=0;d<=3;d++)for(let N=d+3;N<=d+7;N++)for(let K=3;K<=5;K++){
  let best=null;for(const t of subsets(N,d+3))for(let s=0;s<K;s++)for(let u=s+1;u<K;u++){let D=qdist(t,s,u,d);assert(D[0]>0n,"polynomial distinction");polynomialPairs++;best=best===null?D:min(best,D)}
  for(const t of subsets(N,d+2)){let D=qdist(t,0,1,d);assert(D[0]===0n,"one short");quotientChecks++}
  if(d===0){let L=N+K-2,den=(2*L-5)**2+4*(2*L-4)**2+(2*L-3)**2;assert(cmp(best,F(16,den))===0,"quadratic sharp");sharpProfiles.push({N,K,D_normalized:str(mul(best,F(4,BigInt(L)**4n)))})}
 }
 // Full mixed-fault profiles for normalized quadratic, exact finite subset minimization.
 for(let N of [8,12]){let K=3,L=N+K-2;for(let n=2;n<=N;n++){let best=null,witness=null;for(const t of subsets(N,n))for(let s=0;s<K;s++)for(let u=s+1;u<K;u++){let D=qdist(t,s,u,0);if(best===null||cmp(D,best)<0){best=D;witness={t,s,u}}}
  const D=mul(best,F(4,BigInt(L)**4n));profiles.push({N,r:N-n,quadratic:str(D),quadratic_radius:Math.sqrt(num(D))/2,binary:str(binaryD(N,N-n)),witness});
 }}
 // Exact receiver: for each candidate, enumerate surviving clean masks, then fit signed gain >=1 and arbitrary degree-d drift.
 function candidates(y,K,e,d,eps2){let S=y.map((v,i)=>v===null?-1:i).filter(i=>i>=0);let k=Math.max(0,S.length-e);return Array.from({length:K},(_,s)=>s).filter(s=>{if(k===0)return true;for(const mask of subsets(S.length,k)){let t=mask.map(i=>S[i]),a=project(t,d,pilot(t,s,d)),b=project(t,d,t.map(i=>y[i])),P=dot(a,a),R=dot(b,b),C=abs(dot(a,b));let score;if(!P[0])score=R;else{let g=max(one,div(C,P));score=sub(add(R,mul(P,mul(g,g))),mul(two,mul(g,C)))}if(cmp(score,eps2)<=0)return true}return false})}
 let decodes=0,midpoints=0;
 for(let d=0;d<=2;d++)for(let e=0;e<=1;e++)for(let f=0;f<=1;f++){
  let K=3,N=d+3+2*e+f,n=N-2*e-f,D=null,w=null;
  for(const t of subsets(N,n))for(let s=0;s<K;s++)for(let u=s+1;u<K;u++){let a=project(t,d,pilot(t,s,d)),b=project(t,d,pilot(t,u,d)),p=pair(a,b);if(D===null||cmp(p.D,D)<0){D=p.D;w={t,s,u,p}}}
  assert(D[0]>0n,"positive radius");
  // For positive correlated quadratic/polynomial residuals here use sign determined by actual inner product.
  let {t,s,u,p}=w;let aa=pilot(Array.from({length:N},(_,i)=>i),s,d),bb=pilot(Array.from({length:N},(_,i)=>i),u,d);
  let ar=project(t,d,t.map(i=>aa[i])),br=project(t,d,t.map(i=>bb[i]));let sign=dot(ar,br)[0]<0n?F(-1):one;
  aa=scale(aa,p.g1);bb=scale(bb,mul(sign,p.g2));
  // Fit difference on retained positions: recover nuisance polynomial by exact interpolation of projection complement on first d+1 ticks.
  let diff=t.map(i=>sub(aa[i],bb[i])),res=project(t,d,diff),fit=minus(diff,res);
  function lagrange(x){let v=zero;for(let j=0;j<=d;j++){let z=fit[j];for(let l=0;l<=d;l++)if(l!==j)z=mul(z,F(x-t[l],t[j]-t[l]));v=add(v,z)}return v}
  bb=bb.map((v,i)=>add(v,lagrange(i)));assert(cmp(dot(t.map(i=>sub(aa[i],bb[i])),t.map(i=>sub(aa[i],bb[i]))),D)===0,"fit midpoint");
  let dropped=Array.from({length:N},(_,i)=>i).filter(i=>!t.includes(i));let y=aa.map((v,i)=>t.includes(i)?div(add(v,bb[i]),two):dropped.indexOf(i)<f?null:dropped.indexOf(i)<f+e?bb[i]:v);
  let cs=candidates(y,K,e,d,div(D,four));assert(cs.includes(s)&&cs.includes(u),"midpoint list");midpoints++;
  // deterministic test for every phase and both signs, with arbitrary offset/drift and sparse faults, small nonzero dense noise.
  for(let phase=0;phase<K;phase++)for(let sg of [-1,1]){
    let x=Array.from({length:N},(_,i)=>add(mul(F(3*sg),pilot([i],phase,d)[0]),F(7+Array.from({length:d},(_,j)=>(j+2)*i**(j+1)).reduce((a,b)=>a+b,0))));
    // Use D/(large factor) as rational amplitude, guaranteed squared smaller than D/16.
    let eta=div(D,mul(F(100),add(one,D)));x[N-1]=add(x[N-1],eta);for(let i=0;i<f;i++)x[i]=null;for(let i=f;i<f+e;i++)x[i]=F(123456+i);
    let eps2=mul(eta,eta);assert(cmp(eps2,div(D,four))<0,"inside radius");let c=candidates(x,K,e,d,eps2);assert(c.length===1&&c[0]===phase,"unique decode");decodes++;
  }
 }
 // Clean affine aliases for linear ramp and exponential, and quadratic + degree-one drift.
 for(let d of [0,1,2]){let t=[0,1,2,3,4,5,6];let a=t.map(i=>F(BigInt(i)**BigInt(d+1))),b=t.map(i=>F(BigInt(i+1)**BigInt(d+1)));assert(pair(project(t,d,a),project(t,d,b)).D[0]===0n,"degree too low")}
 let t=[0,1,2,3];assert(pair(project(t,0,t.map(i=>F(2n**BigInt(i)))),project(t,0,t.map(i=>F(2n**BigInt(i+1))))).D[0]===0n,"exponential alias");
 return {contingencyProfiles,balancedProfiles,gainChecks,polynomialPairs,quotientChecks,sharpProfiles,profiles,decodes,midpoints,negativeControls:4,arithmetic:"exact BigInt rationals; displayed radii floating point"};
};
console.log(JSON.stringify(laboratory(),null,2));
