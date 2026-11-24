'use strict';
// MHAC #250; exact integer synthetic laboratory, no dependencies.
// Run with node lab.js. All code in the executable was run before commit.
const result = (function laboratory(){
"use strict";
const assert=(v,m)=>{if(!v)throw Error(m)};
function validate(w,m,k=0){
 if(!Array.isArray(w)||w.some(x=>!Number.isSafeInteger(x)||Math.abs(x)>1000000)||w.length>20||!Number.isInteger(k)||k<0||k>w.length||!(m===null||(Number.isInteger(m)&&m>=0&&m<=w.length)))throw Error("invalid bounded integer audit model");
}
const sum=a=>a.reduce((s,x)=>s+x,0);
const sort=a=>[...a].sort((a,b)=>a-b);
const remove=(a,i)=>a.slice(0,i).concat(a.slice(i+1));
function bounds(w,m=null){
 validate(w,m);const a=sort(w);
 if(m===null)return [sum(a.filter(x=>x<0)),sum(a.filter(x=>x>0))];
 return [sum(a.slice(0,m)),sum(a.slice(a.length-m))];
}
function width(w,m){let [lo,hi]=bounds(w,m);return hi-lo}
function brier(rows,D,m=null){
 if(!Number.isInteger(D)||D<1||D>100||!Array.isArray(rows)||rows.length<1||rows.length>20)throw Error("invalid scale or roster");
 let base=0,w=[];
 for(const row of rows){
  if(!Array.isArray(row)||row.length!==3)throw Error("invalid row");
  const [p,q,y]=row;
  if(!Number.isInteger(p)||!Number.isInteger(q)||p<0||q<0||p>D||q>D||![0,1,null].includes(y))throw Error("invalid forecast/label");
  base+=p*p-q*q;
  const c=2*D*(q-p);
  if(y===null)w.push(c);else base+=c*y;
 }
 const [lo,hi]=bounds(w,m);
 return {numerators:[base+lo,base+hi],denominator:rows.length*D*D,weights:w,base};
}
function optimal(w,m,k){
 validate(w,m,k);
 const n=w.length,l=n-k;
 const indexed=w.map((x,i)=>({x,i})).sort((a,b)=>a.x-b.x||a.i-b.i);
 let retained, value;
 if(m===null){
  retained=[...indexed].sort((a,b)=>Math.abs(a.x)-Math.abs(b.x)||a.i-b.i).slice(0,l);
  value=sum(retained.map(x=>Math.abs(x.x)));
 }else{
  const r=Math.min(m,n-m,Math.floor(l/2));
  value=Infinity;
  for(let j=0;j<=n-l;j++){
   const block=indexed.slice(j,j+l), a=block.map(x=>x.x);
   const v=width(a,r);
   if(v<value){value=v;retained=block}
  }
 }
 const keep=new Set(retained.map(x=>x.i));
 return {width:value,audit:w.map((_,i)=>i).filter(i=>!keep.has(i)),retained:retained.map(x=>x.i)};
}
function* subsets(n,k,start=0,prefix=[]){
 if(k===0){yield prefix;return}
 for(let i=start;i<=n-k;i++)yield* subsets(n,k-1,i+1,[...prefix,i]);
}
function fixedOracle(w,m,k){
 let best=Infinity;
 for(const ix of subsets(w.length,k)){
  const chosen=new Set(ix), rest=w.filter((_,i)=>!chosen.has(i));
  let worst=0;
  for(let t=0;t<=k;t++){
   if(m!==null&&(m-t<0||m-t>rest.length))continue;
   worst=Math.max(worst,width(rest,m===null?null:m-t));
  }
  best=Math.min(best,worst);
 }
 return best;
}
const memo=new Map();
function adaptiveOracle(w,m,k){
 const a=sort(w),key=JSON.stringify([a,m,k]);
 if(memo.has(key))return memo.get(key);
 let v;
 if(k===0||m===0||m===a.length)v=width(a,m);
 else {
  v=Infinity;
  for(let i=0;i<a.length;i++){
   const rest=remove(a,i), branches=[];
   if(m===null||m< a.length)branches.push(adaptiveOracle(rest,m,k-1));
   if(m===null||m>0)branches.push(adaptiveOracle(rest,m===null?null:m-1,k-1));
   v=Math.min(v,Math.max(...branches));
  }
 }
 memo.set(key,v);return v;
}
// Expected-width numerators under uniform distribution over fixed-count worlds.
// At each branch, the number of compatible worlds changes; adding child totals
// counts each original world once. No floating arithmetic is required.
function choose(n,k){if(k<0||k>n)return 0;let c=0;for(const _ of subsets(n,k))c++;return c}
function expectedAdaptive(w,m,k){
 if(k===0||m===0||m===w.length)return {num:choose(w.length,m)*width(w,m),first:null};
 let best={num:Infinity,first:null};
 for(let i=0;i<w.length;i++){
  const r=remove(w,i);
  let v=0;
  if(m< w.length)v+=expectedAdaptive(r,m,k-1).num;
  if(m>0)v+=expectedAdaptive(r,m-1,k-1).num;
  if(v<best.num)best={num:v,first:i};
 }
 return best;
}
function expectedFixed(w,m,k){
 let best={num:Infinity,audit:null};
 for(const ix of subsets(w.length,k)){
  const chosen=new Set(ix),r=w.filter((_,i)=>!chosen.has(i));
  let v=0;
  for(let t=0;t<=k;t++){
   if(m-t<0||m-t>r.length)continue;
   v+=choose(k,t)*choose(r.length,m-t)*width(r,m-t);
  }
  if(v<best.num)best={num:v,audit:ix};
 }
 return best;
}
function directBrier(rows,D,m){
 const n=rows.filter(r=>r[2]===null).length;
 let lo=Infinity,hi=-Infinity;
 for(let t=0;t<=n;t++){
  if(m!==null&&t!==m)continue;
  for(const ix of subsets(n,t)){
   const positive=new Set(ix);let j=0,s=0;
   for(const [p,q,y] of rows){
    const z=y===null?Number(positive.has(j++)):y;
    s+=(p-D*z)**2-(q-D*z)**2;
   }
   lo=Math.min(lo,s);hi=Math.max(hi,s);
  }
 }
 return [lo,hi];
}
function* multiset(n,low=-2,prefix=[]){
 if(n===0){yield prefix;return}
 for(let i=low;i<=2;i++)yield* multiset(n-1,i,[...prefix,i]);
}
function* rosters(n,prefix=[]){
 if(n===0){yield prefix;return}
 for(let p=0;p<=2;p++)for(let q=0;q<=2;q++)for(const y of [0,1,null])yield* rosters(n-1,[...prefix,[p,q,y]]);
}
let scoreComparisons=0,policyComparisons=0,refusals=0;
for(let n=1;n<=3;n++)for(const rows of rosters(n)){
 const miss=rows.filter(r=>r[2]===null).length;
 for(const m of [null,...Array.from({length:miss+1},(_,i)=>i)]){
  assert(JSON.stringify(brier(rows,2,m).numerators)===JSON.stringify(directBrier(rows,2,m)),"Brier bound mismatch");scoreComparisons++;
 }
}
for(let n=0;n<=7;n++)for(const w of multiset(n))for(const m of [null,...Array.from({length:n+1},(_,i)=>i)])for(let k=0;k<=n;k++){
 const p=optimal(w,m,k);
 assert(p.audit.length===k,"audit count");
 const f=fixedOracle(w,m,k),a=adaptiveOracle(w,m,k);
 assert(p.width===f&&f===a,"policy mismatch "+JSON.stringify([w,m,k,p,f,a]));
 // independently check the returned fixed witness
 let actual=0;
 const r=w.filter((_,i)=>!p.audit.includes(i));
 for(let t=0;t<=k;t++)if(m===null||(m>=t&&m-t<=r.length))actual=Math.max(actual,width(r,m===null?null:m-t));
 assert(actual===p.width,"witness mismatch");
 policyComparisons++;
}
const w=[0,1,1,3,3,4],m=2,k=2;
const eA=expectedAdaptive(w,m,k),eF=expectedFixed(w,m,k),den=choose(w.length,m);
assert(eA.num===38&&eF.num===40&&den===15,"expected counterexample");
const after0=expectedAdaptive(remove(w,eA.first),2,1),after1=expectedAdaptive(remove(w,eA.first),1,1);
const example=Array.from({length:7},(_,budget)=>({budget,known:optimal([-4,-3,-2,1,2,5],2,budget).width,unknown:optimal([-4,-3,-2,1,2,5],null,budget).width}));
assert(width([5,5,5,5],2)===0&&width([5,5,5,5],null)===20,"count identifies constant weights");
assert(optimal([0,0,0,0],null,1).width===0,"equal forecasts");
assert(optimal([1,2,3],1,3).width===0,"full audit");
for(const f of [()=>bounds([1],2),()=>optimal([1],null,2),()=>brier([[0,3,null]],2),()=>brier([[1,1,2]],2),()=>brier([],2)]){
 let refused=false;try{f()}catch(e){refused=true}assert(refused,"invalid input accepted");refusals++;
}
return {scoreComparisons,policyComparisons,refusals,expectedExample:{w,m,k,den,eA,eF,after0,after1,worst:optimal(w,m,k)},frontier:example};
})();
console.log(JSON.stringify(result,null,2));
