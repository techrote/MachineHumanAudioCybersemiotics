"use strict";
function run(){
  const assert=(x,msg)=>{if(!x)throw Error(msg)};
  const comb=(a,k)=>{if(!k)return [[]];if(a.length<k)return [];return a.flatMap((x,i)=>comb(a.slice(i+1),k-1).map(t=>[x,...t]))};
  const det=a=>a.length===0?1:a[0].reduce((s,x,i)=>s+(-1)**i*x*det(a.slice(1).map(r=>r.filter((_,j)=>i!==j))),0);
  const bit=(v,g)=>(v>>g)&1;
  const cube=(n)=>Array.from({length:2**n},(_,i)=>i);
  const parity=x=>x.toString(2).split("1").length%2===0?1:0;
  function witness(words,n){
    if(!Number.isInteger(n)||n<1||n>4||!Array.isArray(words)||new Set(words).size!==words.length||words.some(v=>!Number.isInteger(v)||v<0||v>=2**n))throw Error("invalid cube family");
    const rows=Array.from({length:n+1},(_,i)=>i);
    const entry=(i,v)=>i===0?1:2*bit(v,i-1)-1;
    for(let k=1;k<=Math.min(n+1,words.length);k++)for(const w of comb(words,k))for(const rr of comb(rows,k)){
      const M=rr.map(i=>w.map(v=>entry(i,v)));
      let den=det(M);if(!den)continue;
      let nums=w.map((_,j)=>det(M.map((r,l)=>r.map((v,h)=>h===j?Number(rr[l]===0):v))));
      if(den<0){den=-den;nums=nums.map(x=>-x)}
      if(nums.some(x=>x<=0))continue;
      if(rows.every(i=>w.reduce((s,v,j)=>s+nums[j]*entry(i,v),0)===(i===0?den:0)))return {words:w,nums,den};
    }
    return null;
  }
  function deterministic(words,n){return words.some(v=>words.includes(v^((1<<n)-1)))}
  function gridSupports(n){
    const C=cube(n), results=new Map();
    for(let a=0;a<C.length;a++)for(let b=a;b<C.length;b++)for(let c=b;c<C.length;c++)for(let d=c;d<C.length;d++){
      const w=[a,b,c,d];
      if(Array.from({length:n},(_,g)=>g).some(g=>w.reduce((s,v)=>s+bit(v,g),0)!==2))continue;
      const m=w.reduce((s,v)=>s|(1<<v),0), k=new Set(w).size;
      results.set(m,k);
    }
    return results;
  }
  const census={};
  for(const n of [1,2,3]){
    const C=cube(n),grid=gridSupports(n),stats={families:0,infeasible:0,deterministic:0,randomizedOnly:0,minLabels:{}};
    for(let mask=0;mask<2**C.length;mask++){
      const words=C.filter(v=>mask&(1<<v)),w=witness(words,n);
      const oracle=[...grid].filter(([m])=>(m&mask)===m).map(([,k])=>k);
      const expected=oracle.length?Math.min(...oracle):null;
      assert((w?w.words.length:null)===expected,"cube oracle");
      const d=deterministic(words,n);assert(d===(expected===2),"deterministic criterion");
      stats.families++;
      if(!w)stats.infeasible++;else{
        stats[d?"deterministic":"randomizedOnly"]++;
        stats.minLabels[expected]=(stats.minLabels[expected]||0)+1;
      }
    }
    census[n]=stats;
  }
  const even=cube(3).filter(v=>parity(v)===0);
  assert(even.length===4&&!deterministic(even,3),"parity control");
  const ew=witness(even,3);assert(ew.words.length===4&&ew.nums.every(x=>4*x===ew.den),"unique parity weights");
  // Each partition of six states: state index 2*g+b. Independent contexts enforce
  // at most one state per group; forbidden odd triples exclude any full odd support.
  function validBlock(block){
    const by=[0,1,2].map(g=>block.filter(x=>(x>>1)===g));
    if(by.some(b=>b.length>1))return false;
    if(block.length<3)return true;
    return by.reduce((s,b)=>s^(b[0]&1),0)===0;
  }
  // Explicit context intersection oracle independent of the parity predicate.
  const contexts=[];
  for(let g=0;g<3;g++)contexts.push([[2*g,1],[2*g+1,2]]);
  for(const v of cube(3).filter(x=>parity(x)===1))contexts.push([0,1,2].map(g=>[2*g+bit(v,g),7^(1<<g)]));
  function contextValid(block){return contexts.every(c=>c.filter(([s])=>block.includes(s)).reduce((a,[,m])=>a&m,7)!==0)}
  for(let m=0;m<64;m++){const b=Array.from({length:6},(_,i)=>i).filter(i=>m&(1<<i));assert(validBlock(b)===contextValid(b),"context realization")}
  function* partitions(n,blocks=[]){if(!n){yield blocks;return}const v=6-n;for(let i=0;i<blocks.length;i++)yield*partitions(n-1,blocks.map((b,j)=>j===i?[...b,v]:b));yield*partitions(n-1,[...blocks,[v]])}
  let partitionCount=0,validCount=0,minTV4=Infinity,minWitness=null;
  for(const p of partitions(6)){
    partitionCount++;if(!p.every(contextValid))continue;validCount++;
    const rows=[0,1,2].map(g=>p.map(b=>b.filter(x=>(x>>1)===g).length));
    let tv4=0;for(const [a,b] of comb(rows,2))tv4=Math.max(tv4,a.reduce((s,x,i)=>s+Math.abs(x-b[i]),0));
    if(tv4<minTV4){minTV4=tv4;minWitness=p}
  }
  assert(partitionCount===203&&minTV4===2,"deterministic leakage");
  // Two equal-size groups: compare all bipartite graphs through size 3
  // to an exhaustive bijection oracle and a Hall-subset test.
  function* perm(a){if(!a.length){yield [];return}for(let i=0;i<a.length;i++)for(const tail of perm(a.filter((_,j)=>i!==j)))yield [a[i],...tail]}
  let graphs=0,matchable=0;
  for(let n=1;n<=3;n++)for(let m=0;m<2**(n*n);m++){
    const edge=(i,j)=>Boolean(m&(1<<(i*n+j)));
    const matched=[...perm(Array.from({length:n},(_,i)=>i))].some(p=>p.every((j,i)=>edge(i,j)));
    let hall=true;for(let s=1;s<2**n;s++){let L=0,R=new Set();for(let i=0;i<n;i++)if(s&(1<<i)){L++;for(let j=0;j<n;j++)if(edge(i,j))R.add(j)}if(R.size<L)hall=false}
    assert(hall===matched,"Hall oracle");graphs++;if(matched)matchable++;
  }
  // Direct transcript counts, same latent state, independent draws.
  const repeated=[];
  for(let k=1;k<=10;k++){
    const rows=[0,1,2].map(g=>{
      const r=new Map();for(let b=0;b<2;b++){
        const labels=even.filter(v=>bit(v,g)===b);assert(labels.length===2,"two eligible labels");
        for(let i=0;i<2**k;i++){const t=Array.from({length:k},(_,j)=>labels[bit(i,j)]).join(",");r.set(t,(r.get(t)||0)+1)}
      }return r;
    });
    const keys=[...new Set(rows.flatMap(r=>[...r.keys()]))],den=2**(k+1);
    assert(rows.every(r=>[...r.values()].reduce((a,b)=>a+b,0)===den),"transcript normalization");
    for(const [a,b] of comb(rows,2)){const l1=keys.reduce((s,t)=>s+Math.abs((a.get(t)||0)-(b.get(t)||0)),0);assert(l1===2*(den-4),"transcript TV")}
    const best=keys.reduce((s,t)=>s+Math.max(...rows.map(r=>r.get(t)||0)),0);
    assert(best===3*den-8,"Bayes classification");
    repeated.push({k,tv:[den-4,den],accuracy:[best,3*den],transcripts:keys.length});
  }
  let refusals=0;for(const [a,n] of [[[1,1],3],[[8],3],[[1.5],3],[[],0],[[],5]]){try{witness(a,n)}catch(e){refusals++}}
  assert(refusals===5,"refusals");
  return {census,even,ew,partitionCount,validCount,minTV4,minWitness,graphs,matchable,repeated,refusals};
}
console.log(JSON.stringify(run(),null,2));
