"use strict";
function experiment(){
  const assert=(ok,msg)=>{if(!ok)throw Error(msg);checks++};
  let checks=0, cases=0, allocations=0, residueVisits=0;
  const mod=(x,m)=>((x%m)+m)%m;
  function* compositions(t,n,p=[]){if(n===1){yield [...p,t];return}for(let j=0;j<=t;j++)yield* compositions(t-j,n-1,[...p,j])}
  function pitches(g,m){let s=0;return g.map(t=>s=(s+t)%m)}
  function counts(m,n,T){let a=[1];for(let i=0;i<n;i++){let b=Array(a.length+m-1).fill(0);for(let j=0;j<a.length;j++)for(let r=0;r<m;r++)b[j+r]+=a[j];a=b}return a.reduce((v,c,s)=>v+(s<=T&&mod(s-T,m)===0?c:0),0)}
  function* residues(m,n,p=[]){if(n===0){yield p;return}for(let j=0;j<m;j++)yield* residues(m,n-1,[...p,j])}
  const rows=[];
  for(let m=2;m<=7;m++)for(let n=1;n<=5;n++)for(let T=0;T<=Math.min(24,(n-1)*(m-1)+m);T++){
    const actual=new Set();
    for(const g of compositions(T,n)){allocations++;const p=pitches(g,m);assert(p.at(-1)===T%m,"endpoint");actual.add(p.join(","))}
    let count=0;
    for(const pre of residues(m,n-1)){residueVisits++;const r=[...pre,mod(T-pre.reduce((a,b)=>a+b,0),m)];const sum=r.reduce((a,b)=>a+b,0);const reachable=sum<=T;const key=pitches(r,m).join(",");assert(actual.has(key)===reachable,"residue witness");if(reachable)count++}
    assert(count===actual.size,"witness count");assert(counts(m,n,T)===count,"coefficient formula");
    const largest=n*(m-1)-mod(n*(m-1)-T,m);
    assert((count===m**(n-1))===(T>=largest),"sharp residue threshold");
    if(T>=(n-1)*(m-1))assert(count===m**(n-1),"uniform saturation");
    if(n>1&&T===(n-1)*(m-1)-1)assert(count<m**(n-1),"sharp previous tick");
    cases++;
    if(m===5&&n===4)rows.push({T,count,endpoint:T%m});
  }
  return {cases,allocations,residueVisits,checks,rows};
}
console.log(JSON.stringify(experiment(), null, 2));
