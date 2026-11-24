// Original finite experiment, no external dependencies. Run node laboratory.js [output-directory]
function laboratory() {
  "use strict";
  const check=(b,m)=>{if(!b)throw Error(m)};
  const pop=x=>{let n=0;while(x){x&=x-1;n++}return n};
  function choose(n,k){if(k<0||k>n)return 0;let z=1;for(let j=1;j<=k;j++)z=z*(n-j+1)/j;return Math.round(z)}
  const masks=n=>Array.from({length:(1<<n)-1},(_,i)=>i+1);
  function denom(n,c){return c.reduce((s,w,k)=>s+(k?choose(n-1,k-1)*w:0),0)}
  function profile(n,parity){return Array.from({length:n+1},(_,k)=>k>0&&k%2===parity?1:0)}
  function restricted(n,c,r){return Array.from({length:r+1},(_,j)=>j?Array.from({length:n-r+1},(_,h)=>choose(n-r,h)*c[j+h]).reduce((a,b)=>a+b,0):0)}
  function projection(n,c,T,i){
    const out=new Map();
    for(const s of masks(n))if((s&(1<<i))&&c[pop(s)]){let u=s&T;out.set(u,(out.get(u)||0)+c[pop(s)])}
    return out;
  }
  function value(n,c,prior,actions,T){
    const den=denom(n,c), total=prior.reduce((a,b)=>a+b,0);
    let z=0;
    for(const s of masks(n)){
      const w=c[pop(s)];if(!w)continue;
      let best=-Infinity;
      for(const a of actions){let v=0;for(let i=0;i<n;i++)if((T&(1<<i))&&(s&(1<<i)))v+=prior[i]*a[i];best=Math.max(best,v)}
      z+=w*best;
    }
    return [z,den*total];
  }
  function top(n,c,l){let z=0;for(let k=1;k<=n;k++)z+=choose(n,k)*c[k]*Math.min(k,l);return [z,n*denom(n,c)]}
  function eq(a,b){return a[0]*b[1]===b[0]*a[1]}
  function reduce(a){let x=Math.abs(a[0]),y=a[1];while(y){const t=x%y;x=y;y=t}return [a[0]/x,a[1]/x]}
  let normalization=0,supports=0,rowChecks=0,kernelChecks=0,decisionChecks=0,topChecks=0;
  const rows=[];
  for(let n=2;n<=9;n++){
    const O=profile(n,1),E=profile(n,0),D=denom(n,O),full=(1<<n)-1;
    check(D===denom(n,E)&&D===2**(n-2),"normalization formula");
    for(const c of [O,E])for(let i=0;i<n;i++){
      let count=0;for(const s of masks(n))if(s&(1<<i))count+=c[pop(s)];
      check(count===D,"row sum");normalization++;
    }
    for(let T=1;T<full;T++){
      supports++;const r=pop(T),d=restricted(n,O,r),e=restricted(n,E,r);
      check(JSON.stringify(d)===JSON.stringify(e),"restricted formula");
      for(let i=0;i<n;i++)if(T&(1<<i)){
        const p=projection(n,O,T,i),q=projection(n,E,T,i);
        for(let U=T;U;U=(U-1)&T){
          const expected=U&(1<<i)?d[pop(U)]:0;
          check((p.get(U)||0)===expected&&(q.get(U)||0)===expected,"projection");rowChecks++;
        }
        // Verify the product of project-and-reinflate kernels exactly, with
        // numerator cancellation against the target marginal for each S.
        for(const target of [O,E]){
          const other=target===O?q:p;
          for(const S of masks(n))if(target[pop(S)]){
            const U=S&T;if(!U)continue;
            const marginal=d[pop(U)];
            check(marginal>0,"reverse kernel denominator");
            check((other.get(U)||0)*target[pop(S)]===((S&(1<<i))?marginal*target[pop(S)]:0),"reverse kernel composition");
            kernelChecks++;
          }
        }
      }
      // Deterministic, heterogeneous priors and signed utility matrices;
      // not a substitute for the proof covering all priors and actions.
      const prior=Array.from({length:n},(_,i)=>T&(1<<i)?1+(i*7+T)%11:0);
      const acts=Array.from({length:4},(_,a)=>Array.from({length:n},(_,i)=>((T+13*a+7*i+3*a*i)%17)-8));
      check(eq(value(n,O,prior,acts,T),value(n,E,prior,acts,T)),"arbitrary utility witness");
      decisionChecks++;
    }
    const gaps=[];
    for(let l=1;l<=n;l++){
      const a=top(n,O,l),b=top(n,E,l),expected=l<n?(-1)**(l-1)*choose(n-2,l-1):0;
      check(a[0]-b[0]===expected,"top-l formula");
      const actions=masks(n).filter(s=>pop(s)===l).map(s=>Array.from({length:n},(_,i)=>Number(Boolean(s&(1<<i)))));
      // Explicit payoff maximization independent of the closed formula.
      if(n<=7){const prior=Array(n).fill(1);check(eq(value(n,O,prior,actions,full),a)&&eq(value(n,E,prior,actions,full),b),"top-l oracle")}
      topChecks++;
      gaps.push(reduce([a[0]-b[0],a[1]]).join("/"));
    }
    rows.push({n,row_denominator:D,top1_odd:reduce(top(n,O,1)).join("/"),top1_even:reduce(top(n,E,1)).join("/"),gaps});
  }
  // Independent census: all integer symmetric profiles with common row
  // denominator D=8, not just the parity endpoints.
  const census=[];
  for(const n of [3,4,5]){
    const D=8,groups=new Map();let count=0,pairs=0,maxGap=0;
    function visit(c,k,left){
      if(k===n+1){
        if(left)return;count++;
        const sig=restricted(n,c,n-1).join(",");
        if(!groups.has(sig))groups.set(sig,[]);
        groups.get(sig).push(c.slice());return;
      }
      const w=choose(n-1,k-1);for(let t=0;t*w<=left;t++){c[k]=t;visit(c,k+1,left-t*w)}
    }
    visit([0],1,D);
    for(const g of groups.values())for(let a=0;a<g.length;a++)for(let b=a+1;b<g.length;b++){
      pairs++;let delta=g[a][1]-g[b][1];
      for(let k=1;k<=n;k++)check(g[a][k]-g[b][k]===delta*(-1)**(k-1),"kernel uniqueness");
      check(Math.abs(delta)*2**(n-2)<=D,"sharp delta bound");
      for(let l=1;l<n;l++){
        const gap=top(n,g[a],l)[0]-top(n,g[b],l)[0];
        check(gap===delta*(-1)**(l-1)*choose(n-2,l-1),"general gap");
        maxGap=Math.max(maxGap,Math.abs(gap));
      }
    }
    census.push({n,denominator:D,profiles:count,restriction_classes:groups.size,locally_equivalent_distinct_pairs:pairs,max_shortlist_gap:reduce([maxGap,n*D]).join("/")});
  }
  // Negative controls: n=2 cannot give the top-2 reversal; identical
  // experiments have identical full decision values. A nonalternating
  // perturbation is detected on a proper restriction.
  check(eq(top(2,profile(2,0),2),top(2,profile(2,1),2)),"n=2 negative");
  check(JSON.stringify(restricted(3,[0,2,0,0],2))!==JSON.stringify(restricted(3,[0,0,1,0],2)),"detected nonalternating perturbation");
  // Exact deterministic original PCM. Truth is state A; each possible
  // output appears once in ascending mask order, then projected masks sorted.
  function wave(seq){
    const sr=8000,frames=1600,gap=400,data=new Uint8Array(44+2*(frames+gap)*seq.length),v=new DataView(data.buffer);
    const str=(o,s)=>{for(let i=0;i<s.length;i++)data[o+i]=s.charCodeAt(i)};
    str(0,"RIFF");v.setUint32(4,data.length-8,true);str(8,"WAVE");str(12,"fmt ");v.setUint32(16,16,true);v.setUint16(20,1,true);v.setUint16(22,1,true);v.setUint32(24,sr,true);v.setUint32(28,sr*2,true);v.setUint16(32,2,true);v.setUint16(34,16,true);str(36,"data");v.setUint32(40,data.length-44,true);
    for(let j=0;j<seq.length;j++)for(let t=0;t<frames;t++){
      let y=0;for(let i=0;i<3;i++)if(seq[j]&(1<<i))y+=((t%[40,30,24][i])<[20,15,12][i]?1:-1)*3500;
      const ramp=Math.min(t,frames-1-t,80);y=Math.trunc(y*ramp/80);
      v.setInt16(44+2*(j*(frames+gap)+t),y,true);
    }
    return data;
  }
  const odd=[1,7],even=[3,5],pr=s=>s.map(x=>x&3).sort((a,b)=>a-b);
  const audio={odd:wave(odd),even:wave(even),odd_projected:wave(pr(odd)),even_projected:wave(pr(even))};
  const equal=(a,b)=>a.length===b.length&&a.every((v,i)=>v===b[i]);
  check(!equal(audio.odd,audio.even),"full audio differs");check(equal(audio.odd_projected,audio.even_projected),"projected audio identical");
  function fnv(bytes){let h=2166136261;for(const x of bytes)h=Math.imul(h^x,16777619)>>>0;return h.toString(16).padStart(8,"0")}
  return {receipt:{schema:"mhac-236-v1",normalization,supports,rowChecks,kernelChecks,decisionChecks,topChecks,rows,census,audio:Object.fromEntries(Object.entries(audio).map(([k,v])=>[k,{bytes:v.length,fnv1a32:fnv(v)}]))},audio};
}
const result=laboratory();
console.log(JSON.stringify(result.receipt,null,2));
if(process.argv[2]){const fs=require('node:fs'),path=require('node:path');fs.mkdirSync(process.argv[2],{recursive:true});for(const [name,bytes] of Object.entries(result.audio))fs.writeFileSync(path.join(process.argv[2],name+'.wav'),bytes);}
