"use strict";
// Standalone Node.js, no dependencies. All decisions are exact integers/strings.
const run = function laboratory(){
  "use strict";
  const assert=(v,msg)=>{if(!v)throw Error(msg);};
  const choose=(xs,k)=>k===0?[[]]:xs.flatMap((x,i)=>choose(xs.slice(i+1),k-1).map(y=>[x,...y]));
  const perms=xs=>xs.length===0?[[]]:xs.flatMap((x,i)=>perms(xs.filter((_,j)=>i!==j)).map(y=>[x,...y]));
  const range=n=>Array.from({length:n},(_,i)=>i);
  const proj=(p,S)=>p.filter(x=>S.includes(x)).join("");
  const sig=(p,Ms)=>Ms.map(S=>proj(p,S));
  const dist=(a,b)=>a.reduce((s,x,i)=>s+(x!==b[i]),0);
  const cover=(Ms,a,b)=>Ms.filter(S=>S.includes(a)&&S.includes(b)).length;
  const local=(Ms,p)=>Math.min(...p.slice(1).map((b,i)=>cover(Ms,p[i],b)));
  const global=(Ms,n)=>Math.min(...choose(range(n),2).map(([a,b])=>cover(Ms,a,b)));
  const swap=(p,i)=>{let q=p.slice();[q[i],q[i+1]]=[q[i+1],q[i]];return q;};
  const word=range(7),P=perms(word);
  const fano=range(7).map(i=>[i,(i+1)%7,(i+3)%7].sort((a,b)=>a-b));
  const fixed=[[0,1,2],[2,3,4],[4,5,6]];
  const replicate=(M,k)=>Array.from({length:k},()=>M).flat();
  const S=P.map(p=>sig(p,fano));
  assert(global(fano,7)===1,"Fano coverage");
  assert(new Set(S.map(x=>x.join("|"))).size===5040,"Fano injectivity");
  let adjacentChecks=0;
  for(let i=0;i<P.length;i++)for(let j=0;j<6;j++){
    assert(dist(S[i],sig(swap(P[i],j),fano))===1,"Fano adjacency");
    assert(dist(sig(P[i],replicate(fano,3)),sig(swap(P[i],j),replicate(fano,3)))===3,"triple replication");
    adjacentChecks+=2;
  }
  const erasures=[];
  for(let k=0;k<=7;k++){
    let hist={},max=0,unique=0,total=0;
    for(const erased of choose(range(7),k)){
      let active=range(7).filter(j=>!erased.includes(j)),groups=new Map();
      for(const row of S){const key=active.map(j=>row[j]).join("|");groups.set(key,(groups.get(key)||0)+1);}
      for(const m of groups.values()){hist[m]=(hist[m]||0)+m;total+=m;max=Math.max(max,m);if(m===1)unique++;}
    }
    erasures.push({erased:k,history_mask_cases:total,unique,worst_candidates:max,histogram:hist});
  }
  assert(JSON.stringify(erasures[1].histogram)===JSON.stringify({1:10080,2:20160,6:5040}),"one erasure census");
  let runChecks=0;
  for(let j=0;j<7;j++){
    const map=new Map(),act=range(7).filter(i=>i!==j);
    for(let i=0;i<P.length;i++){const key=act.map(l=>S[i][l]).join("|");map.set(key,(map.get(key)||0)+1);}
    for(let i=0;i<P.length;i++){
      let r=0,m=1;for(const x of [...P[i],-1]){
        if(fano[j].includes(x))r++;
        else{for(let z=2;z<=r;z++)m*=z;r=0;}
      }
      assert(m===map.get(act.map(l=>S[i][l]).join("|")),"run product");runChecks++;
    }
  }
  let state=8092026;
  const rand=n=>{state=(Math.imul(state,1664525)+1013904223)>>>0;return state%n;};
  const small=perms(range(5)), triples=choose(range(5),3), pairs=choose(range(5),2);
  let localChecks=0,graphChecks=0;
  for(let i=0;i<48;i++){
    let M=range(1+rand(12)).map(()=>triples[rand(triples.length)]);
    let signatures=small.map(p=>sig(p,M));
    let mn=Infinity;
    for(let u=0;u<small.length;u++){
      let d=Infinity;
      for(let v=0;v<small.length;v++)if(v!==u)d=Math.min(d,dist(signatures[u],signatures[v]));
      assert(d===local(M,small[u]),"local distance");mn=Math.min(mn,d);localChecks++;
    }
    assert(mn===global(M,5),"global distance");
    let E=pairs.filter(()=>rand(3)!==0);
    if(!E.length)E=[pairs[0]];
    let traces=small.map(p=>sig(p,E).join("|"));
    let dg=Infinity;
    for(let u=0;u<small.length;u++)for(let v=u+1;v<small.length;v++)if(traces[u]!==traces[v])dg=Math.min(dg,dist(signatures[u],signatures[v]));
    assert(dg===Math.min(...E.map(([a,b])=>cover(M,a,b))),"dependency distance");graphChecks++;
  }
  const fixedSig=sig(word,fixed);
  const fixedCandidates=P.filter(p=>dist(sig(p,fixed),fixedSig)===0);
  assert(fixedCandidates.length===1,"retrospective order");
  const fixedWorst=new Map();for(const p of P){const k=sig(p,fixed).join("|");fixedWorst.set(k,(fixedWorst.get(k)||0)+1);}
  const fixedHist={};for(const v of fixedWorst.values())fixedHist[v]=(fixedHist[v]||0)+v;
  const M=replicate(fano,3), SS=P.map(p=>sig(p,M));
  let decodes=0;
  for(let i=0;i<120;i++){
    const u=rand(P.length),y=SS[u].slice();
    if(i%2===0){let a=rand(M.length);y[a]="CORRUPTED";}
    else{let a=rand(M.length),b=(a+1+rand(M.length-1))%M.length;y[a]=null;y[b]=null;}
    const e=i%2===0?1:0;
    const candidates=SS.map((s,j)=>[s,j]).filter(([s])=>s.reduce((n,x,j)=>n+(y[j]!==null&&x!==y[j]),0)<=e).map(([,j])=>j);
    assert(candidates.length===1&&candidates[0]===u,"bounded fault decode");decodes++;
  }
  const p=word,q=swap(p,0),a=sig(p,fano),b=sig(q,fano);
  const changed=a.map((x,i)=>x!==b[i]?i:-1).filter(i=>i>=0);
  assert(changed.length===1,"single monitor collision");
  return {model:"distinct known events; exact subset projections; monitor-level faults; no physical or human results",fano,retrospective:fixed,permutations:P.length,adjacentChecks,runChecks,localChecks,graphChecks,decodes,erasures,retrospective_fixed_histogram:fixedHist,retrospective_fixed_worst:Math.max(...fixedWorst.values()),witness:{p,q,changed_monitor:changed[0],line:fano[changed[0]],p_projection:a[changed[0]],q_projection:b[changed[0]]}};
};
console.log(JSON.stringify(run(),null,2));
