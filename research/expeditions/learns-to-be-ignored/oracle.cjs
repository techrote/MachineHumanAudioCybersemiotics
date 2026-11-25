"use strict";
// Synthetic binary transition masks; no model of human perception.
function oracle(){
  function pop(x){let k=0;while(x){x&=x-1;k++}return k}
  function choose(n,k){if(k<0||k>n)return 0;let v=1;for(let i=1;i<=k;i++)v=v*(n-i+1)/i;return v}
  let assertions=0,pairs=0,groups=0,budgets=0;
  function check(ok,msg){assertions++;if(!ok)throw Error(msg)}
  for(let n=0;n<=8;n++){
    const m=1<<n, fibers=new Map(),frontiers=new Map();
    for(let a=0;a<m;a++)for(let o=0;o<m;o++){
      pairs++;
      const s=pop(a),k=pop(o),u=a|o,h=pop(u),f=pop(o&~a);
      check(h===s+f,"union accounting");
      check(f>=Math.max(0,k-s)&&f<=Math.min(k,n-s),"bounds");
      const key=[s,k,u].join(",");
      if(!fibers.has(key))fibers.set(key,{count:0,states:new Set()});
      const g=fibers.get(key);g.count++;g.states.add(a);
      const budget=[s,k].join(",");
      if(!frontiers.has(budget))frontiers.set(budget,new Set());
      frontiers.get(budget).add(f);
    }
    for(const [key,g] of fibers){
      groups++;
      const [s,k,u]=key.split(",").map(Number),h=pop(u);
      check(g.states.size===choose(h,s),"state masks per trace");
      check(g.count===choose(h,s)*choose(s,s+k-h),"joint histories per trace");
    }
    for(let s=0;s<=n;s++)for(let k=0;k<=n;k++){
      budgets++;
      const fs=frontiers.get([s,k].join(","));
      for(let f=0;f<=n;f++)check(fs.has(f)===(f>=Math.max(0,k-s)&&f<=Math.min(k,n-s)),"sharp frontier");
      for(let u=0;u<m;u++){
        const h=pop(u);
        check(fibers.has([s,k,u].join(","))===(h>=Math.max(s,k)&&h<=Math.min(n,s+k)),"trace feasibility");
      }
    }
  }
  return {pairs,groups,budgets,assertions};
}
console.log(JSON.stringify(oracle(), null, 2));
