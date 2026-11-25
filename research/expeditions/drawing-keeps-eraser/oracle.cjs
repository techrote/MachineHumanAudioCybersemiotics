'use strict';
// Finite synthetic oracle. No dependencies or empirical data.
function laboratory(){
  let checks=0,graphs=0,histories=0,orientations=0,valid=0,distinctScars=0;
  const check=(x,msg)=>{if(!x)throw Error(msg);checks++};
  const seq=n=>Array.from({length:n},(_,i)=>i);
  const perms=a=>a.length?a.flatMap((v,i)=>perms(a.filter((_,j)=>i!==j)).map(p=>[v,...p])):[[]];
  const key=x=>x.join(",");
  function scar(n,edges,order){
    const live=new Set(seq(n)),s=Array(n).fill(0);
    for(const v of order){for(const [a,b] of edges){if(a===v&&live.has(b)||b===v&&live.has(a))s[v]++}live.delete(v)}
    return s;
  }
  function peel(n,edges,scar){
    const alive=new Set(seq(n)),d=[...scar],bits=Array(edges.length).fill(-1);
    while(alive.size){
      if([...alive].some(v=>d[v]<0))return null;
      const z=[...alive].find(v=>d[v]===0);
      if(z===undefined)return null;
      for(let i=0;i<edges.length;i++){
        const [a,b]=edges[i];if(a===z&&alive.has(b)){bits[i]=1;d[b]--}
        else if(b===z&&alive.has(a)){bits[i]=0;d[a]--}
      }
      alive.delete(z);
    }
    return bits;
  }
  function topo(n,edges,bits){
    const incoming=Array(n).fill(0),adj=seq(n).map(()=>[]);
    edges.forEach(([a,b],i)=>{if(bits[i])[a,b]=[b,a];adj[a].push(b);incoming[b]++});
    const queue=seq(n).filter(i=>incoming[i]===0);let k=0;
    while(k<queue.length){for(const v of adj[queue[k++]])if(--incoming[v]===0)queue.push(v)}
    return k===n;
  }
  for(let n=1;n<=5;n++){
    const pairs=seq(n).flatMap(a=>seq(n).filter(b=>b>a).map(b=>[a,b])),orders=perms(seq(n));
    for(let g=0;g<2**pairs.length;g++){
      const edges=pairs.filter((_,i)=>g&(1<<i)),observed=new Map(),orientSet=new Set();graphs++;
      for(const p of orders){
        const s=scar(n,edges,p),rank=seq(n).map(v=>p.indexOf(v)),bits=edges.map(([a,b])=>Number(rank[b]<rank[a])),k=key(s),b=key(bits);
        check(s.reduce((a,b)=>a+b,0)===edges.length,"sum");check(key(peel(n,edges,s))===b,"peel");
        check(!observed.has(k)||observed.get(k)===b,"scar collision");observed.set(k,b);orientSet.add(b);histories++;
      }
      const feasible=new Set();
      for(let m=0;m<2**edges.length;m++){
        const bits=edges.map((_,i)=>Number(Boolean(m&(1<<i)))),s=Array(n).fill(0);edges.forEach(([a,b],i)=>s[bits[i]?b:a]++);
        const acyclic=topo(n,edges,bits);orientations++;
        check((peel(n,edges,s)!==null)===acyclic,"cyclic control");
        if(acyclic){valid++;feasible.add(key(bits));check(observed.get(key(s))===key(bits),"orientation coverage")}
      }
      check(feasible.size===orientSet.size&&orientSet.size===observed.size,"bijection");distinctScars+=observed.size;
    }
  }
  const p=[[0,1],[1,2]],a=scar(3,p,[0,2,1]),b=scar(3,p,[2,0,1]);
  check(key(a)==="1,0,1"&&key(a)===key(b),"ambiguous total order");
  check(key(scar(3,p,[0,1,2]))!==key(scar(3,p,[2,1,0])),"distinct labelled");
  check(key(scar(3,p,[0,1,2]).sort())===key(scar(3,p,[2,1,0]).sort()),"anonymous collision");
  check(peel(4,[[0,1],[1,2],[2,3],[0,3]],[1,1,1,1])===null,"cycle all ones");
  const cases=[[],[[0,1],[1,2],[2,3]],[[0,1],[1,2],[2,3],[0,3]],seq(4).flatMap(a=>seq(4).filter(b=>b>a).map(b=>[a,b]))];
  const counts=cases.map(e=>new Set(perms(seq(4)).map(p=>key(scar(4,e,p)))).size);
  check(key(counts)==="1,8,14,24","four graph witnesses");
  return {graphs,histories,orientations,valid,distinctScars,checks,counts};
}
console.log(JSON.stringify(laboratory(), null, 2));
