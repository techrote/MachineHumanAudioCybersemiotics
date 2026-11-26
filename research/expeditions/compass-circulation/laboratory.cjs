"use strict";
function laboratory(){
  const assert=(v,m)=>{if(!v)throw Error(m)};
  const conv=(a,b)=>a.map((_,i)=>a.reduce((s,x,j)=>s+x*b[(i-j+a.length)%a.length],0));
  const rev=a=>a.map((_,i)=>a[(a.length-i)%a.length]);
  const sym=a=>a.map((x,i)=>x+rev(a)[i]);
  const near=(a,b)=>Math.max(...a.map((x,i)=>Math.abs(x-b[i])));
  const receipt={circulant_profiles:0,circulant_lag_checks:0,max_floating_error:0,exact_eight_state_checks:0,delayed_coupling:[],arrow_receipts:[],entropy_frontier:[],triple_repair_checks:0,negative_controls:{}};
  for(let n=3;n<=17;n++){
    const r=Math.floor((n-1)/2), w=Array.from({length:r},(_,j)=>(j+1)/(4*r*(r+1)));
    const p=mask=>Array.from({length:n},(_,k)=>(1+2*w.reduce((s,a,j)=>s+a*(mask>>j&1?-1:1)*Math.sin(2*Math.PI*(j+1)*k/n),0))/n);
    let ref=p(0), refLag=ref, refs=[];
    for(let t=1;t<=8;t++){refs.push(sym(refLag));refLag=conv(refLag,ref)}
    let distinct=new Set();
    for(let mask=0;mask<2**r;mask++){
      const a=p(mask);assert(Math.min(...a)>0,"positive");distinct.add(a.map(x=>x.toFixed(10)).join(","));
      let v=a;
      for(let t=0;t<8;t++){const e=near(sym(v),refs[t]);assert(e<1e-12,"all lag");receipt.max_floating_error=Math.max(receipt.max_floating_error,e);receipt.circulant_lag_checks++;v=conv(v,a)}
      receipt.circulant_profiles++;
    }
    assert(distinct.size===2**r,"distinct");
  }
  const a=[0,1,0,1,0,-1,0,-1],b=[0,0,1,0,0,0,-1,0];
  assert(conv(a,a).every((x,i)=>x===2*conv(b,b)[i]),"exact integer convolution");
  receipt.exact_eight_state_checks++;
  const phi=x=>x*Math.log((1+x)/(1-x));
  for(const t of [.2,.4,.6,.8,.9,.99,.999,.9999,.99999,.999999]){
    const p=a.map(x=>(1+t*x/Math.SQRT2)/8),q=b.map(x=>(1+t*x)/8);
    const kl=x=>x.reduce((s,v,i)=>s+v*Math.log(v/x[(8-i)%8]),0);
    let u=p,v=q;
    for(let j=1;j<=16;j++){const e=near(sym(u),sym(v));assert(e<1e-12,"eight state lag");receipt.exact_eight_state_checks++;u=conv(u,p);v=conv(v,q)}
    const ea=phi(t/Math.SQRT2)/2,eb=phi(t)/4;
    assert(Math.abs(kl(p)-ea)<1e-10&&Math.abs(kl(q)-eb)<1e-9,"KL");
    assert(eb>ea,"strict KL disparity");
    receipt.entropy_frontier.push({t,spread:ea,concentrated:eb,ratio:eb/ea,min_concentrated:Math.min(...q)});
  }
  const mul=(A,B)=>A.map(row=>B[0].map((_,j)=>row.reduce((s,x,k)=>s+x*B[k][j],0n)));
  const add=(A,B)=>A.map((row,i)=>row.map((v,j)=>v+B[i][j]));
  const trans=A=>A.map((row,i)=>row.map((_,j)=>A[j][i]));
  const eq=(A,B)=>A.every((row,i)=>row.every((x,j)=>x===B[i][j]));
  const symM=A=>add(A,trans(A));
  const walsh=(i,j)=>{let v=i&j,p=0;while(v){p^=v&1;v>>=1}return p?-1n:1n};
  for(let h=0;h<=7;h++){
    const n=2**Math.ceil(Math.log2(h+5)),D=BigInt(16*(h+1)),den=BigInt(n)*D;
    const path=[2,...Array.from({length:h},(_,j)=>5+j),3];
    const P=sign=>Array.from({length:n},(_,i)=>Array.from({length:n},(_,j)=>{
      let s=D;
      for(let l=0;l+1<path.length;l++){const x=path[l],y=path[l+1];s+=walsh(i,x)*walsh(j,y)+walsh(i,y)*walsh(j,x)}
      s+=BigInt(h+1)*(walsh(i,1)*walsh(j,2)-walsh(i,2)*walsh(j,1));
      s+=BigInt(sign*2*(h+1))*(walsh(i,3)*walsh(j,4)-walsh(i,4)*walsh(j,3));
      return s;
    }));
    const p=P(1),q=P(-1);
    for(const X of [p,q]){assert(X.every(row=>row.every(v=>v>0n)&&row.reduce((s,x)=>s+x,0n)===den),"row");assert(trans(X).every(row=>row.reduce((s,x)=>s+x,0n)===den),"column")}
    let u=p,v=q,first=null;
    for(let lag=1;lag<=h+4;lag++){if(!eq(symM(u),symM(v))&&first===null)first=lag;u=mul(u,p);v=mul(v,q)}
    assert(first===h+3,"delayed coupling");
    receipt.delayed_coupling.push({intermediate_kernel_directions:h,states:n,last_equal_lag:first-1,first_distinct_lag:first});
  }
  // Exact return/triple/four-block comparison for two separate nonzero current components.
  const n=6,D=12n;
  const P=sgn=>Array.from({length:n},(_,i)=>Array.from({length:n},(_,j)=>{
    const ci=i<3?0:1,cj=j<3?0:1;
    if(ci!==cj||i===j)return D;
    return D+BigInt((j-i+3)%3===1?1:-1)*(ci===0?2n:BigInt(sgn)*3n)
  }));
  const p=P(1),q=P(-1);
  const mass=(X,word)=>word.slice(1).reduce((v,j,i)=>v*X[word[i]][j],1n);
  const unord=(X,w)=>mass(X,w)+mass(X,[...w].reverse());
  for(let length=2;length<=4;length++){
    let diffs=0,words=n**length;
    for(let code=0;code<words;code++){let z=code,w=[];for(let i=0;i<length;i++){w.push(z%n);z=Math.floor(z/n)}
      if(unord(p,w)!==unord(q,w))diffs++;
    }
    assert((length<4)===(diffs===0),"sym block depth");
    receipt.arrow_receipts.push({length,words,differences:diffs});
  }
  for(let i=0;i<n;i++)for(let j=i+1;j<n;j++){
    const x=p[i][j],y=p[j][i],s=x+y,r=x*y;
    assert(s*s-4n*r===(x-y)*(x-y),"return discriminant");
    receipt.triple_repair_checks++;
  }
  // General strictly positive uniform kernels: recover unordered directed flows
  // from pair sums and returns, test all 4-block sym laws under global reversal.
  let seed=74801;const rand=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed};
  for(let rep=0;rep<120;rep++){
    const n=3+rep%5, X=Array.from({length:n},()=>Array(n).fill(40n));
    for(let k=0;k<12;k++){let i=rand()%n,j=rand()%n,l=rand()%n;if(new Set([i,j,l]).size!==3)continue;
      for(const [a,b] of [[i,j],[j,l],[l,i]]){X[a][b]++;X[b][a]--}}
    const T=trans(X);
    for(let i=0;i<n;i++)for(let j=i+1;j<n;j++){
      const x=X[i][j],y=X[j][i];assert(x+y===80n,"sym pair");assert((x+y)**2n-4n*mass(X,[i,j,i])===(x-y)**2n,"return");receipt.triple_repair_checks++;
    }
    for(let k=0;k<30;k++){const w=Array.from({length:4},()=>rand()%n);assert(unord(X,w)===unord(T,w),"global reversal");receipt.triple_repair_checks++}
  }
  receipt.negative_controls={three_block_relative_orientation:"two disjoint current triangles indistinguishable through length 3, distinguished at length 4",two_lag_general:"delayed-coupling witnesses disprove two-lag sufficiency outside circulant class",directed_pair:"ordered one-step law recovers full transition matrix",physical_dissipation:"not measured"};
  return receipt;
}
console.log(JSON.stringify(laboratory(),null,2));
