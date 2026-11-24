// MHAC #292: independent forward/inverse exact census; floating log summaries only.
function laboratory(maxN=8) {
  const check=(b,s)=>{if(!b)throw Error(s)};
  function* perms(a) {
    if(a.length===0){yield [];return;}
    for(let j=0;j<a.length;j++)for(const rest of perms(a.filter((_,i)=>i!==j)))yield [a[j],...rest];
  }
  const seq=n=>Array.from({length:n},(_,i)=>i+1);
  const key=p=>p.join(",");
  const standard=p=>p.map(x=>1+p.filter(y=>y<x).length);
  const del=(p,j)=>p.filter((_,i)=>i!==j).map(x=>x-(x>p[j]?1:0));
  const insert=(q,j,k)=>{const p=q.map(x=>x+(x>=k?1:0));p.splice(j,0,k);return p;};
  const runs=p=>{let a=[],k=1;for(let i=1;i<p.length;i++){if(Math.abs(p[i]-p[i-1])===1)k++;else{a.push(k);k=1;}}a.push(k);return a;};
  const fact=n=>{let a=1;for(let j=2;j<=n;j++)a*=j;return a};
  const near=(a,b)=>Math.abs(a-b)<1e-9;
  let table=[], totals={parents:0,observations:0,forwardEvents:0,inverseEvents:0,fibers:0};
  for(let n=2;n<=maxN;n++){
    const map=new Map(),longestHist={}, multiplicityHist={};
    let entropySum=0, maxSum=0, runCounts=Array(n+1).fill(0);
    for(const p of perms(seq(n))){
      totals.parents++;
      const local=new Map();
      for(const l of runs(p))runCounts[l]++;
      for(let j=0;j<n;j++){
        const q=standard(p.filter((_,i)=>i!==j));
        check(key(q)===key(del(p,j)),"decrement vs standardization");
        const qk=key(q), pk=key(p);
        if(!map.has(qk))map.set(qk,new Map());
        const f=map.get(qk);
        f.set(pk,(f.get(pk)||0)+1);
        local.set(qk,(local.get(qk)||0)+1);
        totals.forwardEvents++;
      }
      check([...local.values()].sort((a,b)=>a-b).join()===runs(p).sort((a,b)=>a-b).join(),"run partition");
    }
    check(map.size===fact(n-1),"all observations");
    for(const q of perms(seq(n-1))){
      const qk=key(q), forward=map.get(qk), inv=new Map();
      const byPos=Array.from({length:n},()=>new Set()), byRank=Array.from({length:n},()=>new Set());
      for(let j=0;j<n;j++)for(let k=1;k<=n;k++){
        const p=insert(q,j,k), pk=key(p);
        check(key(del(p,j))===qk,"round trip");
        inv.set(pk,(inv.get(pk)||0)+1);
        byPos[j].add(pk);byRank[k-1].add(pk);
        totals.inverseEvents++;
      }
      check(byPos.every(s=>s.size===n)&&byRank.every(s=>s.size===n),"one coordinate known");
      check(inv.size===n*n-2*(n-1)&&forward.size===inv.size,"fiber cardinality");
      let max=0,entropy=0;
      for(const [p,m] of inv){
        check(forward.get(p)===m,"independent enumeration agrees");
        max=Math.max(max,m);
        multiplicityHist[m]=(multiplicityHist[m]||0)+1;
        const prob=m/(n*n);entropy-=prob*Math.log2(prob);
        totals.fibers++;
      }
      const L=Math.max(...runs(q));
      check(max===L+1,"MAP max run extension");
      longestHist[L]=(longestHist[L]||0)+1;
      entropySum+=entropy;
      maxSum+=max;
      totals.observations++;
    }
    function W(l){if(l===1)return n;if(l>n)return 0;return 2*(n-l+1)**2*fact(n-l)/fact(n);}
    let entropyFormula=2*Math.log2(n);
    for(let l=1;l<=n;l++){
      const expected=W(l)-2*W(l+1)+W(l+2);
      check(near(runCounts[l]/fact(n),expected),"run-count expectation");
      entropyFormula-=l*Math.log2(l)*expected/n;
    }
    const M=fact(n-1);
    check(near(entropySum/M,entropyFormula),"entropy identity");
    table.push({n,observations:M,parentsPerObservation:n*n-2*n+2,longestHist,multiplicityHist,
      mapNumerator:maxSum,mapDenominator:M*n*n,mapSuccess:Number((maxSum/(M*n*n)).toFixed(10)),
      oneCoordinateSuccess:1/n,conditionalEntropy:Number(entropyFormula.toFixed(10)),uniformParentGuess:1/(n*n-2*n+2)});
  }
  // Synthetic rank renderer: 80 samples per period (rank-dependent integer triangle), 800 per note.
  // This is intentionally a canonicalization demonstration, not a perceptual model.
  function wav(p){
    const count=800*p.length, a=new Uint8Array(44+2*count),d=new DataView(a.buffer);
    function str(i,s){for(let j=0;j<s.length;j++)a[i+j]=s.charCodeAt(j);}
    str(0,"RIFF");d.setUint32(4,a.length-8,true);str(8,"WAVE");str(12,"fmt ");d.setUint32(16,16,true);
    d.setUint16(20,1,true);d.setUint16(22,1,true);d.setUint32(24,8000,true);d.setUint32(28,16000,true);
    d.setUint16(32,2,true);d.setUint16(34,16,true);str(36,"data");d.setUint32(40,2*count,true);
    p.forEach((rank,j)=>{const period=40-4*rank;for(let t=0;t<800;t++){
      const phase=t%period, tri=1-4*Math.abs(phase/period-.5), env=Math.min(1,t/40,(799-t)/40);
      d.setInt16(44+2*(800*j+t),Math.round(8000*tri*env),true);
    }});return a;
  }
  const a=[1,2,3,4],b=[4,1,2,3],rawA=a.slice(1),rawB=b.slice(1);
  const qA=standard(rawA),qB=standard(rawB);
  const audio={rawA:wav(rawA),rawB:wav(rawB),ordinalA:wav(qA),ordinalB:wav(qB)};
  const same=(a,b)=>a.length===b.length&&a.every((v,i)=>v===b[i]);
  check(!same(audio.rawA,audio.rawB)&&same(audio.ordinalA,audio.ordinalB),"sonic witness");
  const fingerprint=a=>{let h=2166136261;for(const v of a)h=Math.imul(h^v,16777619);return (h>>>0).toString(16).padStart(8,"0");};
  const receipt={model:"uniform permutation and independent uniform single deletion, exact surviving ranks",maxN,totals,table,
    audio:Object.fromEntries(Object.entries(audio).map(([k,v])=>[k,{bytes:v.length,fnv1a:fingerprint(v)}])),
    witness:{parentA:a,parentB:b,erasedPosition:1,rawA,rawB,qA,qB},assertions:"all passed"};
  return {receipt,audio};
}

import { mkdirSync, writeFileSync } from 'node:fs';
const {receipt,audio}=laboratory();
if(process.argv[2]){mkdirSync(process.argv[2],{recursive:true});for(const [name,data] of Object.entries(audio))writeFileSync(process.argv[2]+'/'+name+'.wav',data);}
console.log(JSON.stringify(receipt,null,2));
