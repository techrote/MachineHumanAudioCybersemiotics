"use strict";
function frontier(){
  function* positions(n,m,lo=0,a=[]){if(!m){yield a;return}for(let i=lo;i<=n-m;i++)yield* positions(n,m-1,i+1,a.concat(i))}
  function* permutations(s){if(!s.length){yield "";return}for(let i=0;i<s.length;i++)for(const p of permutations(s.slice(0,i)+s.slice(i+1)))yield s[i]+p}
  const fact=n=>{let p=1;while(n>1)p*=n--;return p};
  function maxSize(m,n,k,c){const s=n-m-(c+1)*(k-1);if(s<0||c<1||c>m||(k===1&&c!==m))return 0;let p=1;for(let j=1;j<=c;j++)p*=s+j;return p}
  const check=(v,msg)=>{if(!v)throw Error(msg)};
  let words=0,groups=0,profiles=0,tradeoffProfiles=0,examples=[];
  for(let m=1;m<=4;m++)for(let n=m;n<=15;n++)for(let k=2;k<=5;k++){
    if(n<m+2*(k-1))continue;
    const map=new Map(),p=[...permutations("ABCD".slice(0,m))];
    for(const ps of positions(n-2*(k-1),m)){
      const c=1+ps.slice(1).filter((x,i)=>x-ps[i]>=k).length;
      for(const label of p){
        const w=Array(n).fill("0");ps.forEach((x,i)=>w[x+k-1]=label[i]);const windows=[];
        for(let i=0;i<=n-k;i++)windows.push(w.slice(i,i+k).join(""));
        const key=windows.sort().join("|");
        if(!map.has(key))map.set(key,{c,count:0});
        const g=map.get(key);check(g.c===c,"cluster inconsistency");g.count++;words++
      }
    }
    const maxima=Array(m+1).fill(0);
    for(const g of map.values())maxima[g.c]=Math.max(maxima[g.c],g.count);
    for(let c=1;c<=m;c++)check(maxima[c]===maxSize(m,n,k,c),"frontier discrepancy");
    const possible=maxima.map((x,c)=>({c,words:x,orders:fact(c)})).filter(x=>x.c&&x.words);
    const best=Math.max(...maxima);
    if(possible.at(-1).words<best)tradeoffProfiles++;
    if(m===3&&k===4&&(n===12||n===15))examples.push({m,n,k,possible});
    groups+=map.size;profiles++
  }
  return {words,groups,profiles,tradeoffProfiles,examples,assertion_failures:0}
}
if(typeof module!=="undefined")module.exports={frontier};
if(typeof require!=="undefined"&&require.main===module) console.log(JSON.stringify(frontier(),null,2));
