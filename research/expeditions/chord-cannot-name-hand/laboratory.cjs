'use strict';
// MHAC #380: synthetic deterministic exact grid census; numeric sine tests separate.
function laboratory(){
  const assert=(b,m)=>{if(!b)throw Error(m)};
  const pairs=n=>Array.from({length:n},(_,i)=>Array.from({length:n-i-1},(_,j)=>[i,i+j+1])).flat();
  const graphs=n=>{let p=pairs(n);return Array.from({length:2**p.length},(_,m)=>p.filter((_,i)=>m>>i&1))};
  function distances(n,E){let d=Array.from({length:n},(_,i)=>Array.from({length:n},(_,j)=>i===j?0:Infinity));for(const [i,j] of E)d[i][j]=d[j][i]=1;for(let k=0;k<n;k++)for(let i=0;i<n;i++)for(let j=0;j<n;j++)d[i][j]=Math.min(d[i][j],d[i][k]+d[k][j]);return d}
  function comps(V,E){let left=new Set(V),out=[];while(left.size){let Q=[left.values().next().value];left.delete(Q[0]);for(let i=0;i<Q.length;i++)for(const [a,b] of E){let v=a===Q[i]?b:b===Q[i]?a:null;if(left.has(v)){left.delete(v);Q.push(v)}}out.push(Q)}return out}
  function blocks(V,E){if(V.length<=2)return E.length?1:0;for(let v of V){let C=comps(V.filter(x=>x!==v),E.filter(e=>!e.includes(v)));if(C.length>1)return C.reduce((s,c)=>{let a=[v,...c];return s+blocks(a,E.filter(e=>e.every(x=>a.includes(x))))},0)}return 1}
  const mod=(x,q)=>((x%q)+q)%q;
  const key=(x,q)=>Math.min(mod(x,q),mod(-x,q));
  const word=(a,E,q)=>E.map(([i,j])=>key(a[j]-a[i],q)).join(",");
  const all=(n,q)=>Array.from({length:q**(n-1)},(_,k)=>[0,...Array.from({length:n-1},(_,i)=>Math.floor(k/q**i)%q)]);
  function solve(a,E,q){let n=a.length,tree=[],seen=new Set([0]);while(seen.size<n){let edge=E.find(([i,j])=>seen.has(i)!==seen.has(j));assert(edge,"disconnected");let [i,j]=edge;if(seen.has(j))[i,j]=[j,i];tree.push([i,j]);seen.add(j)}let out=new Set(),target=word(a,E,q);for(let m=0;m<2**tree.length;m++){let v=Array(n).fill(0);tree.forEach(([i,j],k)=>v[j]=mod(v[i]+((m>>k&1)?-1:1)*(a[j]-a[i]),q));if(word(v,E,q)===target)out.add(v.join(","))}return out}
  let R={connected_graphs:0,generic_fibers:0,generic_block_orientation_checks:0,finite_graph_grid_profiles:0,finite_fiber_checks:0,finite_worlds_in_ambiguous_fibers:0,uniform_graph_checks:0,sine_cut_checks:0,diameter_checks:0,diameter_sharpness_checks:0,exceptional_cycle:null,examples:[]};
  for(let n=2;n<=5;n++)for(let E of graphs(n)){
    let V=Array.from({length:n},(_,i)=>i),P=pairs(n),D=distances(n,E),diam=Math.max(...D.flat()),connected=Number.isFinite(diam);
    if(connected){
      R.connected_graphs++;let b=blocks(V,E),q=10007,a=[0,...V.slice(1).map(i=>3**(i-1))],sol=solve(a,E,q);
      assert(sol.size===2**b,"generic block count");R.generic_fibers++;
      // Pin a signed spanning-tree edge for each block indirectly: greedily select a coordinate
      // that halves the remaining oriented candidates; each surviving set is a subcube.
      let left=[...sol].map(s=>s.split(",").map(Number)),used=0;
      while(left.length>1){let edge=E.find(([i,j])=>new Set(left.map(v=>mod(v[j]-v[i],q))).size>1);assert(edge,"no orientation edge");let [i,j]=edge,old=left.length;left=left.filter(v=>mod(v[j]-v[i],q)===mod(a[j]-a[i],q));assert(left.length*2===old,"orientation did not halve");used++}
      assert(used===b,"block signed count");R.generic_block_orientation_checks++;
      for(let eps of [0.001,0.00001]){let root=D.findIndex(row=>row.includes(diam)),p=D[root].map(x=>x*eps),mx=L=>Math.max(...L.map(([i,j])=>Math.abs(Math.sin(p[j]-p[i]))));let ratio=mx(E)/mx(P);assert(Math.abs(ratio- Math.sin(eps)/Math.sin(diam*eps))<1e-10,"sharpness family");R.diameter_sharpness_checks++}
    }
    if(n<=4){
      for(let q of [5,8]){
        let A=all(n,q),F=new Map();
        for(let a of A){let w=word(a,E,q);if(!F.has(w))F.set(w,[]);F.get(w).push(a)}
        let uniform=true;
        for(let a of A){
          let group=F.get(word(a,E,q)),ref=new Set([a.join(","),a.map(x=>mod(-x,q)).join(",")]);if(group.length!==ref.size)uniform=false;
          if(group.length>ref.size)R.finite_worlds_in_ambiguous_fibers++;
          if(connected){let s=solve(a,E,q);assert(s.size===group.length&&group.every(v=>s.has(v.join(","))),"direct grid vs tree");R.finite_fiber_checks++}
          if(n===4&&q===5&&E.length===4&&connected&&V.every(i=>E.filter(e=>e.includes(i)).length===2)&&group.length>ref.size&&!R.exceptional_cycle)R.exceptional_cycle={E,a,solutions:group};
        }
        assert(uniform===(E.length===P.length),"uniform graph criterion");R.uniform_graph_checks++;R.finite_graph_grid_profiles++;
      }
    }
    let A=all(n,4),min=Infinity,cut=Infinity;
    for(let mask=1;mask<2**(n-1);mask++){let c=E.filter(([i,j])=>Boolean(mask>>i&1)!==Boolean(mask>>j&1)).length;cut=Math.min(cut,c)}
    for(let a of A){let strong=E.filter(([i,j])=>mod(a[j]-a[i],2)===1).length;if(a.some(x=>x%2===1)){min=Math.min(min,strong);R.sine_cut_checks++}
      if(connected){let mx=L=>Math.max(...L.map(([i,j])=>Math.abs(Math.sin(Math.PI/2*(a[j]-a[i])))));assert(mx(E)+1e-10>=mx(P)/diam,"diameter bound");R.diameter_checks++}}
    assert(min===cut,"signed minimum distance equals cut");
  }
  for(let n of [4,8,16,32,64]){let e=1e-5;R.examples.push({n,path_ratio:Math.sin(e)/Math.sin((n-1)*e),star_limit:1/2,path_limit:1/(n-1),generic_cos:n,uniform_cos:n*(n-1)/2,fixed_signed:n-1,adaptive_signed:1})}
  assert(R.exceptional_cycle,"missing degenerate witness");
  return R;
}
console.log(JSON.stringify(laboratory(), null, 2));
