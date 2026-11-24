"use strict";
// Synthetic exact integer laboratory; no human or hardware data.
function run() {
  const assert=(x,msg)=>{if(!x)throw Error(msg)};
  const range=n=>Array.from({length:n},(_,i)=>i);
  const sum=x=>x.reduce((a,b)=>a+b,0);
  function distances(n,arcs){
    const d=range(n).map(i=>range(n).map(j=>i===j?0:Infinity));
    for(const [i,j,a] of arcs)d[i][j]=Math.min(d[i][j],a);
    for(const k of range(n))for(const i of range(n))for(const j of range(n))d[i][j]=Math.min(d[i][j],d[i][k]+d[k][j]);
    return d;
  }
  function transport(d,b){
    const from=[],to=[];
    b.forEach((v,i)=>{for(let k=0;k<Math.abs(v);k++)(v<0?from:to).push(i)});
    assert(from.length===to.length,"unbalanced query");
    function match(k,used){
      if(k===from.length)return 0;
      let best=Infinity;
      for(let j=0;j<to.length;j++)if(!(used&(1<<j)))best=Math.min(best,d[from[k]][to[j]]+match(k+1,used|(1<<j)));
      return best;
    }
    return match(0,0);
  }
  function vectors(n,low,high,visit,arr=[]){
    if(arr.length===n){visit(arr);return;}
    for(let v=low;v<=high;v++)vectors(n,low,high,visit,[...arr,v]);
  }
  let instances=0,worlds=0,queries=0,pairChecks=0,strictGains=0,symmetric=0,strictTransport=0,zeroNontrivial=0;
  function check(n,edges,values){
    const arcs=edges.flatMap(([i,j],k)=>[[i,j,values[2*k]],[j,i,values[2*k+1]]]);
    const rt=edges.flatMap(([i,j],k)=>[[i,j,values[2*k]+values[2*k+1]],[j,i,values[2*k]+values[2*k+1]]]);
    const d=distances(n,arcs),r=distances(n,rt);
    const isSym=edges.every((_,k)=>values[2*k]===values[2*k+1]);
    if(isSym)symmetric++;
    const feasible=[];
    function enumX(x){
      if(x.length===n){
        if(arcs.every(([i,j,a])=>x[j]-x[i]<=a))feasible.push(x);
        return;
      }
      let j=x.length;
      for(let z=-d[j][0];z<=d[0][j];z++)enumX([...x,z]);
    }
    enumX([0]);assert(feasible.length>0,"missing zero witness");
    instances++;worlds+=feasible.length;
    for(const [i,j,a] of arcs){
      let xs=feasible.map(x=>x[j]-x[i]);
      assert(Math.max(...xs)===d[i][j]&&Math.min(...xs)===-d[j][i],"pair extrema");
      if(d[i][j]<a)strictGains++;
      pairChecks++;
    }
    vectors(n,-2,2,b=>{
      if(sum(b)!==0||b.every(x=>x===0)||sum(b.filter(x=>x>0))>4)return;
      const xs=feasible.map(x=>sum(x.map((v,i)=>v*b[i])));
      const hi=transport(d,b),lo=-transport(d,b.map(x=>-x)),worst=transport(r,b);
      assert(hi===Math.max(...xs)&&lo===Math.min(...xs),"transport extrema");
      assert(hi-lo<=worst,"round trip upper bound");
      if(isSym)assert(hi-lo===worst,"symmetric attainment");
      if(hi-lo<worst)strictTransport++;
      if(hi===lo&&worst>0)zeroNontrivial++;
      queries++;
    });
  }
  vectors(6,0,2,v=>check(3,[[0,1],[1,2],[0,2]],v));
  vectors(6,0,2,v=>check(4,[[0,1],[1,2],[2,3]],v));
  let seed=396;
  for(let k=0;k<256;k++){
    const edges=[[0,1],[1,2],[2,3],[3,0]];
    if(k%2)edges.push([0,2]);
    let v=range(edges.length*2).map(()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return (seed>>>16)%4});
    if(k%4===0)for(let j=0;j<v.length;j+=2)v[j+1]=v[j];
    check(4,edges,v);
  }
  // Exact physical worlds for a three-leg route. The q_ij transcript is 3 on all arcs.
  const x=[0,1,-1],route=[[0,1],[1,2],[2,0]];
  const a=[3,3,3],b=route.map(([i,j])=>3+x[i]-x[j]);
  assert(sum(a)===sum(b)&&a.some((v,i)=>v!==b[i]),"cycle gauge");
  assert(route.every(([i,j],k)=>b[k]+x[j]-x[i]===3),"local transcript");
  // Original click score, 100 ms per delay unit, 80 ms tapered marker.
  function wav(delays){
    const rate=8000,unit=800,mark=640;
    let ticks=[0];for(const t of delays)ticks.push(ticks.at(-1)+t*unit);
    const count=ticks.at(-1)+mark;
    const bytes=new Uint8Array(44+2*count),d=new DataView(bytes.buffer);
    const str=(p,s)=>{for(let i=0;i<s.length;i++)bytes[p+i]=s.charCodeAt(i)};
    str(0,"RIFF");d.setUint32(4,bytes.length-8,true);str(8,"WAVE");str(12,"fmt ");
    d.setUint32(16,16,true);d.setUint16(20,1,true);d.setUint16(22,1,true);
    d.setUint32(24,rate,true);d.setUint32(28,rate*2,true);d.setUint16(32,2,true);d.setUint16(34,16,true);
    str(36,"data");d.setUint32(40,2*count,true);
    for(let k=0;k<ticks.length;k++)for(let i=0;i<mark;i++){
      const period=[32,24,20,32][k],env=Math.min(i,mark-1-i,80);
      const sample=(i%period<period/2?1:-1)*env*100;
      d.setInt16(44+2*(ticks[k]+i),sample,true);
    }
    return bytes;
  }
  function fp(bytes){let h=2166136261;for(const v of bytes)h=Math.imul(h^v,16777619)>>>0;return h.toString(16).padStart(8,"0")}
  const scores={"physical-a":wav(a),"physical-b":wav(b),"receipt-a":wav(a),"receipt-b":wav(a)};
  assert(scores["receipt-a"].every((x,i)=>x===scores["receipt-b"][i]),"receipt equality");
  assert(scores["physical-a"].some((x,i)=>x!==scores["physical-b"][i]),"physical contrast");
  return {receipt:{instances,worlds,queries,pairChecks,strictGains,symmetric,strictTransport,zeroNontrivial,route:{a,b,total:sum(a)},audio:Object.fromEntries(Object.entries(scores).map(([k,v])=>[k,{bytes:v.length,fnv1a:fp(v)}])),assertionFailures:0},scores};
}
if (require.main === module) {
 const {receipt,scores}=run();
 console.log(JSON.stringify(receipt,null,2));
 if(process.argv[2]){const fs=require("node:fs"),p=require("node:path");fs.mkdirSync(process.argv[2],{recursive:true});for(const [name,bytes] of Object.entries(scores))fs.writeFileSync(p.join(process.argv[2],name+".wav"),bytes);}
}
module.exports={run};
