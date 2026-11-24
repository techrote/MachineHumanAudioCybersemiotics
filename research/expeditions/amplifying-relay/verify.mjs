import {model,rate,peak,guards,fromWeights,stringify} from "./relay.mjs";
const check=(x,msg)=>{if(!x)throw Error(msg)};
const abs=x=>x<0n?-x:x;
const pow=(x,n)=>x**BigInt(n);
const eq=(x,y)=>x.num*y.den===y.num*x.den;
const gt=(x,y)=>x.num*y.den>y.num*x.den;
const mm=(a,b)=>a.map(row=>b[0].map((_,j)=>row.reduce((s,x,k)=>s+x*b[k][j],0n)));
const tr=a=>a.reduce((s,row,i)=>s+row[i],0n);
const norm=a=>a[0].reduce((m,_,j)=>{const s=a.reduce((z,r)=>z+abs(r[j]),0n);return s>m?s:m;},0n);
function direct(g,blocked=new Set(),length=g.n){
 const matrices=g.ms.map(m=>m.u.map(x=>m.v.map(y=>x*y)));
 let state="strictly-decaying",p={num:0n,den:1n};
 function walk(word,m){
  const l=word.length,den=pow(g.den,l),first=word[0],last=word.at(-1);
  const n={num:norm(m),den};if(gt(n,p))p=n;
  if(!blocked.has(last+":"+first)){
   const t=abs(tr(m));
   if(t>den)state="growing";
   else if(t===den&&state!=="growing")state="bounded-neutral";
  }
  if(l===length)return;
  for(let j=0;j<g.n;j++)if(!blocked.has(last+":"+j))walk([...word,j],mm(matrices[j],m));
 }
 for(let i=0;i<g.n;i++)walk([i],matrices[i]);
 return {state,p};
}
function brute(g,opts){
 const edges=[];for(let i=0;i<g.n;i++)for(let j=0;j<g.n;j++)if(g.weights[i][j]&&!opts.locked?.includes(i+":"+j))edges.push(i+":"+j);
 let best=Infinity,solutions=[];
 for(let mask=0;mask<2**edges.length;mask++){
  const s=edges.filter((_,i)=>mask&(1<<i)),cost=s.reduce((n,e)=>n+(opts.costs?.[e]??1),0);
  if(cost>best)continue;
  const d=direct(g,new Set(s));
  if(d.state==="growing"||(opts.strict!==false&&d.state==="bounded-neutral")||(opts.cap&&gt(d.p,opts.cap)))continue;
  if(cost<best){best=cost;solutions=[];}solutions.push(s.sort().join(","));
 }
 return {cost:Number.isFinite(best)?best:null,solutions:solutions.sort()};
}
export function experiment(){
 const hist={"strictly-decaying":0,"bounded-neutral":0,"growing":0};
 const hidden={neutral:0,growing:0};let matrixChecks=0,guardChecks=0,peakChecks=0;
 const values=[0,1,2,4],positions=[[0,1],[0,2],[1,0],[1,2],[2,0],[2,1]];
 const repairs={};
 for(let code=0;code<4096;code++){
  const w=Array.from({length:3},()=>[0,0,0]);let z=code;
  for(const [i,j] of positions){w[i][j]=values[z%4];z=Math.floor(z/4);}
  // Zero incoming column is a zero mode. Retain it explicitly with a
  // fourth, unreachable input coordinate, so the matrix remains rank one.
  const g=model(w.map((_,i)=>({u:[0,1,2,3].map(j=>j===i?1:0),v:[...w.map(row=>row[i]),w.every(row=>row[i]===0)?1:0]})),2);
  const r=rate(g),d=direct(g);check(r.status===d.state,"matrix rate "+code);matrixChecks++;hist[r.status]++;
  const pairs=positions.every(([i,j])=>w[i][j]*w[j][i]<4);
  if(pairs&&r.status==="bounded-neutral")hidden.neutral++;
  if(pairs&&r.status==="growing")hidden.growing++;
  if(r.status!=="growing"){check(eq(peak(g),d.p),"matrix peak "+code);peakChecks++;}
  const gr=guards(g);check(gr.status==="optimal","guard failed "+code);repairs[gr.cost]=(repairs[gr.cost]??0)+1;
  // Deterministic strided sample of the full population: direct full-matrix
  // exhaustive subset check, with weighted, locked and peak-constrained options.
  if(code%32===0){
   for(const opts of [{strict:true},{strict:false,costs:{"0:1":3,"1:2":2},locked:["2:0"],cap:{num:2n,den:1n}}]){
    const got=guards(g,opts),want=brute(g,opts);
    check(got.status===(want.cost===null?"impossible":"optimal")&&got.cost===want.cost&&JSON.stringify(got.solutions.map(s=>s.join(",")).sort())===JSON.stringify(want.solutions),"guard oracle "+code);guardChecks++;
   }
  }
 }
 // Signed factors: direct check includes cancellations and noncoordinate vectors.
 let seed=8131;
 const rand=()=>{seed=(Math.imul(1664525,seed)+1013904223)>>>0;return seed;};
 for(let t=0;t<64;t++){
  const modes=Array.from({length:3},()=>({u:[1,(rand()>>>16)%5-2,(rand()>>>16)%5-2],v:[1,(rand()>>>16)%5-2,(rand()>>>16)%5-2]}));
  const g=model(modes,3),r=rate(g),d=direct(g);
  check(r.status===d.state,"signed rate "+t);matrixChecks++;
  if(r.status!=="growing"){check(eq(peak(g),direct(g,new Set(),5).p),"signed peak "+t);peakChecks++;}
 }
 const ring=fromWeights([[0,16,0],[0,0,16],[1,0,0]],4);
 const minimal=guards(ring),choices=minimal.solutions.map(s=>({blocked:s,rate:rate(ring,new Set(s)),peak:peak(ring,new Set(s))}));
 const limited=guards(ring,{cap:{num:4n,den:1n}});
 check(limited.solutions.length===1&&limited.solutions[0][0]==="1:2","peak guard");
 check(guards(ring,{cap:{num:3n,den:1n}}).status==="impossible","singleton peak cannot be guarded");
 check(guards(ring,{locked:["0:1","1:2","2:0"]}).status==="impossible","locked cycle");
 check(guards(ring,{budget:1}).status==="budget-exhausted","budget isn't impossibility");
 const neutral=fromWeights([[0,2],[2,0]],2);
 check(rate(neutral).status==="bounded-neutral"&&guards(neutral,{strict:false}).cost===0&&guards(neutral).cost===1,"neutral distinction");
 const decaying=fromWeights([[0,4],[1,0]],4);
 check(rate(decaying).status==="strictly-decaying"&&eq(peak(decaying),{num:1n,den:1n}),"decaying control");
 return {population:{description:"all 4^6 off-diagonal chronological transition weights in {0,1/2,1,2}; zero diagonal; zero modes replaced by nonzero maps from an unreachable fourth coordinate",histogram:hist,pair_strictly_decaying_but_global: hidden,minimum_strict_guard_cost:repairs},qualification:{direct_matrix_rate_checks:matrixChecks,direct_matrix_peak_checks:peakChecks,exhaustive_guard_oracle_checks:guardChecks,explicit_negative_controls:5},ring:{weights:[[0,16,0],[0,0,16],[1,0,0]],denominator:4,rate:rate(ring),minimum_guard:minimal,choices,peak_cap_four:limited},neutral:rate(neutral),decaying:rate(decaying)};
}
if(typeof process!=="undefined"&&process.argv[1]?.endsWith("verify.mjs"))console.log(stringify(experiment()).trimEnd());
