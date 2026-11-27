'use strict';
// MHAC #801: dependency-free exact combinatorial certificates.
function laboratory(){
  const assert=(b,m)=>{if(!b)throw Error(m)};
  const sum=a=>a.reduce((x,y)=>x+y,0);
  const range=n=>Array.from({length:n},(_,i)=>i);
  const matrix=q=>range(q).map(()=>range(q).map(()=>0));
  function chain(w){
    const q=w.length,r=w[0].length;
    function inc(reverse){const d=range(q+1).map(()=>range(r+1).map(()=>0));for(let i=1;i<=q;i++)for(let j=1;j<=r;j++)d[i][j]=Math.max(d[i-1][j],d[i][j-1],d[i-1][j-1]+w[i-1][reverse?r-j:j-1]);return d[q][r]}
    return Math.max(inc(false),inc(true));
  }
  function histogram(x,N,s,u,q){let w=matrix(q);for(let t=0;t<N;t++)w[x[t+s]][x[t+u]]++;return w}
  function cyclic(x,K,q){const z=x.concat(range(K-1).map(i=>x[i%x.length]));return profile(z,x.length,K,q)}
  function profile(x,N,K,q){let L=0,pairs=[];for(let s=0;s<K;s++)for(let u=s+1;u<K;u++){const w=histogram(x,N,s,u,q),l=chain(w);L=Math.max(L,l);pairs.push({s,u,L:l,matrix:w})}return {N,K,L,d:N-L,pairs}}
  function cover(q){let c=[];for(let k=-(q-2);k<=q-2;k++)c.push(range(q).map(i=>[i,i+k]).filter(([i,j])=>j>=0&&j<q));c.push([[0,q-1],[q-1,0]]);return c}
  function euler(edges){
    const out=new Map(), degree=new Map();
    for(const [a,b,v] of edges){if(!out.has(a))out.set(a,[]);out.get(a).push([b,v]);degree.set(a,(degree.get(a)||0)+1);degree.set(b,(degree.get(b)||0)-1)}
    assert([...degree.values()].every(v=>v===0),"balance");
    const stack=[[edges[0][0],null]], back=[];
    while(stack.length){let [a,v]=stack[stack.length-1],e=out.get(a);if(e&&e.length)stack.push(e.pop());else{stack.pop();if(v!==null)back.push(v)}}
    assert(back.length===edges.length,"disconnected Euler graph");
    return back.reverse()
  }
  function words(K,J){let arr=[];for(let n=0;n<3**K;n++){let x=range(K).map(i=>Math.floor(n/3**i)%3);if(x.filter(v=>v===1).length===J)arr.push(x)}return arr}
  const fractions=[];
  for(let K=2;K<=100;K++){
    let H=K*(K-1), ab=range(K+1).map(j=>({j,A:(K-j)*(K-j-1)/2+j*(j-1),B:j*(K-j)}));
    let numerator,denominator,mixture;
    if(K<=4){numerator=1;denominator=4;mixture=[[0,4-K],[1,K]].filter(x=>x[1]);assert(ab.every(v=>2*(v.A+v.B)>=H),"quarter lower");assert(4*sum(mixture.map(([j,w])=>w*ab[j].A))===4*H&&4*sum(mixture.map(([j,w])=>w*ab[j].B))===4*H,"quarter upper")}
    else if(K===5){numerator=4;denominator=15;mixture=[[1,1],[2,2]];assert(ab.every(v=>2*v.A+v.B>=16),"five lower");assert(sum(mixture.map(([j,w])=>w*ab[j].A))===16&&sum(mixture.map(([j,w])=>w*ab[j].B))===16,"five upper")}
    else{let j=Math.floor((K+1)/3);numerator=ab[j].A;denominator=H;mixture=[[j,1]];assert(ab.every(v=>v.A>=numerator)&&ab[j].B<=numerator,"large K certificate")}
    fractions.push({K,numerator,denominator,mixture})
  }
  const pairwise=[];
  for(let q=2;q<=32;q++){
    const c=cover(q), seen=new Set();assert(c.length===2*q-2,"cover length");
    for(const ch of c){assert(ch.every(([a,b],i)=>!i||a>ch[i-1][0]),"row");assert(ch.every(([a,b],i)=>!i||b>ch[i-1][1])||ch.every(([a,b],i)=>!i||b<ch[i-1][1]),"column");for(const [a,b] of ch){let k=a*q+b;assert(!seen.has(k),"overlap");seen.add(k)}}
    assert(seen.size===q*q,"cover total");
    let edges=[];for(let a=0;a<q;a++)for(let b=0;b<q;b++)if(a===0||b===0||a===q-1||b===q-1)edges.push([a,b,a]);
    let x=euler(edges),p=cyclic(x,2,q);assert(x.length===4*q-4&&p.L===2,"perimeter cycle");
    pairwise.push({q,N:p.N,L:p.L,cycle:x})
  }
  const small=cyclic([1,0,0,2,1,2,2,0],4,3);
  assert(small.pairs.every(p=>p.L===2&&p.matrix.flat().every((v,i)=>v===(i===4?0:1))),"four-phase cycle");
  const edges5=[];
  for(let j of [1,2])for(const x of words(5,j))for(let n=0;n<j;n++)edges5.push([x.slice(0,-1).join(""),x.slice(1).join(""),x[0]]);
  const x5=euler(edges5), five=cyclic(x5,5,3);
  assert(five.N===240&&five.L===64&&five.pairs.every(p=>p.L===64),"five-phase Euler");
  const tripleCounts={};for(let t=0;t<x5.length;t++){let k=range(5).map(i=>x5[(t+i)%x5.length]).join("");tripleCounts[k]=(tripleCounts[k]||0)+1}
  assert(Object.keys(tripleCounts).length===160,"distinct five-tuples");
  for(const [w,c] of Object.entries(tripleCounts))assert(c===[...w].filter(x=>x==="1").length,"multiplicity");
  const asymptotic=[];
  for(let K=6;K<=8;K++){
    const j=Math.floor((K+1)/3), ws=words(K,j), bound=fractions[K-2];
    for(const repeats of [1,4,16]){
      const x=ws.flatMap(w=>range(repeats).flatMap(()=>w)), p=cyclic(x,K,3);
      assert(p.L*bound.denominator>=p.N*bound.numerator,"finite lower");
      assert(p.L*bound.denominator<=p.N*bound.numerator+ws.length*(K-1)*bound.denominator,"boundary upper");
      asymptotic.push({K,j,repeats,blocks:ws.length,N:p.N,L:p.L,d:p.d,boundaryAllowance:ws.length*(K-1)})
    }
  }
  // Independent brute mask oracle for strict order, including ties.
  function brute(a,b){let best=0;for(let m=0;m<2**a.length;m++){let ids=range(a.length).filter(i=>m&(1<<i));if(ids.length<=best)continue;for(const sign of [1,-1])if(ids.every(i=>ids.every(j=>Math.sign(a[i]-a[j])===sign*Math.sign(b[i]-b[j])))){best=ids.length;break}}return best}
  let state=20261127;function rnd(n){state=(Math.imul(1664525,state)+1013904223)>>>0;return Math.floor(state/4294967296*n)}
  let oracleChecks=0;for(let rep=0;rep<300;rep++){let q=2+rnd(5),N=3+rnd(7),x=range(N).map(()=>rnd(q)),y=range(N).map(()=>rnd(q)),w=matrix(q);for(let i=0;i<N;i++)w[x[i]][y[i]]++;assert(chain(w)===brute(x,y),"mask oracle");oracleChecks++}
  // Actual candidate lists under adversarial sparse errors, unknown monotone polarity.
  function decode(x,N,K,obs,e){const vals=[...new Set(obs.filter(v=>v!==null))].sort((a,b)=>a-b),r=vals.length;let result=[];for(let s=0;s<K;s++){let w=range(3).map(()=>range(r).map(()=>0));for(let t=0;t<N;t++)if(obs[t]!==null)w[x[(s+t)%x.length]][vals.indexOf(obs[t])]++;if(chain(w)>=obs.filter(v=>v!==null).length-e)result.push(s)}return result}
  let decodes=0;for(const [x,K,N,e,f] of [[[1,0,0,2,1,2,2,0],4,8,2,1],[x5,5,240,80,15]])for(let rep=0;rep<60;rep++){let s=rnd(K),sign=rnd(2)?1:-1,levels=[rnd(20),30+rnd(20),60+rnd(20)].map(v=>sign*v+100),obs=range(N).map(t=>levels[x[(s+t)%x.length]]),indices=range(N);for(let i=indices.length-1;i>0;i--){let j=rnd(i+1);[indices[i],indices[j]]=[indices[j],indices[i]]}for(let i=0;i<f;i++)obs[indices[i]]=null;for(let i=f;i<f+e;i++)obs[indices[i]]=1000+rnd(50);let got=decode(x,N,K,obs,e);assert(got.length===1&&got[0]===s,"candidate list");decodes++}
  // Six-phase finite nonattainment: equality forces exactly two middle symbols per window.
  let sixObstructions=0;
  for(let i=0;i<6;i++)for(let j=i+1;j<6;j++){
    const z=range(6).map(k=>k===i||k===j?1:0);
    const d=range(5).map(k=>k+1).find(d=>z.every((v,t)=>!(v&&z[(t+d)%6])));
    assert(d!==undefined,"disjoint rotation");
    for(let N=1;N<=60;N++){
      let counts=range(6).map(s=>sum(range(N).map(t=>z[(s+t)%6])));
      assert(sum(counts)===2*N,"occupancy total");
      const exclusive=range(6).map(s=>counts[s]+counts[(s+d)%6]);
      assert(3*Math.max(...exclusive)>=2*N,"six-phase finite obstruction");
      sixObstructions++;
    }
  }
  return {sixObstructions,schema:"mhac-801-execution-v1",fractions,pairwise,four:{cycle:[1,0,0,2,1,2,2,0],...small},five:{cycle:x5,...five,distinctWindows:Object.keys(tripleCounts).length},asymptotic,oracleChecks,decodes,assertionFailures:0}
}
console.log(JSON.stringify(laboratory(),null,2));
