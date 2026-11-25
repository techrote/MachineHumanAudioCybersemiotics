'use strict';
function laboratory(){
 const assert=(x,m)=>{if(!x)throw Error(m)};
 const pairs=n=>Array.from({length:n},(_,i)=>Array.from({length:n-i-1},(_,j)=>[i,i+j+1])).flat();
 function histories(n){
  const p=pairs(n), out=[];
  function walk(cs,d,h){
   if(cs.length===1){out.push(p.map(([a,b])=>d[a*n+b]));return}
   for(let i=0;i<cs.length;i++)for(let j=i+1;j<cs.length;j++){
    const e=d.slice();for(const a of cs[i])for(const b of cs[j])e[a*n+b]=e[b*n+a]=h;
    walk(cs.filter((_,k)=>k!==i&&k!==j).concat([cs[i].concat(cs[j])]),e,h+1)
   }
  }
  walk(Array.from({length:n},(_,i)=>[i]),Array(n*n).fill(0),1);return out
 }
 function reconstruct(n,oracle){
  const m=Array.from({length:n},()=>Array(n).fill(0));let queries=0;
  function heavy(S){
   if(S.length===1)return S[0];
   let h=0;for(const a of S)for(const b of S)h=Math.max(h,m[a][b]);
   const A=S.filter(b=>m[S[0]][b]<h),B=S.filter(b=>m[S[0]][b]===h);
   assert(A.length&&B.length,"split");return heavy(A.length>=B.length?A:B)
  }
  for(let x=1;x<n;x++){
   let S=Array.from({length:x},(_,i)=>i);
   function learn(T){
    if(!T.length)return;
    const r=heavy(T),h=oracle(x,r);queries++;m[x][r]=m[r][x]=h;
    const unresolved=[];
    for(const y of T)if(y!==r){if(m[r][y]===h)unresolved.push(y);else m[x][y]=m[y][x]=Math.max(h,m[r][y])}
    assert(unresolved.length<=Math.floor(T.length/2),"heavy recursion");learn(unresolved)
   }
   const before=queries;learn(S);assert(queries-before<=1+Math.floor(Math.log2(x)),"query bound")
  }
  return {vector:pairs(n).map(([a,b])=>m[a][b]),queries}
 }
 const profiles=[];let total=0, projections=0, collisionTests=0, weightedTests=0;
 for(let n=3;n<=6;n++){
  const P=pairs(n),M=P.length,H=histories(n),keys=H.map(x=>x.join(","));assert(new Set(keys).size===H.length,"unique histories");
  let expected=1;for(let k=n;k>=2;k--)expected*=k*(k-1)/2;assert(expected===H.length,"count");
  let maxQueries=0,querySum=0;
  const indices=new Map(P.map(([a,b],i)=>[a*n+b,i]));
  for(const v of H){const r=reconstruct(n,(a,b)=>v[indices.get(Math.min(a,b)*n+Math.max(a,b))]);assert(r.vector.every((x,i)=>x===v[i]),"reconstruction");maxQueries=Math.max(maxQueries,r.queries);querySum+=r.queries}
  for(let i=0;i<M;i++){
   let s=new Set(H.map(v=>v.filter((_,j)=>j!==i).join(",")));assert(s.size===H.length,"one missing pair");projections+=H.length;
   for(let j=i+1;j<M;j++){
    let seen=new Map(),found=false;
    for(const v of H){let k=v.filter((_,l)=>l!==i&&l!==j).join(",");if(seen.has(k)){const u=seen.get(k);assert(v[i]!==u[i]&&v[j]!==u[j],"two-coordinate witness");found=true;break}seen.set(k,v)}
    assert(found,"every two omissions ambiguous");collisionTests++;
   }
  }
  if(n<=5)for(let trial=0;trial<15;trial++){
   const w=P.map((_,i)=>(i*17+trial*13+i*trial*7)%5);let min=Infinity;
   for(let i=0;i<H.length;i++)for(let j=i+1;j<H.length;j++){let s=0;for(let k=0;k<M;k++)if(H[i][k]!==H[j][k])s+=w[k];min=Math.min(min,s)}
   const sw=w.slice().sort((a,b)=>a-b);assert(min===sw[0]+sw[1],"weighted distance");weightedTests++
  }
  profiles.push({n,histories:H.length,pairs:M,maxQueries,querySum,adaptiveBound:Array.from({length:n-1},(_,i)=>1+Math.floor(Math.log2(i+1))).reduce((a,b)=>a+b,0)});total+=H.length
 }
 // Explicit equal-height failure: same barcode with two merges at height 1 and 2? one-pair ambiguity if ties allowed:
 // AB merges at 1 or 2, CD at 1, EF at 2; barcode multiplicities differ, so instead allow multifurcation:
 // dAB changes 1->2; barcode changes unless another merge changes. Untrusted barcode is the clean negative control.
 const A=[1,3,3],B=[2,3,3];assert(A.filter((_,i)=>i!==0).join()===B.filter((_,i)=>i!==0).join(),"untrusted heights negative");
 return {profiles,totalHistories:total,oneOmissionProjections:projections,twoOmissionDictionaries:collisionTests,weightedCensuses:weightedTests,negativeControl:{a:A,b:B,contract:"untrusted barcode"},status:"PASS"}
}
if (require.main === module) console.log(JSON.stringify(laboratory(), null, 2));
module.exports = laboratory;
