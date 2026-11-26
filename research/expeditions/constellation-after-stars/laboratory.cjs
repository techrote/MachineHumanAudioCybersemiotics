"use strict";
// Standalone finite synthetic oracle, no participant data.
function laboratory() {
  const n=12, full=(1<<n)-1;
  const pop=x=>{let k=0;while(x){x&=x-1;k++;}return k;};
  const mask=(a,d)=>(1<<a)|(1<<((a+d)%n))|(1<<((a+2*d)%n));
  const family=D=>[...new Set(Array.from({length:D},(_,i)=>i+1).flatMap(d=>Array.from({length:n},(_,a)=>mask(a,d))))];
  const choose=(n,k)=>{if(k<0||k>n)return 0;let v=1;for(let i=1;i<=k;i++)v=v*(n-i+1)/i;return Math.round(v);};
  let checks=0;const check=(x,msg)=>{checks++;if(!x)throw Error(msg);};
  const totals=[];
  for(let D=1;D<=5;D++){
    const F=family(D), rows=[];
    for(let k=0;k<=n;k++){
      let total=0, fixed=0, any=0, hits=0,max=0,dist={};
      for(let s=0;s<=full;s++){
        if(pop(s)!==k)continue;
        total++;
        const h=F.filter(m=>(s&m)===m).length;
        const direct=new Set();
        for(let a=0;a<n;a++)for(let d=1;d<=D;d++){
          const b=(a+d)%n,c=(a+2*d)%n;
          if([a,b,c].every(x=>s&(1<<x)))direct.add([a,b,c].sort((x,y)=>x-y).join(","));
        }
        check(h===direct.size,"independent direct enumeration");
        const rot=((s<<1)&full)|(s>>(n-1));
        check(h===F.filter(m=>(rot&m)===m).length,"rotation invariance");
        fixed+=Number((s&mask(0,1))===mask(0,1));
        any+=Number(h>0);hits+=h;max=Math.max(max,h);dist[h]=(dist[h]||0)+1;
      }
      check(total===choose(n,k),"population cardinality");
      check(fixed===choose(n-3,k-3),"preselected pattern");
      check(hits===F.length*fixed,"double counted incidence");
      check(fixed<=any&&any<=hits,"union bounds");
      rows.push({k,total,fixed,any,hits,max,dist});
    }
    totals.push({D,motifs:F.length,rows});
  }
  const carrier=(1<<0)|(1<<3)|(1<<6)|(1<<10);
  check((carrier&mask(0,1))!==mask(0,1),"fixed test misses");
  check((carrier&mask(0,3))===mask(0,3),"scanned test finds");
  check(family(5).length===52,"duplicate triple handling");
  return {n,checks,totals,witness:{pulses:[0,3,6,10],found:family(5).filter(m=>(carrier&m)===m).map(m=>Array.from({length:n},(_,i)=>i).filter(i=>m&(1<<i)))}};
}
console.log(JSON.stringify(laboratory(), null, 2));
