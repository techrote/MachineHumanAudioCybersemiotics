const api = require('./pilot.cjs');
const verify = function verify(api){
  const {params,evolve,compile,decode}=api; const assert=(v,msg)=>{if(!v)throw Error(msg)};
  const pop=x=>{let k=0;while(x){x&=x-1;k++}return k};
  const step=(x,n)=>x^(((x<<1)&((1<<n)-1))|(x>>>(n-1)));
  const result={rings:0,kernel_states:0,transition_comparisons:0,pilot_masks:0,budget_contracts:0,decodes:0,impossible:0,odd_surcharge:0};
  for(let n=1;n<=12;n++){
    const P=params(n,0).P;
    for(let t=0;t<=P+1;t++){
      result.rings++;const kernel=[]; const {d,p}=params(n,t);
      for(let x=0;x<1<<n;x++){let z=x;for(let j=0;j<t;j++)z=step(z,n);assert(BigInt(z)===evolve(n,t,BigInt(x)),"evolution");result.transition_comparisons++;if(z===0&&x)kernel.push(x)}
      assert(kernel.length===2**d-1,"dimension");result.kernel_states+=kernel.length;
      const fullDist=kernel.length?Math.min(...kernel.map(pop)):n+1;
      assert(!d||fullDist===n/p,"distance");
      const best=Array(n+2).fill(Infinity);
      for(let mask=0;mask<1<<n;mask++){
        let dist=n+1;for(const k of kernel){dist=Math.min(dist,pop(k&mask));if(!dist)break}
        best[dist]=Math.min(best[dist],pop(mask));result.pilot_masks++;
      }
      for(let i=n;i>=0;i--)best[i]=Math.min(best[i],best[i+1]);
      for(let e=0;e<=n;e++){
        result.budget_contracts++;const c=compile(n,t,e);
        if(c.status==="impossible"){assert(!Number.isFinite(best[e+1]),"false impossible");result.impossible++;continue}
        assert(c.minimum===best[e+1],"nonoptimal");assert(new Set(c.pilots).size===c.minimum&&c.pilots.every(i=>i>=0&&i<n),"bad coordinates");
        let mask=c.pilots.reduce((s,i)=>s|(1<<i),0);assert(kernel.every(k=>pop(k&mask)>e),"bad layout");
        if(d&&c.minimum>(e+1)*p&&e>0)result.odd_surcharge++;
        const x=BigInt(((n*71+t*11+e*23)%(1<<n))),y=evolve(n,t,x);
        const obs=c.pilots.slice(Math.min(e,c.pilots.length)).map(i=>[i,Number((x>>BigInt(i))&1n)]);
        const got=decode(n,t,y,obs);assert(got.status==="unique"&&got.x===x,"decode");result.decodes++;
      }
    }
  }
  assert(compile(8,3,2).minimum===7,"odd surcharge");
  assert(compile(8,3,1).minimum===4,"one loss");
  assert(decode(8,3,0n,[[0,0],[4,0],[1,0]]).status==="ambiguous","duplicate residues");
  assert(decode(8,1,1n,[]).status==="inconsistent","impossible output");
  let rejected=0;for(const f of [()=>compile(0,1,0),()=>compile(8,-1,0),()=>compile(8,1,9),()=>evolve(8,1,256n),()=>decode(8,1,0n,[[0,0],[0,1]])]){try{f()}catch{rejected++}}assert(rejected===5,"validation");result.refusals=rejected;
  return result;
};
console.log(JSON.stringify(verify(api),null,2));
