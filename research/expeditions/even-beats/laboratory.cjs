"use strict";
function laboratory(){
  const assert=(x,msg)=>{if(!x)throw Error(msg)};
  const abs=x=>x<0n?-x:x, max=x=>x>0n?x:0n;
  const choose=(n,k)=>{let x=1n;for(let i=1;i<=k;i++)x=x*BigInt(n-i+1)/BigInt(i);return x};
  const table=(plus,minus)=>{const D=plus.reduce((a,b)=>a+b,0n);assert(D===minus.reduce((a,b)=>a+b,0n),"row sum");return {D,cols:plus.map((x,i)=>[x,minus[i]])}};
  const prod=(A,B)=>({D:A.D*B.D,cols:A.cols.flatMap(([p,q])=>B.cols.map(([u,v])=>[p*u,q*v]))});
  const mix=(A,B)=>({D:2n*A.D*B.D,cols:[...A.cols.map(([p,q])=>[p*B.D,q*B.D]),...B.cols.map(([p,q])=>[p*A.D,q*A.D])]});
  // Enumerate multinomial count profiles; their conditional probabilities are exact.
  const repeat=(A,n)=>{const cols=[];function rec(j,left,c,p,q){if(j===A.cols.length-1){const [u,v]=A.cols[j];cols.push([c*p*u**BigInt(left),c*q*v**BigInt(left)]);return}const [u,v]=A.cols[j];for(let k=0;k<=left;k++)rec(j+1,left-k,c*choose(left,k),p*u**BigInt(k),q*v**BigInt(k))}rec(0,n,1n,1n,1n);return {D:A.D**BigInt(n),cols}};
  // Bayes accuracy with prior 1/(1+z) for z=u/v, compare max(p*v,q*u).
  const numerator=(A,u,v)=>A.cols.reduce((s,[p,q])=>s+(p*v>q*u?p*v:q*u),0n);
  const knots=(A,B)=>[[0n,1n],[1n,1n],...A.cols,...B.cols].filter(([u,v])=>v>0n);
  let checks=0;
  const dominates=(A,B)=>{let ok=true;for(const [u,v] of knots(A,B)){checks++;if(numerator(A,u,v)*B.D<numerator(B,u,v)*A.D)ok=false}return ok};
  const gcd=(a,b)=>b?gcd(b,a%b):abs(a);
  const frac=(a,b)=>{let g=gcd(a,b);return `${a/g}/${b/g}`};
  const acc=(A,u=1n,v=1n)=>frac(numerator(A,u,v),A.D*(u+v));
  const overlap=A=>A.cols.reduce((s,[p,q])=>s+(p<q?p:q),0n);
  const A=table([133n,260n,7n],[7n,260n,133n]),B=table([3n,1n],[1n,3n]);
  const horizons=[];
  for(let n=1;n<=16;n++){let X=repeat(A,n),Y=repeat(B,n);let ab=dominates(X,Y),ba=dominates(Y,X);
    assert(ab===(n!==1&&n!==3)&&!ba,"horizon");
    horizons.push({n,A:acc(X),B:acc(Y),A_dominates:ab,B_dominates:ba})}
  let grid=0;
  for(let a=1;a<10;a++)for(let b=1;b<10;b++)for(let r=1;r<10;r++){
    const i=BigInt(a),j=BigInt(r),k=BigInt(b);
    let X=table([j*(10n+i),20n*(10n-j),j*(10n-i)],[j*(10n-i),20n*(10n-j),j*(10n+i)]);
    let Y=table([10n+k,10n-k],[10n-k,10n+k]);
    let expected=i>=k && i*j*(20n-j)>=100n*k && j*j*i*(100n-i*i)>=100n*(200n*k-i*(100n+k*k));
    assert(dominates(repeat(X,2),repeat(Y,2))===expected,"two-read formula");grid++;
  }
  const C=mix(A,B),S=table([19n,1n],[1n,19n]);
  assert(dominates(prod(A,C),prod(B,C)),"catalyst");
  assert(dominates(S,C),"stronger context");
  assert(!dominates(prod(A,S),prod(B,S)),"stronger context fails");
  const strong=[acc(prod(A,S),19n,1n),acc(prod(B,S),19n,1n)];
  assert(numerator(prod(A,S),19n,1n)*prod(B,S).D<numerator(prod(B,S),19n,1n)*prod(A,S).D,"skew prior counterexample");
  let oddHoles=0,evenCertificates=0;
  for(let h=1;h<=15;h++){
    const M=2n**BigInt(2*h+2)+1n,m2=M*M,m4=m2*m2;
    // a=1-M^-4, b=1-2M^-2, r=1-M^-1.
    const plus=(M-1n)*(2n*m4-1n),minus=M-1n,zero=2n*m4;
    let X=table([plus,zero,minus],[minus,zero,plus]);
    let Y=table([m2-1n,1n],[1n,m2-1n]);
    assert(dominates(repeat(X,2),repeat(Y,2)),"arbitrary family 2");evenCertificates++;
    for(let n=1;n<=2*h+1;n+=2){
      const U=repeat(X,n),V=repeat(Y,n);
      assert(overlap(U)*V.D>overlap(V)*U.D,"odd gap");oddHoles++;
    }
  }
  return {method:"BigInt exact conditional likelihoods; count profiles and rational prior knots",horizons,two_read_grid_profiles:grid,prior_knot_checks:checks,arbitrary_family_odd_failures:oddHoles,arbitrary_family_two_read_certificates:evenCertificates,side_receipts:{tagged_mixture_catalyzes:true,stronger_binary_dominates_mixture:true,stronger_binary_catalyzes:false,skew_prior:"1/20",A_accuracy:strong[0],B_accuracy:strong[1]},assertion_failures:0};
}
console.log(JSON.stringify(laboratory(),null,2));
