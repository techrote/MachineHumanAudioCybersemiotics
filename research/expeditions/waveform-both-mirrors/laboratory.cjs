"use strict";
function laboratory(){
  const assert=(x,s)=>{if(!x)throw Error(s)};
  const eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
  const wt=n=>{let w=0;for(;n;n>>=1)w+=n&1;return w};
  const parity=n=>wt(n)%2;
  const make=(m,b)=>{let x=[1];for(let j=0;j<m;j++){const f=(b>>j)&1?[-1,2,1]:[1,2,-1];x=f.flatMap(a=>x.map(v=>a*v))}return x};
  const ac=x=>Array.from({length:x.length},(_,k)=>x.slice(k).reduce((s,v,i)=>s+v*x[i],0));
  const mask=(n,m)=>{let a=0;for(let j=0;j<m;j++,n=Math.floor(n/3))if(n%3!==1)a|=1<<j;return a};
  const canon=x=>x.map(v=>v*Math.sign(x[0])).join(",");
  const stats={family_members:0,autocorrelation_cells:0,pointwise_energy_cells:0,pair_parity_checks:0,prefix_profiles:0,adjacent_checks:0,sign_census_candidates:0,hamming_codewords:0,hamming_fault_receipts:0};
  const rows=[];
  for(let m=1;m<=5;m++){
    const N=3**m,B=2**m,center=(N-1)/2;
    const xs=Array.from({length:B},(_,b)=>make(m,b)), ref=xs[0], R=ac(ref), E=6**m;
    const max=Array(B).fill(0),adj=Array(m).fill(0);
    assert(R[0]===E,"energy");
    assert(new Set(xs.map(x=>x.join(","))).size===B,"distinct");
    assert(new Set(xs.map(x=>[x.join(","),x.slice().reverse().join(",")].sort()[0])).size===B/2,"reversal");
    for(let b=0;b<B;b++){
      const x=xs[b];assert(x[center]===2**m,"center");
      assert(eq(ac(x),R),"autocorrelation");stats.autocorrelation_cells+=N;
      assert(eq(x.map(v=>v*v),ref.map(v=>v*v)),"pointwise");stats.pointwise_energy_cells+=N;
      for(let i=0;i<N;i++)for(let j=i+1;j<N;j++){
        const a=mask(i,m)^mask(j,m),v=ref[i]*ref[j],p=x[i]*x[j];
        assert(p===v*(parity(a&b)?-1:1),"parity");
        if(b===0)max[a]=Math.max(max[a],Math.abs(v));
        if(j===i+1){
          let k=0,l=j;while(l%3===0){k++;l/=3}
          assert(a===1<<k,"adjacent digit");
          if(b===0)adj[k]=Math.max(adj[k],Math.abs(v));
          stats.adjacent_checks++;
        }
        stats.pair_parity_checks++;
      }
      stats.family_members++;
    }
    for(let a=1;a<B;a++)assert(max[a]===2**(2*m-wt(a)),"max product");
    for(let j=0;j<m;j++)assert(adj[j]===2**(2*m-2*j-1),"adj maximum");
    for(let L=1;L<=N;L++){
      let k=0;while(k<m&&3**k<L)k++;
      assert(new Set(xs.map(x=>canon(x.slice(0,L)))).size===2**k,"prefix");
      stats.prefix_profiles++;
    }
    let census=null;
    if(m<=2){
      const inds=Array.from({length:N},(_,i)=>i).filter(i=>i!==center);
      census=0;
      for(let q=0;q<2**(N-1);q++){
        let x=ref.map(Math.abs);
        inds.forEach((i,j)=>{if((q>>j)&1)x[i]*=-1});
        if(eq(ac(x),R))census++;
        stats.sign_census_candidates++;
      }
      assert(census===B,"small full fibre");
    }
    rows.push({m,N,partners:B,up_to_reversal:B/2,first_full_prefix:3**(m-1)+1,energy:E,small_full_fibre:census,maximum_products_by_parity_weight:Array.from({length:m},(_,j)=>2**(2*m-j-1)),adjacent_max_products:adj});
  }
  const codeRows=[];
  for(let m=1;m<=12;m++){
    let r=1;while(2**r<m+r+1)r++;
    const cols=Array.from({length:2**r-1},(_,j)=>j+1).filter(v=>wt(v)>1).slice(0,m);
    const allcols=cols.concat(Array.from({length:r},(_,j)=>1<<j));
    const n=m+r;let d=n;
    const syndrome=w=>allcols.reduce((s,c,j)=>s^(((w>>j)&1)?c:0),0);
    for(let b=0;b<2**m;b++){
      let p=cols.reduce((s,c,j)=>s^(((b>>j)&1)?c:0),0),word=b|(p<<m);
      assert(syndrome(word)===0,"syndrome");
      if(b)d=Math.min(d,wt(word));
      stats.hamming_codewords++;
      if(m<=8)for(let j=-1;j<n;j++){
        const received=word^(j<0?0:1<<j),s=syndrome(received);
        const corrected=received^(s?1<<allcols.indexOf(s):0);
        assert(corrected===word,"fault");
        stats.hamming_fault_receipts++;
      }
    }
    assert(d>=3,"distance");
    codeRows.push({m,n,redundancy:r,distance:d,adjacent_only_triplication:3*m});
  }
  return {schema:"mhac-502-exact-v1",stats,rows,codeRows,example: {a:make(2,0),b:make(2,1),autocorrelation:ac(make(2,0))},assertion_failures:0};
}
console.log(JSON.stringify(laboratory(), null, 2));
