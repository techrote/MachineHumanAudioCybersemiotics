function greedy(signs,B){
  let x=0,resets=[],states=[];
  for(let i=0;i<signs.length;i++){
    if(Math.abs(x+signs[i])>B){resets.push(i);x=0;}
    x+=signs[i];states.push(x);
  }
  return {cost:resets.length,resets,states};
}

function optimal(signs,B){
  let states=new Map([[0,{cost:0,resets:[],states:[]}]]);
  for(let i=0;i<signs.length;i++){
    const next=new Map();
    for(const [x,p] of states) for(const reset of [false,true]){
      if(reset&&x===0)continue;
      const y=(reset?0:x)+signs[i];
      if(Math.abs(y)>B)continue;
      const q={cost:p.cost+Number(reset),resets:reset?[...p.resets,i]:p.resets,states:[...p.states,y]};
      if(!next.has(y)||q.cost<next.get(y).cost)next.set(y,q);
    }
    states=next;
  }
  return [...states.values()].reduce((a,b)=>a.cost<=b.cost?a:b);
}

function brute(signs,B){
  let best=Infinity;
  for(let mask=0;mask<2**signs.length;mask++){
    let x=0,cost=0,ok=true;
    for(let i=0;i<signs.length;i++){
      if(mask&(1<<i)){x=0;cost++;}
      if(cost>=best){ok=false;break;}
      x+=signs[i];if(Math.abs(x)>B){ok=false;break;}
    }
    if(ok)best=cost;
  }
  return best;
}

function check(){
  let checks=0;const assert=(v)=>{if(!v)throw Error("failed check "+checks);checks++;};
  const rows=[];
  for(let B=1;B<=4;B++){
    let sequences=0,worse=0,regret=0,first=null;
    for(let n=0;n<=10;n++)for(let mask=0;mask<2**n;mask++){
      const signs=Array.from({length:n},(_,i)=>mask&(1<<i)?1:-1);
      const g=greedy(signs,B),o=optimal(signs,B);
      sequences++;
      assert(o.cost===brute(signs,B));
      assert(g.cost>=o.cost);
      for(const p of [g,o]){
        let x=0;
        for(let i=0;i<n;i++){
          if(p.resets.includes(i))x=0;
          x+=signs[i];assert(x===p.states[i]&&Math.abs(x)<=B);
        }
        assert(p.cost===p.resets.length);
      }
      if(g.cost>o.cost){worse++;regret=Math.max(regret,g.cost-o.cost);if(!first)first={signs,greedy:g,optimal:o};}
      if(B===1)assert(g.cost===o.cost);
    }
    rows.push({B,sequences,worse,regret,first});
  }
  for(let B=2;B<=32;B++){
    const signs=[...Array(B+1).fill(-1),...Array(B+2).fill(1)];
    assert(greedy(signs,B).cost===2);
    assert(optimal(signs,B).cost===1);
  }
  const witness=[-1,-1,-1,1,1,1,1];
  return {checks,rows,witness:{signs:witness,greedy:greedy(witness,2),optimal:optimal(witness,2)}};
}

console.log(JSON.stringify(check(),null,2));
