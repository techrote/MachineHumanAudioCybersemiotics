"use strict";
console.log(JSON.stringify((function lab(){
const ok=(b,m)=>{if(!b)throw Error(m)}, R=n=>Array.from({length:n},(_,i)=>i), cycle=n=>R(n).map(i=>[i,(i+1)%n]);
const counts={channels:0,layerCertificates:0,directDecoderCells:0,oddCycleWitnesses:0,finiteAlphabetFamilies:0,repeatHistories:0,negativeControls:0};
function metrics(rows,D,edges){
 const n=rows.length,m=rows[0].length;
 ok(rows.every(r=>r.length===m&&r.every(x=>Number.isSafeInteger(x)&&x>=0)&&r.reduce((a,b)=>a+b,0)===D),"row law");
 let U=0,V=0,correct=0,layerU=0,layerV=0,layerRows=Array(n).fill(0);
 for(let j=0;j<m;j++){
  const col=rows.map(r=>r[j]); U+=Math.max(...col);
  for(const [a,b] of edges){
   V+=Math.min(col[a],col[b]);
   const bins=Array.from({length:n},()=>[]);
   for(let x=0;x<n;x++)bins[x===b?a:x].push(col[x]);
   for(const bin of bins)if(bin.length){correct+=Math.max(...bin);counts.directDecoderCells++;}
  }
  const levels=[...new Set(col.filter(x=>x>0))].sort((a,b)=>a-b);
  let prev=0;
  for(const t of levels){
   const w=t-prev,mask=col.map(x=>x>=t);prev=t;layerU+=w;
   for(let x=0;x<n;x++)if(mask[x])layerRows[x]+=w;
   for(const [a,b] of edges)if(mask[a]&&mask[b])layerV+=w;
   counts.layerCertificates++;
  }
 }
 ok(layerU===U&&layerV===V&&layerRows.every(x=>x===D),"layer identity");
 ok(n*edges.length*D-correct===V,"direct decoder error");
 counts.channels++;return {U,V};
}
function bounds(n,D,v){
 const k=(n-1)/2;
 ok(k*v.U+v.V>=n*D,"first support line");
 ok(n*v.U+v.V>=2*n*D,"second support line");
}
function comp(D,m){return m===1?[[D]]:R(D+1).flatMap(i=>comp(D-i,m-1).map(r=>[i,...r]));}
function enumerate(n,D,m,edges,isCycle=false){
 const choices=comp(D,m),rows=[];
 function walk(){if(rows.length===n){const v=metrics(rows,D,edges);if(isCycle)bounds(n,D,v);return}
 for(const row of choices){rows.push(row);walk();rows.pop();}}
 walk();
}
for(let mask=1;mask<8;mask++)enumerate(3,2,3,[[0,1],[0,2],[1,2]].filter((_,i)=>mask>>i&1));
enumerate(5,3,3,cycle(5),true);
function orbit(n,s){
 const k=(n-1)/2, seed=s<=k?R(s).map(i=>2*i):R(n).filter(i=>!R(n-s).map(j=>2*j).includes(i));
 return R(n).map(x=>R(n).map(j=>Number(seed.includes((x-j+n)%n))));
}
for(let n=5;n<=15;n+=2){
 const k=(n-1)/2;
 for(let s=1;s<=n;s++){
  const v=metrics(orbit(n,s),s,cycle(n));
  ok(v.U===n&&v.V===n*Math.max(0,2*s-n),"orbit minimum internal edges");
  bounds(n,s,v);counts.oddCycleWitnesses++;
 }
 for(const [s,t] of [[k,k+1],[k+1,n]]){
  const a=orbit(n,s),b=orbit(n,t);
  for(let i=0;i<=10;i++){
   const D=10*s*t,rows=a.map((r,x)=>[...r.map(v=>v*i*t),...b[x].map(v=>v*(10-i)*s)]);
   const v=metrics(rows,D,cycle(n));bounds(n,D,v);
   ok(s===k?k*v.U+v.V===n*D:n*v.U+v.V===2*n*D,"sharp mixture");counts.oddCycleWitnesses++;
  }
 }
}
const independent=R(31).map(i=>i+1).filter(m=>cycle(5).every(([a,b])=>!((m>>a&1)&&(m>>b&1))));
for(let f=1;f<(1<<independent.length);f++){
 const sets=independent.filter((_,i)=>f>>i&1);
 if(sets.length>4||sets.reduce((a,b)=>a|b,0)!==31)continue;
 const witness=R(32).find(m=>R(5).filter(i=>m>>i&1).length===3&&sets.every(s=>R(5).filter(i=>(s&m)>>i&1).length<=1));
 ok(witness!==undefined,"three-state lower bound with <=4 names");counts.finiteAlphabetFamilies++;
}
const det=metrics([[1,0,0],[0,1,0],[1,0,0],[0,1,0],[0,0,1]],1,cycle(5));ok(det.U===3&&det.V===0,"deterministic witness");
const rand=metrics(orbit(5,2),2,cycle(5));ok(rand.U===5&&rand.V===0,"five-name witness");
const constant=metrics(R(5).map(()=>[1]),1,cycle(5));ok(constant.U===1&&constant.V===5,"no information baseline");counts.negativeControls+=3;
for(let r=1;r<=10;r++){
 const rows=orbit(5,2),buckets=new Map();
 for(let x=0;x<5;x++){
  const tags=R(5).filter(j=>rows[x][j]);
  for(let i=0;i<2**r;i++){const key=R(r).map(j=>tags[i>>j&1]).join(",");buckets.set(key,(buckets.get(key)||0)+1);counts.repeatHistories++;}
 }
 ok(buckets.size===5*(2**r-1),"repeat vulnerability");
 ok([...buckets.values()].every(x=>x===1||x===2),"repeat posterior support");
}
return counts;
})()));
