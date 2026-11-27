// Dependency-free exact verifier, Node.js or V8. All fixture counts are small integers.
function check(p,msg){if(!p)throw Error(msg)}
const fixtures=[
 [5,"201200011202122121001010221102"],
 [6,"202112210101100"],
 [6,"102120001010122220112002211202"],
 [6,"121020101200120102102122210120000112020110022"],
 [6,"120012212210021020201122121000201120021120001011022212122010"],
 [6,"210010210012012221212020101102221121020121200112122011021200101000211120021122201100012102"]
];
// enumerate all subsets of the nine cells, independent of DP
const chains=[];
for(let m=1;m<512;m++){
 const c=Array.from({length:9},(_,i)=>i).filter(i=>m>>i&1);
 if([1,-1].some(s=>c.every((v,i)=>!i||(Math.floor(v/3)>Math.floor(c[i-1]/3)&&s*(v%3-c[i-1]%3)>0))))chains.push(c);
}
const mass=w=>Math.max(...chains.map(c=>c.reduce((s,i)=>s+w[i],0)));
function dp(w,q,r){let best=0;for(let sign of [1,-1]){
 const D=Array(q*r).fill(0);
 for(let a=0;a<q;a++)for(let b=0;b<r;b++){let j=sign===1?b:r-1-b, m=0;
 for(let u=0;u<a;u++)for(let v=0;v<b;v++)m=Math.max(m,D[u*r+v]);
 D[a*r+b]=w[a*r+j]+m;best=Math.max(best,D[a*r+b]);}
}return best;}
function matrix(x,s,u){let w=Array(9).fill(0);for(let t=0;t<x.length;t++)w[3*x[(t+s)%x.length]+x[(t+u)%x.length]]++;return w}
function qualify(K,word){const x=Array.from(word,Number), N=x.length;let L=0,pairs=[];
 for(let s=0;s<K;s++)for(let u=s+1;u<K;u++){
 let w=matrix(x,s,u), l=mass(w);check(l===dp(w,3,3),"DP discrepancy");L=Math.max(L,l);pairs.push({s,u,w,L:l});}
 const target=K===5?4*N/15:Math.floor(4*N/15)+1;
 check(L===target,"fixture failed");
 const middle=x.map(v=>+(v===1)), occ=Array(K+1).fill(0);
 for(let t=0;t<N;t++)occ[Array.from({length:K},(_,s)=>middle[(t+s)%N]).reduce((a,b)=>a+b,0)]++;
 if(K===5){check(N===30&&occ[1]===10&&occ[2]===20,"occupancy");
 check(pairs.every(p=>p.w.join()==="3,4,3,4,2,4,3,4,3"),"five-phase pair inventory");}
 const autocorr=Array.from({length:K-1},(_,i)=>middle.reduce((a,v,t)=>a+(2*v-1)*(2*middle[(t+i+1)%N]-1),0));
 return {K,N,word,L,d:N-L,maxErrors:Math.floor((N-L-1)/2),occupancy:occ,middleSignAutocorrelation:autocorr,pairs};
}
// Exhaust all middle masks then extreme assignments at N=15, K=5.
// The occupancy condition is necessary for equality (not assumed sufficient).
function exhaustive15(){let masks=0,words=0,valid=0,min=15;
 for(let mask=0;mask<1<<15;mask++){
  let z=Array.from({length:15},(_,i)=>mask>>i&1);
  let occ=Array.from({length:15},(_,t)=>Array.from({length:5},(_,s)=>z[(t+s)%15]).reduce((a,b)=>a+b,0));
  if(occ.some(v=>v!==1&&v!==2)||occ.filter(v=>v===2).length!==10)continue;
  masks++;let p=z.map((v,i)=>v?-1:i).filter(i=>i>=0);
  for(let bits=0;bits<1<<p.length;bits++){
   let x=z.slice();for(let i=0;i<p.length;i++)x[p[i]]=2*(bits>>i&1);
   words++;let L=0;for(let d=1;d<=4;d++)L=Math.max(L,mass(matrix(x,0,d)));
   min=Math.min(min,L);if(L<=4)valid++;
  }
 }
 check(words===310272&&valid===0,"exhaustive mismatch");return {masks,words,valid,minimumAmongOccupancyQualified:min};
}
let seed=805;function rand(n){seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed%n}
function decode(x,K,y,e){const ranks=[...new Set(y.filter(v=>v!==null))].sort((a,b)=>a-b),n=y.length;
 const cand=[];for(let s=0;s<K;s++){let w=Array(3*ranks.length).fill(0),keep=0;
 for(let i=0;i<n;i++)if(y[i]!==null){w[x[(i+s)%n]*ranks.length+ranks.indexOf(y[i])]++;keep++;}
 if(dp(w,3,ranks.length)>=keep-e)cand.push(s);
 }return cand;}
function tests(profiles){let trials=0;for(let p of profiles){let x=Array.from(p.word,Number),N=p.N;
 for(let t=0;t<40;t++){let s=rand(p.K),f=(p.d-1)%2,e=Math.floor((p.d-1-f)/2);
 const map=[-19,3,71].map(v=>v*(t%2?1:-1)+t);
 let y=x.map((_,i)=>map[x[(i+s)%N]]),order=x.map((_,i)=>i);
 for(let i=N-1;i>0;i--){let j=rand(i+1);[order[i],order[j]]=[order[j],order[i]];}
 for(let i=0;i<f;i++)y[order[i]]=null;
 for(let i=f;i<f+e;i++)y[order[i]]=1000+rand(1000);
 check(decode(x,p.K,y,e).join()===String(s),"candidate failure");trials++;
 }}return trials;}
const profiles=fixtures.map(([K,w])=>qualify(K,w));
const receipt={chainCount:chains.length,profiles,exhaustive15:exhaustive15(),syntheticDecodes:tests(profiles),assertionFailures:0};
console.log(JSON.stringify(receipt,null,2));
