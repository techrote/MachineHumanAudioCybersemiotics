'use strict';
// Synthetic finite exact checks. Run: node lab.js
function laboratory(){
 const stats={families:0,matchingActions:0,subsetChecks:0,decoderInputs:0,cycleCertificates:0,colourAssignments:0,admissionBudgets:0,seededActionChecks:0};
 const check=(v,msg)=>{if(!v)throw Error(msg)};
 const bits=(n,m)=>Array.from({length:n},(_,i)=>i).filter(i=>m>>i&1);
 const pop=m=>{let n=0;while(m){m&=m-1;n++}return n};
 function subsets(n,k){return Array.from({length:2**n},(_,i)=>i).filter(m=>pop(m)===k)}
 function construct(n,edges){
  check(Number.isInteger(n)&&n>=1&&n<=8,"bounded n");
  check(Array.isArray(edges)&&new Set(edges).size===edges.length&&edges.every(e=>Number.isInteger(e)&&e>0&&e<2**n&&pop(e)>=3),"invalid hyperedge");
  const blocks=[], matching=Array.from({length:n},()=>[]);
  let N=0;
  for(const e of edges){
   const labels=bits(n,e);
   if(labels.length%2===0)labels.push(labels[0+1]); // repeat second, not adjacent to itself; last edge neighbors first and prior last
   const length=labels.length;
   // For original even length >=4, last repeated label is second, distinct from first and preceding label.
   for(let j=0;j<length;j++)matching[labels[j]].push([N+j,N+(j+1)%length]);
   blocks.push({start:N,length,labels,e});
   N+=length;
  }
  if(!N)N=1;
  const maps=matching.map(es=>{
   check(new Set(es.flat()).size===2*es.length,"action is not a matching");
   const f=Array.from({length:N},(_,i)=>i);
   for(const [u,v] of es)f[v]=u;
   stats.matchingActions++;
   return f;
  });
  // Independent reconstruction of collision edges from actual map fibres.
  const collisions=maps.map(f=>{
   const fibers=new Map();f.forEach((y,x)=>{if(!fibers.has(y))fibers.set(y,[]);fibers.get(y).push(x)});
   check([...fibers.values()].every(xs=>xs.length<=2),"oversized fibre");
   return [...fibers.values()].filter(xs=>xs.length===2);
  });
  // Explicit 3-colour witness for full union of the constructed odd cycles.
  const three=Array(N).fill(0);
  for(const b of blocks){for(let j=0;j<b.length-1;j++)three[b.start+j]=j%2;three[b.start+b.length-1]=2}
  check(collisions.flat().every(([x,y])=>three[x]!==three[y]),"three-colour witness");
  return {N,maps,collisions,blocks};
 }
 function binaryTags(N,edges){
  const adj=Array.from({length:N},()=>[]);for(const [x,y] of edges){adj[x].push(y);adj[y].push(x)}
  const c=Array(N).fill(-1);
  for(let i=0;i<N;i++)if(c[i]<0){
   c[i]=0;const q=[i];
   for(let p=0;p<q.length;p++)for(const v of adj[q[p]]){
    if(c[v]===c[q[p]])return null;
    if(c[v]<0){c[v]=1-c[q[p]];q.push(v)}
   }
  }return c;
 }
 function direct(f,c){
  const seen=new Set();for(let x=0;x<f.length;x++){
   const key=2*f[x]+c[x];check(!seen.has(key),"actual decoder collision");seen.add(key);stats.decoderInputs++;
  }
 }
 function census(n,edges,enumerateColours=false){
  const model=construct(n,edges), size=2**n, full=size-1, safe=[];
  stats.families++;
  for(let s=0;s<size;s++){
   const ids=bits(n,s);
   const tags=binaryTags(model.N,ids.flatMap(i=>model.collisions[i]));
   const bad=edges.find(e=>(s&e)===e);
   check((tags!==null)===(bad===undefined),"subset theorem");safe[s]=tags!==null;stats.subsetChecks++;
   if(tags)for(const i of ids)direct(model.maps[i],tags);
   else{
    const b=model.blocks.find(b=>b.e===bad);
    check(b.length%2===1&&b.labels.every(i=>s>>i&1),"odd-cycle certificate");
    for(let j=0;j<b.length;j++){
     const x=b.start+j,y=b.start+(j+1)%b.length,f=model.maps[b.labels[j]];
     check(f[x]===f[y],"certificate is not actual collision");
    }stats.cycleCertificates++;
   }
  }
  // Exact partition DP over safe whole-action subsets (not individual edges).
  const min=Array(size).fill(n+1);min[0]=0;
  for(let s=1;s<size;s++)for(let t=s;t;t=(t-1)&s)if(safe[t])min[s]=Math.min(min[s],1+min[s^t]);
  if(enumerateColours){
   for(let k=1;k<=3;k++){
    let possible=false;
    for(let i=0;i<k**n;i++){
     let v=i;const classes=Array(k).fill(0);
     for(let j=0;j<n;j++){classes[v%k]|=1<<j;v=Math.floor(v/k)}
     if(classes.every(s=>safe[s]))possible=true;
     stats.colourAssignments++;
    }
    check(possible===(min[full]<=k),"partition DP versus assignment oracle");
   }
  }
  return {min,safe};
 }
 for(let n=3;n<=5;n++){
  const triples=subsets(n,3);
  for(let f=0;f<2**triples.length;f++)census(n,triples.filter((_,i)=>f>>i&1),true);
 }
 // Mixed parity edge lengths: every subset of the 4- and 5-edge families on five actions.
 const mixed=[...subsets(5,4),...subsets(5,5)];
 for(let f=0;f<2**mixed.length;f++)census(5,mixed.filter((_,i)=>f>>i&1),true);
 const fano=[7,25,97,42,82,76,52]; // lines: 012,034,056,135,146,236,245
 const F=census(7,fano,true);
 check(F.min[127]===3,"Fano needs three hints");
 for(let i=0;i<7;i++)check(F.min[127^(1<<i)]===2,"Fano deletion");
 for(let n=3;n<=8;n++)for(let t=2;t<n;t++){
  const C=census(n,subsets(n,t+1),false);
  check(C.min[2**n-1]===Math.ceil(n/t),"uniform hint count");
  for(let k=1;k<=n;k++){
   const cap=Math.min(n,k*t);
   const admitted=Array.from({length:2**n},(_,i)=>i).filter(i=>C.min[i]<=k);
   check(Math.max(...admitted.map(pop))===cap,"uniform coverage upper bound");
   const seeds=subsets(n,cap);
   for(let j=0;j<n;j++){
    const hits=seeds.filter(s=>s>>j&1).length;
    check(hits*n===seeds.length*cap,"seeded worst-action coverage");
    stats.seededActionChecks++;
   }stats.admissionBudgets++;
  }
 }
 let refused=0;for(const [n,edges] of [[0,[]],[4,[3]],[3,[8]],[4,[7,7]],[9,[]]]){try{construct(n,edges)}catch(e){refused++}}
 check(refused===5,"malformed input acceptance");
 return {...stats,malformedRefusals:refused};
}
console.log(JSON.stringify(laboratory(),null,2));
