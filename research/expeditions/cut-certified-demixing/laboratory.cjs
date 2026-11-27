'use strict';
// Deterministic exact integer fixtures; no external dependencies.
function lab(){
 const assert=(v,msg)=>{if(!v)throw Error(msg)};
 const gcd=(a,b)=>b?gcd(b,a%b):a;
 const edges=(p,q,n,drop=[])=>Array.from({length:n},(_,t)=>[t%p,p+t%q,t]).filter(e=>!drop.includes(e[2]));
 // Exact cut via elimination of each right vertex independently.
 function mincut(p,q,E){
   let best=Infinity,side=[];
   const test=(S)=>{const c=E.filter(([u,v])=>S[u]!==S[v]).length;if(c<best){best=c;side=S.slice()}};
   for(let j=0;j<q;j++){let s=Array(p+q).fill(0);s[p+j]=1;test(s)}
   for(let m=1;m<(1<<p)-1;m++){
     let s=Array.from({length:p+q},(_,i)=>i<p?((m>>i)&1):0);
     let zero=Array(q).fill(0),one=zero.slice();
     for(const [u,v] of E)(s[u]?one:zero)[v-p]++;
     for(let j=0;j<q;j++)s[p+j]=one[j]>zero[j]?1:0;
     test(s);
   }
   return {value:best,side};
 }
 // Unit undirected flows, followed by decomposition into disjoint paths.
 function paths(V,E,s,t,k){
   const f=Array(E.length).fill(0),adj=Array.from({length:V},()=>[]);
   E.forEach(([a,b],i)=>{adj[a].push([b,i,1]);adj[b].push([a,i,-1])});
   function bfs(ok){
     let pred=Array(V).fill(null),queue=[s];pred[s]=[-1,-1,0];
     for(let j=0;j<queue.length&&!pred[t];j++){
       const u=queue[j];for(const [v,i,dir] of adj[u])if(!pred[v]&&ok(i,dir)){
         pred[v]=[u,i,dir];queue.push(v);
       }
     }
     if(!pred[t])return null;
     let out=[];for(let v=t;v!==s;){const [u,i,dir]=pred[v];out.push([i,dir]);v=u}
     return out.reverse();
   }
   for(let j=0;j<k;j++){const a=bfs((i,dir)=>f[i]*dir<1);if(!a)return null;for(const [i,dir] of a)f[i]+=dir}
   let out=[];for(let j=0;j<k;j++){const a=bfs((i,dir)=>f[i]*dir>0);assert(a,"flow decomposition");for(const [i,dir] of a)f[i]-=dir;out.push(a)}
   return out;
 }
 function decode(V,E,Y,e){
   let result=[0],maxPath=0;
   for(let t=1;t<V;t++){
     const ps=paths(V,E,0,t,2*e+1);if(!ps)return null;
     const used=new Set();for(const path of ps){maxPath=Math.max(maxPath,path.length);for(const [i] of path){assert(!used.has(i),"disjoint");used.add(i)}}
     const values=ps.map(path=>-path.reduce((a,[i,dir])=>a+dir*Y[i],0)).sort((a,b)=>a-b);
     result.push(values[e]);
   }
   return {result,maxPath};
 }
 const pred=(p,q,n)=>n<p+q-1?0:Math.max(1,Math.floor(n/q));
 let profiles=0,flowChecks=0,coarea=0,sharp=0,decodes=0,noisy=0,weighted=0;
 let deadlines={};
 for(let p=3;p<=11;p++)for(let q=p+1;q<=19;q++)if(gcd(p,q)===1){
   for(let d=1;d<=2*p+2;d++){
     const n=d===1?p+q-1:d*q;
     for(const N of [n-1,n,n+1]){
       const E=edges(p,q,N),c=mincut(p,q,E);
       assert(c.value===pred(p,q,N),`prefix ${p} ${q} ${N} ${c.value}`);
       profiles++;
       // Independently verify a unit-flow lower bound and one cut upper bound.
       if(p<=7&&q<=11&&d<=6&&N===n){
         for(let t=1;t<p+q;t++){assert(paths(p+q,E,0,t,d),"flow lower");flowChecks++}
         assert(!paths(p+q,E,c.side[0]?c.side.indexOf(1):c.side.indexOf(0),c.side[0]?c.side.indexOf(0):c.side.indexOf(1),d+1),"flow upper");flowChecks++;
       }
     }
   }
 }
 for(const [p,q] of [[3,5],[5,7],[7,11],[11,17]]){
   deadlines[`${p},${q}`]=Array.from({length:5},(_,e)=>({errors:e,n:e===0?p+q-1:(2*e+1)*q}));
 }
 // Deterministic PRNG and exact integer arithmetic.
 let state=754; const rand=n=>{state=(Math.imul(1664525,state)+1013904223)>>>0;return state%n};
 for(const [p,q] of [[3,5],[5,7],[7,11]]){
   for(let e=0;e<=3;e++)for(let f=0;f<=3;f++){
     const d=2*e+f+1,n=d===1?p+q-1:d*q;
     const E0=edges(p,q,n),C=mincut(p,q,E0);
     assert(C.value===d,"deadline");
     // Sharp ambiguity at preceding prefix with f erasures and e errors each.
     const old=edges(p,q,n-1),cut=mincut(p,q,old),h=cut.side;
     const diff=old.map(([u,v])=>h[u]-h[v]);
     const discrep=diff.map((x,i)=>x?i:-1).filter(i=>i>=0);
     assert(discrep.length===d-1,"one short cut");
     const erased=new Set(discrep.slice(0,f)), remaining=discrep.filter(i=>!erased.has(i));
     const Y=diff.map((v,i)=>remaining.slice(0,e).includes(i)?v:0);
     assert(Y.filter((v,i)=>!erased.has(i)&&v!==0).length<=e,"ball zero");
     assert(Y.filter((v,i)=>!erased.has(i)&&v!==diff[i]).length<=e,"ball cut");sharp++;
     for(let trial=0;trial<20;trial++){
       let order=Array.from({length:n},(_,i)=>i);for(let j=n-1;j>0;j--){let i=rand(j+1);[order[i],order[j]]=[order[j],order[i]]}
       const E=edges(p,q,n,order.slice(0,f)),bad=new Set(order.slice(f,f+e)),V=p+q;
       let theta=Array.from({length:V},()=>rand(101)-50);theta=theta.map(v=>v-theta[0]);
       const clean=E.map(([u,v])=>theta[u]-theta[v]);
       const Y=clean.map((v,i)=>v+(bad.has(E[i][2])?(rand(2)?1:-1)*(1000+rand(9000)):0));
       const recovered=decode(V,E,Y,e);assert(recovered&&recovered.result.every((v,i)=>v===theta[i]),"median decode");decodes++;
       const Ynoise=Y.map((v,i)=>v+(bad.has(E[i][2])?0:rand(5)-2));
       const noisyDecode=decode(V,E,Ynoise,e);assert(noisyDecode.result.every((v,i)=>Math.abs(v-theta[i])<=2*noisyDecode.maxPath),"median bound");noisy++;
       const hh=Array.from({length:V},()=>rand(19)-9),range=Math.max(...hh)-Math.min(...hh);
       const abs=E.map(([u,v])=>Math.abs(hh[u]-hh[v]));
       const margin=abs.reduce((a,v,i)=>a+(bad.has(E[i][2])?-v:v),0);
       let layer=0;for(let k=Math.min(...hh);k<Math.max(...hh);k++)layer+=E.reduce((a,[u,v,t])=>a+((hh[u]>k)!==(hh[v]>k)?(bad.has(t)?-1:1):0),0);
       assert(margin===layer&&margin>=range,"coarea margin");coarea++;
     }
   }
 }
 // Exact weighted signed-cut criterion: minimum over all cuts vs multi-level vectors.
 for(let trial=0;trial<80;trial++){
   const p=3,q=5,V=p+q,E=edges(p,q,15),weights=E.map(()=>1+rand(5)),bad=new Set([rand(E.length),rand(E.length)]);
   let delta=Infinity,cut;
   for(let m=1;m<(1<<V)-1;m++){
     let s=Array.from({length:V},(_,i)=>(m>>i)&1);
     let c=E.reduce((a,[u,v],i)=>a+(s[u]!==s[v]?(bad.has(i)?-1:1)*weights[i]:0),0);
     if(c<delta){delta=c;cut=s}
   }
   const cm=E.reduce((a,[u,v],i)=>a+Math.abs(cut[u]-cut[v])*(bad.has(i)?-1:1)*weights[i],0);
   assert(cm===delta,"weighted witness");
   for(let j=0;j<10;j++){
     let h=Array.from({length:V},()=>rand(13)-6);
     let m=E.reduce((a,[u,v],i)=>a+Math.abs(h[u]-h[v])*(bad.has(i)?-1:1)*weights[i],0);
     assert(m>=delta*(Math.max(...h)-Math.min(...h)),"weighted coarea");weighted++;
   }
 }
 // Weighted failure and least-squares non-robustness via one contaminated sample.
 const E=edges(5,7,21),h=Array(12).fill(0);h[5]=1;
 const diff=E.map(([u,v])=>h[u]-h[v]),i=diff.findIndex(x=>x!==0);
 const Y=diff.map((v,j)=>j===i?v:0);
 const cost=(z,wt)=>Y.reduce((a,v,j)=>a+wt[j]*Math.abs(v-z[j]),0);
 const w=E.map((_,j)=>j===i?3:1),ones=E.map(()=>1);
 assert(cost(diff,w)<cost(E.map(()=>0),w)&&cost(diff,ones)>cost(E.map(()=>0),ones),"weighted failure");
 return {profiles,flowChecks,sharp,decodes,noisy,coarea,weighted,deadlines,weightedFailure:{trueWeightedCost:cost(E.map(()=>0),w),wrongWeightedCost:cost(diff,w),trueUnweightedCost:cost(E.map(()=>0),ones),wrongUnweightedCost:cost(diff,ones)},failures:0};
}
console.log(JSON.stringify(lab(),null,2));
