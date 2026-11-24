"use strict";
// Exact synthetic state model; no audio hardware or dependencies.
function laboratory(){
  // x,y numerators at tick t, common denominator 8^t; coefficients /8.
  let assertions=0, systems=0, pairs=0, trajectories=0;
  function check(ok,msg){assertions++;if(!ok)throw Error(msg);}
  function trace(m,u,v){
    let x=0n,y=0n,den=1n;
    let out=[{x,y,den}];
    let [a,b,c,d]=m.map(BigInt);
    for(let t=0;t<u.length;t++){
      den*=8n;
      [x,y]=[a*x+b*y+BigInt(u[t])*den,c*x+d*y+BigInt(v[t])*den];
      out.push({x,y,den});
    }
    return out;
  }
  const zero=Array(12).fill(0), imp=zero.map((_,i)=>i===0?1:0);
  const mixed=[1,0,-1,1,1,0,0,-1,0,1,-1,0];
  for(let a=0;a<=3;a++)for(let d=0;d<=3;d++){
    const groups=new Map();
    for(let b=1;b<=5;b++)for(let c=1;c<=5;c++){
      if(a+b>7||c+d>7)continue;
      systems++;
      const m=[a,b,c,d],p=b*c;
      if(!groups.has(p))groups.set(p,[]);
      groups.get(p).push(m);
      // independent scalar recurrence for a nonzero two-port input.
      const s=trace(m,mixed,imp);
      for(let t=0;t<mixed.length-1;t++){
        const lhs=s[t+2].x;
        const rhs=BigInt(a+d)*s[t+1].x+BigInt(b*c-a*d)*s[t].x+
          BigInt(mixed[t+1])*s[t+2].den-BigInt(d*mixed[t])*s[t+1].den+
          BigInt(b*imp[t])*s[t+1].den;
        check(lhs===rhs,"scalar elimination");
      }
      trajectories++;
    }
    for(const g of groups.values())for(let i=0;i<g.length;i++)for(let j=i+1;j<g.length;j++){
      const A=g[i],B=g[j];pairs++;
      for(const u of [imp,mixed]){
        const l=trace(A,u,zero),rr=trace(B,u,zero);trajectories+=2;
        for(let t=0;t<l.length;t++)check(l[t].x===rr[t].x,"keyboard equivalence");
      }
      const l=trace(A,zero,imp),rr=trace(B,zero,imp);trajectories+=2;
      check(l[2].x===8n*BigInt(A[1]),"A calibrated port");
      check(rr[2].x===8n*BigInt(B[1]),"B calibrated port");
      check(l[2].x!==rr[2].x,"room response separates pair");
      for(let t=0;t<l.length;t++)check(l[t].x*BigInt(B[1])===rr[t].x*BigInt(A[1]),"environment response scales");
    }
  }
  const A=[2,1,4,2],B=[2,4,1,2];
  // Exhaustively vary five keyboard input ticks over {-1,0,1}.
  for(let k=0;k<243;k++){
    let q=k,u=[];for(let i=0;i<5;i++){u.push(q%3-1);q=Math.floor(q/3);}
    const l=trace(A,u,Array(5).fill(0)),rr=trace(B,u,Array(5).fill(0));trajectories+=2;
    for(let t=0;t<l.length;t++)check(l[t].x===rr[t].x,"signed keyboard sequence");
  }
  const ka=trace(A,imp,zero),kb=trace(B,imp,zero),ea=trace(A,zero,imp),eb=trace(B,zero,imp);
  const first=(s)=>s.slice(0,7).map(o=>Number(o.x)/Number(o.den));
  check(ka[2].y===4n*8n && kb[2].y===8n,"environment state differs after keyboard");
  check(ea[2].x*4n===eb[2].x,"fourfold environmental coupling");
  return {assertions,systems,pairs,trajectories,exhaustiveKeyboardInputs:243,keyboard:first(ka),roomA:first(ea),roomB:first(eb)};
}
console.log(JSON.stringify(laboratory(),null,2));
