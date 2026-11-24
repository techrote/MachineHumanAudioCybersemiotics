import {analyze,plan,phasePlan,sign,census} from './chord.mjs';
import {readFileSync} from 'node:fs';
import assert from 'node:assert/strict';
export function verify(){
  const receipt=census();
  function convolution(f,a){
    const pairs=new Map();
    for(let i=0;i<f.length;i++)for(let j=0;j<f.length;j++){
      const k=f[i]+f[j];pairs.set(k,(pairs.get(k)||0)+a[i]*a[j]);
    }
    return f.map(t=>f.reduce((v,z,i)=>v+(pairs.get(t+z)||0)*a[i],0));
  }
  function eq(a,b){if(JSON.stringify(a)!==JSON.stringify(b))throw Error(JSON.stringify({a,b}));}
  let cases=0,phaseCases=0;
  for(const row of receipt.rows){
    const {n,span}=row,ones=Array(n).fill(1),hist=new Map();
    let sidon=0,apFree=0,apFalse=0,visited=0;
    function walk(f,next){
      if(f.length===n-1){
        f=[...f,span];const a=analyze(f);
        const r=convolution(f,ones).map(v=>v-(2*n-1));
        const s=f.map((_,i)=>convolution(f,ones.map((_,j)=>Number(i!==j)))[i]);
        eq(a.residual,r);eq(a.silent,s);
        const diffs=[];for(let i=0;i<n;i++)for(let j=i+1;j<n;j++)diffs.push(f[j]-f[i]);
        eq(a.sidon,new Set(diffs).size===diffs.length);eq(a.sidon,!s.some(Boolean));
        const ap=!f.some((x,i)=>f.some((y,j)=>i<j&&f.includes(2*y-x)));
        eq(a.apFree,ap);sidon+=Number(a.sidon);apFree+=Number(ap);apFalse+=Number(ap&&!a.sidon);
        const p=Math.max(...s),t=r.reduce((x,y)=>x+y,0);hist.set(p+','+t,[p,t]);visited++;cases++;return;
      }
      for(let x=next;x<span;x++)walk([...f,x],x+1);
    }
    walk([0],1);
    const v=[...hist.values()];
    const frontier=v.filter(a=>!v.some(b=>a!==b&&b[0]<=a[0]&&b[1]<=a[1])).sort((a,b)=>a[0]-b[0]||a[1]-b[1]);
    eq([visited,sidon,apFree,apFalse,frontier],[row.visited,row.sidon,row.apFree,row.apFalse,row.frontier.map(v=>[v.peak,v.total])]);
  }
  for(const p of receipt.phase){
    eq(p.status,'OPTIMAL');
    const f=Array.from({length:p.n},(_,i)=>i);
    // Independent pair-sum certificate: XOR labels injective within each sum.
    const seen=new Set();
    for(let i=0;i<p.n;i++)for(let j=i;j<p.n;j++){
      const key=(i+j)+','+(p.labels[i]^p.labels[j]);if(seen.has(key))throw Error('pair collision');seen.add(key);
    }
    if(p.n>8)continue;
    for(let w=0;w<3**p.n;w++){
      let v=w;const a=f.map(()=>{const z=v%3-1;v=Math.floor(v/3);return z;});
      const accum=f.map(()=>0),power=a.reduce((s,x)=>s+x*x,0);
      for(let t=0;t<p.frames;t++){
        const signs=p.labels.map(l=>sign(l,t)),c=convolution(f,a.map((x,i)=>x*signs[i]));
        for(let i=0;i<p.n;i++)accum[i]+=c[i]*signs[i];
      }
      eq(accum,a.map(x=>p.frames*x*(2*power-x*x)));phaseCases++;
    }
  }
  // Independent brute-force lower bound for small dense grids using pair-sum injectivity.
  for(const p of receipt.phase.filter(x=>x.n<=5)){
    for(let bits=0;bits<p.bits;bits++){
      const q=2**bits;
      for(let word=0;word<q**(p.n-1);word++){
        let v=word;const labels=[0];for(let i=1;i<p.n;i++){labels.push(v%q);v=Math.floor(v/q);}
        const pairs=new Set();let ok=true;
        for(let i=0;i<p.n;i++)for(let j=i;j<p.n;j++){
          const key=(i+j)+','+(labels[i]^labels[j]);if(pairs.has(key))ok=false;pairs.add(key);
        }
        if(ok)throw Error('smaller code found');
      }
    }
  }
  eq(analyze([0,1,4,5]).silent,[2,2,2,2]);
  eq(analyze([0,1,4,6]).silent,[0,0,0,0]);
  eq(plan([0,1,2,3],3,[],1).status,'BUDGET_EXHAUSTED');
  eq(phasePlan([0,1,2,3],1).status,'INFEASIBLE_WITHIN_BITS');
  eq(phasePlan([0,1,2,3],4,1).status,'BUDGET_EXHAUSTED');
  for(const f of [[0,0],[NaN,1],[1.2,2]]){let rejected=false;try{analyze(f)}catch{rejected=true}eq(rejected,true);}
  return {cases,phaseCases,rows:receipt.rows.length,phasePlans:receipt.phase.length};
}
assert.deepEqual(JSON.parse(readFileSync(new URL('./results.synthetic.txt',import.meta.url),'utf8')),census());
console.log(JSON.stringify(verify()));
