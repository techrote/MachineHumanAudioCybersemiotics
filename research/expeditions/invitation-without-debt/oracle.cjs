// Synthetic finite oracle. No human behavioural model.
function audit() {
  let histories=0, traces=0, checks=0;
  const assert=(condition,msg)=>{checks++;if(!condition)throw Error(msg)};
  const factorial=n=>n===0?1:n*factorial(n-1);
  const examples=[];
  for (const [m,maxN] of [[2,8],[3,6]]) {
    for(let n=0;n<=maxN;n++){
      const census=new Map();
      function walk(t,counts,trace){
        if(t===n){
          histories++;
          const k=trace.join(","), h=counts.join(",");
          if(!census.has(k))census.set(k,new Map());
          const group=census.get(k); group.set(h,(group.get(h)||0)+1);
          return;
        }
        for(let a=0;a<m;a++){
          counts[a]++;
          for(const heard of [-1,a]){trace.push(heard);walk(t+1,counts,trace);trace.pop()}
          counts[a]--;
        }
      }
      walk(0,Array(m).fill(0),[]);
      for(const [key,group] of census){
        traces++;
        const seq=key===""?[]:key.split(",").map(Number);
        const r=Array(m).fill(0);let s=0;
        for(const a of seq){if(a===-1)s++;else r[a]++}
        assert([...group.values()].reduce((a,b)=>a+b,0)===m**s,"history count");
        function compositions(left,parts){
          if(parts.length===m-1){
            const d=[...parts,left];
            const h=d.map((v,i)=>v+r[i]).join(",");
            const predicted=factorial(s)/d.reduce((a,b)=>a*factorial(b),1);
            assert(group.get(h)===predicted,"multinomial multiplicity");
            return 1;
          }
          let k=0;for(let j=0;j<=left;j++)k+=compositions(left-j,[...parts,j]);return k;
        }
        assert(group.size===compositions(s,[]),"no additional allocations");
        if(n%m===0){
          const q=n/m, possible=r.every(a=>a<=q);
          assert(group.has(Array(m).fill(q).join(","))===possible,"balanced offer feasibility");
        }
        if(m===2){
          const diffs=[...group.keys()].map(h=>{const [a,b]=h.split(",").map(Number);return a-b});
          assert(Math.min(...diffs)===r[0]-r[1]-s && Math.max(...diffs)===r[0]-r[1]+s,"sharp signed disparity");
        }
        if(m===2&&n===8&&key==="0,1,-1,-1,-1,-1,-1,-1")examples.push({trace:key,allocations:[...group]});
      }
    }
  }
  return {histories,traces,checks,examples};
}
console.log(JSON.stringify(audit(),null,2));
