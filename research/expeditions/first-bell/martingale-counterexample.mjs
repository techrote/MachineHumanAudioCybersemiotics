// MHAC #284: exhaustive finite martingale/terminal-outcome counterexample.
function martingaleCounterexample(){
 const C=[[0,4,8,4],[4,8,4,0]], q1=[2,1], q2=[0,1,2,3], sum=a=>a.reduce((x,y)=>x+y,0);
 const assert=(x,m)=>{if(!x)throw Error(m)};
 for(let i=0;i<2;i++)assert(sum(C[i].map((c,j)=>c*q2[j]))===q1[i]*sum(C[i]),"forecast martingale");
 const ideal=[[0,1,4,3],[0,2,2,0]], results=[];
 // Enumerate every possible label count in each occupied trace cell.
 for(let a=0;a<=4;a++)for(let b=0;b<=8;b++)for(let c=0;c<=4;c++)for(let d=0;d<=4;d++)for(let e=0;e<=8;e++)for(let f=0;f<=4;f++){
  const z=[[0,a,b,c],[d,e,f,0]];
  if(z.some((row,i)=>4*sum(row)!==q1[i]*sum(C[i])))continue;
  if(q2.some((q,j)=>4*(z[0][j]+z[1][j])!==q*(C[0][j]+C[1][j])))continue;
  const count=sum(C[0])+C[1][2], positives=sum(z[0])+z[1][2];
  const history=z.every((row,i)=>row.every((v,j)=>4*v===q2[j]*C[i][j]));
  const delta=a-1;
  assert(JSON.stringify(z)===JSON.stringify([[0,1+delta,4-delta,3],[0,2-delta,2+delta,0]]),"exhaustive family");
  assert(history===(delta===0),"history condition");
  results.push({delta,positives,count,history,z});
 }
 assert(results.length===4&&results[0].positives===9&&results[3].positives===12,"exact range");
 return {forecastScale:4,first:q1,second:q2,counts:C,ideal,results};
}
console.log(JSON.stringify(martingaleCounterexample(),null,2));
