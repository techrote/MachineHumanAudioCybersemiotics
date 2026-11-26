// Exact integer moment-polytope vertex census. Node >=18; no dependencies.
// All products are safe integers for n <= 40. Degenerate vertices are included.
function run(){
  const check=(ok,msg)=>{if(!ok)throw Error(msg)};
  const eq=(a,b,c,d)=>a*d===b*c;
  const rows=[]; let supports=0,feasible=0;
  for(let n=3;n<=40;n++){
    let grid=Array.from({length:n+1},(_,i)=>2*i-n);
    for(let k of [2,3]){
      if(n<=k)continue;
      let min=Infinity,max=-Infinity,count=0;
      function visit(a,start){
        if(a.length<k+1){
          for(let i=start;i<=grid.length-(k+1-a.length);i++)visit([...a,grid[i]],i+1);
          return;
        }
        supports++;
        // Lagrange basis expectation under moments E1=1, ES=0, ES²=n, ES³=0.
        for(let i=0;i<a.length;i++){
          let others=a.filter((_,j)=>i!==j);
          let den=others.reduce((p,x)=>p*(a[i]-x),1);
          let num=k===2?n+others[0]*others[1]:-n*others.reduce((s,x)=>s+x,0)-others.reduce((p,x)=>p*x,1);
          if(num*den<0)return;
        }
        feasible++;count++;
        let product=a.reduce((p,x)=>p*x,1),sum=a.reduce((s,x)=>s+x,0),e2=0;
        for(let i=0;i<a.length;i++)for(let j=i+1;j<a.length;j++)e2+=a[i]*a[j];
        // The support polynomial vanishes, giving the next moment exactly.
        let moment=k===2?sum*n+product:-e2*n-product;
        min=Math.min(min,moment);max=Math.max(max,moment);
      }
      visit([],0);
      let den=n*(n-1)*(n-2);
      if(k===2){
        let b=n%2?n*(n-1):n*(n-2);
        check(min===-b&&max===b,"third moment "+n);
        rows.push({n,order:3,feasible_vertices_with_multiplicity:count,min_numerator:min,max_numerator:max,denominator:den});
      }else{
        let squares=[...new Set(grid.map(x=>x*x))].sort((a,b)=>a-b);
        let lo=Math.max(...squares.filter(x=>x<=n)),hi=Math.min(...squares.filter(x=>x>=n));
        let lower=(lo+hi)*n-lo*hi,upper=n%2?n*n*n-n*n+n:n*n*n;
        check(min===lower&&max===upper,"fourth moment "+n);
        rows.push({n,order:4,feasible_vertices_with_multiplicity:count,min_numerator:min-3*n*n+2*n,max_numerator:max-3*n*n+2*n,denominator:den*(n-3)});
      }
    }
  }
  return {method:"integer Lagrange support enumeration",max_n:40,profiles:rows.length,supports,feasible,assertion_failures:0,rows};
}
if(typeof module!=="undefined"&&require.main===module)console.log(JSON.stringify(run(),null,2));
