"use strict";
function generalLaboratory(){
 const assert=(x,msg)=>{if(!x)throw Error(msg)}, sum=a=>a.reduce((x,y)=>x+y,0);
 const pop=x=>{let c=0;while(x){c+=x&1;x>>=1}return c};
 const comb=(n,k)=>Array.from({length:1<<n},(_,i)=>i).filter(x=>pop(x)===k).map(T=>Array.from({length:n},(_,i)=>i).filter(i=>T&(1<<i)));
 const risk=(K,A)=>sum(K[0].map((_,y)=>Math.min(...A.map(a=>sum(a.map((v,i)=>v*K[i][y]))))));
 const overlap=(K,T)=>sum(K[0].map((_,y)=>Math.min(...T.map(i=>K[i][y]))));
 const exclusive=(K,i)=>sum(K[i].filter((_,y)=>K.every((row,j)=>j===i||row[y]===0)));
 const counts={channels:0,lower_witnesses:0,upper_witnesses:0,loss_matrices:0,positive_baseline:0,repetition_checks:0};
 let seed=638;const rnd=n=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return (seed>>>8)%n};
 const rows=(D,q)=>q===1?[[D]]:Array.from({length:D+1},(_,i)=>rows(D-i,q-1).map(a=>[i,...a])).flat();
 function check(K,D,exhaust){
  const n=K.length,q=K[0].length;counts.channels++;
  assert(K.every(a=>sum(a)===D&&a.length===q),"normalized");
  for(let m=2;m<=n;m++){
    let T=comb(n,m).reduce((a,b)=>overlap(K,a)<=overlap(K,b)?a:b);
    let lo=overlap(K,T);
    let i=Array.from({length:n},(_,i)=>i).reduce((a,b)=>exclusive(K,a)<=exclusive(K,b)?a:b);
    let hi=D-exclusive(K,i);
    let A=T.map(i=>Array.from({length:n},(_,j)=>Number(i===j)));
    assert(risk(K,A)===lo,"lower endpoint");counts.lower_witnesses++;
    let a=Array.from({length:n},(_,j)=>Number(i===j)),b=a.map(v=>(1-v)*D);
    A=[a,b];while(A.length<m)A.push(a);
    assert(risk(K,A)===hi,"upper endpoint");counts.upper_witnesses++;
    const verify=A=>{let L=Math.min(...A.map(sum)),R=risk(K,A);assert(lo*L<=R&&R<=hi*L,"risk envelope");counts.loss_matrices++;if(L>0)counts.positive_baseline++};
    if(exhaust){
      let rs=Array.from({length:(1<<m)-1},(_,i)=>i);
      for(let v=0;v<rs.length**n;v++){
        let x=v,A=Array.from({length:m},()=>[]);
        for(let i=0;i<n;i++){let t=rs[x%rs.length];x=Math.floor(x/rs.length);for(let j=0;j<m;j++)A[j].push((t>>j)&1)}
        verify(A)
      }
    }else for(let j=0;j<40;j++){
      A=Array.from({length:m},()=>[]);
      for(let i=0;i<n;i++){let row=Array.from({length:m},()=>rnd(21)),mi=Math.min(...row);for(let a=0;a<m;a++)A[a].push(row[a]-mi)}
      verify(A)
    }
  }
 }
 for(let n=2;n<=3;n++)for(let q=2;q<=3;q++){
  let rr=rows(2,q);
  for(let v=0;v<rr.length**n;v++){let x=v,K=[];for(let i=0;i<n;i++){K.push(rr[x%rr.length]);x=Math.floor(x/rr.length)}check(K,2,true)}
 }
 for(let n=3;n<=7;n++)for(let trial=0;trial<30;trial++){
  let q=2+rnd(5),D=9;
  let K=Array.from({length:n},()=>{let row=Array(q).fill(0);for(let j=0;j<D;j++)row[rnd(q)]++;return row});
  check(K,D,false)
 }
 const repeat=(K,d)=>K.map(row=>{let z=[1];for(let i=0;i<d;i++)z=z.flatMap(a=>row.map(b=>a*b));return z});
 const example=[];const K=[[3,1],[1,3]];
 for(let d=1;d<=10;d++){
   let kd=repeat(K,d), tau=overlap(kd,[0,1]), den=4**d;
   assert(tau>=2**d,"repeat overlap lower");counts.repetition_checks++;
   example.push({d,overlapNumerator:tau,overlapDenominator:den,erasureDominates:(3**d)*den<=tau*5**d});
 }
 assert(!example[0].erasureDominates&&example[1].erasureDominates,"repetition flips");
 return {schema:"mhac-638-general-v1",counts,example,assertion_failures:0};
}
if(require.main===module) console.log(JSON.stringify(generalLaboratory(),null,2));
module.exports=generalLaboratory;
