'use strict';
function laboratory() {
  let checks=0, examined=0, validExamined=0;
  function check(x,msg){if(!x)throw Error(msg);checks++}
  const count=(n,prev)=>{let a=1,b=1;for(let i=0;i<n;i++){[a,b]=[b,a+b]}return prev==="A"?a:b};
  function unrank(n,k){let s="",prev="B";if(!Number.isInteger(k)||k<0||k>=count(n,prev))throw Error("rank");
    while(n){let a=prev==="A"?0:count(n-1,"A");if(k<a){s+="A";prev="A"}else{k-=a;s+="B";prev="B"}n--}return s}
  const rows=[];
  for(let n=1;n<=16;n++){
    let valid=[], mass=0, diff=0, nA=0, localA=0, globalA=0;
    for(let i=0;i<2**n;i++){let s=i.toString(2).padStart(n,"0").replace(/0/g,"A").replace(/1/g,"B");examined++;
      if(s.includes("AA"))continue;
      let forced=0;for(let j=1;j<n;j++)if(s[j-1]==="A")forced++;
      let weight=2**forced;valid.push(s);mass+=weight;validExamined++;
      if(s[0]==="A"){nA++;localA+=weight}globalA+=s.split("A").length-1;
    }
    const N=count(n,"B"),D=2**n;
    check(valid.length===N,"count");check(mass===D,"normalization");
    check(nA===count(n-1,"A"),"prefix count");check(localA*2===D,"local first");
    for(let j=0;j<N;j++){check(unrank(n,j)===valid[j],"rank bijection");let f=valid[j].slice(0,-1).split("A").length-1;diff+=Math.abs(2**f*N-D)}
    rows.push({n,valid:N,localFirstA:localA/D,globalFirstA:nA/N,totalVariation:diff/(2*D*N),allBLocal:1/D,allBGlobal:1/N,globalMeanA:globalA/N});
  }
  for(const k of [-1,count(4,"B"),.5]){let rejected=false;try{unrank(4,k)}catch{rejected=true}check(rejected,"invalid rank")}
  check(count(0,"A")===1&&count(0,"B")===1,"empty completion");
  check(unrank(0,0)==="","empty word");
  return {examined,validExamined,checks,rows};
}
console.log(JSON.stringify(laboratory(), null, 2));
