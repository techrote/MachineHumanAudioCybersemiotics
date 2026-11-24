import * as lib from "./fade.mjs";
function check(x,msg){if(!x)throw Error(msg);}
const stringify=x=>JSON.stringify(x,(_,v)=>typeof v==="bigint"?v.toString():v,2);
const rows=[];
let joint=0,primitive=0,nonnegative=0,maxNumericalResidual=0;
for(let q=2;q<=128;q++){
  const p=lib.phi(q);let expected=0;
  const gcd=(a,b)=>b?gcd(b,a%b):a;
  for(let k=1;k<q;k++)if(gcd(k,q)===1)expected++;
  check(p.length-1===expected,"totient");
  for(let k=1;k<q;k++)if(gcd(k,q)===1){
    // Evaluate primitive root against signed polynomial separately.
    let x=0,y=0;for(let j=0;j<p.length;j++){
      x+=Number(p[j])*Math.cos(2*Math.PI*j*k/q);
      y+=Number(p[j])*Math.sin(2*Math.PI*j*k/q);
    }
    check(Math.hypot(x,y)<1e-10,"primitive root");primitive++;
  }
}
for(let q=2;q<=24;q++)for(let z=q;z<=24;z++){
  const a=lib.plan([q,z]);
  check(lib.exactNotch(a.witness,[q,z]),"exact joint notch");
  check(a.span>=a.degreeLower&&a.mass%a.massDivisor===0n,"bounds");
  if(a.product.every(x=>x>=0n)){check(a.spanOptimal&&a.massOptimal,"positive product optimal");nonnegative++;}
  for(const n of a.orders)maxNumericalResidual=Math.max(maxNumericalResidual,lib.complexGain(a.witness,n));
  joint++;
}
let candidates=0,short=[];
for(let m=1;m<=64;m++){
  const a=lib.bestShort5(m);candidates+=a.visited;
  check(!lib.exactNotch(a.witness,[5]),"short rational impossible");
  const [A,B]=a.squaredTwice;
  check((A*A-5n*B*B)%4n===0n&&A*A-5n*B*B>=4n,"integer norm");
  short.push({...a,gain:lib.complexGain(a.witness,5)});
}
const phi=(1+Math.sqrt(5))/2;
let fibonacci=[];
for(let k=1;k<=15;k++){
  const w=lib.fibShort5(k),m=lib.mass(w),[A,B]=lib.squared5(w);
  check(A*A-5n*B*B===4n,"unit norm");
  const g=lib.complexGain(w,5),formula=phi**(-k-1)/Number(m);
  check(Math.abs(g-formula)<1e-14,"Fibonacci formula");
  fibonacci.push({k,m,w,g,formula,norm:1});
}
let frontier=[];
for(let d=6;d<=15;d++)frontier.push({span:d,...lib.search([6,10],d,4,100000)});
check(frontier[0].status==="no-witness-within-mass-cap"&&frontier[1].status==="no-witness-within-mass-cap","short composite");
check(frontier.slice(2,9).every(x=>x.mass===4)&&frontier[9].mass===2,"frontier");
const budget=lib.search([6,10,15],14,12,100);
check(budget.status==="budget-exhausted","budget refusal");
check(!lib.exactNotch([1n,1n,1n,1n],[5]),"four taps nonzero");
check(lib.exactNotch([1n,1n,1n,1n,1n],[5]),"five taps zero");
let refusals=0;
for(const f of [()=>lib.plan([]),()=>lib.plan([1]),()=>lib.exactNotch([0n],[5]),()=>lib.bestShort5(0),()=>lib.search([5],3,10,0)]){
  try{f();}catch{refusals++;}
}
check(refusals===5,"validation");
console.log(stringify({classification:"synthetic",primitive,joint,nonnegative,maxNumericalResidual,candidates,short,fibonacci,frontier,budget,refusals}));
