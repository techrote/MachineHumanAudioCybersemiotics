"use strict";
function laboratory(){
 const assert=(x,msg)=>{if(!x)throw Error(msg)};
 const pop=x=>{let n=0;while(x){n+=x&1;x>>=1;}return n};
 const masks=n=>Array.from({length:(1<<n)-1},(_,i)=>i+1);
 const sum=x=>x.reduce((a,b)=>a+b,0);
 const choose=(n,k)=>{if(k<0||k>n)return 0;let v=1;for(let i=1;i<=k;i++)v=v*(n-i+1)/i;return Math.round(v)};
 const counts={channels:0,loss_matrices:0,positive_baseline_cases:0,lower_witnesses:0,upper_witnesses:0,repeat_profiles:0,repeat_coverage_checks:0,fixed_size_profiles:0};
 const coverage=(w,T)=>sum(w.map((a,S)=>(S&T)===T?a:0));
 const rowDen=(n,w)=>{let D=coverage(w,1);assert(D>0&&masks(n).filter(x=>pop(x)===1).every(x=>coverage(w,x)===D),"row sums");return D};
 const risk=(n,w,loss)=>sum(masks(n).map(S=>w[S]*Math.min(...loss.map(col=>sum(col.filter((_,i)=>S&(1<<i)))))));
 const baseline=loss=>Math.min(...loss.map(sum));
 const low=(n,w,m)=>Math.min(...masks(n).filter(T=>pop(T)===Math.min(m,n)).map(T=>coverage(w,T)));
 const high=(n,w,D)=>D-Math.min(...Array.from({length:n},(_,i)=>w[1<<i]));
 const fixed=(n,s)=>Array.from({length:1<<n},(_,i)=>Number(pop(i)===s));
 const combine=(w,z)=>{const out=Array(w.length).fill(0);for(let a=1;a<w.length;a++)for(let b=1;b<z.length;b++)out[a&b]+=w[a]*z[b];out[0]=0;return out};
 let seed=0x638;const rnd=n=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed%n};
 const randomPartition=n=>{let b=Array(n).fill(0);for(let i=0;i<n;i++)b[rnd(n)]|=1<<i;return b.filter(Boolean)};
 function check(n,w,exhaust){
   const D=rowDen(n,w);counts.channels++;
   for(let m=2;m<=n+1;m++){
     const l=low(n,w,m), h=high(n,w,D);
     const T=masks(n).find(T=>pop(T)===Math.min(m,n)&&coverage(w,T)===l);
     const ids=Array.from({length:n},(_,i)=>i).filter(i=>T&(1<<i));
     const witness=ids.map(i=>Array.from({length:n},(_,j)=>Number(i===j)));
     while(witness.length<m)witness.push(witness[0].slice());
     assert(baseline(witness)===1&&risk(n,w,witness)===l,"lower witness");counts.lower_witnesses++;
     const i=Array.from({length:n},(_,j)=>j).find(j=>w[1<<j]===D-h);
     const A=Array.from({length:n},(_,j)=>Number(i===j)), B=A.map(x=>1-x);
     const up=[A,B];while(up.length<m)up.push(A.slice());
     assert(baseline(up)===1&&risk(n,w,up)===h,"upper witness");counts.upper_witnesses++;
     const verify=loss=>{let L=baseline(loss),R=risk(n,w,loss);counts.loss_matrices++;if(L>0)counts.positive_baseline_cases++;assert(l*L<=R&&R<=h*L,"risk bounds")};
     if(exhaust&&m<=3){
       const rows=masks(m).filter(x=>x!==(1<<m)-1).concat(0);
       for(let v=0;v<rows.length**n;v++){
         let x=v, loss=Array.from({length:m},()=>[]);
         for(let j=0;j<n;j++){let z=rows[x%rows.length];x=Math.floor(x/rows.length);for(let a=0;a<m;a++)loss[a].push((z>>a)&1)}
         verify(loss);
       }
     }
     for(let trial=0;trial<64;trial++){
       let loss=Array.from({length:m},()=>Array(n).fill(0));
       for(let j=0;j<n;j++){let row=Array.from({length:m},()=>rnd(17)),min=Math.min(...row);for(let a=0;a<m;a++)loss[a][j]=row[a]-min}
       verify(loss);
     }
   }
   if(n<=5){
      let z=w.slice();
      for(let d=2;d<=3;d++){z=combine(z,w);assert(rowDen(n,z)===D**d,"repeat denom");counts.repeat_profiles++;
        for(let T of masks(n)){assert(coverage(z,T)===coverage(w,T)**d,"repeat coverage");counts.repeat_coverage_checks++}
      }
   }
 }
 for(let n=2;n<=7;n++)for(let s=1;s<=n;s++){
   let w=fixed(n,s), D=rowDen(n,w);
   for(let m=2;m<=n;m++){assert(low(n,w,m)===choose(n-m,s-m),"fixed-size closed form");counts.fixed_size_profiles++}
   check(n,w,n<=4);
 }
 for(let n=3;n<=5;n++)for(let j=0;j<32;j++){
   let w=Array(1<<n).fill(0);
   for(let q=0;q<4;q++)for(let S of randomPartition(n))w[S]++;
   check(n,w,j<3&&n<=4);
 }
 // Non-constant-on-subset channel: singleton-free but still informative through biased weights.
 // Two states, three labels (AB duplicated with distinct tags). Both labels name AB.
 // P(tag0|A)=1, P(tag1|B)=1; observed tag gives perfect identification.
 // This is outside the model, and treating tags as interchangeable sets loses information.
 const counter={tag_channel:[[1,0],[0,1]],merged_channel:[[1],[1]],tag_risk:0,merged_risk:0.5};
 // Explicit n=5, r=3 thresholds and exact normalized witnesses for m=2,3.
 const example={n:5,s:3,denominator:6,cover2:3,cover3:1,cover4:0,reveal_p:"1/2",two_action_risks:["1/10","1/10"],three_action_risks:["1/10","1/30"]};
 return {schema:"mhac-638-laboratory-v1",counts,example,counter,assertion_failures:0};
}
if (require.main === module) console.log(JSON.stringify(laboratory(), null, 2));
module.exports = laboratory;
