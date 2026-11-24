// Exact integer/rational arithmetic; levels are integer ticks, not linear amplitudes.
function closure(matrix) {
  const n=matrix.length, d=matrix.map(r=>r.slice());
  for(let i=0;i<n;i++) d[i][i]=Math.min(d[i][i],0);
  for(let k=0;k<n;k++) for(let i=0;i<n;i++) for(let j=0;j<n;j++)
    d[i][j]=Math.min(d[i][j],d[i][k]+d[k][j]);
  return d;
}
function gcd(a,b){while(b){[a,b]=[b,a%b]}return Math.abs(a)}
// Each [i,j,lo,hi] is an inclusive bound on x[j]-x[i].
// A finite radius requires every pair connected by finite two-sided bounds.
function solve(n,edges) {
  if(!Number.isInteger(n)||n<1||n>32||!Array.isArray(edges)) throw Error("invalid size");
  const d0=Array.from({length:n},(_,i)=>Array.from({length:n},(_,j)=>i===j?0:Infinity));
  for(const e of edges){
    if(!Array.isArray(e)||e.length!==4||!e.every(Number.isSafeInteger)) throw Error("invalid edge");
    const [i,j,lo,hi]=e;
    if(i<0||j<0||i>=n||j>=n||lo>hi||Math.abs(lo)>1000000||Math.abs(hi)>1000000)throw Error("invalid bound");
    d0[i][j]=Math.min(d0[i][j],hi);d0[j][i]=Math.min(d0[j][i],-lo);
  }
  // Detect infeasibility before Floyd-Warshall; keeps intermediate integer
  // bounds polynomial even for input with negative cycles.
  let v=Array(n).fill(0);
  for(let k=0;k<n;k++){
    const w=v.map((x,j)=>Math.min(x,...v.map((y,i)=>y+d0[i][j])));
    if(w.every((x,j)=>x===v[j])) break;
    if(k===n-1)return {status:"infeasible"};
    v=w;
  }
  const d=closure(d0);
  if(d.some(row=>row.some(x=>!Number.isFinite(x))))return {status:"unbounded"};
  let p=0,q=1,cycle=[0,0];
  // Maximum mean of closed walks of length <= n. A simple maximizer exists.
  for(let s=0;s<n;s++){
    let val=Array(n).fill(-Infinity), paths=Array(n).fill(null);
    val[s]=0;paths[s]=[s];
    for(let k=1;k<=n;k++){
      let next=Array(n).fill(-Infinity), np=Array(n).fill(null);
      for(let i=0;i<n;i++)if(paths[i])for(let j=0;j<n;j++){
        let w=val[i]+d[i][j];
        if(w>next[j]){next[j]=w;np[j]=[...paths[i],j]}
      }
      val=next;paths=np;
      if(val[s]*q>p*k){p=val[s];q=k;cycle=paths[s]}
    }
  }
  const g=gcd(p,q);p/=g;q/=g;
  // At radius p/q, enforce y[j]-y[i] <= R-d[j][i].
  // Include the original bounds as well: a feasible optimal center exists.
  const c=closure(d.map((r,i)=>r.map((x,j)=>Math.min(q*x,p-q*d[j][i]))));
  if(c.some((r,i)=>r[i]<0))throw Error("center certificate failed");
  const y=c[0].slice(); // y[0]=0; all values share denominator q.
  const diameter=Math.max(...d.flatMap((r,i)=>r.map((x,j)=>x+d[j][i])));
  return {status:"optimal",d,diameter,radius:[p,q],centerNumerators:y,cycle};
}
function lossNumerator(d,y,q){
  return Math.max(...d.flatMap((r,i)=>r.map((x,j)=>q*x-y[j]+y[i])));
}

export {solve, lossNumerator};
