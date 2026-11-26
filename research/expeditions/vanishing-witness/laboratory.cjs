const laboratory = function laboratory() {
  "use strict";
  // Exact rational arithmetic, no dependencies.
  const gcd=(a,b)=>b===0n?(a<0n?-a:a):gcd(b,a%b);
  function Q(a,b=1) {a=BigInt(a);b=BigInt(b);if(!b)throw Error("zero denominator");if(b<0n){a=-a;b=-b;}const g=gcd(a,b);return [a/g,b/g];}
  const add=(a,b)=>Q(a[0]*b[1]+b[0]*a[1],a[1]*b[1]);
  const neg=a=>Q(-a[0],a[1]), sub=(a,b)=>add(a,neg(b));
  const mul=(a,b)=>Q(a[0]*b[0],a[1]*b[1]), div=(a,b)=>Q(a[0]*b[1],a[1]*b[0]);
  const str=a=>a[0]+(a[1]===1n?"":"/"+a[1]), zero=Q(0),one=Q(1);
  const sum=a=>a.reduce(add,zero), pos=a=>a[0]>0n?a:zero, eq=(a,b)=>sub(a,b)[0]===0n;
  const p2=j=>j>=0?Q(2n**BigInt(j)):Q(1,2n**BigInt(-j));
  let assertions=0, literalKnots=0, roundingKnots=0, roundedProfiles=0;
  function check(ok,msg){assertions++;if(!ok)throw Error(msg);}
  function table(start,numerators,den){return new Map(numerators.map((n,i)=>[start+i,Q(n,den)]));}
  const at=(c,j)=>c.get(j)||zero;
  const D=(c,j)=>sub(add(at(c,j-1),at(c,j+1)),mul(Q(3,2),at(c,j)));
  const rows=c=>[...c].filter(([j,w])=>w[0]>0n).map(([j,w])=>[w,mul(w,p2(-j))]);
  function valid(R){check(R.every(r=>r.every(x=>x[0]>0n)),"positive rows");for(let k=0;k<2;k++)check(eq(sum(R.map(r=>r[k])),one),"normalized rows");}
  function hinge(R,z){return sum(R.map(([p,m])=>pos(sub(p,mul(z,m)))));}
  const E=[[Q(2,21),Q(1,3)],[Q(5,7),Q(5,8)],[Q(4,21),Q(1,24)]];
  const F=[[Q(3,7),Q(3,4)],[Q(4,7),Q(1,4)]];
  const product=(A,B)=>A.flatMap(a=>B.map(b=>a.map((v,i)=>mul(v,b[i]))));
  const erase=(R,e)=>[...R.map(r=>r.map(v=>mul(v,sub(one,e)))).filter(r=>r[0][0]>0n),...(e[0]>0n?[[e,e]]:[])];
  function direct(R){valid(R);const A=product(E,R),B=product(F,R);
    const zs=[...new Map([...A,...B].map(([p,m])=>{const z=div(p,m);return [str(z),z];})).values()];
    const ds=zs.map(z=>sub(hinge(A,z),hinge(B,z)));literalKnots+=zs.length;return ds.every(x=>x[0]>=0n);
  }
  function verifyC(c){valid(rows(c));const ks=[...c.keys()];for(let j=Math.min(...ks)-1;j<=Math.max(...ks)+1;j++)check(D(c,j)[0]>=0n,"primal");check(direct(rows(c)),"literal primal");}
  function remove(c,e){const v=new Map(c);v.set(0,sub(at(c,0),e));return v;}
  function raw(c,e){return rows(new Map([...remove(c,e)].map(([j,w])=>[j,div(w,sub(one,e))])));}
  const C=table(-1,[9,14,12,4],39), e=Q(14,39);
  verifyC(C);
  const g=table(0,[22,8],39),lambda=Q(2,13),mu=Q(8,39);
  check(eq(add(lambda,mu),e),"fixed dual objective");
  for(let j=-1;j<=2;j++){
    const slack=sub(add(lambda,mul(mu,p2(-j))),D(g,j));
    check(sub(slack,j===0?one:zero)[0]>=0n,"fixed dual pointwise");
  }
  check(lambda[0]>0n&&mu[0]>0n,"fixed dual tails");
  const R=raw(C,e);valid(R);check(!direct(R),"fixed raw is not catalyst");
  let singletonChecks=0;
  for(let k=0;k<39;k++){const t=Q(k,39);check(direct(erase(R,t))===(k===14),"singleton scan");singletonChecks++;}
  check(eq(sub(hinge(product(E,R),Q(16,7)),hinge(product(F,R),Q(16,7))),Q(-4,75)),"explicit negative hinge");
  const B=table(-3,[3144,4716,3930,12152,14298,20268,16104,3888],78500),rho=Q(10973,78500);
  verifyC(B);const S=raw(B,rho);valid(S);check(direct(S),"robust raw qualifies");
  const g0=new Map([[-3,Q(3639,39250)],[-2,Q(449,1570)],[0,Q(22509,39250)],[2,Q(109,314)],[3,Q(5449,39250)]]);
  const g1=new Map([[-1,Q(3761,7850)],[1,Q(4089,7850)]]);
  const G=new Map([...g0,...g1]),l=Q(10893,78500),m=Q(4,3925);
  check([...G.values()].every(x=>x[0]>=0n),"robust dual positivity");
  check(eq(add(at(g1,-1),at(g1,1)),one),"unit erasure coefficient");
  check(eq(add(l,m),rho),"robust dual objective");
  for(let j=-4;j<=4;j++)check(sub(add(l,mul(m,p2(-j))),D(G,j))[0]>=0n,"robust dual pointwise");
  check(l[0]>0n&&m[0]>0n,"robust dual tails");
  let robustChecks=0;
  for(let k=0;k<=100;k++){const t=mul(rho,Q(k,100));check(direct(erase(S,t)),"robust interval");robustChecks++;}
  check(!direct(erase(S,add(rho,Q(1,78500)))),"just above robust limit");
  // Off-grid rounding: match both state masses, then test exact hinge receipts.
  function round(R){const c=new Map();for(const [w,v] of R){const L=div(w,v);let j=0;while(sub(L,p2(j))[0]<0n)j--;while(sub(L,p2(j+1))[0]>=0n)j++;
    const alpha=div(sub(div(one,L),p2(-j-1)),sub(p2(-j),p2(-j-1)));
    for(const [k,x] of [[j,mul(w,alpha)],[j+1,mul(w,sub(one,alpha))]])c.set(k,add(at(c,k),x));
  }return c;}
  // Nontrivial valid two-ratio side channels, plus independent tagged erasure.
  for(let i=1;i<=12;i++)for(let j=1;j<=12;j++){
    const L=Q(i,13),U=Q(13+j,13);
    const w=div(sub(one,div(one,U)),sub(div(one,L),div(one,U)));
    const R0=[[w,div(w,L)],[sub(one,w),div(sub(one,w),U)]];
    const R1=erase(R0,Q(i+j,30));valid(R1);
    const c=round(R1),R2=rows(c);valid(R2);
    check(sub(at(c,0),Q(i+j,30))[0]>=0n,"retained neutral");
    for(let k=-8;k<=8;k++){
      const z=mul(Q(4,7),p2(k));
      const h=(A)=>sub(hinge(product(E,A),z),hinge(product(F,A),z));
      check(eq(h(R1),h(R2)),"rounding hinge equality");roundingKnots++;
      check(eq(h(R2),mul(Q(2,21),D(c,k-1))),"grid convolution");
    }
    roundedProfiles++;
  }
  return {status:"PASS",arithmetic:"exact BigInt rational",assertions,literalKnots,roundingKnots,roundedProfiles,singletonChecks,robustChecks,knownRate:str(e),uniformRate:str(rho),fixedSide:R.map(row=>row.map(str)),robustSide:S.map(row=>row.map(str))};
};
console.log(JSON.stringify(laboratory(), null, 2));
