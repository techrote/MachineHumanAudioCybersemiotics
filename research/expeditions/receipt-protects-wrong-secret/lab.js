"use strict";
function lab(){
"use strict";
const assert=(x,msg)=>{if(!x)throw Error(msg)};
let checks={graphPriorTargets:0,partitionOracleLeaves:0,cutChecks:0,decoderCells:0,crownWitnesses:0,crownPartitionChecks:0,twoTargetPartitionChecks:0};
function graph(n,edges){let g=Array.from({length:n},()=>Array(n).fill(false));for(const [u,v] of edges){g[u][v]=g[v][u]=true;}return g;}
function copies(w){return w.flatMap((a,i)=>Array(a).fill(i));}
function sum(a){return a.reduce((x,y)=>x+y,0);}
function partitions(g,w,visit){
 const xs=copies(w), blocks=[];
 function rec(i){if(i===xs.length){visit(blocks);return;}
 const x=xs[i];for(const B of blocks.slice()){if(B.every(y=>!g[x][y])){B.push(x);rec(i+1);B.pop();}}
 blocks.push([x]);rec(i+1);blocks.pop();}
 rec(0);
}
function cols(blocks,n){return blocks.map(B=>{let c=Array(n).fill(0);for(const x of B)c[x]++;return c;});}
function score(C,t){return sum(C.map(c=>{let a=0,b=0;c.forEach((v,x)=>{if(t[x])b+=v;else a+=v});return Math.max(a,b)}));}
function full(C){return sum(C.map(c=>Math.max(...c)));}
function flow(g,w,t){
 const L=copies(w).filter(x=>!t[x]),R=copies(w).filter(x=>t[x]),mate=Array(R.length).fill(-1);
 function aug(i,seen){for(let j=0;j<R.length;j++)if(!g[L[i]][R[j]]&&!seen[j]){seen[j]=true;if(mate[j]<0||aug(mate[j],seen)){mate[j]=i;return true;}}return false;}
 let m=0;for(let i=0;i<L.length;i++)if(aug(i,Array(R.length).fill(false)))m++;
 let used=Array(L.length).fill(false),B=[];
 mate.forEach((i,j)=>{if(i>=0){B.push([L[i],R[j]]);used[i]=true;}else B.push([R[j]]);});
 L.forEach((x,i)=>{if(!used[i])B.push([x]);});
 return {m,C:cols(B,w.length)};
}
function cut(g,w,t){
 let L=w.map((_,i)=>i).filter(i=>!t[i]),R=w.map((_,i)=>i).filter(i=>t[i]),min=sum(w);
 for(let mask=0;mask<2**L.length;mask++){let S=L.filter((_,i)=>mask&(1<<i));let N=R.filter(y=>S.some(x=>!g[x][y]));let capacity=sum(L.filter(x=>!S.includes(x)).map(x=>w[x]))+sum(N.map(y=>w[y]));min=Math.min(min,capacity);checks.cutChecks++;}
 return min;
}
function decode(g,w,C){
 const n=w.length;
 assert(C.length>0&&w.every((v,x)=>sum(C.map(c=>c[x]))===v),"row sums");
 for(let u=0;u<n;u++)for(let v=u+1;v<n;v++)if(g[u][v]){
 for(const c of C){let seen=new Map();for(let x=0;x<n;x++)if(c[x]>0){let out=x===v?u:x;assert(!seen.has(out),"ambiguous decoder");seen.set(out,x);checks.decoderCells++;}}
 }
}
const es=[];for(let i=0;i<4;i++)for(let j=i+1;j<4;j++)es.push([i,j]);
for(let mask=0;mask<64;mask++){
 const g=graph(4,es.filter((_,i)=>mask&(1<<i)));
 for(const w of [[1,1,1,1],[1,2,1,2],[2,1,1,1]]){
 const targets=Array.from({length:14},(_,i)=>Array.from({length:4},(_,x)=>Boolean((i+1)&(1<<x))));
 const best=Array(14).fill(Infinity);
 partitions(g,w,B=>{let C=cols(B,4);targets.forEach((t,i)=>{best[i]=Math.min(best[i],score(C,t));checks.partitionOracleLeaves++;});});
 targets.forEach((t,i)=>{let {m,C}=flow(g,w,t);assert(m===cut(g,w,t),"cut");assert(score(C,t)===sum(w)-m&&best[i]===sum(w)-m,"oracle");decode(g,w,C);checks.graphPriorTargets++;});
 }
}
function crown(r){let e=[];for(let i=0;i<r;i++)for(let j=0;j<r;j++)if(i!==j)e.push([i,r+j]);return graph(2*r,e);}
for(let r=3;r<=24;r++){
 const g=crown(r),t=Array.from({length:2*r},(_,i)=>i>=r);
 for(let b=1;b<=8;b++)for(let a=0;a<=b;a++){
 let C=[];for(let i=0;i<r;i++){let c=Array(2*r).fill(0);c[i]=c[r+i]=a;if(a)C.push(c);}
 if(b>a)for(let side=0;side<2;side++)C.push(t.map(v=>Number(v)===side?b-a:0));
 const w=Array(2*r).fill(b),W=sum(w),M=W-score(C,t);
 assert(M===r*a&&full(C)===r*a+2*(b-a),"crown witness");
 assert(r*full(C)===W+(r-2)*M,"crown equality");decode(g,w,C);checks.crownWitnesses++;
 }
}
{
 const r=3,g=crown(r),w=Array(2*r).fill(1),t=w.map((_,i)=>i>=r);
 partitions(g,w,B=>{let C=cols(B,2*r),W=sum(w),M=W-score(C,t);assert(r*full(C)>=W+(r-2)*M,"crown bound");checks.crownPartitionChecks++;});
}
{
 const g=graph(4,[[0,3],[1,2]]),w=[1,1,1,1],t1=[0,0,1,1],t2=[0,1,0,1];
 partitions(g,w,B=>{let C=cols(B,4);assert(score(C,t1)+score(C,t2)>=6,"two-target bound");checks.twoTargetPartitionChecks++;});
 for(const t of [t1,t2])assert(flow(g,w,t).m===2,"individual perfect privacy");
 // Two flagged perfect-for-one channels mixed with equal probability.
 const C=[...flow(g,w,t1).C,...flow(g,w,t2).C];
 decode(g,[2,2,2,2],C);assert(score(C,t1)===6&&score(C,t2)===6&&full(C)===4,"balanced mixture");
 // Same full-state score, different target score.
 assert(full(flow(g,w,t1).C)===full(flow(g,w,t2).C),"same full");
 assert(score(flow(g,w,t1).C,t1)===2&&score(flow(g,w,t2).C,t1)===4,"different target");
}
return checks;
}
console.log(JSON.stringify(lab(), null, 2));
