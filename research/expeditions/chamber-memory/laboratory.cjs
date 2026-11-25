"use strict";
function laboratory(){
  const gcd=(a,b)=>{a=a<0n?-a:a;b=b<0n?-b:b;while(b){[a,b]=[b,a%b]}return a||1n};
  const R=(n,d=1n)=>{n=BigInt(n);d=BigInt(d);if(!d)throw Error("zero denominator");if(d<0n){n=-n;d=-d}const g=gcd(n,d);return [n/g,d/g]};
  const add=(a,b)=>R(a[0]*b[1]+b[0]*a[1],a[1]*b[1]), neg=a=>R(-a[0],a[1]),sub=(a,b)=>add(a,neg(b)),mul=(a,b)=>R(a[0]*b[0],a[1]*b[1]),div=(a,b)=>R(a[0]*b[1],a[1]*b[0]),eq=(a,b)=>a[0]===b[0]&&a[1]===b[1],sum=a=>a.reduce(add,R(0)),prod=a=>a.reduce(mul,R(1)),str=a=>`${a[0]}/${a[1]}`,num=a=>Number(a[0])/Number(a[1]);
  const C=(a,b=R(0))=>[a,b],ca=(a,b)=>C(add(a[0],b[0]),add(a[1],b[1])),cm=(a,b)=>C(sub(mul(a[0],b[0]),mul(a[1],b[1])),add(mul(a[0],b[1]),mul(a[1],b[0]))),cd=(a,b)=>{const z=add(mul(b[0],b[0]),mul(b[1],b[1]));return C(div(add(mul(a[0],b[0]),mul(a[1],b[1])),z),div(sub(mul(a[1],b[0]),mul(a[0],b[1])),z))},ce=(a,b)=>eq(a[0],b[0])&&eq(a[1],b[1]),cs=a=>a.reduce(ca,C(R(0))),cp=a=>a.reduce(cm,C(R(1))),abs2=a=>add(mul(a[0],a[0]),mul(a[1],a[1]));
  const H=(p,s)=>cs(p.map(([l,w])=>cd(C(mul(l,w)),ca(C(l),s))));
  const F=(p,x)=>sum(p.map(([l,w])=>div(mul(w,l),add(x,l))));
  let checks=0;const assert=(b,m)=>{checks++;if(!b)throw Error(m)};
  const split=(poles,numerator)=>{
    let vals=poles.map((l,i)=>div(numerator(neg(l)),mul(l,prod(poles.filter((_,j)=>j!==i).map(q=>sub(q,l))))));
    let pos=vals.filter(x=>x[0]>0n),negative=vals.filter(x=>x[0]<0n).map(neg),mass=sum(pos);
    assert(eq(mass,sum(negative)),"equal DC mass");assert(pos.length===negative.length&&pos.length*2===poles.length,"alternation");
    return [1,-1].map(sign=>poles.flatMap((l,i)=>vals[i][0]*BigInt(sign)>0n?[[l,div(sign===1?vals[i]:neg(vals[i]),mass)]]:[]));
  };
  const rec={complex_cases:0,magnitude_cases:0,spectral_factor_forward_cases:0,finite_difference_cases:0,parallel_split_cases:0,balanced_cases:0,examples:{}};
  for(let k=1;k<=7;k++)for(let shift=0;shift<4;shift++){
    const poles=Array.from({length:2*k},(_,i)=>R(i+1+shift)),freqs=Array.from({length:k-1},(_,i)=>R(i+1,shift+1));
    const [a,b]=split(poles,x=>mul(x,prod(freqs.map(w=>add(mul(x,x),mul(w,w))))));
    for(const f of freqs)assert(ce(H(a,C(R(0),f)),H(b,C(R(0),f))),"complex collision");
    const extra=R(k+1,shift+1);assert(!ce(H(a,C(R(0),extra)),H(b,C(R(0),extra))),"complex extra");
    rec.complex_cases++;
    if(k===2&&shift===0)rec.examples.complex={a:a.map(p=>p.map(str)),b:b.map(p=>p.map(str)),shared:H(a,C(R(0),R(1))).map(str),extra_a:H(a,C(R(0),R(2))).map(str),extra_b:H(b,C(R(0),R(2))).map(str)};
    const mp=poles.map(x=>mul(x,x)),xf=Array.from({length:2*k-2},(_,i)=>R((i+1)**2,(shift+1)**2));
    const [u,v]=split(mp,x=>mul(x,prod(xf.map(z=>sub(x,z)))));
    for(const x of xf)assert(eq(F(u,x),F(v,x)),"magnitude collision");
    assert(!eq(F(u,R(0===k?0:(2*k)**2,(shift+1)**2)),F(v,R((2*k)**2,(shift+1)**2))),"magnitude extra");
    rec.magnitude_cases++;
    if(k===2&&shift===0)rec.examples.magnitude={a:u.map(p=>p.map(str)),b:v.map(p=>p.map(str)),shared:xf.map(x=>str(F(u,x))),extra_a:str(F(u,R(9))),extra_b:str(F(v,R(9)))};
  }
  for(let k=1;k<=8;k++)for(let shift=0;shift<5;shift++){
    const weights=Array.from({length:k},(_,i)=>R(i+1+shift)),mass=sum(weights);
    const p=weights.map((w,i)=>[R(i+1),div(w,mass)]);
    const q=p.map(([l,w])=>[mul(l,l),mul(mul(R(2),w),H(p,C(l))[0])]);
    assert(eq(sum(q.map(x=>x[1])),R(1)),"magnitude mass");
    for(let f=0;f<=9;f++){assert(eq(abs2(H(p,C(R(0),R(f,2)))),F(q,R(f*f,4))),"spectral identity");rec.spectral_factor_forward_cases++}
  }
  const choose=(n,j)=>{let x=1n;for(let i=1;i<=j;i++)x=x*BigInt(n-i+1)/BigInt(i);return x};
  for(let k=1;k<=6;k++)for(let den of [2,10,100,1000]){
    const n=2*k-1,h=R(1,den),tau=Array.from({length:n+1},(_,i)=>add(R(1),mul(R(i),h))),mass=R(2n**BigInt(n-1));
    const a=tau.flatMap((t,i)=>i%2===0?[[div(R(1),t),div(R(choose(n,i)),mass)]]:[]),b=tau.flatMap((t,i)=>i%2===1?[[div(R(1),t),div(R(choose(n,i)),mass)]]:[]);
    for(let f=0;f<=8;f++){
      const s=C(R(0),R(f,2)),factor=cm(s,C(h)),rhs=cd(cm(C(div(R(choose(n,n)*Array.from({length:n},(_,i)=>BigInt(i+1)).reduce((a,b)=>a*b,1n)),mass)),cp(Array(n).fill(factor))),cp(tau.map(t=>ca(C(R(1)),cm(s,C(t))))));
      const diff=ca(H(a,s),cm(C(R(-1)),H(b,s)));
      assert(ce(diff,rhs),"finite difference identity");rec.finite_difference_cases++;
    }
  }
  for(let a=1;a<=4;a++)for(let b=1;b<=4;b++)for(let c=1;c<=4;c++){
    const g=[R(a),R(b),R(c)],G=sum(g),s=C(R(0),R(3,2)),tau=R(2,3),cap=mul(G,tau);
    const fractions=[R(1,6),R(2,6),R(3,6)];
    for(let i=0;i<3;i++)for(let j=0;j<3;j++){
      const single=cd(C(mul(g[i],g[j])),ca(C(G),cm(s,C(cap))));
      const multi=cs(fractions.map(f=>cd(C(mul(mul(f,g[i]),mul(f,g[j]))),ca(C(mul(f,G)),cm(s,C(mul(f,cap)))))));
      assert(ce(single,multi),"parallel split");rec.parallel_split_cases++;
    }
    const u=[R(b),R(-a),R(0)];assert(eq(sum(g.map((v,i)=>mul(v,u[i]))),R(0)),"balanced drive");rec.balanced_cases++;
  }
  rec.assertions=checks;return rec;
}
console.log(JSON.stringify(laboratory(), null, 2));
