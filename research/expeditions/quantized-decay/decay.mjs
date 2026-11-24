function insist(b,m){if(!b)throw Error(m)}

function energy(s){return s[0]*s[0]+s[1]*s[1]}

function nearest(n,q){return Math.sign(n)*Math.floor((2*Math.abs(n)+q)/(2*q))||0}

function trunc(n,q){return Math.trunc(n/q)||0}

function transform(s,a,b,q,mode){const round=mode==="N"?nearest:trunc;return [round(a*s[0]-b*s[1],q),round(b*s[0]+a*s[1],q)]}

function model(a,b,q){
  insist([a,b,q].every(Number.isSafeInteger)&&q>=2&&q<=16&&a*a+b*b<q*q,"unsupported coefficients");
  const delta=q*q-a*a-b*b,R=Math.ceil(3*q*q/(2*delta));
  insist(R<=250,"disk budget exceeded");
  const states=[],ids=new Map(),key=s=>s.join(",");
  for(let x=-R;x<=R;x++)for(let y=-R;y<=R;y++)if(x*x+y*y<=R*R){ids.set(key([x,y]),states.length);states.push([x,y])}
  const N=states.map(s=>ids.get(key(transform(s,a,b,q,"N")))),T=states.map(s=>ids.get(key(transform(s,a,b,q,"T")))),E=states.map(energy),zero=ids.get("0,0");
  for(let i=0;i<states.length;i++){insist(N[i]!==undefined&&T[i]!==undefined,"disk closure");insist(i===zero||E[T[i]]<E[i],"trunc descent")}
  return {a,b,q,R,states,N,T,E,zero}
}

function solve(m){
  const {states,N,T,E,zero}=m,n=states.length,W=n+1,rev=Array.from({length:n},()=>[]);
  for(let i=0;i<n;i++){rev[N[i]].push([i,1]);if(N[i]!==T[i])rev[T[i]].push([i,W+1])}
  const d=Array(n).fill(Infinity),heap=[];
  function push(v){let i=heap.length;heap.push(v);while(i){let p=(i-1)>>1;if(heap[p][0]<=v[0])break;heap[i]=heap[p];i=p}heap[i]=v}
  function pop(){const v=heap[0],tail=heap.pop();if(heap.length){let i=0;while(2*i+1<heap.length){let j=2*i+1;if(j+1<heap.length&&heap[j+1][0]<heap[j][0])j++;if(heap[j][0]>=tail[0])break;heap[i]=heap[j];i=j}heap[i]=tail}return v}
  d[zero]=0;push([0,zero]);
  while(heap.length){const [dist,i]=pop();if(dist!==d[i])continue;for(const [j,w] of rev[i])if(dist+w<d[j]){d[j]=dist+w;push([d[j],j])}}
  const choice=Array(n).fill("N"),guard=Array(n).fill(0),guardSteps=Array(n).fill(0),cycles=[],status=new Uint8Array(n),basin=new Int32Array(n);
  for(let i=0;i<n;i++){
    if(i!==zero){insist(d[i]===Math.min(1+d[N[i]],W+1+d[T[i]]),"Bellman certificate");choice[i]=d[i]===1+d[N[i]]?"N":"T";insist(d[i]<Infinity&&d[i]%W<n,"distance bounds")}
    if(status[i])continue;
    const path=[];let j=i;
    while(!status[j]){status[j]=1;path.push(j);j=N[j]}
    if(status[j]===1){const cycle=path.slice(path.indexOf(j));cycles.push(cycle);for(const k of cycle)basin[k]=cycles.length-1}
    for(let k=path.length-1;k>=0;k--){const u=path[k];basin[u]=basin[N[u]];status[u]=2}
  }
  for(const i of Array.from({length:n},(_,i)=>i).sort((i,j)=>E[i]-E[j])){
    if(i===zero)continue;
    const useN=E[N[i]]<E[i],next=useN?N[i]:T[i];guard[i]=guard[next]+(useN?0:1);guardSteps[i]=1+guardSteps[next];insist(d[i]<=W*guard[i]+guardSteps[i],"optimal no worse than greedy")
  }
  return {d,W,choice,guard,guardSteps,cycles,basin}
}

