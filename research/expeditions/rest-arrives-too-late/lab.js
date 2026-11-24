// Dependency-free synthetic expedition; run with node lab.js.
function run(){
  "use strict";
  const assert=(v,msg)=>{if(!v)throw Error(msg)};
  const weight=m=>{let k=0;for(;m;m&=m-1)k++;return k};
  const syndrome=(h,m)=>h.reduce((s,c,i)=>s^((m>>i&1)?c:0),0);
  const all=n=>Array.from({length:2**n},(_,i)=>i);
  const span=h=>{let s=new Set([0]);for(const c of h)for(const v of [...s])s.add(v^c);return s};
  const select=(h,m)=>h.filter((_,i)=>m>>i&1);
  const verify=(h,b)=>{if(!Array.isArray(h)||h.length<1||h.length>20||h.some(x=>!Number.isInteger(x)||x<0||x>=2**20)||!Number.isInteger(b)||b<0||!span(h).has(b))throw Error("invalid or infeasible bounded model")};
  function plan(h,b){
    verify(h,b);
    let dp=new Map([[0,0]]);
    for(let i=0;i<h.length;i++){
      const next=new Map(dp);
      for(const [s,m] of dp){
        const v=s^h[i], z=m|1<<i;
        if(!next.has(v)||weight(z)<weight(next.get(v)))next.set(v,z);
      }
      dp=next;
    }
    let rev=new Map([[0,0]]), pivots=0;
    for(let i=h.length-1;i>=0;i--)if(!rev.has(h[i])){
      pivots|=1<<i;
      for(const [s,m] of [...rev])rev.set(s^h[i],m|1<<i);
    }
    return {eventual:dp.get(b),immediate:rev.get(b),pivots};
  }
  function deadline(h,E,i,d){
    const unknown=h.filter((_,j)=>j!==i&&((E>>j&1)||j>d));
    return !(E>>i&1)||!span(unknown).has(h[i]);
  }
  const counts={matrices:0,sourceCosets:0,masks:0,deadlineChecks:0,optima:0,groupLawChecks:0,transcripts:0,gapExamples:0,refusals:0};
  function census(r,n){
    const limit=2**(r*n), words=all(n), full=(1<<n)-1;
    for(let index=0;index<limit;index++){
      const h=Array.from({length:n},(_,i)=>index>>(r*i)&((1<<r)-1));
      const cosets=new Map();
      for(const x of words){const b=syndrome(h,x);if(!cosets.has(b))cosets.set(b,[]);cosets.get(b).push(x)}
      counts.matrices++;
      for(const [b,C] of cosets){
        counts.sourceCosets++;
        let best=Infinity;
        const p=plan(h,b);
        for(const E of words){
          const K=full^E, P=new Set(C.map(x=>x&K));
          const privateSupport=P.has(0);
          const recover=P.size===C.length;
          assert(privateSupport===span(select(h,E)).has(b),"privacy support");
          assert(recover===(span(select(h,E)).size===2**weight(E)),"erasure recovery");
          let ontime=true;
          for(let i=0;i<n;i++)if(E>>i&1)for(let d=i;d<n;d++){
            const observed=K&((1<<(d+1))-1), map=new Map();let direct=true;
            for(const x of C){const key=x&observed,v=x>>i&1;if(map.has(key)&&map.get(key)!==v)direct=false;map.set(key,v)}
            assert(direct===deadline(h,E,i,d),"deadline");
            if(d===i&&!direct)ontime=false;
            counts.deadlineChecks++;
          }
          if(privateSupport&&recover)best=Math.min(best,weight(E));
          const predicted=(E&p.immediate)===p.immediate&&(E&p.pivots)===E;
          assert((privateSupport&&ontime)===predicted,"immediate feasible family");
          counts.masks++;
        }
        assert(weight(p.eventual)===best&&syndrome(h,p.eventual)===b,"eventual optimum");
        assert(syndrome(h,p.immediate)===b,"immediate optimum");
        counts.optima+=2;
      }
    }
  }
  for(let n=1;n<=5;n++)census(2,n);
  for(let n=1;n<=4;n++)census(3,n);
  function witness(h,b,E,G){
    const C=all(h.length).filter(x=>syndrome(h,x)===b);
    const K=(1<<h.length)-1^E, P=[...new Set(C.map(x=>x&K))];
    assert(P.includes(0),"witness infeasible");
    let baseline;
    for(let g=0;g<G;g++){
      const other=Array.from({length:G},(_,i)=>i).filter(i=>i!==g);
      const dependent=other.pop(), law=new Map();
      for(const x of C){
        const rows=Array(G).fill(0);rows[g]=x&K;
        function visit(j){
          if(j<other.length){for(const y of P){rows[other[j]]=y;visit(j+1)}return}
          rows[dependent]=rows.reduce((s,v,i)=>s^(i===dependent?0:v),0);
          assert(P.includes(rows[dependent]),"closure");
          assert(rows.reduce((s,v)=>s^v,0)===0&&rows[g]===(x&K),"exact rows");
          const key=rows.join(",");law.set(key,(law.get(key)||0)+1);counts.transcripts++;
        }
        visit(0);
      }
      if(!baseline)baseline=law;
      else {assert(law.size===baseline.size&&[...law].every(([k,v])=>baseline.get(k)===v),"exact common law");counts.groupLawChecks++}
    }
  }
  for(const h of [[1,1,1],[3,1,2],[0,1,2],[1,2,3,1],[0,0,0]]){
    for(const b of span(h)){
      const p=plan(h,b);
      for(const E of new Set([p.eventual,p.immediate]))for(const G of [3,5])witness(h,b,E,G);
    }
  }
  for(let r=1;r<=15;r++){
    const b=(1<<r)-1,h=[b,...Array.from({length:r},(_,i)=>1<<i)];
    const p=plan(h,b);
    assert(weight(p.eventual)===1&&syndrome(h,p.eventual)===b,"gap eventual");
    assert(weight(p.immediate)===r,"gap immediate");
    assert(deadline(h,1,0,1)&&!deadline(h,1,0,0),"gap one tick delay");
    counts.gapExamples++;
  }
  for(const [h,b] of [[[],0],[[1],2],[[1.5],0],[[1],-1],[[2**20],0]]){
    let refused=false;try{plan(h,b)}catch{refused=true}assert(refused,"invalid input");counts.refusals++;
  }
  return counts;
}
console.log(JSON.stringify(run(), null, 2));
