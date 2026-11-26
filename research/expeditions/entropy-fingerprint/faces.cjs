"use strict";
function faces(){
 const assert=(x,m)=>{if(!x)throw Error(m)};
 const C=(n,k)=>{let v=1;for(let i=1;i<=k;i++)v=v*(n-i+1)/i;return Math.round(v)};
 const signs=(n,mask)=>Array.from({length:n},(_,i)=>(mask>>i)&1?1:-1);
 const laws=n=>{let A=[],B=[];for(let mask=0;mask<2**n;mask++){let s=signs(n,mask);(s.reduce((a,b)=>a*b,1)===1?A:B).push(s)}return [A,B]};
 const mi=(law,p,e)=>law.reduce((I,s)=>{let a=s.map(v=>1+e*v),q=a.reduce((v,x,i)=>v+p[i]*x,0);return I+a.reduce((v,x,i)=>v+p[i]*x*Math.log(x/q),0)/law.length},0);
 let projection_checks=0, row_checks=0, shortlist_checks=0, information_checks=0, moment_checks=0;
 const examples=[];
 for(let n=3;n<=9;n++){
  let [A,B]=laws(n);
  for(let j=0;j<n;j++){for(const law of [A,B]){assert(law.reduce((z,s)=>z+s[j],0)===0,"row");row_checks++}}
  for(let T=1;T<2**n-1;T++){
   const marginal=law=>{let m=new Map;for(const s of law){let k=s.filter((_,i)=>(T>>i)&1).join(",");m.set(k,(m.get(k)||0)+1)}return m};
   const a=marginal(A),b=marginal(B);assert(a.size===b.size,"projection size");
   for(const [k,v] of a){assert(b.get(k)===v,"projection");projection_checks++}
  }
  // Integer numerator: epsilon=e/8, output column weights (8+e*s).
  for(let e=1;e<8;e++)for(let l=1;l<=n;l++){
   const V=law=>law.reduce((v,s)=>v+s.map(x=>8+e*x).sort((a,b)=>b-a).slice(0,l).reduce((a,b)=>a+b,0),0);
   assert(V(A)-V(B)===(l===n?0:2*e*(-1)**(n+l)*C(n-2,l-1)),"shortlist");shortlist_checks++;
  }
  // Integer weighted sum moments, deterministic strictly positive priors.
  for(let k=0;k<4;k++){
   let p=Array.from({length:n},(_,i)=>1+(i+1)*(k+1)%7),z=p.reduce((a,b)=>a+b,0);
   const M=(law,r)=>law.reduce((v,s)=>v+BigInt(s.reduce((a,b,i)=>a+b*p[i],0))**BigInt(r),0n);
   for(let r=0;r<n;r++){assert(M(A,r)===M(B,r),"lower moments");moment_checks++}
   let expected=2n*BigInt(A.length)*Array.from({length:n},(_,i)=>BigInt(i+1)*BigInt(p[i])).reduce((a,b)=>a*b,1n);
   assert(M(A,n)-M(B,n)===expected,"leading moment");moment_checks++;
   for(let e of [.3,.5,.8,.95]){let gap=mi(A,p.map(x=>x/z),e)-mi(B,p.map(x=>x/z),e);assert(gap*(-1)**(n+1)>0,"MI sign");information_checks++}
  }
  let p=Array(n).fill(1/n), e=.5;
  examples.push({n,plus_nats:mi(A,p,e),minus_nats:mi(B,p,e),gap:mi(A,p,e)-mi(B,p,e)});
 }
 return {status:"PASS",projection_checks,row_checks,shortlist_checks,information_checks,moment_checks,examples,limits:"Exact integer projections, moments and shortlist numerators; floating point MI sign checks on selected priors only."};
}
if(typeof module!=="undefined"&&require.main===module)console.log(JSON.stringify(faces(),null,2));