function trace(m,sol,i,policy){
  const {N,T,E,zero,states}=m,steps=[states[i]],actions=[],seen=new Set();
  while(i!==zero&&!seen.has(i)){seen.add(i);const c=policy==="optimal"?sol.choice[i]:policy==="greedy"?(E[N[i]]<E[i]?"N":"T"):"N";actions.push(c);i=c==="N"?N[i]:T[i];steps.push(states[i])}
  return {states:steps,actions,terminated:i===zero}
}

function independent(m,s){
  const {N,T,zero,states}=m,n=states.length;let checks=0;
  for(let i=0;i<n;i++){
    // Breadth-first on (state, exact number of interventions), independent of weighted heap.
    const k=Math.floor(s.d[i]/s.W),limit=k+1,visited=new Set([i+":0"]),queue=[[i,0,0]],best=Array(limit).fill(Infinity);
    for(let h=0;h<queue.length;h++){const [u,c,t]=queue[h];if(u===zero){best[c]=Math.min(best[c],t);continue}for(const [v,extra] of [[N[u],0],[T[u],1]]){const z=c+extra,key=v+":"+z;if(z<limit&&!visited.has(key)){visited.add(key);queue.push([v,z,t+1])}}}
    insist(best.slice(0,k).every(x=>x===Infinity)&&best[k]===s.d[i]%s.W,"independent budget BFS disagrees");checks++;
  }
  return checks
}

function census(){
 const result={range:"labelled nonnegative (a,b), 2<=q<=10, a²+b²<q²; repeated rational coefficients retained",models:0,states:0,modelsWithNonzeroCycle:0,nonzeroCycles:0,persistentBasinStates:0,periodHistogram:{},maxPeriod:0,maxInterventions:0,greedyWorseStates:0,maxGreedyExcess:0,independentChecks:0,byQ:{},examples:{}};
 for(let q=2;q<=10;q++)for(let a=0;a<q;a++)for(let b=0;b<q;b++){
   if(a*a+b*b>=q*q)continue;const m=model(a,b,q),s=solve(m),n=m.states.length;
   result.models++;result.states+=n;const row=result.byQ[q]??={models:0,states:0,persistentModels:0};row.models++;row.states+=n;
   const nonzero=s.cycles.filter(c=>!c.includes(m.zero));if(nonzero.length){result.modelsWithNonzeroCycle++;row.persistentModels++}result.nonzeroCycles+=nonzero.length;
   for(const c of nonzero){result.periodHistogram[c.length]=(result.periodHistogram[c.length]||0)+1;if(c.length>result.maxPeriod){result.maxPeriod=c.length;result.examples.longestCycle={a,b,q,R:m.R,cycle:c.map(i=>m.states[i]),optimal:trace(m,s,c[0],"optimal")}}}
   for(let i=0;i<n;i++){
     if(!s.cycles[s.basin[i]].includes(m.zero))result.persistentBasinStates++;
     const opt=Math.floor(s.d[i]/s.W),ex=s.guard[i]-opt;
     if(ex>0)result.greedyWorseStates++;
     if(ex>result.maxGreedyExcess){result.maxGreedyExcess=ex;result.examples.greedyGap={a,b,q,R:m.R,start:m.states[i],optimal:trace(m,s,i,"optimal"),greedy:trace(m,s,i,"greedy"),nominal:trace(m,s,i,"nominal"),opt,greedyCost:s.guard[i]}}
     if(opt>result.maxInterventions){result.maxInterventions=opt;result.examples.hardEscape={a,b,q,R:m.R,start:m.states[i],optimal:trace(m,s,i,"optimal"),nominal:trace(m,s,i,"nominal")}}
   }
   if(q<=4)result.independentChecks+=independent(m,s)
 }
 return result
}

export {model,solve,trace,census,transform};
