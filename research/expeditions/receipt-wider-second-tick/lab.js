'use strict';
// Synthetic finite checks; run node lab.js.
function laboratory(){
 const assert=(x,m)=>{if(!x)throw Error(m)};
 const N=5, V=Array.from({length:N},(_,i)=>i), edges=V.map(i=>[i,(i+1)%N]);
 const maps=edges.map(([u,v])=>V.map(x=>x===v?u:x));
 const states=V.flatMap(x=>V.map(y=>[x,y]));
 const contexts=maps.flatMap((_,i)=>maps.map((_,j)=>[i,j]));
 const obs=([x,y],[a,b])=>[maps[a][x],maps[b][y]].join(",");
 const adj=(x,y)=>x===y||(x-y+5)%5===1||(y-x+5)%5===1;
 const graph=(rows,cs)=>rows.map((u,i)=>rows.map((v,j)=>i!==j&&cs.some(c=>obs(u,c)===obs(v,c))));
 let graphChecks=0,searchNodes=0,decoderChecks=0,partitionChecks=0;
 const full=graph(states,contexts);
 for(let i=0;i<25;i++)for(let j=0;j<25;j++){
   const [a,b]=states[i],[c,d]=states[j];
   assert(full[i][j]===(i!==j&&adj(a,c)&&adj(b,d)),"strong product");
   graphChecks++;
 }
 function colour(g,k){
   const n=g.length, c=Array(n).fill(-1);
   function rec(done,used){
     searchNodes++;
     if(done===n)return c.slice();
     let at=-1, sat=-1, degree=-1;
     for(let i=0;i<n;i++)if(c[i]<0){
       const s=new Set(c.filter((v,j)=>v>=0&&g[i][j])).size,d=g[i].filter(Boolean).length;
       if(s>sat||(s===sat&&d>degree)){at=i;sat=s;degree=d;}
     }
     for(let v=0;v<Math.min(k,used+1);v++){
       if(c.some((u,j)=>u===v&&g[at][j]))continue;
       c[at]=v;const res=rec(done+1,Math.max(used,v+1));if(res)return res;c[at]=-1;
     }
     return null;
   }
   return rec(0,0);
 }
 function exact(g){for(let k=1;k<=g.length;k++){const tags=colour(g,k);if(tags)return {k,tags};}throw Error("no colour");}
 function decodeCheck(rows,cs,tags){
   for(const context of cs){
     const seen=new Set();
     for(let i=0;i<rows.length;i++){
       const key=obs(rows[i],context)+":"+tags[i];
       assert(!seen.has(key),"decoder collision");seen.add(key);decoderChecks++;
     }
   }
 }
 const fullTags=states.map(([x,y])=>(x+2*y)%5);
 decodeCheck(states,contexts,fullTags);
 assert(exact(full).k===5,"offline optimum");
 const costs={};
 for(let mask=1;mask<32;mask++){
   const B=V.filter(x=>mask>>x&1), rows=states.filter(([x])=>B.includes(x));
   const g=graph(rows,contexts), optimum=exact(g);
   const hasEdge=edges.some(([x,y])=>B.includes(x)&&B.includes(y));
   assert(optimum.k===(hasEdge?5:3),"branch cost");
   decodeCheck(rows,contexts,optimum.tags);
   costs[mask]=optimum.k;
 }
 const partitions=[];
 function part(i,blocks){
   if(i===5){partitions.push(blocks.slice());return;}
   for(let j=0;j<blocks.length;j++){blocks[j]|=1<<i;part(i+1,blocks);blocks[j]^=1<<i;}
   blocks.push(1<<i);part(i+1,blocks);blocks.pop();
 }
 part(0,[]);
 assert(partitions.length===52,"Bell number");
 const table=[];
 for(let first=1;first<=5;first++)for(let second=1;second<=6;second++){
   let best=Infinity, nonconstant=Infinity;
   for(const p of partitions){
     partitionChecks++;
     if(p.length>first||p.some(b=>costs[b]>second))continue;
     const cost=p.reduce((a,b)=>a+costs[b],0);
     best=Math.min(best,cost);
     if(p.length>1)nonconstant=Math.min(nonconstant,cost);
   }
   const expected=second>=5?5:second>=3&&first>=3?9:Infinity;
   assert(best===expected,"capacity table");
   if(first>=2&&second>=5)assert(nonconstant===8,"nonconstant optimum");
   table.push([first,second,Number.isFinite(best)?best:null]);
 }
 const shared=maps.map((_,i)=>[i,i]), sharedGraph=graph(states,shared), sharedOpt=exact(sharedGraph);
 decodeCheck(states,shared,sharedOpt.tags);
 let sharedRemoved=0;
 for(let i=0;i<25;i++)for(let j=0;j<25;j++){
   assert(!sharedGraph[i][j]||full[i][j],"shared support subset");
   if(full[i][j]&&!sharedGraph[i][j])sharedRemoved++;
 }
 assert(sharedRemoved>0,"support negative control");
 const scalar=[0,1,0,1,2], scalarGraph=V.map(i=>V.map(j=>i!==j&&adj(i,j)));
 assert(exact(scalarGraph).k===3,"scalar optimum");
 decodeCheck(states,contexts,states.map(([x,y])=>scalar[x]*3+scalar[y]));
 // Offline can spread the five block colours across a 2-by-3 alphabet,
 // but the first digit then varies with the not-yet-revealed second source.
 const offlineFirst=states.map(([x,y])=>Math.floor(((x+2*y)%5)/3));
 const witnesses=V.filter(x=>new Set(states.filter(s=>s[0]===x).map(([a,b])=>Math.floor(((a+2*b)%5)/3))).size>1);
 assert(witnesses.length===5,"preview witness");
 assert(offlineFirst.every(x=>x===0||x===1),"offline first cap");
 return {graphChecks,searchNodes,decoderChecks,partitionChecks,partitions:partitions.length,branchGraphs:31,sharedOpt:sharedOpt.k,sharedRemovedDirectedEdges:sharedRemoved,previewWitnesses:witnesses.length,table};
}
console.log(JSON.stringify(laboratory(),null,2));
