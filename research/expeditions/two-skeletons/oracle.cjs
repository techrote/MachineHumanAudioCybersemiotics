"use strict";
// Exact integer arithmetic; values are twice the mean at each edit.
function lab(){
  const check=(ok,msg)=>{if(!ok)throw new Error(msg);assertions++};
  let assertions=0;
  function matchings(xs){
    if(!xs.length)return [[]];
    const a=xs[0],rest=xs.slice(1);
    return rest.flatMap((b,i)=>matchings(rest.filter((_,j)=>i!==j)).map(t=>[[a,b],...t]));
  }
  function partners(n,edges){const p=Array(n);for(const [a,b] of edges){p[a]=b;p[b]=a}return p}
  function twiceMean(x,p){return x.map((v,i)=>v+x[p[i]])}
  function components(p,q){
    const seen=new Set(),sizes=[];
    for(let i=0;i<p.length;i++){if(seen.has(i))continue;const todo=[i];let size=0;
      while(todo.length){const j=todo.pop();if(seen.has(j))continue;seen.add(j);size++;todo.push(p[j],q[j]);}
      sizes.push(size);
    }return sizes;
  }
  const rows=[];
  for(const n of [2,4,6,8]){
    const ms=matchings(Array.from({length:n},(_,i)=>i)).map(e=>partners(n,e));
    let commuting=0,bases=0;
    for(const p of ms)for(const q of ms){
      let equal=true;
      for(let i=0;i<n;i++){
        const e=Array.from({length:n},(_,j)=>Number(i===j));
        const pq=twiceMean(twiceMean(e,p),q),qp=twiceMean(twiceMean(e,q),p);
        const same=pq.every((v,j)=>v===qp[j]);equal&&=same;
        check(pq.reduce((a,b)=>a+b,0)===4&&qp.reduce((a,b)=>a+b,0)===4,"mass");
        check(same===(q[p[i]]===p[q[i]]),"basis commutation");
        bases++;
      }
      check(equal===components(p,q).every(s=>s<=4),"cycle criterion");
      if(equal)commuting++;
    }
    rows.push({events:n,matchings:ms.length,orderedPairs:ms.length**2,commuting,bases});
  }
  const p=[1,0,3,2,5,4],q=[5,2,1,4,3,0],x=[1,0,0,0,0,0];
  const pq=twiceMean(twiceMean(x,p),q),qp=twiceMean(twiceMean(x,q),p);
  check(pq.join()==="1,1,1,0,0,1"&&qp.join()==="1,1,0,0,1,1","witness");
  return {rows,assertions,witness:{p,q,x,pThenQNumerators:pq,qThenPNumerators:qp,denominator:4}};
}
console.log(JSON.stringify(lab(), null, 2));
