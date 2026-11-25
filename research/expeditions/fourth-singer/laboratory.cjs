"use strict";
function laboratory() {
  const assert = (b, msg) => { if (!b) throw Error(msg); };
  const pop = n => { let c=0; for(;n;n&=n-1)c++; return c; };
  function* combos(n,k,repeat,start=0,prefix=[]) {
    if(!k){yield prefix;return;}
    for(let i=start;i<(repeat?n:n-k+1);i++)yield* combos(n,k-1,repeat,i+(repeat?0:1),[...prefix,i]);
  }
  const masks=(m,r)=>Array.from({length:1<<m},(_,i)=>i).filter(i=>pop(i)<=r);
  const moments=(rows,ms)=>ms.map(s=>rows.reduce((a,x)=>a+Number((x&s)===s),0));
  const S=(n,k)=>{let a=Array(k+1).fill(0);a[0]=1;for(let i=1;i<=n;i++){let b=Array(k+1).fill(0);for(let j=1;j<=k;j++)b[j]=a[j-1]+j*a[j];a=b;}return a[k];};
  function infer(m,r,ms,signature){
    const k=2**r, map=new Map(ms.map((s,i)=>[s,signature[i]])), groups=[], constants=[];
    for(let i=0;i<m;i++){
      const c=map.get(1<<i);
      if(c===0||c===k){constants.push([i,c===k?1:0]);continue;}
      if(c!==k/2)return null;
      let found=false;
      for(const g of groups){
        const pair=map.get((1<<i)|(1<<g[0][0]));
        if(pair===0||pair===k/2){g.push([i,pair===0?1:0]);found=true;break;}
        if(pair!==k/4)return null;
      }
      if(!found)groups.push([[i,0]]);
    }
    if(groups.length!==r+1)return null;
    const legs=[[],[]];
    for(let y=0;y<1<<(r+1);y++){
      let x=0;
      for(const [i,b] of constants)x|=b<<i;
      for(let j=0;j<groups.length;j++)for(const [i,b] of groups[j])x|=(((y>>j)&1)^b)<<i;
      legs[pop(y)%2].push(x);
    }
    for(const leg of legs){leg.sort((a,b)=>a-b);if(moments(leg,ms).join(",")!==signature.join(","))return null;}
    return {legs, groups:groups.map(g=>g.map(x=>x[0])), query:groups.reduce((a,g)=>a|(1<<g[0][0]),0)};
  }
  const profiles=[];
  for(const [m,r,k,repeat] of [[3,1,2,true],[4,1,2,true],[5,1,2,true],[3,2,3,true],[3,2,4,true],[4,2,3,true],[4,2,4,true],[5,2,3,true],[5,2,4,true],[4,3,8,false]]){
    const ms=masks(m,r), fibres=new Map();let count=0, max=0,ambiguous=0,checked=0;
    for(const rows of combos(1<<m,k,repeat)){
      const sig=moments(rows,ms).join(",");
      if(!fibres.has(sig))fibres.set(sig,[]);
      fibres.get(sig).push(rows);count++;
    }
    for(const [sig,rows] of fibres){
      max=Math.max(max,rows.length);
      if(rows.length>1)ambiguous++;
      if(k<2**r)assert(rows.length===1,"below threshold");
      if(r===1){let s=sig.split(",").slice(1).map(Number).filter(x=>x===1).length;assert(rows.length===2**Math.max(0,s-1),"duet");}
      if(r>=2&&k===2**r){
        const inferred=infer(m,r,ms,sig.split(",").map(Number));
        assert(rows.length<=2,"fibre bound");
        assert(Boolean(inferred)===(rows.length===2),"detector");
        if(inferred){
          assert(inferred.legs.map(x=>x.join(",")).sort().join(";")===rows.map(x=>x.join(",")).sort().join(";"),"exact legs");
          const parityCounts=rows.map(leg=>leg.filter(x=>pop(x&inferred.query)%2).length);
          assert(Math.min(...parityCounts)===0&&Math.max(...parityCounts)===k,"one bit repair");
          for(let s=1;s<1<<m;s++)if(pop(s)===r+1){
            let differing=moments(rows[0],[s])[0]!==moments(rows[1],[s])[0];
            let transversal=inferred.groups.every(g=>g.filter(i=>s&(1<<i)).length===1);
            assert(differing===transversal,"transversal");
            checked++;
          }
        }
      }
    }
    if(r>=2&&k===2**r)assert(ambiguous===2**(m-r-1)*S(m+1,r+2),"Stirling count");
    profiles.push({m,r,k,repeat,multisets:count,fibres:fibres.size,ambiguous,max_fibre:max,transversal_checks:checked});
  }
  // No fixed coordinate-local probe may be omitted: singleton blocks on its mask.
  let omittedChecks=0;
  for(let m=3;m<=9;m++)for(let r=2;r<m;r++){
    const targets=masks(m,r+1).filter(x=>pop(x)===r+1);
    for(const t of targets){
      const legs=[[],[]];
      for(let x=t;;x=(x-1)&t){legs[pop(x)%2].push(x);if(!x)break;}
      assert(moments(legs[0],masks(m,r)).join(",")===moments(legs[1],masks(m,r)).join(","),"local baseline");
      for(const u of targets){assert((moments(legs[0],[u])[0]!==moments(legs[1],[u])[0])===(u===t),"local necessity");omittedChecks++;}
    }
  }
  return {profiles,omitted_probe_checks:omittedChecks,status:"pass"};
}
console.log(JSON.stringify(laboratory(),null,2));
