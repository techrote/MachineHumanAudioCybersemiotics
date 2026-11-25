'use strict';

function laboratory(){
  let checks=0,cases=0;const gaps=[0,0,0,0],hist={};
  const ok=(x,msg)=>{checks++;if(!x)throw Error(msg)};
  const pop=x=>{let n=0;while(x){x&=x-1;n++}return n};
  const range=n=>Array.from({length:1<<n},(_,i)=>i);
  const cert=(f,w,k,n)=>range(n).every(v=>((v^w)&k)!==0||f(v)===f(w));
  const minDisclosure=(f,w,ks,n)=>{
    let best=n+1;
    for(const d of range(n))if(ks.every(k=>cert(f,w,k|d,n)))best=Math.min(best,pop(d));
    return best;
  };
  const viaHitting=(f,w,ks,n)=>{
    const needs=[];
    for(const k of ks)for(const v of range(n))if(f(v)!==f(w)&&((v^w)&k)===0)needs.push(v^w);
    let best=n+1;
    for(const d of range(n))if(needs.every(e=>e&d))best=Math.min(best,pop(d));
    return best;
  };
  for(let table=0;table<256;table++){
    const f=v=>(table>>v)&1;
    for(const w of range(3))for(const a of range(3))for(const b of range(3)){
      const d=minDisclosure(f,w,[a,b],3),p=minDisclosure(f,w,[a&b],3);
      ok(d===viaHitting(f,w,[a,b],3),"distributed hitting equivalence");
      ok(p===viaHitting(f,w,[a&b],3),"public hitting equivalence");
      ok(p>=d,"public dominates");
      ok(p-d<=Math.min(pop(a&~b),pop(b&~a)),"gap upper bound");
      ok(p-d<=1,"three-bit maximum");
      ok(d===0===(cert(f,w,a,3)&&cert(f,w,b,3)),"zero cost iff both certify");
      cases++;gaps[p-d]++;hist[`${d},${p}`]=(hist[`${d},${p}`]||0)+1;
    }
  }
  const witnesses=[];
  for(let k=1;k<=5;k++){
    const n=2*k,a=(1<<k)-1,b=a<<k,w=a|b;
    const f=v=>Number((v&a)===a||(v&b)===b);
    const d=minDisclosure(f,w,[a,b],n),p=minDisclosure(f,w,[a&b],n);
    ok(d===0&&p===k,"sharp block OR witness");
    witnesses.push({n,d,p});
  }
  const or=v=>Number(v!==0),and=v=>Number(v===3);
  ok(minDisclosure(or,3,[1,2],2)===0,"OR separate proofs");
  ok(minDisclosure(or,3,[0],2)===1,"OR public proof cost");
  ok(minDisclosure(and,3,[1,2],2)===2,"AND shared packet must contain both");
  ok(minDisclosure(and,3,[0],2)===2,"AND public proof cost");
  ok(minDisclosure(or,3,[3,3],2)===0,"already shared");
  return {cases,checks,gaps,hist,witnesses};
}

console.log(JSON.stringify(laboratory(), null, 2));
