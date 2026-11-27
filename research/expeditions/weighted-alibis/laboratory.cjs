"use strict";
function laboratory(){
 const assert=(v,m)=>{if(!v)throw Error(m)};
 const abs=x=>x<0n?-x:x, gcd=(a,b)=>{a=abs(a);b=abs(b);while(b){[a,b]=[b,a%b]}return a};
 const dot=(a,b)=>a.reduce((s,x,i)=>s+x*b[i],0n);
 const frac=(a,b)=>{const g=gcd(a,b);return [a/g,b/g]};
 const lt=(a,b)=>a[0]*b[1]<b[0]*a[1];
 const approx=(a,b)=>{if(a===0n)return 0;let s=a<0n?-1:1;a=abs(a);const x=a.toString(),y=b.toString();return s*Number(x.slice(0,15))/Number(y.slice(0,15))*10**(Math.max(0,x.length-15)-Math.max(0,y.length-15))};
 const fs=f=>f.map(String).join("/");
 const sqrt=n=>{if(n<2n)return n;let x=1n<<BigInt(Math.ceil(n.toString(2).length/2));for(;;){let y=(x+n/x)>>1n;if(y>=x)return x;x=y}};
 const conv=(a,b)=>{let c=Array(a.length+b.length-1).fill(0n);a.forEach((x,i)=>b.forEach((y,j)=>c[i+j]+=x*y));return c};
 const ps=[5,7,11,13,17], a=ps.reduce((p,q)=>conv(p,Array(q).fill(1n)),[-1n,1n]), D=a.length-1;
 assert(D===49,"degree");
 const H=N=>Array.from({length:N-D},(_,i)=>Array.from({length:N},(_,j)=>a[j-i]??0n));
 function projection(N){
   const rows=H(N), basis=[], norms=[];
   for(let r of rows){r=r.slice();for(let i=0;i<basis.length;i++){let z=dot(r,basis[i]);if(z===0n)continue;let d=norms[i],g=gcd(d,z);r=r.map((x,j)=>x*(d/g)-basis[i][j]*(z/g));let k=r.reduce(gcd,0n);assert(k!==0n,"independence");r=r.map(x=>x/k)}
    assert(basis.every(x=>dot(r,x)===0n),"orthogonality");basis.push(r);norms.push(dot(r,r));}
   const L=norms.reduce((s,n)=>s/gcd(s,n)*n,1n);
   const G=Array.from({length:N},(_,i)=>Array.from({length:N},(_,j)=>basis.reduce((s,r,k)=>s+r[i]*r[j]*(L/norms[k]),0n)));
   assert(G.reduce((s,r,i)=>s+r[i],0n)===BigInt(N-D)*L,"trace");
   for(const r of rows)for(let i=0;i<N;i++)assert(dot(G[i],r)===L*r[i],"row fixed");
   for(let i=0;i<N;i++)for(const p of ps)for(let v=0;v<p;v++)assert(G[i].reduce((s,x,j)=>s+(j%p===v?x:0n),0n)===0n,"period annihilation");
   return {G,L};
 }
 function quant(G){
   const max=G.reduce((s,r,i)=>r[i]>s?r[i]:s,0n);let attempts=[];
   for(let b=0;b<=40;b++){let scale=1n<<BigInt(b);let w=G.map((r,i)=>sqrt(r[i]*scale*scale/max));
     let fails=0, min=null, pair=null;
     for(let i=0;i<w.length;i++)for(let j=0;j<w.length;j++)if(i!==j){let left=abs(G[i][j])*w[i],right=G[i][i]*w[j];if(w[i]===0n||right<=left)fails++;else if(left>0n&&(!min||lt([right,left],min))){min=[right,left];pair=[i,j]}}
     attempts.push({bits:b,failedOrderedInequalities:fails});
     if(fails===0)return {bits:b,weights:w.map(String),minRatio:fs(frac(...min)),minRatioApprox:approx(...min),pair,attempts};
   }throw Error("quantization search exhausted");
 }
 const profiles=[];
 let q51;
 for(const N of [51,52,53,55,57,60,64,70,85]){
  let {G,L}=projection(N);if(N===51)q51={G,L};
  let minOpen=null,minClosed=null,minClean=null,openPair=null,closedPair=null,cleanIndex=null,minAngle=null,anglePair=null,checks=0;
  for(let i=0;i<N;i++){const U=G[i][i];assert(U>0n,"nonzero column");if(!minClean||lt([U,L],minClean)){minClean=[U,L];cleanIndex=i}
    for(let j=0;j<N;j++)if(i!==j){const V=G[j][j],W=abs(G[i][j]),det=U*V-W*W;assert(det>0n,"noncollinear");checks++;
      const op=[det,L*V],ang=[det,U*V];
      if(!minOpen||lt(op,minOpen)){minOpen=op;openPair=[i,j]}
      if(!minAngle||lt(ang,minAngle)){minAngle=ang;anglePair=[i,j]}
      const cl=W>V?[det,L*V]:W>U?[det,L*U]:[U+V-2n*W,L];
      if(!minClosed||lt(cl,minClosed)){minClosed=cl;closedPair=[i,j]}
    }
  }
  const overall=lt(minClean,minClosed)?minClean:minClosed;
  profiles.push({N,orderedPairs:checks,openPair,openRadiusPerUnit:Math.sqrt(approx(...minOpen))/2,openDistanceSquared:fs(frac(...minOpen)),closedPair,closedDistanceSquared:fs(frac(...minClosed)),cleanIndex,cleanDistanceSquared:fs(frac(...minClean)),minimaxRadiusPerUnit:Math.sqrt(approx(...overall))/2,minAngleDegrees:Math.asin(Math.sqrt(approx(...minAngle)))*180/Math.PI,anglePair});
 }
 const {G,L}=q51, h=H(51),raw=Array.from({length:51},(_,i)=>Array.from({length:51},(_,j)=>h.reduce((s,r)=>s+r[i]*r[j],0n)));
 const rawWeights=quant(raw), projectedWeights=quant(G);
 const w=projectedWeights.weights.map(BigInt),z=rawWeights.weights.map(BigInt);
 // The old two-error explanation is checked against both new weightings.
 assert(127n*w[0]<w[25]+w[26],"projected counterexample repair");
 assert(127n*z[0]<z[25]+z[26],"raw counterexample repair");
 assert(a[25]===32n&&a[26]===95n&&a[24]===-32n,"predecessor");
 // Construct an exact midpoint collision for the global minimax radius.
 const [i,j]=profiles[0].closedPair,U=G[i][i],V=G[j][j],W=abs(G[i][j]);
 const sign=G[i][j]<0n?-1n:1n;
 let an=1n,bn=1n,den=1n;if(W>V){bn=W;an=V;den=V}else if(W>U){an=W;bn=U;den=U}
 assert(an>=den&&bn>=den,"minimum amplitude");
 // Projected centers are G[:,i]*an/(L*den) and G[:,j]*sign*bn/(L*den).
 const diff=G.map(r=>an*r[i]-sign*bn*r[j]),ds=dot(diff,diff);
 assert(fs(frac(ds,L*L*den*den))===profiles[0].closedDistanceSquared,"midpoint exact squared distance");
 // Lift each center to an admissible clean signal plus one fault:
 // clean = projected fault - fault; every H row annihilates it.
 for(const r of h){assert(dot(r,G.map((v,k)=>v[i]-BigInt(k===i)*L))===0n,"first lift");assert(dot(r,G.map((v,k)=>v[j]-BigInt(k===j)*L))===0n,"second lift")}
 return {periods:ps,D,profiles,rawWeights,projectedWeights,oldAlternativeWeightedCost:{raw:approx(z[25]+z[26],127n*z[0]),projected:approx(w[25]+w[26],127n*w[0])},midpoint:{i,j,alpha:fs(frac(an,den)),beta:fs(frac(sign*bn,den)),squaredRadius:fs(frac(ds,4n*L*L*den*den))}};
}
console.log(JSON.stringify(laboratory(),null,2));
