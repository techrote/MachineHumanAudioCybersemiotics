"use strict";
// Synthetic experiment. Node.js 18+, no dependencies.
function laboratory(){
  "use strict";
  const assert=(condition,message)=>{if(!condition)throw new Error(message)};
  const matrix=n=>Array.from({length:n+1},()=>Array(n+1).fill(0));
  const sum=a=>a.reduce((x,y)=>x+y,0);
  function prefix(W){
    const n=W.length-1,F=matrix(n);
    for(let i=1;i<=n;i++)for(let j=1;j<=n;j++)F[i][j]=W[i][j]+F[i-1][j]+F[i][j-1]-F[i-1][j-1];
    return F;
  }
  function inverse(F){
    const n=F.length-1,W=matrix(n);
    for(let i=1;i<=n;i++)for(let j=1;j<=n;j++)W[i][j]=F[i][j]-F[i-1][j]-F[i][j-1]+F[i-1][j-1];
    return W;
  }
  const major=F=>JSON.stringify([F.map(row=>row.at(-1)),F.at(-1)]);
  const dot=(W,widths)=>sum(widths.map((v,i)=>sum(W[i+1].slice(1,v+1))));
  function simulate(W,history){
    const n=W.length-1,S=matrix(n);const out=[];
    for(const t of history){
      for(let i=1;i<=n;i++)for(let j=1;j<=i;j++){
        if(t>=i)S[i][j]=1;else if(t<j)S[i][j]=0;
      }
      out.push(sum(W.map((row,i)=>sum(row.map((v,j)=>v*S[i][j])))));
    }
    return out;
  }
  function rectangles(widths){
    const corners=[];
    for(let i=0;i<widths.length;i++)if(widths[i]>0&&(i===widths.length-1||widths[i]>widths[i+1]))corners.push([i+1,widths[i]]);
    return corners;
  }
  function staircase(F,widths){
    let p=0,prev=0;
    for(const [u,v] of rectangles(widths)){
      p+=F[u][v]-F[prev][v];prev=u;
    }
    return p;
  }
  function reachable(n){
    const queue=[{t:0,widths:Array(n).fill(0),history:[0]}],seen=new Set(["0:"+Array(n).fill(0)]);
    for(let h=0;h<queue.length;h++){
      const {t,widths,history}=queue[h];
      for(let x=0;x<=n;x++){
        const next=widths.map((w,i)=>x>t&&i<x?n:x<t?Math.min(w,x):w);
        const key=x+":"+next;
        if(!seen.has(key)){seen.add(key);queue.push({t:x,widths:next,history:[...history,x]})}
      }
    }
    return queue;
  }
  function* compositions(total,k,arr=[]){
    if(k===1){yield [...arr,total];return;}
    for(let v=0;v<=total;v++)yield* compositions(total-v,k-1,[...arr,v]);
  }
  function maxDiff(A,B){
    let d=0;for(let i=0;i<A.length;i++)for(let j=0;j<A.length;j++)d=Math.max(d,Math.abs(A[i][j]-B[i][j]));
    return d;
  }
  function census(n,total){
    const cells=[];for(let i=1;i<=n;i++)for(let j=1;j<=i;j++)cells.push([i,j]);
    const groups=new Map(),states=reachable(n);
    let ensembles=0,firstReversals=0,historyComparisons=0,majorPairs=0,pairPathChecks=0,nontrivialMajorClasses=0,largestClass=0;
    for(const weights of compositions(total,cells.length)){
      const W=matrix(n);cells.forEach(([i,j],k)=>W[i][j]=weights[k]);const F=prefix(W);
      assert(JSON.stringify(inverse(F))===JSON.stringify(W),"mixed difference inverse");
      const reconstructed=matrix(n);
      for(let u=1;u<=n;u++)for(let v=1;v<=n;v++){
        if(v>=u)reconstructed[u][v]=F[u][n];
        else if(u===n)reconstructed[u][v]=F[n][v];
        else reconstructed[u][v]=simulate(W,[0,u,v]).at(-1);
      }
      assert(JSON.stringify(inverse(reconstructed))===JSON.stringify(W),"major and minimal probes inverse");
      for(let u=0;u<=n;u++)for(let v=0;v<=u;v++){
        assert(simulate(W,[0,u,v]).at(-1)===F[u][v],"first reversal");
        firstReversals++;
      }
      const outputs=states.map(({widths,history})=>{
        const a=dot(W,widths);
        assert(a===simulate(W,history).at(-1)&&a===staircase(F,widths),"history/staircase agreement");
        historyComparisons++;return a;
      });
      const key=major(F);if(!groups.has(key))groups.set(key,[]);
      groups.get(key).push({F,outputs});ensembles++;
    }
    for(const g of groups.values()){
      largestClass=Math.max(largestClass,g.length);if(g.length>1)nontrivialMajorClasses++;
      for(let a=0;a<g.length;a++)for(let b=a+1;b<g.length;b++){
        const E=maxDiff(g[a].F,g[b].F);assert(E>0,"distinct ensembles have distinct F");
        majorPairs++;
        states.forEach(({widths},k)=>{
          const r=rectangles(widths).length,d=Math.abs(g[a].outputs[k]-g[b].outputs[k]);
          assert(d*(r+1)<=r*total,"absolute nested bound");
          assert(d<=Math.max(0,2*r-1)*E,"relative nested bound");pairPathChecks++;
        });
      }
    }
    return {n,total,ensembles,majorClasses:groups.size,nontrivialMajorClasses,largestClass,reachableStates:states.length,firstReversals,historyComparisons,majorPairs,pairPathChecks};
  }
  function witness(r){
    const m=r+1,n=2*m,A=matrix(n),B=matrix(n),history=[0];
    for(let i=1;i<m;i++)A[m+i][m-i]=1;
    A[n][m]=1;
    for(let i=1;i<=m;i++)B[m+i][m+1-i]=1;
    for(let i=1;i<=r;i++)history.push(m+m-i,i);
    const F=prefix(A),G=prefix(B),a=simulate(A,history),b=simulate(B,history);
    assert(major(F)===major(G),"witness major");
    assert(maxDiff(F,G)===1,"witness FORC discrepancy");
    assert(a.at(-1)===r&&b.at(-1)===0,"witness nested discrepancy");
    return {m,r,n,A,B,history,a,b};
  }
  function ratioWitness(r){
    const m=r+1,n=2*m,H=matrix(n);
    for(let i=1;i<=r;i++){
      H[m+m-i][i]=1;
      if(i<r)H[m+m-i-1][i]=-1;
    }
    const D=inverse(H),A=matrix(n),B=matrix(n);
    for(let i=1;i<=n;i++)for(let j=1;j<=n;j++){
      assert(j<=i||D[i][j]===0,"support");
      A[i][j]=Math.max(D[i][j],0);B[i][j]=Math.max(-D[i][j],0);
    }
    const F=prefix(A),G=prefix(B),history=witness(r).history;
    const total=F[n][n],d=simulate(A,history).at(-1)-simulate(B,history).at(-1);
    assert(major(F)===major(G)&&maxDiff(F,G)===1,"ratio witness");
    assert(d===2*r-1,"sharp amplification");
    return {r,total,firstReversalDifferenceNumerator:1,nestedDifferenceNumerator:d};
  }
  function wav(values,total){
    const rate=8000,slot=640,pcm=new Uint8Array(44+2*slot*values.length),dv=new DataView(pcm.buffer);
    const str=(o,s)=>[...s].forEach((c,i)=>pcm[o+i]=c.charCodeAt(0));
    str(0,"RIFF");dv.setUint32(4,pcm.length-8,true);str(8,"WAVE");str(12,"fmt ");
    dv.setUint32(16,16,true);dv.setUint16(20,1,true);dv.setUint16(22,1,true);
    dv.setUint32(24,rate,true);dv.setUint32(28,rate*2,true);dv.setUint16(32,2,true);
    dv.setUint16(34,16,true);str(36,"data");dv.setUint32(40,pcm.length-44,true);
    for(let i=0;i<values.length;i++)for(let k=0;k<slot;k++){
      const tri=16-2*Math.abs((k%32)-16),env=Math.min(k,slot-1-k,32);
      const y=Math.round(12000*values[i]*tri*env/(total*16*32));
      dv.setInt16(44+2*(i*slot+k),y,true);
    }
    return pcm;
  }
  const fnv=bytes=>{let h=2166136261;for(const b of bytes)h=Math.imul(h^b,16777619)>>>0;return h.toString(16).padStart(8,"0")};
  const cases=[2,3,4].map(n=>census(n,4));
  const witnesses=[],amplification=[];
  for(const r of [1,2,3,4,5,8,15,31,63]){
    const w=witness(r);witnesses.push({r,total:w.m,firstReversalDifferenceNumerator:1,nestedDifferenceNumerator:r});amplification.push(ratioWitness(r));
  }
  const w=witness(7),majorPath=[...Array.from({length:w.n+1},(_,i)=>i),...Array.from({length:w.n},(_,i)=>w.n-1-i)];
  const files={"major-a.wav":wav(simulate(w.A,majorPath),w.m),"major-b.wav":wav(simulate(w.B,majorPath),w.m),"nested-a.wav":wav(w.a,w.m),"nested-b.wav":wav(w.b,w.m)};
  assert(files["major-a.wav"].every((x,i)=>x===files["major-b.wav"][i]),"major PCM collision");
  assert(files["nested-a.wav"].some((x,i)=>x!==files["nested-b.wav"][i]),"nested PCM separation");
  const receipt={model:"synthetic finite nonnegative relay weights; no human data",cases,witnesses,amplification,audio:Object.fromEntries(Object.entries(files).map(([k,v])=>[k,{bytes:v.length,fnv1a32:fnv(v)}])),audioNestedPath:w.history,audioNestedOutputs:{A:w.a,B:w.b},assertions:"pass"};
  return {receipt,files};
}

module.exports = {laboratory};
if (require.main === module) {
  const fs=require("node:fs"), path=require("node:path");
  const {receipt,files}=laboratory();
  const dest=process.argv[2];
  if(dest){fs.mkdirSync(dest,{recursive:true});for(const [name,bytes] of Object.entries(files))fs.writeFileSync(path.join(dest,name),bytes);}
  process.stdout.write(JSON.stringify(receipt,null,2)+"\n");
}
