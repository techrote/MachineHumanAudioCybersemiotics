"use strict";
function laboratory(){
  function assert(x,msg){if(!x)throw Error(msg)}
  function intervalPeak(w){let best=0;for(let i=0;i<w.length;i++){let s=0;for(let j=0;j<w.length;j++){s+=w[(i+j)%w.length]==="1"?1:-1;best=Math.max(best,s)}}return best}
  function runLengths(w){let i=[...w].findIndex((x,j)=>x==="1"&&w[(j+w.length-1)%w.length]==="0");let v=w.slice(i)+w.slice(0,i),a=[],b=[];for(let m of v.match(/1+|0+/g))(m[0]==="1"?a:b).push(m.length);return [a,b]}
  function hist(w,r){let counts={};for(let i=0;i<w.length;i++){let k=(w+w).slice(i,i+r);counts[k]=(counts[k]||0)+1}return Object.entries(counts).sort().map(x=>x.join(":")).join(",")}
  function workload(w,c=Infinity){let q=0,loss=0,trace=[];for(let i=0;i<2*w.length;i++){q=Math.max(0,q+(w[i%w.length]==="1"?1:-1));if(q>c){if(i>=w.length)loss+=q-c;q=c}if(i>=w.length)trace.push(q)}return {trace,loss,peak:Math.max(...trace)}}
  function score(a,b){return a.map((v,i)=>"1".repeat(v)+"0".repeat(b[i])).join("")}
  function sum(x){return x.reduce((a,b)=>a+b,0)}
  function invMax(a,b){let x=[...a].sort((a,b)=>b-a),y=[...b].sort((a,b)=>a-b);return Math.max(...x.map((_,i)=>sum(x.slice(0,i+1))-sum(y.slice(0,i))))}
  function add(map,key,p){if(!map.has(key))map.set(key,new Set());map.get(key).add(p)}
  let words=0,capChecks=0,invFibres=0,histFibres=0,profiles=[];
  for(let n=2;n<=12;n++){let inv=new Map(),fibres=new Map(),count=0;for(let k=1;k<2**n-1;k++){let w=k.toString(2).padStart(n,"0"),A=[...w].filter(x=>x==="1").length,B=n-A;if(A>B)continue;let [a,b]=runLengths(w),R=a.length,p=intervalPeak(w);assert(workload(w).peak===p,"interval");for(let c=0;c<=p;c++){let z=workload(w,c);assert(z.peak<=c&&z.loss>=p-c&&(z.loss===0)===(c>=p),"capacity");capChecks++}add(inv,JSON.stringify([[...a].sort((a,b)=>a-b),[...b].sort((a,b)=>a-b)]),p);for(let r=2;r<=n;r++)if(Math.min(...a,...b)>=r-1)add(fibres,JSON.stringify([r,A,B,R,hist(w,r)]),p);count++;words++}
    for(let [key,ps] of inv){let [a,b]=JSON.parse(key);assert(Math.max(...ps)===invMax(a,b),"inventory max")}
    for(let [key,ps] of fibres){let [r,A,B,R]=JSON.parse(key),lo=Math.ceil(A/R),hi=A-(R-1)*(r-1);assert(ps.size===hi-lo+1&&Math.min(...ps)===lo&&Math.max(...ps)===hi,"histogram range")}
    invFibres+=inv.size;histFibres+=fibres.size;profiles.push({n,words:count,inventory_fibres:inv.size,long_run_histogram_fibres:fibres.size})}
  function* sortedTuples(vals,n,start=0,p=[]){if(n===0){yield p;return}for(let i=start;i<vals.length;i++)yield* sortedTuples(vals,n-1,i,[...p,vals[i]])}
  function* perms(v,p=[]){if(!v.length){yield p;return}for(let i=0;i<v.length;i++){if(i>0&&v[i]===v[i-1])continue;yield* perms(v.filter((_,j)=>i!==j),[...p,v[i]])}}
  function partition2(v,B){for(let i=1;i<5;i++)for(let j=i+1;j<6;j++)if(v[0]+v[i]+v[j]===B)return true;return false}
  let reduction={profiles:0,yes:0,no:0,orderings:0,examples:[]};
  for(let B=8;B<=18;B++){let vals=Array.from({length:B-1},(_,i)=>i+1).filter(v=>B<4*v&&2*v<B);for(let items of sortedTuples(vals,6)){if(sum(items)!==2*B)continue;let oracle=partition2(items,B);reduction.profiles++;reduction[oracle?"yes":"no"]++;for(let a of [1,2,4]){let opt=Infinity;for(let p of perms(items.map(v=>v+a)))for(let j=0;j<5;j++){let q=Array.from({length:6},(_,k)=>k===j||k===5?B+a:a);opt=Math.min(opt,workload(score(p,q)).peak);reduction.orderings++}assert((opt<=B+a)===oracle,"3-partition");if(B===15&&["4,4,4,6,6,6","4,4,5,5,6,6"].includes(items.join(",")))reduction.examples.push({items,B,a,minimum:opt,partition:oracle})}}}
  let good=score([4,4,2,2],[4,4,2,2]),bad=score([4,4,2,2],[2,2,4,4]);assert(hist(good,3)===hist(bad,3),"witness hist");assert(workload(good).peak===4&&workload(bad).peak===6,"witness peaks");assert(workload(good,4).loss===0&&workload(bad,4).loss===2,"witness losses");
  return {census:{words,cap_checks:capChecks,inventory_fibres:invFibres,histogram_fibres:histFibres,profiles},reduction,witness:{good:{word:good,...workload(good),capped:workload(good,4)},bad:{word:bad,...workload(bad),capped:workload(bad,4)}}}
}
console.log(JSON.stringify(laboratory(),null,2));
