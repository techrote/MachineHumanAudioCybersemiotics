'use strict';
function run(){
  let checks=0; const assert=(b,msg)=>{checks++;if(!b)throw Error(msg)};
  function costs(word){
    let n=word.length, a=Array(n).fill(0), b=Array(n).fill(0);
    for(const x of word){
      const u=a.map((v,k)=>Math.min(v,k?b[k-1]:Infinity)+(x==="0"?0:1));
      const v=b.map((z,k)=>Math.min(z,k?a[k-1]:Infinity)+(x==="1"?0:1));
      a=u;b=v;
    }
    return a.map((v,k)=>Math.min(v,b[k]));
  }
  function brute(word){
    const n=word.length, a=Array(n).fill(n);
    for(let i=0;i<2**n;i++){
      const g=i.toString(2).padStart(n,"0");
      let s=0,d=0;
      for(let j=0;j<n;j++){d+=+(word[j]!==g[j]);if(j)s+=+(g[j]!==g[j-1]);}
      a[s]=Math.min(a[s],d);
    }
    for(let k=1;k<n;k++)a[k]=Math.min(a[k],a[k-1]);
    return a;
  }
  function choose(n,k){let a=1;for(let i=1;i<=k;i++)a=a*(n-i+1)/i;return Math.round(a)}
  let census=[], words=0, bruteWords=0;
  for(let n=1;n<=12;n++){
    const sums=Array(n).fill(0);
    for(let i=0;i<2**n;i++){
      const w=i.toString(2).padStart(n,"0"), d=costs(w);words++;
      let ones=w.split("1").length-1;
      let changes=[...w].slice(1).filter((x,j)=>x!==w[j]).length;
      assert(d[0]===Math.min(ones,n-ones),"fixed grammar");
      assert(d[n-1]===0,"unlimited");
      assert(JSON.stringify(d)===JSON.stringify(costs([...w].reverse().join(""))),"reversal");
      assert(JSON.stringify(d)===JSON.stringify(costs(w.replace(/./g,x=>x==="0"?"1":"0"))),"complement");
      if(n<=8){bruteWords++;assert(JSON.stringify(d)===JSON.stringify(brute(w)),"brute path agreement")}
      for(let k=0;k<n;k++){
        assert(Number.isInteger(d[k])&&d[k]>=0&&d[k]<=n,"integer mismatch");
        assert(k===0||d[k]<=d[k-1],"monotonic");
        assert((d[k]===0)===(k>=changes),"perfect retrospective fit");
        sums[k]+=3**(n-d[k]);
      }
    }
    const den=4**n;
    let fixed=0;
    for(let j=0;j<=n;j++)fixed+=choose(n,j)*3**Math.max(j,n-j);
    assert(sums[0]===fixed,"binomial normalizer");
    assert(sums[n-1]===6**n,"unlimited normalizer");
    for(let k=0;k<n;k++){
      const paths=2*Array.from({length:k+1},(_,j)=>choose(n-1,j)).reduce((a,b)=>a+b,0);
      assert(sums[k]>=den&&sums[k]<=paths*den&&sums[k]<=6**n,"normalizer bounds");
    }
    census.push({n,denominator:den,numerators:sums,regret_bits:sums.map(x=>Math.log2(x/den))});
  }
  const examples=["00001111","01010101","00000000"].map(word=>({word,mismatches:costs(word)}));
  return {checks,words,bruteWords,census,examples};
}
console.log(JSON.stringify(run(), null, 2));
