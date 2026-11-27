'use strict';
// Synthetic finite oracle. Run node laboratory.cjs. No dependencies.
function laboratory(){
 const assert=(v,m)=>{if(!v)throw Error(m)};
 const pop=x=>{let n=0;for(;x;x&=x-1)n++;return n};
 const sum=xs=>xs.reduce((a,b)=>a+b,0);
 const key=(c,u,r)=>`${c},${u},${r}`;
 const unit=()=>new Map([[key(0,0,0),1n]]);
 const put=(m,k,v)=>m.set(k,(m.get(k)||0n)+v);
 const unpack=k=>k.split(",").map(Number);
 const conv=(a,b)=>{let o=new Map();for(const [k,v] of a)for(const [l,w] of b){const x=unpack(k),y=unpack(l);put(o,key(...x.map((z,i)=>z+y[i])),v*w)}return o};
 const canon=m=>[...m].map(([k,v])=>[k,String(v)]).sort((a,b)=>a[0].localeCompare(b[0],"en"));
 const equal=(a,b)=>JSON.stringify(canon(a))===JSON.stringify(canon(b));
 const mask=t=>Number.isInteger(t)?1<<t:t.reduce((m,x)=>m|mask(x),0);
 const nodes=t=>Number.isInteger(t)?[t]:[t,...t.flatMap(nodes)];
 const minCost=(t,s)=>!(mask(t)&s)?1:Number.isInteger(t)?0:sum(t.map(x=>minCost(x,s)));
 const savings=(t,s)=>Number.isInteger(t)?0:((mask(t)&s)?0:t.length-1)+sum(t.map(x=>savings(x,s)));
 // Per-event polynomial: cut count, invisible count, root cut count.
 function per(t,s,root=true){
  let o;
  if(Number.isInteger(t))o=s&mask(t)?unit():new Map([[key(1,0,root?1:0),1n]]);
  else {o=t.map(x=>per(x,s,false)).reduce(conv,unit());if(!(mask(t)&s))put(o,key(1,0,root?1:0),1n)}
  if(root&&s===0)o=new Map([...o].map(([k,v])=>{const [c,,r]=unpack(k);return [key(c,1,r),v]}));
  return o
 }
 // Independent enumeration of all edge subsets, discarding intersecting clades.
 function enumerate(t){
  const ns=nodes(t).map(mask),all=mask(t),out=new Map();
  for(let m=0;m<2**ns.length;m++){
   let removed=0,ok=true;
   for(let i=0;i<ns.length;i++)if(m&(1<<i)){if(removed&ns[i]){ok=false;break}removed|=ns[i]}
   if(!ok)continue;
   const s=all^removed,k=key(pop(m),s===0?1:0,m&1?1:0);
   if(!out.has(s))out.set(s,new Map());put(out.get(s),k,1n);
  }
  return out
 }
 const rows=m=>[...m].map(([k,v])=>({cost:unpack(k)[0],invisible:unpack(k)[1],rootCuts:unpack(k)[2],count:String(v)})).sort((a,b)=>a.cost-b.cost||a.invisible-b.invisible||a.rootCuts-b.rootCuts);
 const support=m=>[...new Set([...m.keys()].map(k=>unpack(k)[0]))].sort((a,b)=>a-b);
 const interval=(s,d)=>s.length&&s.every((x,i)=>x===s[0]+d*i);
 function infer(t,w,vs){
  const h=vs.length,ps=Array.from({length:2**h},(_,s)=>per(t,s)),memo=new Map();
  function rec(i,p){
   if(i===w.length)return p.every((a,j)=>a===vs[j].length)?unit():new Map();
   const k=i+":"+p.join(",");if(memo.has(k))return memo.get(k);
   let ready=0,o=new Map();for(let j=0;j<h;j++)if(vs[j][p[j]]===w[i])ready|=1<<j;
   for(let s=ready;;s=(s-1)&ready){
    const a=conv(ps[s],rec(i+1,p.map((v,j)=>v+((s>>j)&1))));
    for(const [k,v] of a)put(o,k,v);
    if(!s)break
   }
   memo.set(k,o);return o
  }
  return rec(0,Array(h).fill(0))
 }
 const trees=[{name:"binaryPair",t:[0,1],arity:2},{name:"balancedFour",t:[[0,1],[2,3]],arity:2},{name:"crossedFour",t:[[0,2],[1,3]],arity:2},{name:"combFour",t:[0,[1,[2,3]]],arity:2},{name:"starThree",t:[0,1,2],arity:3},{name:"ternaryNine",t:[[0,1,2],[3,4,5],[6,7,8]],arity:3},{name:"mixed",t:[[0,1,2],3],arity:0}];
 let singleMasks=0,canonicalEdgeSets=0,reportCases=0,weightedHistories=0n,strictParsimonyCases=0,topologyChanges=0,budgetChecks=0;
 let comparison=new Map(),firstStrict=null,firstTopology=null;
 const words=n=>n?words(n-1).flatMap(s=>[s+"A",s+"B"]):[""];
 const total=m=>[...m.values()].reduce((a,b)=>a+b,0n);
 for(const {name,t,arity} of trees){
  const all=mask(t),h=pop(all),br=enumerate(t);
  for(let s=0;s<=all;s++){
   const p=per(t,s),b=br.get(s);assert(equal(p,b),"edge subsets "+name+" "+s);
   const supp=support(p),miss=h-pop(s);
   assert(supp[0]===minCost(t,s)&&supp.at(-1)===miss,"extrema");
   assert(miss-minCost(t,s)===savings(t,s),"savings");
   if(arity)assert(interval(supp,arity-1),"uniform arity support");
   for(let B=supp[0];B<=miss;B++){
    const r=rows(p).filter(x=>x.cost<=B);
    if(arity)assert(Math.min(...r.map(x=>x.rootCuts))===Math.max(0,(s===0?1:0)-Math.floor((B-supp[0])/(arity-1))),"root budget");
    budgetChecks++;
   }
   singleMasks++;canonicalEdgeSets+=Number(total(p));
  }
  if(h>4)continue;
  for(let n=0;n<=3;n++)for(const w of words(n)){
   // Independent grouping of every ordered sequence of antichain choices by exact reports.
   const agg=new Map();
   function visit(i,vs,c,u,r,weight){
    if(i===n){const k=JSON.stringify(vs);if(!agg.has(k))agg.set(k,new Map());put(agg.get(k),key(c,u,r),weight);return}
    for(const [s,p] of br){
     const next=vs.map((v,j)=>v+((s>>j)&1?w[i]:""));
     for(const [k,a] of p){const [x,y,z]=unpack(k);visit(i+1,next,c+x,u+y,r+z,weight*a)}
    }
   }
   visit(0,Array(h).fill(""),0,0,0,1n);
   let mass=0n;
   for(const [k,b] of agg){
    const vs=JSON.parse(k),a=infer(t,w,vs);assert(equal(a,b),"joint polynomial "+name+" "+w+" "+k);
    const supp=support(a),rr=rows(a),leafOnly=h*n-sum(vs.map(v=>v.length)),mn=supp[0];
    assert(supp.at(-1)===leafOnly,"constant leaf-only count");
    if(arity)assert(interval(supp,arity-1),"joint support");
    const umin=Math.min(...rr.map(x=>x.invisible)),uminOptimal=Math.min(...rr.filter(x=>x.cost===mn).map(x=>x.invisible));
    if(uminOptimal>umin){strictParsimonyCases++;if(!firstStrict)firstStrict={name,w,vs,minCost:mn,minInvisible:umin,minInvisibleAtMinCost:uminOptimal,polynomial:rr}}
    if(name==="balancedFour")comparison.set(w+":"+k,mn);
    if(name==="crossedFour"&&comparison.get(w+":"+k)!==mn){topologyChanges++;if(!firstTopology)firstTopology={w,vs,balanced:comparison.get(w+":"+k),crossed:mn}}
    mass+=total(a);reportCases++;
   }
   const perEvent=BigInt([...br.values()].reduce((v,p)=>v+Number(total(p)),0));
   assert(mass===perEvent**BigInt(n),"mass");weightedHistories+=mass;
  }
 }
 const fixture=(t,w,vs)=>({tree:t,w,reports:vs,polynomial:rows(infer(t,w,vs)),costSupport:support(infer(t,w,vs))});
 const examples={
  repeatedPair:fixture([0,1],"AA",["A","A"]),
  sharedSiblings:fixture([[0,1],[2,3]],"AA",["A","A","AA","AA"]),
  separatedLeaves:fixture([[0,2],[1,3]],"AA",["A","A","AA","AA"]),
  polytomy:fixture([0,1,2],"A",["","",""]),
  binaryRefinement:fixture([0,[1,2]],"A",["","",""]),
  mixedClade:fixture([[0,1,2],3],"A",["","","","A"]),
  impossible:fixture([0,1],"AB",["BA","A"])
 };
 assert(JSON.stringify(examples.polytomy.costSupport)==="[1,3]","polytomy gap");
 assert(JSON.stringify(examples.binaryRefinement.costSupport)==="[1,2,3]","refinement");
 assert(examples.repeatedPair.polynomial.some(x=>x.cost===1&&x.invisible===1&&x.rootCuts===1)&&examples.repeatedPair.polynomial.some(x=>x.cost===2&&x.invisible===0&&x.rootCuts===0),"parsimony counterexample");
 assert(examples.sharedSiblings.costSupport[0]===1&&examples.separatedLeaves.costSupport[0]===2,"topology example");
 assert(!examples.impossible.costSupport.length,"reject impossible");
 return {singleMasks,canonicalEdgeSets,reportCases,weightedHistories:String(weightedHistories),budgetChecks,strictParsimonyCases,topologyChanges,firstStrict,firstTopology,examples,assertionFailures:0}
}
console.log(JSON.stringify(laboratory(),null,2));
