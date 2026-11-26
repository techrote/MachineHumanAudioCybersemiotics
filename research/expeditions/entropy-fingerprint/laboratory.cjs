"use strict";
function laboratory() {
  const assert=(x,m)=>{if(!x)throw Error(m)};
  const C=(n,k)=>{let v=1n;for(let j=1;j<=k;j++)v=v*BigInt(n-j+1)/BigInt(j);return v};
  const mul=(p,q)=>{let z=Array(p.length+q.length-1).fill(0n);p.forEach((a,i)=>q.forEach((b,j)=>z[i+j]+=a*b));return z};
  const trim=p=>{while(p.length&&p[p.length-1]===0n)p.pop();return p};
  const dot=(p,x)=>p.reduceRight((s,v)=>s*x+v,0n);
  const moment=(law,k)=>law.reduce((s,[x,w])=>s+w*BigInt(x)**BigInt(k),0n);
  const g=x=>x===-1?0:(1+x)*Math.log1p(x);
  const info=(law,d,u)=>{let z=Number(moment(law,0));return law.reduce((s,[x,w])=>{let t=x/d;return s+Number(w)/z*((1+u)/2*g(t)+(1-u)/2*g(-t)-g(u*t))},0)};
  const curvature=(law,d,u)=>law.reduce((s,[x,w])=>s+Number(w)/Number(moment(law,0))*(x/d)**2/(1+u*x/d),0);
  const call=(law,d,k)=>law.reduce((s,[x,w])=>s+Number(w)/Number(moment(law,0))*Math.max(0,x/d-k),0);
  let jet_checks=0, recurrence_checks=0, reflection_checks=0, polynomial_profiles=0, rational_evaluation_checks=0;
  const parity=[];
  for(let m=2;m<=16;m++){
    let n=2*m-1,d=n+1,A=[],B=[];
    for(let j=0;j<=n;j++)(j%2?B:A).push([2*j-n,C(n,j)]);
    assert(moment(A,0)===moment(B,0)&&moment(A,1)===0n&&moment(B,1)===0n,"normalization");
    for(let k=0;k<n;k++){assert(moment(A,k)===moment(B,k),"jet");jet_checks++}
    assert(moment(A,n)!==moment(B,n),"first mismatch");
    for(const law of [A,B]){
      let p=law.reduce((p,[x])=>mul(p,[-BigInt(x),1n]),[1n]);
      for(let k=0;k<=m;k++){assert(p.reduce((s,v,j)=>s+v*moment(law,k+j),0n)===0n,"annihilator");recurrence_checks++}
    }
    for(let j=0;j<=20;j++){let u=(j-10)/11;assert(Math.abs(info(A,d,u)-info(B,d,-u))<1e-14,"reflection");reflection_checks++}
    parity.push({m,matched_moment_degree:n-1,first_unmatched:n,center_information_nats:info(A,d,0),off_center_difference:info(A,d,.5)-info(B,d,.5)});
  }
  let seed=932847;const rand=n=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed%n};
  const randomLaw=()=>{let a=new Map;for(let j=0;j<1+rand(8);j++){let x=1+rand(7),y=1+rand(7),w=BigInt(1+rand(9));a.set(-x,(a.get(-x)||0n)+BigInt(y)*w);a.set(y,(a.get(y)||0n)+BigInt(x)*w)}return [...a]};
  // Common grid t=x/8. Exact signed measure after cross-multiplying denominators.
  for(let trial=0;trial<600;trial++){
    let A=randomLaw(),B=randomLaw(),zA=moment(A,0),zB=moment(B,0),diff=new Map();
    for(const [x,w] of A)diff.set(x,(diff.get(x)||0n)+w*zB);
    for(const [x,w] of B)diff.set(x,(diff.get(x)||0n)-w*zA);
    let D=[...diff].filter(([x,w])=>w!==0n);
    if(!D.length)continue;
    assert(moment(D,0)===0n&&moment(D,1)===0n,"signed normalization");
    let r=D.length;
    let p=Array(r).fill(0n);
    for(let i=0;i<r;i++){let [x,w]=D[i],q=[1n];for(let j=0;j<r;j++)if(j!==i)q=mul(q,[8n,BigInt(D[j][0])]);q.forEach((v,k)=>p[k]+=v*w*BigInt(x*x))}
    trim(p);assert(p.length>0&&p.length<=r-2,"curvature degree");polynomial_profiles++;
    for(let u=-3;u<=3;u++){
      // p(u/4) * 4^(r-1), directly from product of denominators.
      let direct=0n;
      for(let i=0;i<r;i++){let [x,w]=D[i],v=w*BigInt(x*x);for(let j=0;j<r;j++)if(j!==i)v*=32n+BigInt(u*D[j][0]);direct+=v}
      let evalP=p.reduce((s,v,k)=>s+v*BigInt(u)**BigInt(k)*4n**BigInt(r-1-k),0n);
      assert(direct===evalP,"rational polynomial evaluation");rational_evaluation_checks++;
    }
  }
  const A=[[-3,1n],[1,3n]], B=[[-1,3n],[3,1n]], conditioning=[];
  for(let d of [4,8,16,32,64,128,256,512]){
    let h=1/d, gap=0;for(let j=0;j<=1000;j++){let u=(j-500)/500;gap=Math.max(gap,Math.abs(info(A,d,u)-info(B,d,u)))}
    let actionGap=call(B,d,h)-call(A,d,h);
    assert(Math.abs(actionGap-h/2)<1e-15,"call witness");
    assert(gap>0&&gap<=4*(3*h)**3/(2*3*(1-3*h)),"uniform bound");
    conditioning.push({h,grid_max_information_gap_nats:gap,decision_value_gap:actionGap,ratio:actionGap/gap});
  }
  assert(Math.abs(curvature(A,4,0)-curvature(B,4,0))<1e-15,"center curvature");
  return {status:"PASS",jet_checks,recurrence_checks,reflection_checks,polynomial_profiles,rational_evaluation_checks,parity,conditioning,limitations:"Exact integer assertions except information, curvature and decision numerical illustrations; sampled prior grid is not a continuous optimization. Same-agent synthetic checks."};
}
if(typeof module!=="undefined"&&require.main===module)console.log(JSON.stringify(laboratory(),null,2));
