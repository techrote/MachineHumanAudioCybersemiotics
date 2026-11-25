// Synthetic mathematical laboratory; run node lab.js. No dependencies.
function lab(){
 const ok=(c,msg)=>{if(!c)throw Error(msg)};
 const pop=x=>{let k=0;while(x){x&=x-1;k++}return k};
 const s=(z,i)=>((z>>i)&1)?-1:1;
 const counts={witnesses:0,balancedTargets:0,targetCells:0,decoderCells:0,posteriorVectors:0,posteriorSignSums:0,smallChannels:0,feasibleSmallChannels:0,majorizationVectors:0};
 function signedMean(v){let a=0;for(let z=0;z<2**v.length;z++){let b=0;for(let i=0;i<v.length;i++)b+=v[i]*s(z,i);a+=Math.abs(b)}return a}
 function targetScore(rows,mask){let a=0;for(let j=0;j<rows[0].length;j++){let p=0,n=0;for(let x=0;x<rows.length;x++)if((mask>>x)&1)p+=rows[x][j];else n+=rows[x][j];a+=Math.max(p,n);counts.targetCells++}return a}
 function allTargets(rows){let best=0;const m=rows.length/2;for(let mask=0;mask<2**(2*m);mask++)if(pop(mask)===m){best=Math.max(best,targetScore(rows,mask));counts.balancedTargets++}return best}
 function check(m,D,T,compressed){
  const z=Array.from({length:2**m},(_,i)=>i).filter(i=>!compressed||m===2||pop(i&7)%2===0);
  const K=z.length, den=K*D, W=z.map((_,j)=>compressed?T[0]+(j===0?(D-T[0])*K:0):D);
  const rows=Array.from({length:2*m},(_,x)=>z.map((v,j)=>W[j]+s(v,x>>1)*(x%2?-1:1)*T[x>>1]));
  for(const row of rows)ok(row.every(v=>v>=0)&&row.reduce((a,b)=>a+b,0)===den,"row");
  for(let i=0;i<m;i++){
   // Actual pair-collapse map. Result i*2 is the shared output; all other
   // source states except i*2+1 remain unchanged.
   const fibres=Array.from({length:2*m},()=>[]);
   for(let x=0;x<2*m;x++)fibres[x===2*i+1?2*i:x].push(x);
   let correct=0;
   for(const f of fibres)if(f.length)for(let j=0;j<K;j++){
    correct+=Math.max(...f.map(x=>rows[x][j]));counts.decoderCells+=f.length
   }
   ok(2*m*den-correct===K*(D-T[i]),"direct decoder error");
  }
  const best=allTargets(rows);
  const A=signedMean(T);
  // Bayes optimum = 1/2 + A/(2*m*D*2^m).
  ok(best*2**m===m*den*2**m+K*A,"target optimum");
  if(compressed){
   // Exact positive mass per antipodal pair (or sign vector for m=2)
   const mass=new Map();
   for(let j=0;j<K;j++){const v=m===2?z[j]:Math.min(z[j],z[j]^((1<<m)-1));mass.set(v,(mass.get(v)||0)+W[j])}
   ok(mass.size===K&&[...mass.values()].sort((a,b)=>b-a).join(",")===[...W].sort((a,b)=>b-a).join(","),"distinct classes");
   ok(Math.min(...W)===T[0],"minimum mass");
  }
  counts.witnesses++;
  return {m,T,D,compressed,labels:K,score:best/(2*m*den),entropy:W.reduce((a,w)=>w?a-w/den*Math.log2(w/den):a,0)};
 }
 const examples=[];
 for(const m of [2,4,6,8]){
  for(const T of (m===8?[1]:[1,2,4]))examples.push(check(m,4,Array(m).fill(T),true));
  if(m<8){
   examples.push(check(m,4,Array.from({length:m},(_,i)=>i%2?0:4),false));
   examples.push(check(m,4,Array.from({length:m},(_,i)=>i%2?1:3),false));
  }
 }
 for(const m of [2,4,6]){
  const cm=Array.from({length:2**m},(_,i)=>pop(i)).filter(k=>k===m/2).length;
  for(let n=0;n<4**m;n++){
   const v=Array.from({length:m},(_,i)=>(n>>(2*i))&3),sum=v.reduce((a,b)=>a+b,0),A=signedMean(v);
   ok(A>=cm*sum,"Rademacher convexity");ok((A===cm*sum)===v.every(x=>x===v[0]),"strict equality");
   counts.posteriorVectors++;counts.posteriorSignSums+=2**m
  }
 }
 function compositions(n,k){if(k===1)return [[n]];return Array.from({length:n+1},(_,i)=>compositions(n-i,k-1).map(v=>[i,...v])).flat()}
 for(const L of [2,3]){
  const D=2,rr=compositions(D,L);let best=Infinity;
  for(const a of rr)for(const b of rr)for(const c of rr)for(const d of rr){
   const rows=[a,b,c,d];counts.smallChannels++;
   if([0,2].some(i=>rows[i].reduce((v,x,j)=>v+Math.min(x,rows[i+1][j]),0)>1))continue;
   counts.feasibleSmallChannels++;
   const score=allTargets(rows);best=Math.min(best,score);
   ok(score>5,"no two/three label exact optimum");
  }
  examples.push({m:2,labels:L,gridDenominator:D,best:best/8});
 }
 // Exhaust integer label masses with K required classes, each >= one unit.
 // Sorting/prefix sums verify the extremal vector majorizes every candidate.
 for(const K of [3,4,8])for(const D of [K,K+1,K+3]){
  const extreme=[D-K+1,...Array(K-1).fill(1)];
  for(const v of compositions(D-K,K)){
   const w=v.map(x=>x+1).sort((a,b)=>b-a);let e=0,a=0;
   for(let i=0;i<K;i++){e+=extreme[i];a+=w[i];ok(a<=e,"majorization")}
   counts.majorizationVectors++
  }
 }
 // Chance-level special case: no information, one label.
 const constant=[[1],[1],[1],[1]];ok(allTargets(constant)===2,"chance control");
 // Equal average error, unequal worst privacy optimum.
 const uniform=examples.find(x=>x.m===4&&x.compressed&&x.T[0]===2);
 const uneven=examples.find(x=>x.m===4&&!x.compressed&&x.T[0]===4);
 ok(uniform.score===0.59375&&uneven.score===0.625,"averaged budget countercontrol");
 return {counts,examples,pass:true};
}
console.log(JSON.stringify(lab(),null,2));
