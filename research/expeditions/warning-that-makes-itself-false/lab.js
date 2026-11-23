// MHAC #226 — exact bounded integer arithmetic, no empirical parameters.
// Run with Node.js: node lab.js
const result = (function lab(){
  "use strict";
  function check(N,u,v,t) {
    if(!Number.isSafeInteger(N)||N<1||N>1000||![u,v,t].every(Number.isSafeInteger)||u<0||v<0||u>N||v>N||t<1||t>N)throw new RangeError("Require integer grid 1..1000, risks 0..N, threshold 1..N");
  }
  function response(q,u,v,t){return q<t?u:v}
  function analysis(N,u,v,t){
    check(N,u,v,t);
    const fixed=[];if(u<t)fixed.push(u);if(v>=t)fixed.push(v);
    const a=Math.min(u,t-1),b=Math.max(v,t);
    const residual=Math.min(Math.abs(u-a),Math.abs(v-b));
    // Brier numerator with common denominator N^3.
    const loss=(q,y)=>N*(q-y)**2+N*y*(N-y);
    const candidates=[[a,loss(a,u)],[b,loss(b,v)]];
    const best=Math.min(...candidates.map(x=>x[1]));
    return {fixed,residual,best,bestReports:candidates.filter(x=>x[1]===best).map(x=>x[0]),cycle:u>=t&&v<t,soft:(u===0&&v===N)?null:[u,N+u-v]};
  }
  function brute(N,u,v,t){
    let fixed=[],residual=Infinity,best=Infinity,bestReports=[];
    for(let q=0;q<=N;q++){
      const y=response(q,u,v,t),error=Math.abs(y-q);
      const loss=y*(N-q)**2+(N-y)*q*q;
      if(q===y)fixed.push(q);
      residual=Math.min(residual,error);
      if(loss<best){best=loss;bestReports=[q]}else if(loss===best)bestReports.push(q);
    }
    return {fixed,residual,best,bestReports};
  }
  function assert(x,msg){if(!x)throw Error(msg)}
  function equal(a,b){return JSON.stringify(a)===JSON.stringify(b)}
  function census(max=20){
    let models=0,initialReports=0,cycleModels=0,twoFixed=0,scoreConflict=0,softChecks=0;
    for(let N=1;N<=max;N++)for(let t=1;t<=N;t++)for(let u=0;u<=N;u++)for(let v=0;v<=N;v++){
      const a=analysis(N,u,v,t),b=brute(N,u,v,t);
      for(const k of Object.keys(b))assert(equal(a[k],b[k]),JSON.stringify([N,u,v,t,k,a,b]));
      models++;
      if(a.fixed.length===2)twoFixed++;
      if(a.fixed.length>0&&!a.bestReports.some(q=>a.fixed.includes(q)))scoreConflict++;
      if(a.cycle){
        cycleModels++;
        assert(u!==v&&response(u,u,v,t)===v&&response(v,u,v,t)===u,"cycle");
        // Both reports equally weighted: total predicted mass equals total observed mass, but report-wise gaps persist.
        assert(u+v===response(u,u,v,t)+response(v,u,v,t),"mean equality");
        assert((u-v)**2>0,"nonzero reliability gap");
      }
      if(a.soft){
        const [num,den]=a.soft;
        assert(den>0&&num>=0&&num<=den,"soft root range");
        assert(num*N===u*(den-num)+v*num,"soft root identity");
      }else assert(u===0&&v===N,"all q roots");
      softChecks++;
      for(let q=0;q<=N;q++){
        const y=response(q,u,v,t),z=response(y,u,v,t),w=response(z,u,v,t);
        assert(a.cycle?(z!==y&&w===y):(z===w&&a.fixed.includes(z)),"retraining dynamics");
        initialReports++;
      }
    }
    return {max,models,initialReports,cycleModels,twoFixed,scoreConflict,softChecks};
  }
  function main(){
    const result=census();
    const examples={
      preventive:analysis(10,8,2,5),
      selfFulfilling:analysis(10,2,9,5),
      scoreConflict:analysis(100,29,0,30),
      boundary:analysis(10,5,2,5),
      exogenous:analysis(10,6,6,5),
    };
    assert(equal(examples.preventive.fixed,[])&&examples.preventive.residual===3,"preventive fixture");
    assert(equal(examples.selfFulfilling.fixed,[2,9]),"two fixed fixture");
    assert(equal(examples.scoreConflict.fixed,[29])&&equal(examples.scoreConflict.bestReports,[30]),"score conflict fixture");
    assert(examples.boundary.residual===1,"boundary grid");
    assert(equal(examples.exogenous.fixed,[6]),"exogenous control");
    let refused=0;for(const args of [[0,0,0,0],[10,-1,0,1],[10,0,11,1],[10,0,0,0],[10,1.2,0,1]]){try{analysis(...args)}catch(e){if(e instanceof RangeError)refused++;else throw e}}
    assert(refused===5,"malformed input");
    return {census:result,examples,refused};
  }
  return main();
})();
console.log(JSON.stringify(result, null, 2));
