'use strict';
// Exact integer spectral-constraint and receipt-graph census. Node >=18.
function run() {
  const check=(x,msg)=>{if(!x)throw Error(msg)};
  const mod=(x,n)=>((x%n)+n)%n;
  const counts={families:0,triads:0,pair_decompositions:0,quartic_mask_pairs:0,quartic_exact_orders:0,small_phase_assignments:0,small_phase_solutions:0,graph_profiles:0,graph_code_pairs:0,minimum_budget_profiles:0};
  function fixture(r,J){
    const N=3*2**r,base=Array.from({length:r+1},(_,i)=>2**i);
    const extra=J.map(j=>N/2-2**j),A=base.concat(extra),S=[0,...A,...A.map(a=>N-a)];
    check(new Set(S).size===S.length,"support collision");
    const mask=new Map(S.map(a=>[a,0]));
    extra.forEach((a,i)=>{mask.set(a,1<<i);mask.set(N-a,1<<i)});
    return {N,A,S,base,extra,mask};
  }
  function weight(n){let k=0;while(n){k+=n&1;n>>>=1}return k;}
  function family(r,J){
    const {N,A,S,base,extra,mask}=fixture(r,J),set=new Set(S),pairs=new Map();
    const k=J.length;
    for(const a of S)for(const b of S){
      const c=mod(a+b,N),m=mask.get(a)^mask.get(b);
      counts.pair_decompositions++;
      if(set.has(c)){counts.triads++;check(m===mask.get(c),"nontrivial triple mask");}
      if(!pairs.has(c))pairs.set(c,new Set());
      pairs.get(c).add(m);
    }
    const found=new Set();
    for(const ms of pairs.values())for(const x of ms)for(const y of ms){
      const z=x^y;counts.quartic_mask_pairs++;check(weight(z)<=2,"quartic >2");found.add(z);
    }
    check(found.size===1+k+k*(k-1)/2,"missing quartic masks");
    for(let i=0;i<k;i++){
      check(mod(extra[i]+2**J[i]-base[r]-base[r-1],N)===0,"anchor sum");
      check(found.has(1<<i),"anchor missing");
      for(let j=0;j<i;j++)check(found.has((1<<i)|(1<<j)),"edge missing");
    }
    counts.families++;
    if(k)counts.quartic_exact_orders++;
  }
  // Every nonadjacent subset for r<=12; maximal packing up to r=25.
  for(let r=3;r<=12;r++){
    for(let s=0;s<2**(r-2);s++){
      if(s&(s<<1))continue;
      const J=Array.from({length:r-2},(_,i)=>i).filter(i=>s&(1<<i));
      family(r,J);
    }
  }
  for(let r=13;r<=25;r++)family(r,Array.from({length:r-2},(_,i)=>i).filter(i=>i%2===0));
  // Independent full finite-phase enumeration on a 24th-root grid.
  // The proof establishes that this grid includes every exact solution for N=24.
  const f=fixture(3,[0]), N=f.N, d=f.A.length;
  const vectors=new Map([[0,Array(d).fill(0)]]);
  f.A.forEach((a,i)=>{let v=Array(d).fill(0);v[i]=1;vectors.set(a,v);vectors.set(N-a,v.map(x=>-x));});
  const rs=new Map();
  for(const a of f.S)for(const b of f.S){
    const c=mod(a+b,N);if(!vectors.has(c))continue;
    const v=vectors.get(a).map((x,i)=>x+vectors.get(b)[i]-vectors.get(c)[i]);
    if(v.some(Boolean))rs.set(v.join(","),v);
  }
  const rows=[...rs.values()], alpha=Array(d).fill(0),sol=[];
  function visit(i){
    if(i===d){
      counts.small_phase_assignments++;
      if(rows.every(v=>mod(v.reduce((s,x,j)=>s+x*alpha[j],0),N)===0)){
        counts.small_phase_solutions++;
        sol.push(alpha.slice());
      }
      return;
    }
    for(let a=0;a<N;a++){alpha[i]=a;visit(i+1);}
  }
  visit(0);
  check(sol.length===48,"phase count");
  const classes=new Set(sol.map(a=>a.map((x,i)=>mod(x-f.A[i]*a[0],N)).join(",")));
  check(classes.size===2,"orbit count");
  // All simple receipt graphs on <=5 vertices. Compare literal code distance
  // against min cut (enumerated separately as bipartitions including root=0).
  for(let v=2;v<=5;v++){
    const es=[];for(let i=0;i<v;i++)for(let j=i+1;j<v;j++)es.push([i,j]);
    const words=1<<(v-1);
    for(let g=0;g<(1<<es.length);g++){
      const edges=es.filter((_,i)=>g&(1<<i));
      const bit=(word,i)=>i===0?0:(word>>(i-1))&1;
      const enc=Array.from({length:words},(_,w)=>edges.map(([i,j])=>bit(w,i)^bit(w,j)));
      let distance=Infinity;for(let a=0;a<words;a++)for(let b=a+1;b<words;b++){
        const dist=enc[a].reduce((s,x,i)=>s+(x!==enc[b][i]),0);
        distance=Math.min(distance,dist);counts.graph_code_pairs++;
      }
      let cut=Infinity;
      for(let s=1;s<words;s++)cut=Math.min(cut,edges.filter(([i,j])=>bit(s,i)!==bit(s,j)).length);
      check(distance===cut,"code/cut");counts.graph_profiles++;
    }
  }
  // Sharp repeated-receipt budget: tree for d=1, multicycle + long edge cover
  // for d>=2 (two vertices use parallel edges).
  for(let v=2;v<=11;v++)for(let D=1;D<=8;D++){
    let E=[];
    if(D===1)for(let i=1;i<v;i++)E.push([0,i]);
    else if(v===2)E=Array.from({length:D},()=>[0,1]);
    else {
      for(let h=0;h<Math.floor(D/2);h++)for(let i=0;i<v;i++)E.push([i,(i+1)%v]);
      if(D%2){const m=Math.floor(v/2);for(let i=0;i<(v%2?m+1:m);i++)E.push([i,i+m]);}
    }
    const bit=(s,i)=>i===0?0:(s>>(i-1))&1;
    let cut=Infinity;
    for(let s=1;s<1<<(v-1);s++)cut=Math.min(cut,E.filter(([i,j])=>bit(s,i)!==bit(s,j)).length);
    check(cut>=D,"budget construction cut");
    check(E.length===(D===1?v-1:Math.ceil(v*D/2)),"budget count");
    counts.minimum_budget_profiles++;
  }
  return {contract:"synthetic exact integer checks; no physical/human validation",counts,small_fixture:{N:24,support:f.A,phase_grid:24,solutions:sol.length,translation_classes:classes.size},assertion_failures:0};
}
if(typeof module!=="undefined")module.exports=run;
if(typeof require!=="undefined"&&require.main===module)console.log(JSON.stringify(run(),null,2));
