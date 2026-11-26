'use strict';
function laboratory(){
  const ok=(x,msg)=>{if(!x)throw Error(msg)};
  let schedules=0,rows=0,reverseChecks=0,dense=0,dpChecks=0;
  function span(s){let x=0,lo=0,hi=0;for(const d of s){x+=d;lo=Math.min(lo,x);hi=Math.max(hi,x)}return hi-lo}
  function directions(k,mask){return Array.from({length:k},(_,i)=>mask>>i&1?-1:1)}
  function run(q,h,s,x){
    const n=q**h, tail=q**(h-1);let a=Array(n).fill(0);a[x]=1;
    for(const d of s){let b=Array(n).fill(0);for(let i=0;i<n;i++)if(a[i])for(let z=0;z<q;z++)b[d===1?(i%tail)*q+z:Math.floor(i/q)+z*tail]+=a[i];a=b}
    return a
  }
  for(const [q,hs] of [[2,[2,3,4,5]],[3,[2,3]]])for(const h of hs){
    const n=q**h;
    for(let k=0;k<=8;k++)for(let mask=0;mask<2**k;mask++){
      let s=directions(k,mask),m=Math.max(0,h-span(s)),support=q**(h-m),den=q**k,distinct=new Set();
      for(let x=0;x<n;x++){
        let a=run(q,h,s,x), nonzero=a.filter(Boolean);
        ok(nonzero.length===support&&nonzero.every(z=>z*support===den),"row support");
        distinct.add(a.join(","));rows++;
      }
      ok(distinct.size===q**m,"distinct rows");
      let signs=Array.from({length:h},(_,i)=>i);
      for(const d of s)signs=d===1?[...signs.slice(1),-1]:[-1,...signs.slice(0,-1)];
      ok(signs.filter(z=>z>=0).length===m,"literal lineage");
      schedules++;
    }
  }
  for(let h=2;h<=8;h++)for(let e=0;e<=3;e++){
    let k=h+2*e;
    for(let mask=0;mask<2**k;mask++){
      let s=directions(k,mask);if(s.filter(z=>z<0).length<=e){ok(span(s)>=h,"reversal upper");reverseChecks++}
    }
    let witness=[...Array.from({length:e},()=>[1,-1]).flat(),...Array(h-1).fill(1)];
    ok(witness.length===k-1&&span(witness)===h-1,"reversal lower");
  }
  function mul(a,b){return a.map(row=>b[0].map((_,j)=>row.reduce((s,x,i)=>s+x*b[i][j],0n)))}
  for(let n=2;n<=12;n++)for(let h=1;h<n;h++){
    let B=Array.from({length:n},()=>Array(n).fill(0n));
    for(let i=0;i<h-1;i++)for(let j=0;j<n;j++){
      let v=BigInt((j===i+1?n:0)-1);
      B[i][j]+=v;B[n-1][j]-=v;
    }
    let max=B.flat().reduce((a,b)=>{let v=b<0n?-b:b;return v>a?v:a},0n),base=max+1n,D=base*BigInt(n);
    let P=B.map(row=>row.map(x=>x+base));
    ok(P.every(row=>row.every(x=>x>0n)&&row.reduce((a,b)=>a+b,0n)===D),"positive row stochastic");
    ok(P[0].every((_,j)=>P.reduce((a,row)=>a+row[j],0n)===D),"column stochastic");
    let M=P,den=D;
    for(let k=1;k<=h;k++){
      ok(M.every(row=>row.every(x=>x*BigInt(n)===den))===(k===h),"exact dense horizon");
      if(k<h){M=mul(M,P);den*=D;}
    }dense++;
  }
  // Exact count DP on relative position and span; compare to literal direction words.
  const dpProfiles=[];
  for(let h=2;h<=12;h++){
    let a=new Map([["0,0",1n]]),den=1n;let out=[];
    for(let k=0;k<=100;k++){
      let remaining=[...a.values()].reduce((x,y)=>x+y,0n);
      if(k<=12){
        let literal=0n;for(let mask=0;mask<2**k;mask++)if(span(directions(k,mask))<h)literal++;
        ok(literal===remaining,"DP vs enumeration");dpChecks++;
      }
      if([h,2*h,4*h,8*h,100].includes(k))out.push({steps:k,survivalNumerator:remaining.toString(),denominator:den.toString(),probabilityNotForgotten:Number(remaining)/Number(den)});
      let b=new Map();for(let [key,count] of a){let [r,x]=key.split(",").map(Number);for(let d of [-1,1]){
        let y=x+d,R=r;if(y<0){R++;y=0}else if(y>r)R++;
        if(R<h){let z=R+","+y;b.set(z,(b.get(z)||0n)+count)}
      }}a=b;den*=2n;
    }
    dpProfiles.push({h,expectedSteps:h*(h+1)/2,profiles:out});
  }
  // Balanced hidden directions: constant-zero initial state retains a positive marginal bias
  // at every finite horizon in h>=2 because alternating paths preserve an original digit.
  let hiddenChecks=0;
  for(let h=2;h<=5;h++)for(let k=1;k<=10;k++){
    let n=2**h,counts=Array(n).fill(0);
    for(let mask=0;mask<2**k;mask++){let a=run(2,h,directions(k,mask),0);a.forEach((v,i)=>counts[i]+=v)}
    const total=4**k;
    const ones=counts.reduce((v,c,i)=>v+c*i.toString(2).replace(/0/g,"").length,0);
    ok(2*ones<h*total,"hidden schedule bias");hiddenChecks++;
  }
  return {schedules,rows,reverseChecks,dense,dpChecks,hiddenChecks,dpProfiles,assertionFailures:0};
}
console.log(JSON.stringify(laboratory(), null, 2));
