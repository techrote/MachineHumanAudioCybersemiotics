"use strict";
// Standard-library Node-compatible exact finite enumeration.
function laboratory(){
  const assert=(b,m)=>{if(!b)throw Error(m)};
  const pop=x=>{let k=0;while(x){k+=x&1;x>>>=1}return k};
  const rot=(x,n,s)=>((x<<s)|(x>>>(n-s)))&((1<<n)-1);
  const choose=(n,k)=>{if(k<0||k>n||!Number.isInteger(k))return 0;let a=1;for(let i=1;i<=k;i++)a=a*(n-i+1)/i;return Math.round(a)};
  let ringCases=0,maskChecks=0,histChecks=0,lotteryTuples=0,lotteryCases=0;
  const rings=[];
  for(let n=2;n<=10;n++){
    let symmetric=0,soloPossible=0;
    for(let x=0;x<1<<n;x++){
      const stabilizer=Array.from({length:n},(_,s)=>s).filter(s=>rot(x,n,s)===x);
      const h=stabilizer.length,p=n/h,hist=Array(n+1).fill(0);
      if(h>1)symmetric++;
      if(h===1)soloPossible++;
      for(let y=0;y<1<<n;y++){
        maskChecks++;
        if(stabilizer.every(s=>rot(y,n,s)===y))hist[pop(y)]++;
      }
      for(let k=0;k<=n;k++){assert(hist[k]===choose(p,k/h),"mask histogram");histChecks++}
      assert(hist[1]===(h===1?n:0),"solo obstruction");
      ringCases++;
    }
    rings.push({n,symmetric,soloPossible});
  }
  const lotteries=[];
  for(let n=2;n<=6;n++)for(let q=2;q<=6;q++){
    let wins=Array(n).fill(0),tie=0,tuples=q**n;
    for(let i=0;i<tuples;i++){
      let t=i,arr=[];
      for(let j=0;j<n;j++){arr.push(t%q);t=Math.floor(t/q)}
      let m=Math.max(...arr),w=arr.map((v,j)=>v===m?j:-1).filter(j=>j>=0);
      if(w.length===1)wins[w[0]]++;else tie++;
      lotteryTuples++;
    }
    const S=Array.from({length:q},(_,j)=>j**(n-1)).reduce((a,b)=>a+b,0);
    assert(wins.every(v=>v===S),"per candidate wins");
    assert(tie===tuples-n*S,"tie count");
    lotteryCases++;
    if(n===4)lotteries.push({n,q,success:n*S/tuples,tie:tie/tuples,threeRoundFailure:(tie/tuples)**3});
  }
  assert(rot(5,4,2)===5,"periodic witness");
  assert(rot(1,4,2)!==1,"single chair breaks witness");
  assert(rot(1,4,1)!==1,"first-index negative control");
  return {ringCases,maskChecks,histChecks,lotteryTuples,lotteryCases,rings,lotteries};
}
console.log(JSON.stringify(laboratory(),null,2));
