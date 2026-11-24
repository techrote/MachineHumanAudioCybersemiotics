// Run: node verify.cjs (standard library only).
function verify(api) {
  const {compile,leakage16,apply}=api;
  const eq=(a,b)=>{if(JSON.stringify(a)!==JSON.stringify(b))throw Error(JSON.stringify({a,b}));};
  function words(n,k,visit,p=[]){if(n===0){visit(p);return;}for(let i=0;i<k;i++)words(n-1,k,visit,[...p,i]);}
  let matrixCases=0, tiedCases=0, anchorCases=0, candidates=0, tiedOptima=0, refusals=0;
  // Direct basis-vector synthesis/reanalysis, separately from graph expression.
  for(let n=3;n<=4;n++) words(2*n,3,w=>{
    let pairs=Array.from({length:n},(_,i)=>w.slice(2*i,2*i+2));
    let columns=Array.from({length:n},(_,j)=>apply(Array.from({length:n},(_,i)=>Number(i===j)),pairs).residual);
    eq(columns.flat().reduce((s,x)=>s+64*x*x,0),4*leakage16(pairs));
    matrixCases++;
  });
  for(let n=3;n<=7;n++) words(n,3,g=>{
    let columns=Array.from({length:n},(_,j)=>apply(Array.from({length:n},(_,i)=>Number(i===j)),g.map(v=>[v,v])).residual);
    for(let i=0;i<n;i++)for(let j=0;j<n;j++){
      let dot=columns[i].reduce((s,x,k)=>s+x*columns[j][k],0);
      eq(4*dot,i===j?(g[i]-g[(i+n-1)%n])**2:0);
    }
    tiedCases++;
  });
  // Exhaustive search of all free integer gains, anchors at 0 and d.
  for(let n=3;n<=7;n++)for(let d=1;d<n;d++)for(let M=1;M<=4;M++){
    let bestE=Infinity,bestS=Infinity,both=0;
    words(n-2,M+1,w=>{
      let j=0,g=Array.from({length:n},(_,i)=>i===0?0:i===d?M:w[j++]);
      let z=g.map((v,i)=>v-g[(i+1)%n]);
      let E=z.reduce((s,x)=>s+x*x,0),S=Math.max(...z.map(Math.abs));
      if(E<bestE){bestE=E;both=0;}bestS=Math.min(bestS,S);candidates++;
    });
    let p=compile(n,[[0,0],[d,M]]);
    eq(p.g[0],0);eq(p.g[d],M);eq(p.energyTimes4,bestE);eq(p.operatorNormTimes2,bestS);
    anchorCases++;tiedOptima++;
  }
  // Several anchors, including wrap, single anchor, and infeasible input.
  eq(compile(7,[[5,2],[1,4],[3,0]]).g,[3,4,2,0,1,2,2]);
  eq(compile(5,[[2,7]]).g,[7,7,7,7,7]);
  for(const f of [()=>compile(2,[[0,0]]),()=>compile(5,[]),()=>compile(5,[[1,0],[1,1]]),()=>compile(5,[[0,-1]]),()=>compile(5,[[5,1]])]){
    try{f();}catch(e){refusals++;continue;}throw Error("missing refusal");
  }
  // Nonconstant mask can be consistent for a particular signal.
  const p=[[0,0],[0,0],[1,1],[1,1]];
  eq(apply([0,1,0,0],p).residual,Array(8).fill(0));
  if(!apply([1,0,0,0],p).residual.some(Boolean))throw Error("missing counterexample");
  let frontier=[];
  for(let n of [4,8,16,32,64,128]){
    let hard=Array.from({length:n},(_,i)=>i<n/2?0:64);
    let ramp=compile(n,[[0,0],[n/2,64]]);
    frontier.push({n,hardE4:leakage16(hard.map(v=>[v,v]))/4,rampE4:ramp.energyTimes4,hardS2:64,rampS2:ramp.operatorNormTimes2});
  }
  return {matrixCases,tiedCases,anchorCases,candidates,tiedOptima,refusals,frontier};
}
if(typeof module!=="undefined"&&typeof require!=="undefined"&&require.main===module)console.log(JSON.stringify(verify(require("./mask.cjs")),null,2));
