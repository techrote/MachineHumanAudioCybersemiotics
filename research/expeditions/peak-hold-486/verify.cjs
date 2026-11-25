'use strict';
const {compile,observe}=require('./inverse.cjs');
const check=(ok,msg)=>{if(!ok)throw Error(msg)};
function census(){
 const totals={instances:0,classes:0,extremalReplays:0,forcedChecks:0,erasureChecks:0,inconsistent:0,feasibleArbitrary:0,invalid:0,byN:[]};
 const support=x=>x.filter(Boolean).length, energy=x=>x.reduce((s,v)=>s+v*v,0), sum=x=>x.reduce((s,v)=>s+v,0);
 for(let n=2;n<=7;n++){
  const families=[];for(let a=1;a<=n;a++){families.push([a]);for(let b=a+1;b<=n;b++)families.push([a,b]);}
  let instances=0,classes=0;
  for(const widths of families){
   const groups=new Map();
   for(let k=0;k<3**n;k++){
    const x=Array.from({length:n},(_,i)=>Math.floor(k/3**i)%3);
    const rows=observe(x,widths),key=rows.map(r=>r.value).join(',');
    if(!groups.has(key))groups.set(key,{rows,inputs:[]});
    groups.get(key).inputs.push(x);instances++;
   }
   for(const [key,{rows,inputs}] of groups){
    const v=compile(n,rows);check(v.status==='feasible','feasible rejected');
    const extrema=f=>[Math.min(...inputs.map(f)),Math.max(...inputs.map(f))];
    check(support(v.sparse)===extrema(support)[0],'support');
    check(sum(v.sparse)===extrema(sum)[0]&&energy(v.sparse)===extrema(energy)[0],'minimum mass/energy');
    check(sum(v.cap)===extrema(sum)[1]&&energy(v.cap)===extrema(energy)[1],'maximum mass/energy');
    check(v.cap.every((c,i)=>c===Math.max(...inputs.map(x=>x[i]))),'component maximum');
    for(const x of [v.sparse,v.cap])check(observe(x,widths).map(r=>r.value).join(',')===key,'replay');
    const forced=Array.from({length:n},(_,i)=>i).filter(i=>v.cap[i]>0&&inputs.every(x=>x[i]===v.cap[i]));
    check(JSON.stringify(forced)===JSON.stringify(v.forced),'forced');
    // Direct deletion oracle, independent of candidate-set formula.
    let limit=null;
    if(rows.some(r=>r.value>0)){
      let first=n+1;
      for(let mask=1;mask<2**n;mask++){
        const weight=mask.toString(2).replace(/0/g,'').length;
        if(weight>=first)continue;
        const z=v.cap.map((x,i)=>mask&(1<<i)?0:x);
        if(observe(z,widths).map(r=>r.value).join(',')!==key)first=weight;
      }
      limit=first-1;
    }
    check(v.erasureLimit===limit,'erasure limit');
    classes++;totals.extremalReplays+=2;totals.forcedChecks++;totals.erasureChecks++;
   }
  }
  totals.instances+=instances;totals.classes+=classes;totals.byN.push({n,instances,classes});
 }
 // Enumerate arbitrary complete ternary meter readings, including impossible ones.
 for(let n=2;n<=5;n++)for(let w=1;w<=n;w++){
  const actual=new Set();
  for(let k=0;k<3**n;k++){const x=Array.from({length:n},(_,i)=>Math.floor(k/3**i)%3);actual.add(observe(x,[w]).map(r=>r.value).join(','));}
  for(let k=0;k<3**n;k++){
   const values=Array.from({length:n},(_,i)=>Math.floor(k/3**i)%3);
   const rows=values.map((value,start)=>({start,length:w,value}));
   const v=compile(n,rows), ok=actual.has(values.join(','));
   check((v.status==='feasible')===ok,'arbitrary feasibility');
   if(ok)totals.feasibleArbitrary++;else totals.inconsistent++;
  }
 }
 for(const args of [[0,[]],[2,[]],[2,[{start:0,length:1,value:1}]],[2,[{start:2,length:2,value:1}]],[2,[{start:0,length:2,value:-1}]]]){
  let rejected=false;try{compile(...args)}catch(e){rejected=e instanceof RangeError}check(rejected,'invalid');totals.invalid++;
 }
 const n=16,rows=observe(Array(n).fill(4),[5,8]),v=compile(n,rows);
 check(support(v.sparse)===4&&v.erasureLimit===4,'flat case');
 const contradiction=compile(3,[{start:0,length:2,value:2},{start:0,length:1,value:1},{start:1,length:1,value:1},{start:2,length:1,value:0}]);
 check(contradiction.status==='inconsistent','inconsistent row witness');
 // Circular packing lower bound need not be tight: 3 pair arcs, 2 hits, packing 1.
 const triangle=compile(3,observe([1,1,1],[2]));
 check(support(triangle.sparse)===2,'triangle');
 return {...totals,flatExample:v,contradiction,triangle};
}
if(typeof module!=='undefined'&&require.main===module)console.log(JSON.stringify(census(),null,2));
