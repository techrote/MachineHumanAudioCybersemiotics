"use strict";
function laboratory(){
  const assert=(p,m)=>{if(!p)throw Error(m)};
  const range=n=>Array.from({length:n},(_,i)=>i);
  const sum=a=>a.reduce((s,v)=>s+v,0);
  const same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
  const matrix=n=>range(n).map(()=>range(n).map(()=>0));
  const receipts=q=>{
    const n=q.length, u=range(n).map(i=>sum(q[i].slice(i+1))), l=range(n).map(j=>sum(range(n).slice(j+1).map(i=>q[i][j])));
    const diag=range(n).map(i=>q[i][i]), rows=q.map(sum), cols=range(n).map(j=>sum(q.map(row=>row[j])));
    return {u,l,diag,rows,cols};
  };
  function recover(s,known,n){
    const out=matrix(n);
    for(let i=0;i<n;i++)out[i][i]=s.diag[i];
    // Upper triangle: row 0 and column n-1 are tree edges.
    for(let i=1;i<n-1;i++){
      for(let j=i+1;j<n-1;j++)out[i][j]=known[i][j];
      out[i][n-1]=s.u[i]-sum(out[i].slice(i+1,n-1));
    }
    for(let j=1;j<n;j++){
      const upperCol=s.cols[j]-s.diag[j]-s.l[j];
      out[0][j]=upperCol-sum(range(n).slice(1,j).map(i=>out[i][j]));
    }
    // Lower triangle, transposed version of the same tree.
    for(let j=1;j<n-1;j++){
      for(let i=j+1;i<n-1;i++)out[i][j]=known[i][j];
      out[n-1][j]=s.l[j]-sum(range(n).slice(j+1,n-1).map(i=>out[i][j]));
    }
    for(let i=1;i<n;i++){
      const lowerRow=s.rows[i]-s.diag[i]-s.u[i];
      out[i][0]=lowerRow-sum(out[i].slice(1,i));
    }
    return out;
  }
  let seed=654;
  const random=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed};
  let reconstruction=0, trades=0, survival=0, gapMean=0;
  for(let n=2;n<=20;n++)for(let rep=0;rep<32;rep++){
    const q=range(n).map(()=>range(n).map(()=>1+random()%31)), s=receipts(q);
    assert(same(q,recover(s,q,n)),"tree recovery");reconstruction++;
    let known=0;
    for(let i=1;i<n-1;i++)for(let j=i+1;j<n-1;j++){
      known+=2;
      for(const transpose of [false,true]){
        const w=q.map(row=>row.slice());
        for(const [a,b,d] of [[i,j,1],[0,n-1,1],[i,n-1,-1],[0,j,-1]])w[transpose?b:a][transpose?a:b]+=d;
        assert(same(receipts(w),s),"rectangle trade");
        assert(!same(w,q),"trade not distinct");trades++;
        const gap=x=>sum(x.map((row,i)=>sum(row.map((v,j)=>v*Math.abs(i-j)))));
        assert(gap(w)===gap(q),"mean absolute gap invariant");gapMean++;
      }
    }
    assert(known===(n-2)*(n-3),"chord count");
    for(let h=0;h<n;h++){
      const exact=sum(s.rows.slice(h+1)), minLater=sum(s.u.slice(h+1))+sum(s.l.slice(h+1))+sum(s.diag.slice(h+1));
      const lo=minLater+s.l[h], hi=minLater+sum(s.l.slice(0,h+1));
      assert(lo<=exact&&exact<=hi,"survival bounds");
      // Construct exact endpoints: all B-first hidden A times at j+1 or n-1.
      for(const upper of [false,true]){
        const w=q.map(row=>row.slice());
        for(let j=0;j<n;j++){for(let i=j+1;i<n;i++)w[i][j]=0;if(j<n-1)w[upper?n-1:j+1][j]=s.l[j]}
        const t=receipts(w);
        assert(same([t.u,t.l,t.diag],[s.u,s.l,s.diag]),"first receipts");
        assert(sum(t.rows.slice(h+1))===(upper&&h<n-1?hi:lo),"endpoint");
      }survival++;
    }
  }
  function* perms(a,k=0){if(k===a.length){yield a.slice();return;}for(let j=k;j<a.length;j++){[a[k],a[j]]=[a[j],a[k]];yield* perms(a,k+1);[a[k],a[j]]=[a[j],a[k]]}}
  let permutations=0, thresholds=0;
  const frontier=[];
  for(let m=1;m<=8;m++){
    const mn=range(2*m).map(()=>m), mx=range(2*m).map(()=>0);let minVar=Infinity,maxVar=-Infinity;
    for(const p of perms(range(m))){
      const gaps=p.map((j,i)=>m+j-i);
      const varNum=sum(gaps.map(g=>(g-m)**2));
      assert(sum(gaps)===m*m,"mean");minVar=Math.min(minVar,varNum);maxVar=Math.max(maxVar,varNum);
      for(let g=0;g<2*m;g++){const c=gaps.filter(v=>v<=g).length;mn[g]=Math.min(mn[g],c);mx[g]=Math.max(mx[g],c);thresholds++}
      permutations++;
    }
    for(let g=0;g<2*m;g++){
      assert(mn[g]===Math.max(0,g-m+1)&&mx[g]===Math.min(m,g),"gap frontier");
    }
    assert(minVar===0&&3*maxVar===m*(m*m-1),"variance");
    frontier.push({m,min_counts:mn,max_counts:mx,max_variance_numerator:maxVar,denominator:m});
  }
  return {status:"pass",reconstruction_profiles:reconstruction,rectangle_trades:trades,mean_gap_checks:gapMean,survival_profiles:survival,permutations,threshold_checks:thresholds,frontier};
}
console.log(JSON.stringify(laboratory(),null,2));
