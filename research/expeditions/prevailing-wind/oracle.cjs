// MHAC #406: synthetic directed cost field; no human effort measurements.
function laboratory(){
  let cases=0,conservative=0,circulating=0,assertions=0;
  const hist={};
  function check(ok,msg){assertions++;if(!ok)throw Error(msg)}
  const sum=a=>a.reduce((s,x)=>s+x,0);
  // Independently enumerate all admissible integer vertex potentials (U0=0).
  const gradients=new Set();
  for(let u1=-4;u1<=4;u1++)for(let u2=u1-4;u2<=u1+4;u2++)for(let u3=-4;u3<=4;u3++){
    if(Math.abs(u3-u2)>4)continue;
    const u=[0,u1,u2,u3];
    gradients.add(u.map((v,i)=>4+u[(i+1)%4]-v).join(","));
  }
  for(let a=0;a<=8;a++)for(let b=0;b<=8;b++)for(let c=0;c<=8;c++)for(let d=0;d<=8;d++){
    const w=[a,b,c,d], rev=w.map(x=>8-x), cw=sum(w),ccw=sum(rev),circ=cw-16;
    cases++;hist[circ]=(hist[circ]||0)+1;
    check(cw+ccw===32,"paired budget");
    check(cw-ccw===2*circ,"circulation");
    const fits=gradients.has(w.join(","));
    check(fits===(circ===0),"potential census");
    if(fits)conservative++;else circulating++;
    // All pairs of vertices: compare clockwise and counterclockwise simple routes.
    // Remove 4 per step from costs: directional residual is the object tested.
    for(let s=0;s<4;s++)for(let t=0;t<4;t++){
      if(s===t)continue;
      let i=s,p=0,q=0;
      while(i!==t){p+=w[i]-4;i=(i+1)%4}
      i=s;while(i!==t){i=(i+3)%4;q+=4-w[i]}
      check(p-q===circ,"route residual difference");
      check((p===q)===fits,"path independence");
    }
  }
  check(conservative===gradients.size,"gradient count");
  const examples=[[4,4,4,4],[5,5,5,1],[1,1,1,1]].map(w=>({cw:w,ccw:w.map(x=>8-x),cwTotal:sum(w),ccwTotal:32-sum(w),circulation:sum(w)-16}));
  return {cases,conservative,circulating,assertions,hist,examples};
}
console.log(JSON.stringify(laboratory(),null,2));
