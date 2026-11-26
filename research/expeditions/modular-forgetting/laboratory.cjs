"use strict";
function laboratory(){
 const assert=(b,m)=>{if(!b)throw Error(m)};
 const zeros=(p,a,w)=>{let z=[];for(let j=1;j<=a;j++){let n=p**j,h=n/p,r=Array(n).fill(0);w.forEach((v,i)=>r[i%n]+=v);if(Array.from({length:h},(_,i)=>i).every(i=>Array.from({length:p},(_,k)=>r[i+k*h]).every(x=>x===r[i])))z.push(j)}return z};
 function* counts(n,d,prefix=[]){if(n===1){yield [...prefix,d];return}for(let v=0;v<=d;v++)yield*counts(n-1,d-v,[...prefix,v])}
 const vp=(d,p)=>{let a=0;while(d%p===0){a++;d/=p}return a};
 const conv=(x,y)=>{let z=Array(x.length).fill(0n);for(let i=0;i<x.length;i++)for(let j=0;j<y.length;j++)z[(i+j)%z.length]+=x[i]*y[j];return z};
 const uniform=x=>x.every(v=>v===x[0]);
 const schedule=(h,c,e)=>{const arr=Array.from({length:h*(e+1)},(_,i)=>i%h);return Array.from({length:Math.ceil(arr.length/c)},(_,i)=>arr.slice(i*c,(i+1)*c))};
 const digit=(p,a,js)=>{let n=p**a,w=Array(n).fill(0n),xs=[0];for(let j of js)xs=xs.flatMap(x=>Array.from({length:p},(_,k)=>x+k*p**j));for(let x of xs)w[x]=1n;return w};
 function* omissions(k,e,start=0,arr=[]){yield arr;if(e)for(let i=start;i<k;i++)yield*omissions(k,e-1,i+1,[...arr,i])}
 let integerProfiles=0,integerZeroChecks=0,exactSchedules=0,exactErasureChecks=0,realProfiles=0,realSchedules=0,realErasureChecks=0,maxResidual=0;
 for(let [p,a,dmax] of [[2,1,8],[2,2,8],[2,3,7],[2,4,5],[3,1,8],[3,2,5],[5,1,6]]){
  for(let d=1;d<=dmax;d++)for(let w of counts(p**a,d)){
   let z=zeros(p,a,w),s=w.filter(Boolean).length;assert(p**z.length<=s,"support bound");assert(z.length<=vp(d,p),"denominator bound");integerProfiles++;integerZeroChecks+=a;
   if(a===1)assert(z.length===0||w.every(x=>x===w[0]),"prime rational");
  }
 }
 for(let p of [2,3,5])for(let a=1;a<= (p===2?5:p===3?3:2);a++)for(let c=1;c<=a;c++)for(let e=0;e<=2;e++){
  let n=p**a,sets=schedule(a,c,e),ws=sets.map(s=>digit(p,a,s));for(let i=0;i<sets.length;i++)assert(zeros(p,a,ws[i].map(Number)).join()===sets[i].map(j=>j+1).sort((a,b)=>a-b).join(),"digit orders");
  let id=Array(n).fill(0n);id[0]=1n;for(let omit of omissions(ws.length,e)){let z=ws.reduce((x,w,i)=>omit.includes(i)?x:conv(x,w),id);assert(uniform(z),"exact erased stages");exactErasureChecks++}exactSchedules++;
 }
 const features=(p,ks,x)=>[1,...ks.flatMap(k=>[Math.cos(2*Math.PI*k*x/p),Math.sin(2*Math.PI*k*x/p)])];
 // Caratheodory elimination: find one null direction using row reduction.
 function sparse(p,ks){let w=Array(p).fill(1/p),dim=1+2*ks.length;
  while(w.filter(x=>x>0).length>dim){
   let ids=w.map((v,i)=>i).filter(i=>w[i]>0).slice(0,dim+1),cols=ids.map(i=>features(p,ks,i)),A=Array.from({length:dim},(_,i)=>cols.map(c=>c[i])),piv=[],r=0;
   for(let c=0;c<ids.length&&r<dim;c++){let b=r;for(let i=r+1;i<dim;i++)if(Math.abs(A[i][c])>Math.abs(A[b][c]))b=i;if(Math.abs(A[b][c])<1e-10)continue;[A[b],A[r]]=[A[r],A[b]];let v=A[r][c];A[r]=A[r].map(x=>x/v);for(let i=0;i<dim;i++)if(i!==r){let v=A[i][c];A[i]=A[i].map((x,j)=>x-v*A[r][j])}piv.push(c);r++}
   let free=ids.findIndex((_,i)=>!piv.includes(i));assert(free>=0,"null direction");let d=ids.map(()=>0);d[free]=1;piv.forEach((c,i)=>d[c]=-A[i][free]);let t=Math.min(...d.map((v,i)=>v>0?w[ids[i]]/v:Infinity));assert(Number.isFinite(t),"step");ids.forEach((x,i)=>{w[x]-=t*d[i];if(Math.abs(w[x])<1e-10)w[x]=0;assert(w[x]>=0,"nonnegative")});
  }
  assert(w.filter(x=>x>0).length===dim,"sharp support");let sums=features(p,ks,0).map((_,i)=>w.reduce((s,v,x)=>s+v*features(p,ks,x)[i],0));sums[0]-=1;let err=Math.max(...sums.map(Math.abs));maxResidual=Math.max(maxResidual,err);assert(err<1e-7,"real moments");return w
 }
 const fconv=(x,y)=>{let z=x.map(()=>0);for(let i=0;i<x.length;i++)for(let j=0;j<y.length;j++)z[(i+j)%z.length]+=x[i]*y[j];return z};
 for(let p of [3,5,7,11,13,17]){let h=(p-1)/2,bank=new Map;for(let m=0;m<2**h;m++){let ks=Array.from({length:h},(_,i)=>i+1).filter((_,i)=>m>>i&1);bank.set(ks.join(),sparse(p,ks));realProfiles++}
 for(let c=1;c<=h;c++)for(let e=0;e<=2;e++){let ws=schedule(h,c,e).map(s=>bank.get(s.map(j=>j+1).sort((a,b)=>a-b).join()));let id=Array(p).fill(0);id[0]=1;for(let omit of omissions(ws.length,e)){let z=ws.reduce((x,w,i)=>omit.includes(i)?x:fconv(x,w),id);let err=Math.max(...z.map(v=>Math.abs(v-1/p)));maxResidual=Math.max(maxResidual,err);assert(err<1e-7,"real erased stages");realErasureChecks++}realSchedules++}
 }
 let p=5,a=[0.5,0,0,0.5,0],b=[0.5,0.5,0,0,0]; // explicit negative control uses identical binary stages, not complementary
 let t=Array(5).fill(0n);t[0]=1n;let tv=[];for(let k=1;k<=12;k++){t=conv(t,[1n,1n,0n,0n,0n]);assert(!uniform(t),"same mask");let d=2**k;tv.push(t.reduce((s,v)=>s+Math.abs(Number(v)/d-1/5),0)/2)}
 return {integerProfiles,integerZeroChecks,exactSchedules,exactErasureChecks,realProfiles,realSchedules,realErasureChecks,maxResidual,repeatedBinaryTV:tv,assertionFailures:0};
}
console.log(JSON.stringify(laboratory(),null,2));
