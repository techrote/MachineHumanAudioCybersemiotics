'use strict';
// Exhaustive symbolic pitch-class tests; no acoustic or perceptual inference.
function run(){
  const mod=(a,n)=>((a%n)+n)%n;
  const gcd=(a,b)=>b?gcd(b,a%b):a;
  const set=(n,s,m,r=0)=>new Set(Array.from({length:m},(_,i)=>mod((r+i)*s,n)));
  const overlap=(a,b)=>[...a].filter(x=>b.has(x)).length;
  let cases=0, checks=0;
  const eq=(a,b)=>{checks++;if(a!==b)throw Error(`${a} != ${b}`)};
  for(let n=2;n<=32;n++)for(let s=1;s<n;s++){
    const L=n/gcd(n,s);
    for(let m=1;m<=L;m++){
      const A=set(n,s,m);
      eq(A.size,m);
      let stabilizers=0;
      for(let k=0;k<L;k++){
        const B=set(n,s,m,k);
        const o=overlap(A,B);
        eq(o,Math.max(0,m-k)+Math.max(0,m-(L-k)));
        if(o===m)stabilizers++;
        eq(m-o,[...A].filter(x=>!B.has(x)).length);
        cases++;
      }
      eq(stabilizers,m===L?L:1);
    }
  }
  const witnesses=[];
  for(const [n,g] of [[12,7],[19,11],[31,18],[24,14]]){
    const s=mod(-3*g,n),L=n/gcd(n,s),A=set(n,s,4);
    const rows=Array.from({length:4},(_,k)=>[...set(n,s,4,k)].sort((a,b)=>a-b));
    const aliases=new Set(rows.map(r=>r.join(","))).size;
    eq(aliases,L===4?1:4);
    const distances=rows.map(r=>4-overlap(A,new Set(r)));
    eq(distances.join(","),L===4?"0,0,0,0":"0,1,2,3");
    const defect=mod(4*s,n);eq(defect,n===19||n===31?1:0);
    witnesses.push({n,g,s,L,rows,aliases,distances,defect});
  }
  return {cases,checks,witnesses};
}
console.log(JSON.stringify(run(), null, 2));
