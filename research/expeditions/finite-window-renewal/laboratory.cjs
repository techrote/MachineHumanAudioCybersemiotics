"use strict";
function laboratory(){
  const assert=(x,msg)=>{if(!x)throw Error(msg)};
  const gcd=(a,b)=>b?gcd(b,a%b):a;
  const rat=(a,b)=>{let g=gcd(a,b);return `${a/g}/${b/g}`};
  const sum=a=>a.reduce((x,y)=>x+y,0);
  const mean=p=>sum(p.map((v,i)=>v*(i+1)));
  const surv=(p,k)=>sum(p.slice(k-1));
  const stop=(p,h)=>sum(p.map((v,i)=>v*Math.max(i+1-h,0)));
  function* compositions(d,m){
    if(m===1){yield [d];return}
    for(let i=0;i<=d;i++)for(let x of compositions(d-i,m-1))yield [i,...x];
  }
  const D=4, maxW=6, on=[...compositions(D,5)], off=[...compositions(D,3)];
  const sigToWord=Array.from({length:maxW+1},()=>new Map());
  const wordToSig=Array.from({length:maxW+1},()=>new Map());
  const counts={profiles:0,wordComparisons:0,signatureChecks:0,stopLossBounds:0,jointFeasibleGridPoints:0,jointInfeasibleGridPoints:0,jointConstructed:0};
  // Literal hidden residual-state propagation. Integer unnormalized weights.
  function literal(ps,w){
    const map=new Map();
    function walk(s,left,k,word,weight){
      word+=s;
      if(k===1){map.set(word,(map.get(word)||0)+weight);return}
      if(left>1)walk(s,left-1,k-1,word,weight*D);
      else for(let i=0;i<ps[1-s].length;i++)if(ps[1-s][i])walk(1-s,i+1,k-1,word,weight*ps[1-s][i]);
    }
    for(let s=0;s<2;s++)for(let l=1;l<=ps[s].length;l++)if(surv(ps[s],l))walk(s,l,w,"",surv(ps[s],l));
    return map;
  }
  function formula(ps,word){
    const runs=word.match(/0+|1+/g);
    if(runs.length===1)return stop(ps[+word[0]],word.length-1)*D**(word.length-1);
    let v=surv(ps[+runs[0][0]],runs[0].length);
    for(let i=1;i<runs.length-1;i++)v*=ps[+runs[i][0]][runs[i].length-1]||0;
    const end=runs[runs.length-1];
    return v*surv(ps[+end[0]],end.length)*D**(word.length-runs.length);
  }
  for(let p of on)for(let q of off){
    const ps=[q,p], T=mean(p)+mean(q);counts.profiles++;
    for(let w=2;w<=maxW;w++){
      const map=literal(ps,w), denom=T*D**(w-1), words=[];
      assert(sum([...map.values()])===denom,"normalization");
      for(let i=0;i<2**w;i++){
        const word=i.toString(2).padStart(w,"0"), x=map.get(word)||0;
        assert(x===formula(ps,word),"run factorization");
        words.push(rat(x,denom));counts.wordComparisons++;
      }
      const sig=JSON.stringify([mean(q),mean(p),...ps.map(z=>Array.from({length:w-2},(_,i)=>z[i]||0))]);
      const receipt=words.join(",");
      if(sigToWord[w].has(sig))assert(sigToWord[w].get(sig)===receipt,"sufficiency");
      if(wordToSig[w].has(receipt))assert(wordToSig[w].get(receipt)===sig,"necessity");
      sigToWord[w].set(sig,receipt);wordToSig[w].set(receipt,sig);counts.signatureChecks++;
    }
  }
  // Check conditional tail bounds with integer weights, no numerical tolerance.
  for(let p of on)for(let a=1;a<=5;a++){
    let t=0,m=0;for(let l=a;l<=5;l++){t+=p[l-1];m+=l*p[l-1]}
    if(!t)continue;
    for(let h=a;h<=5;h++){
      const s=stop(p,h);
      assert(s>=Math.max(0,m-h*t),"Jensen lower");
      if(a<5)assert(s*(5-a)<=(m-a*t)*(5-h),"chord upper");
      else assert(s===0,"degenerate tail");
      counts.stopLossBounds++;
    }
  }
  // Joint event-count and occupancy polygon. All coordinates in quarter units.
  // Construct endpoint masses explicitly in a common integer denominator.
  for(let a=1;a<=4;a++)for(let h=a;h<5;h++)for(let m=a*D;m<=5*D;m++)for(let q=0;q<=D;q++)for(let s=0;s<=D*(5-h);s++){
    const short=m-h*q-s;
    const feasible=q<=s&&s<=(5-h)*q&&a*(D-q)<=short&&short<=h*(D-q);
    if(!feasible){counts.jointInfeasibleGridPoints++;continue}
    counts.jointFeasibleGridPoints++;
    const A=h-a||1,B=5-h-1||1,scale=A*B,weights=Array(5).fill(0);
    if(h===a)weights[a-1]+=(D-q)*scale;
    else {weights[h-1]+=(short-a*(D-q))*B;weights[a-1]+=(h*(D-q)-short)*B}
    if(h+1===5)weights[4]+=q*scale;
    else {weights[4]+=(s-q)*A;weights[h]+=(q*(5-h)-s)*A}
    assert(weights.every(x=>x>=0)&&sum(weights)===D*scale,"joint mass");
    assert(mean(weights)===m*scale&&stop(weights,h)===s*scale&&sum(weights.slice(h))===q*scale,"joint witness");
    counts.jointConstructed++;
  }
  // Circular score: equal windows through 5; not an iid renewal realization claim.
  const build=lengths=>lengths.flatMap(l=>[...Array(l).fill(1),...Array(4).fill(0)]);
  const gate=(seq,h)=>{let age=0;return seq.map(v=>{age=v?age+1:0;return +(age>h)})};
  const hist=(seq,w)=>{let out={};for(let i=0;i<seq.length;i++){let k=Array.from({length:w},(_,j)=>seq[(i+j)%seq.length]).join("");out[k]=(out[k]||0)+1}return Object.entries(out).sort()};
  const A=build(Array(20).fill(5)),B=build([...Array(19).fill(4),24]);
  for(let w=1;w<=5;w++)assert(JSON.stringify(hist(A,w))===JSON.stringify(hist(B,w)),"score windows");
  assert(JSON.stringify(hist(A,6))!==JSON.stringify(hist(B,6)),"score longer witness");
  const ga=gate(A,4),gb=gate(B,4), episodes=x=>x.filter((v,i)=>v&&!x[(i+x.length-1)%x.length]).length;
  assert(sum(ga)===sum(gb)&&sum(ga)===20&&episodes(ga)===20&&episodes(gb)===1,"score gated");
  return {model:"exact integer weights; independent alternating renewal; circular score separate",counts,distinctWindowLaws:Object.fromEntries(sigToWord.slice(2).map((v,i)=>[i+2,v.size])),score:{slots:A.length,rawOnSlots:[sum(A),sum(B)],gatedOnSlots:[sum(ga),sum(gb)],gatedEpisodes:[episodes(ga),episodes(gb)],matchedWindowLengths:[1,2,3,4,5],firstDifference:6},assertions:"passed"};
}
console.log(JSON.stringify(laboratory(),null,2));
