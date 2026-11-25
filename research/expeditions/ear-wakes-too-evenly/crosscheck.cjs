// Standard-library Node.js; all calculations exact integer.
function run(){
 const counts={profiles:0,explicit_window_fault_checks:0,near_bound_graph_checks:0,budgets:0,balanced_failures:0,joint_optimum_failures:0};
 let byN={};
 for(let n=2;n<=10;n++){
  let z={profiles:0,balanced_failures:0};
  for(let a=1;a<=n;a++){
   const em=Math.min(2,a-1), records=[];
   for(let mask=0;mask<2**n;mask++){
    const B=Array.from({length:n},(_,i)=>(mask>>i)&1);
    let b=B.reduce((x,y)=>x+y,0), min=a, worst=Array(em+1).fill(0);
    for(let shift=0;shift<n;shift++){
     const hits=Array.from({length:n},(_,i)=>i<a?B[(i+shift)%n]:0);
     min=Math.min(min,hits.reduce((x,y)=>x+y,0));
     for(let start=0;start<n;start++){
      let c=0,e=0;
      for(let G=1;G<=n;G++){
       c+=hits[(start+G-1)%n];
       while(e<=em&&c>=e+1){worst[e]=Math.max(worst[e],G);e++}
       if(e>em)break;
      }
      while(e<=em){worst[e]=n+1;e++}
     }
    }
    for(let e=0;e<=em;e++){
     if((worst[e]===n+1)!==(min<=e))throw Error("existence");
     if(worst[e]<n-a+e+1||((worst[e]===n-a+e+1)!==(b===n)))throw Error("floor");
     counts.explicit_window_fault_checks++;
     if(e+2<=a){
      const s=e+2;let okay=true;
      for(let i=0;i<n;i++)if(!B[i])for(let d=1;d<a;d++)if((d<s||d>=a-s+1)&&!B[(i+d)%n])okay=false;
      if((worst[e]<=n-a+s)!==okay)throw Error("graph");
      counts.near_bound_graph_checks++;
     }
    }
    if(min>Math.floor(a*b/n))throw Error("count upper");
    records.push({mask,b,min,g:worst[0]});counts.profiles++;z.profiles++;
   }
   for(let b=0;b<=n;b++){
    const rs=records.filter(r=>r.b===b), mc=Math.max(...rs.map(r=>r.min)), mg=Math.min(...rs.map(r=>r.g));
    let mask=0;for(let i=0;i<n;i++)if(Math.floor((i+1)*b/n)!==Math.floor(i*b/n))mask|=1<<i;
    const bal=rs.find(r=>r.mask===mask);
    if(mc!==Math.floor(a*b/n)||bal.min!==mc)throw Error("balanced count");
    if(bal.g>mg){counts.balanced_failures++;z.balanced_failures++}
    if(!rs.some(r=>r.min===mc&&r.g===mg))counts.joint_optimum_failures++;
    counts.budgets++;
   }
  }byN[n]=z;
 }
 // Noncontiguous transmitting set: all 15 receiver pairs fail.
 const A=[0,1,3];let failures=0;
 for(let i=0;i<6;i++)for(let j=i+1;j<6;j++){
  const B=[i,j];let counts=Array.from({length:6},(_,t)=>A.filter(x=>B.includes((x+t)%6)).length);
  if(Math.min(...counts)!==0)throw Error("noninterval witness");failures++;
 }
 return {domain:"N=2..10, all interval lengths, masks and phases; literal forward window search",counts,byN,noncontiguous_pairs_failed:failures};
}
console.log(JSON.stringify(run(),null,2));
