"use strict";
function laboratory(){
  const assert=(ok,msg)=>{if(!ok)throw Error(msg)};
  const gcd=(a,b)=>b?gcd(b,a%b):a;
  const comb=(n,k)=>{let v=1n;for(let i=1;i<=k;i++)v=v*BigInt(n-i+1)/BigInt(i);return v};
  const norm=(m,M)=>{
    const den=BigInt(M)**BigInt(m),q=BigInt(M-1);
    let bestN=den,bestD=1n,bestK=0;
    for(let k=1;k<=m;k++){
      let n=0n;
      for(let j=0;j<=m;j++)n+=comb(m,j)*q**BigInt(j)*BigInt(Math.abs(k-j));
      if(n*bestD<bestN*BigInt(k)){bestN=n;bestD=BigInt(k);bestK=k}
    }
    const g=gcd(bestN,bestD*den);return {n:bestN/g,d:bestD*den/g,k:bestK};
  };
  let exactProfiles=0,criterionProfiles=0;
  for(let M=2;M<=32;M++)for(let m=1;m<=30;m++){
    const a=norm(m,M),q=BigInt(M-1);
    const criterion=2n*q**BigInt(m-1)>=BigInt(M)**BigInt(m-1);
    assert(a.n*BigInt(M)<=a.d,"single slice upper bound");
    assert((a.n*BigInt(M)===a.d)===criterion,"binomial derivative criterion");
    if(m<=Math.floor((M+1)/2)){assert(criterion,"coprime dimension bound");criterionProfiles++}
    exactProfiles++;
  }
  let exhaustive=0,randomProfiles=0,sharp=0,seed=763;
  const rng=n=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed%n};
  const grid=ps=>{const P=ps.reduce((a,b)=>a*b,1);return Array.from({length:P},(_,t)=>ps.map(p=>t%p))};
  const check=(ps,theta,cells)=>{
    const values=cells.map(c=>theta[0]+c.reduce((a,v,i)=>a+theta[i+1][v],0));
    const l1=values.reduce((a,b)=>a+Math.abs(b),0),max=Math.max(...values.map(Math.abs)),d=cells.length/Math.max(...ps);
    assert(l1>=d*max,"full grid concentration");
    return {values,l1,max,d}
  };
  for(const ps of [[2,3,5],[3,5,7],[3,5,11],[2,3,5,7],[3,5,7,11],[5,7,11,13,17]]){
    const cells=grid(ps),dim=1+ps.reduce((a,b)=>a+b-1,0);
    const decode=arr=>{let j=1;return [arr[0],...ps.map(p=>[0,...Array.from({length:p-1},()=>arr[j++])])]};
    if(ps.join()==="2,3,5"){
      for(let t=0;t<3**dim;t++){let k=t;const arr=Array.from({length:dim},()=>{let a=k%3-1;k=Math.floor(k/3);return a});check(ps,decode(arr),cells);exhaustive++}
    }
    const reps=cells.length>10000?8:64;
    for(let i=0;i<reps;i++){check(ps,decode(Array.from({length:dim},()=>rng(21)-10)),cells);randomProfiles++}
    const theta=[0,...ps.map((p,i)=>Array.from({length:p},(_,j)=>i===ps.length-1&&j===1?1:0))];
    const a=check(ps,theta,cells);assert(a.l1===a.d&&a.max===1,"sharp slice");
    for(let e=0;e<=a.d;e++){assert(Math.min(e,a.d)===a.values.filter(x=>x===1).slice(0,e).length,"sharp top mass");if(e>30&&e<a.d)e=a.d-1}
    sharp++;
  }
  const neg=Array.from({length:64},(_,i)=>3-i.toString(2).split("1").length+1);
  const sorted=neg.map(Math.abs).sort((a,b)=>b-a);
  const total=sorted.reduce((a,b)=>a+b,0),bad=sorted.slice(0,15).reduce((a,b)=>a+b,0);
  assert(total===60&&bad===31&&2*15<32&&bad>total-bad,"binary full-grid failure");
  const table=[[2,3],[2,6],[3,3],[4,4],[5,4],[7,4]].map(([M,m])=>{let x=norm(m,M);return {M,m,minimumMean:x.n.toString()+"/"+x.d.toString(),minimumMass:Number(x.n)*M**m/Number(x.d),k:x.k}});
  return {exactProfiles,criterionProfiles,exhaustive,randomProfiles,sharp,negative:{cells:64,distance:32,errors:15,trueCost:bad,falseCost:total-bad},table};
}
console.log(JSON.stringify(laboratory(),null,2));
