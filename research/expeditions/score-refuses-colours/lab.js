'use strict';
// Synthetic finite model, not a perceptual experiment.
function lab(){
  const pairs=[[0,1],[0,2],[0,3],[1,2],[1,3],[2,3]];
  let checks=0, assignments=0, configurations=0;
  const assert=(ok,msg)=>{checks++;if(!ok)throw Error(msg)};
  const canon=a=>{const m=new Map();return a.map(x=>{if(!m.has(x))m.set(x,m.size);return m.get(x)}).join("")};
  const partitions=[];
  function extend(a){if(a.length===4){partitions.push(a);return}for(let i=0;i<=Math.max(-1,...a)+1;i++)extend([...a,i])}
  extend([]);
  const falling=(q,b)=>{let n=1;for(let i=0;i<b;i++)n*=q-i;return n};
  const rows=[], examples={};
  for(let mask=0;mask<64;mask++){
    const edges=pairs.filter((_,i)=>(mask>>i)&1);
    const allowed=partitions.filter(a=>edges.every(([i,j])=>a[i]!==a[j]));
    const chi=Math.min(...allowed.map(a=>1+Math.max(...a)));
    for(let k=3;k<=6;k++){
      const q=k-2, possible=allowed.filter(a=>Math.max(...a)<q);
      const expected=k*(k-1)*possible.reduce((s,a)=>s+falling(q,1+Math.max(...a)),0);
      let count=0;const patterns=new Set(), eq=pairs.map(()=>0);
      // Independent enumeration: all labelled assignments to both anchors and four events.
      for(let v=0;v<k**6;v++){
        assignments++;
        let x=v,a=[];for(let i=0;i<6;i++){a.push(x%k);x=Math.floor(x/k)}
        if(a[0]===a[1]||a.slice(2).some(t=>t===a[0]||t===a[1])||edges.some(([i,j])=>a[i+2]===a[j+2]))continue;
        count++;const b=a.slice(2);patterns.add(canon(b));pairs.forEach(([i,j],p)=>{if(b[i]===b[j])eq[p]++});
      }
      configurations++;
      assert(count===expected,"labelled count");
      assert(patterns.size===possible.length&&possible.every(a=>patterns.has(a.join(""))),"partition set");
      const statuses=eq.map(e=>!count?"infeasible":e===count?"same":e===0?"different":"free");
      pairs.forEach(([i,j],p)=>{
        const hits=possible.filter(a=>a[i]===a[j]).length;
        assert(statuses[p]===(!possible.length?"infeasible":hits===possible.length?"same":hits===0?"different":"free"),"pair status");
        if(q>=chi+1&&!edges.some(([a,b])=>a===i&&b===j))assert(statuses[p]==="free","spare colour theorem");
      });
      rows.push({mask,k,count,patterns:patterns.size,forcedUnwritten:statuses.filter((s,p)=>!(mask>>p&1)&&(s==="same"||s==="different")).length});
      if(mask===0||mask===41)examples[`${mask}/${k}`]={count,patterns:patterns.size,statuses,chi};
    }
  }
  const summary=[3,4,5,6].map(k=>{const a=rows.filter(r=>r.k===k);return {k,feasible:a.filter(r=>r.count>0).length,implicit:a.filter(r=>r.forcedUnwritten>0).length}});
  return {checks,assignments,configurations,examples,summary};
}
console.log(JSON.stringify(lab(), null, 2));
