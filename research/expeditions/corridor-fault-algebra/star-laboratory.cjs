"use strict";
function starLab(){
 const range=n=>Array.from({length:n},(_,i)=>i);
 const pairs=a=>a.flatMap((x,i)=>a.slice(i+1).map(y=>[x,y]));
 const pop=x=>x?1+pop(x&(x-1)):0;
 let graphs=0,states=0,nonbipartite=0,ambiguous=0,connectedBipartite=0;
 for(let n=3;n<=5;n++){
  const E=pairs(range(n));
  for(let mask=0;mask<1<<E.length;mask++){
   const P=E.filter((_,i)=>mask>>i&1);
   const color=Array(n).fill(-1);let comps=0, bip=[];
   for(let i=0;i<n;i++)if(color[i]===-1){
    comps++;const q=[i],sizes=[1,0];color[i]=0;let ok=true;
    for(let j=0;j<q.length;j++)for(const [a,b] of P){
     const u=q[j]===a?b:q[j]===b?a:-1;if(u<0)continue;
     if(color[u]===-1){color[u]=1-color[q[j]];sizes[color[u]]++;q.push(u)}
     else if(color[u]===color[q[j]])ok=false;
    }
    if(ok)bip.push(sizes);
   }
   const M=new Map();
   for(let f=0;f<1<<n;f++){
    const rec=P.map(([a,b])=>((f>>a)&1)+((f>>b)&1)).join(",");
    if(!M.has(rec))M.set(rec,[]);M.get(rec).push(pop(f));states++;
   }
   const actual=Math.min(...[...M.values()].filter(x=>x.length>1).map(x=>x.sort((a,b)=>a-b)[1]));
   const predicted=Math.min(...bip.map(x=>Math.max(...x)));
   if(actual!==predicted)throw Error("sparse star threshold");
   if(bip.length===0){nonbipartite++;if(M.size!==1<<n)throw Error("star rank")}
   else ambiguous++;
   if(comps===1&&bip.length===1){connectedBipartite++;if([...M.values()].filter(x=>x.length>1).length!==1)throw Error("connected bipartite fibre")}
   graphs++;
  }
 }
 return {graphs,states,nonbipartite,ambiguous,connectedBipartite};
}
console.log(JSON.stringify(starLab(), null, 2));
