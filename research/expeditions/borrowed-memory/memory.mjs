// MHAC #240: exact synthetic stationary binary observation laboratory.
function lab(){
  const gcd=(a,b)=>{a=a<0n?-a:a;b=b<0n?-b:b;while(b){[a,b]=[b,a%b]}return a};
  const lcm=(a,b)=>a/gcd(a,b)*b;
  const sum=v=>v.reduce((a,b)=>a+b,0n);
  const assert=(x,m)=>{if(!x)throw Error(m)};
  function model(labels,rows,weights){
    const n=labels.length;
    assert(n>0&&rows.length===n&&weights.length===n,"dimensions");
    assert(labels.every(x=>x===0||x===1),"binary labels");
    const A=rows.map(r=>r.map(BigInt)),w=weights.map(BigInt),d=sum(A[0]),W=sum(w);
    assert(d>0n&&W>0n&&w.every(x=>x>0n),"positive initial support");
    assert(A.every(r=>r.length===n&&r.every(x=>x>=0n)&&sum(r)===d),"stochastic rows");
    for(let j=0;j<n;j++)assert(sum(w.map((v,i)=>v*A[i][j]))===w[j]*d,"stationary weights required");
    return {labels,A,w,d,W,n,edges:A.map(r=>r.flatMap((v,j)=>v?[[j,v]]:[]))};
  }
  function step(m,r,b=null,f=1n){
    const out=Array(m.n).fill(0n);
    for(let i=0;i<m.n;i++)if(r[i]&&(b===null||m.labels[i]===b))for(const [j,v] of m.edges[i])out[j]+=r[i]*v*f;
    return out;
  }
  function fraction(a,b){const g=gcd(a,b);return `${a/g}/${b/g}`}
  function word(m,s){let r=m.w.slice(),den=m.W;for(const b of s){r=step(m,r,Number(b));den*=m.d}return fraction(sum(r),den)}
  function surrogate(m){
    const w=[0n,0n],c=[[0n,0n],[0n,0n]];
    for(let i=0;i<m.n;i++){const a=m.labels[i];w[a]+=m.w[i];for(const [j,v] of m.edges[i])c[a][m.labels[j]]+=m.w[i]*v;}
    assert(w.every(x=>x>0n),"both labels must occur");
    const d=lcm(w[0]*m.d,w[1]*m.d);
    return model([0,1],c.map((r,i)=>r.map(v=>v*(d/(w[i]*m.d)))),w);
  }
  function strong(m){
    const seen=new Map();
    for(let i=0;i<m.n;i++){const a=m.labels[i],r=sum(m.A[i].filter((_,j)=>m.labels[j]===1));if(seen.has(a)&&seen.get(a)!==r)return false;seen.set(a,r)}
    return true;
  }
  function reversible(m){return m.A.every((r,i)=>r.every((v,j)=>m.w[i]*v===m.w[j]*m.A[j][i]))}
  function pair(m,k,a,b){
    let r=m.w.map((v,i)=>m.labels[i]===a?v:0n),den=m.W;
    for(let t=0;t<k;t++){r=step(m,r);den*=m.d}
    return fraction(sum(r.filter((_,i)=>m.labels[i]===b)),den);
  }
  function allLags(m,k){
    const bound=m.n+k.n-1;
    for(let t=0;t<=bound;t++)for(let a=0;a<2;a++)for(let b=0;b<2;b++){const p=pair(m,t,a,b),q=pair(k,t,a,b);if(p!==q)return {equal:false,lag:t,a,b,p,q,bound}}
    return {equal:true,bound};
  }
  function primitive(v){const g=v.reduce(gcd,0n);if(!g)return v;let out=v.map(x=>x/g);if(out.find(x=>x)!==undefined&&out.find(x=>x)<0n)out=out.map(x=>-x);return out}
  // Exact reachable row-span equivalence, breadth first. Keep actual un-reduced
  // prefix rows for extension; elimination is used only to decide independence.
  function equivalence(m,k){
    const d=lcm(m.d,k.d),W=lcm(m.W,k.W),initial=[...m.w.map(x=>x*(W/m.W)),...k.w.map(x=>-x*(W/k.W))];
    const basis=[],queue=[{r:initial,s:""}];let tested=0;
    for(let q=0;q<queue.length;q++){
      const {r,s}=queue[q];tested++;
      if(sum(r)!==0n)return {equal:false,witness:s,p:word(m,s),q:word(k,s),rank:basis.length,tested};
      let v=primitive(r);
      for(const {p,u} of basis){if(v[p])v=primitive(v.map((x,i)=>x*u[p]-u[i]*v[p]))}
      const p=v.findIndex(x=>x!==0n);
      if(p<0)continue;
      basis.push({p,u:v});
      for(let b=0;b<2;b++)queue.push({r:[...step(m,r.slice(0,m.n),b,d/m.d),...step(k,r.slice(m.n),b,d/k.d)],s:s+b});
    }
    return {equal:true,rank:basis.length,tested};
  }
  function classify(m){const k=surrogate(m);return {states:m.n,strong:strong(m),reversible:reversible(m),pairLags:allLags(m,k),words:equivalence(m,k)}}
  function parityBlock(k){
    assert(Number.isInteger(k)&&k>=3&&k<=7,"block range");
    const B=2**(k-1),n=k*B,labels=[],rows=[];
    for(let p=0;p<k;p++)for(let z=0;z<B;z++){
      let b=0;for(let i=0;i<k-1;i++)b^=(z>>i)&1;
      labels.push(p===k-1?b:(z>>p)&1);
      const r=Array(n).fill(0);if(p<k-1)r[(p+1)*B+z]=B;else for(let j=0;j<B;j++)r[j]=1;
      rows.push(r);
    }
    return model(labels,rows,Array(n).fill(1));
  }
  function delayLine(){const labels=[],rows=[];for(let a=0;a<2;a++)for(let b=0;b<2;b++){labels.push(b);const r=Array(4).fill(0);for(let c=0;c<2;c++)r[c*2+a]=1;rows.push(r)}return model(labels,rows,[1,1,1,1])}
  function cycle(s){return model([...s].map(Number),[...s].map((_,i)=>[...s].map((_,j)=>Number(j===(i+1)%s.length))),[...s].map(()=>1))}
  function symmetricCensus(){
    const results=[];
    for(let n=2;n<=5;n++){
      const edges=[];for(let i=0;i<n;i++)for(let j=i+1;j<n;j++)edges.push([i,j]);
      let total=0,lump=0,positive=0;
      for(let g=0;g<2**edges.length;g++){
        const A=Array.from({length:n},(_,i)=>Array.from({length:n},(_,j)=>i===j?n:0));
        edges.forEach(([i,j],e)=>{if((g>>e)&1){A[i][j]=A[j][i]=1;A[i][i]--;A[j][j]--}});
        for(let mask=2;mask<2**n;mask+=2){
          const b=Array.from({length:n},(_,i)=>(mask>>i)&1),m1=b.reduce((x,y)=>x+y,0),m0=n-m1;
          const r=A.map(row=>row.reduce((s,v,j)=>s+v*b[j],0));
          const s0=r.reduce((s,v,i)=>s+v*(1-b[i]),0),s1=r.reduce((s,v,i)=>s+v*b[i],0);
          const variance=m0*m1*r.reduce((s,v)=>s+v*v,0)-m1*s0*s0-m0*s1*s1;
          // Independent explicit two-step path count.
          let paths=0;for(let i=0;i<n;i++)for(let j=0;j<n;j++)for(let k=0;k<n;k++)paths+=b[i]*A[i][j]*A[j][k]*b[k];
          const defect=m0*m1*paths-m1*s0*s0-m0*s1*s1;
          const exact=r.every((v,i)=>r.every((u,j)=>b[i]!==b[j]||u===v));
          assert(defect===variance&&defect>=0&&(defect===0)===exact,"reversible identity");
          total++;if(exact)lump++;else positive++;
        }
      }
      results.push({states:n,graphs:2**edges.length,partitions_per_graph:2**(n-1)-1,total,lumpable:lump,positive_defect:positive});
    }
    return results;
  }
  function cyclicCensus(){
    const results=[];let first=null;
    for(let n=2;n<=12;n++){
      let total=0,lag2equal=0,hidden=0,strongCount=0,earliest=null;
      for(let mask=1;mask<2**n-1;mask++){
        const b=Array.from({length:n},(_,i)=>(mask>>i)&1),m=b.reduce((x,y)=>x+y,0),c=t=>b.reduce((s,v,i)=>s+v*b[(i+t)%n],0),c1=c(1),c2=c(2);
        const equal=c2*m*(n-m)===c1*c1*(n-m)+(m-c1)**2*m;
        const isStrong=b.every((v,i)=>b.every((u,j)=>u!==v||b[(i+1)%n]===b[(j+1)%n]));
        total++;if(isStrong)strongCount++;
        if(equal){lag2equal++;if(!isStrong){hidden++;if(!earliest)earliest=b.join("");if(!first)first=b.join("")}}
      }
      results.push({states:n,total,lag2equal,strong:strongCount,hidden,example:earliest});
    }
    return {results,first,first_classification:first?classify(cycle(first)):null};
  }
  function run(){
    const examples=[3,4,5].map(k=>{const m=parityBlock(k),r=classify(m);assert(r.pairLags.equal&&!r.words.equal&&r.words.witness.length===k,"parity example");return {block:k,...r}});
    const weak=classify(delayLine());assert(!weak.strong&&weak.words.equal&&weak.pairLags.equal,"weak-only control");
    const good=classify(model([0,0,1,1],Array.from({length:4},()=>[1,1,1,1]),[1,1,1,1]));assert(good.strong&&good.reversible&&good.words.equal,"strong control");
    const rev=classify(model([0,0,1],[[2,1,0],[1,1,1],[0,1,2]],[1,1,1]));assert(rev.reversible&&!rev.strong&&!rev.pairLags.equal&&rev.pairLags.lag===2&&!rev.words.equal,"reversible failure");
    const symmetric=symmetricCensus(),cyclic=cyclicCensus();
    // Independent direct enumeration of full words for all four examples,
    // check every shorter word and replay the witness.
    for(const k of [3,4,5]){
      const m=parityBlock(k),s=surrogate(m);
      for(let len=0;len<k;len++)for(let z=0;z<2**len;z++){const bits=len?z.toString(2).padStart(len,"0"):"";assert(word(m,bits)===word(s,bits),"shorter word");}
      assert(word(m,"0".repeat(k))!==word(s,"0".repeat(k)),"zero witness");
    }
    return {schema:"fictional-borrowed-memory-v1",examples,weak,good,rev,symmetric,cyclic};
  }
  return {model,step,word,pair,surrogate,strong,reversible,allLags,equivalence,classify,parityBlock,delayLine,cycle,symmetricCensus,cyclicCensus,run};
}
export const laboratory = lab();
