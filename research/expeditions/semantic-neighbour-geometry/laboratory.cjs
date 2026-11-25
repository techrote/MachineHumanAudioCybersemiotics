'use strict';
function laboratory(){
  let checks=0, maxError=0, profiles=0, pairs=0, inversions=0, localProfiles=0;
  const eq=(x,y)=>{let e=Math.abs(x-y);maxError=Math.max(e,maxError);if(!Number.isFinite(e)||e>1e-9*Math.max(1,Math.abs(x),Math.abs(y)))throw Error(`${x} != ${y}`);checks++};
  const ok=x=>{if(!x)throw Error("assertion");checks++};
  const sq=(a,b)=>a.reduce((s,v,i)=>s+(v-b[i])**2,0);
  const norm2=a=>a.reduce((s,v)=>s+v*v,0);
  const radius=k=>2*(1-1/k);
  const cap=(a,b,E)=>a+b+(Math.sqrt(E-a)-Math.sqrt(E-b))**2;
  const code=(m,n,E)=>Array.from({length:m+n},(_,i)=>{
    const first=i<m, k=first?m:n, offset=first?0:m;
    let v=Array(m+n+1).fill(0); for(let j=offset;j<offset+k;j++)v[j]=Math.SQRT2*((j===i?1:0)-1/k);
    v[m+n]=E===null?0:Math.sqrt(E-radius(k));return v;
  });
  for(let m=2;m<=20;m++)for(let n=2;n<=20;n++){
    let a=radius(m),b=radius(n);
    for(let E of [null,Math.max(a,b),Math.max(a,b)+.1,4,16]){
      let v=code(m,n,E),c=E===null?a+b:cap(a,b,E);
      for(let i=0;i<v.length;i++){
        eq(norm2(v[i]),E===null?(i<m?a:b):E);
        for(let j=0;j<i;j++){
          eq(sq(v[i],v[j]),(i<m)===(j<m)?4:c);pairs++;
        }
      }
      profiles++;
    }
    if(m!==n)for(let frac of [.001,.01,.1,.5,1]){
      let eps=Math.abs(a-b)*frac, E=frac===1?Math.max(a,b):(a+b)/2+eps/4+(a-b)**2/(4*eps);
      eq(cap(a,b,E),a+b+eps);ok(E>=Math.max(a,b)-1e-10);inversions++;
    }
    for(let k=2;k<=Math.min(m,n);k++){
      eq(radius(k)+radius(k),4-4/k);ok(radius(k)+radius(k)<=a+b+1e-10);localProfiles++;
    }
    const p=Math.ceil(Math.log2(m)),q=Math.ceil(Math.log2(n));
    const v=Array.from({length:m+n},(_,i)=>Array.from({length:p+q},(_,j)=>i<m?(j<p?((i>>j)&1?1:-1):0):(j<p?0:(((i-m)>>(j-p))&1?1:-1))));
    for(let i=0;i<v.length;i++)for(let j=0;j<i;j++){eq(Math.max(...v[i].map((x,k)=>Math.abs(x-v[j][k]))),(i<m)===(j<m)?2:1);pairs++}
  }
  return {profiles,coordinatePairChecks:pairs,inverseEnergyCases:inversions,balancedSubsetChecks:localProfiles,assertions:checks,maxAbsoluteNumericError:maxError,example:{m:2,n:6,unconstrainedCrossSquared:radius(2)+radius(6),equalEnergyMinimum:cap(radius(2),radius(6),radius(6)),equalEnergy8:cap(radius(2),radius(6),8)}};
}
console.log(JSON.stringify(laboratory(), null, 2));
