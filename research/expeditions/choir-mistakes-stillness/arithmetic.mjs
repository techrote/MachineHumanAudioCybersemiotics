// Original exact combinatorial count and prime/composite witness; executed functions.
function choose(n,k){
  if(!Number.isInteger(k)||k<0||k>n)return 0n;
  k=Math.min(k,n-k);let v=1n;
  for(let i=1;i<=k;i++)v=v*BigInt(n-i+1)/BigInt(i);
  return v;
}

function gcd(a,b){while(b)[a,b]=[b,a%b];return a}

function erasureCount(t){
  const [a,b,c,d]=t,r0=a+b,r1=c+d,c0=a+c;
  if(!(r0&&r1&&c0&&b+d))throw Error("constant partition");
  if(a*d===b*c)return 0n;
  const g=gcd(r0,r1);
  let rows=0n,both=0n;
  for(let k=0;k<=g;k++){
    const u=k*r0/g,v=k*r1/g,w=k*c0/g;
    rows+=choose(r0,u)*choose(r1,v);
    if(!Number.isInteger(w))continue;
    for(let i=0;i<=a;i++)both+=choose(a,i)*choose(b,u-i)*choose(c,w-i)*choose(d,v-w+i);
  }
  if(rows<both)throw Error("invalid intersection count");
  return rows-both;
}

function constructiveWitness(n){
  let p=2;while(p*p<=n&&n%p)p++;
  if(p*p>n)return null;
  const q=n/p,t=[0,p,1,n-p-1];
  const x=Array.from({length:n},(_,i)=>i===0||(i>=p&&i<p+q-1)?1:0);
  const groups=[Array.from({length:n},(_,i)=>i<p?0:1),Array.from({length:n},(_,i)=>i===p?0:1)];
  // Compare exact numerator/denominator via integer group averaging.
  const step=(v,g)=>{let count=[0,0],sum=[0,0];g.forEach((j,i)=>{count[j]++;sum[j]+=v[i]});return g.map(j=>sum[j]*count[1-j])};
  const y=step(step(x,groups[0]),groups[1]),z=step(step(x,groups[1]),groups[0]);
  if(!y.every(v=>v===y[0])||z.every(v=>v===z[0])||erasureCount(t)===0n)throw Error("constructive witness failed");
  return {n,p,q,t};
}

function countingCensus(){
  let tables=0,positiveTables=0;
  const rows=[];
  for(let n=2;n<=30;n++){
    let count=0n,valid=0,positive=0;
    for(let a=0;a<=n;a++)for(let b=0;b<=n-a;b++)for(let c=0;c<=n-a-b;c++){
      const d=n-a-b-c;
      if(!(a+b&&c+d&&a+c&&b+d))continue;
      valid++;
      const k=erasureCount([a,b,c,d]);count+=k;if(k)positive++;
    }
    const composite=constructiveWitness(n)!==null;
    if(composite!==(count>0n))throw Error("prime/composite discrepancy");
    tables+=valid;positiveTables+=positive;
    rows.push({n,valid,positive,orderErasure:count.toString(),composite});
  }
  let witnesses=0;
  for(let n=2;n<=200;n++)if(constructiveWitness(n))witnesses++;
  return {tables,positiveTables,constructiveWitnessesThrough200:witnesses,rows};
}

export { erasureCount, constructiveWitness, countingCensus };
