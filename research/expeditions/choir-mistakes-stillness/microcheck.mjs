// Independent expanded-roster BigInt cross-check, executed function serialized verbatim.
function microCensus(){
  let tables=0,initialVectors=0,orderErasure=0,first=null,recurrences=0;
  const rows=[];
  for(let n=2;n<=8;n++){
    let nTables=0,nVectors=0,nErased=0;
    for(let a=0;a<=n;a++)for(let b=0;b<=n-a;b++)for(let c=0;c<=n-a-b;c++){
      const d=n-a-b-c,t=[a,b,c,d];
      if(!(a+b&&c+d&&a+c&&b+d))continue;
      const cells=t.flatMap((m,j)=>Array(m).fill(j));
      const axes=[cells.map(j=>j>>1),cells.map(j=>j&1)];
      const sizes=axes.map(g=>[g.filter(x=>x===0).length,g.filter(x=>x===1).length].map(BigInt));
      const den=sizes.flat().reduce((x,y)=>x*y,1n),num=BigInt(a*d-b*c)**2n;
      function step(x,k){
        const g=axes[k],counts=sizes[k],s=[0n,0n];
        x.forEach((v,i)=>s[g[i]]+=v);
        return g.map(j=>s[j]*counts[1-j]);
      }
      const forward=x=>step(step(x,0),1), reverse=x=>step(step(x,1),0);
      const N=BigInt(n);
      nTables++;
      for(let mask=0;mask<2**n;mask++){
        const x=Array.from({length:n},(_,i)=>BigInt((mask>>i)&1));
        const sum=x.reduce((u,v)=>u+v,0n),y=forward(x),z=forward(y),rev=reverse(x);
        if(!y.every((v,i)=>N*z[i]-sum*den**2n===num*(N*v-sum*den)))throw Error("micro recurrence failed");
        if(y.reduce((u,v)=>u+v,0n)!==sum*den)throw Error("mean not preserved");
        if(y.every(v=>N*v===sum*den)&&rev.some(v=>N*v!==sum*den)){
          nErased++;
          if(!first)first={n,table:t,input:x.map(Number),forwardNumerators:y.map(Number),reverseNumerators:rev.map(Number),denominator:Number(den)};
        }
        nVectors++;recurrences++;
      }
    }
    tables+=nTables;initialVectors+=nVectors;orderErasure+=nErased;
    rows.push({n,tables:nTables,initialVectors:nVectors,orderErasure:nErased});
  }
  if(first?.n!==4)throw Error("unexpected smallest binary witness");
  return {tables,initialVectors,recurrences,orderErasure,first,rows};
}

export { microCensus };
