'use strict';
// Original synthetic finite-model laboratory; node lab.js
function lab(){
  "use strict";
  const E=[0,3,5,6], G=[1,2,4];
  const assert=(x,m)=>{if(!x)throw Error(m)};
  const sum=a=>a.reduce((x,y)=>x+y,0);
  const tv2=(a,b)=>sum(a.map((v,i)=>Math.abs(v-b[i])));
  const same=(a,b)=>a.length===b.length&&a.every((v,i)=>v===b[i]);
  const receipt={gridModels:0,gridTriples:0,productAndPairChecks:0,delayedTranscripts:0,projectionChecks:0,sourcePathChecks:0,resetChecks:0};
  function laws(g,d,k){
    let a=[]; const on=E.map((x,i)=>x&g?i:-1).filter(x=>x>=0),off=E.map((x,i)=>x&g?-1:i).filter(x=>x>=0);
    for(let j=0;j<=2*k;j++)for(let l=0;l<=2*(d-k);l++){
      const w=[0,0,0,0];w[on[0]]=j;w[on[1]]=2*k-j;w[off[0]]=l;w[off[1]]=2*(d-k)-l;a.push(w);
    }return a;
  }
  function local(g,d,k){
    if(!Number.isInteger(d)||d<=0||!Number.isInteger(k)||k<0||k>d||!G.includes(g))throw Error("invalid model");
    return E.map(x=>3*k<=2*d?(x===0?2*d-3*k:k):(x===0?0:x&g?k:2*(d-k)));
  }
  for(let d=1;d<=6;d++)for(let k=0;k<=d;k++){
    const [A,B,C]=G.map(g=>laws(g,d,k));let best=Infinity;
    for(const a of A)for(const b of B)for(const c of C){
      const s=Math.max(tv2(a,b),tv2(a,c),tv2(b,c));best=Math.min(best,s);receipt.gridTriples++;
    }
    const ws=G.map(g=>local(g,d,k));
    for(let j=0;j<3;j++){
      assert(sum(ws[j])===2*d,"normalization");
      assert(sum(ws[j].filter((_,i)=>E[i]&G[j]))===2*k,"source switch");
    }
    assert(best===2*Math.max(0,3*k-2*d),"sharp grid lower");
    assert(Math.max(tv2(ws[0],ws[1]),tv2(ws[0],ws[2]),tv2(ws[1],ws[2]))===best,"witness");
    receipt.gridModels++;
  }
  function words(L,fn){let a=[];function rec(){if(a.length===L){fn(a);return;}for(const x of E){a.push(x);rec();a.pop();}}rec();}
  const pow=(x,n)=>BigInt(x)**BigInt(n);
  const abs=x=>x<0n?-x:x;
  for(let d=1;d<=5;d++)for(let k=0;k<=d;k++)for(let L=1;L<=6;L++){
    let lockMass=[0n,0n,0n],freshMass=[0n,0n,0n],lockTV=0n,freshTV=0n;
    words(L,a=>{
      let p=G.map(g=>G.filter(h=>h!==g).reduce((total,h)=>{
        if(a.some(x=>x!==0&&x!==(g|h)))return total;
        let n=a.filter(x=>x!==0).length;
        return total+pow(k,n)*pow(d-k,L-n);
      },0n));
      let f=G.map(g=>a.reduce((acc,x)=>acc*BigInt(local(g,d,k)[E.indexOf(x)]),1n));
      p.forEach((v,i)=>lockMass[i]+=v);f.forEach((v,i)=>freshMass[i]+=v);
      lockTV+=abs(p[0]-p[1]);freshTV+=abs(f[0]-f[1]);
    });
    assert(lockMass.every(v=>v===2n*pow(d,L)),"lock norm");
    assert(freshMass.every(v=>v===pow(2*d,L)),"fresh norm");
    assert(lockTV===2n*(pow(d,L)-pow(d-k,L)),"lock TV");
    if(3*k<=2*d)assert(freshTV===0n,"threshold privacy");
    if(k===d)assert(freshTV===2n*(pow(2*d,L)-pow(d,L)),"always-flip fresh TV");
    if(L===1)assert(freshTV===BigInt(2*Math.max(0,3*k-2*d)),"one transition TV");
    receipt.productAndPairChecks++;
    // Independent reset blocks: overlap is empty-block mass plus common pair mass.
    const den=2n*pow(d,L), overlap=pow(d,L)+pow(d-k,L);
    for(let R=1;R<=8;R++){
      let direct=0n; // enumerate number of informative blocks with binomial multiplicity
      let choose=1n;
      for(let j=0;j<=R;j++){
        direct+=choose*(2n*pow(d-k,L))**BigInt(R-j)*(pow(d,L)-pow(d-k,L))**BigInt(j);
        if(j<R)choose=choose*BigInt(R-j)/BigInt(j+1);
      }
      assert(direct===overlap**BigInt(R),"reset overlap");assert(direct<=den**BigInt(R),"reset range");receipt.resetChecks++;
    }
  }
  for(let L=2;L<=8;L++){
    const counts=G.map(()=>new Map()), deletes=G.map(()=>Array.from({length:L},()=>new Map()));
    const source=G.map(()=>new Map()); let tv=0, common=0, nonempty=0;
    const inc=(m,key)=>m.set(key,(m.get(key)||0)+1);
    words(L,a=>{
      const prefix=a.slice(0,-1).reduce((u,v)=>u^v,0), target=7^prefix;
      const via=G.map(g=>{
        // Given the actual source's final bit, require it and choose the other
        // mismatched coordinate uniformly. Prefix has uniform even words.
        const allowed=G.filter(h=>h!==g).map(h=>target^h);
        return allowed.includes(a[L-1])?1:0;
      });
      const aggregate=a.reduce((u,v)=>u^v,0);
      assert(same(via,G.map(g=>aggregate!==0&&(aggregate&g)?1:0)),"causal vs parity oracle");
      assert(sum(via)===0||sum(via)===2,"support");
      if(sum(via)>0)nonempty++;
      if(via[0]&&via[1])common++;
      tv+=Math.abs(via[0]-via[1]);
      for(let j=0;j<3;j++)if(via[j]){
        inc(counts[j],a.join(","));
        const own=a.map(x=>x&G[j]?1:0);
        assert(sum(own)%2===1,"odd source");
        inc(source[j],own.join(""));
        for(let t=0;t<L;t++)inc(deletes[j][t],a.filter((_,i)=>i!==t).join(","));
      }
      receipt.delayedTranscripts++;
    });
    const den=2*4**(L-1);
    assert(counts.every(m=>m.size===den),"transcript norm");
    assert(tv===den&&common===den/2,"sharp pair TV");
    assert(nonempty===3*4**(L-1),"Bayes support");
    for(let j=0;j<3;j++){
      assert(source[j].size===2**(L-1)&&[...source[j].values()].every(v=>v===2**L),"uniform source paths");
      receipt.sourcePathChecks+=source[j].size;
      for(const m of deletes[j]){
        assert(m.size===4**(L-1)&&[...m.values()].every(v=>v===2),"every deletion uniform");receipt.projectionChecks+=m.size;
      }
    }
  }
  let refusals=0;
  for(const a of [[0,1,0],[1,0,0],[1,2,-1],[1,2,3],[1,2,0.5]]){try{local(...a)}catch(e){refusals++}}
  assert(refusals===5,"input refusal");
  receipt.refusals=refusals;return receipt;
}
console.log(JSON.stringify(lab(),null,2));
