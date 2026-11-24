"use strict";
function arithmetic(){
const assert=(p,m)=>{if(!p)throw Error(m)};
const gcd=(a,b)=>{a=Math.abs(a);b=Math.abs(b);while(b){[a,b]=[b,a%b]}return a;};
const all=(n)=>Array.from({length:n*(n-1)},(_,k)=>[k%n,1+Math.floor(k/n)]);
const row=(n,[i,l])=>Array.from({length:n},(_,j)=>Number((j-i+n)%n<l));
function det(M){
 let A=M.map(r=>r.map(BigInt)),n=A.length,sign=1n,prev=1n;
 for(let j=0;j<n-1;j++){let i=j;while(i<n&&A[i][j]===0n)i++;if(i===n)return 0;if(i!==j){[A[i],A[j]]=[A[j],A[i]];sign=-sign;}let p=A[j][j];for(let k=j+1;k<n;k++){for(let l=j+1;l<n;l++){let a=p*A[k][l]-A[k][j]*A[j][l];assert(a%prev===0n,"nonexact Bareiss");A[k][l]=a/prev;}A[k][j]=0n;}prev=p;}
 return Number(sign*A[n-1][n-1]);
}
function gain(n,F){
 const adj=Array.from({length:n},()=>[]);for(const [i,l] of F){let j=(i+l)%n,w=Number(i+l>=n);adj[i].push([j,w]);adj[j].push([i,-w]);}
 const h=Array(n).fill(null),c=Array(n).fill(-1);let count=0,g=0;
 for(let i=0;i<n;i++)if(h[i]===null){h[i]=0;c[i]=count++;let q=[i];for(let k=0;k<q.length;k++){let v=q[k];for(const [u,w] of adj[v]){if(h[u]===null){h[u]=h[v]+w;c[u]=c[v];q.push(u);}else g=gcd(g,h[v]+w-h[u]);}}}
 return {count,g,h,c};
}
const pc=m=>m.toString(2).replace(/0/g,"").length;
const out={families:[],maximalMinorEvaluations:0,connectedFullRank:0,targetChecks:0,coprimeLengthChecks:0,unitErrorChecks:0};
function rank(A,n){let B=A.map(r=>r.map(BigInt)),r=0;for(let j=0;j<n&&r<B.length;j++){let k=r;while(k<B.length&&B[k][j]===0n)k++;if(k===B.length)continue;[B[r],B[k]]=[B[k],B[r]];for(let i=r+1;i<B.length;i++){let v=B[i][j];if(v)for(let l=j;l<n;l++)B[i][l]=B[r][j]*B[i][l]-v*B[r][l];}r++;}return r;}
for(let n=2;n<=4;n++){
 const E=all(n),rows=E.map(e=>row(n,e)),N=2**E.length,mins=[];
 for(let m=0;m<N;m++)if(pc(m)===n){mins.push([m,Math.abs(det(rows.filter((_,i)=>m&(1<<i))))]);out.maximalMinorEvaluations++;}
 const ranks=Array.from({length:N},(_,m)=>rank(rows.filter((_,i)=>m&(1<<i)),n));const hist={};
 for(let m=0;m<N;m++){
  const F=E.filter((_,i)=>m&(1<<i)),a=gain(n,F),r=ranks[m];
  if(a.count===1&&a.g){let d=0;for(const [s,v] of mins)if((s&m)===s)d=gcd(d,v);assert(d===a.g,"minor gcd");hist[d]=(hist[d]||0)+1;out.connectedFullRank++;}
  for(let k=0;k<E.length;k++){const [i,l]=E[k],j=(i+l)%n,w=Number(i+l>=n);const known=a.c[i]===a.c[j]&&(a.g!==0||a.h[j]-a.h[i]===w);assert((ranks[m|(1<<k)]===r)===known,"target");out.targetChecks++;}
 }
 out.families.push({n,subsets:N,smithIndexHistogram:hist});
}
for(let n=2;n<=15;n++)for(let l=1;l<n;l++)if(gcd(n,l)===1){
 const E=Array.from({length:n},(_,i)=>[i,l]),A=E.map(e=>row(n,e));
 assert(Math.abs(det(A))===l&&gain(n,E).g===l,"coprime determinant");
 out.coprimeLengthChecks++;
 const x=Array.from({length:n},(_,i)=>i+2),y=A.map(r=>r.reduce((a,b,i)=>a+b*x[i],0)),sum=y.reduce((a,b)=>a+b,0);
 assert(sum%l===0,"integer total");
 for(let j=0;j<n;j++)for(const d of [-1,1]){const z=y.map((v,i)=>v+(i===j?d:0));assert((z.reduce((a,b)=>a+b,0)%l===0)===(l===1),"unit error");out.unitErrorChecks++;}
}
return out;
}
if (typeof module !== "undefined") module.exports={arithmetic};
if (typeof require !== "undefined" && require.main===module) console.log(JSON.stringify(arithmetic(),null,2));
