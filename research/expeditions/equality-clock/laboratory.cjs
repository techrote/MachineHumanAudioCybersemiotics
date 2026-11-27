'use strict';
// Standalone deterministic synthetic laboratory, Node.js or V8.
function run(){
  const assert=(c,m)=>{if(!c)throw Error(m)};
  const seq=(n)=>Array.from({length:n},(_,i)=>i);
  const pairs=(k)=>seq(k).flatMap(s=>seq(k).slice(s+1).map(u=>[s,u]));
  const mask=(n,m)=>seq(n).filter(i=>(m>>i)&1);
  const sign=(v)=>Math.sign(v);
  // Weighted strict product-order chain; duplicate cells contribute multiplicity.
  function chain(a,b,d){
    const cells=new Map();
    for(let i=0;i<a.length;i++){
      let x=a[i],y=d*b[i],key=x+','+y;
      if(cells.has(key))cells.get(key).w++;else cells.set(key,{x,y,w:1});
    }
    const p=[...cells.values()].sort((a,b)=>a.x-b.x||a.y-b.y), dp=[];
    for(let i=0;i<p.length;i++){
      let best=0;
      for(let j=0;j<i;j++)if(p[j].x<p[i].x&&p[j].y<p[i].y)best=Math.max(best,dp[j]);
      dp.push(best+p[i].w);
    }
    return Math.max(0,...dp);
  }
  const longest=(a,b)=>Math.max(chain(a,b,1),chain(a,b,-1));
  function compatible(a,b,d){
    for(let i=0;i<a.length;i++)for(let j=0;j<i;j++)
      if(sign(a[i]-a[j])!==d*sign(b[i]-b[j]))return false;
    return true;
  }
  function brute(a,b){
    let best=0;
    for(let m=0;m<2**a.length;m++){
      let t=mask(a.length,m);if(t.length<=best)continue;
      let aa=t.map(i=>a[i]),bb=t.map(i=>b[i]);
      if(compatible(aa,bb,1)||compatible(aa,bb,-1))best=t.length;
    }
    return best;
  }
  const words=(x,n,k)=>seq(k).map(s=>x.slice(s,s+n));
  const profile=(x,n,k)=>pairs(k).map(([s,u])=>{const a=x.slice(s,s+n),b=x.slice(u,u+n);return [s,u,chain(a,b,1),chain(a,b,-1)]});
  const score=(x,n,k)=>Math.max(...profile(x,n,k).flatMap(p=>p.slice(2)));
  const candidates=(w,y,e)=>w.map((a,s)=>[s,longest(a.filter((_,i)=>y[i]!==null),y.filter(v=>v!==null))]).filter(([s,l])=>l>=y.filter(v=>v!==null).length-e).map(p=>p[0]);
  function bruteCandidates(w,y,e){
    return w.map((a,s)=>[s,brute(a.filter((_,i)=>y[i]!==null),y.filter(v=>v!==null))]).filter(([s,l])=>l>=y.filter(v=>v!==null).length-e).map(p=>p[0]);
  }
  // Exact floor-constrained least squares. y and g are in integer scaled units.
  // 840 is divisible by every possible block weight for N<=8.
  function floorCost(a,y,d,g){
    const groups=new Map();
    for(let i=0;i<a.length;i++){
      const key=d*a[i],z=y[i]-g*key;
      const v=groups.get(key)||{sum:0,n:0,sq:0};
      v.sum+=z;v.n++;v.sq+=z*z;groups.set(key,v);
    }
    let blocks=[],sumSq=0;
    for(const [key,v] of [...groups].sort((a,b)=>a[0]-b[0])){
      sumSq+=v.sq;blocks.push({sum:v.sum,n:v.n});
      while(blocks.length>1){
        let b=blocks[blocks.length-1],a=blocks[blocks.length-2];
        if(a.sum*b.n<=b.sum*a.n)break;
        blocks.splice(-2,2,{sum:a.sum+b.sum,n:a.n+b.n});
      }
    }
    let c=sumSq*840;
    for(const b of blocks){assert(840%b.n===0,'unsupported block size');c-=b.sum*b.sum*(840/b.n)}
    assert(Number.isSafeInteger(c)&&c>=0,'invalid exact cost');return c;
  }
  function floorCandidates(w,y,e,g,eps2times840){
    const t=seq(y.length).filter(i=>y[i]!==null),need=Math.max(0,t.length-e);
    return w.map((a,s)=>{
      let best=Infinity;
      for(let m=0;m<2**t.length;m++){
        let T=mask(t.length,m).map(i=>t[i]);if(T.length!==need)continue;
        for(const d of [1,-1])best=Math.min(best,floorCost(T.map(i=>a[i]),T.map(i=>y[i]),d,g));
      }
      return [s,best];
    }).filter(p=>p[1]<=eps2times840).map(p=>p[0]);
  }
  const tieFixtures=[
    [3,[0,0,0,1,0]], [4,[0,0,0,1,0,0]], [5,[0,0,1,0,0,2,0]],
    [6,[0,0,1,0,0,2,0,0]], [7,[1,3,3,0,2,0,0,3,1]],
    [8,[1,3,0,0,1,0,3,2,3,3]], [12,[1,5,0,4,0,2,5,4,5,5,2,3,3,0]]
  ];
  // last fixture rank compression: original [5,12,4,11,4,6,12,11,12,12,6,7,7,4].
  const distinctFixtures=[
    [3,[0,1,3,2,4]],[8,[4,8,7,1,5,6,9,2,3,0]],[9,[8,3,6,7,0,9,5,10,1,2,4]],
    [12,[6,13,2,7,3,12,1,11,8,4,9,10,0,5]],
    [16,[7,0,6,10,3,9,17,4,12,11,13,16,2,5,8,1,14,15]],
    [25,[21,9,0,3,12,13,26,6,14,8,7,25,11,2,1,22,15,20,4,24,17,23,18,5,10,19,16]]
  ];
  let checkedMasks=0;
  const fixtures=[...tieFixtures.map(([n,x])=>({type:'ties',n,x})),...distinctFixtures.map(([n,x])=>({type:'distinct',n,x}))].map(o=>{
    const p=profile(o.x,o.n,3),L=Math.max(...p.flatMap(v=>v.slice(2)));
    if(o.n<=12)for(const [s,u,i,j] of p){assert(brute(o.x.slice(s,s+o.n),o.x.slice(u,u+o.n))===Math.max(i,j),'mask vs chain');checkedMasks+=2**o.n;}
    if(o.type==='ties'&&o.n<=8)assert(L===2,'three-survivor tie fixture');
    if(o.type==='ties'&&o.n===12)assert(L===3,'four-survivor tie fixture');
    return {...o,L,distance:o.n-L,maxEffectiveFaults:o.n-L-1,pairs:p};
  });
  function eachPerm(a,k,f){
    if(k===a.length){f(a);return}
    for(let j=k;j<a.length;j++){[a[k],a[j]]=[a[j],a[k]];eachPerm(a,k+1,f);[a[k],a[j]]=[a[j],a[k]]}
  }
  // Separate fast strict LIS for exhaustive distinct-rank pilots.
  function lis(v){
    let tails=[];
    for(let x of v){let l=0,h=tails.length;while(l<h){let m=(l+h)>>1;if(tails[m]<x)l=m+1;else h=m}tails[l]=x}
    return tails.length;
  }
  function distinctScore(x,n,k){
    let order=seq(k).map(s=>seq(n).sort((i,j)=>x[i+s]-x[j+s]));
    return Math.max(...pairs(k).map(([s,u])=>{const b=order[s].map(i=>x[i+u]);return Math.max(lis(b),lis(b.map(v=>-v)))}));
  }
  let exhaustive=[];
  for(let n=3;n<=7;n++){
    let best=n,w=null,counts={},count=0;
    eachPerm(seq(n+2),0,x=>{if(x[0]>x[x.length-1])return;let l=distinctScore(x,n,3);counts[l]=(counts[l]||0)+1;count++;if(l<best||w===null){best=l;w=x.slice()}});
    assert(best===(n===3?2:3),'finite optimum');
    exhaustive.push({n,count,best,w,counts});
  }
  // Independent arbitrary four-tick phase orders: canonicalize first to identity.
  let permitted=[];
  eachPerm(seq(4),0,p=>{if(p[0]<p[3]&&longest(seq(4),p)<=2)permitted.push(p.slice())});
  assert(permitted.length===2&&longest(...permitted)>=3,'four-tick triple impossibility');
  // Exact random-existence bound, q smallest satisfying K(K-1) binomial(N,q) < q!
  const combin=(n,q)=>{let v=1n;for(let i=1;i<=q;i++)v=v*BigInt(n-i+1)/BigInt(i);return v};
  const fact=q=>seq(q).reduce((a,i)=>a*BigInt(i+1),1n);
  let existence=[];
  for(let n of [100,1000,10000])for(let k of [3,8]){
    let q=2;while(q<=n&&BigInt(k*(k-1))*combin(n,q)>=fact(q))q++;
    existence.push({n,k,q,Lupper:Math.min(n,2*q-2),Llower:Math.ceil(Math.sqrt(n))});
  }
  let seed=0x4192cafe;
  function rng(m){seed=(Math.imul(1664525,seed)+1013904223)>>>0;return seed%m}
  function shuffled(n){let a=seq(n);for(let i=n-1;i>0;i--){let j=rng(i+1);[a[i],a[j]]=[a[j],a[i]]}return a}
  const w=words(tieFixtures[5][1],8,3);
  let randomChecks=0,strictDecodes=0,floorDecodes=0;
  for(let i=0;i<600;i++){
    let n=1+rng(8),a=seq(n).map(()=>rng(5)),b=seq(n).map(()=>rng(5));
    assert(longest(a,b)===brute(a,b),'random chain vs mask');randomChecks++;
    let s=i%3,dir=(i%2===0?1:-1),map=[-12,-3,9,23].map(v=>v*dir+2),y=w[s].map(v=>map[v]);
    let order=shuffled(8),e=i%3,f=5-2*e;
    for(let j=0;j<f;j++)y[order[j]]=null;
    for(let j=f;j<f+e;j++)y[order[j]]=rng(71)-35;
    let c=candidates(w,y,e);
    assert(JSON.stringify(c)===JSON.stringify(bruteCandidates(w,y,e)),'candidate list oracle');
    assert(c.length===1&&c[0]===s,'strict ordinal decode');strictDecodes++;
    // floor-constrained channel: g=4 in integer quarter units. One clean noise
    // coordinate of +/-1 has physical L2 norm 1/4, below exact 1/sqrt(8).
    const noised=w[s].map(v=>map[v]);
    for(let j=0;j<f;j++)noised[order[j]]=null;
    for(let j=f;j<f+e;j++)noised[order[j]]=rng(71)-35;
    noised[order[f+e]]+=dir;
    let fc=floorCandidates(w,noised,e,4,840);
    assert(fc.length===1&&fc[0]===s,'strict floor decode');floorDecodes++;
  }
  // Boundary witness: e=2,f=1, shared triple 0,2,3. Quarter units.
  const clean0=w[0].map(v=>[0,16,20,24][v]),clean1=w[1].map(v=>[-2,2,6,16][v]);
  const T=[0,2,3],erased=1,C0=[4,5],C1=[6,7];
  const y=seq(8).map(i=>i===erased?null:T.includes(i)?(clean0[i]+clean1[i])/2:C0.includes(i)?clean1[i]:clean0[i]);
  const SSE=(a,T)=>T.reduce((s,i)=>s+(a[i]-y[i])**2,0);
  assert(SSE(clean0,T)===2&&SSE(clean1,T)===2,'midpoint energy');
  let at=floorCandidates(w,y,2,4,2*840),below=floorCandidates(w,y,2,4,2*840-1);
  assert(at.includes(0)&&at.includes(1)&&below.length<=1,'boundary ambiguity');
  // Show artificial jitter of tied pilot removes its exact three-survivor contract.
  const jittered=tieFixtures[5][1].map((v,i)=>v*100+i);
  assert(score(jittered,8,3)>=3,'tie-breaking cost');
  return {status:'pass',fixtures,checkedMaskBudget:checkedMasks,exhaustive,arbitraryFourTickPermitted:permitted,existence,randomChecks,strictDecodes,floorDecodes,boundary:{T,erased,C0,C1,clean0,clean1,y,at,below,squaredNoise:'1/8',unit:'rank units; integer arrays scaled by 4'},jittered:{x:jittered,L:score(jittered,8,3)}};
}
console.log(JSON.stringify(run(),null,2));
