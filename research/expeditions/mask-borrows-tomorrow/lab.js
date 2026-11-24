// Synthetic exact-arithmetic laboratory; no empirical claims.
function lab(){
"use strict";
const W=[0,3,5,6], bit=(w,g)=>(w>>g)&1, idx=w=>W.indexOf(w);
const check=(x,msg)=>{if(!x)throw Error(msg)};
const D=48, sum=a=>a.reduce((x,y)=>x+y,0);
const swap=(w,a,b)=>bit(w,a)===bit(w,b)?w:w^(1<<a)^(1<<b);
const relabel=(P,a,b)=>W.flatMap(w=>W.map(v=>P[4*idx(swap(w,a,b))+idx(swap(v,a,b))]));
const tv2=(p,q)=>sum(p.map((v,i)=>Math.abs(v-q[i])));
function marg(P,g){
  const m=[0,0,0,0];
  W.forEach((w,i)=>W.forEach((v,j)=>m[2*bit(w,g)+bit(v,g)]+=P[4*i+j]));
  return m;
}
function validateCausal(P,g,m){
  check(sum(P)===D,"normalization");
  check(marg(P,g).join() === [24-4*m,4*m,12,12].join(),"source path law");
  W.forEach((w,i)=>{
    const row=P.slice(4*i,4*i+4), ones=sum(row.filter((_,j)=>bit(W[j],g)));
    check(6*ones===(bit(w,g)?3:m)*sum(row),"causal conditional law");
  });
}
function rowSym(mass,m){
  const ones=mass*m/6;
  if(!Number.isInteger(ones)||ones%2)return [];
  return Array.from({length:mass-ones+1},(_,y)=>[mass-ones-y,ones/2,ones/2,y]);
}
function rowFree(mass){
  const out=[];
  for(let a=0;a<=mass/2;a++)for(let b=0;b<=mass/2;b++)
    out.push([a,b,mass/2-b,mass/2-a]);
  return out;
}
let policies=0, causalChecks=0, opt=[];
for(let m=0;m<=6;m++){
  let best=Infinity;
  for(let t=0;t<=24;t++){
    for(const row0 of rowSym(t,m))for(const row6 of rowSym(24-t,m))for(const row3 of rowFree(12)){
      const row5=W.map(w=>row3[idx(swap(w,1,2))]);
      const P=[...row0,...row3,...row5,...row6];
      const Q=[P,relabel(P,0,1),relabel(P,0,2)];
      Q.forEach((q,g)=>{validateCausal(q,g,m);causalChecks++;});
      const loss=Math.max(tv2(Q[0],Q[1]),tv2(Q[0],Q[2]),tv2(Q[1],Q[2]));
      check(loss>=6*Math.max(0,m-4),"sharp lower bound");
      best=Math.min(best,loss);policies++;
    }
  }
  check(best===6*Math.max(0,m-4),"attaining policy on grid");
  opt.push({aNumerator:m,aDenominator:6,tvNumerator:best,tvDenominator:2*D});
}
const low=[],high=[];
for(const w of W)for(const v of W){
  low.push(w===0?(v===0?6:0):(v===0||v===w?3:0));
  high.push(w===0?(v===0?0:2):(v!==0&&v!==w?3:0));
}
let offline=0;
for(let m=0;m<=10;m++){
  const P=low.map((x,i)=>(10-m)*x+m*high[i]);
  check(sum(P)===240,"offline normalized");
  for(let g=0;g<3;g++){
    check(marg(P,g).join()===[120-10*m,10*m,60,60].join(),"offline marginal");offline++;
    check(relabel(P,0,g).join()===P.join(),"offline permutation symmetry");
  }
}
check(high[0]===0&&high.slice(0,4).reduce((a,b)=>a+b,0)===6,"high first row");
check(marg(high,0).join()===[2,10,6,6].join(),"high witness");
check(sum(high.slice(0,4).filter((_,j)=>bit(W[j],0)))===4,"preview witness numerator");
let localOracle=new Map(), laws=0;
for(let a=0;a<=24;a++)for(let b=0;b<=24-a;b++)for(let c=0;c<=24-a-b;c++){
 const d=24-a-b-c, q=[b+c,b+d,c+d];
 const k=q.join();
 check(!localOracle.has(k),"tetrahedron uniqueness");
 localOracle.set(k,[a,b,c,d]);laws++;
}
function local(q){
 const [x,y,z]=q;
 const s=[24-(x+y+z)/2,(x+y-z)/2,(x+z-y)/2,(y+z-x)/2];
 return s.every(v=>v>=0)?s:null;
}
let localChecks=0,twoTick=0;
for(let x=0;x<=24;x+=2)for(let y=0;y<=24;y+=2)for(let z=0;z<=24;z+=2){
 const q=[x,y,z], a=local(q),b=localOracle.get(q.join())||null;
 check(JSON.stringify(a)===JSON.stringify(b),"local law");localChecks++;
}
for(let a=0;a<=24;a+=2)for(let b=0;b<=24;b+=2){
 const can=W.every(w=>!!localOracle.get([0,1,2].map(g=>bit(w,g)?b:a).join()));
 check(can===(a<=16&&a<=2*b&&a+2*b<=48),"two-tick criterion");twoTick++;
}
function feasible(tree,depth,useOracle){
 function visit(prefix,t){
   if(t===depth)return true;
   const q=prefix.map(p=>tree[p.length? p:"-"]);
   const law=useOracle?localOracle.get(q.join()):local(q);
   if(!law)return false;
   return W.every((w,i)=>!law[i]||visit(prefix.map((p,g)=>p+bit(w,g)),t+1));
 }
 return visit(["","",""],0);
}
let trees=0, feasibleTrees=0;
for(let i=0;i<729;i++){
 let n=i,tree={"-":12};
 for(const p of ["0","1","00","01","10","11"]){tree[p]=[0,12,24][n%3];n=Math.floor(n/3)}
 const a=feasible(tree,3,false),b=feasible(tree,3,true);
 check(a===b,"three-tick viability");trees++;feasibleTrees+=Number(a);
}
check(feasible({"-":12,"0":20,"1":12},2,false)===false,"strict separation");
check(feasible({"-":12,"0":16,"1":12},2,false)===true,"boundary");
check(feasible({"-":12,"0":12,"1":12},2,false)===true,"iid control");
return {policies,causalChecks,opt,offline,laws,localChecks,twoTick,trees,feasibleTrees,negativeControls:3};
}
console.log(JSON.stringify(lab(), null, 2));
