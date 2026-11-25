// Synthetic finite interval-partition oracle; no participant data.
function laboratory(){
  const stats={open:0,cyclic:0,forest:0,unicycle:0,integerFlex:0,checks:0};
  function check(x,msg){if(!x)throw Error(msg);stats.checks++}
  function analyze(n,A,B,cyclic){
    const starts=cyclic?[...new Set([...A,...B])].sort((a,b)=>a-b):[0,...new Set([...A,...B])].sort((a,b)=>a-b);
    const aa=cyclic?A:[0,...A],bb=cyclic?B:[0,...B];
    function owner(c,t){let k=c.findLastIndex(v=>v<=t);return k<0?c.length-1:k}
    const edges=starts.map((t,i)=>({u:owner(aa,t),v:aa.length+owner(bb,t),w:(starts[i+1]??(cyclic?starts[0]+n:n))-t}));
    const N=aa.length+bb.length;
    const parent=Array.from({length:N},(_,i)=>i);
    function root(i){while(parent[i]!==i)i=parent[i];return i}
    for(const {u,v} of edges)parent[root(u)]=root(v);
    const components=new Set(parent.map((_,i)=>root(i))).size;
    const shared=A.filter(t=>B.includes(t)).length;
    check(edges.every(e=>e.w>0),"positive overlap");
    check(edges.reduce((s,e)=>s+e.w,0)===n,"length");
    check(edges.length===N-(cyclic?0:1)-shared,"edge count");
    check(components===(cyclic?Math.max(1,shared):shared+1),"components");
    const rank=edges.length-N+components;
    check(rank===(cyclic&&shared===0?1:0),"cycle rank");
    // Independent marginal computation by per-slot ownership.
    const margins=Array(N).fill(0);
    for(let t=0;t<n;t++){margins[owner(aa,t)]++;margins[aa.length+owner(bb,t)]++}
    const pending=edges.map((_,i)=>i),res=margins.slice();
    const recovered=Array(edges.length).fill(null);
    // Peel leaves using only topology and marginal totals.
    while(pending.length){
      const incidence=Array.from({length:N},()=>[]);
      for(const i of pending){incidence[edges[i].u].push(i);incidence[edges[i].v].push(i)}
      const leaf=incidence.findIndex(a=>a.length===1);
      if(leaf<0)break;
      const i=incidence[leaf][0],e=edges[i],w=res[leaf];
      recovered[i]=w;
      check(w===e.w,"leaf reconstruction");
      res[e.u]-=w;res[e.v]-=w;pending.splice(pending.indexOf(i),1);
    }
    if(rank===0){
      stats.forest++;
      check(pending.length===0&&res.every(x=>x===0),"forest resolved");
    }else{
      stats.unicycle++;
      check(pending.length>=2&&pending.length%2===0,"even core");
      const signs=new Map([[pending[0],1]]);
      while(signs.size<pending.length){
        let progress=false;
        for(const i of pending)if(!signs.has(i)){
          const e=edges[i],j=[...signs.keys()].find(j=>[edges[j].u,edges[j].v].some(v=>v===e.u||v===e.v));
          if(j!==undefined){signs.set(i,-signs.get(j));progress=true}
        }
        if(!progress)throw Error("disconnected core");
      }
      const delta=Array(N).fill(0);
      for(const [i,s] of signs){delta[edges[i].u]+=s;delta[edges[i].v]+=s}
      check(delta.every(x=>x===0),"alternating kernel");
      const low=1-Math.min(...pending.filter(i=>signs.get(i)===1).map(i=>edges[i].w));
      const high=Math.min(...pending.filter(i=>signs.get(i)===-1).map(i=>edges[i].w))-1;
      check(low<=0&&high>=0,"positive integer interval");
      if(high>low)stats.integerFlex++;
      for(let d=low;d<=high;d++){
        const m=Array(N).fill(0);
        edges.forEach((e,i)=>{const w=e.w+d*(signs.get(i)??0);check(w>0,"perturbed positive");m[e.u]+=w;m[e.v]+=w});
        check(m.every((v,i)=>v===margins[i]),"perturbed margins");
      }
    }
    return {edges,margins,components,rank};
  }
  for(let n=1;n<=8;n++){
    const subsets=(count,offset)=>Array.from({length:2**count},(_,m)=>Array.from({length:count},(_,i)=>i+offset).filter((_,i)=>m&(1<<i)));
    const op=subsets(n-1,1),cy=subsets(n,0).slice(1);
    for(const A of op)for(const B of op){stats.open++;analyze(n,A,B,false)}
    for(const A of cy)for(const B of cy){stats.cyclic++;analyze(n,A,B,true)}
  }
  const witnesses=[1,2,3].map(x=>analyze(8,[0,4],[x,x+4],true));
  check(witnesses.every(w=>w.margins.join()==="4,4,4,4"&&w.rank===1),"offset witness");
  const aligned=analyze(8,[0,4],[0,4],true);
  check(aligned.rank===0&&aligned.components===2,"aligned control");
  const parallel=analyze(4,[0],[2],true);
  check(parallel.edges.length===2&&parallel.rank===1,"parallel edge control");
  return {stats,witnesses,aligned,parallel};
}
console.log(JSON.stringify(laboratory(), null, 2));
