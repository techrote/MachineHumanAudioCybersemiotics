// Standalone exact integer witness. Run: node laboratory.cjs
"use strict";
function run(){
 const assert=(v,m)=>{if(!v)throw Error(m)};
 const sum=x=>x.reduce((a,b)=>a+b,0);
 const pairs=[[0,1],[0,2],[1,2]];
 function trimmed(ds,r){return sum(ds.slice().sort((a,b)=>a-b).slice(0,Math.max(0,ds.length-r)))}
 function profile(s,N){return Array.from({length:N+1},(_,r)=>Math.min(...pairs.map(([i,j])=>trimmed(Array.from({length:N},(_,t)=>(s[t+i]-s[t+j])**2),r))))}
 let triples=0,attainments=0,period3=0;
 for(let A=1;A<=12;A++)for(let g=0;g<=A;g++){
   let best=-1;
   for(let x=-A;x<=A;x++)for(let y=x+g;y<=A;y++)for(let z=y+g;z<=A;z++){
     let q=(x-y)**2+(y-z)**2+(z-x)**2;assert(q<=8*A*A-4*A*g+2*g*g,"triple upper");best=Math.max(best,q);triples++;
   }
   assert(best===8*A*A-4*A*g+2*g*g,"triple attainment");attainments++;
 }
 for(let A=1;A<=8;A++)for(let k=1;k<=6;k++){
   let N=3*k, best=Array(N+1).fill(-1);
   for(let g=0;g<=A;g++){
     let s=Array.from({length:N+2},(_,t)=>[-A,-A+g,A][t%3]), p=profile(s,N);
     for(let r=0;r<=N;r++){
       let formula=r<=k?k*g*g+k*(2*A-g)**2+(k-r)*4*A*A:r<=2*k?k*g*g+(2*k-r)*(2*A-g)**2:(N-r)*g*g;
       assert(p[r]===formula,"trim formula");best[r]=Math.max(best[r],p[r]);period3++;
     }
   }
   for(let r=0;r<=N;r++){
     let binary=4*A*A*Math.max(0,2*k-r),ternary=A*A*(r<=k?6*k-4*r:N-r);
     assert(best[r]===Math.max(binary,ternary),"endpoint optimal");
   }
 }
 let finite=[];
 for(let N of [3,6,9]){
   let best=Array(N+1).fill(-1),count=3**(N+2);
   for(let i=0;i<count;i++){
     let z=i,s=[];for(let j=0;j<N+2;j++){s.push(z%3-1);z=Math.floor(z/3)}
     let p=profile(s,N);for(let r=0;r<=N;r++)best[r]=Math.max(best[r],p[r]);
   }
   let k=N/3;
   assert(best.every((v,r)=>v===Math.max(4*Math.max(0,2*k-r),r<=k?6*k-4*r:N-r)),"finite ternary grid");
   finite.push({N,count,best});
 }
 // K-dimensional integer embedding of a regular (K-1)-simplex.
 const vec=(K,t)=>Array.from({length:K},(_,i)=>i===((t%K)+K)%K?K-1:-1);
 const dist=(a,b)=>sum(a.map((v,i)=>(v-b[i])**2));
 const half=(a,b)=>a.map((v,i)=>(v+b[i])/2);
 const candidates=(received,K,e,budget)=>Array.from({length:K},(_,s)=>s).filter(s=>trimmed(received.flatMap((x,t)=>x===null?[]:[dist(x,vec(K,t+s))]),e)<=budget);
 let simplexChecks=0,strictTrials=0,midpointTrials=0,historyChecks=0;
 for(let K=2;K<=8;K++){
   let R2=K*(K-1),c=2*K*K;
   for(let i=0;i<K;i++){assert(dist(vec(K,i),Array(K).fill(0))===R2,"radius");for(let j=i+1;j<K;j++){assert(dist(vec(K,i),vec(K,j))===c,"simplex");simplexChecks++}}
   for(let N=1;N<=12;N++)for(let e=0;2*e<N;e++)for(let f=0;2*e+f<N;f++){
     let r=2*e+f, threshold=(N-r)*c/4;
     for(let a=0;a<K;a++)for(let b=a+1;b<K;b++){
       // Erase f, allocate e arbitrary substitutions to each hypothesis, midpoint the rest.
       let z=Array.from({length:N},(_,t)=>t<f?null:t<f+e?vec(K,t+b):t<f+2*e?vec(K,t+a):half(vec(K,t+a),vec(K,t+b)));
       let got=candidates(z,K,e,threshold);
       assert(got.includes(a)&&got.includes(b),"sharp midpoint");midpointTrials++;
       // Strictly nearer to a on common coordinates; same gross fault pattern.
       z=z.map((x,t)=>x===null?null:t<f+2*e?x:vec(K,t+a).map((v,i)=>(3*v+vec(K,t+b)[i])/4));
       got=candidates(z,K,e,threshold/4);
       assert(got.length===1&&got[0]===a,"strict decoder");strictTrials++;
     }
   }
   for(let N=1;N<=15;N++)for(let i=0;i<=N;i++)for(let j=i;j<=N;j++){
     let ds=Array.from({length:N},(_,t)=>dist(vec(K,t+(t>=i?1:0)),vec(K,t+(t>=j?1:0))));
     for(let r=0;r<=N;r++){assert(trimmed(ds,r)===c*Math.max(0,j-i-r),"history metric");historyChecks++}
   }
   assert(dist(vec(K,0),vec(K,K))===0,"modulo alias");
 }
 // Arbitrary unobserved payload can cancel any scalar pilot. Period-3 payload can do so inside same periodic space.
 let pilot=[-1,0,1];assert(pilot.every((x,i)=>x+(-pilot[i])===0),"payload cancellation");
 return {scalar_triples:triples,scalar_bound_attainments:attainments,period3_trim_checks:period3,finite_grid:finite,simplex_pairs:simplexChecks,strict_decoder_trials:strictTrials,midpoint_ambiguities:midpointTrials,history_trim_checks:historyChecks,negative_controls:["modulo alias","unknown additive payload cancellation"]};
}
if(typeof module!=="undefined"&&require.main===module)console.log(JSON.stringify(run(),null,2));
