// Standalone Node.js laboratory; no dependencies. Synthetic model only.
function run(){
  const fact=n=>n<2?1:n*fact(n-1);
  const choose=(n,k)=>k<0||k>n?0:fact(n)/(fact(k)*fact(n-k));
  const derange=n=>n===0?1:n===1?0:(n-1)*(derange(n-1)+derange(n-2));
  function* perms(a){if(!a.length){yield [];return;}for(let i=0;i<a.length;i++)for(const rest of perms(a.filter((_,j)=>i!==j)))yield [a[i],...rest];}
  let checks=0, permutations=0, masks=0;
  function eq(a,b){checks++;if(a!==b)throw Error(`${a} != ${b}`);}
  const rows=[];
  for(let n=2;n<=7;n++){
    const ps=[...perms(Array.from({length:n},(_,i)=>i))];permutations+=ps.length;
    eq(ps.length,fact(n));
    const totals=Array(n+1).fill(0), survived=Array.from({length:n+1},()=>Array(1<<n).fill(0));
    for(const p of ps){
      let bits=0;for(let i=0;i<n;i++)if(p[i]===i)bits|=1<<i;
      const f=bits.toString(2).replace(/0/g,"").length;totals[f]++;
      for(let m=0;m<(1<<n);m++){masks++;if((m&bits)===m)survived[f][m]++;}
    }
    for(let f=0;f<=n;f++){
      eq(totals[f],choose(n,f)*derange(n-f));
      for(let m=0;m<(1<<n);m++){
        const s=m.toString(2).replace(/0/g,"").length;
        eq(survived[f][m],choose(n-s,f-s)*derange(n-f));
      }
    }
    for(let k=0;k<n;k++){
      const compatible=ps.filter(p=>p.slice(0,k).every((x,i)=>x===i));
      eq(compatible.length,fact(n-k));
      const numerator=Array.from({length:n},(_,target)=>Math.max(...Array.from({length:n},(_,key)=>compatible.filter(p=>p[key]===target).length))).reduce((a,b)=>a+b,0);
      eq(numerator*n*0+numerator,(k+1)*compatible.length);
      eq(compatible.filter(p=>p.every((x,i)=>x===i)).length,1);
      if(n===4)rows.push({k,stableSingle:`${numerator}/${n*compatible.length}`,stablePhrase:`1/${compatible.length}`,freshSingle:`1/${n}`,freshPhrase:`1/${fact(n)}`});
    }
  }
  return {checks,permutations,maskEvaluations:masks,rows};
}
console.log(JSON.stringify(run(),null,2));
