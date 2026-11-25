"use strict";
function laboratory(){
  const S=840,N=8;
  const assert=(v,m)=>{if(!v)throw Error(m)};
  function* compositions(n,k,p=[]){if(k===1){yield [...p,n];return}for(let i=1;i<=n-k+1;i++)yield* compositions(n-i,k-1,[...p,i])}
  function* partitions(n,groups=[[0]],i=1){if(i===n){yield groups;return}for(let j=0;j<groups.length;j++)yield* partitions(n,groups.map((g,k)=>k===j?[...g,i]:g),i+1);yield* partitions(n,[...groups,[i]],i+1)}
  const sum=x=>x.reduce((a,b)=>a+b,0);
  function rows(p,q,groups=p.map((_,i)=>[i])){return groups.map(g=>{const P=sum(g.map(i=>p[i])),Q=sum(g.map(i=>q[i]));assert(S%Q===0,"scale");return {p:P,q:Q,r:P*S/Q}}).sort((a,b)=>a.r-b.r)}
  function lower(rs,x){let y=0;for(const a of rs){const take=Math.min(x,a.q);y+=take*a.r;x-=take}assert(x===0,"mass");return y}
  const hinge=(rs,t)=>sum(rs.map(a=>a.q*Math.max(0,t-a.r)));
  const area2=rs=>sum(Array.from({length:N},(_,i)=>lower(rs,i)+lower(rs,i+1)));
  const gini=rs=>sum(rs.flatMap(a=>rs.map(b=>a.q*b.q*Math.abs(a.r-b.r))));
  function error(f,c){return Math.max(...Array.from({length:N+1},(_,i)=>lower(c,i)-lower(f,i)))}
  function dp(p,q,k){const n=p.length;const cost=(i,j)=>{let g=Array.from({length:j-i},(_,z)=>z+i),c=rows(p,q,[g])[0],f=g.map(z=>({q:q[z],r:p[z]*S/q[z]}));return hinge(f,c.r)};
    let D=Array.from({length:k+1},()=>Array(n+1).fill(Infinity));D[0][0]=0;for(let a=1;a<=k;a++)for(let j=a;j<=n;j++)for(let i=a-1;i<j;i++)D[a][j]=Math.min(D[a][j],Math.max(D[a-1][i],cost(i,j)));return D[k][n]}
  let receipt={normalization:N,integer_scale:S,profiles:0,allocation_witnesses:0,curve_knots:0,coarsenings:0,dual_equalities:0,area_equalities:0,lossless_equivalences:0,dp_comparisons:0,noncontiguous_improvements:0,first_noncontiguous:null,by_dimension:{}};
  for(let n=2;n<=5;n++){
    const parts=[...partitions(n)];let count=0;
    for(const pp of compositions(N,n))for(const qq of compositions(N,n)){
      const ids=pp.map((_,i)=>i).sort((a,b)=>pp[a]*qq[b]-pp[b]*qq[a]);
      const p=ids.map(i=>pp[i]),q=ids.map(i=>qq[i]),f=rows(p,q);
      receipt.profiles++;count++;
      const min=Array(N+1).fill(Infinity);
      function alloc(i,x,y){if(i===n){min[x]=Math.min(min[x],y);receipt.allocation_witnesses++;return}for(let a=0;a<=q[i];a++)alloc(i+1,x+a,y+a*p[i]*S/q[i])}
      alloc(0,0,0);
      for(let i=0;i<=N;i++){assert(min[i]===lower(f,i),"knapsack");receipt.curve_knots++}
      const tv=sum(p.map((a,i)=>Math.abs(a-q[i])))/2;
      assert(Math.max(...Array.from({length:N+1},(_,i)=>i*S-lower(f,i)))===tv*S,"TV");
      assert(2*area2(f)===2*N*N*S-gini(f),"Gini full");
      let best=Array(n+1).fill(Infinity),bestParts=[];
      for(const g of parts){
        let c=rows(p,q,g),e=error(f,c);
        let h=Math.max(...[...f,...c].map(a=>hinge(f,a.r)-hinge(c,a.r)));
        assert(e===h,"dual error");
        assert(2*(area2(c)-area2(f))===gini(f)-gini(c),"Gini gap");
        assert((e===0)===g.every(a=>a.every(i=>p[i]*q[a[0]]===p[a[0]]*q[i])),"lossless");
        assert(Array.from({length:N+1},(_,i)=>lower(c,i)>=lower(f,i)).every(Boolean),"ordering");
        if(g.every(a=>a.at(-1)-a[0]+1===a.length)){
          const cost=Math.max(...g.map(a=>{let t=rows(p,q,[a])[0].r;return sum(a.map(i=>q[i]*Math.max(0,t-p[i]*S/q[i])))}));
          assert(e===cost,"contiguous");
        }
        if(e<best[g.length]){best[g.length]=e;bestParts[g.length]=g}
        receipt.coarsenings++;receipt.dual_equalities++;receipt.area_equalities++;receipt.lossless_equivalences++;
      }
      for(let k=1;k<=n;k++){
        const d=dp(p,q,k);assert(d>=best[k],"DP impossible");
        const contiguous=parts.filter(g=>g.length===k&&g.every(a=>a.at(-1)-a[0]+1===a.length));
        assert(d===Math.min(...contiguous.map(g=>error(f,rows(p,q,g)))),"DP optimum");
        if(d>best[k]){receipt.noncontiguous_improvements++;if(!receipt.first_noncontiguous)receipt.first_noncontiguous={p,q,k,contiguous:d,arbitrary:best[k],groups:bestParts[k]}}
        receipt.dp_comparisons++;
      }
    }receipt.by_dimension[n]=count;
  }
  // Explicit sign-only audit failure: q=(1/4,...), p=(1,2,3,4)/10.
  receipt.sign_only_witness={p:[1,2,3,4],p_total:10,q:[1,1,1,1],q_total:4,delta:"1/10",B:"9/40",A:"19/100",gap:"-7/200",fine_lower_at_quarter:"1/10",coarse_lower_at_quarter:"3/20",restricted_coarse_A:"47/200",restricted_gap:"1/100",TV:"1/5"};
  return receipt;
}
console.log(JSON.stringify(laboratory(), null, 2));
