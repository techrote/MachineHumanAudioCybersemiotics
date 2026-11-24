// Synthetic finite oracle; no perceptual data.
console.log(JSON.stringify((function lab(){
 const gcd=(a,b)=>b===0?a:gcd(b,a%b);
 let checks=0,cases=0,vertices=0;
 const check=(condition,msg)=>{if(!condition)throw Error(msg);checks++};
 for(let n=2;n<=120;n++)for(let s=0;s<n;s++){
   let labels=Array(n).fill(-1),count=0;
   for(let i=0;i<n;i++)if(labels[i]<0){let queue=[i];labels[i]=count;for(let j=0;j<queue.length;j++){let x=queue[j];for(let y of [(x+s)%n,(x-s+n)%n])if(labels[y]<0){labels[y]=count;queue.push(y)}}count++}
   const g=gcd(n,s);check(count===g,"component count");for(let i=0;i<n;i++){check(labels[i]===labels[i%g],"component residue");vertices++}cases++;
 }
 const orbit=[{a:1n,b:1n}], rows=[];
 for(let k=1;k<=128;k++){let {a,b}=orbit[k-1];a*=3n;while(a>=2n*b)b*=2n;check(a>=b&&a<2n*b,"fold range");check(a===3n**BigInt(k),"numerator");check((b&(b-1n))===0n,"power of 2");for(let p of orbit)check(a*p.b!==p.a*b,"unique exact orbit");orbit.push({a,b});
 if([1,2,5,12,24,53,128].includes(k)){let cents=orbit.map(p=>1200*Math.log2(Number(p.a)/Number(p.b))).sort((a,b)=>a-b);let gaps=cents.slice(1).map((v,i)=>v-cents[i]);gaps.push(1200-cents[cents.length-1]+cents[0]);rows.push({steps:k,points:k+1,endpointCents:1200*Math.log2(Number(a)/Number(b)),maxGapCents:Math.max(...gaps)})}}
 const grids=[12,19,24,31,53,72,96,120].map(n=>{let s=Math.round(n*Math.log2(3))%n;return {n,s,classes:gcd(n,s)}});
 return {cases,vertices,checks,rows,grids};
})(),null,2));
