"use strict";
function laboratory() {
  const assert=(p,s)=>{if(!p)throw Error(s)};
  function* combinations(n,k,start=0,a=[]){if(!k){yield a;return}for(let i=start;i<=n-k;i++)yield* combinations(n,k-1,i+1,[...a,i])}
  function* permutations(a,p=[]){if(!a.length){yield p;return}for(let i=0;i<a.length;i++)yield* permutations(a.filter((_,j)=>i!==j),[...p,a[i]])}
  const pop=x=>{let c=0;for(;x;x&=x-1)c++;return c};
  const profiles=[];
  for(let n=2;n<=5;n++){
    const points=[...combinations(7,n)],perm=[...permutations(Array.from({length:n},(_,i)=>i))];
    let cases=0,feasible=0,assignments=0,maskChecks=0,greedyChecks=0,disagreements=0,maxGap=0;
    for(const x of points)for(const y of points)for(let v=0;v<=4;v++){
      cases++;
      const allowed=x.map(a=>y.map(b=>Math.abs(a-b)<=v));
      const p=perm.filter(a=>a.every((j,i)=>allowed[i][j]));
      assert(Boolean(p.length)===allowed.every((row,i)=>row[i]),"sorted feasibility");
      if(!p.length)continue;
      feasible++;assignments+=p.length;
      const all=new Set(), sorted=new Set();
      for(let i=0;i<n;i++)for(let j=i+1;j<n;j++){
        const edge=(1<<i)|(1<<j);
        if(allowed[i][j]&&allowed[j][i])sorted.add(edge);
        if(p.some(a=>allowed[i][a[j]]&&allowed[j][a[i]]))all.add(edge);
      }
      const cover=(mask,edges)=>[...edges].every(e=>e&mask);
      let cs=n,cu=n;
      for(let mask=0;mask<1<<n;mask++){
        const selected=Array.from({length:n},(_,i)=>i).filter(i=>mask&(1<<i));
        const receipts=p.map(a=>selected.map(i=>a[i]).join(","));
        const cert=receipts.filter(s=>s===selected.join(",")).length===1;
        const universal=new Set(receipts).size===p.length;
        assert(cert===cover(mask,sorted),"sorted certificate");
        assert(universal===cover(mask,all),"universal certificate");
        if(cert)cs=Math.min(cs,pop(mask));
        if(universal)cu=Math.min(cu,pop(mask));
        maskChecks+=2;
      }
      let independent=0,available=(1<<n)-1;
      while(available){
        const bit=available&-available;independent++;available&=~bit;
        for(const edge of sorted)if(edge&bit)available&=~edge;
      }
      assert(cs===n-independent,"greedy sorted cover");greedyChecks++;
      if(cu>cs)disagreements++;
      maxGap=Math.max(maxGap,cu-cs);
      // Unit-separated integer grids: upper bound for both contracts.
      assert(cs<=n-Math.ceil(n/(v+1)),"sorted minimax bound");
      assert(cu<=n-Math.ceil(n/Math.max(1,2*v)),"universal minimax bound");
    }
    profiles.push({n,cases,feasible,assignments,maskChecks,greedyChecks,disagreements,maxGap});
  }
  // Integer grid spacing 2 permits exact half-integer displacement ratios.
  let uniformChecks=0;
  const uniform=[];
  for(let n=2;n<=7;n++){
    const p=[...permutations(Array.from({length:n},(_,i)=>i))];
    for(let v=0;v<=9;v++){
      const x=Array.from({length:n},(_,i)=>2*i);
      const y=x.map(a=>a-(v%2));
      const good=p.filter(a=>a.every((j,i)=>Math.abs(x[i]-y[j])<=v));
      assert(good.length>0,"uniform witness feasible");
      const sorted=[],all=[];
      for(let i=0;i<n;i++)for(let j=i+1;j<n;j++){
        let a=Math.abs(x[i]-y[j])<=v&&Math.abs(x[j]-y[i])<=v;
        let b=good.some(p=>Math.abs(x[i]-y[p[j]])<=v&&Math.abs(x[j]-y[p[i]])<=v);
        if(a)sorted.push((1<<i)|(1<<j));
        if(b)all.push((1<<i)|(1<<j));
        assert(a===(j-i<=Math.floor((v-(v%2))/2)),"uniform sorted edge");
        assert(b===(j-i<Math.max(1,v)),"uniform universal edge");uniformChecks+=2;
      }
      // A shifted half-step grid attains universal bound. The unshifted grid
      // separately attains the sorted bound (same k for these half-step ratios).
      const min=edges=>Math.min(...Array.from({length:1<<n},(_,mask)=>mask).filter(mask=>edges.every(e=>e&mask)).map(pop));
      assert(min(sorted)===n-Math.ceil(n/(Math.floor(v/2)+1)),"uniform sorted optimum");
      assert(min(all)===n-Math.ceil(n/Math.max(1,v)),"uniform universal optimum");
      uniform.push({n,displacementOverSpacing:v/2,assignments:good.length,sortedAnchors:min(sorted),universalAnchors:min(all)});
    }
  }
  return {profiles,uniformChecks,uniform,status:"pass"};
}
console.log(JSON.stringify(laboratory(), null, 2));
