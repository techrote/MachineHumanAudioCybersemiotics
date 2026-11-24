// Synthetic mathematical checks; run with node lab.js.
function lab(){
  "use strict";
  const counts={graphs:0,constructed:0,edgeObservations:0,pairChecks:0,oraclePalettes:0,oracleRowTransitions:0,oracleDistances:0,crownWitnesses:0,negativeControls:0};
  function check(ok,msg){if(!ok)throw Error(msg);}
  const sum=x=>x.reduce((a,b)=>a+b,0);
  const overlap=(a,b)=>sum(a.map((v,j)=>Math.min(v,b[j])));
  const tv=(a,b)=>sum(a.map((v,j)=>Math.abs(v-b[j])))/2;
  const cap=rows=>sum(rows[0].map((_,j)=>Math.max(...rows.map(row=>row[j]))));
  function distances(n,edges,u){
    const d=Array(n).fill(-1),queue=[u];d[u]=0;
    for(let i=0;i<queue.length;i++)for(const [a,b] of edges){
      const v=a===queue[i]?b:b===queue[i]?a:-1;
      if(v>=0&&d[v]<0){d[v]=d[queue[i]]+1;queue.push(v);}
    }return d;
  }
  // Each palette atom carries one integer unit. q is its complementary
  // support, p is the actual receipt row; no floating point probabilities.
  function construct(d,L,D,a,extreme){
    const l=Math.floor(L/2),scale=Math.max(1,l),H=(D-a)*scale,M=(2*D-a)*scale;
    const universe=Array.from({length:M},(_,i)=>i);
    const interval=(start,len)=>new Set(universe.slice(start,start+len));
    const outside=(...sets)=>universe.filter(j=>sets.every(s=>!s.has(j)));
    const even=[],odd=[];
    if(!extreme||l===0){
      even.push(interval(0,H));odd.push(interval(H,H));
    }else{
      const h=Math.min(a*scale,D-a); // l*h <= H
      for(let i=0;i<=l;i++)even.push(interval(i*h,H));
      for(let i=0;i<l;i++)odd.push(new Set(outside(even[i],even[i+1]).slice(0,H)));
      if(L%2){
        const available=outside(even[l]);
        available.sort((x,y)=>Number(even[0].has(y))-Number(even[0].has(x))||x-y);
        odd.push(new Set(available.slice(0,H)));
      }else odd.push(odd[l-1]);
    }
    const rows=d.map(j=>{
      const array=j%2?odd:even;
      const set=array[Math.min(Math.floor(j/2),array.length-1)];
      return universe.map(t=>Number(!set.has(t)));
    });
    return {rows,den:D*scale,err:a*scale};
  }
  function verify(rows,edges,den,err){
    check(rows.every(row=>sum(row)===den),"row sums");
    check(cap(rows)===2*den-err,"exact vulnerability");
    // Construct the actual decoder fibre for each oriented collapse.
    for(const [u,v] of edges){
      const fibres=new Map();
      for(let x=0;x<rows.length;x++){
        const y=x===v?u:x;
        if(!fibres.has(y))fibres.set(y,[]);
        fibres.get(y).push(x);
      }
      let loss=0;
      for(const fibre of fibres.values())for(let j=0;j<rows[0].length;j++){
        const masses=fibre.map(x=>rows[x][j]);
        loss+=sum(masses)-Math.max(...masses);
        counts.edgeObservations++;
      }
      check(loss===err,"direct Bayes decoder loss");
    }
  }
  for(let n=2;n<=5;n++){
    const all=[];for(let i=0;i<n;i++)for(let j=i+1;j<n;j++)all.push([i,j]);
    for(let mask=1;mask<2**all.length;mask++){
      const edges=all.filter((_,i)=>(mask>>i)&1),d0=distances(n,edges,0);
      if(d0.includes(-1)||edges.some(([u,v])=>(d0[u]-d0[v])%2===0))continue;
      counts.graphs++;
      for(let u=0;u<n;u++){
        const d=distances(n,edges,u);
        for(let v=u+1;v<n;v++)for(let D=1;D<=5;D++)for(let a=0;a<D;a++)for(const extreme of [false,true]){
          const L=d[v],l=Math.floor(L/2),w=construct(d,L,D,a,extreme);
          verify(w.rows,edges,w.den,w.err);
          const scale=w.den/D;
          const want=L%2?(extreme?Math.max(0,D-a-l*a):D-a):(extreme?Math.min(D-a,l*a):0);
          check(tv(w.rows[u],w.rows[v])===want*scale,"pair extremum");
          counts.constructed++;counts.pairChecks++;
        }
      }
    }
  }
  // Independent finite-grid oracle: enumerate EVERY ordered row within
  // each unordered column-capacity partition. Build compatibility from
  // actual pairwise Bayes overlap; propagate reachable endpoints.
  function partitions(total,limit,min=1,p=[]){
    if(total===0)return [p];
    const result=[];
    for(let x=min;x<=Math.min(total,limit);x++)result.push(...partitions(total-x,limit,x,[...p,x]));
    return result;
  }
  function boundedRows(m,D,i=0,p=[]){
    if(i===m.length)return D===0?[p]:[];
    const out=[];for(let x=0;x<=Math.min(D,m[i]);x++)out.push(...boundedRows(m,D-x,i+1,[...p,x]));return out;
  }
  for(let D=1;D<=4;D++)for(let a=0;a<D;a++){
    const M=2*D-a,maxL=9;
    const lows=Array(maxL+1).fill(Infinity),highs=Array(maxL+1).fill(-1),alias=Array(maxL+1).fill(Infinity);
    for(const m of partitions(M,D)){
      counts.oraclePalettes++;
      const rows=boundedRows(m,D);
      const adj=rows.map(x=>rows.map((y,j)=>overlap(x,y)<=a?j:-1).filter(j=>j>=0));
      counts.oracleRowTransitions+=rows.length**2;
      for(let i=0;i<rows.length;i++){
        let reach=new Set([i]);
        for(let L=1;L<=maxL;L++){
          const next=new Set();for(const j of reach)for(const k of adj[j])next.add(k);reach=next;
          for(const j of reach){
            const t=tv(rows[i],rows[j]);
            const lo=L%2?Math.max(0,D-a-Math.floor(L/2)*a):0;
            const hi=L%2?D-a:Math.min(D-a,Math.floor(L/2)*a);
            check(t>=lo&&t<=hi,"oracle violated bound");
            lows[L]=Math.min(lows[L],t);highs[L]=Math.max(highs[L],t);
            if(t===0)alias[L]=Math.min(alias[L],m.length);
            counts.oracleDistances++;
          }
        }
      }
    }
    // Grid extrema attained even if the full-real construction uses finer atoms:
    // each step shifts at most a units and can stop when target is reached.
    for(let L=1;L<=maxL;L++){
      const l=Math.floor(L/2);
      check(lows[L]===(L%2?Math.max(0,D-a-l*a):0),"oracle min");
      check(highs[L]===(L%2?D-a:Math.min(D-a,l*a)),"oracle max");
    }
    if(a===1&&D>=2)check(alias[2*D-1]===2*D-1,"odd-cycle vocabulary boundary");
  }
  for(let k=1;k<=30;k++){
    const L=2*k+1,D=k+1;
    const rows=Array.from({length:L+1},(_,i)=>Array.from({length:L},(_,j)=>{
      // q labels are the rotating maximum independent sets of C_L.
      for(let t=0;t<k;t++)if((j+2*t)%L===i%L)return 0;
      return 1;
    }));
    verify(rows,Array.from({length:L},(_,i)=>[i,i+1]),D,1);
    check(tv(rows[0],rows[L])===0,"cycle closure");
    counts.pairChecks++;
  }
  for(let r=3;r<=12;r++){
    const n=2*r,edges=[];
    for(let i=0;i<r;i++)for(let j=0;j<r;j++)if(i!==j)edges.push([i,r+j]);
    const d=distances(n,edges,0);check(d[r]===3,"crown distance");
    // Any one alias at e=1/2.
    const w=construct(d,3,2,1,true);verify(w.rows,edges,w.den,w.err);
    check(tv(w.rows[0],w.rows[r])===0,"single crown alias");
    // All aliases at quotient K_r threshold.
    const rows=Array.from({length:n},(_,i)=>Array.from({length:r},(_,j)=>Number(i%r!==j)));
    verify(rows,edges,r-1,r-2);
    for(let i=0;i<r;i++)check(tv(rows[i],rows[i+r])===0,"joint crown alias");
    counts.crownWitnesses+=2;
  }
  // Average error can conceal one completely ambiguous action.
  const rows=[[1,0],[1,0],[0,1],[0,1],[0,1]],edges=[[0,1],[0,2],[0,3],[0,4]];
  check(cap(rows)===2&&sum(edges.map(([u,v])=>overlap(rows[u],rows[v])))===1&&tv(rows[0],rows[1])===0,"average-error control");
  counts.negativeControls++;
  return counts;
}
console.log(JSON.stringify(lab(), null, 2));
