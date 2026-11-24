"use strict";
const assert=(p,msg)=>{if(!p)throw Error(msg)};
const stats={balancedTargets:0,targetCountVectors:0,transversalCells:0,parityCells:0,decoderCells:0,posteriorWeightCases:0,repeatSequences:0};
function* words(n,b){if(!n){yield [];return}for(const w of words(n-1,b))for(let i=0;i<b;i++)yield [...w,i]}
const parity=x=>{let v=0;while(x){v^=x&1;x>>>=1}return v};
const choose=(n,k)=>{let r=1;for(let i=1;i<=k;i++)r=r*(n-i+1)/i;return r};
function* balanced(n,k,start=0,mask=0){if(!k){yield mask;return}for(let i=start;i<=n-k;i++)yield* balanced(n,k-1,i+1,mask+2**i)}
// States encoded as coset index * h + within-coset coordinate. Each intervention merges exactly one pair.
function decoder(rows,m,h){
 for(let g=0;g<m;g++)for(let a=0;a<h;a++)for(let b=a+1;b<h;b++)for(const row of rows){
  const u=g*h+a,v=g*h+b,seen=new Map;
  for(const x of row){const y=x===v?u:x;assert(!seen.has(y),"decoder collision");seen.set(y,x);stats.decoderCells++}
 }
}
for(const [m,h] of [[2,2],[2,4],[4,2],[4,4],[8,2]]){
 const n=m*h,rows=Array.from(words(m,h),w=>w.map((a,i)=>i*h+a));
 decoder(rows,m,h);
 for(let x=0;x<n;x++)assert(rows.filter(row=>row.includes(x)).length*h===rows.length,"prior");
 let worst=0;
 for(const mask of balanced(n,n/2)){
  let bias=0;
  for(const row of rows){let s=0;for(const x of row)s+=((mask>>>x)&1)?1:-1;bias+=Math.abs(s);stats.transversalCells++}
  worst=Math.max(worst,bias);stats.balancedTargets++;
 }
 assert(worst*2**m===rows.length*m*choose(m,m/2),"Boolean optimum");
 // Independent polynomial distribution oracle using counts of positive signs in each coset.
 let worst2=0;
 for(const t of words(m,h+1)){
  if(t.reduce((a,b)=>a+b,0)!==n/2)continue;
  let law=[1];
  for(const q of t){const next=Array(law.length+1).fill(0);law.forEach((v,i)=>{next[i]+=v*(h-q);next[i+1]+=v*q});law=next}
  const score=law.reduce((s,v,i)=>s+v*Math.abs(2*i-m),0);
  worst2=Math.max(worst2,score);stats.targetCountVectors++;
 }
 assert(worst2===worst,"count-vector oracle");
}
// Affine transversal: each column of A independently chooses a k-bit vector.
for(const [ell,k] of [[1,1],[2,1],[1,2],[2,2],[3,1],[3,2],[4,1]]){
 const m=2**ell,h=2**k,n=m*h,rows=[];
 for(const A of words(ell,h))for(let b=0;b<h;b++){
  const row=[];
  for(let y=0;y<m;y++){let a=b;for(let j=0;j<ell;j++)if(y&(1<<j))a^=A[j];row.push(y*h+a)}
  rows.push(row)
 }
 decoder(rows,m,h);
 for(let s=1;s<n;s++){
  let bias=0;
  for(const row of rows){bias+=Math.abs(row.reduce((z,x)=>z+1-2*parity(x&s),0));stats.parityCells++}
  assert(bias===(s%h?rows.length:0),"parity optimum")
 }
 for(let x=0;x<n;x++)assert(rows.filter(row=>row.includes(x)).length*h===rows.length,"prior");
}
// Convex lower bound over integer-weight posterior choices (zeros allowed).
for(const m of [2,4,8])for(const w of words(m,4)){
 const total=w.reduce((a,b)=>a+b,0);if(!total)continue;
 let bias=0;for(let mask=0;mask<2**m;mask++)bias+=Math.abs(w.reduce((s,v,i)=>s+(((mask>>i)&1)?v:-v),0));
 assert(bias>=total*choose(m,m/2),"Rademacher lower bound");stats.posteriorWeightCases++;
}
// Repeated fresh uniform-transversal labels: enumerate possible intersections for a fixed source.
for(const [m,h,r] of [[2,2,2],[4,2,2],[4,2,3],[4,4,2],[4,4,3]]){
 const rows=Array.from(words(m-1,h),w=>[0,...w]);const hist=Array(m+1).fill(0);
 function visit(first,depth){if(depth===r){hist[first.filter(v=>v>=0).length]++;stats.repeatSequences++;return}
  for(const row of rows)visit(first.map((v,i)=>v===row[i]?v:-1),depth+1)}
 for(const row of rows)visit(row,1);
 const den=h**(r-1),factor=rows.length;
 for(let z=0;z<m;z++)assert(hist[z+1]===factor*choose(m-1,z)*(den-1)**(m-1-z),"repeat intersection law");
}
console.log(JSON.stringify(stats,null,2));
