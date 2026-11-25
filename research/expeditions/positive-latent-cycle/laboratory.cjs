"use strict";
function census(){
 const rows=[];
 for(const [n,d] of [...Array.from({length:8},(_,i)=>[i+3,1]),[3,2],[4,2]]){
  const N=n**d;
  const allowed=(i,j)=>{for(let k=0;k<d;k++){let a=i%n,b=j%n;if(b!==a&&b!==(a+1)%n)return false;i=Math.floor(i/n);j=Math.floor(j/n)}return true};
  const mat=Array.from({length:N},(_,i)=>Array.from({length:N},(_,j)=>allowed(i,j)?1:0));
  const adj=mat.map(row=>row.reduce((a,v,j)=>a+(v<<j),0));
  const pop=x=>{let c=0;while(x){x&=x-1;c++}return c};
  let max=0,rectangles=0,maximum=0;
  for(let m=1;m<2**N;m++){let a=(1<<N)-1;for(let i=0;i<N;i++)if(m>>i&1)a&=adj[i];let b=pop(a),r=pop(m),size=b*r;rectangles+=2**b-1;if(size>max){max=size;maximum=1}else if(size===max)maximum++}
  if(max!==2**d)throw Error("rectangle bound");
  let B=mat.map(row=>row.map(BigInt)),rank=0;
  for(let j=0;j<N;j++){let p=B.findIndex((row,i)=>i>=rank&&row[j]!==0n);if(p<0)continue;[B[rank],B[p]]=[B[p],B[rank]];let z=B[rank][j];for(let i=rank+1;i<N;i++){let v=B[i][j];if(v!==0n)for(let k=j;k<N;k++)B[i][k]=B[i][k]*z-v*B[rank][k]}rank++}
  if(rank!==(n%2?n:n-1)**d)throw Error("rank");
  rows.push({n,d,rank,max,rectangles,maximum,row_subsets:2**N-1});
 }
 const cap=[];let pairs=0;
 function vectors(n,D,T){
  let out=[];function walk(a,left,frac){if(a.length===n){if(!left)out.push(a);return}for(let x of [0,D,...(!frac&&T%D?[T%D]:[])])if(x<=left)walk([...a,x],left-x,frac||(x>0&&x<D))}walk([],T,false);return out
 }
 for(let n=3;n<=7;n++)for(let D=2;D<=4;D++)for(let T=1;T<=n*D;T++){
  let vs=vectors(n,D,T),max=0;for(let x of vs)for(let y of vs){let z=x.reduce((a,v,i)=>a+v*(y[i]+y[(i+1)%n]),0);max=Math.max(max,z);pairs++}
  let expected=T<=D?T*T:T<=(n-1)*D?2*T*D-D*D:2*T*D-D*D+(T-(n-1)*D)**2;
  if(max!==expected)throw Error(`cap ${n} ${D} ${T} ${max} ${expected}`);
  cap.push({n,D,T,vertices:vs.length,max});
 }
 let tilings=[];
 for(let n=3;n<=9;n++){let c=0;for(let mask=0;mask<2**(2*n);mask++){let valid=true;for(let i=0;i<n;i++){let row=(mask>>i)&1,col=(mask>>(n+i))&1,next=(mask>>(n+(i+1)%n))&1;if(row+col!==1||row+next!==1){valid=false;break}}if(valid)c++}if(c!==2)throw Error("rigidity");tilings.push({n,tilings:c,masks:2**(2*n)})}
 let divisors=[];for(let n=3;n<=48;n++)for(let k=2;k<n;k++)if(n%k===0){let t=n/k,good=0,bad=0,counts=Array(n).fill(0),cols=Array(n).fill(0);for(let b=0;b<k;b++)for(let i=b*t;i<(b+1)*t;i++)for(let j=b*t+1;j<=(b+1)*t;j++){let jj=j%n;counts[i]++;cols[jj]++;if(jj===i||jj===(i+1)%n)good++;else bad++}if(!counts.every(x=>x===t)||!cols.every(x=>x===t)||good!==k*(2*t-1)||bad!==k*(t-1)**2)throw Error("block");divisors.push({n,k,t,good,bad})}
 return {rectangle_profiles:rows,cap_profiles:cap,cap_vertex_pairs:pairs,tiling_profiles:tilings,divisor_profiles:divisors,assertions:"PASS"};
}
console.log(JSON.stringify(census(),null,2));
