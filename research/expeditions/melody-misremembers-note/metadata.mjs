// MHAC #292: multiple deletion metadata census. All cases synthetic.
function multicheck(){
  const ck=(v,s)=>{if(!v)throw Error(s)};
  const fact=n=>n<2?1:n*fact(n-1);
  const choose=(n,k)=>fact(n)/(fact(k)*fact(n-k));
  const range=n=>Array.from({length:n},(_,i)=>i+1);
  function* perms(a){if(!a.length){yield [];return;}for(let i=0;i<a.length;i++)for(const p of perms(a.filter((_,j)=>i!==j)))yield [a[i],...p];}
  function* subsets(a,k){if(k===0){yield [];return;}for(let i=0;i<=a.length-k;i++)for(const s of subsets(a.slice(i+1),k-1))yield [a[i],...s];}
  const key=a=>a.join(",");
  const standard=a=>a.map(v=>a.slice().sort((x,y)=>x-y).indexOf(v)+1);
  const rows=[];
  for(let n=2;n<=7;n++)for(let k=1;k<n&&k<=3;k++){
    const both=new Map(), positions=new Map(), ranks=new Map(), qcounts=new Map();
    let events=0;
    for(const p of perms(range(n)))for(const I of subsets(range(n),k)){
      const R=I.map(i=>p[i-1]).sort((a,b)=>a-b);
      const q=standard(p.filter((_,i)=>!I.includes(i+1)));
      const qk=key(q), ik=key(I), rk=key(R);
      for(const [map,x] of [[both,qk+"|"+ik+"|"+rk],[positions,qk+"|"+ik],[ranks,qk+"|"+rk],[qcounts,qk]])map.set(x,(map.get(x)||0)+1);
      events++;
    }
    const c=choose(n,k), f=fact(k), obs=fact(n-k);
    ck(both.size===obs*c*c&&[...both.values()].every(x=>x===f),"both sets");
    ck(positions.size===obs*c&&[...positions.values()].every(x=>x===c*f),"positions");
    ck(ranks.size===obs*c&&[...ranks.values()].every(x=>x===c*f),"ranks");
    ck(qcounts.size===obs&&[...qcounts.values()].every(x=>x===c*c*f),"rank-only events");
    // With either set fixed, every contributing event is a distinct parent:
    // for fixed positions deletion is deterministic; for fixed deleted ranks likewise.
    rows.push({n,k,events,observations:obs,bothSetCells:both.size,oneSetParents:c*f,bothSetParents:f,rankOnlyEvents:c*c*f});
  }
  return {rows,totalEvents:rows.reduce((s,x)=>s+x.events,0),assertions:"all passed"};
}
console.log(JSON.stringify(multicheck(),null,2));
