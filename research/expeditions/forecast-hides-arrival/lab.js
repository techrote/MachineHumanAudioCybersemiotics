"use strict";
// Synthetic exact bounded-integer laboratory; no human or empirical data.
function laboratory() {
  const eq=(a,b,msg)=>{if(a!==b)throw Error(`${msg}: ${a} != ${b}`)};
  const yes=(x,msg)=>{if(!x)throw Error(msg)};
  const words=[0,3,5,6], bit=(w,g)=>(w>>g)&1;
  const counters={signalFamilies:0,selectionVertices:0,selectionOptima:0,massShiftBounds:0,constructedGroupLaws:0,pairTVChecks:0,erasureModels:0,publicFlagComparisons:0,controls:0,refusals:0};
  function validate(rows,k){
    yes(Array.isArray(rows)&&rows.length>0&&rows.length<=8,"row count");
    yes(rows.every(r=>Array.isArray(r)&&r.length===2&&r.every(x=>Number.isSafeInteger(x)&&x>=0&&x<=1000000)),"counts");
    const H=rows.reduce((s,r)=>s+r[0]+r[1],0);
    yes(H>0&&H<=1000000&&Number.isSafeInteger(k)&&k>=0&&k<=H,"mass");
    return H;
  }
  // joint counts conditional on X1=0; select k count-units.
  function greedy(rows,k){
    validate(rows,k);
    let left=k,whole=0;
    for(const [z,o] of rows.filter(r=>r[0]+r[1]>0).slice().sort((a,b)=>a[1]*b[0]-b[1]*a[0])){
      const n=z+o;
      if(left<n)return [whole*n+left*o,n];
      whole+=o;left-=n;
    }
    eq(left,0,"greedy mass");return [whole,1];
  }
  // Independent vertex oracle: full/empty rows plus at most one fractional row.
  function oracle(rows,k){
    validate(rows,k);let best=null;
    for(let mask=0;mask<(1<<rows.length);mask++){
      let n=0,o=0;
      for(let i=0;i<rows.length;i++)if(mask>>i&1){n+=rows[i][0]+rows[i][1];o+=rows[i][1]}
      if(n>k)continue;
      const test=(a,b)=>{counters.selectionVertices++;if(!best||a*best[1]<best[0]*b)best=[a,b]};
      if(n===k)test(o,1);
      else for(let j=0;j<rows.length;j++)if(!(mask>>j&1)){
        const d=rows[j][0]+rows[j][1];
        if(d>=k-n)test(o*d+(k-n)*rows[j][1],d);
      }
    }
    yes(best,"oracle feasibility");return best;
  }
  // Scale S = 8 H den, then all transcript masses are integral.
  function witness(rows){
    const H=validate(rows,0);yes(H%2===0,"even mass for witness");
    const A=rows.reduce((s,r)=>s+r[1],0), [num,den]=greedy(rows,H/2);
    const S=8*H*den,T=S/4,M=4*num,N=4*den*A-M;
    const laws=[];
    function local(m){
      return [T-(m[0]+m[1]+m[2])/2,(m[0]+m[1]-m[2])/2,(m[0]+m[2]-m[1])/2,(m[1]+m[2]-m[0])/2];
    }
    for(let g=0;g<3;g++){
      const p=[];
      for(const w of words){
        let q;
        if(w===0&&3*M>2*T)q=words.map(v=>v===0?0:bit(v,g)?M/2:T-M);
        else q=local([0,1,2].map(j=>w===0?M:bit(w,j)?T/2:N));
        yes(q.every(x=>Number.isSafeInteger(x)&&x>=0),"nonnegative integer local masses");
        eq(q.reduce((a,b)=>a+b,0),T,"first marginal");
        const ones=q.reduce((a,b,i)=>a+bit(words[i],g)*b,0);
        eq(ones,w===0?M:bit(w,g)?T/2:N,"actual conditional second-bit mass");
        p.push(...q);
      }
      const path=[0,0,0,0];
      for(let i=0;i<16;i++)path[2*bit(words[i>>2],g)+bit(words[i%4],g)]+=p[i];
      [S/2-4*den*A,4*den*A,S/4,S/4].forEach((v,i)=>eq(path[i],v,"actual path law"));
      eq(p.reduce((a,b)=>a+b,0),S,"total");
      laws.push(p);counters.constructedGroupLaws++;
    }
    const predicted=Math.max(0,3*M/2-T);
    for(let i=0;i<3;i++)for(let j=i+1;j<3;j++){
      const tv=laws[i].reduce((s,x,k)=>s+Math.abs(x-laws[j][k]),0)/2;
      eq(tv,predicted,"pair TV");counters.pairTVChecks++;
    }
    return {num:predicted,den:S,laws};
  }
  function* compositions(n,k,p=[]){
    if(k===1){yield [...p,n];return}
    for(let i=0;i<=n;i++)yield* compositions(n-i,k-1,[...p,i]);
  }
  for(let H=2;H<=10;H+=2)for(const c of compositions(H,6)){
    const rows=[[c[0],c[1]],[c[2],c[3]],[c[4],c[5]]];
    counters.signalFamilies++;
    const [m,d]=greedy(rows,H/2),F=Math.max(0,3*m-H*d);
    for(let k=0;k<=H;k++){
      const [n,e]=greedy(rows,k),[o,f]=oracle(rows,k);
      eq(n*f,o*e,"greedy vs vertex oracle");counters.selectionOptima++;
      const cost=Math.max(0,3*n-2*k*e)+2*Math.abs(k-H/2)*e;
      yes(cost*d>=F*e,"mass-shift bound");counters.massShiftBounds++;
    }
    witness(rows);
  }
  for(let D=2;D<=24;D+=2)for(let A=0;A<=D;A++)for(let Q=0;Q<=D;Q++){
    const rows=[[(D-A)*Q,0],[(D-A)*(D-Q),A*(D-Q)],[0,A*Q]];
    const w=witness(rows);
    const num=Math.max(0,(6*A-5*D)*D*D,(3*A-2*D)*D*D-6*Q*A*(D-A));
    eq(w.num*8*D**3,num*w.den,"erasure closed form");counters.erasureModels++;
    const u=witness([[D-A,A]]),v=witness([[D-A,0],[0,A]]);
    eq(u.num*8*D,Math.max(0,3*A-2*D)*u.den,"no preview");
    eq(v.num*8*D,Math.max(0,6*A-5*D)*v.den,"full preview");
    const pub=(D-Q)*Math.max(0,3*A-2*D)+Q*Math.max(0,6*A-5*D);
    yes(w.num*8*D*D<=pub*w.den,"hidden cannot be worse");
    // Direct pair TV on disjoint flagged blocks, cross-multiplied.
    const raw0=u.laws[0].reduce((s,x,k)=>s+Math.abs(x-u.laws[1][k]),0);
    const raw1=v.laws[0].reduce((s,x,k)=>s+Math.abs(x-v.laws[1][k]),0);
    // Avoid huge products: endpoint denominators here <= 8*24*24.
    eq(4*D*((D-Q)*raw0*v.den+Q*raw1*u.den),pub*u.den*v.den,"public flag");
    counters.publicFlagComparisons++;
  }
  const no=witness([[1,5]]),weak=witness([[1,2],[0,3]]);
  eq(no.num*16,no.den,"no hint endpoint");
  eq(weak.num,0,"weak hint endpoint");
  eq(Math.max(1,5),Math.max(1,2)+Math.max(0,3),"same Bayes accuracy");counters.controls+=3;
  const endpoint=witness([[3,0],[2,10],[0,15]]);
  eq(endpoint.num,0,"q=.6 at a=5/6 after scaling");counters.controls++;
  for(const args of [[[],0],[[[1,-1]],0],[[[0,0]],0],[[[1,1]],3],[[[1,.5]],1]]){
    let threw=false;try{greedy(...args)}catch(e){threw=true}yes(threw,"malformed input accepted");counters.refusals++;
  }
  return counters;
}
console.log(JSON.stringify(laboratory(),null,2));
