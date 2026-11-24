"use strict";
function momentCheck(){
  const rows=[];for(let a=0;a<=4;a++)for(let b=0;b<=4-a;b++)rows.push([a,b,4-a-b]);
  function* multiset(m,start=0,p=[]){if(!m){yield p;return}for(let i=start;i<rows.length;i++)yield*multiset(m-1,i,[...p,i])}
  const sequences=k=>Array.from({length:3**k},(_,i)=>Array.from({length:k},(_,j)=>Math.floor(i/3**j)%3));
  function sig(g,k){return sequences(k).map(t=>g.reduce((s,i)=>s+t.reduce((p,a)=>p*rows[i][a],1),0)).join(",")}
  const result=[];
  for(let m=2;m<=4;m++){
    const full=new Set(),partial=new Map();let count=0,collision=null;
    for(const g of multiset(m)){
      const key=sig(g,m);if(full.has(key))throw Error("full moment collision");full.add(key);count++;
      const short=sig(g,m-1);if(partial.has(short)&&!collision)collision=[partial.get(short).map(i=>rows[i]),g.map(i=>rows[i])];partial.set(short,g);
    }
    result.push({m,groups:count,distinctFull:full.size,distinctShort:partial.size,exampleShortCollision:collision});
  }
  return {rowDenominator:4,rows:rows.length,result};
}
console.log(JSON.stringify(momentCheck(),null,2));
