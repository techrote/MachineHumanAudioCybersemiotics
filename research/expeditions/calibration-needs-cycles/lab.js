'use strict';
// Standalone exact integer oracle; no dependencies. Run node lab.js.
const assert=(ok,msg)=>{if(!ok)throw Error(msg);};
const edges=Array.from({length:9},(_,i)=>[Math.floor(i/3),3+i%3]);
const pop=n=>{let k=0;while(n){n&=n-1;k++;}return k;};
const ids=m=>edges.map((_,i)=>i).filter(i=>m>>i&1);
const cost=i=>1+(i*7)%11;
const sumCost=m=>ids(m).reduce((a,i)=>a+cost(i),0);
const weights=[edges.map(([u,v])=>(u===0?1:-1)*(v===3?1:-1)),edges.map(([u,v])=>u+2*v)];
let counts={graphs:0,integerFlows:0,conservedFlows:0,probeSets:0,weightedMinima:0,targetChecks:0,channelCells:0};
function forest(m){
 const p=[0,1,2,3,4,5];const root=x=>p[x]===x?x:root(p[x]);
 let t=0;
 for(const i of ids(m).sort((a,b)=>cost(b)-cost(a))){
  const [u,v]=edges[i],a=root(u),b=root(v);
  if(a!==b){p[a]=b;t|=1<<i;}
 }
 return t;
}
// Potential existence independently tested by propagation.
function gradient(m,w){
 const z=Array(6).fill(null);
 for(let s=0;s<6;s++)if(z[s]===null){
  z[s]=0;let todo=[s];
  while(todo.length){const u=todo.pop();
   for(const i of ids(m)){const [a,b]=edges[i];if(a!==u&&b!==u)continue;
    const v=a===u?b:a,d=a===u?w[i]:-w[i],next=z[u]+d;
    if(z[v]===null){z[v]=next;todo.push(v);}
    else if(z[v]!==next)return false;
   }
  }
 }
 return true;
}
// Independent exhaustive ternary-flow oracle. A simple signed cycle is always ternary.
const truth=[];
for(let m=0;m<512;m++){
 const e=ids(m),bal=Array(6).fill(0),bad=[false,false];let nonzero=false;
 function visit(j,used,values){
  if(j===e.length){counts.integerFlows++;
   if(bal.some(Boolean))return;
   counts.conservedFlows++;if(used)nonzero=true;
   for(let t=0;t<2;t++)if(values[t])bad[t]=true;
   return;
  }
  const i=e[j],[u,v]=edges[i];
  for(let a=-1;a<=1;a++){
   bal[u]+=a;bal[v]-=a;
   visit(j+1,used||a!==0,values.map((x,t)=>x+a*weights[t][i]));
   bal[u]-=a;bal[v]+=a;
  }
 }
 visit(0,false,[0,0]);truth[m]={nonzero,bad};
 assert(nonzero===(forest(m)!==m),'forest iff zero flow');
 weights.forEach((w,t)=>{assert(gradient(m,w)===!bad[t],'target potential');counts.targetChecks++;});
 counts.graphs++;
}
for(let m=0;m<512;m++){
 let best=Infinity,cheapest=Infinity;
 for(let s=m;;s=(s-1)&m){
  counts.probeSets++;
  if(!truth[m^s].nonzero){best=Math.min(best,pop(s));cheapest=Math.min(cheapest,sumCost(s));}
  if(!s)break;
 }
 const t=forest(m);
 assert(best===pop(m^t),'minimum probe count');
 assert(cheapest===sumCost(m^t),'minimum probe cost');
 counts.weightedMinima++;
}
// K2,4: two contexts, four uniformly selected words, two parity classes.
const h=[1,-1],chi=[1,-1,-1,1],center=[10,2,2,2];
const p=(x,w,e,variant)=>center[e]+(variant?2*h[x]*chi[w]*chi[e]:0);
const row=(x,variant)=>Array.from({length:4},(_,y)=>[0,1,2,3].reduce((s,w)=>s+p(x,w,y^w,variant),0));
for(let x=0;x<2;x++)for(let w=0;w<4;w++){
 const a=[0,1,2,3].map(e=>p(x,w,e,true));
 assert(a.every(v=>v>=0)&&a.reduce((s,v)=>s+v,0)===16,'probability');
 for(const bit of [1,2])assert(a.reduce((s,v,e)=>s+((e&bit)?v:0),0)===4,'proper marginal');
 for(let e=0;e<4;e++){
  assert([0,1,2,3].reduce((s,j)=>s+p(x,j,e,true),0)===4*center[e],'source margin');
  assert(p(0,w,e,true)+p(1,w,e,true)===2*center[e],'word margin');
  counts.channelCells++;
 }
}
assert(JSON.stringify(row(0,false))==='[16,16,16,16]','uniform reference');
assert(JSON.stringify(row(0,true))==='[24,8,8,24]','positive context');
assert(JSON.stringify(row(1,true))==='[8,24,24,8]','negative context');
assert(row(0,true).reduce((s,v,i)=>s+Math.max(v,row(1,true)[i]),0)===96,'Bayes 96/128');
let minFull=8,minTarget=8;
for(let p=0;p<256;p++){
 const full=[0,1,2,3].filter(w=>!(p>>w&1)&&!(p>>(4+w)&1));
 if(full.length<=1)minFull=Math.min(minFull,pop(p));
 if(!full.some(w=>chi[w]===1)||!full.some(w=>chi[w]===-1))minTarget=Math.min(minTarget,pop(p));
}
assert(minFull===3&&minTarget===2,'selective audit savings');
console.log(JSON.stringify({counts,K24:{minFull,minTarget,baselineGuess:0.5,hiddenGuess:0.75}},null,2));
