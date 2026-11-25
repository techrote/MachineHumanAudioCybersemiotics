'use strict';
// Exact integer synthetic lab; run node lab.js.
function laboratory(){
 const assert=(v,msg)=>{if(!v)throw Error(msg)};
 const pc=x=>{let n=0;while(x){x&=x-1;n++}return n};
 const sign=(s,x)=>(s>>x)&1?1:-1;
 const chr=(a,x)=>pc(a&x)%2?-1:1;
 const range=n=>Array.from({length:n},(_,i)=>i);
 const eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
 const c={balancedFunctions:0,orientationCandidates:0,validOrientations:0,allMixedOrientations:0,directChannelCells:0,decoderCells:0,targetEvaluations:0,targetLabelCells:0,noiseFunctionChecks:0,affineSets:0};
 const fs=range(256).filter(s=>(s&1)&&pc(s)===4);
 c.balancedFunctions=fs.length;
 // classify using shell sums, not Walsh coefficients
 const key=v=>v.join(",");
 const shell=(s,y)=>range(4).map(d=>range(8).filter(x=>pc(x^y)===d).reduce((a,x)=>a+sign(s,x)*sign(s,y),0));
 const pat={
  D:["1,1,-1,-1"], P:["1,-1,-1,1"], Q:["1,-3,3,-1"],
  B:["1,1,-1,-1","1,-1,-1,1"], M:["1,-1,1,-1","1,3,-3,-1"],
  C:["1,-1,1,-1","1,-3,1,1","1,1,-3,1"]
 };
 const expected={D:3,P:3,Q:1,B:12,M:4,C:12}, classes={},counts={};
 for(const s of fs){
  const shells=range(8).map(y=>key(shell(s,y)));
  const t=Object.keys(pat).find(t=>eq([...new Set(shells)].sort(),[...pat[t]].sort()));
  assert(t,"unknown balanced function");
  const mult={};for(const a of shells)mult[a]=(mult[a]||0)+1;
  const want={D:[8],P:[8],Q:[8],B:[4,4],M:[2,6],C:[2,2,4]}[t];
  assert(eq(Object.values(mult).sort((a,b)=>a-b),want),"shell multiplicity");
  classes[s]=t;counts[t]=(counts[t]||0)+1;
 }
 for(const t in expected)assert(counts[t]===expected[t],"type count");
 const valid=[];
 for(let a=0;a<35;a++)for(let b=a+1;b<35;b++)for(let d=b+1;d<35;d++)for(let e=d+1;e<35;e++){
  c.orientationCandidates++;
  const z=[fs[a],fs[b],fs[d],fs[e]];
  if(z.some((u,i)=>z.slice(i+1).some(v=>pc(u^v)!==4))||pc(z.reduce((a,b)=>a^b,0))!==4)continue;
  // direct antipodal coverage as second check
  const reps=new Set(range(8).map(x=>{const v=z.reduce((a,s,i)=>a+((s>>x)&1)*(1<<i),0);return Math.min(v,v^15)}));
  assert(reps.size===8,"antipodal coverage");
  c.validOrientations++;assert(z.some(s=>!["D","M"].includes(classes[s])),"all strong types");
  if(z.every(s=>classes[s]==="B"))c.allMixedOrientations++;
  valid.push(z);
 }
 assert(c.orientationCandidates===52360&&c.validOrientations===840&&c.allMixedOrientations===24,"enumeration counts");
 const witness=valid.find(z=>z.every(s=>classes[s]==="B"));
 const noise=(k,q,d,x,y)=>(d-q)**(k-pc(x^y))*q**pc(x^y);
 // exact integer Bayes advantage for each function
 for(const [q,d] of [[1,10],[1,4],[2,5],[1,100],[49,100],[0,1],[1,2]]){
  const rho=d-2*q,D=d**3;
  const values={D:8*rho*d*d,P:8*rho*rho*d,Q:8*rho**3,B:4*rho*d*(d+rho),M:2*rho*(3*d*d+rho*rho),C:Math.max(4*rho*d*d,2*rho*(d+rho)**2)};
  const adv={};
  for(const s of fs){adv[s]=range(8).reduce((a,y)=>a+Math.abs(range(8).reduce((b,x)=>b+sign(s,x)*noise(3,q,d,x,y),0)),0);assert(adv[s]===values[classes[s]],"noise shell formula");c.noiseFunctionChecks++}
  const best=Math.max(...valid.map(z=>Math.min(...z.map(s=>adv[s]))));
  assert(best===values.B&&Math.min(...witness.map(s=>adv[s]))===best,"nonlinear minimax");
 }
 function audit(f,k,q,d,t,den,expectOptimal){
  const n=1<<k,m=f.length,D=n*den*d**k;
  const rows=range(2*m).map(a=>range(n).map(y=>range(n).reduce((v,x)=>{c.directChannelCells++;return v+(den+(a%2?-1:1)*t[a>>1]*f[a>>1][x])*noise(k,q,d,x,y)},0)));
  for(const row of rows)assert(row.every(v=>v>=0)&&row.reduce((a,b)=>a+b,0)===D,"row normalization");
  for(let y=0;y<n;y++)assert(rows.reduce((a,row)=>a+row[y],0)*n===2*m*D,"uniform output");
  const T=range(m).map(i=>range(n).reduce((a,y)=>{c.decoderCells+=2;return a+Math.abs(rows[2*i][y]-rows[2*i+1][y])},0));
  // direct full balanced target audit
  let M=0;
  for(let mask=0;mask<1<<(2*m);mask++)if(pc(mask)===m){
   c.targetEvaluations++;
   const v=range(n).reduce((a,y)=>{c.targetLabelCells++;return a+Math.abs(rows.reduce((b,row,i)=>b+sign(mask,i)*row[y],0))},0);
   M=Math.max(M,v);
  }
  const R=range(1<<m).reduce((a,s)=>a+Math.abs(T.reduce((b,v,i)=>b+sign(s,i)*v,0)),0);
  assert(M*(1<<m)>=R,"heterogeneous bound");
  if(expectOptimal!==null)assert((M*(1<<m)===R)===expectOptimal,"end-to-end optimality status");
  return {T:T.map(v=>v/(2*D)),V:(1+M/(2*m*D))/2,R:(1+R/((1<<m)*m*2*D))/2};
 }
 const af=(m)=>{const k=m-1;return [...range(k).map(i=>1<<i),3].map(a=>range(1<<k).map(x=>chr(a,x)))};
 const result={};
 for(const m of [4,6,8]){
  const k=m-1,f=af(m);
  for(const [q,d] of [[1,10],[1,4]]){
   const raw=audit(f,k,q,d,range(m).map(()=>1),1,true);
   const repaired=audit(f,k,q,d,range(m).map(i=>i===m-1?d:d-2*q),d,true);
   const rho=(d-2*q)/d;
   assert(raw.T.every((v,i)=>Math.abs(v-(i===m-1?rho*rho:rho))<1e-12),"affine utility");
   assert(repaired.T.every(v=>Math.abs(v-rho*rho)<1e-12)&&repaired.V<raw.V,"repair");
   if(m===4&&q===1&&d===10)result.affine={raw,repaired};
  }
 }
 // Full cube extra-slot witness
 const full=range(4).map(i=>range(16).map(x=>chr(1<<i,x)));
 result.full=audit(full,4,1,10,[1,1,1,1],1,true);
 result.nonlinear=audit(witness.map(s=>range(8).map(x=>sign(s,x))),3,1,10,[1,1,1,1],1,false);
 assert(result.nonlinear.T.every(t=>Math.abs(t-.72)<1e-12),"nonlinear recovery");
 // Exhaust all affine row sets for k=3,5 (choose k+1 from nonzero characters).
 // Valid iff unique dependence is odd, equivalently even subset XORs never zero.
 for(const k of [3,5]){
  const m=k+1;let good=0, best=99;
  function rec(arr,start){
   if(arr.length===m){
    let even=true;for(let s=1;s<(1<<m);s++)if(pc(s)%2===0&&arr.reduce((a,x,i)=>a^(((s>>i)&1)?x:0),0)===0){even=false;break}
    if(!even)return;
    c.affineSets++;good++;
    const weights=arr.map(pc);assert(new Set(weights).size>1,"equal affine degree");best=Math.min(best,Math.max(...weights));return;
   }
   for(let a=start;a<(1<<k);a++)rec([...arr,a],a+1);
  }
  rec([],1);assert(good>0&&best===2,"affine minimax");
 }
 return {counts:c,witness,classes:counts,results:result};
}
console.log(JSON.stringify(laboratory(), null, 2));
